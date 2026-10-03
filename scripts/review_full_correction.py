"""Independent trace, source, invariant and live-correction provenance review."""
import argparse
from collections import Counter
import json
from pathlib import Path
from acceptance_report import checksums
from capture_business_diagnostic import normalized
from capture_reviewed_replay import verify_source
from curate_business_replay import ROOT, CASE, digest
from full_correction import stages
from inspect_capture import mission, system, completed
from recovery_replay import FEEDBACK
from review_correction_capture import review


def citation_comparison(original,corrected):
    before,after=Counter(original),Counter(corrected)
    return {'missing':list((before-after).elements()),'added':list((after-before).elements()),
            'sameCoverage':before==after,'orderChanged':before==after and original!=corrected}


def inspect(directory):
    d=Path(directory).resolve();load=lambda name:json.loads((d/name).read_bytes())
    manifest=load('manifest.json');events=load('journal.json');before=load('business-records-before.json');after=load('business-records-after.json')
    inventory=review(d);live=manifest['mode']=='controlled live full correction';rehearsal=manifest['mode']=='offline full correction rehearsal';checks=[];paths={}
    def check(path,name,value):checks.append({'path':path,'check':name,'passed':bool(value)})
    check(None,'finalized capture checksums match',checksums(d)>0)
    check(None,'two distinct completed full-workflow cases',len(manifest['results'])==2 and
          {i['path'] for i in manifest['results']}=={'java','sidecar'} and len({i['caseId'] for i in manifest['results']})==2)
    check(None,'exact paid-call scope',manifest['paidCalls']==(2 if live else 0) and manifest['approved'] is False)
    bundle=json.loads((ROOT/'fixtures/replay/business-reviewed-v1.json').read_bytes())
    approval=json.loads((ROOT/'fixtures/replay/business-reviewed-v1-approval.json').read_bytes())
    check(None,'approved baseline fixture remains unchanged',approval['fixtureSha256']==manifest['baselineFixtureSha256']==digest(ROOT/'fixtures/replay/business-reviewed-v1.json'))
    for item in manifest['results']:
        path,case=item['path'],item['caseId'];storage='python' if path=='sidecar' else 'java'
        sample=bundle['scenarios']['baseline'][path];verify_source(sample)
        source_steps=normalized(sample['steps'],CASE,case);baseline=normalized(sample['expected'],CASE,case)
        reg=load(path+'-registration.json');terminal=load(path+'-assessment.json')
        local=[e for e in events if e.get('caseId')==case];calls=[e for e in local if e['event']=='model-request'];replies=[e for e in local if e['event']=='model-response']
        correction_index=next(i for i,s in enumerate(reg['steps']) if s['stageSkill']=='compareOptions')+1
        corrected=[e for e in replies if e['stage']==correction_index]
        if len(corrected)!=1:raise ValueError('No unique full-workflow correction response: '+path)
        response=corrected[0]['response'];expected=json.loads(response['choices'][0]['message']['content'])
        check(path,'one genuine correction stage with no other live registration',reg['mode']==('controlled-live' if live else 'replay') and
              [i for i,s in enumerate(reg['steps']) if s.get('live')]==([correction_index] if live else []))
        live_replies=[e for e in replies if e.get('provenance')=='live OpenRouter']
        check(path,'exactly one actual successful Muse-medium correction or provider-free replay',
              (len(live_replies)==1 and live_replies[0]==corrected[0] and corrected[0]['status']==200 and
               next(e['request'] for e in calls if e['requestId']==corrected[0]['requestId'])['model']==manifest['model']=='meta/muse-spark-1.3-contributor' and
               next(e['request'] for e in calls if e['requestId']==corrected[0]['requestId'])['reasoning_effort']=='medium') if live else not live_replies)
        check(path,'all stages pair exactly once without unexpected calls',len(calls)==len(replies)==item['expectedCalls']==len(reg['steps']) and
              sorted(e['stage'] for e in replies)==list(range(len(reg['steps']))) and
              len({e['requestId'] for e in calls})==len(calls) and {e['requestId'] for e in calls}=={e['requestId'] for e in replies} and
              not any(e['event'] in ['model-rejected','provider-transport-failure'] for e in local))
        if live:
            wanted=stages(source_steps)
        elif rehearsal:
            original_response=next(s['response'] for s in source_steps if s['stageSkill']=='compareOptions')
            wanted=stages(source_steps,original_response,{'kind':'Explicit offline original-content rehearsal, not genuine correction'})
        else:
            from curate_full_correction import verify_sample
            fixture=json.loads((ROOT/'fixtures/replay/full-correction-reviewed-v1.json').read_bytes())
            curated=fixture['samples'][path];verify_sample(curated)
            wanted=normalized(curated['steps'],CASE,case)
            check(path,'offline fixture and corrected expected content match reviewed provenance',
                  manifest['correctionFixtureSha256']==digest(ROOT/'fixtures/replay/full-correction-reviewed-v1.json') and
                  expected==normalized(curated['expected'],CASE,case)==load(path+'-expected.json'))
        check(path,'registration equals source-derived fault correction and real-result parent envelopes',reg['steps']==wanted)
        check(path,'canonical input preserved at every actual stage',all(
              canonical(e['request'])==reg['steps'][next(r['stage'] for r in replies if r['requestId']==e['requestId'])]['missionInputEquals'] for e in calls))
        check(path,'completed assessment equals actual genuine corrected response',terminal['status']=='COMPLETED' and
              terminal.get('assessmentVersion') and json.loads(terminal.get('result','{}'))==expected)
        check(path,'authoritative quotes assessment identity and scope unchanged by correction',all(
              expected.get(k)==baseline[k] for k in ['caseId','assetId','selectedOption','quotes','equipmentAssessment']))
        citations=citation_comparison(baseline['citations'],expected.get('citations',[]))
        check(path,'original comparison citation coverage retained without missing or added references',citations['sameCoverage'])
        request=next(e['request'] for e in calls if e['requestId']==corrected[0]['requestId'])
        fault=next(e for e in replies if e['stage']==correction_index-1)['response']['choices'][0]['message']['content']
        assistant=[m['content'] for m in request['messages'] if m['role']=='assistant']
        complete_candidate=assistant==[fault]
        check(path,'actual corrective request retains entire malformed candidate',complete_candidate)
        check(path,'extra-brace source fault and actual parser feedback',fault==source_steps[correction_index-1]['response']['choices'][0]['message']['content']+'}' and
              any(m.get('role')=='user' and m.get('content','').startswith(FEEDBACK) and "Unexpected close marker '}'" in m['content'] for m in request['messages']))
        comparison=next(e['request'] for e in calls if mission(e['request'],'compareOptions'))
        check(path,'complete authoritative asset approval commercial context and cents reach comparison',all(
              marker in json.dumps(comparison) for marker in ['AP24B-0517','AUTH-NB','100000','Priya Shah','integer USD cents','workEstimateHours','S-3','S-5']))
        finals=[t for e in calls if 'All required plan tasks are already COMPLETE.' in system(e['request']) for t in completed(e['request'])
                if t['skillName'] in ['compareOptions','planResolution']]
        check(path,'both actual native parent inputs preserve genuine corrected result',len(finals)==2 and
              {t['skillName'] for t in finals}=={'compareOptions','planResolution'} and all(json.loads(t['result'])==expected for t in finals))
        records=load(storage+'-business-records.json');quotes={r['id']:json.loads(r['body']) for r in records['quotes']}
        check(path,'authoritative persisted quotes and integer USD cents unchanged',all(quotes.get(q['quoteId'])==q for q in expected['quotes']) and
              [(q['maxExposure'],q['fullyCoveredScopeMaximum']) for q in expected['quotes']]==[(78000,30000),(48000,0)])
        check(path,'only one correct immutable assessment and no invalid intermediate publication',
              sum(json.loads(r['body']).get('caseId')==case for r in records['assessments'])==1 and
              any(r['version']==terminal['assessmentVersion'] and json.loads(r['body'])==expected for r in records['assessments']))
        check(path,'no service commitment and prior durable records intact',before[storage]['requests']==after[storage]['requests'] and
              all(row in after[storage][table] for table in ['quotes','assessments'] for row in before[storage][table]))
        x=inventory['paths'][path];roots=[t for t in x['traces'] if t['entrySkill']=='resolveEquipment']
        ids={e['frameId'] for e in terminal.get('events',[]) if e.get('frameId')}
        frames=[json.loads(line) for t in roots for line in (d/t['file']).read_text().splitlines()]
        check(path,'actual successful root trace uniquely correlates to public execution',len(roots)==1 and roots[0]['outcome']=='SUCCEEDED' and
              (roots[0]['sessionId']==terminal['sessionId'] if terminal.get('sessionId') else bool(ids) and ids.issubset({f.get('frameId') for f in frames})))
        check(path,'every original fault correction and parent response equals Framework trace',x['providerContentsMatchFrameworkTrace'])
        schemas=[f for f in x['traceCorrectionEvents'] if f['recordType']=='STRUCTURED_OUTPUT_RECORDED' and f.get('data',{}).get('skillName')=='compareOptions']
        check(path,'actual trace rejects invalid JSON then accepts correction on attempt two',len(schemas)==2 and
              schemas[0]['data']['status']=='RETRYING' and schemas[0]['data']['failureMode']=='INVALID_JSON' and
              schemas[1]['data']['status']=='PASSED' and schemas[1]['data']['attempt']==2 and schemas[0]['sequence']<schemas[1]['sequence'])
        paths[path]={'caseId':case,'correctionRequestId':corrected[0]['requestId'],'correctionStage':correction_index,
                     'decodedFieldsChangedFromOriginal':[k for k in baseline if baseline[k]!=expected.get(k)],
                     'citationComparison':citations,'completeCandidateReceived':complete_candidate,
                     'traces':roots,'reportedCorrectionCost':response.get('usage',{}).get('cost'),'correctedContentSha256':digest_content(response),
                     'scope':'Actual genuine correction within complete workflow; both parent envelopes explicitly copy actual child'}
    return {'status':'PASS' if all(c['passed'] for c in checks) else 'FAIL','checks':checks,'paths':paths,
            'reviewPolicy':'complete candidate and citation coverage; ordering alone is not evidence loss',
            'paidCalls':manifest['paidCalls'],'approved':False,'scope':'Full-workflow recovery and invariants; separate semantic review required for curation'}


def canonical(request):
    text=next(m['content'] for m in request['messages'] if m.get('role')=='user' and m.get('content','').startswith('Mission objective:'))
    return json.JSONDecoder().raw_decode(text.split('Canonical mission input:\n',1)[1].lstrip())[0]


def digest_content(response):
    import hashlib
    return hashlib.sha256(response['choices'][0]['message']['content'].encode()).hexdigest()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('capture',type=Path);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.resolve().is_relative_to(args.capture.resolve()):parser.error('Write outside source capture')
    result=inspect(args.capture);args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2)
    print(result['status'],[(c['path'],c['check']) for c in result['checks'] if not c['passed']])
    raise SystemExit(0 if result['status']=='PASS' else 1)
