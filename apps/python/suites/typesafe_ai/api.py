from fastapi import APIRouter, Depends, HTTPException
import json
from .policy import decide, number, SUPPORTED_SKILLS
from ...infrastructure.sidecar_client import (
    ExecutionResponse, execution_caller, submit, read_execution, execution_view,
)

router = APIRouter(prefix='/suites/typesafe-ai')


@router.post('/evaluations/{skill}', status_code=202)
async def evaluate(skill: str, body: dict, caller=Depends(execution_caller)):
    if not skill.startswith('tsTriage'):
        raise HTTPException(404)
    return await submit(skill, body, caller)


@router.get('/executions/{execution_id}')
async def result(execution_id: str, caller=Depends(execution_caller)):
    execution = await read_execution(execution_id, caller)
    if isinstance(execution, ExecutionResponse):
        return execution
    return ExecutionResponse(execution_view(execution))


@router.get('/executions/{execution_id}/impact')
async def impact(execution_id: str, evidenceThreshold: str = '0.80', caller=Depends(execution_caller)):
    execution = await read_execution(execution_id, caller)
    if isinstance(execution, ExecutionResponse):
        return execution
    if execution.skill_name not in SUPPORTED_SKILLS: raise HTTPException(404)
    try:
        threshold = float(evidenceThreshold)
        if not number(threshold, 0, 1): raise ValueError()
    except ValueError:
        raise HTTPException(400, 'Invalid evidenceThreshold')
    outcome = {}
    if execution.status == 'COMPLETED':
        try: answers = json.loads(execution.result)
        except (ValueError, TypeError): answers = None
        if execution.skill_name != 'tsTriageEvidenceSummary':
            answers = answers.get('answers') if isinstance(answers, dict) else None
        outcome['impactDecision'] = decide(answers, threshold)
    return ExecutionResponse(execution_view(execution) | outcome)
