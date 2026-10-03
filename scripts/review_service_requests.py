"""Independent read-only checks of offline approval-bound creation and recovery."""
import argparse, datetime, hashlib, json
from pathlib import Path
from collections import Counter
from inspect_capture import mission, completed, system

def inspect(directory):
    d=Path(directory).resolve();load=lambda name:json.loads((d/name).read_bytes())
    manifest=load('manifest.json'); events=load('journal.json'); index=load('trace-index.json')
    before=load('business-records-before.json');after=load('business-records-after.json'); checks=[]
    def check(path,name,value):checks.append({'path':path,'check':name,'passed':bool(value)})
    check(None,'two complete independently scoped cases',len(manifest['results'])==2 and {x['path'] for x in manifest['results']}=={'java','sidecar'} and len({x['caseId'] for x in manifest['results']})==2)
    check(None,'finalized evidence checksums unchanged',all(hashlib.sha256((d/name).read_bytes()).hexdigest()==digest for name,digest in load('checksums.json').items()))
    check(None,'offline fixture only; no provider or unexpected-stage calls',manifest['paidCalls']==0 and all(e.get('provenance')!='live OpenRouter' and e['event'] not in ['model-rejected','provider-transport-failure'] for e in events))
    for item in manifest['results']:
        path,case=item['path'],item['caseId'];storage='python' if path=='sidecar' else 'java'
        terminal=load(path+'-assessment.json');expected=load(path+'-expected.json'); observations=load(path+'-observations.json'); ops={o['name']:o for o in observations}
        local=[e for e in events if e.get('caseId')==case]; req=[e for e in local if e['event']=='model-request'];resp=[e for e in local if e['event']=='model-response']
        check(path,'fresh reviewed immutable assessment published unchanged',terminal['status']=='COMPLETED' and terminal.get('assessmentVersion') and json.loads(terminal['result'])==expected)
        check(path,'only expected assessment stages call model fixture',len(req)==len(resp)==item['expectedCalls'] and {e['requestId'] for e in req}=={e['requestId'] for e in resp} and sorted(e['stage'] for e in resp)==list(range(item['expectedCalls'])))
        quote=next(q for q in expected['quotes'] if q['option']=='expedited')
        created=ops['approved-create-lost-result'];result=created['terminal'];receipt=json.loads(result.get('result','{}'));approval=created['approval']
        check(path,'approved pending-dispatch receipt binds exact assessment quote and USD cents',created['caller']=='luis' and created['httpStatus']==202 and result['status']=='COMPLETED' and receipt.get('status')=='PENDING_DISPATCH' and receipt.get('approval')==approval and approval['approved'] is True and approval['assessmentVersion']==terminal['assessmentVersion'] and approval['cap']==78000 and type(approval['cap']) is int and all(approval[k]==quote[k] for k in ['option','quoteId','attendance','scope']) and receipt.get('quote')==quote and receipt.get('evidence')==expected['citations'] and receipt.get('caseId')==case and receipt.get('assetId')=='NB-P240-017')
        expected_issuer=manifest.get('runtimeIdentity',{}).get('issuer','http://localhost:18080/realms/equipment')
        check(path,'verified Luis identity and submission before authoritative expiry',receipt.get('approver')=={'issuer':expected_issuer,'subject':'luis'} and datetime.datetime.fromisoformat(receipt['createdAt'])<datetime.datetime.fromisoformat(quote['expiresAt']))
        loss=created['lostResult']
        check(path,'actual transport response loss occurs after creation completed',loss.get('clientError') in ['RemoteProtocolError','ReadError'] and loss.get('upstream')==result and result['status']=='COMPLETED')
        recovery=load(path+'-recovery.json');retry=ops['same-content-retry-after-expiry']
        check(path,'lookup and same-content retry recover exact original receipt at expiry',load(path+'-expiry-clock.json')['now']==quote['expiresAt'] and recovery['httpStatus']==200 and recovery['body']==receipt and retry['terminal']['status']=='COMPLETED' and json.loads(retry['terminal']['result'])==receipt and retry['requestsBefore']==retry['requestsAfter'])
        for name in ['missing-approval','changed-quote-terms','same-key-content-conflict','new-request-at-expiry']:
            o=ops[name]
            check(path,name+' fails without changing durable requests',o['httpStatus']==202 and o['terminal']['status']=='FAILED' and o['requestsBefore']==o['requestsAfter'])
        denied=ops['unauthorized-maya'];valid=created['approval']
        check(path,'otherwise-valid Maya denied at public Framework creation boundary',denied['approval']==valid and denied['caller']=='maya' and (denied['httpStatus']==403 or denied.get('terminal',{}).get('status')=='FAILED') and denied['requestsBefore']==denied['requestsAfter'])
        check(path,'Maya cannot recover Luis receipt',load(path+'-unauthorized-recovery.json')['httpStatus']==403)
        added=[row for row in after[storage]['requests'] if row not in before[storage]['requests']]
        check(path,'exactly one new durable owner-scoped request with atomic matching approval',len(added)==1 and json.loads(added[0][2])==approval and json.loads(added[0][3])==receipt and added[0][0]==receipt['approver']['issuer']+'|luis' and added[0][1]==approval['idempotencyKey'])
        check(path,'prior requests quotes and assessments remain intact',all(row in after[storage][table] for table in ['requests','quotes','assessments'] for row in before[storage][table]))
        records=load(storage+'-business-records.json');quotes={r['id']:json.loads(r['body']) for r in records['quotes']}
        check(path,'authoritative quotes remain identical and both caps are cents',all(quotes[q['quoteId']]==q for q in expected['quotes']) and [(q['maxExposure'],q['fullyCoveredScopeMaximum']) for q in expected['quotes']]==[(78000,30000),(48000,0)])
        traces=[t for t in index if t['path']==path and case in t['cases']]; contents=[];frames_by_session={}
        for t in traces:
            raw=(d/t['file']).read_bytes();assert hashlib.sha256(raw).hexdigest()==t['sha256']
            frames=[json.loads(line) for line in raw.decode().splitlines()]
            frames_by_session[t['sessionId']]=frames
            if t['entrySkill']=='createServiceRequest':
                check(path,'creation trace '+t['sessionId']+' has no model request',not any(f['recordType'].startswith('MODEL_') for f in frames))
            for f in frames:
                if f['recordType']=='MODEL_RESPONSE_RECEIVED':
                    payload=f.get('data')
                    if payload is None:
                        ident=f['metadata']['payloadId'];chunks=sorted([x for x in frames if x['recordType']=='PAYLOAD_CHUNK_APPENDED' and x['metadata'].get('payloadId')==ident],key=lambda x:x['metadata']['chunkIndex']);payload=json.loads(''.join(x['data'] for x in chunks))
                    contents.append(payload['content'])
        check(path,'all fixture responses equal actual Framework trace content',Counter(contents)==Counter(e['response']['choices'][0]['message']['content'] for e in resp))
        for o in observations:
            if o.get('httpStatus')==202:
                terminal=o['terminal'];session=terminal.get('sessionId')
                ids={e['frameId'] for e in terminal.get('events',[]) if e.get('frameId')}
                matches=[t for t in traces if t['entrySkill']=='createServiceRequest' and (
                    t['sessionId']==session if session else bool(ids) and ids.issubset(
                        {f.get('frameId') for f in frames_by_session[t['sessionId']]}))]
                check(path,o['name']+' has actual correlated creation trace',len(matches)==1 and matches[0]['outcome']==('SUCCEEDED' if o['terminal']['status']=='COMPLETED' else 'FAILED'))
    return {'status':'PASS' if all(c['passed'] for c in checks) else 'FAIL','checks':checks,'paidCalls':0,'scope':'Direct approval-bound creation, denial, result-response loss, idempotency and expiry recovery on both paths; no nested-positive-control or complete first-delivery claim'}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('capture',type=Path);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.resolve().is_relative_to(args.capture.resolve()):p.error('Write outside source capture')
    result=inspect(args.capture);args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2)
    print(result['status'],[(x['path'],x['check']) for x in result['checks'] if not x['passed']]);raise SystemExit(0 if result['status']=='PASS' else 1)
