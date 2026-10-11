"""Bounded native live evaluation. No chat calls, retries, fallback or auto-promotion."""
import base64
from contextlib import contextmanager
from dataclasses import replace
import json
import math
import os
import tempfile
import time
import uuid
import zipfile
import httpx
import yaml
from .scenarios import bind
from trace_payload import payload
from .decisions import verify as verify_decision, summarize as summarize_decisions


def selection(args, root):
    pack = json.loads((root / 'fixtures/typesafe-ai/live-cases.json').read_bytes())
    if args.model != pack['model'] or args.skill_model or args.reasoning != 'medium':
        raise ValueError('Native live scope pins jev-1.13.0; chat/reasoning overrides are unsupported')
    names = list(dict.fromkeys(args.scenario or pack.get('defaultScenarios', [c['name'] for c in pack['cases']])))
    catalog = {c['name']: c for c in pack['cases']}
    if set(names) - set(catalog):
        raise ValueError('Only predeclared live-case definitions are eligible for native live execution')
    paths = [args.path or 'java'] if args.mode == 'evaluate' else ['java', 'sidecar']
    if len(names) * len(paths) > 12:
        raise ValueError('Native live batch exceeds 12 physical sends')
    return [catalog[n] for n in names], paths


@contextmanager
def runtime(core, directory, paths, report):
    if os.getenv('LOOMSPAN_RUN_OVERLAY') or os.getenv('LOOMSPAN_MODEL_CONFIG_DIRECTORY'):
        raise RuntimeError('Native live requires normal provider-disabled runtime')
    core.require_offline_provider()
    services = {'fixtures': {'environment': {'OPENROUTER_API_KEY': '',
        'LOOMSPAN_TYPESAFE_API_KEY': '${LOOMSPAN_TYPESAFE_API_KEY:?TypeSafe key required}',
        'TYPESAFE_LIVE_RUN': report['runId']}}}
    for path in paths:
        config = yaml.safe_load((core.ROOT / 'config' / (path + '.yaml')).read_bytes())
        native = config['loomspan']['connections']['typesafeTriage']
        if native['base-url'] != 'http://fixtures:8080/typesafe/' + path:
            raise ValueError('Native live requires the bounded fixture gateway')
        native['request-timeout'] = '60s'
        native['provider-retry'] = {'enabled': False, 'max-attempts': 1}
        target = directory / (path + '.yaml')
        target.write_text(yaml.safe_dump(config, sort_keys=False), encoding='utf-8')
        services[path] = {'volumes': [target.as_posix() + ':/config/runtime.yaml:ro']}
    overlay = directory / 'compose.yaml'
    overlay.write_text(yaml.safe_dump({'services': services}), encoding='utf-8')
    report['runtimeRestored'] = False
    try:
        os.environ['LOOMSPAN_RUN_OVERLAY'] = str(overlay)
        core.command(core.environment.compose() + ['up', '-d', '--no-deps', '--force-recreate', 'fixtures', *paths])
        core.ready()
        core.verify_mounted(directory, paths)
        yield
    finally:
        os.environ.pop('LOOMSPAN_RUN_OVERLAY', None)
        core.command(core.environment.compose() + ['up', '-d', '--no-deps', '--force-recreate', 'fixtures', *paths])
        core.ready()
        core.require_offline_provider()
        report['runtimeRestored'] = True


def answer_contract(answers, questions):
    def number(v, lo, hi):
        return type(v) in (int, float) and math.isfinite(v) and lo <= v <= hi
    if not isinstance(answers, dict) or set(answers) != set(questions):
        return False
    for key, question in questions.items():
        a = answers[key]
        kind = question['type']
        if not isinstance(a, dict) or a.get('type') != kind:
            return False
        if kind == 'noul':
            if not number(a.get('noul'), 0, 1): return False
            continue
        keys = set(question['criteria']) if kind == 'choice' else {str(i) for i in range(len(question['criteria']))}
        probabilities = a.get('probabilities')
        if (not isinstance(probabilities, dict) or set(probabilities) != keys
                or not all(number(v, 0, 1) for v in probabilities.values())
                or abs(sum(probabilities.values()) - 1) > .001
                or not number(a.get('confidence'), 0, 1)):
            return False
        if kind == 'choice':
            if a.get('choice') not in keys or probabilities[a['choice']] < max(probabilities.values()) - .001: return False
        elif (not number(a.get('score'), 0, len(keys)-1)
              or abs(a['score'] - sum(int(k)*v for k, v in probabilities.items())) > .01 + 1e-12):
            return False
    return True


def review_flags(case, answers):
    flags = list(case['rubric'].get('manual', []))
    for key in ('department', 'repeat', 'impact', 'impactEvidence'):
        if key not in case['rubric'] or key not in answers: continue
        expected = case['rubric'][key]
        value = answers[key].get({'department': 'choice', 'repeat': 'noul', 'impact': 'score', 'impactEvidence': 'noul'}[key])
        ok = value in expected if key == 'department' else isinstance(value, (int, float)) and expected[0] <= value <= expected[1]
        if not ok: flags.append(key + ': outside the predeclared expectation ' + str(expected))
    return flags


def resume_capture(core, previous, cases, paths, bundle):
    """Keep original evidence and reuse only unspent permits, never reissue a send."""
    with zipfile.ZipFile(previous / 'bundle.zip') as archive:
        hashes = json.loads(archive.read('checksums.json'))
        if any(core.digest(archive.read(name)) != digest for name, digest in hashes.items()):
            raise ValueError('Previous capture checksum mismatch')
        original = json.loads(archive.read('report.json'))
        if original['suite'] != 'typesafe-ai' or not original['runtimeRestored'] or original['model'] != 'jev-1.13.0':
            raise ValueError('Previous capture is not eligible for continuation')
        ledger = json.loads(archive.read('send-ledger.json'))
        file = core.ROOT / '.runtime/fixture' / ('typesafe-live-' + original['runId'] + '.json')
        if json.loads(file.read_bytes()) != ledger:
            raise ValueError('Live ledger changed since capture; refusing uncertain continuation')
        for name in archive.namelist():
            raw = archive.read(name)
            bundle.add('initial/' + name, raw)
            if name.startswith('source/config/') and (core.ROOT / name.removeprefix('source/')).read_bytes() != raw:
                raise ValueError('Authored configuration changed since capture')
        reassessed = []
        for result in original['cases']:
            prefix = result['scenario'] + '/' + result['path']
            case = json.loads(archive.read(prefix + '/case.json'))
            prior = dict(result['checks'])
            if set(k for k, v in prior.items() if not v) - {'typed answer contract'} or result.get('executionError'):
                raise ValueError('Previous mechanical failure requires separate investigation')
            result['checks']['typed answer contract'] = answer_contract(result.get('answers'), case['request']['questions'])
            if not all(result['checks'].values()): raise ValueError('Captured answer still fails offline checks')
            result['reviewFlags'] = review_flags(case, result['answers'])
            result['status'] = 'CHECKS_PASS_REVIEW_REQUIRED'
            if result['checks'] != prior:
                reassessed.append({'scenario': result['scenario'], 'path': result['path'], 'previousChecks': prior,
                    'reason': 'Corrected floating-point comparison at the existing 0.01 Score consistency tolerance; no new provider call.'})
            for name in archive.namelist():
                if name.startswith(prefix + '/'): bundle.add(name, archive.read(name))
    scheduled = []
    for ident, permit in ledger['permits'].items():
        if permit['used']: continue
        matches = [bind(c, ident) for c in cases if bind(c, ident)['request'] == permit['request']]
        if len(matches) != 1 or permit['path'] not in paths: raise ValueError('Remaining permit no longer matches selected live scope')
        scheduled.append((matches[0], permit['path']))
    if not scheduled: raise ValueError('No unused permits remain')
    original.update(status='FAIL', resumedFrom=str(previous), offlineReassessment=reassessed)
    original.pop('error', None)
    return original, ledger, file, scheduled


def execute(core, client, case, path, token, secrets, suite, bundle):
    ident = case['input']['context']['caseId']
    prefix = case['name'] + '/' + path
    headers = {'Authorization': 'Bearer ' + token}
    control = {'X-Control-Key': secrets['control']}
    before = core.database(path)
    old_traces = {r['traceId'] for r in core.trace_catalog(client, path, secrets['observer'])}
    result = {'suite': suite.name, 'scenario': case['name'], 'path': path, 'caseId': ident,
        'status': 'FAIL', 'checks': {}, 'businessReview': 'PENDING_SEMANTIC_REVIEW',
        'usage': {'modelCalls': 0, 'paidModelCalls': 0, 'reportedCost': None}}
    terminal, trace, events = {}, [], []
    bundle.add(prefix + '/case.json', case)
    try:
        client.post(core.environment.url(18090, '/control/cases/' + ident), headers=control,
            json={'suite': suite.name, 'mode': 'live', 'path': path, 'steps': [], 'nativeRequest': case['request']}).raise_for_status()
        api = core.environment.url(core.PORTS[path]) + '/suites/typesafe-ai'
        r = client.post(api + '/evaluations/' + case['skill'], headers=headers, json=case['input'])
        r.raise_for_status()
        execution = r.json()['id']
        deadline = time.monotonic() + 90
        while time.monotonic() < deadline:
            r = client.get(api + '/executions/' + execution, headers=headers)
            r.raise_for_status()
            terminal = r.json()
            if terminal.get('status') in ('COMPLETED', 'FAILED', 'CANCELLED'): break
            time.sleep(.1)
        result['checks']['completed'] = terminal.get('status') == 'COMPLETED'
        verify_decision(client, api, execution, headers, terminal, case, result, bundle, prefix)
        for attempt in range(20):
            try:
                trace = core.trace_for(client, path, ident, secrets['observer'], bundle, prefix,
                                       replace(suite, entry_skill=case['skill']), old_traces)
                break
            except ValueError:
                if attempt == 19: raise
                time.sleep(.1)
    except Exception as error:
        result['executionError'] = bundle.error(error)
    finally:
        bundle.add(prefix + '/terminal.json', terminal)
        r = client.get(core.environment.url(18090, '/control/journal'), headers=control)
        r.raise_for_status()
        events = [e for e in r.json() if e.get('caseId') == ident]
        bundle.add(prefix + '/journal.json', events)
        sends = [e for e in events if e['event'] == 'native-live-attempt']
        requests = [e for e in events if e['event'] == 'native-request']
        responses = [e for e in events if e['event'] == 'native-response']
        checks = result['checks']
        checks['exactly one physical send and request'] = len(sends) == len(requests) == 1
        checks['exact native request'] = len(requests) == 1 and requests[0]['request'] == case['request']
        checks['no chat calls'] = not any(e['event'] == 'model-request' for e in events)
        checks['successful live response'] = len(responses) == 1 and responses[0]['status'] == 200 and responses[0]['provenance'] == 'live TypeSafe'
        checks['equipment data unchanged'] = core.database(path) == before
        result['usage']['paidModelCalls'] = len(sends)  # Attempts may be billable even if no response arrives.
        result['usage']['modelCalls'] = sum(r['recordType'] == 'MODEL_RESPONSE_RECEIVED' for r in trace)
        if checks['successful live response']:
            envelope = responses[0]['response']
            envelope_object = envelope if isinstance(envelope, dict) else {}
            answers = envelope_object.get('answers')
            result['answers'] = answers
            checks['pinned served model'] = envelope_object.get('model') == 'jev-1.13.0'
            checks['typed answer contract'] = answer_contract(answers, case['request']['questions'])
            checks['exact answer passthrough'] = terminal.get('result') is not None and json.loads(terminal['result']) == answers
            request_records = [payload(r, trace) for r in trace if r['recordType'] == 'MODEL_REQUEST_SENT']
            response_records = [r for r in trace if r['recordType'] == 'MODEL_RESPONSE_RECEIVED']
            checks['traced request fidelity'] = len(request_records) == 1 and request_records[0].get('request') == case['request']
            checks['traced envelope fidelity'] = len(response_records) == 1 and payload(response_records[0], trace).get('envelope') == envelope
            usage = envelope_object.get('usage', {})
            usage = usage if isinstance(usage, dict) else {}
            result['usage']['nativeUsage'] = usage
            valid_usage = all(type(usage.get(k)) is int and usage[k] >= 0 for k in ('input_tokens', 'output_tokens'))
            checks['exact usage accounting'] = valid_usage and len(response_records) == 1 and response_records[0]['metadata'].get('usage') == {
                'precision': 'EXACT', 'promptUnits': usage.get('input_tokens'), 'completionUnits': usage.get('output_tokens'),
                'totalUnits': usage.get('input_tokens', 0) + usage.get('output_tokens', 0)}
            if checks['typed answer contract']:
                result['reviewFlags'] = review_flags(case, answers)
        if trace:
            result['usage']['traceSeconds'] = max(r['timestamp'] for r in trace) - min(r['timestamp'] for r in trace)
        result['status'] = 'CHECKS_PASS_REVIEW_REQUIRED' if all(checks.values()) and 'executionError' not in result else 'FAIL'
    return result


def run(args, parser, suite, core):
    try:
        cases, paths = selection(args, core.ROOT)
    except ValueError as error:
        parser.error(str(error))
    if args.dry_run:
        if getattr(args, 'resume_capture', None):
            previous, _, _, pending = resume_capture(core, args.resume_capture, cases, paths, core.Bundle([]))
            print(json.dumps({'suite': suite.name, 'mode': args.mode, 'model': args.model,
                'originalRunId': previous['runId'], 'maximumPaidCalls': len(pending), 'retries': False,
                'requests': [{'scenario': c['name'], 'path': path} for c, path in pending]}, indent=2))
            return 0
        print(json.dumps({'suite': suite.name, 'mode': args.mode, 'model': args.model,
            'scenarios': [c['name'] for c in cases], 'paths': paths, 'maximumPaidCalls': len(cases)*len(paths),
            'retries': False, 'chatCalls': 0}, indent=2))
        return 0
    if not os.getenv('LOOMSPAN_TYPESAFE_API_KEY'):
        parser.error('LOOMSPAN_TYPESAFE_API_KEY is required; no runtime changes made')
    secrets = json.loads((core.ROOT / '.runtime/secrets.json').read_bytes())
    bundle = core.Bundle([*secrets.values(), os.environ['LOOMSPAN_TYPESAFE_API_KEY']])
    report = {'runId': uuid.uuid4().hex, 'suite': suite.name, 'mode': args.mode, 'model': args.model,
        'status': 'FAIL', 'runtimeRestored': False, 'cases': [], 'businessReview': 'PENDING_SEMANTIC_REVIEW',
        'replayApproved': False, 'reviewAreas': ['Compare answers with the predeclared rubric; flags are not automatic acceptance.',
            'Review incomplete/ambiguous contacts separately; do not infer calibration from this small batch.']}
    scheduled = [(bind(c, 'typesafe-' + path + '-' + uuid.uuid4().hex), path) for c in cases for path in paths]
    plan = {'runId': report['runId'], 'permits': {c['input']['context']['caseId']:
            {'request': c['request'], 'path': path, 'used': False} for c, path in scheduled}}
    plan_file = core.ROOT / '.runtime/fixture' / ('typesafe-live-' + report['runId'] + '.json')
    resumed = bool(getattr(args, 'resume_capture', None))
    if resumed:
        report, plan, plan_file, scheduled = resume_capture(core, args.resume_capture, cases, paths, bundle)
    try:
        core.ready()
        core.require_offline_provider()
        report['runtimeRestored'] = True
        report['build'] = core.baseline()
        for file in [*(core.ROOT / 'config').rglob('*.yaml'), core.ROOT / 'fixtures/typesafe-ai/live-cases.json',
                     core.ROOT / 'apps/python/suites/typesafe_ai/policy.py',
                     core.ROOT / 'apps/python/suites/typesafe_ai/api.py',
                     core.ROOT / 'apps/java/src/main/java/example/suites/typesafeai/policy/ImpactPolicy.java',
                     core.ROOT / 'apps/java/src/main/java/example/suites/typesafeai/api/TypeSafeApi.java',
                     core.ROOT / 'scripts/suites/typesafe_ai/decisions.py',
                     core.ROOT / 'fixtures/typesafe.py', core.ROOT / 'scripts/suites/typesafe_ai/live.py']:
            bundle.add('source/' + file.relative_to(core.ROOT).as_posix(), file.read_bytes())
        if not resumed:
            with plan_file.open('x', encoding='utf-8') as stream: json.dump(plan, stream)
        with tempfile.TemporaryDirectory(prefix='typesafe-live-', dir=core.ROOT / '.runtime') as temporary:
            from pathlib import Path
            directory = Path(temporary)
            with runtime(core, directory, paths, report):
                for file in directory.glob('*.yaml'): bundle.add('effective/' + file.name, file.read_bytes())
                token, expires = None, 0
                with httpx.Client(timeout=100, trust_env=False) as client:
                    for case, path in scheduled:
                        if time.time() + 120 >= expires:
                            token = core.login('maya')
                            bundle.secrets.append(token)
                            segment = token.split('.')[1]
                            expires = json.loads(base64.urlsafe_b64decode(segment + '=' * (-len(segment) % 4)))['exp']
                        result = execute(core, client, case, path, token, secrets, suite, bundle)
                        report['cases'].append(result)
                        print(case['name'] + '/' + path + ': ' + result['status'], flush=True)
                        if result['status'] == 'FAIL':
                            raise RuntimeError('Unexpected native live failure; remaining paid cases stopped')
        report['status'] = 'CHECKS_PASS_REVIEW_REQUIRED'
    except (Exception, KeyboardInterrupt) as error:
        report['error'] = bundle.error(error)
    finally:
        report['decisionEvaluation'] = summarize_decisions(report['cases'])
        if plan_file.exists():
            ledger = json.loads(plan_file.read_bytes())
            report['reservedProviderAttempts'] = sum(p['used'] for p in ledger['permits'].values())
            bundle.add('send-ledger.json', ledger)
        core.write_report(report, bundle, args.output)
    return 0 if report['status'] == 'CHECKS_PASS_REVIEW_REQUIRED' else 1
