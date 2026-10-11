import os
import httpx
from fastapi.responses import JSONResponse

async def submit(skill:str,body:dict,who):
    async with httpx.AsyncClient(timeout=30) as client:
        r=await client.post(os.environ['SIDECAR']+'/v1/skills/'+skill+'/executions',json=body,headers={'Authorization':who[1]})
    return JSONResponse(r.json(),status_code=r.status_code)
async def poll(execution_id:str,who):
    async with httpx.AsyncClient(timeout=30) as client:
        r=await client.get(os.environ['SIDECAR']+'/v1/executions/'+execution_id,headers={'Authorization':who[1]})
    return JSONResponse(r.json(),status_code=r.status_code)
