"""Record the local snapshot and verify that both packaged hosts embed its bytes."""
import hashlib
import json
import pathlib
import subprocess
import zipfile
import yaml

ROOT=pathlib.Path(__file__).resolve().parents[1]
VERSION='1.0.0-beta.8-SNAPSHOT'

def main():
    installed=pathlib.Path.home()/'.m2/repository/ai/loomspan/loomspan-spring-boot-starter'/VERSION/('loomspan-spring-boot-starter-'+VERSION+'.jar')
    digest=hashlib.sha256(installed.read_bytes()).hexdigest()
    overlay=yaml.safe_load((ROOT/'compose.snapshot.yaml').read_text())
    settings=overlay['services']['java']['environment']
    request_timeout=int(settings['LOOMSPAN_CONNECTIONS_MODEL_REQUESTTIMEOUT'].removesuffix('s'))
    mission_timeout=int(settings.get('LOOMSPAN_SESSION_MISSIONTIMEOUT','600s').removesuffix('s'))
    sidecar_settings=overlay['services']['sidecar']['environment']
    assert sidecar_settings['LOOMSPAN_CONNECTIONS_MODEL_REQUESTTIMEOUT']==str(request_timeout)+'s'
    assert sidecar_settings.get('LOOMSPAN_SESSION_MISSIONTIMEOUT','600s')==str(mission_timeout)+'s'
    result={'framework':VERSION,'frameworkCommit':subprocess.check_output(['git','-C',str(ROOT.parent/'loomspan-framework'),'rev-parse','HEAD'],text=True).strip(),
            'sidecar':'1.0.0-beta.2 source with local Framework snapshot',
            'sidecarCommit':'da3bb8f8ae6087955f9b3a6bd02b9706d3b582e7','buildMode':'local snapshot; not published Sidecar binary',
            'providerRequestTimeoutSeconds':request_timeout,'missionTimeoutSeconds':mission_timeout,
            'installedFrameworkSha256':digest,'artifacts':{},'configurationSha256':{}}
    for name,path in [('java',ROOT/'apps/java/target/equipment-java-1.0.jar'),
                      ('sidecar',ROOT/'.build/sidecar-1.0.0-beta.2-framework-beta.8-SNAPSHOT/target/loomspan-sidecar-1.0.0-beta.2.jar')]:
        with zipfile.ZipFile(path) as jar:
            embedded=jar.read('BOOT-INF/lib/loomspan-spring-boot-starter-'+VERSION+'.jar')
        if hashlib.sha256(embedded).hexdigest()!=digest: raise RuntimeError(name+' packaged a different Framework artifact')
        result['artifacts'][name]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'frameworkSha256':digest}
    for path in [ROOT/'compose.snapshot.yaml',*(ROOT/'config').rglob('*.yaml')]:
        result['configurationSha256'][path.relative_to(ROOT).as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
    (ROOT/'.runtime/build-baseline.json').write_text(json.dumps(result,indent=2))
    print('Both packaged hosts match the installed Framework snapshot; build baseline recorded.')

if __name__=='__main__':main()
