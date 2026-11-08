"""Installed FastAPI callback fixture. Its state is confined to a disposable recipe."""
import asyncio
from contextlib import asynccontextmanager
from hashlib import sha256
import os
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import Response
from loomspan_sdk import IssuanceSettings, ProvidedSigning
from loomspan_sdk.fastapi import CallbackMiddleware, Loomspan

RESULT = '  {"result":"équipement"}\n'
ISSUER = 'loomspan-app'
ROLE = 'ROLE_ORDER_EDITOR'
AUDIENCE = 'callback-receiver'

loomspan = Loomspan(
    os.environ['SIDECAR_URL'],
    ProvidedSigning(Path('/signing/signer-key.pem'), Path('/public/jwks.json')),
    IssuanceSettings(issuer=ISSUER, roles=(ROLE, 'ORDER_EDITOR'), additional_audiences=(AUDIENCE,)),
    callback_prefix='/loomspan/callbacks', callback_audience=AUDIENCE,
    overlap_jwks=Path('/trust/callback.json'),
)
observations = []
entered = asyncio.Event()
release = asyncio.Event()


@asynccontextmanager
async def lifespan(app):
    async with loomspan.lifespan(app):
        Path('/public/jwks.json').chmod(0o644)
        yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(CallbackMiddleware, loomspan=loomspan)


@app.get('/health')
async def health():
    return {'ready': True}


@app.get('/control/observations')
async def counts():
    return {'callbacks': observations, 'blockEntered': entered.is_set()}


@app.post('/control/release')
async def unblock():
    release.set()
    return {'released': True}


@app.post('/loomspan/callbacks/block')
async def block(principal=Depends(loomspan.principal)):
    if ROLE not in principal.authorities or principal.subject != 'alice':
        raise HTTPException(403)
    entered.set()
    await asyncio.wait_for(release.wait(), 20)
    return Response(RESULT, media_type='application/json')


@app.api_route('/loomspan/callbacks/owned', methods=['GET', 'POST'])
async def owned(request: Request, principal=Depends(loomspan.principal)):
    evidence = {'issuer': principal.issuer, 'subject': principal.subject, 'roles': list(principal.authorities),
                'method': request.method, 'bodyLength': len(await request.body()),
                'digest': sha256(request.headers['Authorization'].encode()).hexdigest(),
                'marker': request.headers.get('X-Reference-Marker'), 'effect': False}
    observations.append(evidence)
    if ROLE not in principal.authorities or principal.subject not in ('alice', 'java:alice'):
        raise HTTPException(403)
    evidence['effect'] = True
    return Response(RESULT, media_type='application/json')
