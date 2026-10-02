"""Prepare isolated release sources and local-only credentials; never print secrets."""
import json, os, pathlib, secrets, subprocess, tarfile
ROOT = pathlib.Path(__file__).resolve().parents[1]
def write(path, value):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(value, encoding="utf-8")
def main():
    for name, version, expected in [
        ('sidecar','1.0.0-beta.2','da3bb8f8ae6087955f9b3a6bd02b9706d3b582e7'),
        ('framework','1.0.0-beta.7','0778065ef5bafc9c8ea979093e5e0e48d7e1e687')]:
        repo=ROOT.parent / ('loomspan-'+name)
        sha=subprocess.check_output(['git','-C',str(repo),'rev-parse',f'v{version}^{{commit}}'],text=True).strip()
        if sha != expected: raise RuntimeError(f'{name} tag mismatch: {sha}')
        dest=ROOT/'.build'/(name+'-'+version)
        if not dest.exists():
            archive=ROOT/'.build'/f'{name}-{version}.tar'; archive.parent.mkdir(exist_ok=True)
            subprocess.run(['git','-C',str(repo),'archive','--format=tar',f'--output={archive}',f'v{version}'],check=True)
            dest.mkdir()
            with tarfile.open(archive) as t: t.extractall(dest,filter='data')
    runtime=ROOT/'.runtime'; runtime.mkdir(exist_ok=True)
    secretfile=runtime/'secrets.json'
    if not secretfile.exists():
        write('.runtime/secrets.json',json.dumps({k:secrets.token_urlsafe(36) for k in ['observer','control','keycloak_admin','maya','luis']},indent=2))
    s=json.loads(secretfile.read_text())
    # User passwords are generated development credentials, never source-controlled.
    realm={'realm':'equipment','enabled':True,'sslRequired':'none','accessTokenLifespan':1800,
      'roles':{'realm':[{'name':r} for r in ['ASSESS_EQUIPMENT','REQUEST_SERVICE']]},
      'clients':[{'clientId':'equipment-browser','publicClient':True,'standardFlowEnabled':True,
        'directAccessGrantsEnabled':False,'redirectUris':['http://localhost:18765/callback'],
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
    print('Prepared pinned release sources and ignored local credentials.')
if __name__=='__main__': main()
