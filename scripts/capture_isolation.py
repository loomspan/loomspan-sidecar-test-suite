"""Two complete reviewed cases per application, with independently observed read gates."""
import json
import time
import uuid
import httpx
from baseline import baseline
from capture import collect, wait
from capture_step_correction import records
from capture_reviewed_replay import verify_source, require_offline_provider
from capture_business_diagnostic import normalized
from curate_business_replay import CASE, ROOT, digest
from finalize_evidence import finalize
from login import login
from readiness import ready

GATES = ['serviceHistory', 'referenceEvidence']


def run():
    ready()
    require_offline_provider()
    build = baseline()
    fixture = ROOT / 'fixtures/replay/business-reviewed-v1.json'
    bundle = json.loads(fixture.read_bytes())
    approval = json.loads((fixture.parent / 'business-reviewed-v1-approval.json').read_bytes())
    if approval['fixtureSha256'] != digest(fixture) or approval['status'] != 'APPROVED_FOR_SCOPED_OFFLINE_REPLAY':
        raise ValueError('Reviewed fixture approval/hash mismatch')
    for scenario in ['baseline', 'priority']:
        for sample in bundle['scenarios'][scenario].values():
            verify_source(sample)
    out = ROOT / 'evidence' / ('gated-isolation-' + time.strftime('%Y%m%d-%H%M%S'))
    out.mkdir()
    secrets = json.loads((ROOT / '.runtime/secrets.json').read_text())
    tokens = {user: login(user) for user in ['maya', 'luis']}
    before = records()
    cases, observations = [], []
    results = {'baseline': [], 'priority': []}
    for scenario in results:
        (out / scenario).mkdir()
        (out / scenario / 'business-records-before.json').write_text(json.dumps(before, indent=2))
    with httpx.Client(timeout=300, trust_env=False) as client:
        control = {'X-Control-Key': secrets['control']}

        def journal():
            r = client.get('http://127.0.0.1:18090/control/journal', headers=control)
            r.raise_for_status()
            return r.json()

        def release(case):
            for gate in GATES:
                r = client.post(f'http://127.0.0.1:18090/control/gates/{case}/{gate}', headers=control)
                r.raise_for_status()

        def submit(path, api, scenario, user):
            sample = bundle['scenarios'][scenario][path]
            case = 'isolation-' + path + '-' + scenario + '-' + uuid.uuid4().hex
            steps = normalized(sample['steps'], CASE, case)
            reg = {'mode': 'replay', 'path': path, 'steps': steps}
            if scenario == 'baseline':
                reg['gates'] = GATES
            body = normalized(sample['input'], CASE, case)
            d = out / scenario
            for name, value in [('registration', reg), ('input', body), ('expected', normalized(sample['expected'], CASE, case))]:
                (d / (path + '-' + name + '.json')).write_text(json.dumps(value, indent=2))
            r = client.post('http://127.0.0.1:18090/control/cases/' + case, json=reg, headers=control)
            r.raise_for_status()
            cases.append(case)
            r = client.post(api + '/assessments', json=body, headers={'Authorization': 'Bearer ' + tokens[user]})
            r.raise_for_status()
            item = {'path': path, 'caseId': case, 'executionId': r.json()['id'], 'expectedCalls': len(steps), 'caller': user}
            results[scenario].append(item)
            return item

        try:
            for path, port in [('java', 18081), ('sidecar', 18082)]:
                api = f'http://127.0.0.1:{port}'
                blocked = submit(path, api, 'baseline', 'maya')
                try:
                    deadline = time.monotonic() + 60
                    while time.monotonic() < deadline:
                        entered = [e for e in journal() if e.get('caseId') == blocked['caseId'] and e['event'] == 'entered' and e.get('kind') in GATES]
                        if {e['kind'] for e in entered} == set(GATES):
                            break
                        time.sleep(.25)
                    else:
                        raise TimeoutError('Both independent reads did not enter before release: ' + path)
                    print(path, 'both read gates entered', flush=True)
                    other = submit(path, api, 'priority', 'luis')
                    terminal = wait(client, api, other['executionId'], tokens['luis'], timeout=90)
                    other['status'] = terminal['status']
                    (out / 'priority' / (path + '-assessment.json')).write_text(json.dumps(terminal, indent=2))
                    # Persist the real HTTP observation while both gates remain closed.
                    r = client.get(api + '/v1/executions/' + blocked['executionId'], headers={'Authorization': 'Bearer ' + tokens['maya']})
                    r.raise_for_status()
                    obs = {'path': path, 'blockedCaseId': blocked['caseId'], 'otherCaseId': other['caseId'],
                           'timeNs': time.time_ns(), 'blockedWhileOtherComplete': r.json(), 'otherStatus': terminal['status'],
                           'crossCallerPolls': []}
                    for item, wrong in [(blocked, 'luis'), (other, 'maya')]:
                        r = client.get(api + '/v1/executions/' + item['executionId'], headers={'Authorization': 'Bearer ' + tokens[wrong]})
                        obs['crossCallerPolls'].append({'executionId': item['executionId'], 'caller': wrong, 'httpStatus': r.status_code})
                    observations.append(obs)
                    (out / 'observations.json').write_text(json.dumps(observations, indent=2))
                    print(path, 'other case', terminal['status'], 'while baseline', obs['blockedWhileOtherComplete']['status'], flush=True)
                finally:
                    release(blocked['caseId'])
                terminal = wait(client, api, blocked['executionId'], tokens['maya'], timeout=90)
                blocked['status'] = terminal['status']
                (out / 'baseline' / (path + '-assessment.json')).write_text(json.dumps(terminal, indent=2))
                print(path, 'released baseline', terminal['status'], flush=True)
        finally:
            after = records()
            for scenario, items in results.items():
                d = out / scenario
                collect(client, d, [i['caseId'] for i in items], secrets, list(tokens.values()))
                (d / 'business-records-after.json').write_text(json.dumps(after, indent=2))
                (d / 'manifest.json').write_text(json.dumps({**build, 'mode': 'offline reviewed business replay',
                    'scenario': scenario, 'diagnosticSha256': digest(fixture), 'approved': False, 'paidCalls': 0,
                    'results': items, 'scope': 'Two-case gated isolation, unchanged reviewed source; baseline Maya, priority Luis',
                    'sources': {p: {k:v for k,v in s.items() if k not in ['steps','input','expected']}
                                for p,s in bundle['scenarios'][scenario].items()}}, indent=2))
                finalize(d)
            (out / 'manifest.json').write_text(json.dumps({**build, 'paidCalls': 0, 'gates': GATES,
                'providerDisabledAtStart': True,
                'cases': cases, 'scope': 'Two complete distinct callers/cases per application; no broader load/update claim'}, indent=2))
            (out / 'observations.json').write_text(json.dumps(observations, indent=2))
            finalize(out)
            print(out, flush=True)
    return out


if __name__ == '__main__':
    run()
