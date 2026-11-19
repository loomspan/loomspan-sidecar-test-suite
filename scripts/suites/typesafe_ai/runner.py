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
    plan = {'capabilityName': 'default-' + case['skill'], 'createdAt': '2026-10-11T00:00:00Z', 'status': 'VALID',
            'tasks': [{'taskId': 'triage', 'title': 'Assess support contact', 'capabilityName': 'default-' + child,
                       'intent': 'Assess the supplied support contact', 'status': 'PENDING', 'dependsOn': [],
                       'expectedOutputs': ['judgments'], 'parallelGroup': None, 'note': ''}]}
    return {'contains': [case['input']['context']['caseId'], 'default-' + case['skill']],
            'systemContains': ['Create an ordered flight plan'],
            'response': {"id": "resp_fixture", "object": "response", "created_at": 0, "status": "completed", "model": 'gpt-6-luna', "output": [{"id": "msg_fixture", "type": "message", "role": "assistant", "status": "completed", "content": [{"type": "output_text", "text": json.dumps(plan), "annotations": []}]}], "usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}},
            'provenance': 'authored-typesafe-protocol-fixture'}


def check_executor_trace(checks, trace, case, path):
    records = [payload(r, trace) for r in trace if r['recordType'] == 'EXECUTOR_DIAGNOSTIC_RECORDED']
    messages = []
    requests, replies, failures, retries = [], [], [], []
    endpoint = f'http://fixtures:8080/typesafe/{path}' + case.get('nativePrefix', '/api') + '/v1/systemone'
    for attempt, response in enumerate(case['responses'], start=1):
        messages.append('TypeSafe request')
        requests.append((attempt, endpoint, case['request']))
        if response.get('status', 200) != 200:
            messages.append('TypeSafe HTTP failure')
            failures.append((attempt, response['status'], response['body'], False, False))
            if attempt < len(case['responses']):
                messages.append('TypeSafe retry scheduled')
                retries.append((attempt, 250 if attempt == 1 else 500))
        elif 'body' in response:
            messages.append('TypeSafe response')
            replies.append({'attempt': attempt, 'response': response['body']})
    checks['exact executor diagnostic sequence'] = [r.get('message') for r in records] == messages
    def data(message):
        return [r['data'] for r in records if r.get('message') == message]
    checks['executor trace request fidelity'] = [
        (d['attempt'], d['endpoint'], json.loads(d['body'])) for d in data('TypeSafe request')] == requests
    checks['complete provider envelope and usage in trace'] = data('TypeSafe response') == replies
    checks['executor HTTP error details'] = [
        (d['attempt'], d['status'], json.loads(d['body']), d['truncated'], d['unavailable'])
        for d in data('TypeSafe HTTP failure')] == failures
    checks['executor retry schedule'] = [
        (d['failedAttempt'], d['delayMillis']) for d in data('TypeSafe retry scheduled')] == retries
    planning_calls = int(bool(case.get('parent')))
    for kind in ('MODEL_REQUEST_SENT', 'MODEL_RESPONSE_RECEIVED'):
        events = [r['metadata'] for r in trace if r['recordType'] == kind]
        checks['only planner accounted for ' + kind] = (
            len(events) == planning_calls and all(e.get('segment') == 'planning' for e in events))
    totals = [r['metadata']['sessionUsageSnapshot'] for r in trace if r['recordType'] == 'TRACE_COMPLETED']
    expected = {'modelCalls': planning_calls, 'providerAttempts': planning_calls,
                'exactModelResponses': planning_calls, 'heuristicModelResponses': 0,
                'unavailableModelResponses': 0, 'promptUnits': 0, 'completionUnits': 0, 'totalUnits': 0}
    checks['executor usage excluded from framework totals'] = (
        len(totals) == 1 and all(totals[0].get(k) == v for k, v in expected.items()))
    if case['outcome'] == 'FAILED':
        errors = [payload(r, trace) for r in trace if r['recordType'] == 'ERROR_RECORDED']
        if case['name'] == 'embedded_object_rejected':
            checks['structured transform rejects non-scalar message'] = any(
                'Expected text, number or boolean for message' in e.get('exceptionMessage', '') for e in errors)
        elif not case['responses']:
            field = {'boundary_singleton_null': 'questions.impact.criteria[0]',
                     'empty_choice': 'questions.department.criteria', 'too_many_choices': 'questions.department.criteria',
                     'empty_score': 'questions.impact.criteria', 'too_many_levels': 'questions.impact.criteria',
                     'invalid_noul': 'questions.repeat.criteria.yes', 'missing_path': 'state'}[case['name']]
            checks['resolved request rejected at expected field'] = any(
                e.get('exceptionMessage', '').startswith('input.' + field + ':') for e in errors)
        elif case['name'] == 'malformed_json':
            checks['malformed success fails JSON decoding'] = any(
                e.get('exceptionType', '').endswith('.StreamReadException') for e in errors)
        elif case['name'] in {'binding_rejects_value', 'binding_missing_answer'}:
            cause = 'binding_output_validation:' if case['name'] == 'binding_rejects_value' else 'binding_source_unavailable:'
            checks['parent rejects invalid binding'] = any(e.get('exceptionMessage', '').startswith(cause) for e in errors)


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
                    'nativePrefix': case.get('nativePrefix', '/api'),
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
                actual = json.loads(terminal['result']) if terminal.get('result') is not None else None
                if not case['skill'].endswith('Summary'):
                    checks['complete executor result'] = actual == case['responses'][-1]['body']
                    actual = actual.get('answers') if isinstance(actual, dict) else None
                checks['answers preserved exactly'] = actual == case['expected']
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
                except (ValueError, httpx.RemoteProtocolError):
                    if attempt == 9:
                        raise
                    result['traceReadRetries'] = attempt + 1
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
        checks['exact fixture responses'] = [
            (e['stage'], e['status'], e['response'], e['rawBody']) for e in recorded] == [
            (i, response.get('status', 200), response.get('body'), response.get('raw'))
            for i, response in enumerate(case['responses'])]
        if not case['outcome'].startswith('HTTP_'):
            checks['correlated execution trace captured'] = bool(trace)
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
            check_executor_trace(checks, trace, case, path)
            if case['outcome'] == 'COMPLETED' and case['skill'].endswith('Forward'):
                checks['framework forwarding recorded'] = 'RESULT_FORWARDED' in kinds
            if case['outcome'] == 'COMPLETED' and case['skill'].endswith('Summary'):
                checks['framework assembly recorded'] = 'RESULT_ASSEMBLED' in kinds
        result['status'] = 'PROTOCOL_PASS' if all(checks.values()) and 'executionError' not in result else 'FAIL'
    return result


def run(args, parser, suite, core):
    manifest, cases = load(core.ROOT)
    selected = args.scenario or manifest['scenarios']
    origin = manifest['fixtureOrigin']
    paths = [args.path] if args.path else ['java', 'sidecar']
    if args.dry_run:
        print(json.dumps({'suite': suite.name, 'mode': 'mock', 'paths': paths, 'scenarios': selected,
                          'model': 'jev-1.13.0', 'fixtureOrigin': origin, 'paidCalls': 0}, indent=2))
        return 0
    secrets = json.loads((core.ROOT / '.runtime/secrets.json').read_bytes())
    bundle = core.Bundle(list(secrets.values()))
    report = {'runId': uuid.uuid4().hex, 'suite': suite.name, 'mode': 'mock', 'status': 'FAIL',
              'fixtureOrigin': origin, 'paths': paths, 'scenarios': selected,
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
                     *(core.ROOT / 'fixtures/typesafe-ai/reference-partial-outage').glob('*.json'),
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

        report['status'] = 'PROTOCOL_PASS' if all(c['status'] == 'PROTOCOL_PASS' for c in report['cases']) else 'FAIL'
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
