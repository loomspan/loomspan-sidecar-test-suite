"""Host composition; business behavior belongs to named suites."""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from .infrastructure.security import identity
from .infrastructure.sidecar_client import submit, poll as poll_execution
from .suites.equipment_service import api, skill_routes, business, workflow
from .suites.typesafe_ai.api import router as typesafe_router

# Runtime skill names are global; register suite completion handlers explicitly.
COMPLETION_HANDLERS = {'resolveEquipment': workflow.complete}

@asynccontextmanager
async def lifespan(application):
    connection = business.db()
    try:
        connection.commit()
    finally:
        connection.close()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(typesafe_router)
app.include_router(api.router)
app.include_router(skill_routes.router)
app.include_router(api.router, prefix='/suites/equipment-service')
app.include_router(skill_routes.router, prefix='/suites/equipment-service')

@app.get('/health')
def health():
    return {'status': 'up'}

@app.post('/v1/skills/{skill}/executions')
async def execute(skill: str, body: dict, who=Depends(identity)):
    return await submit(skill, body, who)

@app.get('/v1/executions/{execution_id}')
async def poll(execution_id: str, who=Depends(identity)):
    import json
    response = await poll_execution(execution_id, who)
    handler = COMPLETION_HANDLERS.get(json.loads(response.body).get('skillName'))
    return handler(execution_id, response, who) if handler else response
