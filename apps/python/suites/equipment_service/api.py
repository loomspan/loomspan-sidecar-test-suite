from fastapi import APIRouter, Depends
from ...infrastructure.security import identity
from ...infrastructure.sidecar_client import ISSUER as EXECUTION_ISSUER, execution_caller
from . import business
from .workflow import submit, poll

router = APIRouter()

@router.post('/assessments',status_code=202)
async def assess(body:dict,caller=Depends(execution_caller)):
    business.role(caller[0],'ASSESS_EQUIPMENT'); business.scoped(caller[0],body['assetId'])
    return await submit('resolveEquipment',body,caller)

@router.get('/assessments/{execution_id}')
async def assessment(execution_id:str,caller=Depends(execution_caller)):
    return await poll(execution_id,caller)

@router.post('/service-requests',status_code=202)
async def commitment(approval:dict,caller=Depends(execution_caller)):
    # Deliberately reach Loomspan authorization, including otherwise-valid Maya requests.
    return await submit('createServiceRequest',{'approval':approval},caller)

@router.get('/service-requests/by-key/{key}')
def recovery(key:str,who=Depends(identity)):
    return business.recover(key,who | {'iss': EXECUTION_ISSUER})

