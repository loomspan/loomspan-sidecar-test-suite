"""Execution credentials preserve authenticated identity and enforce callback trust."""
import json
from pathlib import Path
import sys
import time

import jwt
import pytest
from fastapi import HTTPException

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from prepare import prepare_execution_keys
from apps.python.infrastructure import execution_identity as execution


@pytest.fixture
def keys(tmp_path, monkeypatch):
    prepare_execution_keys(tmp_path)
    monkeypatch.setenv('EXECUTION_KEY', str(tmp_path/'execution-key.pem'))
    monkeypatch.setenv('EXECUTION_JWKS', str(tmp_path/'execution-jwks.json'))
    return tmp_path


def test_issued_identity_roles_expiry_and_exact_callback_credential(keys):
    now = int(time.time())
    claims = {'sub': 'maya', 'exp': now+30, 'roles': ['ASSESS_EQUIPMENT', 'admin', 'ROLE_ASSESS_EQUIPMENT']}
    credential = execution.credential((claims, 'Bearer external-login'))
    verified, original = execution.callback_identity(credential)
    assert original == credential
    assert now <= verified.pop('iat') <= int(time.time())
    assert verified == {'iss': 'equipment-app', 'sub': 'maya', 'aud': 'equipment-service',
        'exp': now+30, 'token_use': 'loomspan_execution', 'roles': ['ASSESS_EQUIPMENT']}
    assert jwt.get_unverified_header(credential.split()[1]) == {
        'alg': 'RS256', 'typ': 'loomspan-execution+jwt', 'kid': 'equipment-app'}
    public = json.loads((keys/'execution-jwks.json').read_bytes())['keys'][0]
    assert not set(public) & {'d', 'p', 'q', 'dp', 'dq', 'qi'}
    before = {p.name: p.read_bytes() for p in keys.iterdir()}
    prepare_execution_keys(keys)
    assert before == {p.name: p.read_bytes() for p in keys.iterdir()}


@pytest.mark.parametrize('change,header', [
    ({'aud': 'other'}, {}), ({'iss': 'other'}, {}), ({'exp': 1}, {}),
    ({'token_use': 'login'}, {}), ({}, {'typ': 'JWT'}), ({}, {'kid': 'unknown'}),
    ({'roles': 'REQUEST_SERVICE'}, {}),
])
def test_callback_rejects_wrong_purpose_trust_time_and_identity(keys, change, header):
    claims = {'iss': execution.ISSUER, 'sub': 'luis', 'aud': execution.AUDIENCE,
        'iat': int(time.time()), 'exp': int(time.time())+60,
        'token_use': 'loomspan_execution', 'roles': ['REQUEST_SERVICE']} | change
    token = jwt.encode(claims, (keys/'execution-key.pem').read_bytes(), algorithm='RS256',
        headers={'typ': execution.TYPE, 'kid': 'equipment-app'} | header)
    with pytest.raises(HTTPException) as error:
        execution.callback_identity('Bearer '+token)
    assert error.value.status_code == 401


def test_current_trust_withdrawal_and_source_expiry_fail_closed(keys):
    credential = execution.credential(({'sub': 'maya', 'exp': int(time.time())+60, 'roles': []}, ''))
    (keys/'execution-jwks.json').write_text('{"keys": []}')
    with pytest.raises(HTTPException):
        execution.callback_identity(credential)
    with pytest.raises(HTTPException):
        execution.credential(({'sub': 'maya', 'exp': 1, 'roles': ['REQUEST_SERVICE']}, ''))
    (keys/'execution-jwks.json').unlink()
    with pytest.raises(HTTPException):
        execution.callback_identity(credential)


def test_lifetime_is_bounded_and_private_key_only_mounts_into_python(keys):
    now = int(time.time())
    token = execution.credential(({'sub': 'luis', 'exp': now+3600,
        'roles': ['REQUEST_SERVICE']}, ''))
    verified, _ = execution.callback_identity(token)
    assert verified['exp'] - verified['iat'] == 600
    import yaml
    compose = yaml.safe_load((ROOT/'compose.yaml').read_bytes())
    assert any('execution-key.pem' in mount for mount in compose['services']['python']['volumes'])
    assert not any('execution-key.pem' in mount for mount in compose['services']['sidecar']['volumes'])


@pytest.mark.parametrize('trust', [[], {'keys': None}, {'keys': ['invalid']}, {'keys': [{'kid': 'equipment-app'}]}])
def test_malformed_callback_trust_is_rejected(keys, trust):
    token = execution.credential(({'sub': 'maya', 'exp': int(time.time())+60, 'roles': []}, ''))
    (keys/'execution-jwks.json').write_text(json.dumps(trust))
    with pytest.raises(HTTPException) as error:
        execution.callback_identity(token)
    assert error.value.status_code == 401
