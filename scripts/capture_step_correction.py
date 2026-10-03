"""Explicit controlled fault: captured malformed action, one live correction per path.

Planner/final envelopes are synthetic harness scaffolding, not approved business replay.
The live request is forwarded unchanged. No unexpected stage falls back to a provider.
"""
import environment as target_env
import argparse, hashlib, json, pathlib, sqlite3, time, uuid
import httpx
from baseline import baseline
from capture import collect, wait
from finalize_evidence import finalize
from login import login
from model_profile import model_profile
from readiness import ready

ROOT=pathlib.Path(__file__).resolve().parents[1]

def envelope(content,model):
    return {'id':'controlled-'+uuid.uuid4().hex,'object':'chat.completion','created':1790924400,
            'model':model,'choices':[{'index':0,'finish_reason':'stop','message':{'role':'assistant','content':content}}]}

def records():
    result={}
    for path in ['java','python']:
        with sqlite3.connect(f'file:{(ROOT/".runtime"/path/"equipment.db").as_posix()}?mode=ro',uri=True) as db:
            result[path]={table:db.execute('SELECT * FROM '+table+' ORDER BY rowid').fetchall()
                          for table in ['assessments','quotes','requests']}
    return result

def run(offline=False):
    if offline:
        from capture_reviewed_replay import require_offline_provider
        require_offline_provider()
    ready();build=baseline();profile=model_profile()
    out=ROOT/'evidence'/('controlled-step-'+('offline-' if offline else 'live-')+time.strftime('%Y%m%d-%H%M%S'));out.mkdir()
    source=ROOT/'evidence/json-forensics-20261001-220102'
    hashes=json.loads((source/'checksums.json').read_text())
    for name in ['initial-original.txt','initial-request.json']:
        assert hashlib.sha256((source/name).read_bytes()).hexdigest()==hashes[name]
    candidate=(source/'initial-original.txt').read_text()
    action=json.JSONDecoder().raw_decode(candidate)[0]
    assert action['taskId']=='t-entitlements-01' and action['toolName']=='entitlements'
    old_case=action['toolArguments']['caseId']
    original_request=json.loads((source/'initial-request.json').read_text())
    user=next(m['content'] for m in original_request['messages'] if m['role']=='user')
    original_input=json.JSONDecoder().raw_decode(user.split('Canonical mission input:\n',1)[1])[0]
    token=login('maya');secrets=json.loads((ROOT/'.runtime/secrets.json').read_text())
    cases=[];results=[];before=records()
    (out/'business-records-before.json').write_text(json.dumps(before,indent=2))
    provenance={'kind':'captured malformed response injected into isolated diagnostic',
        'sourceCapture':'evidence/live-20261001-220102','sourceRequestId':'1837c3a9035c4ba7aa2203927dba436d',
        'originalSourceModel':'meta/muse-spark-1.3-contributor','originalReasoning':'medium',
        'sourceCandidateSha256':hashes['initial-original.txt'],'sourceRequestSha256':hashes['initial-request.json'],
        'normalization':'caseId only; original extra closing brace retained',
        'scope':'Temporary one-task planner; not original full mission or a controlled old/new prompt A/B',
        'approvedBusinessReplay':False}
    with httpx.Client(timeout=300,trust_env=False) as client:
        try:
            for path,port in [('java',target_env.port(18081)),('sidecar',target_env.port(18082))]:
                case='correction-'+path+'-'+uuid.uuid4().hex;cases.append(case)
                body=json.loads(json.dumps(original_input).replace(old_case,case))
                injected=candidate.replace(old_case,case)
                plan={'capabilityName':'stepCorrectionDiagnostic','createdAt':'2026-10-02T00:00:00Z','status':'VALID',
                    'tasks':[{'taskId':'t-entitlements-01','title':'Read authoritative entitlements','status':'PENDING',
                    'capabilityName':'entitlements','intent':'Look up authoritative entitlement facts for the supplied case and asset.',
                    'dependsOn':[],'expectedOutputs':['Entitlement facts'],'parallelGroup':None,'note':''}]}
                correction={'contains':[case,'REJECTED STEP ACTION EVIDENCE','Unexpected close marker'],
                    'systemContains':['YOUR PREVIOUS ACTION WAS INVALID','Exact capability/tool: entitlements'],
                    'after':[1]}
                if offline:
                    corrected={'stepAction':'CALL_TOOL','taskId':'t-entitlements-01','toolName':'entitlements',
                               'toolArguments':{'caseId':case,'assetId':'NB-P240-017','context':{}}}
                    correction.update(response=envelope(json.dumps(corrected),profile['model']),
                                      provenance='Synthetic valid correction for offline stage/side-effect checks')
                else:correction['live']=True
                steps=[{'contains':[case],'systemContains':['Create an ordered flight plan'],
                    'response':envelope(json.dumps(plan),profile['model']),'provenance':'Synthetic isolated one-task plan'},
                    {'contains':[case],'systemContains':['Exact capability/tool: entitlements'],
                     'systemExcludes':['YOUR PREVIOUS ACTION WAS INVALID'],'after':[0],
                     'response':envelope(injected,profile['model']),'provenance':provenance},
                    correction,
                    {'contains':[case],'systemContains':['All required plan tasks are already COMPLETE.'],'after':[2],
                     'response':envelope(json.dumps({'stepAction':'FINAL_RESPONSE','finalResponse':{'caseId':case,'diagnostic':'complete'}}),profile['model']),
                     'provenance':'Synthetic terminal diagnostic marker; not a model business result'}]
                (out/(path+'-registration.json')).write_text(json.dumps({'mode':'replay' if offline else 'controlled-live',
                    'path':path,'steps':steps},indent=2))
                (out/(path+'-input.json')).write_text(json.dumps(body,indent=2))
                r=client.post(target_env.url(18090, '/control/cases/', '127.0.0.1')+case,json={'mode':'replay' if offline else 'controlled-live',
                    'path':path,'steps':steps},headers={'X-Control-Key':secrets['control']});r.raise_for_status()
                r=client.post(f'http://127.0.0.1:{port}/v1/skills/stepCorrectionDiagnostic/executions',
                    json=body,headers={'Authorization':'Bearer '+token});r.raise_for_status()
                item={'path':path,'caseId':case,'executionId':r.json()['id']};results.append(item)
                terminal=wait(client,f'http://127.0.0.1:{port}',item['executionId'],token,timeout=300)
                item['status']=terminal['status'];(out/(path+'-execution.json')).write_text(json.dumps(terminal,indent=2))
                print(path,terminal['status'],flush=True)
        finally:
            events,traces=collect(client,out,cases,secrets,[token])
            after=records();(out/'business-records-after.json').write_text(json.dumps(after,indent=2))
            (out/'manifest.json').write_text(json.dumps({**build,**profile,'mode':'controlled offline' if offline else 'controlled live correction',
                'results':results,'provenance':provenance,'businessRecordsUnchanged':before==after,
                'scope':'Invalid step-action rejection/recovery only; synthetic planning and final response; not full-workflow acceptance',
                'review':'PENDING','approved':False},indent=2))
            (out/'compose.correction.yaml').write_bytes((ROOT/'compose.correction.yaml').read_bytes())
            finalize(out);print(out,flush=True)
    return out

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--offline',action='store_true');args=parser.parse_args();run(args.offline)
