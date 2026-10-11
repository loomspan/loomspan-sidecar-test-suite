"""Exercise actual public host APIs, native transport, bindings and traces without providers."""
from dataclasses import replace
import base64
import json
import time
import uuid
import httpx
from .scenarios import bind, load, REVIEW_AREAS
from trace_payload import payload
from .decisions import verify as verify_decision


def planner_step(case):
    child = case.get('childSkill', 'tsTriageFixed')
    plan = {'capabilityName': case['skill'], 'createdAt': '2026-10-11T00:00:00Z', 'status': 'VALID',
            'tasks': [{'taskId': 'triage', 'title': 'Assess support contact', 'capabilityName': child,
                       'intent': 'Assess the supplied support contact', 'status': 'PENDING', 'dependsOn': [],
                       'expectedOutputs': ['judgments'], 'parallelGroup': None, 'note': ''}]}
    return {'contains': [case['input']['context']['caseId'], case['skill']],
            'systemContains': ['Create an ordered flight plan'],
            'response': {'id': 'authored-plan', 'object': 'chat.completion', 'created': 1,
                         'model': 'openai/gpt-6-luna', 'usage': {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0, 'cost': 0},
                         'choices': [{'index': 0, 'finish_reason': 'stop',
                                      'message': {'role': 'assistant', 'content': json.dumps(plan)}}]},
            'provenance': 'authored-typesafe-protocol-fixture'}


def execute(client, raw, path, token, secrets, bundle, suite, core):
    ident = 'typesafe-' + path + '-' + uuid.uuid4().hex
    case = bind(raw, ident)
    prefix = case['name'] + '/' + path
    headers = {'Authorization': 'Bearer ' + token}
    control = {'X-Control-Key': secrets['control']}
    before_rows = core.database(path)
    before_traces = {r['traceId'] for r in core.trace_catalog(client, path, secrets['observer'])}
    registration = {'suite': 'typesafe-ai', 'mode': 'replay', 'path': path,
                    'nativeRequest': case['request'], 'nativeResponses': case['responses'],
                    'nativePrefix': case.get('nativePrefix', ''),
                    'nativeProvenance': case.get('provenance', 'authored-typesafe-protocol-fixture'),
                    'steps': [planner_step(case)] if case.get('parent') else []}
    r = client.post(core.environment.url(18090, '/control/cases/' + ident), json=registration, headers=control)
    r.raise_for_status()
    result = {'suite': suite.name, 'scenario': case['name'], 'path': path, 'mode': 'mock', 'caseId': ident,
              'coverage': case['coverage'], 'checks': {}, 'businessReview': 'NOT_MODEL_EVALUATION',
              'fixtureOrigin': case.get('provenance', 'authored-typesafe-protocol-fixture'),
              'usage': {'modelCalls': 0, 'paidModelCalls': 0, 'reportedCost': 0, 'traceSeconds': None}}
    checks = result['checks']
    trace, terminal = [], {}
    bundle.add(prefix + '/case.json', case)
    api = core.environment.url(core.PORTS[path]) + '/suites/typesafe-ai'
    try:
        r = client.post(api + '/evaluations/' + case['skill'], json=case['input'],
                        headers={} if case['name'] == 'unauthenticated' else headers)
        if case['outcome'].startswith('HTTP_'):
            checks['expected HTTP rejection'] = r.status_code == int(case['outcome'][5:])
            terminal = {'httpStatus': r.status_code}
        else:
            r.raise_for_status()
            execution = r.json()['id']
            deadline = time.monotonic() + 45
            while time.monotonic() < deadline:
                r = client.get(api + '/executions/' + execution, headers=headers)
                r.raise_for_status()
                terminal = r.json()
                if terminal.get('status') in ('COMPLETED', 'FAILED', 'CANCELLED'):
                    break
                time.sleep(.1)
            checks['expected execution outcome'] = terminal.get('status') == case['outcome']
            if case['outcome'] == 'COMPLETED':
                checks['answers preserved exactly'] = terminal.get('result') is not None and json.loads(terminal['result']) == case['expected']
                verify_decision(client, api, execution, headers, terminal, case, result, bundle, prefix)
                if case['name'] == 'mixed_fixed':
                    checks['impact rejects unrelated scale'] = client.get(api + '/executions/' + execution + '/impact', headers=headers).status_code == 404
                if case['name'] == 'reference_evidence_sparse_java':
                    checks['impact requires authentication'] = client.get(api + '/executions/' + execution + '/impact').status_code == 401
                    other = core.login('luis')
                    bundle.secrets.append(other)
                    checks['impact requires execution owner'] = client.get(api + '/executions/' + execution + '/impact',
                        headers={'Authorization': 'Bearer ' + other}).status_code == 404
            else:
                checks['failure has no substitute result'] = terminal.get('result') is None
            # Finalized trace publication can briefly trail the execution snapshot.
            for attempt in range(10):
                try:
                    trace = core.trace_for(client, path, ident, secrets['observer'], bundle, prefix,
                                           replace(suite, entry_skill=case['skill']), before_traces)
                    break
                except ValueError:
                    if attempt == 9:
                        raise
                    time.sleep(.1)
    except Exception as error:
        result['executionError'] = bundle.error(error)
    finally:
        bundle.add(prefix + '/terminal.json', terminal)
        r = client.get(core.environment.url(18090, '/control/journal'), headers=control)
        r.raise_for_status()
        journal = [event for event in r.json() if event.get('caseId') == ident]
        bundle.add(prefix + '/journal.json', journal)
        native = [e for e in journal if e['event'] == 'native-request']
        recorded = [e for e in journal if e['event'] == 'native-response']
        if recorded:
            checks['fixture provenance retained'] = all(e.get('provenance') == registration['nativeProvenance'] for e in recorded)
        chat = [e for e in journal if e['event'] == 'model-request']
        checks['exact native attempt count'] = len(native) == len(case['responses'])
        checks['exact native requests including retries'] = all(e['request'] == case['request'] for e in native)
        checks['no unexpected requests or fixture fallback'] = not any(e['event'].endswith('rejected') for e in journal)
        checks['one planning call only for parent'] = len(chat) == int(bool(case.get('parent')))
        checks['equipment business rows unchanged'] = core.database(path) == before_rows
        result['usage']['modelCalls'] = sum(r['recordType'] == 'MODEL_RESPONSE_RECEIVED' for r in trace)
        result['usage']['providerAttempts'] = len(native) + len(chat)
        if trace:
            kinds = [r['recordType'] for r in trace]
            result['usage']['traceSeconds'] = max(r['timestamp'] for r in trace) - min(r['timestamp'] for r in trace)
            if case['outcome'] == 'FAILED':
                checks['failure recorded in trace'] = 'ERROR_RECORDED' in kinds
            requests = [payload(r, trace) for r in trace if r['recordType'] == 'MODEL_REQUEST_SENT']
            native_requests = [r for r in requests if r.get('payloadType') == 'evaluation']
            checks['native trace request fidelity'] = all(r['request'] == case['request'] for r in native_requests)
            if native:
                checks['native trace present'] = bool(native_requests)
            responses = [(r, payload(r, trace)) for r in trace if r['recordType'] == 'MODEL_RESPONSE_RECEIVED']
            native_responses = [(r, d) for r, d in responses if d.get('payloadType') == 'evaluation']
            if case.get('usagePrecision'):
                checks['native usage precision'] = bool(native_responses) and all(
                    r.get('metadata', {}).get('usage', {}).get('precision') == case['usagePrecision'] for r, _ in native_responses)
                checks['native usage counts'] = bool(native_responses) and all(
                    r['metadata']['usage']['promptUnits'] == (d['envelope']['usage']['input_tokens'] if case['usagePrecision'] == 'EXACT' else 0)
                    and r['metadata']['usage']['completionUnits'] == (d['envelope']['usage']['output_tokens'] if case['usagePrecision'] == 'EXACT' else 0)
                    and r['metadata']['usage']['totalUnits'] == r['metadata']['usage']['promptUnits'] + r['metadata']['usage']['completionUnits']
                    for r, d in native_responses)
            envelopes = [s['body'] for s in case['responses'] if s.get('status', 200) == 200 and 'body' in s]
            if envelopes and not any(s.get('delaySeconds') for s in case['responses']):
                checks['provider envelope preserved in trace'] = [d.get('envelope') for _, d in native_responses] == envelopes
            raw_bodies = [s['raw'] for s in case['responses'] if 'raw' in s]
            if raw_bodies:
                checks['malformed response preserved in trace'] = [d.get('rawBody') for _, d in native_responses] == raw_bodies
            if case['responses'] and (all(s.get('status', 200) != 200 for s in case['responses']) or case['name'] == 'read_timeout'):
                checks['failed transport has no accounted response'] = not native_responses
            if case['outcome'] == 'COMPLETED' and case['skill'].endswith('Forward'):
                checks['framework forwarding recorded'] = 'RESULT_FORWARDED' in kinds
            if case['outcome'] == 'COMPLETED' and case['skill'].endswith('Summary'):
                checks['framework assembly recorded'] = 'RESULT_ASSEMBLED' in kinds
        result['status'] = 'PROTOCOL_PASS' if all(checks.values()) and 'executionError' not in result else 'FAIL'
    return result


def run(args, parser, suite, core):
    manifest, cases = load(core.ROOT)
    selected = args.scenario or manifest['scenarios']
    paths = [args.path] if args.path else ['java', 'sidecar']
    if args.dry_run:
        print(json.dumps({'suite': suite.name, 'mode': 'mock', 'paths': paths, 'scenarios': selected,
                          'model': 'jev-1.13.0', 'fixtureOrigin': manifest['fixtureOrigin'], 'paidCalls': 0}, indent=2))
        return 0
    secrets = json.loads((core.ROOT / '.runtime/secrets.json').read_bytes())
    bundle = core.Bundle(list(secrets.values()))
    report = {'runId': uuid.uuid4().hex, 'suite': suite.name, 'mode': 'mock', 'status': 'FAIL',
              'fixtureOrigin': manifest['fixtureOrigin'], 'paths': paths, 'scenarios': selected,
              'runtimeRestored': False, 'cases': [], 'reviewAreas': REVIEW_AREAS, 'model': 'jev-1.13.0'}
    try:
        core.ready()
        core.require_offline_provider()
        report['build'] = core.baseline()
        # Capture authored inputs/configuration in the checksummed evidence bundle.
        for file in [core.ROOT / 'fixtures/typesafe-ai/cases.json',
                     *(core.ROOT / 'fixtures/typesafe-ai/reference').glob('*.json'),
                     core.ROOT / 'fixtures/typesafe.py', core.ROOT / 'fixtures/server.py',
                     core.ROOT / 'scripts/suites/typesafe_ai/runner.py',
                     core.ROOT / 'scripts/suites/typesafe_ai/scenarios.py',
                     core.ROOT / 'scripts/suites/typesafe_ai/decisions.py',
                     core.ROOT / 'fixtures/typesafe-ai/impact-policy-cases.json',
                     core.ROOT / 'fixtures/typesafe-ai/policy-reference-expectations.json',
                     core.ROOT / 'apps/python/suites/typesafe_ai/policy.py',
                     core.ROOT / 'apps/python/suites/typesafe_ai/api.py',
                     core.ROOT / 'apps/java/src/main/java/example/suites/typesafeai/policy/ImpactPolicy.java',
                     core.ROOT / 'apps/java/src/main/java/example/suites/typesafeai/api/TypeSafeApi.java',
                     core.ROOT / 'scripts/trace_payload.py',
                     core.ROOT / 'config/runtime-source.json',
                     *(core.ROOT / suite.skill_directory).glob('*.yaml'),
                     core.ROOT / 'config/java.yaml', core.ROOT / 'config/sidecar.yaml']:
            bundle.add('source/' + file.relative_to(core.ROOT).as_posix(), file.read_bytes())
        with httpx.Client(timeout=60, trust_env=False) as client:
            token, expires = None, 0
            for name in selected:
                raw = next(c for c in cases if c['name'] == name)
                for path in paths:
                    # Reuse a real PKCE login across these short offline cases. Refresh
                    # before expiry; this decoded timestamp is not an auth decision.
                    if time.time() + 60 >= expires:
                        token = core.login('maya')
                        bundle.secrets.append(token)
                        segment = token.split('.')[1]
                        expires = json.loads(base64.urlsafe_b64decode(segment + '=' * (-len(segment) % 4)))['exp']
                    result = execute(client, raw, path, token, secrets, bundle, suite, core)
                    report['cases'].append(result)
                    print(name + ' / ' + path + ': ' + result['status'], flush=True)
                    if result['status'] == 'FAIL':
                        print('Failed checks: ' + ', '.join(k for k, ok in result['checks'].items() if not ok), flush=True)
                        if result.get('executionError'):
                            print(result['executionError'], flush=True)
                        raise RuntimeError('TypeSafe protocol case failed; stopped without provider fallback')
        report['status'] = 'PROTOCOL_PASS'
    except (Exception, KeyboardInterrupt) as error:
        report['error'] = bundle.error(error)
    finally:
        try:
            core.require_offline_provider()
            report['runtimeRestored'] = True
        except Exception as error:
            report['error'] = bundle.error(error)
            report['status'] = 'FAIL'
        core.write_report(report, bundle, args.output)
    return 0 if report['status'] == 'PROTOCOL_PASS' else 1
