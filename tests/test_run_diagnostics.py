"""Offline triage must not confuse provider/model failures with Framework defects."""
import hashlib
import json
from pathlib import Path
import pytest
from report_run import regenerate
from run_diagnostics import diagnose
from run_suite import observations, summary


def capture(root, *, path='java', status='FAILED', frames=(), events=(), checks=None):
    root.mkdir(parents=True, exist_ok=True)
    case = 'case-' + path
    trace = root / path / 'traces/root.ndjson'
    trace.parent.mkdir(parents=True, exist_ok=True)
    records = list(frames) + [{'recordType': 'TRACE_COMPLETED', 'metadata': {
        'outcome': 'SUCCEEDED' if status == 'COMPLETED' else 'FAILED'}}]
    trace.write_text('\n'.join(json.dumps(e) for e in records))
    for name, value in {
        'manifest.json': {'results': [{'path': path, 'caseId': case, 'status': status}]},
        'journal.json': [dict(e, path=path, caseId=case) for e in events],
        'trace-index.json': [{'path': path, 'cases': [case], 'entrySkill': 'resolveEquipment',
                             'file': trace.relative_to(root).as_posix(),
                             'sha256': hashlib.sha256(trace.read_bytes()).hexdigest()}],
        path + '-assessment.json': {'status': status},
    }.items():
        (root / name).write_text(json.dumps(value))
    (root / 'checksums.json').write_text(json.dumps({p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in root.glob('*.json') if p.name != 'checksums.json'}))
    return {'status': 'FAIL' if status != 'COMPLETED' else 'NEEDS_SEMANTIC_REVIEW',
            'checks': checks if checks is not None else [{'path': path, 'check': 'business answer', 'passed': True}]}


def error(kind, message='Failure', stack='', failure='f'):
    return {'recordType': 'ERROR_RECORDED', 'sequence': 4, 'frameId': 'step', 'route': 'compareOptions',
            'metadata': {'failureId': failure}, 'data': {'exceptionType': kind, 'message': message,
                'diagnostics': [{'kind': 'JAVA_STACK_TRACE', 'text': stack}]}}


def response(body, status=200, ident='r'):
    return {'event': 'model-response', 'requestId': ident, 'status': status, 'response': body}


def completion(content='{}', finish='stop'):
    return {'choices': [{'finish_reason': finish, 'message': {'content': content}}]}


def result(root, review, path='java'):
    return diagnose(root, [path], review)['paths'][0]


@pytest.mark.parametrize('http', [200, 429, 503])
def test_provider_error_envelopes_are_not_model_json_or_framework_defects(tmp_path, http):
    review = capture(tmp_path, events=[response({'error': {'message': 'Rate limited', 'metadata': {
        'provider_name': 'upstream', 'limit_source': 'upstream_provider_shared_pool'}}}, http)])
    r = result(tmp_path, review)
    assert r['primary'] == 'provider_error'
    assert r['businessStatus'] == 'NOT_ASSESSED'
    assert r['recovery']['invalidJsonResponses'] == 0
    assert r['providerObservations'][0]['limitSource'] == 'upstream_provider_shared_pool'
    assert observations(tmp_path)['invalidJsonResponseIds'] == []


def test_missing_choices_is_provider_protocol_failure(tmp_path):
    r = result(tmp_path, capture(tmp_path, events=[response({'id': 'bad-envelope'})]))
    assert r['primary'] == 'provider_error'
    assert r['providerObservations'][0]['message'] == 'Response missing choices'


def test_chunked_framework_stack_is_attributed_once_despite_parent_propagation(tmp_path):
    e = error('java.lang.NullPointerException', stack='java.lang.NullPointerException\n'
              '\tat java.base/java.util.Map.copyOf(Map.java:1)\n'
              '\tat ai.loomspan.internal.core.ExecutionCoordinator.traceSafeNode(ExecutionCoordinator.java:441)')
    body = json.dumps(e['data']); e['data'] = None
    e['metadata'].update(payloadId='p', chunkCount=2)
    chunks = [{'recordType': 'PAYLOAD_CHUNK_APPENDED', 'metadata': {'payloadId': 'p', 'chunkIndex': i}, 'data': part}
              for i, part in enumerate([body[:60], body[60:]])]
    parent = {'recordType': 'STEP_FAILED', 'metadata': {'failureId': 'f', 'exceptionType': 'java.lang.NullPointerException'}}
    r = result(tmp_path, capture(tmp_path, frames=[e, *chunks, parent]))
    assert r['primary'] == 'framework_exception'
    assert len(r['failures']) == 1
    assert r['failures'][0]['line'] == 1


def test_application_npe_is_not_blame_assigned_to_framework(tmp_path):
    e = error('java.lang.NullPointerException', stack='\tat com.example.Business.publish(Business.java:1)\n'
              '\tat ai.loomspan.internal.core.ExecutionCoordinator.execute(ExecutionCoordinator.java:1)')
    assert result(tmp_path, capture(tmp_path, frames=[e]))['primary'] == 'unknown_failure'


def test_changed_journal_blocks_clean_or_model_quality_conclusion(tmp_path):
    review = capture(tmp_path, status='COMPLETED')
    (tmp_path / 'journal.json').write_text('[{}]')
    r = result(tmp_path, review)
    assert r['primary'] == 'evidence_gap'
    assert r['businessStatus'] == 'NOT_ASSESSED'


def test_provider_and_framework_problems_are_both_retained(tmp_path):
    e = error('java.lang.NullPointerException', stack='\tat ai.loomspan.internal.core.ExecutionCoordinator.traceSafeNode(X.java:1)')
    review = capture(tmp_path, frames=[e], events=[response({'error': {'message': 'Busy'}}, 503)])
    r = result(tmp_path, review)
    assert r['primary'] == 'framework_exception'
    assert r['providerObservations'][0]['category'] == 'provider_error'


def test_timeout_and_retry_exhaustion_are_visible_without_claiming_bug(tmp_path):
    e = {'recordType': 'MODEL_ATTEMPT_FAILED', 'sequence': 3, 'frameId': 'model', 'metadata': {
        'failureCategory': 'TIMEOUT', 'attemptId': 'attempt', 'retryDecision': 'ATTEMPTS_EXHAUSTED'},
         'data': {'exceptionType': 'com.openai.errors.OpenAIIoException', 'message': 'Request failed'}}
    r = result(tmp_path, capture(tmp_path, frames=[e, error('com.openai.errors.OpenAIIoException')]))
    assert r['primary'] == 'provider_timeout'
    assert r['recovery']['retryDecisions'] == {'ATTEMPTS_EXHAUSTED': 1}
    assert r['recovery']['providerRetries'] == 0  # Exhausted may mean no retry was allowed.


def test_mission_deadline_is_distinct_from_provider_timeout(tmp_path):
    e = error('java.util.concurrent.TimeoutException', 'Mission timed out')
    assert result(tmp_path, capture(tmp_path, frames=[e]))['primary'] == 'execution_limit'


def test_model_correction_exhaustion_is_not_internal_illegal_state_bug(tmp_path):
    e = error('java.lang.IllegalStateException', "Model failed to produce a valid step action after 2 attempts at step 6.")
    assert result(tmp_path, capture(tmp_path, frames=[e]))['primary'] == 'model_contract'


def test_repaired_action_still_counts_as_recovered_when_child_later_crashes(tmp_path):
    frames = [{'recordType': 'STEP_ACTION_REJECTED', 'frameId': 'step', 'metadata': {}},
              {'recordType': 'STEP_ACTION_VALIDATED', 'frameId': 'step', 'metadata': {}},
              error('java.lang.NullPointerException', stack='\tat ai.loomspan.internal.core.ExecutionCoordinator.traceSafeNode(X.java:1)')]
    r = result(tmp_path, capture(tmp_path, frames=frames))
    assert r['recovery']['recoveredModelFrames'] == 1
    assert r['primary'] == 'framework_exception'


def test_completed_workflow_retains_recovery_and_business_failures(tmp_path):
    frames = [{'recordType': 'STEP_ACTION_REJECTED', 'frameId': 'step', 'metadata': {}},
              {'recordType': 'STEP_COMPLETED', 'frameId': 'step', 'metadata': {}}]
    events = [response(completion('{', 'length')), {'event': 'model-request', 'requestId': 'repair',
               'request': {'messages': [{'role': 'system', 'content': 'YOUR PREVIOUS ACTION WAS INVALID'}]}},
              response(completion(), ident='repair')]
    checks = [{'path': 'java', 'check': 'cited source identifiers exist in actual returned evidence', 'passed': False}]
    r = result(tmp_path, capture(tmp_path, status='COMPLETED', frames=frames, events=events, checks=checks))
    assert r['primary'] == 'completed_business_failure'
    assert r['businessStatus'] == 'FAIL'
    assert r['recovery']['truncatedResponses'] == 1
    assert r['recovery']['invalidJsonResponses'] == 1
    assert r['recovery']['correctionRequests'] == 1
    assert r['recovery']['recoveredModelFrames'] == 1


def test_recovered_provider_retry_does_not_label_completed_run_terminal_failure(tmp_path):
    frames = [{'recordType': 'MODEL_ATTEMPT_FAILED', 'frameId': 'model', 'metadata': {
        'attemptId': 'a', 'failureCategory': 'TIMEOUT', 'retryDecision': 'RETRY'}},
        {'recordType': 'MODEL_REQUEST_SENT', 'frameId': 'model', 'metadata': {'providerAttemptNumber': 2}},
        {'recordType': 'MODEL_RESPONSE_RECEIVED', 'frameId': 'model', 'metadata': {}},
        error('com.openai.errors.RateLimitException')]
    r = result(tmp_path, capture(tmp_path, status='COMPLETED', frames=frames))
    assert r['primary'] == 'completed'
    assert r['recovery']['providerRetries'] == 1
    assert r['recovery']['recoveredModelFrames'] == 1
    assert r['providerObservations'][0]['category'] == 'provider_timeout'
    assert r['semanticReview'] == 'PENDING'


@pytest.mark.parametrize('damage', ['missing', 'hash', 'chunks', 'outside'])
def test_incomplete_or_untrusted_trace_cannot_be_called_clean(tmp_path, damage):
    e = error('java.lang.NullPointerException');e['data'] = None
    e['metadata'].update(payloadId='absent', chunkCount=1)
    review = capture(tmp_path, status='COMPLETED', frames=[e] if damage == 'chunks' else [])
    file = tmp_path / 'java/traces/root.ndjson'
    if damage == 'missing': file.unlink()
    if damage == 'hash': file.write_text('{}')
    if damage == 'outside':
        index = json.loads((tmp_path / 'trace-index.json').read_text());index[0]['file'] = '../external.ndjson'
        (tmp_path / 'trace-index.json').write_text(json.dumps(index))
    r = result(tmp_path, review)
    assert r['primary'] != 'completed'
    assert r['businessStatus'] == 'NOT_ASSESSED'
    assert r['evidenceGaps']


def test_sidecar_uses_its_own_case_and_trace(tmp_path):
    java = tmp_path / 'java-capture'; sidecar = tmp_path / 'sidecar-capture'
    capture(java, events=[response({'error': {'message': 'rate limit'}}, 429)])
    review = capture(sidecar, path='sidecar', status='COMPLETED')
    r = result(sidecar, review, 'sidecar')
    assert r['primary'] == 'completed'
    assert r['path'] == 'sidecar'


def test_mixed_paired_run_keeps_java_failure_out_of_sidecar_diagnosis(tmp_path):
    java = tmp_path / 'paired'; sidecar = tmp_path / 'sidecar'
    jr = capture(java, events=[response({'error': {'message': 'rate limit'}}, 429)])
    sr = capture(sidecar, path='sidecar', status='COMPLETED')
    import shutil
    shutil.copytree(sidecar / 'sidecar', java / 'sidecar')
    shutil.copy2(sidecar / 'sidecar-assessment.json', java / 'sidecar-assessment.json')
    for name in ['manifest.json', 'trace-index.json', 'journal.json']:
        a, b = [json.loads((p / name).read_text()) for p in [java, sidecar]]
        value = {'results': a['results'] + b['results']} if name == 'manifest.json' else a + b
        (java / name).write_text(json.dumps(value))
    (java / 'checksums.json').write_text(json.dumps({p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in java.glob('*.json') if p.name != 'checksums.json'}))
    d = diagnose(java, ['java', 'sidecar'], {'checks': jr['checks'] + sr['checks']})
    assert [p['primary'] for p in d['paths']] == ['provider_error', 'completed']


def test_harness_poll_timeout_does_not_assert_provider_timeout(tmp_path):
    review = capture(tmp_path, status='CHECK_ERROR')
    p = tmp_path / 'java-assessment.json';p.write_text(json.dumps({'status': 'CHECK_ERROR', 'errorType': 'TimeoutError'}))
    hashes = json.loads((tmp_path / 'checksums.json').read_text());hashes[p.name] = hashlib.sha256(p.read_bytes()).hexdigest()
    (tmp_path / 'checksums.json').write_text(json.dumps(hashes))
    r = result(tmp_path, review)
    assert r['primary'] == 'execution_limit'
    assert 'Harness polling/collection error' in ' '.join(r['evidenceGaps'])


def test_summary_and_rereport_preserve_acceptance_and_original_bytes(tmp_path):
    cap = tmp_path / 'capture';review = capture(cap, status='COMPLETED', checks=[{
        'path': 'java', 'check': 'business evidence', 'passed': False}])
    suite = tmp_path / 'suite';suite.mkdir()
    report = {'mode': 'evaluate', 'model': 'example/model', 'paths': ['java'], 'status': 'FAIL',
              'runtimeRestored': True, 'stages': [{'scenario': 'baseline', 'capture': str(cap), 'review': review},
              {'scenario': 'service-requests', 'capture': str(cap), 'review': {'checks': [{
                  'check': 'valid live baseline required for service approval', 'passed': False}]}}]}
    summary(suite, report)
    before = {str(p): p.read_bytes() for d in [suite, cap] for p in d.rglob('*') if p.is_file()}
    new = regenerate(suite / 'report.json', tmp_path / 'new-view')
    text = new.read_text()
    assert 'Completed; business checks failed' in text
    assert 'NOT RUN' in text and 'provider access disabled' in text
    assert 'semantic judgment is not automated' in text
    assert all(Path(p).read_bytes() == raw for p, raw in before.items())
    assert json.loads(new.with_name('report.json').read_text())['status'] == 'FAIL'
    with pytest.raises(ValueError, match='outside'):
        regenerate(suite / 'report.json', cap / 'view')
    with pytest.raises(FileExistsError):
        regenerate(suite / 'report.json', new.parent)


def test_runner_failure_report_never_claims_model_quality_or_restoration(tmp_path):
    report = {'mode': 'evaluate', 'model': 'example/model', 'paths': ['java'], 'status': 'FAIL',
              'stages': [], 'errorType': 'ConnectionError', 'error': 'readiness failed'}
    summary(tmp_path, report)
    text = (tmp_path / 'summary.md').read_text()
    assert 'Runner / environment / restoration error' in text
    assert 'not confirmed' in text
