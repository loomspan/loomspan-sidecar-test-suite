"""Prepare isolated release sources and local-only credentials; never print secrets."""
import environment as target_env
import argparse, json, os, pathlib, secrets, subprocess, tarfile
ROOT = pathlib.Path(__file__).resolve().parents[1]
def write(path, value):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(value, encoding="utf-8")
def export_sources():
    # Export only the Sidecar source used by the current snapshot overlay.
    import io
    repo = ROOT.parent / 'loomspan-sidecar'
    ref = 'v1.0.0-beta.2'
    expected = 'da3bb8f8ae6087955f9b3a6bd02b9706d3b582e7'
    sha = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', ref + '^{commit}'], text=True).strip()
    if sha != expected:
        raise RuntimeError('Sidecar source tag mismatch')
    dest = ROOT / '.build/sidecar-1.0.0-beta.2-framework-beta.8-SNAPSHOT'
    if dest.exists():
        return
    raw = subprocess.check_output(['git', '-C', str(repo), 'archive', '--format=tar', ref])
    dest.mkdir(parents=True)
    with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
        archive.extractall(dest, filter='data')

def prepare_runtime():
    runtime=ROOT/'.runtime'; runtime.mkdir(exist_ok=True)
    secretfile=runtime/'secrets.json'
    if not secretfile.exists():
        write('.runtime/secrets.json',json.dumps({k:secrets.token_urlsafe(36) for k in ['observer','control','keycloak_admin','maya','luis']},indent=2))
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
    parser.add_argument('--runtime-only',action='store_true',help='Generate local runtime credentials without Git, Maven or neighboring checkouts')
    args=parser.parse_args()
    if not args.runtime_only: export_sources()
    prepare_runtime()
if __name__=='__main__': main()
