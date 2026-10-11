from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from ...infrastructure.security import identity
from . import business
from .contracts import LookupInput, ServiceRequestInput

router = APIRouter()

@router.post('/skills/{name}')
async def deterministic(name:str,body:dict,who=Depends(identity)):
    if name=='createServiceRequest':
        business.role(who[0], 'REQUEST_SERVICE')
        try:
            data=ServiceRequestInput.model_validate(body).model_dump()
        except ValidationError:
            raise HTTPException(400, 'Invalid service-request input contract')
        return await business.create(data['approval'],who[0])
    if name not in ['assetContext','serviceHistory','referenceEvidence','serviceTerms','entitlements','serviceResources','continuityOptions','quoteOptions']: raise HTTPException(404)
    business.role(who[0], 'ASSESS_EQUIPMENT')
    try:
        body=LookupInput.model_validate(body).model_dump()
    except ValidationError:
        raise HTTPException(400, 'Invalid lookup input contract')
    return await business.leaf(name,body,who[0])
