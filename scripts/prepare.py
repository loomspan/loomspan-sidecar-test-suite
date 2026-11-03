"""Prepare local-only credentials without replacing existing secrets or keys."""
import environment as target_env
import argparse, json, pathlib, secrets
ROOT = pathlib.Path(__file__).resolve().parents[1]
def write(path, value):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(value, encoding="utf-8")
def prepare_execution_keys(runtime):
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization
    import jwt
    keyfile, jwksfile = runtime/'execution-key.pem', runtime/'execution-jwks.json'
    if keyfile.exists() != jwksfile.exists():
        raise ValueError('Incomplete execution signing material; refusing to replace keys')
    if keyfile.exists():
        return
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    keyfile.write_bytes(key.private_bytes(serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
    jwk = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(key.public_key()))
    jwk.update(kid='equipment-app', alg='RS256', use='sig')
    jwksfile.write_text(json.dumps({'keys': [jwk]}))


def prepare_runtime():
    runtime=ROOT/'.runtime'; runtime.mkdir(exist_ok=True)
    secretfile=runtime/'secrets.json'
    if not secretfile.exists():
        write('.runtime/secrets.json',json.dumps({k:secrets.token_urlsafe(36) for k in ['observer','control','keycloak_admin','maya','luis']},indent=2))
    prepare_execution_keys(runtime)
    s=json.loads(secretfile.read_text())
    # User passwords are generated development credentials, never source-controlled.
    realm={'realm':'equipment','enabled':True,'sslRequired':'none','accessTokenLifespan':1800,
      'roles':{'realm':[{'name':r} for r in ['ASSESS_EQUIPMENT','REQUEST_SERVICE']]},
      'clients':[{'clientId':'equipment-browser','publicClient':True,'standardFlowEnabled':True,
        'directAccessGrantsEnabled':False,'redirectUris':[target_env.url(18765, '/callback', 'localhost')],
        'attributes':{'pkce.code.challenge.method':'S256'},'protocol':'openid-connect',
        'protocolMappers':[
          {'name':'roles','protocol':'openid-connect','protocolMapper':'oidc-usermodel-realm-role-mapper',
           'config':{'claim.name':'roles','jsonType.label':'String','multivalued':'true','access.token.claim':'true'}},
          {'name':'audience','protocol':'openid-connect','protocolMapper':'oidc-audience-mapper',
           'config':{'included.custom.audience':'equipment-service','access.token.claim':'true'}}]}],
      'users':[{'username':u,'id':u,'enabled':True,'emailVerified':True,'firstName':u.title(),'lastName':'Demo',
                'email':u+'@northbank.example','credentials':[{'type':'password','value':s[u],'temporary':False}],
                'realmRoles':['ASSESS_EQUIPMENT']+(['REQUEST_SERVICE'] if u=='luis' else [])} for u in ['maya','luis']]}
    write('.runtime/realm.json',json.dumps(realm,indent=2))
    write('.runtime/compose.env','\n'.join(f'{k.upper()}={v}' for k,v in s.items())+'\n')
    print('Prepared ignored local credentials and realm import; credentials not printed.')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    prepare_runtime()
if __name__=='__main__': main()
