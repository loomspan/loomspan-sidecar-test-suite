import os
import jwt
from jwt import PyJWKClient
from fastapi import Header, HTTPException

jwks=PyJWKClient(os.environ['JWKS'])
def identity(authorization:str=Header('')):
    try:
        scheme, token=authorization.split(' ',1)
        if scheme.lower()!='bearer': raise ValueError()
        claims=jwt.decode(token,jwks.get_signing_key_from_jwt(token).key,algorithms=['RS256'],issuer=os.environ['ISSUER'],audience='equipment-service',options={'require':['exp','iat','iss','sub']})
        if not claims['sub']: raise ValueError()
        return claims,authorization
    except (ValueError,jwt.PyJWTError): raise HTTPException(401,'invalid token')
