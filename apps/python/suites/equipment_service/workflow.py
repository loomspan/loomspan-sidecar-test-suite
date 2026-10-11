import json
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from ...infrastructure.sidecar_client import submit, poll as poll_execution
from . import business

async def poll(execution_id, who):
    response = await poll_execution(execution_id, who)
    return complete(execution_id, response, who)


def complete(execution_id, response, who):
    body = json.loads(response.body)
    if response.status_code == 200 and body.get('status') == 'COMPLETED' and body.get('skillName') == 'resolveEquipment':
        try:
            body['assessmentVersion'] = business.save_assessment(execution_id, body['result'], who[0])
        except (HTTPException, ValueError, KeyError, TypeError):
            body['status'] = 'FAILED'
            body['failure'] = {'kind': 'ASSESSMENT_VALIDATION', 'message': 'Missing or altered authoritative evidence'}
            body['frameworkStatus'] = 'COMPLETED'
    return JSONResponse(body, status_code=response.status_code)
