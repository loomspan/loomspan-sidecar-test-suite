"""Inject a missing field in a captured comparison; one real Muse correction per path.

No synthetic correction or parent final. Direct comparison, not full-workflow recovery.
"""
import argparse
import copy
import hashlib
import json
import pathlib
import time
import uuid
import httpx
from baseline import baseline
from capture import collect, wait
from capture_step_correction import envelope, records
from finalize_evidence import finalize
from inspect_capture import mission
from login import login
from model_profile import model_profile
from readiness import ready

ROOT = pathlib.Path(__file__).resolve().parents[1]


def sample(source, path, case):
    events = json.loads((source / 'journal.json').read_text())
    calls = [e for e in events if e['event'] == 'model-request' and e.get('path') == path
             and mission(e['request'], 'compareOptions')]
    if not calls:
        raise ValueError('No captured comparison')
    call = calls[-1]
    replies = [e for e in events if e['event'] == 'model-response' and e.get('path') == path
               and e.get('requestId') == call['requestId'] and e.get('caseId') == call['caseId']]
    if len(replies) != 1 or replies[0].get('provenance') != 'live OpenRouter' or replies[0].get('status') != 200:
        raise ValueError('No unique real comparison response')
    raw = replies[0]['response']['choices'][0]['message']['content']
    original = json.loads(raw)
    if not original.get('nextDecision') or len(original.get('quotes', [])) != 2:
        raise ValueError('Incomplete comparison is not a mutation source')
    if original.get('selectedOption') not in ['expedited', 'standard', 'loaner', 'replacement', 'defer', 'undecided']:
        raise ValueError('Source selection already violates the current contract')
    text = next(m['content'] for m in call['request']['messages'] if m['role'] == 'user'
                and m['content'].startswith('Mission objective:'))
    body = json.JSONDecoder().raw_decode(text.split('Canonical mission input:\n', 1)[1].lstrip())[0]
    old = call['caseId']
    body = json.loads(json.dumps(body).replace(old, case))
    injected = json.loads(json.dumps(original).replace(old, case))
    injected.pop('nextDecision')
    provenance = {'kind': 'Captured real comparison with deliberate missing-field mutation',
        'sourceCapture': source.name, 'sourcePath': path, 'sourceRequestId': call['requestId'],
        'sourceModel': call['request']['model'], 'sourceReasoning': call['request']['reasoning_effort'],
        'sourceContentSha256': hashlib.sha256(raw.encode()).hexdigest(),
        'sourceJournalSha256': hashlib.sha256((source / 'journal.json').read_bytes()).hexdigest(),
        'normalization': 'caseId substitution in parsed request/response; JSON reserialization',
        'mutation': 'Remove required nextDecision; all other decoded fields unchanged',
        'approvedBusinessReplay': False}
    return body, injected, provenance


def run(source, offline=False):
    ready()
    build, profile = baseline(), model_profile()
    out = ROOT / 'evidence' / ('comparison-correction-' + ('offline-' if offline else 'live-') + time.strftime('%Y%m%d-%H%M%S'))
    out.mkdir()
    secrets = json.loads((ROOT / '.runtime/secrets.json').read_text())
    token = login('maya')
    cases, results = [], []
    before = records()
    (out / 'business-records-before.json').write_text(json.dumps(before, indent=2))
    with httpx.Client(timeout=300, trust_env=False) as client:
        try:
            for path, port in [('java', 18081), ('sidecar', 18082)]:
                case = 'comparison-correction-' + path + '-' + uuid.uuid4().hex
                cases.append(case)
                body, injected, provenance = sample(source, path, case)
                correction = {'contains': [case, "Fulfill the mission for skill 'compareOptions'", '$.nextDecision',
                    'does not satisfy the configured output_schema'], 'after': [0]}
                if offline:
                    valid = copy.deepcopy(injected)
                    valid['nextDecision'] = 'Synthetic rehearsal only; no commitment. Not a model-produced business result.'
                    correction.update(response=envelope(json.dumps(valid), profile['model']),
                        provenance='Synthetic offline rehearsal correction; no business approval')
                else:
                    correction['live'] = True
                registration = {'mode': 'replay' if offline else 'controlled-live', 'path': path, 'steps': [
                    {'contains': [case, "Fulfill the mission for skill 'compareOptions'"],
                     'excludes': ['does not satisfy the configured output_schema'],
                     'response': envelope(json.dumps(injected), profile['model']), 'provenance': provenance}, correction]}
                (out / (path + '-registration.json')).write_text(json.dumps(registration, indent=2))
                (out / (path + '-input.json')).write_text(json.dumps(body, indent=2))
                r = client.post('http://127.0.0.1:18090/control/cases/' + case, json=registration,
                                headers={'X-Control-Key': secrets['control']})
                r.raise_for_status()
                api = f'http://127.0.0.1:{port}'
                auth = {'Authorization': 'Bearer ' + token}
                # Reissue actual authoritative quotes under the fresh diagnostic case.
                r = client.post(api + '/v1/skills/quoteOptions/executions',
                    json={'caseId': case, 'assetId': body['assetId'], 'context': {}}, headers=auth)
                r.raise_for_status()
                quoted = wait(client, api, r.json()['id'], token, timeout=60)
                assert quoted['status'] == 'COMPLETED'
                assert json.loads(quoted['result'])['quotes'] == injected['quotes']
                (out / (path + '-quotes.json')).write_text(json.dumps(quoted, indent=2))
                r = client.post(api + '/v1/skills/compareOptions/executions', json=body, headers=auth)
                r.raise_for_status()
                item = {'path': path, 'caseId': case, 'executionId': r.json()['id']}
                results.append(item)
                terminal = wait(client, api, item['executionId'], token, timeout=300)
                item['status'] = terminal['status']
                (out / (path + '-execution.json')).write_text(json.dumps(terminal, indent=2))
                print(path, terminal['status'], flush=True)
        finally:
            collect(client, out, cases, secrets, [token])
            after = records()
            (out / 'business-records-after.json').write_text(json.dumps(after, indent=2))
            (out / 'manifest.json').write_text(json.dumps({**build, **profile, 'results': results,
                'mode': 'offline comparison rehearsal' if offline else 'controlled live comparison correction',
                'sourceCapture': source.name, 'scope': 'Direct comparison missing-field correction; not full-mission recovery or approved replay',
                'approved': False, 'assessmentAndRequestsUnchanged': all(before[p][table] == after[p][table]
                    for p in ['java', 'python'] for table in ['assessments', 'requests'])}, indent=2))
            finalize(out)
            print(out, flush=True)
    return out


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('capture', type=pathlib.Path)
    parser.add_argument('--offline', action='store_true')
    args = parser.parse_args()
    run(args.capture.resolve(), args.offline)
