"""Review offline replay fidelity and Framework behavior against reviewed Muse sources."""
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
    recovery = manifest.get('recovery', False)
    checks, paths = [], {}
    def check(path, name, value):
        checks.append({'path': path, 'check': name, 'passed': bool(value)})
    check(None, 'finalized evidence checksums match', all(hashlib.sha256((directory/name).read_bytes()).hexdigest()==wanted
          for name,wanted in json.loads((directory/'checksums.json').read_bytes()).items()))
    check(None, 'two distinct integration cases', len(manifest['results']) == 2 and
          {i['path'] for i in manifest['results']} == {'java', 'sidecar'} and
          len({i['caseId'] for i in manifest['results']}) == 2)
    check(None, 'explicit provider-free candidate disposition', manifest['approved'] is False and
          manifest['paidCalls'] == 0 and manifest['mode'] == 'offline reviewed business replay')
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
        check(path, 'completed replay assessment equals reviewed captured output', terminal.get('status') == 'COMPLETED' and
              terminal.get('assessmentVersion') and json.loads(terminal.get('result', '{}')) == expected)
        compare_calls = [e for e in requests if mission(e['request'], 'compareOptions')]
        check(path, 'comparison receives authoritative context and units', len(compare_calls) == (2 if recovery else 1) and all(
              marker in json.dumps(compare_calls[0]['request']) for marker in
              ['AP24B-0517', 'AUTH-NB', '100000', 'Priya Shah', 'integer USD cents', 'workEstimateHours', 'S-3', 'S-5']))
        equipment_calls=[e for e in requests if mission(e['request'],'assessEquipment')]
        equipment_replies=[e for e in responses if e['requestId'] in {c['requestId'] for c in equipment_calls}]
        check(path,'published assessment equals actual assessment child',len(equipment_replies)==1 and
              json.loads(equipment_replies[0]['response']['choices'][0]['message']['content'])==expected['equipmentAssessment'])
        from capture_business_diagnostic import normalized
        from curate_business_replay import CASE, ROOT
        from capture_reviewed_replay import verify_source
        def mission_input_matches(request,step):
            try:
                message=next(m['content'] for m in request['messages'] if m.get('role')=='user' and m.get('content','').startswith('Mission objective:'))
                actual=json.JSONDecoder().raw_decode(message.split('Canonical mission input:\n',1)[1].lstrip())[0]
                return actual==step['missionInputEquals']
            except (StopIteration,KeyError,IndexError,ValueError): return False
        bundle=json.loads((ROOT/'fixtures/replay/business-reviewed-v1.json').read_bytes())
        approval=json.loads((ROOT/'fixtures/replay/business-reviewed-v1-approval.json').read_bytes())
        fixture_digest=hashlib.sha256((ROOT/'fixtures/replay/business-reviewed-v1.json').read_bytes()).hexdigest()
        check(path, 'fixture hash matches scoped approval and captured manifest',
              approval['status']=='APPROVED_FOR_SCOPED_OFFLINE_REPLAY' and
              approval['fixtureSha256']==manifest['diagnosticSha256']==fixture_digest)
        sample=bundle['scenarios'][manifest['scenario']][path]
        verify_source(sample)
        wanted_steps = normalized(sample['steps'],CASE,case)
        if recovery:
            from recovery_replay import recovery_steps, FEEDBACK
            wanted_steps = recovery_steps(wanted_steps)
        check(path,'registration and expected output derive from unedited reviewed source',
              registration['steps']==wanted_steps and expected==normalized(sample['expected'],CASE,case))
        check(path,'every actual canonical child input equals captured source input',all(
              mission_input_matches(r['request'],registration['steps'][next(e['stage'] for e in responses if e['requestId']==r['requestId'])]) for r in requests))
        finals = []
        for e in requests:
            if 'All required plan tasks are already COMPLETE.' in system(e['request']):
                for task in completed(e['request']):
                    if task['skillName'] in ['compareOptions', 'planResolution']:
                        finals.append((task['skillName'], json.loads(task['result'])))
        check(path, 'both actual parent synthesis inputs retain source comparison',
              {name for name, _ in finals} == {'compareOptions', 'planResolution'} and all(v == expected for _, v in finals))
        records = json.loads((directory / (storage + '-business-records.json')).read_text())
        quotes = {r['id']: json.loads(r['body']) for r in records['quotes']}
        check(path, 'exact two authoritative quotes persist unchanged with USD cents', len(expected['quotes']) == 2 and
              {q['quoteId'] for q in expected['quotes']} == {case + '-expedited-v1', case + '-standard-v1'} and
              all(quotes.get(q['quoteId']) == q for q in expected['quotes']) and
              [(q['maxExposure'], q['fullyCoveredScopeMaximum']) for q in expected['quotes']] == [(78000, 30000), (48000, 0)])
        check(path, 'one immutable replay assessment, no intermediate published',
              sum(json.loads(r['body']).get('caseId') == case for r in records['assessments']) == 1 and
              any(r['version'] == terminal.get('assessmentVersion') and json.loads(r['body']) == expected for r in records['assessments']))
        check(path, 'no business commitment or change to prior requests', before[storage]['requests'] == after[storage]['requests'])
        check(path, 'prior quote/assessment records remain intact', all(row in after[storage][table]
              for table in ['assessments', 'quotes'] for row in before[storage][table]))
        x = inventory['paths'][path]
        check(path, 'every model response equals actual Framework trace content', x['providerContentsMatchFrameworkTrace'])
        check(path, 'actual root trace succeeded', any(t['entrySkill'] == 'resolveEquipment' and t['outcome'] == 'SUCCEEDED'
              for t in x['traces']))
        roots=[t for t in x['traces'] if t['entrySkill']=='resolveEquipment']
        frame_ids={e['frameId'] for e in terminal.get('events',[]) if e.get('frameId')}
        actual_ids={json.loads(line).get('frameId') for t in roots
                    for line in (directory/t['file']).read_text().splitlines() if line}
        check(path, 'public execution uniquely correlates to actual root trace', len(roots)==1 and
              (roots[0]['sessionId']==terminal['sessionId'] if terminal.get('sessionId') else
               bool(frame_ids) and frame_ids.issubset(actual_ids)))
        schema = [f for f in x['traceCorrectionEvents'] if f.get('recordType') == 'STRUCTURED_OUTPUT_RECORDED'
                  and f.get('data', {}).get('skillName') == 'compareOptions']
        if recovery:
            rejected = [f for f in schema if f['data'].get('status') == 'RETRYING']
            accepted = [f for f in schema if f['data'].get('status') == 'PASSED']
            check(path, 'actual trace rejects malformed comparison before accepting correction',
                  len(rejected)==len(accepted)==1 and rejected[0]['sequence'] < accepted[0]['sequence'] and
                  rejected[0]['data'].get('failureMode')=='INVALID_JSON' and
                  any(i.get('code')=='invalid_json' for i in rejected[0]['data'].get('issues',[])))
            feedback = [r for r in compare_calls if any(m.get('role')=='user' and m.get('content','').startswith(FEEDBACK)
                        for m in r['request']['messages'])]
            replies = [e for e in responses if e['requestId'] in {r['requestId'] for r in compare_calls}]
            check(path, 'actual parser feedback receives unchanged reviewed correction', len(feedback)==1 and len(replies)==2 and
                  replies[0]['response']['choices'][0]['message']['content'] == replies[1]['response']['choices'][0]['message']['content']+'}' and
                  json.loads(replies[1]['response']['choices'][0]['message']['content']) == expected and
                  len(x['invalidJsonResponses'])==1)
        else:
            check(path,'comparison output schema passes without authored correction',len(schema)==1 and schema[0]['data'].get('status')=='PASSED')
        paths[path] = {'caseId': case, 'modelRequests': len(requests), 'durationSeconds': x['durationSeconds'],
            'traces': x['traces'], 'comparisonSchemaEvents': schema,
            'scope': 'Actual Framework behavior for unedited captured responses; no new model judgment'}
    return {'status': 'PASS' if all(c['passed'] for c in checks) else 'FAIL', 'checks': checks, 'paths': paths,
        'approvedBusinessReplay': not recovery and all(c['passed'] for c in checks), 'paidCalls': 0,
        'scope': 'Full-workflow injected recovery with offline captured correction; no new model judgment' if recovery else 'Approval limited to baseline/priority deterministic assessment replay; no new model judgment, service commitment or complete first-delivery acceptance'}


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
