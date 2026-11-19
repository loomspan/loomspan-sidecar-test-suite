"""Verify provider-free assessment and exact service commitment on both hosts."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
from uuid import UUID, uuid4

import httpx

import environment
from login import login
from readiness import ready
from replay_reference import bind_case, load_reference
from smoke import ROOT, records, require_offline_provider, wait_outcome


def fixture_hashes():
    roots = ['fixtures/reference-responses', 'fixtures/reference', 'fixtures/reference-namespaced', 'fixtures/typesafe-ai',
             'config/skills', 'config/executor-skills']
    files = [ROOT / 'fixtures/business.json']
    for directory in roots:
        files.extend(path for path in (ROOT / directory).rglob('*') if path.is_file())
    return {path.relative_to(ROOT).as_posix(): sha256(path.read_bytes()).hexdigest()
            for path in sorted(files)}


def submit(client, api, route, value, headers):
    accepted = client.post(api + route, json=value, headers=headers)
    assert accepted.status_code == 202, f'{route} admission status {accepted.status_code}'
    return wait_outcome(client, api, accepted.json()['id'], headers)


def exercise(client, path, port, control, maya, luis, reference):
    storage = 'python' if path == 'sidecar' else 'java'
    issuer = 'equipment-app' if path == 'sidecar' else environment.issuer()
    api = environment.url(port)
    before = records(storage)
    case_id = f'equipment-commitment-{path}-{uuid4().hex}'
    key = uuid4().hex
    bound = bind_case(reference, case_id)
    registration = client.post(environment.url(18090, '/control/cases/' + case_id),
                               json={'mode': 'replay', 'path': path, 'steps': bound['steps']},
                               headers=control)
    registration.raise_for_status()
    assessment = submit(client, api, '/assessments', bound['input'], maya)
    assert assessment['status'] == 'COMPLETED'
    assert json.loads(assessment['result']) == bound['expected']
    version = assessment['assessmentVersion']
    quote = next(quote for quote in bound['expected']['quotes'] if quote['option'] == 'standard')
    approval = {name: quote[name] for name in ('option', 'quoteId', 'attendance', 'scope')}
    approval.update(assessmentVersion=version, cap=quote['maxExposure'], idempotencyKey=key, approved=True)
    assert client.post(api + '/service-requests', json=approval, headers=maya).status_code == 403
    result = submit(client, api, '/service-requests', approval, luis)
    assert result['status'] == 'COMPLETED'
    receipt = json.loads(result['result'])
    assert UUID(receipt['requestId'])
    assert receipt['status'] == 'PENDING_DISPATCH'
    assert receipt['approval'] == approval and receipt['quote'] == quote
    assert receipt['approver'] == {'issuer': issuer, 'subject': 'luis'}
    assert receipt['caseId'] == case_id and receipt['assetId'] == bound['input']['assetId']
    assert receipt['evidence'] == bound['expected']['citations']
    recovery = api + '/service-requests/by-key/' + key
    recovered = client.get(recovery, headers=luis)
    assert recovered.status_code == 200 and recovered.json() == receipt
    assert client.get(recovery, headers=maya).status_code == 403
    assert client.get(api + '/service-requests/by-key/' + uuid4().hex, headers=luis).status_code == 404

    repeated = submit(client, api, '/service-requests', approval, luis)
    assert repeated['status'] == 'COMPLETED' and json.loads(repeated['result']) == receipt
    changed = submit(client, api, '/service-requests', approval | {'cap': approval['cap'] - 1}, luis)
    assert changed['status'] == 'FAILED'
    if path == 'sidecar':
        assert 'idempotency content conflict' in changed['failure']['message'].lower()
    assert client.get(recovery, headers=luis).json() == receipt

    after = records(storage)
    assert all(row in after[table] for table, rows in before.items() for row in rows)
    assert len(after['quotes']) == len(before['quotes']) + 2
    assert len(after['assessments']) == len(before['assessments']) + 1
    [added] = [row for row in after['requests'] if row not in before['requests']]
    assert added[:2] == (issuer + '|luis', key) and json.loads(added[3]) == receipt
    journal = client.get(environment.url(18090, '/control/journal'), headers=control)
    journal.raise_for_status()
    events = [event for event in journal.json() if event.get('caseId') == case_id]
    calls = [event for event in events if event['event'] == 'model-request']
    replies = [event for event in events if event['event'] == 'model-response']
    assert len(calls) == len(bound['steps'])
    assert sorted(event['stage'] for event in replies) == list(range(len(bound['steps'])))
    assert all(event['provenance'].startswith('accepted-reference:') for event in replies)
    assert sorted(event['requestId'] for event in replies) == sorted(event['requestId'] for event in calls)
    assert not any(event['event'] in ('model-rejected', 'provider-transport-failure') for event in events)

    normalized = json.dumps(receipt | {'approver': {'issuer': 'verified', 'subject': 'luis'}}, sort_keys=True)
    for generated, replacement in ((receipt['requestId'], '<request>'), (version, '<assessment>'),
                                   (key, '<key>'), (case_id, '<case>')):
        normalized = normalized.replace(generated, replacement)
    return normalized, {'lookupAndAssessmentReplay': True, 'newQuotes': 2, 'newAssessments': 1,
                        'newPendingDispatchRequests': 1, 'ownerRecovery': True,
                        'exactRepeatReturnsReceipt': True, 'conflictAndUnauthorizedDenied': True,
                        'acceptedFixtureResponses': len(replies), 'providerCalls': 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    output = parser.parse_args().output.resolve()
    if output.exists() or not environment.settings()['portOffset']:
        raise ValueError('Use an isolated Compose project and a new output directory')
    ready(timeout=30)
    require_offline_provider()
    hashes = fixture_hashes()
    _, references = load_reference()
    control = {'X-Control-Key': json.loads((ROOT / '.runtime/secrets.json').read_bytes())['control']}
    maya = {'Authorization': 'Bearer ' + login('maya')}
    luis = {'Authorization': 'Bearer ' + login('luis')}
    with httpx.Client(timeout=30, trust_env=False) as client:
        java, java_result = exercise(client, 'java', 18081, control, maya, luis, references['baseline'])
        python, python_result = exercise(client, 'sidecar', 18082, control, maya, luis, references['baseline'])
    assert java == python
    assert fixture_hashes() == hashes
    require_offline_provider()
    output.mkdir(parents=True)
    (output / 'report.json').write_text(json.dumps({
        'status': 'PASS', 'runtime': environment.runtime_identity(),
        'hosts': {'java': java_result, 'sidecar': python_result},
        'fixtureAndContractSha256': hashes,
    }, indent=2) + '\n', encoding='utf-8')
    print('Both hosts committed one PENDING_DISPATCH request with exact owner recovery and no provider calls.')


if __name__ == '__main__':
    main()
