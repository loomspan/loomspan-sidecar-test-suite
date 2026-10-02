"""Offline creation/denial/idempotency/recovery through actual Framework boundaries."""
import copy, hashlib, json, socket, threading, time, uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import httpx
from baseline import baseline
from capture import collect, wait
from capture_step_correction import records
from capture_business_diagnostic import normalized
from capture_reviewed_replay import verify_source
from curate_business_replay import ROOT, CASE
from finalize_evidence import finalize
from login import login
from readiness import ready

def lost_result(api, execution, token):
    """A local proxy observes completion then closes without delivering the HTTP result."""
    observed={}
    class Drop(BaseHTTPRequestHandler):
        def log_message(self,*args): pass
        def do_GET(self):
            try:
                with httpx.Client(timeout=60,trust_env=False) as client:
                    observed['upstream']=wait(client,api,execution,token,timeout=60)
                self.connection.shutdown(socket.SHUT_RDWR)
            finally:
                self.connection.close(); self.close_connection=True
    server=ThreadingHTTPServer(('127.0.0.1',0),Drop)
    thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start()
    try:
        with httpx.Client(timeout=65,trust_env=False) as client:
            try:
                client.get(f'http://127.0.0.1:{server.server_port}/lost-result').raise_for_status()
                observed['clientError']=None
            except httpx.TransportError as error: observed['clientError']=type(error).__name__
    finally:
        server.shutdown();server.server_close();thread.join(timeout=2)
    return observed

def response_body(response):
    try: return response.json()
    except ValueError: return {'rawBody':response.text}

def run():
    ready(); build=baseline(); secrets=json.loads((ROOT/'.runtime/secrets.json').read_bytes())
    tokens={who:login(who) for who in ['maya','luis']}
    file=ROOT/'fixtures/replay/business-reviewed-v1.json'; bundle=json.loads(file.read_bytes())
    approval_file=ROOT/'fixtures/replay/business-reviewed-v1-approval.json'
    approval_record=json.loads(approval_file.read_bytes())
    if hashlib.sha256(file.read_bytes()).hexdigest()!=approval_record['fixtureSha256']: raise ValueError('Unapproved fixture bytes')
    out=ROOT/'evidence'/('service-requests-offline-'+time.strftime('%Y%m%d-%H%M%S'));out.mkdir()
    def save(name,value): (out/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
    cases,results=[],[]; before=records();save('business-records-before.json',before)
    with httpx.Client(timeout=300,trust_env=False) as client:
        try:
            for path,port in [('java',18081),('sidecar',18082)]:
                api=f'http://127.0.0.1:{port}';storage='java' if path=='java' else 'python'
                case='service-acceptance-'+path+'-'+uuid.uuid4().hex;cases.append(case)
                sample=bundle['scenarios']['baseline'][path];verify_source(sample)
                body=normalized(sample['input'],CASE,case);expected=normalized(sample['expected'],CASE,case)
                steps=normalized(sample['steps'],CASE,case)
                registration={'mode':'replay','path':path,'steps':steps}
                save(path+'-registration.json',registration);save(path+'-input.json',body);save(path+'-expected.json',expected)
                r=client.post('http://127.0.0.1:18090/control/cases/'+case,json=registration,headers={'X-Control-Key':secrets['control']});r.raise_for_status()
                r=client.post(api+'/assessments',json=body,headers={'Authorization':'Bearer '+tokens['maya']});r.raise_for_status()
                assessment=wait(client,api,r.json()['id'],tokens['maya'],timeout=180);save(path+'-assessment.json',assessment)
                if assessment['status']!='COMPLETED': raise ValueError('Assessment failed')
                quote=next(q for q in expected['quotes'] if q['option']=='expedited')
                results.append({'path':path,'caseId':case,'executionId':assessment['id'],'status':assessment['status'],'expectedCalls':len(steps)})
                approval={'assessmentVersion':assessment['assessmentVersion'],'option':'expedited','quoteId':quote['quoteId'],'attendance':quote['attendance'],'scope':quote['scope'],'cap':78000,'idempotencyKey':case+'-approved','approved':True}
                observations=[]
                def submit(name,value,who='luis',drop=False):
                    prior=records()[storage]['requests']
                    r=client.post(api+'/service-requests',json=value,headers={'Authorization':'Bearer '+tokens[who]})
                    observation={'name':name,'caller':who,'approval':copy.deepcopy(value),'httpStatus':r.status_code,'admission':response_body(r),'requestsBefore':prior}
                    if r.status_code==202:
                        execution=r.json()['id']
                        if drop:
                            observation['lostResult']=lost_result(api,execution,tokens[who]);observation['terminal']=observation['lostResult']['upstream']
                        else: observation['terminal']=wait(client,api,execution,tokens[who],timeout=60)
                    observation['requestsAfter']=records()[storage]['requests'];observations.append(observation)
                    save(path+'-observations.json',observations)
                    print(path,name,observation.get('terminal',{}).get('status',r.status_code),flush=True)
                    return observation
                missing=copy.deepcopy(approval);missing['approved']=False;missing['idempotencyKey']=case+'-missing'
                submit('missing-approval',missing)
                submit('unauthorized-maya',approval,who='maya')
                changed=copy.deepcopy(approval);changed['cap']=77999;changed['idempotencyKey']=case+'-terms'
                submit('changed-quote-terms',changed)
                created=submit('approved-create-lost-result',approval,drop=True)
                r=client.post('http://127.0.0.1:18090/control/clock/'+case,json={'now':quote['expiresAt']},headers={'X-Control-Key':secrets['control']});r.raise_for_status();save(path+'-expiry-clock.json',r.json())
                r=client.get(api+'/service-requests/by-key/'+approval['idempotencyKey'],headers={'Authorization':'Bearer '+tokens['luis']});save(path+'-recovery.json',{'httpStatus':r.status_code,'body':response_body(r)})
                submit('same-content-retry-after-expiry',approval)
                changed=copy.deepcopy(approval);changed['cap']=77999
                submit('same-key-content-conflict',changed)
                expired=copy.deepcopy(approval);expired['idempotencyKey']=case+'-expired-new'
                submit('new-request-at-expiry',expired)
                r=client.get(api+'/service-requests/by-key/'+approval['idempotencyKey'],headers={'Authorization':'Bearer '+tokens['maya']});save(path+'-unauthorized-recovery.json',{'httpStatus':r.status_code,'body':response_body(r)})
                save(path+'-observations.json',observations)

        finally:
            collect(client,out,cases,secrets,tokens.values());save('business-records-after.json',records())
            save('manifest.json',{**build,'mode':'offline service-request acceptance','results':results,'paidCalls':0,'sources':{p:bundle['scenarios']['baseline'][p]['sourceCapture'] for p in ['java','sidecar']},'fixtureSha256':hashlib.sha256(file.read_bytes()).hexdigest(),'approvalRecordSha256':hashlib.sha256(approval_file.read_bytes()).hexdigest(),'scope':'Fresh reviewed baseline assessment; direct deterministic creation, denial, lost async result response, retry and recovery at expiry; not nested authorization acceptance'})
            finalize(out);print(out,flush=True)
    return out
if __name__=='__main__':run()
