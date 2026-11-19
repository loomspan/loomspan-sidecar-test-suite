"""Project the SDK's typed outcomes onto the app's public execution API."""
import os
from pathlib import Path
from uuid import UUID

from fastapi import Depends, Request
from fastapi.responses import JSONResponse
from loomspan_sdk import (
    AcceptanceUnknown, AuthenticatedIdentity, HttpFailure, IssuanceSettings,
    LocalFailure, ProtocolFailure, ProvidedSigning, ExecutionSnapshot,
)
from loomspan_sdk.fastapi import Loomspan
import simplejson

from .security import identity

ISSUER = 'equipment-app'
AUDIENCE = 'equipment-service'


def configure():
    try:
        seconds = int(os.environ.get('EXECUTION_LIFETIME_SECONDS', '900'))
        if seconds <= 0:
            raise ValueError()
    except ValueError:
        raise ValueError('EXECUTION_LIFETIME_SECONDS must be a positive integer') from None
    return Loomspan(
        os.environ['SIDECAR'],
        ProvidedSigning(Path(os.environ['EXECUTION_KEY']), Path(os.environ['EXECUTION_JWKS'])),
        IssuanceSettings(
            issuer=ISSUER, lifetime_ns=seconds * 1_000_000_000,
            additional_audiences=(AUDIENCE,), roles=('ASSESS_EQUIPMENT', 'REQUEST_SERVICE'),
        ),
        callback_prefix='/skills', callback_audience=AUDIENCE,
        connect_timeout=30, response_timeout=30,
    )


async def execution_caller(request: Request, claims=Depends(identity)):
    loomspan = request.app.state.loomspan
    return claims, await loomspan.client(request), await loomspan.issuer(request)


async def callback_claims(request: Request):
    principal = await request.app.state.loomspan.principal(request)
    return {'iss': principal.issuer, 'sub': principal.subject, 'roles': principal.authorities}


class ExecutionResponse(JSONResponse):
    def render(self, content):
        return simplejson.dumps(content, ensure_ascii=False, use_decimal=True,
                                allow_nan=False, separators=(',', ':')).encode('utf-8')


def _http_failure(error):
    problem = error.problem
    return ExecutionResponse(
        problem if problem is not None else {'detail': 'Sidecar rejected the request'},
        status_code=error.status_code,
    )


async def submit(skill, body, caller):
    claims, client, issuer = caller
    try:
        credential = issuer.issue(AuthenticatedIdentity(claims['sub'], claims['roles']))
        accepted = await client.submit(skill, body, credential)
    except LocalFailure:
        return ExecutionResponse({'detail': 'Invalid execution request'}, status_code=400)
    except HttpFailure as error:
        return _http_failure(error)
    except AcceptanceUnknown:
        return ExecutionResponse(
            {'kind': 'ACCEPTANCE_UNKNOWN', 'detail': 'Sidecar submission acceptance is unknown'},
            status_code=502,
        )
    return ExecutionResponse({'id': str(accepted.id)}, status_code=202)


async def read_execution(execution_id, caller) -> ExecutionSnapshot | ExecutionResponse:
    """Return typed state, or an HTTP error for the calling endpoint to return."""
    claims, client, issuer = caller
    try:
        identifier = UUID(execution_id)
        if str(identifier) != execution_id.lower():
            raise ValueError()
        credential = issuer.issue(AuthenticatedIdentity(claims['sub'], claims['roles']))
        execution = await client.get_execution(identifier, credential)
    except (LocalFailure, ValueError):
        return ExecutionResponse({'detail': 'Invalid execution ID'}, status_code=400)
    except HttpFailure as error:
        return _http_failure(error)
    except ProtocolFailure:
        return ExecutionResponse({'detail': 'Unusable Sidecar execution response'}, status_code=502)

    return execution


def execution_view(execution: ExecutionSnapshot) -> dict:
    """Project SDK state without changing it or serializing business inputs."""
    failure = None
    if execution.failure is not None:
        failure = {'kind': execution.failure.kind, 'message': execution.failure.message}
        if execution.failure.producing_skill_name is not None:
            failure['producingSkillName'] = execution.failure.producing_skill_name
        if execution.failure.issues:
            failure['issues'] = [
                {'path': issue.path, 'code': issue.code, 'message': issue.message}
                for issue in execution.failure.issues
            ]
    snapshot = {
        'id': str(execution.id), 'skillName': execution.skill_name, 'status': execution.status,
        'createdAt': execution.created_at, 'completedAt': execution.completed_at,
        'result': execution.result, 'failure': failure,
        'configurationSnapshotId': str(execution.configuration_snapshot_id)
        if execution.configuration_snapshot_id is not None else None,
    }
    if execution.events is not None:
        snapshot['events'] = [
            {'timestamp': event.timestamp, 'level': event.level, 'type': event.type,
             'details': event.details, 'frameId': event.frame_id, 'route': event.route}
            for event in execution.events
        ]
    return snapshot
