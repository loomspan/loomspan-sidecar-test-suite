import os
import httpx, jwt
from jwt import PyJWKClient
from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.responses import JSONResponse
app=FastAPI()
from . import business
jwks=PyJWKClient(os.environ['JWKS'])
def identity(authorization:str=Header('')):
    try:
        scheme, token=authorization.split(' ',1)
        if scheme.lower()!='bearer': raise ValueError()
        claims=jwt.decode(token,jwks.get_signing_key_from_jwt(token).key,algorithms=['RS256'],issuer=os.environ['ISSUER'],audience='equipment-service',options={'require':['exp','iat','iss','sub']})
        if not claims['sub']: raise ValueError()
        return claims,authorization
    except (ValueError,jwt.PyJWTError): raise HTTPException(401,'invalid token')
@app.get('/health')
def health(): return {'status':'up'}
@app.post('/v1/skills/{skill}/executions')
async def submit(skill:str,body:dict,who=Depends(identity)):
    async with httpx.AsyncClient(timeout=30) as client:
        r=await client.post(os.environ['SIDECAR']+'/v1/skills/'+skill+'/executions',json=body,headers={'Authorization':who[1]})
    return JSONResponse(r.json(),status_code=r.status_code)
@app.get('/v1/executions/{execution_id}')
async def poll(execution_id:str,who=Depends(identity)):
    async with httpx.AsyncClient(timeout=30) as client:
        r=await client.get(os.environ['SIDECAR']+'/v1/executions/'+execution_id,headers={'Authorization':who[1]})
    body=r.json()
    if r.status_code==200 and body.get('status')=='COMPLETED' and body.get('skillName')=='resolveEquipment':
        try: body['assessmentVersion']=business.save_assessment(execution_id,body['result'],who[0])
        except (HTTPException,ValueError,KeyError,TypeError):
            body['status']='FAILED';body['failure']={'kind':'ASSESSMENT_VALIDATION','message':'Missing or altered authoritative evidence'}
            body['frameworkStatus']='COMPLETED'
    return JSONResponse(body,status_code=r.status_code)

@app.post('/assessments',status_code=202)
async def assess(body:dict,who=Depends(identity)):
    business.role(who[0],'ASSESS_EQUIPMENT'); business.scoped(who[0],body['assetId'])
    return await submit('resolveEquipment',body,who)

@app.get('/assessments/{execution_id}')
async def assessment(execution_id:str,who=Depends(identity)):
    return await poll(execution_id,who)

@app.post('/service-requests',status_code=202)
async def commitment(approval:dict,who=Depends(identity)):
    # Deliberately reach Loomspan authorization, including otherwise-valid Maya requests.
    return await submit('createServiceRequest',{'approval':approval},who)

@app.get('/service-requests/by-key/{key}')
def recovery(key:str,who=Depends(identity)):
    return business.recover(key,who[0])

@app.post('/skills/{name}')
async def deterministic(name:str,body:dict,who=Depends(identity)):
    if name=='createServiceRequest': return await business.create(body['approval'],who[0])
    if name not in ['assetContext','serviceHistory','referenceEvidence','serviceTerms','entitlements','serviceResources','continuityOptions','quoteOptions']: raise HTTPException(404)
    return await business.leaf(name,body,who[0])
