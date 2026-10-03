"""Small live access check on both paths; retain failures as well as successes."""
import environment as target_env
import json, pathlib, time, uuid
import httpx
from login import login
from baseline import baseline
from model_profile import model_profile
from readiness import ready
from capture import collect, wait
from finalize_evidence import finalize
ROOT=pathlib.Path(__file__).resolve().parents[1]


def run():
    ready();build=baseline();profile=model_profile()
    out=ROOT/'evidence'/('compatibility-'+time.strftime('%Y%m%d-%H%M%S'));out.mkdir(parents=True)
    secrets=json.loads((ROOT/'.runtime/secrets.json').read_text());token=login()
    results=[];cases=[]
    with httpx.Client(timeout=300,trust_env=False) as client:
        try:
            for path,port in [('java',target_env.port(18081)),('sidecar',target_env.port(18082))]:
                case='compat-'+path+'-'+uuid.uuid4().hex;cases.append(case)
                item={'path':path,'caseId':case,'passed':False};results.append(item)
                try:
                    r=client.post(target_env.url(18090, '/control/cases/', '127.0.0.1')+case,json={'mode':'live','path':path},
                                  headers={'X-Control-Key':secrets['control']});r.raise_for_status()
                    api=f'http://127.0.0.1:{port}'
                    r=client.post(api+'/v1/skills/compatibility/executions',json={'caseId':case},headers={'Authorization':'Bearer '+token});r.raise_for_status()
                    item['executionId']=r.json()['id']
                    result=wait(client,api,item['executionId'],token,timeout=300)
                    (out/(path+'-execution.json')).write_text(json.dumps(result,indent=2))
                    item['status']=result['status']
                    item['passed']=result['status']=='COMPLETED' and json.loads(result['result'])=={'caseId':case,'status':'COMPATIBLE'}
                except (httpx.HTTPError,TimeoutError,ValueError,KeyError) as error:
                    item['status']='CHECK_ERROR';item['errorType']=type(error).__name__
                print(path,item['status'],flush=True)
        finally:
            events,traces=collect(client,out,cases,secrets,[token])
            for item in results:
                requests=[e for e in events if e.get('caseId')==item['caseId'] and e['event']=='model-request']
                responses=[e for e in events if e.get('caseId')==item['caseId'] and e['event']=='model-response']
                item['requestCount']=len(requests)
                item['actualRequestProfileVerified']=bool(requests) and all(e['request'].get('model')==profile['model'] and
                    e['request'].get('reasoning_effort')==profile['reasoning'] for e in requests)
                item['providerAccessVerified']=bool(responses) and all(e.get('status')==200 and e.get('provenance')=='live OpenRouter' for e in responses)
                item['frameworkTraceVerified']=any(t.get('path')==item['path'] and item['caseId'] in t['cases'] and t.get('outcome')=='SUCCEEDED' for t in traces)
                item['passed']=item['passed'] and all(item[k] for k in ['actualRequestProfileVerified','providerAccessVerified','frameworkTraceVerified'])
            (out/'manifest.json').write_text(json.dumps({**build,**profile,'scope':'Small live access compatibility only; not full-workflow acceptance','results':results},indent=2))
            finalize(out)
            print(out,flush=True)
    return 0 if len(results)==2 and all(r['passed'] for r in results) else 1


if __name__=='__main__':raise SystemExit(run())
