"""Record artifact digests without recording environment variables or credentials."""
import hashlib, json, pathlib, subprocess, sys, zipfile
import httpx
ROOT=pathlib.Path(__file__).resolve().parents[1]
def identities(out):
    result={'artifacts':{},'images':{},'config':{}}
    for name,path in [('java',ROOT/'apps/java/target/equipment-java-1.0.jar'),('sidecar',ROOT/'.build/sidecar-1.0.0-beta.2/target/loomspan-sidecar-1.0.0-beta.2.jar')]:
        raw=path.read_bytes()
        with zipfile.ZipFile(path) as z:
            embedded=z.read('BOOT-INF/lib/loomspan-spring-boot-starter-1.0.0-beta.7.jar')
        result['artifacts'][name]={'sha256':hashlib.sha256(raw).hexdigest(),'frameworkSha256':hashlib.sha256(embedded).hexdigest(),'frameworkSha1':hashlib.sha1(embedded).hexdigest()}
    with httpx.Client(trust_env=False,timeout=30) as c:
        r=c.get('https://repo.maven.apache.org/maven2/ai/loomspan/loomspan-spring-boot-starter/1.0.0-beta.7/loomspan-spring-boot-starter-1.0.0-beta.7.jar.sha1');r.raise_for_status()
        checksum=r.text.strip();result['mavenCentralFrameworkSha1']=checksum
        assert all(a['frameworkSha1']==checksum for a in result['artifacts'].values()),'Framework artifact differs from Maven Central release'
    for name in ['equipment-acceptance-java','equipment-acceptance-python','equipment-acceptance-fixtures','equipment-acceptance-sidecar','quay.io/keycloak/keycloak:26.3.5']:
        data=json.loads(subprocess.check_output(['docker','image','inspect',name],text=True))[0]
        result['images'][name]={'id':data['Id'],'repoDigests':data['RepoDigests']}
    for path in sorted((ROOT/'config').rglob('*.yaml')):
        result['config'][path.relative_to(ROOT).as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
    pathlib.Path(out).write_text(json.dumps(result,indent=2));return result
if __name__=='__main__':identities(sys.argv[1]);print('Recorded artifact identities; both embedded framework JARs match Maven Central.')
