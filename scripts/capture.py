"""Explicit live capture through deployed apps; no substitute model or orchestration."""
import environment as target_env
import argparse, hashlib, json, pathlib, subprocess, time, uuid
import httpx
from concurrent.futures import ThreadPoolExecutor
from login import login
from readiness import ready
from finalize_evidence import finalize
from baseline import baseline
from model_profile import model_profile
ROOT=pathlib.Path(__file__).resolve().parents[1]
def collect(client,out,cases,secrets,tokens,paths=('java','sidecar')):
    r=client.get(target_env.url(18090, '/control/journal', '127.0.0.1'),headers={'X-Control-Key':secrets['control']});r.raise_for_status()
    events=[e for e in r.json() if e.get('caseId') in cases]
    (out/'journal.json').write_text(json.dumps(events,indent=2),encoding='utf-8')
    traces=[]
    for path,port in [('java',target_env.port(18081)),('sidecar',target_env.port(18083))]:
        if path not in paths: continue
        base=f'http://127.0.0.1:{port}/_loomspan/observability/v1'; headers={'X-loomspan-Api-Key':secrets['observer']}
        r=client.get(base+'/traces',headers=headers);r.raise_for_status()
        for item in r.json()['items']:
            artifact=client.get(base+'/traces/'+item['traceId']+'/artifact',headers=headers);artifact.raise_for_status();raw=artifact.content
            matched=[case for case in cases if case.encode() in raw]
            if not matched: continue
            if any(s.encode() in raw for s in list(tokens)+list(secrets.values())): raise RuntimeError('Credential detected in trace; refusing export')
            directory=out/path/'traces';directory.mkdir(parents=True,exist_ok=True)
            name='loomspan-trace-'+item['traceId']+'.ndjson';(directory/name).write_bytes(raw)
            traces.append({'path':path,'cases':matched,**item,'file':f'{path}/traces/{name}','sha256':hashlib.sha256(raw).hexdigest()})
    (out/'trace-index.json').write_text(json.dumps(traces,indent=2))
    return events,traces
def wait(client,api,execution,token,timeout=630):
    deadline=time.monotonic()+timeout
    while time.monotonic()<deadline:
        r=client.get(api+'/v1/executions/'+execution,headers={'Authorization':'Bearer '+token});r.raise_for_status();body=r.json()
        if body['status'] in ['COMPLETED','FAILED']: return body
        time.sleep(.5)
    raise TimeoutError('execution deadline exceeded: '+execution)
def run(path='both', priority=False, parallel=False):
    paths=('java','sidecar') if path=='both' else (path,)
    ready();build=baseline();profile=model_profile(paths);s=json.loads((ROOT/'.runtime/secrets.json').read_text());maya=login('maya')
    out=ROOT/'evidence'/('live-'+time.strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:6]);out.mkdir(parents=True)
    cases=[];results=[]
    def execute(target):
        path,port=target
        with httpx.Client(timeout=300,trust_env=False) as client:
            case='case-'+path+'-'+uuid.uuid4().hex; cases.append(case)
            body=json.loads((ROOT/'fixtures/base-case.json').read_text());body['caseId']=case
            if priority:body['context']['restorationRiskPreference']='Prioritize continuity despite higher cost; urgently escalate loaner approval while retaining diagnosis as needed.'
            (out/(path+'-input.json')).write_text(json.dumps(body,indent=2))
            item={'path':path,'caseId':case,'status':'CHECK_ERROR'};results.append(item)
            try:
                r=client.post(target_env.url(18090, '/control/cases/', '127.0.0.1')+case,json={'mode':'live','path':path},headers={'X-Control-Key':s['control']});r.raise_for_status()
                api=f'http://127.0.0.1:{port}';r=client.post(api+'/assessments',json=body,headers={'Authorization':'Bearer '+maya});r.raise_for_status();execution=r.json()['id']
                item['executionId']=execution
                print(path,'submitted',execution,flush=True)
                result=wait(client,api,execution,maya,timeout=build.get('missionTimeoutSeconds',600)+30)
            except (httpx.HTTPError, TimeoutError, ValueError, KeyError) as error:
                result={'status':'CHECK_ERROR','errorType':type(error).__name__}
            (out/(path+'-assessment.json')).write_text(json.dumps(result,indent=2))
            item['status']=result['status'];print(path,result['status'],flush=True)
    with httpx.Client(timeout=300,trust_env=False) as client:
      try:
        targets=[t for t in [('java',target_env.port(18081)),('sidecar',target_env.port(18082))] if t[0] in paths]
        if parallel:
            with ThreadPoolExecutor(max_workers=2) as workers:list(workers.map(execute,targets))
        else:
            for target in targets:execute(target)
      finally:
        manifest={**build,'mode':'live',**profile,'priorityVariation':priority,'parallelPaths':parallel,'selectedPaths':list(paths),'results':results,'traces':0,'review':'PENDING'}
        (out/'manifest.json').write_text(json.dumps(manifest,indent=2))
        try:
            events,traces=collect(client,out,cases,s,[maya],paths)
            manifest['traces']=len(traces)
        except Exception as error:
            manifest['collectionError']=type(error).__name__
            for name in ['journal.json','trace-index.json']:
                if not (out/name).exists(): (out/name).write_text('[]')
        finally:
            (out/'manifest.json').write_text(json.dumps(manifest,indent=2))
            finalize(out);print(out,flush=True)
    return out

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--path',choices=['java','sidecar','both'],default='both');parser.add_argument('--priority',action='store_true');parser.add_argument('--parallel',action='store_true');args=parser.parse_args()
    out=run(args.path,args.priority,args.parallel)
    manifest=json.loads((out/'manifest.json').read_bytes());results=manifest['results']
    return 0 if not manifest.get('collectionError') and results and all(r['status']=='COMPLETED' for r in results) else 1

if __name__=='__main__': raise SystemExit(main())
