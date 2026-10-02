"""Controlled valid-approval nested denial and Luis positive control; no provider calls."""
import copy, hashlib, json, subprocess, time, uuid
import httpx
from baseline import baseline
from capture import collect, wait
from capture_step_correction import records, envelope
from capture_business_diagnostic import normalized
from capture_reviewed_replay import verify_source
from curate_business_replay import ROOT, CASE
from finalize_evidence import finalize
from login import login
from readiness import ready

def plan(parent,child):
    return {'capabilityName':parent,'createdAt':'2026-10-02T00:00:00Z','status':'VALID','tasks':[
        {'taskId':'delegate','title':'Delegate supplied approval','status':'PENDING','capabilityName':child,
         'intent':'Pass supplied explicit approval unchanged.','dependsOn':[],'expectedOutputs':['Receipt'],
         'parallelGroup':None,'note':''}]}

def stages(body,start,positive=False):
    model='meta/muse-spark-1.3-contributor'; steps=[]
    def add(skill,markers,value=None,selector=None):
        step={'contains':[body['caseId'],"Fulfill the mission for skill '"+skill+"'"], 'systemContains':markers,
              'missionInputEquals':copy.deepcopy(body),'after':[start+len(steps)-1],
              'provenance':{'kind':'Hand-authored controlled authorization scaffold; not Muse business replay',
                            'scope':'Valid approval with actual restricted leaf; final envelopes echo actual task evidence'}}
        if selector: step['responseFromCompletedTask']=selector
        else: step['response']=envelope(json.dumps(value),model)
        steps.append(step)
    add('authorizationParent',['Create an ordered flight plan'],plan('authorizationParent','authorizationNested'))
    add('authorizationParent',['Exact capability/tool: authorizationNested'],{'stepAction':'CALL_TOOL','taskId':'delegate','toolName':'authorizationNested','toolArguments':body})
    markers=['Create an ordered flight plan']
    if not positive: markers+=['Available sub-skills (use these exact names for task capabilityName):\n(none)']
    add('authorizationNested',markers,plan('authorizationNested','createServiceRequest'))
    if not positive:
        add('authorizationNested',["value 'createServiceRequest' is not an exact visible capability name."],plan('authorizationNested','createServiceRequest'))
    else:
        add('authorizationNested',['Exact capability/tool: createServiceRequest'],{'stepAction':'CALL_TOOL','taskId':'delegate','toolName':'createServiceRequest','toolArguments':{'approval':body['approval']}})
        add('authorizationNested',['All required plan tasks are already COMPLETE.'],selector={'taskId':'delegate','skillName':'createServiceRequest'})
        add('authorizationParent',['All required plan tasks are already COMPLETE.'],selector={'taskId':'delegate','skillName':'authorizationNested'})
    return steps

def creation_calls():
    p=subprocess.run(['docker','logs','equipment-acceptance-python-1'],capture_output=True,text=True,encoding='utf-8',errors='replace',check=True)
    return sum('/skills/createServiceRequest ' in line for line in (p.stdout+p.stderr).splitlines())

def run():
    ready();build=baseline();secrets=json.loads((ROOT/'.runtime/secrets.json').read_bytes());tokens={u:login(u) for u in ['maya','luis']}
    fixture=ROOT/'fixtures/replay/business-reviewed-v1.json';bundle=json.loads(fixture.read_bytes())
    approval_file=ROOT/'fixtures/replay/business-reviewed-v1-approval.json';approval_record=json.loads(approval_file.read_bytes())
    if hashlib.sha256(fixture.read_bytes()).hexdigest()!=approval_record['fixtureSha256']:raise ValueError('Unapproved fixture')
    out=ROOT/'evidence'/('nested-authorization-offline-'+time.strftime('%Y%m%d-%H%M%S'));out.mkdir()
    def save(name,value):(out/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
    cases,results=[],[];save('business-records-before.json',records())
    with httpx.Client(timeout=180,trust_env=False) as client:
        try:
            for path,port in [('java',18081),('sidecar',18082)]:
                api=f'http://127.0.0.1:{port}';storage='java' if path=='java' else 'python';case='nested-approval-'+path+'-'+uuid.uuid4().hex;cases.append(case)
                sample=bundle['scenarios']['baseline'][path];verify_source(sample)
                base=normalized(sample['steps'],CASE,case);assessment_body=normalized(sample['input'],CASE,case);expected=normalized(sample['expected'],CASE,case)
                # Execution/version assigned only after assessment; register its source stages first.
                registration={'mode':'replay','path':path,'steps':base}
                r=client.post('http://127.0.0.1:18090/control/cases/'+case,json=registration,headers={'X-Control-Key':secrets['control']});r.raise_for_status()
                r=client.post(api+'/assessments',json=assessment_body,headers={'Authorization':'Bearer '+tokens['maya']});r.raise_for_status();assessment=wait(client,api,r.json()['id'],tokens['maya'],timeout=180)
                save(path+'-assessment.json',assessment);save(path+'-expected.json',expected);save(path+'-input.json',assessment_body)
                if assessment['status']!='COMPLETED':raise ValueError('Assessment failed')
                results.append({'path':path,'caseId':case,'executionId':assessment['id'],'status':assessment['status']})
                quote=next(q for q in expected['quotes'] if q['option']=='expedited')
                approval={'assessmentVersion':assessment['assessmentVersion'],'option':'expedited','quoteId':quote['quoteId'],'attendance':quote['attendance'],'scope':quote['scope'],'cap':78000,'approved':True,'idempotencyKey':case+'-nested'}
                body={'caseId':case,'approval':approval};denial=stages(body,len(base));positive=stages(body,len(base)+len(denial),True)
                extension={'steps':denial+positive,'expectedUsed':list(range(len(base)))}
                r=client.post('http://127.0.0.1:18090/control/extend/'+case,json=extension,headers={'X-Control-Key':secrets['control']});r.raise_for_status()
                registration['steps']=base+denial+positive;save(path+'-registration.json',registration);save(path+'-nested-input.json',body)
                observations=[]
                for who in ['maya','luis']:
                    prior=records()[storage]['requests'];calls_before=creation_calls()
                    r=client.post(api+'/v1/skills/authorizationParent/executions',json=body,headers={'Authorization':'Bearer '+tokens[who]});r.raise_for_status()
                    result=wait(client,api,r.json()['id'],tokens[who],timeout=90)
                    observation={'caller':who,'httpStatus':r.status_code,'terminal':result,'requestsBefore':prior,'requestsAfter':records()[storage]['requests'],'creationEndpointCallsBefore':calls_before,'creationEndpointCallsAfter':creation_calls()}
                    observations.append(observation);save(path+'-nested-observations.json',observations);print(path,who,result['status'],flush=True)
        finally:
            collect(client,out,cases,secrets,tokens.values());save('business-records-after.json',records())
            save('manifest.json',{**build,'mode':'offline valid-approval nested authorization','results':results,'paidCalls':0,'fixtureSha256':hashlib.sha256(fixture.read_bytes()).hexdigest(),'scope':'Reviewed baseline assessments plus explicitly hand-authored authorization scaffolding and dynamic echo of real receipt; not new Muse judgment','authorizationOverlaySha256':hashlib.sha256((ROOT/'compose.authorization.yaml').read_bytes()).hexdigest()})
            finalize(out);print(out,flush=True)
    return out
if __name__=='__main__':run()
