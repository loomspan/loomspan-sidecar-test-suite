"""Evidence-based live-run triage. Diagnosis never changes acceptance or approves replay."""
import hashlib
import json
from pathlib import Path
import re


LABELS = {
    'framework_exception': 'Suspected Framework defect',
    'provider_error': 'Provider error / response protocol',
    'provider_timeout': 'Provider request timeout',
    'transport_error': 'Provider connection / transport',
    'execution_limit': 'Execution deadline / budget',
    'model_contract': 'Model output rejected; correction exhausted',
    'unknown_failure': 'Unclassified execution failure',
    'evidence_gap': 'Evidence / harness investigation needed',
    'completed_business_failure': 'Completed; business checks failed',
    'completed': 'Completed; automated checks passed',
}

NEXT_STEPS = {
    'framework_exception': 'Reproduce the internal exception and investigate Framework handling; the stack is a defect candidate, not automatic proof.',
    'provider_error': 'Check the provider status/envelope and route, credentials or limits. This does not measure model reasoning.',
    'provider_timeout': 'Inspect provider latency, network, request timeout and the recorded retry decision before changing limits.',
    'transport_error': 'Inspect the provider connection, proxy and network; an SDK I/O exception alone does not locate the fault.',
    'execution_limit': 'Inspect the mission deadline or usage budget and unfinished work; do not assume a Framework bug or increase limits blindly.',
    'model_contract': 'Inspect rejected model output and correction feedback, then the prompt/schema and model suitability. Expected rejection is not an internal crash.',
    'unknown_failure': 'Inspect the linked exception and application/Framework boundary; available evidence cannot assign responsibility.',
    'evidence_gap': 'Resolve capture, correlation or harness gaps before assigning responsibility or judging the answer.',
    'completed_business_failure': 'Review the failed checks against model outputs, supplied evidence, prompts and application publication. Semantic review is needed to judge answer quality.',
    'completed': 'No automated failure identified; perform semantic review before accepting the business judgment.',
}


def exception_category(meta, data):
    """Use exception diagnostics, never model prose, to attribute an execution error."""
    kind = str(data.get('exceptionType') or meta.get('exceptionType') or '')
    message = str(data.get('message') or meta.get('message') or '')
    stack = '\n'.join(d.get('text', '') for d in data.get('diagnostics', [])
                      if isinstance(d, dict) and d.get('kind') == 'JAVA_STACK_TRACE')
    signal = (kind + ' ' + message + ' ' + stack).lower()
    category = str(meta.get('failureCategory', '')).upper()
    if category == 'TIMEOUT' or ('timeout' in signal or 'timed out' in signal):
        return 'provider_timeout' if (meta.get('attemptId') or 'com.openai.' in signal
                                      or 'sockettimeout' in signal) else 'execution_limit'
    if any(x in signal for x in ['quotaexceeded', 'budgetexceeded', 'usagelimitexceeded', 'usage limit', 'mission deadline', 'mission timeout']):
        return 'execution_limit'
    if 'valid step action after' in signal or 'outputschemavalidationexception' in signal:
        return 'model_contract'
    if 'openaiioexception' in signal or category in {'CONNECTION', 'NETWORK', 'TRANSPORT'}:
        return 'transport_error'
    if kind.startswith('com.openai.errors.') or category in {'RATE_LIMIT', 'AUTHENTICATION', 'SERVER_ERROR'}:
        return 'provider_error'
    # A Framework frame somewhere in a propagated stack is not evidence of a bug.
    frames = re.findall(r'^\s*at ([^\s]+)', stack, re.M)
    origin = next((f for f in frames if not f.startswith(('java.', 'java.base/', 'jdk.', 'sun.'))), '')
    if origin.startswith('ai.loomspan.internal.') and kind in {
            'java.lang.NullPointerException', 'java.lang.ClassCastException',
            'java.lang.IndexOutOfBoundsException', 'java.lang.UnsupportedOperationException',
            'java.lang.AssertionError'}:
        return 'framework_exception'
    return 'unknown_failure'


def diagnose(directory, paths, review):
    directory = Path(directory).resolve()
    gaps = []

    def read(name, expected):
        file = (directory / name).resolve()
        if not file.is_relative_to(directory):
            gaps.append('Evidence path escapes capture: ' + name)
            return expected()
        try:
            value = json.loads(file.read_bytes())
            if not isinstance(value, expected):
                raise ValueError('unexpected JSON shape')
            return value
        except (OSError, ValueError) as error:
            gaps.append(name + ': ' + type(error).__name__)
            return expected()

    manifest, journal, index = read('manifest.json', dict), read('journal.json', list), read('trace-index.json', list)
    hashes = read('checksums.json', dict)
    for name in ['manifest.json', 'journal.json', 'trace-index.json', *(p + '-assessment.json' for p in paths)]:
        file = directory / name
        try:
            if hashlib.sha256(file.read_bytes()).hexdigest() != hashes.get(name):
                gaps.append('Capture checksum missing or mismatched: ' + name)
        except OSError:
            gaps.append('Capture file unavailable: ' + name)
    if manifest.get('collectionError'):
        gaps.append('Capture collection error: ' + str(manifest['collectionError']))
    results = []
    for path in paths:
        local_gaps = list(gaps)
        selected = [r for r in manifest.get('results', []) if r.get('path') == path]
        if len(selected) != 1:
            local_gaps.append('Expected one identified execution for ' + path)
        case = selected[0].get('caseId') if len(selected) == 1 else None
        terminal = read(path + '-assessment.json', dict)
        status = terminal.get('status', 'UNKNOWN')
        events = [e for e in journal if case and e.get('caseId') == case and e.get('path') == path]
        requests = [e for e in events if e.get('event') == 'model-request']
        responses = [e for e in events if e.get('event') == 'model-response']
        observations, failures, trace_outcomes = [], [], []
        recovery = {'truncatedResponses': 0, 'invalidJsonResponses': 0, 'correctionRequests': 0,
                    'rejectedStepActions': 0, 'providerRetries': 0, 'retryDecisions': {},
                    'recoveredModelFrames': 0, 'unrecoveredModelFrames': 0}
        for event in responses:
            body = event.get('response')
            body = body if isinstance(body, dict) else {}
            choices = body.get('choices')
            choice = choices[0] if isinstance(choices, list) and choices and isinstance(choices[0], dict) else {}
            error = body.get('error') or choice.get('error')
            if event.get('status') != 200 or error or not choice or choice.get('finish_reason') == 'error':
                err = error if isinstance(error, dict) else {}
                metadata = err.get('metadata') or {}
                observations.append({'category': 'provider_error', 'requestId': event.get('requestId'),
                    'httpStatus': event.get('status'), 'provider': metadata.get('provider_name') or body.get('provider'),
                    'limitSource': metadata.get('limit_source'),
                    'message': err.get('message') or str(error or ('Response missing choices' if not choice else 'Provider completion error')),
                    'evidence': 'journal.json'})
                continue  # A provider error envelope is not malformed model JSON.
            if choice.get('finish_reason') == 'length':
                recovery['truncatedResponses'] += 1
            try:
                json.loads(choice.get('message', {}).get('content', ''))
            except (ValueError, TypeError):
                recovery['invalidJsonResponses'] += 1
        for event in events:
            if event.get('event') == 'provider-transport-failure':
                kind = str(event.get('errorType', 'Unknown'))
                observations.append({'category': 'provider_timeout' if 'timeout' in kind.lower() else 'transport_error',
                                     'message': kind, 'requestId': event.get('requestId'), 'evidence': 'journal.json'})
        for event in requests:
            messages = event.get('request', {}).get('messages', [])
            if any((m.get('role') == 'system' and 'YOUR PREVIOUS ACTION WAS INVALID' in str(m.get('content', '')))
                   or (m.get('role') == 'user' and str(m.get('content', '')).startswith((
                       'The previous response could not be parsed as JSON.',
                       'The previous response is valid JSON but does not satisfy the configured output_schema.')))
                   for m in messages):
                recovery['correctionRequests'] += 1
        roots = [t for t in index if t.get('path') == path and case and case in t.get('cases', [])
                 and t.get('entrySkill') == 'resolveEquipment']
        if len(roots) != 1:
            local_gaps.append('Expected one case-associated root trace')
        for trace in roots:
            name = trace.get('file', '')
            file = (directory / name).resolve()
            try:
                if not name or not file.is_relative_to(directory):
                    raise ValueError('Trace outside capture')
                raw = file.read_bytes()
                if hashlib.sha256(raw).hexdigest() != trace.get('sha256'):
                    raise ValueError('Trace checksum mismatch')
                frames = [json.loads(line) for line in raw.splitlines() if line]
            except (OSError, ValueError) as error:
                local_gaps.append(name + ': ' + str(error))
                continue
            chunks = {}
            for frame in frames:
                if frame.get('recordType') == 'PAYLOAD_CHUNK_APPENDED':
                    chunks.setdefault(frame['metadata'].get('payloadId'), []).append(frame)

            def payload(frame):
                data = frame.get('data')
                meta = frame.get('metadata') or {}
                if data is None and meta.get('payloadId'):
                    parts = sorted(chunks.get(meta['payloadId'], []), key=lambda c: c['metadata']['chunkIndex'])
                    try:
                        if [p['metadata']['chunkIndex'] for p in parts] != list(range(meta['chunkCount'])):
                            raise ValueError('Missing payload chunks')
                        data = json.loads(''.join(p['data'] for p in parts))
                    except (KeyError, TypeError, ValueError):
                        local_gaps.append(name + ': unreadable payload at sequence ' + str(frame.get('sequence')))
                return data if isinstance(data, dict) else {}

            model_fail_frames, successful_model_frames = set(), set()
            trace_failures = {}
            for line, frame in enumerate(frames, 1):
                record, meta = frame.get('recordType'), frame.get('metadata') or {}
                if record == 'TRACE_COMPLETED':
                    trace_outcomes.append(meta.get('outcome', 'UNKNOWN'))
                if record == 'MODEL_RESPONSE_RECEIVED':
                    successful_model_frames.add(frame.get('frameId'))
                if record == 'MODEL_REQUEST_SENT' and meta.get('providerAttemptNumber', 1) > 1:
                    recovery['providerRetries'] += 1
                if record == 'STEP_ACTION_REJECTED':
                    recovery['rejectedStepActions'] += 1
                    model_fail_frames.add(frame.get('frameId'))
                if record in {'STEP_ACTION_VALIDATED', 'STEP_COMPLETED'}:
                    successful_model_frames.add(frame.get('frameId'))
                if record not in {'ERROR_RECORDED', 'MODEL_ATTEMPT_FAILED', 'STEP_FAILED'}:
                    continue
                data = payload(frame)
                category = exception_category(meta, data)
                detail = {'category': category, 'exceptionType': data.get('exceptionType') or meta.get('exceptionType'),
                          'message': data.get('message') or meta.get('message') or meta.get('failureCategory', record),
                          'route': frame.get('route'), 'evidence': name, 'line': line,
                          'failureId': meta.get('failureId'), 'attemptId': meta.get('attemptId')}
                if record == 'MODEL_ATTEMPT_FAILED':
                    model_fail_frames.add(frame.get('frameId'))
                    decision = meta.get('retryDecision', 'UNKNOWN')
                    recovery['retryDecisions'][decision] = recovery['retryDecisions'].get(decision, 0) + 1
                    detail['retryDecision'] = decision
                    detail['failureCategory'] = meta.get('failureCategory')
                    observations.append(detail)
                else:
                    ident = meta.get('failureId') or str(frame.get('sequence'))
                    prior = trace_failures.get(ident)
                    # Prefer the diagnostic stack to later propagation through parent steps.
                    if prior is None or (prior['category'] == 'unknown_failure' and category != 'unknown_failure'):
                        trace_failures[ident] = detail
            failures.extend(trace_failures.values())
            recovery['recoveredModelFrames'] += len(model_fail_frames & successful_model_frames)
            recovery['unrecoveredModelFrames'] += len(model_fail_frames - successful_model_frames)
        if not trace_outcomes:
            local_gaps.append('No verified Framework terminal trace')
        finished = status == 'COMPLETED' and trace_outcomes == ['SUCCEEDED']
        if selected and selected[0].get('status') != status:
            local_gaps.append('Manifest and public execution status disagree')
        if status == 'COMPLETED' and any(x != 'SUCCEEDED' for x in trace_outcomes):
            local_gaps.append('Public execution and trace outcome disagree')
        # Keep failed checks intact; incomplete executions cannot establish answer quality.
        checks = [c for c in review.get('checks', []) if c.get('path') in (None, path)]
        failed_checks = [c['check'] for c in checks if not c['passed']]
        if not checks:
            local_gaps.append('No automated review checks available')
        if review.get('status') in {'FAIL', 'REJECTED_FOR_REPLAY'} and not any(
                not c['passed'] for c in review.get('checks', [])):
            local_gaps.append('Failed review has no explanatory failed checks')
        evidence_words = ('checksum', 'hash', 'correlat', 'inventory', 'identity recorded', 'read ', 'review:', 'collection', 'profile', 'selected model')
        for check in failed_checks:
            if any(word in check.lower() for word in evidence_words):
                local_gaps.append('Failed evidence check: ' + check)
        local_gaps += [g for g in gaps if g not in local_gaps]
        categories = {f['category'] for f in failures if not finished or f['category'] in {
            'framework_exception', 'unknown_failure'}}
        attempt_categories = {o['category'] for o in observations}
        if status == 'CHECK_ERROR':
            categories.add('execution_limit' if 'timeout' in str(terminal.get('errorType', '')).lower() else 'evidence_gap')
            local_gaps.append('Harness polling/collection error: ' + str(terminal.get('errorType', 'unknown')))
        if not finished:
            categories |= attempt_categories
        priority = ['framework_exception', 'provider_timeout', 'execution_limit', 'provider_error',
                    'transport_error', 'model_contract', 'unknown_failure']
        primary = next((c for c in priority if c in categories), None)
        if primary is None:
            primary = ('evidence_gap' if local_gaps else 'completed_business_failure' if finished and failed_checks
                       else 'completed' if finished else 'unknown_failure')
        results.append({'path': path, 'caseId': case, 'executionStatus': status, 'traceOutcomes': trace_outcomes,
                        'primary': primary, 'label': LABELS[primary], 'runtimeCompleted': finished,
                        'nextStep': NEXT_STEPS[primary],
                        'businessStatus': ('NOT_ASSESSED' if not finished or local_gaps else 'FAIL' if failed_checks else 'PASS'),
                        'failedChecks': failed_checks, 'failures': failures, 'providerObservations': observations,
                        'recovery': recovery, 'evidenceGaps': list(dict.fromkeys(local_gaps)),
                        'modelRequests': len(requests), 'semanticReview': 'PENDING',
                        'configuredLimits': {k: manifest.get(k) for k in [
                            'providerRequestTimeoutSeconds', 'missionTimeoutSeconds', 'sessionMaxUsageUnits']}})
    return {'version': 1, 'paths': results,
            'caveat': 'Categories identify the next investigation, not proven root cause. Completed business failures require model/prompt/source review; semantic judgment is not automated.'}


def cell(value):
    return str(value).replace('|', '\\|').replace('\n', ' ').replace('\r', ' ').replace('<', '&lt;').replace('>', '&gt;')


def render(stage):
    diagnostics = stage.get('diagnostics')
    if not diagnostics:
        if stage['scenario'] == 'service-requests':
            blocked = any(c['check'] == 'valid live baseline required for service approval' and not c['passed']
                          for c in stage['review']['checks'])
            return ['Service checks: **NOT RUN — baseline validation failed.**' if blocked else
                    'Service checks: **' + stage['review']['status'] + '** (no new model calls).', '']
        return ['Diagnostics unavailable; inspect capture and runner errors.', '']
    lines = ['| Integration | Execution | Investigate | Business checks |',
             '| --- | --- | --- | --- |']
    for result in diagnostics['paths']:
        lines.append('| ' + ' | '.join(cell(x) for x in [result['path'], result['executionStatus'], result['label'],
                                                      result['businessStatus']]) + ' |')
    lines += ['', diagnostics['caveat'], '']
    for result in diagnostics['paths']:
        r = result['recovery']
        lines += ['**Next step (' + result['path'] + '):** ' + result['nextStep'], '',
                  '**' + result['path'] + '**: ' + str(result['modelRequests']) + ' model requests; '
                  + str(r['providerRetries']) + ' observed provider retries; ' + str(r['correctionRequests'])
                  + ' correction requests; ' + str(r['truncatedResponses']) + ' truncated responses; '
                  + str(r['invalidJsonResponses']) + ' invalid JSON responses; '
                  + str(r['rejectedStepActions']) + ' rejected step actions.', '',
                  'Recovery: ' + str(r['recoveredModelFrames']) + ' failed provider calls / rejected actions later received a response or valid action; '
                  + str(r['unrecoveredModelFrames']) + ' without recorded recovery. '
                  + 'Retry decisions: ' + (cell(json.dumps(r['retryDecisions'])) if r['retryDecisions'] else 'none recorded') + '.', '']
        if result['primary'] in {'provider_timeout', 'execution_limit'}:
            lines += ['Recorded limits: ' + cell(json.dumps(result['configuredLimits'])) + '.', '']
        details = result['failures'] + result['providerObservations']
        for detail in details:
            file = (Path(stage['capture']) / detail['evidence']).as_posix()
            suffix = ':' + str(detail['line']) if detail.get('line') else ''
            info = '; '.join((('HTTP ' if k == 'httpStatus' else k + ': ') + str(detail[k]))
                             for k in ['exceptionType', 'message', 'route', 'httpStatus', 'provider',
                                       'limitSource', 'retryDecision'] if detail.get(k) is not None)
            lines.append('- ' + LABELS[detail['category']] + ': ' + cell(info)
                         + ' ([evidence](<' + file + suffix + '>)).')
        if not details and result['runtimeCompleted']:
            lines.append('- No Framework exception or provider failure observed in the collected evidence.')
        for gap in result['evidenceGaps']:
            lines.append('- Evidence limitation: ' + cell(gap))
        if result['businessStatus'] == 'FAIL':
            lines.append('- Workflow completed; review model outputs, prompts and evidence transfer. '
                         'Failed checks alone do not prove a Framework defect or insufficient model capability.')
        elif result['businessStatus'] == 'NOT_ASSESSED':
            lines.append('- Answer quality is inconclusive; failed downstream checks may be consequences of incomplete execution/evidence.')
        else:
            lines.append('- Automated checks passed; reasonable business judgment still requires semantic review.')
        lines.append('')
    return lines
