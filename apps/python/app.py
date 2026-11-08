"""Host composition; business behavior belongs to named suites."""
from contextlib import asynccontextmanager
import os
from pathlib import Path
from fastapi import APIRouter, FastAPI, Depends
from jwt import PyJWKClient
from loomspan_sdk.fastapi import CallbackMiddleware

from .infrastructure.sidecar_client import (
    configure, execution_caller, submit, read_execution, ExecutionResponse, execution_view,
)
from .suites.equipment_service import api, skill_routes, business, workflow
from .suites.typesafe_ai.api import router as typesafe_router

# Runtime skill names are global; register suite completion handlers explicitly.
COMPLETION_HANDLERS = {'resolveEquipment': workflow.complete}

def create_app():
    loomspan = configure()
    public_export = Path(os.environ['EXECUTION_JWKS'])

    @asynccontextmanager
    async def lifespan(application):
        connection = business.db()
        try:
            connection.commit()
        finally:
            connection.close()
        async with loomspan.lifespan(application):
            # The public-only mount is shared with Sidecar's separate container user.
            public_export.chmod(0o644)
            yield

    app = FastAPI(lifespan=lifespan)
    app.state.loomspan = loomspan
    app.state.keycloak_jwks = PyJWKClient(os.environ['JWKS'])
    app.include_router(router)
    app.include_router(typesafe_router)
    app.include_router(api.router)
    app.include_router(skill_routes.router)
    app.include_router(api.router, prefix='/suites/equipment-service')
    app.add_middleware(CallbackMiddleware, loomspan=loomspan)
    return app


router = APIRouter()


@router.get('/health')
def health():
    return {'status': 'up'}

@router.post('/v1/skills/{skill}/executions')
async def execute(skill: str, body: dict, caller=Depends(execution_caller)):
    return await submit(skill, body, caller)

@router.get('/v1/executions/{execution_id}')
async def poll(execution_id: str, caller=Depends(execution_caller)):
    execution = await read_execution(execution_id, caller)
    if isinstance(execution, ExecutionResponse):
        return execution
    handler = COMPLETION_HANDLERS.get(execution.skill_name)
    outcome = handler(execution_id, execution, caller[0]) if handler else {}
    return ExecutionResponse(execution_view(execution) | outcome)
