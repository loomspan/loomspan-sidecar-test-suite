"""Provider-free foundation check against both deployed integrations.

Adds two authoritative smoke quote rows per app; never creates a service request.
No historical evidence, replay capture or paid provider access is required.
"""
import json
from pathlib import Path
import sqlite3
import subprocess
import time
import uuid
import httpx
import environment
from baseline import baseline
from login import login
from model_profile import model_profile
from readiness import ready

ROOT = Path(__file__).resolve().parents[1]


def require_offline_provider():
    result = subprocess.run(environment.execute('fixtures', 'python', '-c',
        "import os; print('disabled' if not os.getenv('OPENROUTER_API_KEY') else 'enabled')"),
        check=True, capture_output=True, text=True)
    if result.stdout.strip() != 'disabled':
        raise RuntimeError('Smoke check requires provider-disabled runtime')


def records(host):
    path = ROOT / '.runtime' / host / 'equipment.db'
    with sqlite3.connect('file:' + path.as_posix() + '?mode=ro', uri=True) as db:
        return {t: db.execute('SELECT * FROM ' + t).fetchall()
                for t in ['assessments', 'quotes', 'requests']}


def wait(client, api, ident, headers):
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        response = client.get(api + '/v1/executions/' + ident, headers=headers)
        response.raise_for_status()
        result = response.json()
        if result['status'] in ['COMPLETED', 'FAILED']:
            if result['status'] != 'COMPLETED':
                raise RuntimeError('Deterministic quote execution failed')
            return json.loads(result['result'])
        time.sleep(.25)
    raise TimeoutError('Deterministic quote execution did not finish')


def main():
    ready(timeout=30)
    require_offline_provider()
    identity = baseline()
    profile = model_profile()
    secrets = json.loads((ROOT / '.runtime/secrets.json').read_bytes())
    token = login('maya')
    headers = {'Authorization': 'Bearer ' + token}
    control = {'X-Control-Key': secrets['control']}
    result = {'readyServices': 5, 'providerDisabled': True, 'paidCalls': 0,
              'runtimeIdentity': identity['runtimeIdentity'], 'modelConfiguration': profile,
              'scope': 'Foundation smoke only; not model judgment or release acceptance',
              'paths': {}}
    with httpx.Client(timeout=30, trust_env=False) as client:
        for name, storage, port in [('java', 'java', 18081), ('sidecar', 'python', 18082)]:
            before = records(storage)
            api = environment.url(port)
            case = 'smoke-' + name + '-' + uuid.uuid4().hex
            r = client.post(environment.url(18090, '/control/cases/' + case),
                            json={'mode': 'replay', 'steps': [], 'path': name}, headers=control)
            r.raise_for_status()
            assert client.post(api + '/v1/skills/quoteOptions/executions', json={}).status_code == 401
            r = client.post(api + '/v1/skills/quoteOptions/executions',
                            json={'caseId': case, 'assetId': 'NB-P240-017'}, headers=headers)
            r.raise_for_status()
            output = wait(client, api, r.json()['id'], headers)
            quotes = {q['option']: q for q in output['quotes']}
            assert len(output['quotes']) == 2
            assert quotes['expedited']['maxExposure'] == 78000
            assert quotes['expedited']['fullyCoveredScopeMaximum'] == 30000
            assert quotes['standard']['maxExposure'] == 48000
            assert quotes['standard']['fullyCoveredScopeMaximum'] == 0
            assert all(q['coverage'] == 'PENDING' and not q['reservation']
                       and not q['restorationGuaranteed'] for q in quotes.values())
            approval = {'assessmentVersion': 'not-issued', 'option': 'standard',
                        'quoteId': 'not-issued', 'attendance': 'not-issued',
                        'scope': {'repairHours': 1, 'parts': [], 'onlyIfJustifiedByTechnician': True},
                        'cap': 1, 'idempotencyKey': uuid.uuid4().hex, 'approved': True}
            r = client.post(api + '/v1/skills/createServiceRequest/executions',
                            json={'approval': approval}, headers=headers)
            assert r.status_code == 403, 'Maya must not have request creation permission'
            r = client.get(environment.url(18090, '/control/journal'), headers=control)
            r.raise_for_status()
            assert not any(e.get('caseId') == case and e['event'] == 'model-request' for e in r.json())
            after = records(storage)
            assert all(row in after[t] for t, rows in before.items() for row in rows)
            assert len(after['quotes']) == len(before['quotes']) + 2
            assert len(after['assessments']) == len(before['assessments'])
            assert len(after['requests']) == len(before['requests'])
            result['paths'][name] = {'deterministicQuotes': 'PASS', 'unauthenticatedDenied': True,
                'mayaCreationDenied': True, 'priorRecordsPreserved': True, 'newQuoteRows': 2,
                'modelCalls': 0, 'caseId': case}
    require_offline_provider()
    (ROOT / '.runtime/smoke.json').write_text(json.dumps(result, indent=2) + '\n')
    print('PASS: both integrations; deterministic quotes; identity/permission boundaries;')
    print('prior records preserved; provider disabled; zero model calls. .runtime/smoke.json')


if __name__ == '__main__':
    main()
