"""Read-only mechanical capture review. Never approves a replay baseline.

Write a new report outside the capture so historical evidence/checksums stay intact.
Passing these checks still requires semantic review of judgment and source fidelity.
"""
import argparse
import hashlib
import json
from pathlib import Path


def system(request):
    return '\n'.join(m.get('content','') for m in request.get('messages',[]) if m.get('role')=='system')


def mission(request,skill):
    prefixes=tuple("Mission objective:\n"+verb+" '"+skill+"' using the provided mission input object."
                   for verb in ['Execute skill','Fulfill the mission for skill'])
    return any(m.get('role')=='user' and m.get('content','').startswith(prefixes)
               for m in request.get('messages',[]))


def completed(request):
    text=system(request)
    if '--- COMPLETED TASK EVIDENCE ---\n' not in text: return []
    block=text.split('--- COMPLETED TASK EVIDENCE ---\n',1)[1]
    return json.JSONDecoder().raw_decode(block[block.index('['):])[0]


def inspect(directory):
    directory=Path(directory).resolve()
    checks=[]; hashes={}
    def check(name,passed,path=None):
        checks.append({'check':name,'path':path,'passed':bool(passed)})
    def read(name,default):
        file=(directory/name).resolve()
        if not file.is_relative_to(directory):
            check('evidence path stays within capture',False); return default
        try:
            raw=file.read_bytes(); hashes[name]=hashlib.sha256(raw).hexdigest()
            return json.loads(raw)
        except (OSError,ValueError):
            check('read '+name,False); return default
    manifest=read('manifest.json',{})
    events=read('journal.json',[])
    index=read('trace-index.json',[])
    identities=read('running-identities.json',{})
    check('explicit selected live model and reasoning',manifest.get('mode')=='live' and
          manifest.get('model') in {'openai/gpt-6.1-sol','meta/muse-spark-1.3-contributor'} and manifest.get('reasoning')=='medium')
    for path,storage in [('java','java'),('sidecar','python')]:
        selected=[r for r in manifest.get('results',[]) if r.get('path')==path]
        check('one identified execution',len(selected)==1,path)
        if len(selected)!=1: continue
        case=selected[0].get('caseId')
        local=[e for e in events if e.get('caseId')==case]
        requests=[e for e in local if e['event']=='model-request' and e.get('path')==path]
        responses=[e for e in local if e['event']=='model-response' and e.get('path')==path]
        check('no transport or fixture failures',not any(e['event'] in
              ['provider-transport-failure','model-rejected'] for e in local),path)
        request_ids=[e.get('requestId') for e in requests]
        response_ids=[e.get('requestId') for e in responses]
        check('unambiguous complete request/response pairing',requests and None not in request_ids and
              len(set(request_ids))==len(request_ids) and sorted(request_ids)==sorted(response_ids,key=str),path)
        check('responses recorded from real provider',responses and all(e.get('provenance')=='live OpenRouter'
              and e.get('status')==200 for e in responses),path)
        check('every request uses selected model/reasoning',requests and all(e['request'].get('model')==manifest.get('model')
              and e['request'].get('reasoning_effort')=='medium' for e in requests),path)
        for skill in ['assessEquipment','compareOptions']:
            calls=[e for e in requests if mission(e['request'],skill)]
            check(skill+' model responsibility reached',bool(calls),path)
            text=json.dumps(calls)
            check('registered asset markers reach '+skill,all(marker in text for marker in
                  ['ASSET-017','AP24B-0517','NB-WEST']),path)
            if skill=='compareOptions':
                check('approval routing markers reach comparison',all(marker in text for marker in
                      ['AUTH-NB','100000','Priya Shah','Luis Romero']),path)
                check('explicit monetary units reach comparison','integer USD cents' in text,path)
            if skill=='assessEquipment':
                check('history and guidance markers reach equipment assessment',all(marker in text for marker in
                      ['WO-0820','NOTE-0916','SB-2','20-minute','42 minutes']),path)
        finals={}
        for event in requests:
            if 'All required plan tasks are already COMPLETE.' not in system(event['request']): continue
            try:
                for item in completed(event['request']):
                    if item['skillName'] in ['compareOptions','planResolution']:
                        finals[item['skillName']]=json.loads(item['result'])
            except (KeyError,TypeError,ValueError): check('parse final synthesis evidence',False,path)
        check('both native final synthesis stages reached',set(finals)=={'compareOptions','planResolution'},path)
        terminal=read(path+'-assessment.json',{})
        check('completed immutable application assessment',terminal.get('status')=='COMPLETED' and
              terminal.get('assessmentVersion') and selected[0].get('status')=='COMPLETED',path)
        try: value=json.loads(terminal.get('result','{}'))
        except (TypeError,ValueError): value={}
        check('case and asset retained',value.get('caseId')==case and value.get('assetId')=='NB-P240-017',path)
        check('parent completion preserves comparison',bool(finals) and all(v==value for v in finals.values()),path)
        check('required decision evidence populated',all(value.get(k) for k in
              ['quotes','citations','uncertainty','acceptedRisk','changeConditions','nextDecision','responsibleParty','equipmentAssessment']),path)
        records=read(storage+'-business-records.json',{})
        quotes={row['id']:json.loads(row['body']) for row in records.get('quotes',[])}
        check('authoritative quotes preserved exactly',value.get('quotes') and all(
              q.get('quoteId') in quotes and quotes[q['quoteId']]==q for q in value['quotes']),path)
        check('exactly both case service quotes, without duplicates',isinstance(case,str) and len(value.get('quotes',[]))==2 and
              {q.get('quoteId') for q in value.get('quotes',[])}=={case+'-expedited-v1',case+'-standard-v1'},path)
        expedited=next((q for q in value.get('quotes',[]) if q.get('option')=='expedited'),{})
        check('independent conditional amounts',expedited.get('maxExposure')==78000 and
              expedited.get('fullyCoveredScopeMaximum')==30000 and expedited.get('coverage')=='PENDING',path)
        check('assessment persisted unchanged',any(row.get('version')==terminal.get('assessmentVersion') and
              json.loads(row['body'])==value for row in records.get('assessments',[])),path)
        check('assessment created no service commitment',not any(json.loads(row['receipt']).get('caseId')==case
              for row in records.get('requests',[])),path)
        check('running artifact identity recorded',identities.get(path,{}).get('runningJarSha256'),path)
        traces=[t for t in index if t.get('path')==path and case in t.get('cases',[]) and t.get('entrySkill')=='resolveEquipment']
        check('Framework root trace associated with case',bool(traces),path)
        for trace in traces:
            file=(directory/trace['file']).resolve()
            if not file.is_relative_to(directory) or not file.is_file():
                check('trace file exists inside capture',False,path); continue
            raw=file.read_bytes(); digest=hashlib.sha256(raw).hexdigest(); hashes[trace['file']]=digest
            check('trace bytes match recorded checksum',digest==trace.get('sha256'),path)
            check('Framework trace reports success',trace.get('outcome')=='SUCCEEDED',path)
    return {'status':'REJECTED_FOR_REPLAY' if any(not c['passed'] for c in checks) else 'NEEDS_SEMANTIC_REVIEW',
            'capture':str(directory),'checks':checks,'sourceSha256':hashes,
            'remainingReview':['Evidence fidelity and chronology; no invented diagnosis or coverage.',
              'Defensible alternatives, access, 11:00 continuity decision and restoration uncertainty.',
              'Changed-priority responsiveness on both paths; approved scripted baseline selection.',
              'Real correction feedback and response for the explicitly labeled malformed-output mutation.'],
            'approved':False}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('capture',type=Path); parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.resolve().is_relative_to(args.capture.resolve()):
        parser.error('output must be outside the preserved source capture')
    report=inspect(args.capture)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x',encoding='utf-8') as out: json.dump(report,out,indent=2)
    print(report['status']+'; no replay approval granted')
    return 1 if report['status']=='REJECTED_FOR_REPLAY' else 0


if __name__=='__main__': raise SystemExit(main())
