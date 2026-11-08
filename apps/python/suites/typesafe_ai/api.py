from fastapi import APIRouter, Depends, HTTPException
import json
import simplejson
from .policy import decide, number, SUPPORTED_SKILLS
from ...infrastructure.sidecar_client import ExecutionResponse, execution_caller, submit, poll

router = APIRouter(prefix='/suites/typesafe-ai')


@router.post('/evaluations/{skill}', status_code=202)
async def evaluate(skill: str, body: dict, caller=Depends(execution_caller)):
    if not skill.startswith('tsTriage'):
        raise HTTPException(404)
    return await submit(skill, body, caller)


@router.get('/executions/{execution_id}')
async def result(execution_id: str, caller=Depends(execution_caller)):
    return await poll(execution_id, caller)


@router.get('/executions/{execution_id}/impact')
async def impact(execution_id: str, evidenceThreshold: str = '0.80', caller=Depends(execution_caller)):
    response = await poll(execution_id, caller)
    if response.status_code != 200: return response
    execution = simplejson.loads(response.body, use_decimal=True)
    if execution.get('skillName') not in SUPPORTED_SKILLS: raise HTTPException(404)
    try:
        threshold = float(evidenceThreshold)
        if not number(threshold, 0, 1): raise ValueError()
    except ValueError:
        raise HTTPException(400, 'Invalid evidenceThreshold')
    if execution.get('status') == 'COMPLETED':
        try: answers = json.loads(execution.get('result'))
        except (ValueError, TypeError): answers = None
        execution['impactDecision'] = decide(answers, threshold)
    return ExecutionResponse(execution)
