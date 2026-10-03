"""Read-only assertions for the isolated injected step-action fault."""
import argparse, hashlib, json
from pathlib import Path
from review_correction_capture import review

def inspect(directory):
    directory=Path(directory)
    manifest=json.loads((directory/'manifest.json').read_text())
    events=json.loads((directory/'journal.json').read_text(encoding='utf-8'))
    inventory=review(directory);checks=[];paths={}
    def check(path,name,value):checks.append({'path':path,'check':name,'passed':bool(value)})
    live=manifest['mode']=='controlled live correction'
    for item in manifest['results']:
        path=item['path'];case=item['caseId'];x=inventory['paths'][path]
        local=[e for e in events if e.get('caseId')==case]
        requests={e['requestId']:e for e in local if e['event']=='model-request'}
        responses=[e for e in local if e['event']=='model-response']
        injected=next(e for e in responses if e.get('stage')==1)
        registration=json.loads((directory/(path+'-registration.json')).read_text())
        candidate=injected['response']['choices'][0]['message']['content']
        check(path,'injected captured bytes equal registered case-normalized original',candidate==registration['steps'][1]['response']['choices'][0]['message']['content'])
        check(path,'malformed captured action rejected',len(x['invalidJsonResponses'])==1 and x['invalidJsonResponses'][0]['requestId']==injected['requestId'])
        correction=next((e for e in responses if e.get('stage')==2),None)
        correction_request=requests[correction['requestId']]['request'] if correction else {}
        text='\n'.join(m.get('content','') for m in correction_request.get('messages',[]) if m['role']=='user')
        marker='Rejected assistant response (JSON string): '
        replay=json.JSONDecoder().raw_decode(text.split(marker,1)[1])[0] if marker in text else ''
        complete=replay==candidate
        historical_excerpt='omitted ' in replay and replay.endswith(candidate[-128:]) and len(replay)<8500
        check(path,'actual feedback retains parser reason and complete candidate or historical bounded excerpt',
              'Unexpected close marker' in text and (complete or historical_excerpt))
        check(path,'correction uses selected Muse/medium',correction_request.get('model')==manifest['model'] and correction_request.get('reasoning_effort')=='medium')
        check(path,'one explicit live correction only' if live else 'no provider calls',
              sum(e.get('provenance')=='live OpenRouter' for e in responses)==(1 if live else 0))
        corrected=None
        if correction:
            try:corrected=json.loads(correction['response']['choices'][0]['message']['content'])
            except ValueError:pass
        check(path,'corrected JSON retains assigned task/tool and required real arguments',corrected and
              corrected.get('stepAction')=='CALL_TOOL' and corrected.get('taskId')=='t-entitlements-01' and
              corrected.get('toolName')=='entitlements' and corrected.get('toolArguments',{}).get('caseId')==case and
              corrected.get('toolArguments',{}).get('assetId')=='NB-P240-017')
        frames=[]
        for trace in x['traces']:
            frames.extend(json.loads(line) for line in (directory/trace['file']).read_text().splitlines())
        rejected=[f for f in frames if f.get('recordType')=='STEP_ACTION_REJECTED']
        calls=[f for f in frames if f.get('recordType')=='TOOL_CALL_STARTED']
        finished=[f for f in frames if f.get('recordType')=='TOOL_CALL_COMPLETED']
        check(path,'no tool invocation before rejection; exactly one after valid correction',
              len(rejected)==1 and len(calls)==1 and calls[0]['sequence']>rejected[0]['sequence'])
        check(path,'real entitlement tool completed once',len(finished)==1 and
              finished[0].get('route')=='entitlements')
        check(path,'independent entitlement source reads occurred only after correction response',correction and
              any(e['event']=='returned' for e in local) and
              all(e['timeNs']>correction['timeNs'] for e in local if e['event']=='entered'))
        check(path,'provider/replay contents exactly match actual Framework trace',x['providerContentsMatchFrameworkTrace'])
        check(path,'diagnostic execution and Framework trace succeeded',item.get('status')=='COMPLETED' and
              all(t['outcome']=='SUCCEEDED' for t in x['traces']))
        check(path,'no fixture or transport rejection',not any(e['event'] in ['model-rejected','provider-transport-failure'] for e in local))
        paths[path]={'caseId':case,'injectedRequestId':injected['requestId'],
                     'candidateReplayMode':'complete' if complete else 'historical bounded excerpt',
                     'correctionRequestId':correction['requestId'] if correction else None,
                     'correctionResponse':corrected,'rejectionEvents':rejected,'toolStartEvents':calls,'toolCompletionEvents':finished,
                     'durationSeconds':x['durationSeconds'],'liveCost':x['reportedProviderCost'],
                     'priorContextCopiedExactly':bool(corrected) and corrected.get('toolArguments')==json.JSONDecoder().raw_decode(candidate)[0]['toolArguments']}
    check(None,'all prior business records unchanged',manifest['businessRecordsUnchanged'])
    return {'status':'PASS' if all(c['passed'] for c in checks) and len(paths)==2 else 'FAIL',
            'checks':checks,'paths':paths,'traceInventory':inventory,'approvedBusinessReplay':False,
            'scope':'Isolated controlled step-action correction only; synthetic plan/final marker. Full business acceptance remains incomplete.'}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('capture',type=Path);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    if args.output.resolve().is_relative_to(args.capture.resolve()):parser.error('Write outside preserved capture')
    result=inspect(args.capture);args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x',encoding='utf-8') as out:json.dump(result,out,indent=2)
    print(result['status'],[(c['path'],c['check']) for c in result['checks'] if not c['passed']])
    raise SystemExit(0 if result['status']=='PASS' else 1)
