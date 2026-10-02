"""Read-only actual comparison-schema correction verification; no business approval."""
import argparse
import hashlib
import json
from pathlib import Path
from review_correction_capture import review


def inspect(directory):
    directory = Path(directory).resolve()
    manifest = json.loads((directory / 'manifest.json').read_text())
    events = json.loads((directory / 'journal.json').read_text())
    inventory = review(directory)
    checks, paths = [], {}
    live = manifest['mode'] == 'controlled live comparison correction'
    def check(path, name, value):
        checks.append({'path': path, 'check': name, 'passed': bool(value)})
    check(None, 'two integration paths', {i['path'] for i in manifest['results']} == {'java', 'sidecar'})
    check(None, 'no assessment or commitment created', manifest['assessmentAndRequestsUnchanged'])
    for item in manifest['results']:
        path, case = item['path'], item['caseId']
        local = [e for e in events if e.get('caseId') == case]
        requests = {e['requestId']: e for e in local if e['event'] == 'model-request'}
        responses = [e for e in local if e['event'] == 'model-response']
        terminal = json.loads((directory / (path + '-execution.json')).read_text())
        registration = json.loads((directory / (path + '-registration.json')).read_text())
        seeded = [e for e in responses if e.get('stage') == 0]
        corrected = [e for e in responses if e.get('stage') == 1]
        check(path, 'exactly two paired comparison requests/responses', len(requests) == len(responses) == 2 and
              set(requests) == {e['requestId'] for e in responses} and len(seeded) == len(corrected) == 1)
        check(path, 'no fixture or provider transport failure', not any(e['event'] in
              ['model-rejected', 'provider-transport-failure'] for e in local))
        original = json.loads(seeded[0]['response']['choices'][0]['message']['content']) if seeded else {}
        check(path, 'exact seeded content and deliberate missing field', seeded and
              seeded[0]['response'] == registration['steps'][0]['response'] and 'nextDecision' not in original and
              registration['steps'][0]['provenance']['mutation'].startswith('Remove required nextDecision'))
        correction = corrected[0] if corrected else {}
        request = requests.get(correction.get('requestId'), {}).get('request', {})
        feedback = '\n'.join(m.get('content', '') for m in request.get('messages', []) if m['role'] == 'user')
        check(path, 'actual feedback identifies missing nextDecision', '$.nextDecision' in feedback and
              'does not satisfy the configured output_schema' in feedback and 'missing' in feedback)
        check(path, 'selected Muse/medium in actual correction request',
              request.get('model') == manifest['model'] and request.get('reasoning_effort') == 'medium')
        live_responses = [e for e in responses if e.get('provenance') == 'live OpenRouter']
        check(path, 'one real correction only' if live else 'no provider calls', len(live_responses) == (1 if live else 0))
        check(path, 'real correction succeeds' if live else 'synthetic rehearsal succeeds',
              terminal['status'] == 'COMPLETED' and (not live or correction.get('status') == 200))
        value = json.loads(terminal.get('result', '{}'))
        check(path, 'missing field restored with same case/asset', bool(value.get('nextDecision')) and
              value.get('caseId') == case and value.get('assetId') == original.get('assetId'))
        quotes = json.loads(json.loads((directory / (path + '-quotes.json')).read_text())['result'])['quotes']
        check(path, 'both reissued authoritative quotes unchanged', len(value.get('quotes', [])) == 2 and
              value['quotes'] == quotes == original.get('quotes'))
        check(path, 'equipment assessment retained unchanged', bool(value.get('equipmentAssessment')) and
              value['equipmentAssessment'] == original.get('equipmentAssessment'))
        x = inventory['paths'][path]
        check(path, 'all response text equals actual Framework trace content', x['providerContentsMatchFrameworkTrace'])
        check(path, 'real comparison trace succeeds', any(t['entrySkill'] == 'compareOptions' and t['outcome'] == 'SUCCEEDED' for t in x['traces']))
        schema = [f for f in x['traceCorrectionEvents'] if f.get('recordType') == 'STRUCTURED_OUTPUT_RECORDED'
                  and f.get('data', {}).get('skillName') == 'compareOptions']
        rejected = [f for f in schema if f['data'].get('status') == 'RETRYING' and
                    any(i.get('path') == '$.nextDecision' for i in f['data'].get('issues', []))]
        accepted = [f for f in schema if f['data'].get('status') == 'PASSED']
        check(path, 'trace rejection precedes accepted corrected schema', len(rejected) == len(accepted) == 1 and
              rejected[0]['sequence'] < accepted[0]['sequence'])
        paths[path] = {'caseId': case, 'correctionRequestId': correction.get('requestId'),
            'schemaEvents': schema, 'nextDecision': value.get('nextDecision'),
            'liveReportedCost': sum(e['response'].get('usage', {}).get('cost', 0) or 0 for e in live_responses),
            'traces': x['traces']}
    return {'status': 'PASS' if all(c['passed'] for c in checks) else 'FAIL', 'checks': checks, 'paths': paths,
        'approvedBusinessReplay': False, 'scope': 'Direct comparison output-schema correction; not full-mission recovery or business semantic approval'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('capture', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.resolve().is_relative_to(args.capture.resolve()):
        parser.error('Write outside preserved capture')
    result = inspect(args.capture)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as out: json.dump(result, out, indent=2)
    print(result['status'], [(c['path'], c['check']) for c in result['checks'] if not c['passed']])
    raise SystemExit(0 if result['status'] == 'PASS' else 1)
