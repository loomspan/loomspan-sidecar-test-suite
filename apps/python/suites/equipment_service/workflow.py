from fastapi import HTTPException
from loomspan_sdk import ExecutionSnapshot
from ...infrastructure.sidecar_client import ExecutionResponse, execution_view, read_execution
from . import business


async def poll(execution_id, caller):
    execution = await read_execution(execution_id, caller)
    if isinstance(execution, ExecutionResponse):
        return execution
    outcome = complete(execution_id, execution, caller[0])
    return ExecutionResponse(execution_view(execution) | outcome)


def complete(execution_id, execution: ExecutionSnapshot, who) -> dict:
    """Return application outcomes separately from the immutable SDK snapshot."""
    if execution.status == 'COMPLETED' and execution.skill_name == 'resolveEquipment':
        try:
            return {'assessmentVersion': business.save_assessment(execution_id, execution.result, who)}
        except (HTTPException, ValueError, KeyError, TypeError):
            return {
                'status': 'FAILED',
                'failure': {'kind': 'ASSESSMENT_VALIDATION',
                            'message': 'Missing or altered authoritative evidence'},
                'frameworkStatus': execution.status,
            }
    return {}
