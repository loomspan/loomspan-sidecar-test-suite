"""Run bounded assertions inside the disposable installed reference network."""
import base64
from contextlib import contextmanager
from decimal import Decimal
from hashlib import sha256
from http.server import BaseHTTPRequestHandler, HTTPServer
from importlib.metadata import version
import json
import os
from pathlib import Path
import platform
import socket
import ssl
import sys
from tempfile import TemporaryDirectory
from threading import Thread
import time
import traceback

import httpx
import jwt
import simplejson
from loomspan_sdk import (
    AcceptanceUnknown, AuthenticatedIdentity, CredentialSnapshot, ExecutionStatus,
    ExecutionTokenIssuer, HttpFailure, IssuanceSettings, ProtocolFailure, ProvidedSigning, SidecarClient, WaitOptions,
)

CALLBACK = '/loomspan/callbacks/owned'
ROLE = 'ROLE_ORDER_EDITOR'
LITERAL = 'ORDER_EDITOR'
AUDIENCE = 'callback-receiver'
ISSUER = 'loomspan-app'
RESULT = '  {"result":"équipement"}\n'
TLS = Path('/tls')


def context(ca='group', peer=None):
    result = ssl.create_default_context(cafile=str(TLS / f'{ca}-ca.pem'))
    if peer:
        result.load_cert_chain(TLS / f'{peer}.pem', TLS / f'{peer}-key.pem')
    return result


def until(action, predicate, timeout=50):
    deadline = time.monotonic() + timeout
    while True:
        value = action()
        if predicate(value):
            return value
        if time.monotonic() >= deadline:
            raise TimeoutError('Reference observation did not converge')
        time.sleep(0.1)


def assert_http(action, expected):
    try:
        action()
    except HttpFailure as failure:
        assert failure.status_code == expected
    else:
        raise AssertionError('Expected Sidecar rejection')


def catalog_status(client, credential):
    try:
        return 200 if client.list_skills(credential) else 204
    except HttpFailure as error:
        return error.status_code


@contextmanager
def capture_credential():
    headers = []

    class Capture(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def do_GET(self):
            headers.append(self.headers['Authorization'])
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', '2')
            self.end_headers()
            self.wfile.write(b'[]')

    with HTTPServer(('127.0.0.1', 0), Capture) as server:
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            yield f'http://127.0.0.1:{server.server_port}', headers
        finally:
            server.shutdown()
            thread.join()


def snapshot_header(credential):
    with capture_credential() as (url, headers):
        with SidecarClient(url) as capture:
            assert capture.list_skills(credential) == ()
    [header] = headers
    return header


def terminal(client, ident, credential):
    snapshot = client.wait_for_completion(ident, credential, WaitOptions(timeout=18, poll_interval=0.1))
    assert snapshot.events is not None
    assert all(event.timestamp and event.level and event.type for event in snapshot.events)
    return snapshot


def verify_wire(snapshot, tls, authorization):
    with httpx.Client(base_url=os.environ['SIDECAR_URL'], verify=tls or True,
                      timeout=3, trust_env=False) as direct:
        response = direct.get(f'/v1/executions/{snapshot.id}', headers={'Authorization': authorization})
    assert response.status_code == 200
    wire = simplejson.loads(response.content, use_decimal=True)
    assert wire['result'] == snapshot.result and wire['status'] == snapshot.status
    assert wire['createdAt'] == snapshot.created_at and wire['completedAt'] == snapshot.completed_at
    failure = None
    if snapshot.failure is not None:
        failure = {'kind': snapshot.failure.kind, 'message': snapshot.failure.message}
        if snapshot.failure.issues:
            failure['issues'] = [
                {'path': issue.path, 'code': issue.code, 'message': issue.message}
                for issue in snapshot.failure.issues
            ]
    assert wire['failure'] == failure
    assert wire['events'] == [
        {'timestamp': event.timestamp, 'level': event.level, 'type': event.type,
         'details': event.details, 'frameId': event.frame_id, 'route': event.route}
        for event in snapshot.events
    ]


def atomic_write(path, value):
    if value is None:
        path.unlink()
        return
    candidate = path.with_suffix('.next')
    candidate.write_bytes(value)
    candidate.replace(path)


def local_checks(client, control, issuer, credential):
    bob = issuer.issue(AuthenticatedIdentity('bob', [ROLE]))
    literal = issuer.issue(AuthenticatedIdentity('alice', [LITERAL]))
    own = client.submit('referenceGet', {}, credential).id
    assert_http(lambda: client.get_execution(own, bob), 404)
    assert_http(lambda: client.submit('referenceGet', {}, literal), 403)
    for name, denied in [('referenceGet', bob), ('referenceLiteral', literal)]:
        denied_result = terminal(client, client.submit(name, {}, denied).id, denied)
        assert denied_result.status == ExecutionStatus.FAILED
        assert '403' in denied_result.failure.message

    before = len(control.get('/control/observations').json()['callbacks'])
    blocked = client.submit('referenceBlock', {}, credential).id
    try:
        until(lambda: control.get('/control/observations').json()['blockEntered'], bool)
        with TemporaryDirectory() as temp:
            short_issuer = ExecutionTokenIssuer(ProvidedSigning(
                Path('/signing/signer-key.pem'), Path(temp) / 'jwks.json'), IssuanceSettings(
                issuer=ISSUER, roles=[ROLE], additional_audiences=[AUDIENCE], lifetime_ns=2_000_000_000,
            ))
            short = short_issuer.issue(AuthenticatedIdentity('alice', [ROLE]))
            queued = client.submit('referencePost', {}, short).id
            assert client.get_execution(queued, credential).status == ExecutionStatus.QUEUED
            header = snapshot_header(short)
            payload = header.split('.')[1]
            expiry = json.loads(base64.urlsafe_b64decode(payload + '=' * (-len(payload) % 4)),
                                parse_float=Decimal)['exp']
            until(lambda: time.time_ns(), lambda now: Decimal(now) / Decimal(10**9) >= expiry, timeout=5)
    finally:
        assert control.post('/control/release').status_code == 200
    assert terminal(client, blocked, credential).status == ExecutionStatus.COMPLETED
    expired = terminal(client, queued, credential)
    assert expired.status == ExecutionStatus.FAILED
    assert (expired.failure.kind, expired.failure.message) == (
        'ACCESS_DENIED', 'execution credential expired before start')
    assert len(control.get('/control/observations').json()['callbacks']) == before

    java_token = Path('/java/regular.jwt').read_text().strip()
    java = CredentialSnapshot(java_token)
    java_header = {'Authorization': 'Bearer ' + java_token}
    assert control.get(CALLBACK, headers=java_header).text == RESULT
    observed = control.get('/control/observations').json()['callbacks'][-1]
    assert observed == {'issuer': ISSUER, 'subject': 'java:alice', 'roles': [ROLE, LITERAL],
                        'method': 'GET', 'bodyLength': 0, 'digest': sha256(java_header['Authorization'].encode()).hexdigest(),
                        'marker': None, 'effect': True}
    assert catalog_status(client, java) == 200
    app_trust, sidecar_trust = Path('/trust/callback.json'), Path('/trust/sidecar.json')
    app_original, sidecar_original = app_trust.read_bytes(), sidecar_trust.read_bytes()
    app_export = Path('/public/jwks.json').read_bytes()
    try:
        for unusable in (None, b'{invalid'):
            atomic_write(app_trust, unusable)
            until(lambda: control.get(CALLBACK, headers=java_header).status_code, lambda status: status == 401)
            assert catalog_status(client, java) == 200
            assert control.get(CALLBACK, headers={'Authorization': snapshot_header(credential)}).status_code == 401
            atomic_write(app_trust, app_original)
            until(lambda: control.get(CALLBACK, headers=java_header).status_code, lambda status: status == 200)

            atomic_write(sidecar_trust, unusable)
            until(lambda: catalog_status(client, java), lambda status: status == 401)
            assert control.get(CALLBACK, headers=java_header).status_code == 200
            atomic_write(sidecar_trust, sidecar_original)
            until(lambda: catalog_status(client, java), lambda status: status == 200)
        atomic_write(sidecar_trust, app_export)
        until(lambda: catalog_status(client, java), lambda status: status == 401)
        assert catalog_status(client, credential) == 200
        assert control.get(CALLBACK, headers=java_header).status_code == 200
        atomic_write(app_trust, app_export)
        until(lambda: control.get(CALLBACK, headers=java_header).status_code, lambda status: status == 401)
        assert control.get(CALLBACK, headers={'Authorization': snapshot_header(credential)}).status_code == 200
    finally:
        atomic_write(sidecar_trust, sidecar_original)
        atomic_write(app_trust, app_original)
    until(lambda: catalog_status(client, java), lambda status: status == 200)
    until(lambda: control.get(CALLBACK, headers=java_header).status_code, lambda status: status == 200)
    assert Path('/public/jwks.json').read_bytes() == app_export
    return {'rolesAndOwner': True, 'queuedExpiry': {'callbackArrivals': 0, 'failedBeforeStart': True},
            'javaCredential': True, 'trustReload': {'bothReceiversIndependent': True, 'missing': True,
                                                    'malformed': True, 'withdrawnAndRestored': True}}


def rejected_transport(url, credential, tls):
    with SidecarClient(url, ssl_context=tls, connect_timeout=2, response_timeout=3) as client:
        try:
            client.list_skills(credential)
        except ProtocolFailure:
            pass
        else:
            raise AssertionError('TLS rejection did not occur')
        try:
            client.submit('referencePost', {}, credential)
        except AcceptanceUnknown:
            return
        raise AssertionError('Rejected transport reported admission')


def standard_checks(client, control, credential, header):
    before = len(control.get('/control/observations').json()['callbacks'])
    rejected_transport('https://sidecar:8443', credential, context('other'))
    rejected_transport('https://sidecar-wrong:8443', credential, context())
    for name in ('referenceWrongHost', 'referenceWrongCa'):
        failed = terminal(client, client.submit(name, {}, credential).id, credential)
        assert failed.status == ExecutionStatus.FAILED and failed.failure
        assert (failed.failure.kind, failed.failure.message) == ('SKILL_FAILURE', 'HTTP transport failed')
        assert failed.events
        verify_wire(failed, context(), header)
    with httpx.Client(verify=context('other'), timeout=3, trust_env=False) as bad_ca:
        assert bad_ca.get('https://app:9444/counts').json() == {'attempts': 0, 'forwards': 0, 'accepted': 0}
    assert len(control.get('/control/observations').json()['callbacks']) == before

    with SidecarClient('https://sidecar:9443', ssl_context=context(), response_timeout=3) as fault:
        try:
            fault.submit('referencePost', {}, credential)
        except AcceptanceUnknown:
            pass
        else:
            raise AssertionError('Lost acceptance was not reported')
    until(lambda: len(control.get('/control/observations').json()['callbacks']), lambda count: count == before + 1)
    lost = terminal(client, client.submit('referenceLoss', {}, credential).id, credential)
    assert lost.status == ExecutionStatus.FAILED and lost.failure
    assert (lost.failure.kind, lost.failure.message) == ('SKILL_FAILURE', 'HTTP transport failed')
    assert lost.events
    verify_wire(lost, context(), header)
    # Wait longer than the configured single response deadline to detect delayed replay.
    time.sleep(3.2)
    expected = {'attempts': 1, 'forwards': 1, 'accepted': 1}
    with httpx.Client(verify=context(), timeout=3, trust_env=False) as secure:
        assert secure.get('https://sidecar:9443/counts').json() == expected
        assert secure.get('https://app:9443/counts').json() == expected
    observations = control.get('/control/observations').json()['callbacks']
    assert len(observations) == before + 2 and all(row['effect'] for row in observations[-2:])
    assert all(row['bodyLength'] == 0 and row['digest'] == sha256(header.encode()).hexdigest()
               for row in observations[-2:])
    return {'invocationTls': True, 'callbackTls': True,
            'submissionLoss': expected | {'effects': 1, 'acceptanceUnknown': True},
            'callbackLoss': expected | {'effects': 1, 'terminalFailure': True}}


def hardened_checks(client, control, credential, header):
    before = len(control.get('/control/observations').json()['callbacks'])
    rejected_transport('https://sidecar-proxy:8443', credential, context(peer='app-wrong-ca-client'))
    rejected_transport('https://sidecar-proxy:8443', credential, context('other', 'app-client'))
    with httpx.Client(base_url='https://app-proxy:8444', verify=context(), timeout=3, trust_env=False) as ingress:
        assert ingress.get('/health').status_code == 200
        assert ingress.get('/control/observations').status_code == 404
        assert ingress.get(CALLBACK, headers={'Authorization': header}).status_code == 404
    for name in ('referenceWrongClient', 'referenceWrongCa'):
        failure = terminal(client, client.submit(name, {}, credential).id, credential)
        assert failure.status == ExecutionStatus.FAILED and failure.events
        assert failure.failure.kind == 'SKILL_FAILURE' and failure.failure.message == 'HTTP 502'
        verify_wire(failure, None, header)
    assert len(control.get('/control/observations').json()['callbacks']) == before
    return {'invocationMtls': True, 'callbackMtls': True, 'privateBackend': True}


def outsider():
    for host, ports in [('app-proxy', (8081, 9080)), ('sidecar-proxy', (8080, 9080, 9083, 9084))]:
        for port in ports:
            try:
                connection = socket.create_connection((host, port), timeout=2)
            except OSError:
                continue
            connection.close()
            raise AssertionError('A private backend was reachable')


def exercise(recipe):
    verify = context() if recipe == 'standard' else None
    control_url = 'https://app:8443' if recipe == 'standard' else 'http://127.0.0.1:8081'
    readiness_url = 'https://sidecar:8443' if recipe == 'standard' else (
        'https://sidecar-proxy:8443' if recipe == 'hardened' else os.environ['SIDECAR_URL'])

    def ready():
        try:
            with httpx.Client(verify=context(peer='app-client') if recipe == 'hardened' else verify or True,
                              timeout=2, trust_env=False) as ready_client:
                return ready_client.get(readiness_url + '/actuator/health/readiness').status_code == 200
        except httpx.TransportError:
            return False

    until(ready, bool, timeout=110)
    with TemporaryDirectory() as temp, httpx.Client(base_url=control_url, verify=verify or True,
                                                    timeout=3, trust_env=False) as control:
        until(lambda: control.get('/health').status_code, lambda status: status == 200)
        issuer = ExecutionTokenIssuer(ProvidedSigning(
            Path('/signing/signer-key.pem'), Path(temp) / 'jwks.json'), IssuanceSettings(
            issuer=ISSUER, roles=[ROLE, LITERAL], additional_audiences=[AUDIENCE],
        ))
        credential = issuer.issue(AuthenticatedIdentity('alice', [ROLE, 'ignored']))
        header = snapshot_header(credential)
        token = header.removeprefix('Bearer ')
        [public] = json.loads(Path('/public/jwks.json').read_bytes())['keys']
        assert jwt.get_unverified_header(token) == {'alg': 'RS256', 'typ': 'loomspan-execution+jwt', 'kid': public['kid']}
        decoded = jwt.decode(token, jwt.PyJWK.from_dict(public).key, algorithms=['RS256'],
                             audience='loomspan-sidecar', issuer=ISSUER)
        assert decoded['roles'] == [ROLE] and decoded['sub'] == 'alice'
        assert decoded['token_use'] == 'loomspan_execution' and decoded['aud'] == ['loomspan-sidecar', ISSUER, AUDIENCE]
        with SidecarClient(os.environ['SIDECAR_URL'], ssl_context=verify, response_timeout=5) as client:
            assert_http(lambda: client.list_skills(CredentialSnapshot('invalid')), 401)
            for name, method in [('referenceGet', 'GET'), ('referencePost', 'POST')]:
                done = terminal(client, client.submit(name, {}, credential).id, credential)
                assert done.status == ExecutionStatus.COMPLETED and done.failure is None and done.events
                assert done.result == RESULT
                verify_wire(done, verify, header)
                [evidence] = control.get('/control/observations').json()['callbacks'][-1:]
                assert evidence == {'issuer': ISSUER, 'subject': 'alice', 'roles': [ROLE],
                                    'method': method, 'bodyLength': 0,
                                    'digest': sha256(header.encode()).hexdigest(),
                                    'marker': 'installed-python', 'effect': True}
            checked = {'positive': {'signatureAndDerivedKid': True, 'bodylessMethods': ['GET', 'POST'],
                                    'exactResult': True, 'retainedDiagnostics': True, 'credentialDigestMatches': True}}
            cases = {'local': lambda: local_checks(client, control, issuer, credential),
                     'standard': lambda: standard_checks(client, control, credential, header),
                     'hardened': lambda: hardened_checks(client, control, credential, header)}
            checked.update(cases[recipe]())
    return {'checks': checked, 'runtime': {'python': platform.python_version(), 'machine': platform.machine(),
                                          'system': platform.system(), 'sdk': version('loomspan-sdk')}}


if __name__ == '__main__':
    if sys.argv[1] == 'outsider':
        outsider()
    else:
        try:
            print(json.dumps(exercise(sys.argv[1])))
        except Exception as failure:
            location = traceback.extract_tb(failure.__traceback__)[-1]
            print(json.dumps({'probeFailure': {'type': type(failure).__name__, 'file': Path(location.filename).name,
                                               'line': location.lineno}}))
