"""Offline creation/denial/idempotency/recovery through actual Framework boundaries."""
from replay_selection import business_fixture, approval_file as business_approval
import environment as target_env
import copy, hashlib, json, socket, threading, time, uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import httpx
from pathlib import Path
from acceptance_report import checksums
from baseline import baseline
from capture import collect, wait
from capture_step_correction import records
from capture_business_diagnostic import normalized
from capture_reviewed_replay import verify_source, require_offline_provider
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

def run(live_source=None, paths=('java','sidecar')):
    if live_source is None: require_offline_provider()
    else:
        live_source=Path(live_source).resolve(); checksums(live_source)
    ready(); build=baseline(); secrets=json.loads((ROOT/'.runtime/secrets.json').read_bytes())
    tokens={who:login(who) for who in ['maya','luis']}
    if live_source is None:
        file=business_fixture(); bundle=json.loads(file.read_bytes())
        approval_file=business_approval()
        approval_record=json.loads(approval_file.read_bytes())
        if hashlib.sha256(file.read_bytes()).hexdigest()!=approval_record['fixtureSha256']: raise ValueError('Unapproved fixture bytes')
    out=ROOT/'evidence'/(('service-requests-live-' if live_source else 'service-requests-offline-')+time.strftime('%Y%m%d-%H%M%S'));out.mkdir()
    def save(name,value): (out/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
    cases,results=[],[]; before=records();save('business-records-before.json',before)
    with httpx.Client(timeout=300,trust_env=False) as client:
        try:
            for path,port in [('java',target_env.port(18081)),('sidecar',target_env.port(18082))]:
                api=f'http://127.0.0.1:{port}';storage='java' if path=='java' else 'python'
                if path not in paths: continue
                if live_source:
                    body=json.loads((live_source/(path+'-input.json')).read_bytes())
                    assessment=json.loads((live_source/(path+'-assessment.json')).read_bytes())
                    expected=json.loads(assessment.get('result','{}'));case=body['caseId'];cases.append(case);steps=[]
                    save(path+'-input.json',body);save(path+'-expected.json',expected);save(path+'-assessment.json',assessment)
                    r=client.post(target_env.url(18090, '/control/cases/', '127.0.0.1')+case,json={'mode':'live','path':path},headers={'X-Control-Key':secrets['control']})
                    if r.status_code != 409: r.raise_for_status()
                else:
                    case='service-acceptance-'+path+'-'+uuid.uuid4().hex;cases.append(case)
                    sample=bundle['scenarios']['baseline'][path];verify_source(sample)
                    body=normalized(sample['input'],CASE,case);expected=normalized(sample['expected'],CASE,case)
                    steps=normalized(sample['steps'],CASE,case)
                    registration={'mode':'replay','path':path,'steps':steps}
                    save(path+'-registration.json',registration);save(path+'-input.json',body);save(path+'-expected.json',expected)
                    r=client.post(target_env.url(18090, '/control/cases/', '127.0.0.1')+case,json=registration,headers={'X-Control-Key':secrets['control']});r.raise_for_status()
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
                r=client.post(target_env.url(18090, '/control/clock/', '127.0.0.1')+case,json={'now':quote['expiresAt']},headers={'X-Control-Key':secrets['control']});r.raise_for_status();save(path+'-expiry-clock.json',r.json())
                r=client.get(api+'/service-requests/by-key/'+approval['idempotencyKey'],headers={'Authorization':'Bearer '+tokens['luis']});save(path+'-recovery.json',{'httpStatus':r.status_code,'body':response_body(r)})
                submit('same-content-retry-after-expiry',approval)
                changed=copy.deepcopy(approval);changed['cap']=77999
                submit('same-key-content-conflict',changed)
                expired=copy.deepcopy(approval);expired['idempotencyKey']=case+'-expired-new'
                submit('new-request-at-expiry',expired)
                r=client.get(api+'/service-requests/by-key/'+approval['idempotencyKey'],headers={'Authorization':'Bearer '+tokens['maya']});save(path+'-unauthorized-recovery.json',{'httpStatus':r.status_code,'body':response_body(r)})
                save(path+'-observations.json',observations)

        finally:
            events,index=collect(client,out,cases,secrets,tokens.values(),paths);save('business-records-after.json',records())
            source_requests={e['requestId'] for e in json.loads((live_source/'journal.json').read_bytes()) if e['event']=='model-request'} if live_source else set()
            if live_source:
                # Assessment traces survive a host recreation via the immutable source capture.
                for trace in json.loads((live_source/'trace-index.json').read_bytes()):
                    if trace['path'] not in paths or trace['file'] in {t['file'] for t in index}: continue
                    target=out/trace['file'];target.parent.mkdir(parents=True,exist_ok=True)
                    target.write_bytes((live_source/trace['file']).read_bytes());index.append(trace)
                save('trace-index.json',index)
            provenance = ({k:json.loads((live_source/'manifest.json').read_bytes())[k] for k in ['model','reasoning']} if live_source else {
                'sources':{p:bundle['scenarios']['baseline'][p]['sourceCapture'] for p in paths},
                'fixtureSha256':hashlib.sha256(file.read_bytes()).hexdigest(),
                'approvalRecordSha256':hashlib.sha256(approval_file.read_bytes()).hexdigest()})
            save('manifest.json',{**build,**provenance,'selectedPaths':list(paths),'liveSource':str(live_source) if live_source else None,
                'liveSourceChecksumsSha256':hashlib.sha256((live_source/'checksums.json').read_bytes()).hexdigest() if live_source else None,
                'mode':'live service-request acceptance' if live_source else 'offline service-request acceptance',
                'results':results,'paidCalls':sum(e['event']=='model-response' and e.get('provenance')=='live OpenRouter' and e['requestId'] not in source_requests for e in events),
                'referencedLiveResponses':sum(e['event']=='model-response' and e.get('provenance')=='live OpenRouter' and e['requestId'] in source_requests for e in events),
                'newModelRequestIds':[e['requestId'] for e in events if live_source and e['event']=='model-request' and e['requestId'] not in source_requests],
                'scope':'Assessment followed by direct deterministic creation, denial, lost response, retry and expiry recovery; not nested authorization acceptance'})
            finalize(out);print(out,flush=True)
    return out
if __name__=='__main__':run()
