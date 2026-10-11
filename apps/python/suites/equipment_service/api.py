from fastapi import APIRouter, Depends
from ...infrastructure.security import identity
from . import business
from .workflow import submit, poll

router = APIRouter()

@router.post('/assessments',status_code=202)
async def assess(body:dict,who=Depends(identity)):
    business.role(who[0],'ASSESS_EQUIPMENT'); business.scoped(who[0],body['assetId'])
    return await submit('resolveEquipment',body,who)

@router.get('/assessments/{execution_id}')
async def assessment(execution_id:str,who=Depends(identity)):
    return await poll(execution_id,who)

@router.post('/service-requests',status_code=202)
async def commitment(approval:dict,who=Depends(identity)):
    # Deliberately reach Loomspan authorization, including otherwise-valid Maya requests.
    return await submit('createServiceRequest',{'approval':approval},who)

@router.get('/service-requests/by-key/{key}')
def recovery(key:str,who=Depends(identity)):
    return business.recover(key,who[0])

