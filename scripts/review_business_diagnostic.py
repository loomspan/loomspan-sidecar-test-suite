"""Read-only verification of authored offline workflow diagnostics; never approval."""
import argparse
import hashlib
import json
from pathlib import Path
from inspect_capture import completed, mission, system
from review_correction_capture import review


def inspect(directory):
    directory = Path(directory).resolve()
    manifest = json.loads((directory / 'manifest.json').read_text())
    events = json.loads((directory / 'journal.json').read_text())
    before = json.loads((directory / 'business-records-before.json').read_text())
    after = json.loads((directory / 'business-records-after.json').read_text())
    inventory = review(directory)
    checks, paths = [], {}
    def check(path, name, value):
        checks.append({'path': path, 'check': name, 'passed': bool(value)})
    check(None, 'two distinct integration cases', len(manifest['results']) == 2 and
          {i['path'] for i in manifest['results']} == {'java', 'sidecar'} and
          len({i['caseId'] for i in manifest['results']}) == 2)
    check(None, 'explicit offline unapproved disposition', manifest['approved'] is False and
          manifest['paidCalls'] == 0 and manifest['mode'] == 'offline authored business diagnostic')
    for item in manifest['results']:
        path, case = item['path'], item['caseId']
        storage = 'python' if path == 'sidecar' else 'java'
        expected = json.loads((directory / (path + '-expected.json')).read_text())
        terminal = json.loads((directory / (path + '-assessment.json')).read_text())
        local = [e for e in events if e.get('caseId') == case]
        requests = [e for e in local if e['event'] == 'model-request']
        responses = [e for e in local if e['event'] == 'model-response']
        registration = json.loads((directory / (path + '-registration.json')).read_text())
        check(path, 'strict replay registration has no live stages', registration['mode'] == 'replay' and
              all(not s.get('live') for s in registration['steps']))
        check(path, 'no provider/fallback/fixture failures', all(e.get('provenance') != 'live OpenRouter' for e in local) and
              not any(e['event'] in ['model-rejected', 'provider-transport-failure'] for e in local))
        check(path, 'all expected stages paired exactly once', len(requests) == len(responses) == item['expectedCalls'] and
              len({e['requestId'] for e in requests}) == len(requests) and
              {e['requestId'] for e in requests} == {e['requestId'] for e in responses} and
              sorted(e['stage'] for e in responses) == list(range(item['expectedCalls'])))
        check(path, 'completed diagnostic assessment equals authored expected output', terminal.get('status') == 'COMPLETED' and
              terminal.get('assessmentVersion') and json.loads(terminal.get('result', '{}')) == expected)
        compare_calls = [e for e in requests if mission(e['request'], 'compareOptions')]
        check(path, 'comparison receives authoritative context and units', len(compare_calls) == 2 and all(
              marker in json.dumps(compare_calls[0]['request']) for marker in
              ['AP24B-0517', 'AUTH-NB', '100000', 'Priya Shah', 'integer USD cents', 'workEstimateHours', 'S-3', 'S-5']))
        feedback = '\n'.join(m.get('content', '') for e in compare_calls for m in e['request']['messages']
                             if m.get('role') == 'user' and m.get('content', '').startswith('The previous response'))
        check(path, 'actual schema feedback rejects quote-ID selection', '$.selectedOption' in feedback and
              'does not satisfy the configured output_schema' in feedback)
        compare_responses = [e for e in responses if e['requestId'] in {c['requestId'] for c in compare_calls}]
        values = [json.loads(e['response']['choices'][0]['message']['content']) for e in compare_responses]
        check(path, 'injected selection rejected then synthetic corrected selection accepted', len(values) == 2 and
              values[0]['selectedOption'] == next(q['quoteId'] for q in expected['quotes'] if q['option'] == 'expedited') and
              values[1] == expected and values[0] != expected)
        finals = []
        for e in requests:
            if 'All required plan tasks are already COMPLETE.' in system(e['request']):
                for task in completed(e['request']):
                    if task['skillName'] in ['compareOptions', 'planResolution']:
                        finals.append((task['skillName'], json.loads(task['result'])))
        check(path, 'both actual parent synthesis inputs retain corrected comparison',
              {name for name, _ in finals} == {'compareOptions', 'planResolution'} and all(v == expected for _, v in finals))
        records = json.loads((directory / (storage + '-business-records.json')).read_text())
        quotes = {r['id']: json.loads(r['body']) for r in records['quotes']}
        check(path, 'exact two authoritative quotes persist unchanged with USD cents', len(expected['quotes']) == 2 and
              {q['quoteId'] for q in expected['quotes']} == {case + '-expedited-v1', case + '-standard-v1'} and
              all(quotes.get(q['quoteId']) == q for q in expected['quotes']) and
              [(q['maxExposure'], q['fullyCoveredScopeMaximum']) for q in expected['quotes']] == [(78000, 30000), (48000, 0)])
        check(path, 'one immutable diagnostic assessment, no invalid intermediate published',
              sum(json.loads(r['body']).get('caseId') == case for r in records['assessments']) == 1 and
              any(r['version'] == terminal.get('assessmentVersion') and json.loads(r['body']) == expected for r in records['assessments']))
        check(path, 'no business commitment or change to prior requests', before[storage]['requests'] == after[storage]['requests'])
        check(path, 'prior quote/assessment records remain intact', all(row in after[storage][table]
              for table in ['assessments', 'quotes'] for row in before[storage][table]))
        x = inventory['paths'][path]
        check(path, 'every model response equals actual Framework trace content', x['providerContentsMatchFrameworkTrace'])
        check(path, 'actual root trace succeeded', any(t['entrySkill'] == 'resolveEquipment' and t['outcome'] == 'SUCCEEDED'
              for t in x['traces']))
        schema = [f for f in x['traceCorrectionEvents'] if f.get('recordType') == 'STRUCTURED_OUTPUT_RECORDED'
                  and f.get('data', {}).get('skillName') == 'compareOptions']
        rejected = [f for f in schema if f['data'].get('status') == 'RETRYING' and
                    any(i.get('path') == '$.selectedOption' for i in f['data'].get('issues', []))]
        accepted = [f for f in schema if f['data'].get('status') == 'PASSED']
        check(path, 'trace records selection rejection before corrected schema acceptance',
              len(rejected) == len(accepted) == 1 and rejected[0]['sequence'] < accepted[0]['sequence'])
        paths[path] = {'caseId': case, 'modelRequests': len(requests), 'durationSeconds': x['durationSeconds'],
            'traces': x['traces'], 'comparisonSchemaEvents': schema,
            'scope': 'Actual Framework behavior for authored/captured responses; no new model judgment'}
    return {'status': 'PASS' if all(c['passed'] for c in checks) else 'FAIL', 'checks': checks, 'paths': paths,
        'approvedBusinessReplay': False, 'paidCalls': 0,
        'scope': 'Offline workflow diagnostic only; synthetic correction/final outputs do not approve source captures'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('capture', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.resolve().is_relative_to(args.capture.resolve()):
        parser.error('Write outside original capture')
    result = inspect(args.capture)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as out:
        json.dump(result, out, indent=2)
    print(result['status'], [(c['path'], c['check']) for c in result['checks'] if not c['passed']])
    raise SystemExit(0 if result['status'] == 'PASS' else 1)
