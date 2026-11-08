from fastapi import HTTPException
import simplejson
from ...infrastructure.sidecar_client import ExecutionResponse, submit, poll as poll_execution
from . import business

async def poll(execution_id, caller):
    response = await poll_execution(execution_id, caller)
    return complete(execution_id, response, caller[0])


def complete(execution_id, response, who):
    if response.status_code != 200:
        return response
    body = simplejson.loads(response.body, use_decimal=True)
    if body.get('status') == 'COMPLETED' and body.get('skillName') == 'resolveEquipment':
        try:
            body['assessmentVersion'] = business.save_assessment(execution_id, body['result'], who)
        except (HTTPException, ValueError, KeyError, TypeError):
            body['status'] = 'FAILED'
            body['failure'] = {'kind': 'ASSESSMENT_VALIDATION', 'message': 'Missing or altered authoritative evidence'}
            body['frameworkStatus'] = 'COMPLETED'
    return ExecutionResponse(body)
