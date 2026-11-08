"""Exercise the maintained app against a local Sidecar wire peer."""
from contextlib import contextmanager
from decimal import Decimal
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import base64
import json
import os
from pathlib import Path
import socket
import sys
from threading import Thread
import time
from types import SimpleNamespace

import jwt
import pytest
import simplejson
import yaml
from fastapi.testclient import TestClient
from cryptography.hazmat.primitives import serialization

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from prepare import prepare_execution_keys


@contextmanager
def wire_peer(responses):
    requests = []

    class Handler(BaseHTTPRequestHandler):
        def exchange(self):
            body = self.rfile.read(int(self.headers.get('Content-Length', '0')))
            requests.append((self.command, self.path, self.headers['Authorization'], body))
            status, response = next(responses)
            if status is None:
                self.connection.shutdown(socket.SHUT_RDWR)
                return
            self.send_response(status)
            self.send_header('Content-Type', 'application/problem+json' if status >= 400 else 'application/json')
            self.send_header('Content-Length', str(len(response)))
            self.end_headers()
            self.wfile.write(response)

        do_POST = do_GET = exchange

        def log_message(self, *_):
            pass

    with ThreadingHTTPServer(('127.0.0.1', 0), Handler) as server:
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            yield f'http://127.0.0.1:{server.server_port}', requests
        finally:
            server.shutdown()
            thread.join()


EXECUTION_ID = '6a0c950c-d172-4151-b629-6a5c15c7ae37'
ACCEPTED = (202, json.dumps({'id': EXECUTION_ID}).encode())


def test_existing_pem_sdk_export_and_independent_execution_lifetime(tmp_path, monkeypatch):
    prepare_execution_keys(tmp_path)
    key = tmp_path / 'execution-key.pem'
    original = key.read_bytes()
    numbers = serialization.load_pem_private_key(original, None).public_key()
    legacy_key = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(numbers)) | {'kid': 'equipment-app'}
    legacy = tmp_path / 'execution-jwks.json'
    legacy.write_text(json.dumps({'keys': [legacy_key]}), encoding='utf-8')
    legacy_bytes = legacy.read_bytes()
    trust = tmp_path / 'execution-trust' / 'jwks.json'
    trust.parent.mkdir(exist_ok=True)
    monkeypatch.setenv('EXECUTION_KEY', str(key))
    monkeypatch.setenv('EXECUTION_JWKS', str(trust))
    monkeypatch.setenv('JWKS', 'http://127.0.0.1:1/keycloak')
    monkeypatch.setenv('ISSUER', 'https://login.example.test')
    monkeypatch.delenv('EXECUTION_LIFETIME_SECONDS', raising=False)

    with wire_peer(iter([ACCEPTED])) as (url, requests):
        monkeypatch.setenv('SIDECAR', url)
        from apps.python.app import create_app
        from apps.python.infrastructure.security import identity
        from apps.python.suites.equipment_service import business

        app = create_app()
        monkeypatch.setattr(business, 'DB', tmp_path / 'equipment.db')
        now = int(time.time())
        claims = {'iss': 'https://login.example.test', 'sub': 'maya', 'exp': now + 30,
                  'roles': ['ASSESS_EQUIPMENT', 'admin', 'ROLE_ASSESS_EQUIPMENT']}
        app.dependency_overrides[identity] = lambda: claims
        try:
            with TestClient(app) as client:
                response = client.post('/v1/skills/example/executions', json={'test': True})
                assert response.status_code == 202
                assert response.json() == {'id': EXECUTION_ID}
                assert trust.is_file(), 'Startup did not publish the SDK execution trust export'
        finally:
            app.dependency_overrides.clear()

    [request] = requests
    token = request[2].removeprefix('Bearer ')
    [public] = json.loads(trust.read_bytes())['keys']
    header = jwt.get_unverified_header(token)
    assert header == {'alg': 'RS256', 'typ': 'loomspan-execution+jwt', 'kid': public['kid']}
    assert header['kid'] != 'equipment-app'
    jwt.decode(token, jwt.PyJWK.from_dict(public).key, algorithms=['RS256'],
               issuer='equipment-app', audience='equipment-service')
    assert jwt.PyJWK.from_dict(public).key.public_numbers() == numbers.public_numbers()
    payload = token.split('.')[1]
    verified = json.loads(base64.urlsafe_b64decode(payload + '=' * (-len(payload) % 4)), parse_float=Decimal)
    assert verified['exp'] - verified['iat'] == Decimal(900)
    assert verified['sub'] == 'maya' and verified['roles'] == ['ASSESS_EQUIPMENT']
    assert verified['token_use'] == 'loomspan_execution'
    assert key.read_bytes() == original and legacy.read_bytes() == legacy_bytes


@pytest.fixture
def deployed(tmp_path, monkeypatch):
    from apps.python.app import create_app
    from apps.python.suites.equipment_service import business

    prepare_execution_keys(tmp_path)
    key = tmp_path / 'execution-key.pem'
    trust = tmp_path / 'execution-trust' / 'jwks.json'
    monkeypatch.setenv('EXECUTION_KEY', str(key))
    monkeypatch.setenv('EXECUTION_JWKS', str(trust))
    monkeypatch.setenv('JWKS', 'http://127.0.0.1:1/keycloak')
    monkeypatch.setenv('ISSUER', 'https://login.example.test')
    monkeypatch.setenv('EXECUTION_LIFETIME_SECONDS', '45')
    monkeypatch.setattr(business, 'DB', tmp_path / 'equipment.db')
    public = serialization.load_pem_private_key(key.read_bytes(), None).public_key()

    def start(url):
        monkeypatch.setenv('SIDECAR', url)
        app = create_app()
        monkeypatch.setattr(app.state.keycloak_jwks, 'get_signing_key_from_jwt',
                            lambda token: SimpleNamespace(key=public))
        return app

    def login(subject, roles):
        now = int(time.time())
        token = jwt.encode({'iss': 'https://login.example.test', 'sub': subject, 'aud': 'equipment-service',
                            'iat': now, 'exp': now + 30, 'roles': roles}, key.read_bytes(), algorithm='RS256')
        return {'Authorization': f'Bearer {token}'}

    return start, login, key, trust


def test_sdk_execution_boundary(deployed, monkeypatch):
    from apps.python.suites.equipment_service import business

    start, login, key, trust = deployed
    effects = []

    async def leaf(name, body, claims):
        business.scoped(claims, body['assetId'])
        effects.append((name, body, claims))
        return {'accepted': True}

    monkeypatch.setattr(business, 'leaf', leaf)
    submit = '/v1/skills/example/executions'
    callback = '/skills/assetContext'
    body = {'assetId': 'NB-P240-017', 'caseId': 'local-case'}
    maya = login('maya', ['ASSESS_EQUIPMENT', 'ROLE_ASSESS_EQUIPMENT', 'admin'])
    luis = login('luis', ['REQUEST_SERVICE'])
    with wire_peer(iter([ACCEPTED, ACCEPTED])) as (url, requests), TestClient(start(url)) as client:
        assert client.post(submit, json={}).status_code == 401
        for roles in ('ASSESS_EQUIPMENT', ['  '], [4]):
            assert client.post(submit, json={}, headers=login('maya', roles)).status_code == 401
        for headers in (maya, luis):
            assert client.post(submit, json={}, headers=headers).status_code == 202
        assert len(requests) == 2
        maya_exec, luis_exec = [{'Authorization': request[2]} for request in requests]
        assert len({maya['Authorization'], luis['Authorization'], requests[0][2], requests[1][2]}) == 4
        [public] = json.loads(trust.read_bytes())['keys']
        for request, subject, roles in zip(requests, ['maya', 'luis'], [['ASSESS_EQUIPMENT'], ['REQUEST_SERVICE']]):
            token = request[2].removeprefix('Bearer ')
            verified = jwt.decode(token, jwt.PyJWK.from_dict(public).key, algorithms=['RS256'],
                                  issuer='equipment-app', audience='equipment-service')
            payload = token.split('.')[1]
            exact = json.loads(base64.urlsafe_b64decode(payload + '=' * (-len(payload) % 4)), parse_float=Decimal)
            assert exact['exp'] - exact['iat'] == Decimal(45)
            assert verified['sub'] == subject and verified['roles'] == roles
            assert verified['aud'] == ['loomspan-sidecar', 'equipment-app', 'equipment-service']
            assert jwt.get_unverified_header(token)['kid'] == public['kid']
        for route in ('/skills', '/skills/unknown', callback):
            assert client.post(route, json=body).status_code == 401
        assert client.post(callback, json=body, headers=maya).status_code == 401
        assert client.post(callback, json=body, headers=luis_exec).status_code == 403
        assert client.post(callback, json=body | {'assetId': 'other'}, headers=maya_exec).status_code == 403
        assert client.post('/skills/unknown', json=body, headers=maya_exec).status_code == 404
        assert client.post('/suites/equipment-service' + callback, json=body, headers=maya_exec).status_code == 404
        now = int(time.time())
        claims = {'iss': 'equipment-app', 'sub': 'maya', 'aud': ['equipment-service'],
                  'iat': now - 180, 'exp': now + 10, 'token_use': 'loomspan_execution',
                  'roles': ['ASSESS_EQUIPMENT']}
        for changed, kid in (({'exp': now - 90}, public['kid']),
                             ({'token_use': 'login'}, public['kid']), ({}, 'wrong-key')):
            invalid = jwt.encode(claims | changed, key.read_bytes(), algorithm='RS256',
                                 headers={'typ': 'loomspan-execution+jwt', 'kid': kid})
            status = client.post(callback, json=body, headers={'Authorization': f'Bearer {invalid}'}).status_code
            assert status == 401
        assert client.post(callback, json=body, headers=maya_exec).json() == {'accepted': True}
    assert effects == [('assetContext', body, {'iss': 'equipment-app', 'sub': 'maya',
                                              'roles': ('ASSESS_EQUIPMENT',)})]


@pytest.mark.parametrize('value', ['0', '-1', 'garbage', '1.5'])
def test_invalid_lifetime_fails_before_export(deployed, monkeypatch, value):
    start, _, key, trust = deployed
    original = key.read_bytes()
    monkeypatch.setenv('EXECUTION_LIFETIME_SECONDS', value)
    with pytest.raises(ValueError):
        start('http://127.0.0.1:1')
    assert key.read_bytes() == original and not trust.exists()


def test_invalid_pem_fails_without_replacement(deployed):
    from loomspan_sdk import LocalFailure
    start, _, key, trust = deployed
    key.write_bytes(b'invalid synthetic PEM')
    with pytest.raises(LocalFailure):
        with TestClient(start('http://127.0.0.1:1')):
            pytest.fail('Invalid signer started')
    assert key.read_bytes() == b'invalid synthetic PEM' and not trust.exists()


@pytest.mark.parametrize('existing', ['execution-jwks.json', 'secrets.json', 'python', 'execution-trust'])
def test_partial_workspace_never_creates_a_signer(tmp_path, existing):
    (tmp_path / existing).touch()
    with pytest.raises(ValueError, match='existing workspace'):
        prepare_execution_keys(tmp_path)
    assert not (tmp_path / 'execution-key.pem').exists()


def test_trust_mount_keeps_key_and_existing_data_separate(tmp_path):
    for name in ['environment.json', 'compose.isolated.yaml']:
        (tmp_path / name).touch()
    prepare_execution_keys(tmp_path)
    files = {'execution-key.pem': (tmp_path / 'execution-key.pem').read_bytes(),
             'execution-jwks.json': b'old-public-file', 'equipment.db': b'existing-data'}
    for name in ('execution-jwks.json', 'equipment.db'):
        (tmp_path / name).write_bytes(files[name])
    prepare_execution_keys(tmp_path)
    assert all((tmp_path / name).read_bytes() == data for name, data in files.items())
    compose = yaml.safe_load((Path(__file__).resolve().parents[1] / 'compose.yaml').read_bytes())
    python = compose['services']['python']['volumes']
    sidecar = compose['services']['sidecar']['volumes']
    assert './.runtime/execution-key.pem:/execution/key.pem:ro' in python
    assert './.runtime/execution-trust:/trust' in python
    assert './.runtime/execution-trust:/trust:ro' in sidecar
    assert all('execution-key' not in mount and 'execution-jwks' not in mount for mount in sidecar)


@pytest.mark.skipif(os.name != 'posix', reason='POSIX directory modes')
def test_public_trust_directory_remains_readable_with_restrictive_umask(tmp_path):
    original = os.umask(0o077)
    try:
        prepare_execution_keys(tmp_path)
    finally:
        os.umask(original)
    assert (tmp_path / 'execution-key.pem').stat().st_mode & 0o777 == 0o600
    assert (tmp_path / 'execution-trust').stat().st_mode & 0o777 == 0o755


def test_public_execution_projection(deployed):
    start, login, _, _ = deployed
    headers = login('maya', ['ASSESS_EQUIPMENT'])
    poll = '/v1/executions/' + EXECUTION_ID
    submit = '/v1/skills/example/executions'
    timestamp = '2026-11-07T10:00:00.123456789Z'
    base = {'id': EXECUTION_ID, 'skillName': 'example', 'status': 'RUNNING', 'createdAt': timestamp,
            'completedAt': None, 'result': None, 'failure': None, 'configurationSnapshotId': None}
    success = base | {'status': 'COMPLETED', 'result': '  résultat équipement\n', 'completedAt': timestamp, 'events': []}
    issue = {'path': '/caseId', 'code': 'required', 'message': 'missing'}
    failed = base | {'status': 'FAILED', 'completedAt': timestamp, 'failure': {
        'kind': 'SKILL_FAILURE', 'message': 'exercise rejected', 'issues': [issue],
    }, 'events': [{'timestamp': timestamp, 'level': 'WARN', 'type': 'reference',
                   'details': {'nested': [Decimal('1.23456789123456789e350'), {'n': None}]},
                   'frameId': None, 'route': 'default'}]}
    problems = [(400, {'type': 'about:blank', 'title': 'Bad Request', 'status': 400,
                       'detail': 'Invalid skill input', 'instance': submit, 'issues': [issue]}),
                (403, {'type': 'about:blank', 'title': 'Forbidden', 'status': 403, 'detail': 'Access Denied'}),
                (404, {'type': 'about:blank', 'title': 'Not Found', 'status': 404, 'detail': 'Execution not found'})]
    def encoded(value):
        return simplejson.dumps(value, use_decimal=True).encode()
    responses = [(200, encoded(item)) for item in (base, success, failed)]
    responses += [(status, encoded(problem)) for status, problem in problems]
    responses += [(503, b''), (200, b'{"invalid":true}'), (202, b'{"id":"invalid"}'), (None, b'')]
    with wire_peer(iter(responses)) as (url, requests), TestClient(start(url)) as client:
        for index, expected in enumerate((base, success, failed), 1):
            response = client.get(poll, headers=headers)
            assert response.status_code == 200
            assert simplejson.loads(response.content, use_decimal=True) == expected
            assert len(requests) == index
        for status, expected in problems:
            response = (client.get(poll, headers=headers) if status == 404
                        else client.post(submit, json={}, headers=headers))
            assert response.status_code == status and response.json() == expected
        response = client.get(poll, headers=headers)
        assert response.status_code == 503 and response.json() == {'detail': 'Sidecar rejected the request'}
        assert client.get('/v1/executions/invalid', headers=headers).status_code == 400
        assert len(requests) == 7
        assert client.get(poll, headers=headers).status_code == 502
        for count in (9, 10):
            response = client.post(submit, json={}, headers=headers)
            assert response.status_code == 502 and response.json()['kind'] == 'ACCEPTANCE_UNKNOWN'
            assert len(requests) == count
