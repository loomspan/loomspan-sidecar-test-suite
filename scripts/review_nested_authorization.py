"""Independent review of valid-approval nested authorization and real leaf effects."""
import argparse,hashlib,json
from collections import Counter
from pathlib import Path
from inspect_capture import mission,system,completed

def inspect(directory):
    d=Path(directory).resolve();load=lambda name:json.loads((d/name).read_bytes());manifest=load('manifest.json');events=load('journal.json');index=load('trace-index.json');before=load('business-records-before.json');after=load('business-records-after.json');checks=[]
    def check(path,name,value):checks.append({'path':path,'check':name,'passed':bool(value)})
    check(None,'two distinct completed assessment cases',len(manifest['results'])==2 and {i['path'] for i in manifest['results']}=={'java','sidecar'} and len({i['caseId'] for i in manifest['results']})==2)
    check(None,'immutable evidence checksum verification',all(hashlib.sha256((d/name).read_bytes()).hexdigest()==digest for name,digest in load('checksums.json').items()))
    check(None,'no live calls provider failures or unexpected replay stages',manifest['paidCalls']==0 and all(e.get('provenance')!='live OpenRouter' and e['event'] not in ['model-rejected','provider-transport-failure'] for e in events))
    for item in manifest['results']:
        path,case=item['path'],item['caseId'];storage='python' if path=='sidecar' else 'java'
        expected=load(path+'-expected.json');assessment=load(path+'-assessment.json');body=load(path+'-nested-input.json');approval=body['approval'];quote=next(q for q in expected['quotes'] if q['option']=='expedited')
        obs=load(path+'-nested-observations.json');maya=next(o for o in obs if o['caller']=='maya');luis=next(o for o in obs if o['caller']=='luis')
        local=[e for e in events if e.get('caseId')==case];requests=[e for e in local if e['event']=='model-request'];responses=[e for e in local if e['event']=='model-response'];reg=load(path+'-registration.json');count=len(reg['steps'])
        check(path,'fresh assessment unchanged and approval complete valid within ceiling',assessment['status']=='COMPLETED' and json.loads(assessment['result'])==expected and approval['assessmentVersion']==assessment['assessmentVersion'] and approval['approved'] is True and approval['cap']==78000 and type(approval['cap']) is int and all(approval[k]==quote[k] for k in ['option','quoteId','attendance','scope']))
        check(path,'all strict registered offline stages paired once',reg['mode']=='replay' and all(not s.get('live') for s in reg['steps']) and len(requests)==len(responses)==count and {e['requestId'] for e in requests}=={e['requestId'] for e in responses} and sorted(e['stage'] for e in responses)==list(range(count)))
        check(path,'explicit controlled provenance and real-result echo only',all(s['provenance']['kind'].startswith('Hand-authored controlled authorization') for s in reg['steps'][-10:]) and [s.get('responseFromCompletedTask') for s in reg['steps'][-2:]]==[{'taskId':'delegate','skillName':'createServiceRequest'},{'taskId':'delegate','skillName':'authorizationNested'}])
        n=len(reg['steps'])-10;request_by_id={e['requestId']:e['request'] for e in requests}
        denied_nested=[request_by_id[e['requestId']] for e in responses if e['stage'] in [n+2,n+3]]
        allowed_nested=[request_by_id[e['requestId']] for e in responses if e['stage']==n+6]
        def visible(r):return system(r).split('Available sub-skills (use these exact names for task capabilityName):',1)[1].split('Constraints:',1)[0]
        check(path,'actual Maya nested capability list excludes creation',len(denied_nested)==2 and all('(none)' in visible(r) and 'createServiceRequest' not in visible(r) for r in denied_nested))
        check(path,'actual unavailable-child feedback reached before terminal denial',any("value 'createServiceRequest' is not an exact visible capability name." in system(r) for r in denied_nested) and maya['httpStatus']==202 and maya['terminal']['status']=='FAILED' and maya['requestsBefore']==maya['requestsAfter'])
        check(path,'Luis sees same restricted leaf under same supplied input',len(allowed_nested)==1 and 'createServiceRequest' in visible(allowed_nested[0]) and maya['requestsAfter']==luis['requestsBefore'])
        path_traces=[t for t in index if t['path']==path and case in t['cases']];contents=[];frames_by_session={}
        for t in path_traces:
            raw=(d/t['file']).read_bytes();assert hashlib.sha256(raw).hexdigest()==t['sha256'];frames=[json.loads(line) for line in raw.decode().splitlines()];frames_by_session[t['sessionId']]=frames
            for f in frames:
                if f['recordType']=='MODEL_RESPONSE_RECEIVED':
                    payload=f.get('data')
                    if payload is None:
                        ident=f['metadata']['payloadId'];chunks=sorted([x for x in frames if x['recordType']=='PAYLOAD_CHUNK_APPENDED' and x['metadata'].get('payloadId')==ident],key=lambda x:x['metadata']['chunkIndex']);payload=json.loads(''.join(x['data'] for x in chunks))
                    contents.append(payload['content'])
        check(path,'every fixture response equals actual Framework trace content',Counter(contents)==Counter(e['response']['choices'][0]['message']['content'] for e in responses))
        def correlated(o):
            terminal=o['terminal'];session=terminal.get('sessionId')
            ids={e['frameId'] for e in terminal.get('events',[]) if e.get('frameId')}
            return [t for t in path_traces if t['entrySkill']=='authorizationParent' and (
                t['sessionId']==session if session else bool(ids) and ids.issubset({f.get('frameId') for f in frames_by_session[t['sessionId']]}))]
        for who,o,outcome in [('maya',maya,'FAILED'),('luis',luis,'SUCCEEDED')]:
            selected=correlated(o)
            check(path,who+' actual correlated root trace outcome',len(selected)==1 and selected[0]['outcome']==outcome)
        mt,lt=correlated(maya),correlated(luis)
        mf=frames_by_session[mt[0]['sessionId']] if len(mt)==1 else []
        lf=frames_by_session[lt[0]['sessionId']] if len(lt)==1 else []
        def leaf_calls(frames,kind):return [f for f in frames if f['recordType']==kind and f.get('metadata',{}).get('capabilityName')=='createServiceRequest']
        check(path,'Maya has no real creation invocation or durable request',not leaf_calls(mf,'TOOL_CALL_STARTED') and maya['requestsBefore']==maya['requestsAfter'])
        check(path,'Luis invokes and completes actual creation exactly once',len(leaf_calls(lf,'TOOL_CALL_STARTED'))==len(leaf_calls(lf,'TOOL_CALL_COMPLETED'))==1 and luis['terminal']['status']=='COMPLETED')
        if luis['terminal']['status']=='COMPLETED':
            receipt=json.loads(luis['terminal']['result']);added=[row for row in luis['requestsAfter'] if row not in luis['requestsBefore']]
            check(path,'exactly one durable matching Luis receipt with quote scope USD cents',len(added)==1 and json.loads(added[0][2])==approval and json.loads(added[0][3])==receipt and receipt['approval']==approval and receipt['quote']==quote and receipt['evidence']==expected['citations'] and receipt['status']=='PENDING_DISPATCH' and receipt['approver']=={'issuer':'http://localhost:18080/realms/equipment','subject':'luis'} and receipt['caseId']==case)
            finals=[request_by_id[e['requestId']] for e in responses if e['stage'] in [n+8,n+9]]
            children=[json.loads(task['result']) for r in finals for task in completed(r)]
            check(path,'both native parent inputs and final echoes preserve real receipt',len(finals)==2 and len(children)==2 and all(v==receipt for v in children))
        else:check(path,'Luis publishes durable receipt through both parents',False)
        check(path,'prior records preserved with only one new request',all(row in after[storage][table] for table in ['requests','quotes','assessments'] for row in before[storage][table]) and len(after[storage]['requests'])==len(before[storage]['requests'])+1)
        if path=='sidecar':
            check(path,'independent REST log has no Maya creation call and one Luis call',maya['creationEndpointCallsAfter']==maya['creationEndpointCallsBefore'] and luis['creationEndpointCallsAfter']==luis['creationEndpointCallsBefore']+1)
    return {'status':'PASS' if all(c['passed'] for c in checks) else 'FAIL','checks':checks,'paidCalls':0,'scope':'Controlled nested caller authorization on valid reviewed assessment approval; hand-authored scaffold, real leaf and native parent completion; not new Muse judgment or complete first-delivery acceptance'}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('capture',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.resolve().is_relative_to(a.capture.resolve()):p.error('Write outside source capture')
    result=inspect(a.capture);a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2)
    print(result['status'],[(c['path'],c['check']) for c in result['checks'] if not c['passed']]);raise SystemExit(0 if result['status']=='PASS' else 1)
