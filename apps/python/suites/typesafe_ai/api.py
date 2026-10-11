from fastapi import APIRouter, Depends, HTTPException
import json
from .policy import decide, number, SUPPORTED_SKILLS
from ...infrastructure.security import identity
from ...infrastructure.sidecar_client import submit, poll

router = APIRouter(prefix='/suites/typesafe-ai')


@router.post('/evaluations/{skill}', status_code=202)
async def evaluate(skill: str, body: dict, who=Depends(identity)):
    if not skill.startswith('tsTriage'):
        raise HTTPException(404)
    return await submit(skill, body, who)


@router.get('/executions/{execution_id}')
async def result(execution_id: str, who=Depends(identity)):
    return await poll(execution_id, who)


@router.get('/executions/{execution_id}/impact')
async def impact(execution_id: str, evidenceThreshold: str = '0.80', who=Depends(identity)):
    response = await poll(execution_id, who)
    if response.status_code != 200: return response
    execution = json.loads(response.body)
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
    return execution
