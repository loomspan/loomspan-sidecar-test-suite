"""Controlled live full-workflow correction, or strict replay of its reviewed fixture."""
import environment as target_env
import argparse
import json
import time
import uuid
import httpx
from baseline import baseline
from capture import collect, wait
from capture_step_correction import records
from capture_business_diagnostic import normalized
from capture_reviewed_replay import verify_source, require_offline_provider
from curate_business_replay import ROOT, CASE, digest
from finalize_evidence import finalize
from full_correction import stages
from login import login
from model_profile import model_profile
from readiness import ready


def run(offline=False, rehearsal=False):
    ready()
    if offline or rehearsal: require_offline_provider()
    build,profile=baseline(),model_profile()
    original=ROOT/'fixtures/replay/business-reviewed-v1.json'
    bundle=json.loads(original.read_bytes())
    approved=json.loads((original.parent/'business-reviewed-v1-approval.json').read_bytes())
    if approved['fixtureSha256']!=digest(original):raise ValueError('Baseline approval mismatch')
    fixture=ROOT/'fixtures/replay/full-correction-reviewed-v1.json'
    replay=json.loads(fixture.read_bytes()) if offline else None
    if offline:
        from curate_full_correction import verify_sample
        for sample in replay['samples'].values():verify_sample(sample)
    out=ROOT/'evidence'/('full-correction-'+('rehearsal-' if rehearsal else 'offline-' if offline else 'live-')+time.strftime('%Y%m%d-%H%M%S'))
    out.mkdir()
    secrets=json.loads((ROOT/'.runtime/secrets.json').read_bytes());token=login('maya')
    def save(name,value):(out/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
    cases,results=[],[];save('business-records-before.json',records())
    with httpx.Client(timeout=300,trust_env=False) as client:
        try:
            for path,port in [('java',target_env.port(18081)),('sidecar',target_env.port(18082))]:
                sample=bundle['scenarios']['baseline'][path];verify_source(sample)
                case='full-correction-'+path+'-'+uuid.uuid4().hex;cases.append(case)
                if offline:
                    steps=normalized(replay['samples'][path]['steps'],CASE,case)
                    expected=normalized(replay['samples'][path]['expected'],CASE,case)
                    save(path+'-expected.json',expected)
                elif rehearsal:
                    source=normalized(sample['steps'],CASE,case)
                    original_response=next(s['response'] for s in source if s['stageSkill']=='compareOptions')
                    steps=stages(source,original_response,{'kind':'Explicit offline original-content rehearsal, not genuine correction'})
                    save(path+'-expected.json',normalized(sample['expected'],CASE,case))
                else:
                    steps=stages(normalized(sample['steps'],CASE,case))
                body=normalized(sample['input'],CASE,case)
                registration={'mode':'replay' if offline or rehearsal else 'controlled-live','path':path,'steps':steps}
                save(path+'-registration.json',registration);save(path+'-input.json',body)
                save(path+'-baseline-expected.json',normalized(sample['expected'],CASE,case))
                r=client.post(target_env.url(18090, '/control/cases/', '127.0.0.1')+case,json=registration,headers={'X-Control-Key':secrets['control']});r.raise_for_status()
                api=f'http://127.0.0.1:{port}'
                r=client.post(api+'/assessments',json=body,headers={'Authorization':'Bearer '+token});r.raise_for_status()
                item={'path':path,'caseId':case,'executionId':r.json()['id'],'expectedCalls':len(steps)};results.append(item)
                result=wait(client,api,item['executionId'],token,timeout=420)
                item['status']=result['status'];save(path+'-assessment.json',result)
                print(path,result['status'],flush=True)
        finally:
            events,index=collect(client,out,cases,secrets,[token])
            paid=sum(e['event']=='model-response' and e.get('provenance')=='live OpenRouter' for e in events)
            save('business-records-after.json',records())
            save('manifest.json',{**build,**profile,'mode':'offline full correction rehearsal' if rehearsal else 'offline full correction replay' if offline else 'controlled live full correction',
                'results':results,'paidCalls':paid,'approved':False,'baselineFixtureSha256':digest(original),
                'correctionFixtureSha256':digest(fixture) if offline else None,
                'scope':'Complete business workflow; extra-brace fault; genuine correction; offline parent envelopes copy actual child evidence'})
            finalize(out);print(out,flush=True)
    return out


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group();group.add_argument('--offline',action='store_true');group.add_argument('--rehearsal',action='store_true')
    args=parser.parse_args();run(args.offline,args.rehearsal)
