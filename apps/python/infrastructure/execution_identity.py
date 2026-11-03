"""App-owned execution credentials derived from authenticated public requests."""
import json
import os
from pathlib import Path
import time

import jwt
from fastapi import Header, HTTPException

ISSUER = 'equipment-app'
AUDIENCE = 'equipment-service'
ROLES = frozenset({'ASSESS_EQUIPMENT', 'REQUEST_SERVICE'})
TYPE = 'loomspan-execution+jwt'


def credential(who):
    # who is supplied exclusively by the public route's verified identity dependency.
    claims = who[0]
    now = int(time.time())
    expiry = min(int(claims['exp']), now + 600)
    if expiry <= now or not claims['sub']:
        raise HTTPException(401, 'expired identity')
    roles = claims.get('roles', [])
    if not isinstance(roles, list) or any(not isinstance(role, str) for role in roles):
        raise HTTPException(401, 'invalid roles')
    token = jwt.encode({'iss': ISSUER, 'sub': claims['sub'], 'aud': AUDIENCE,
        'iat': now, 'exp': expiry, 'token_use': 'loomspan_execution',
        'roles': [role for role in roles if role in ROLES]},
        Path(os.environ['EXECUTION_KEY']).read_bytes(), algorithm='RS256',
        headers={'typ': TYPE, 'kid': 'equipment-app'})
    return 'Bearer ' + token


def callback_identity(authorization: str = Header('')):
    try:
        scheme, token = authorization.split(' ', 1)
        header = jwt.get_unverified_header(token)
        if scheme.lower() != 'bearer' or header.get('typ') != TYPE:
            raise ValueError()
        # Read current trust on every callback; never retain withdrawn keys.
        trust = json.loads(Path(os.environ['EXECUTION_JWKS']).read_bytes())
        if not isinstance(trust, dict) or not isinstance(trust.get('keys'), list):
            raise ValueError()
        keys = trust['keys']
        if any(not isinstance(key, dict) for key in keys):
            raise ValueError()
        matches = [key for key in keys if key.get('kid') == header.get('kid')]
        if len(matches) != 1:
            raise ValueError()
        claims = jwt.decode(token, jwt.PyJWK.from_dict(matches[0]).key,
            algorithms=['RS256'], issuer=ISSUER, audience=AUDIENCE,
            options={'require': ['exp', 'iat', 'iss', 'sub', 'token_use', 'roles']})
        if (not claims['sub'] or claims['token_use'] != 'loomspan_execution'
                or not isinstance(claims['roles'], list)
                or any(not isinstance(role, str) for role in claims['roles'])):
            raise ValueError()
        return claims, authorization
    except (OSError, KeyError, TypeError, ValueError, jwt.PyJWTError):
        raise HTTPException(401, 'invalid execution token') from None
