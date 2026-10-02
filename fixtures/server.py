"""External evidence/model fixture. Control API is separate from business routes."""
import asyncio, datetime, json, os, pathlib, time, uuid
import httpx
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
app=FastAPI()
DATA=pathlib.Path(os.getenv('FIXTURE_DATA','/data')); DATA.mkdir(exist_ok=True)
cases={}; gates={}; lock=asyncio.Lock()
def journal(event, **data):
    with (DATA/'journal.ndjson').open('a',encoding='utf-8') as f:
        f.write(json.dumps({'timeNs':time.time_ns(),'event':event,**data})+'\n')

def mission_input_matches(body, step):
    if 'missionInputEquals' not in step:
        return True
    try:
        message=next(m['content'] for m in body.get('messages',[]) if m.get('role')=='user'
                     and m.get('content','').startswith('Mission objective:'))
        actual=json.JSONDecoder().raw_decode(message.split('Canonical mission input:\n',1)[1].lstrip())[0]
        return actual == step['missionInputEquals']
    except (StopIteration, KeyError, IndexError, ValueError):
        return False

def completed_task_response(body, selector):
    """Controlled offline envelope copying actual Framework task evidence unchanged."""
    try:
        system='\n'.join(m.get('content','') for m in body.get('messages',[]) if m.get('role')=='system')
        block=system.split('--- COMPLETED TASK EVIDENCE ---\n',1)[1]
        tasks=json.JSONDecoder().raw_decode(block[block.index('['):])[0]
        matches=[t for t in tasks if t.get('taskId')==selector['taskId'] and t.get('skillName')==selector['skillName']]
        if len(matches)!=1: raise ValueError()
        result=matches[0]['result']
        if isinstance(result,str): json.loads(result)
        else: result=json.dumps(result)
    except (KeyError,IndexError,ValueError,TypeError):
        raise HTTPException(409,'missing or ambiguous completed task evidence')
    return {'id':'controlled-echo-'+uuid.uuid4().hex,'object':'chat.completion','created':1790924400,
            'model':body.get('model','meta/muse-spark-1.3-contributor'),
            'choices':[{'index':0,'finish_reason':'stop','message':{'role':'assistant',
              'content':json.dumps({'stepAction':'FINAL_RESPONSE','finalResponse':result})}}]}
def control(key):
    if not key or key != os.environ['CONTROL_KEY']: raise HTTPException(403)
@app.get('/health')
def health(): return {'status':'up'}
@app.post('/control/cases/{case_id}')
async def register(case_id:str, body:dict, x_control_key:str=Header('')):
    control(x_control_key)
    if case_id in cases: raise HTTPException(409,'case already registered')
    if body.get('mode','replay') not in ['live','replay','controlled-live']:
        raise HTTPException(400,'invalid fixture mode')
    live_steps=[i for i,s in enumerate(body.get('steps',[])) if s.get('live')]
    if live_steps and (body.get('mode')!='controlled-live' or len(live_steps)!=1):
        raise HTTPException(400,'one explicit live stage requires controlled-live mode')
    if body.get('mode')=='controlled-live' and len(live_steps)!=1:
        raise HTTPException(400,'controlled-live requires exactly one live stage')
    if body.get('path') not in [None,'java','sidecar']:
        raise HTTPException(400,'invalid integration path')
    cases[case_id]={**body,'used':[],'attempts':{}}
    for name in body.get('gates',[]): gates[(case_id,name)]=asyncio.Event()
    journal('registered',caseId=case_id,mode=body.get('mode','replay'))
    return {'caseId':case_id}
@app.post('/control/gates/{case_id}/{name}')
async def release(case_id:str,name:str,x_control_key:str=Header('')):
    control(x_control_key); gates[(case_id,name)].set(); journal('released',caseId=case_id,name=name)
    return {'released':True}

@app.post('/control/extend/{case_id}')
async def extend(case_id:str,body:dict,x_control_key:str=Header('')):
    control(x_control_key)
    async with lock:
        if case_id not in cases: raise HTTPException(404,'unregistered case')
        case=cases[case_id]; steps=body.get('steps',[])
        expected=list(range(len(case.get('steps',[]))))
        if case.get('mode')!='replay' or sorted(case['used'])!=expected or body.get('expectedUsed')!=expected:
            raise HTTPException(409,'existing replay stages must be exhausted')
        if not steps or any(s.get('live') for s in steps): raise HTTPException(400,'offline stages required')
        case['steps'].extend(steps)
        journal('extended',caseId=case_id,previousStages=len(expected),addedStages=len(steps))
    return {'caseId':case_id,'stages':len(case['steps'])}
@app.get('/control/journal')
def get_journal(x_control_key:str=Header('')):
    control(x_control_key)
    p=DATA/'journal.ndjson'
    return [json.loads(x) for x in p.read_text().splitlines()] if p.exists() else []

@app.post('/control/clock/{case_id}')
async def clock(case_id:str, body:dict, x_control_key:str=Header('')):
    control(x_control_key)
    if case_id not in cases: raise HTTPException(404,'unregistered case')
    try:
        now=body['now']; parsed=datetime.datetime.fromisoformat(now)
        if parsed.utcoffset() is None: raise ValueError()
    except (KeyError, TypeError, ValueError): raise HTTPException(400,'offset timestamp required')
    cases[case_id]['clock']=now
    journal('clock-set',caseId=case_id,now=now)
    return {'caseId':case_id,'now':now}
@app.get('/records/{case_id}/{kind}')
async def records(case_id:str,kind:str):
    if case_id not in cases: raise HTTPException(404,'unregistered case')
    journal('entered',caseId=case_id,kind=kind)
    gate=gates.get((case_id,kind))
    if gate: await asyncio.wait_for(gate.wait(),180)
    source=json.loads(pathlib.Path('fixtures/business.json').read_text())
    if kind=='clock' and 'clock' in cases[case_id]:
        source['clock']={'now':cases[case_id]['clock']}
    if kind not in source: raise HTTPException(404)
    result={'caseId':case_id,'revision':'1','kind':kind,'data':source[kind]}
    journal('returned',caseId=case_id,kind=kind,result=result)
    return result
@app.post('/model/{path}/v1/chat/completions')
async def model(path:str,request:Request):
    body=await request.json(); serialized=json.dumps(body)
    matches=[k for k in cases if k in serialized]
    if len(matches)!=1:
        journal('model-rejected',path=path,reason='missing or ambiguous case correlation',request=body)
        raise HTTPException(409,'missing or ambiguous case correlation')
    case_id=matches[0]; case=cases[case_id]
    if case.get('path') and case['path']!=path:
        journal('model-rejected',path=path,caseId=case_id,reason='wrong integration path')
        raise HTTPException(409,'wrong integration path')
    request_id=uuid.uuid4().hex
    journal('model-request',path=path,caseId=case_id,requestId=request_id,request=body)
    step=None; i=None
    if case.get('mode')!='live':
        async with lock:
            candidates=[]
            system='\n'.join(m.get('content','') for m in body.get('messages',[]) if m.get('role')=='system')
            for n,item in enumerate(case.get('steps',[])):
                if n in case['used']: continue
                if (all(t in serialized for t in item['contains']) and all(t not in serialized for t in item.get('excludes',[]))
                    and all(t in system for t in item.get('systemContains',[]))
                    and all(t not in system for t in item.get('systemExcludes',[]))
                    and all(d in case['used'] for d in item.get('after',[]))
                    and mission_input_matches(body,item)):candidates.append((n,item))
            if len(candidates)!=1:
                journal('model-rejected',path=path,caseId=case_id,requestId=request_id,reason='unexpected or ambiguous stage',candidates=[n for n,_ in candidates])
                raise HTTPException(409,'unexpected or ambiguous replay stage')
            i,step=candidates[0];case['used'].append(i)
    if case.get('mode')=='live' or (case.get('mode')=='controlled-live' and step.get('live')):
        key=os.getenv('OPENROUTER_API_KEY')
        if not key: raise HTTPException(503,'provider credential unavailable')
        client=httpx.AsyncClient(timeout=240)
        try:
            upstream=client.build_request('POST','https://openrouter.ai/api/v1/chat/completions',json=body,headers={'Authorization':'Bearer '+key})
            response=await client.send(upstream,stream=True)
        except (httpx.HTTPError,ValueError) as error:
            await client.aclose()
            journal('provider-transport-failure',path=path,caseId=case_id,requestId=request_id,errorType=type(error).__name__)
            return JSONResponse({'error':{'message':'Provider transport failed; see fixture journal','type':'upstream_transport_error'}},status_code=502)
        async def relay():
            chunks=[]
            try:
                async for chunk in response.aiter_bytes():
                    chunks.append(chunk)
                    yield chunk
                result=json.loads(b''.join(chunks))
                journal('model-response',path=path,caseId=case_id,requestId=request_id,status=response.status_code,response=result,provenance='live OpenRouter',stage=i)
            except (httpx.HTTPError,ValueError) as error:
                journal('provider-transport-failure',path=path,caseId=case_id,requestId=request_id,errorType=type(error).__name__)
                raise
            finally:
                await response.aclose()
                await client.aclose()
        # Forward upstream headers/body promptly, including any provider whitespace
        # keepalives. This is still one non-streaming Chat Completions JSON response.
        return StreamingResponse(relay(),status_code=response.status_code,media_type=response.headers.get('content-type','application/json'))
    result=(completed_task_response(body,step['responseFromCompletedTask'])
            if 'responseFromCompletedTask' in step else step['response'])
    journal('model-response',path=path,caseId=case_id,requestId=request_id,response=result,stage=i,provenance=step.get('provenance','development scaffold'))
    return result
