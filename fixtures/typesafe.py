"""Strict System One replay and explicitly permitted, single-send live forwarding."""
import asyncio
import json
import os
import re
import uuid
import httpx
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse, Response


def reserve_live(data, case_id, path, body):
    """Durable one-use permits survive service restarts and failed HTTP calls."""
    run = os.getenv('TYPESAFE_LIVE_RUN', '')
    if not re.fullmatch('[a-f0-9]{32}', run) or not os.getenv('LOOMSPAN_TYPESAFE_API_KEY'):
        raise HTTPException(403, 'native live access disabled')
    file = data / ('typesafe-live-' + run + '.json')
    plan = json.loads(file.read_bytes())
    permits = plan['permits']
    permit = permits.get(case_id)
    if (plan['runId'] != run or not 0 < len(permits) <= 12 or not permit
            or permit['used'] or permit['path'] != path or permit['request'] != body
            or body.get('model') != 'jev-1.13.0'):
        raise HTTPException(409, 'native live permit mismatch or exhausted')
    permit['used'] = True
    temporary = file.with_suffix('.tmp')
    with temporary.open('w', encoding='utf-8') as stream:
        json.dump(plan, stream)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, file)


async def forward_live(harness, case_id, path, body, request_id):
    async with harness.lock:
        reserve_live(harness.DATA, case_id, path, body)
    harness.journal('native-live-attempt', caseId=case_id, requestId=request_id, path=path)
    try:
        async with httpx.AsyncClient(timeout=45, trust_env=False, follow_redirects=False) as client:
            response = await client.post('https://api.typesafe.ai/v1/systemone', json=body,
                headers={'Authorization': 'Bearer ' + os.environ['LOOMSPAN_TYPESAFE_API_KEY']})
        try:
            envelope = response.json()
        except ValueError:
            envelope = None
        harness.journal('native-response', caseId=case_id, requestId=request_id,
            status=response.status_code, response=envelope, rawBody=response.text,
            provenance='live TypeSafe', stage=0)
        return Response(response.content, status_code=response.status_code, media_type='application/json')
    except httpx.HTTPError as error:
        harness.journal('native-transport-failure', caseId=case_id, requestId=request_id,
                        errorType=type(error).__name__)
        raise HTTPException(502, 'native provider transport failure; permit consumed') from None


def install(app):
    @app.post('/typesafe/{path}/v1/systemone')
    @app.post('/typesafe/{path}/api/v1/systemone')
    async def evaluate(path: str, request: Request):
        from fixtures import server as harness
        body = await request.json()
        serialized = json.dumps(body)
        matches = [key for key, case in harness.cases.items()
                   if case.get('suite') == 'typesafe-ai' and key in serialized]
        if len(matches) != 1:
            raise HTTPException(409, 'missing or ambiguous TypeSafe case')
        case_id = matches[0]
        case = harness.cases[case_id]
        if case.get('path') != path or case.get('mode') not in ('replay', 'live'):
            raise HTTPException(409, 'TypeSafe requires matching offline registration')
        request_id = uuid.uuid4().hex
        harness.journal('native-request', path=path, caseId=case_id, requestId=request_id,
                        request=body, endpoint=request.url.path)
        if case.get('mode') == 'live':
            if (body != case.get('nativeRequest') or request.url.path != '/typesafe/' + path + '/v1/systemone'
                    or request.headers.get('authorization') != 'Bearer fixture-typesafe-transport'):
                raise HTTPException(409, 'native live request mismatch')
            return await forward_live(harness, case_id, path, body, request_id)
        async with harness.lock:
            index = case.get('nativeUsed', 0)
            responses = case.get('nativeResponses', [])
            expected_path = '/typesafe/' + path + case.get('nativePrefix', '') + '/v1/systemone'
            if (body != case.get('nativeRequest') or index >= len(responses)
                    or request.url.path != expected_path
                    or request.headers.get('authorization') != 'Bearer fixture-typesafe-transport'):
                harness.journal('native-rejected', caseId=case_id, requestId=request_id)
                raise HTTPException(409, 'unexpected native request, route, authorization or exhausted fixture')
            case['nativeUsed'] = index + 1
            response = responses[index]
        if response.get('delaySeconds'):
            await asyncio.sleep(response['delaySeconds'])
        harness.journal('native-response', caseId=case_id, requestId=request_id,
                        status=response.get('status', 200), response=response.get('body'),
                        rawBody=response.get('raw'), stage=index,
                        provenance=case.get('nativeProvenance', 'authored-typesafe-protocol-fixture'))
        if 'raw' in response:
            return Response(response['raw'], status_code=response.get('status', 200), media_type='application/json')
        return JSONResponse(response.get('body'), status_code=response.get('status', 200))
