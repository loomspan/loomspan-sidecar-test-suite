import os
import jwt
from fastapi import Header, HTTPException, Request
from loomspan_sdk import AuthenticatedIdentity, LocalFailure

def identity(request: Request, authorization: str = Header('')):
    try:
        scheme, token=authorization.split(' ',1)
        if scheme.lower()!='bearer': raise ValueError()
        key = request.app.state.keycloak_jwks.get_signing_key_from_jwt(token).key
        claims = jwt.decode(token, key, algorithms=['RS256'], issuer=os.environ['ISSUER'],
                            audience='equipment-service', options={'require': ['exp', 'iat', 'iss', 'sub']})
        roles = claims.get('roles', [])
        if not isinstance(roles, list):
            raise ValueError()
        authenticated = AuthenticatedIdentity(claims['sub'], roles)
        return {'iss': claims['iss'], 'sub': authenticated.subject, 'roles': authenticated.authorities}
    except (ValueError, jwt.PyJWTError, LocalFailure):
        raise HTTPException(401, 'invalid token') from None
