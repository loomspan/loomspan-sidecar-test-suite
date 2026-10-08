"""Record the pinned release build and verify that both packaged hosts embed its bytes."""
import hashlib
import argparse
import json
import pathlib
import subprocess
import zipfile
import yaml

ROOT=pathlib.Path(__file__).resolve().parents[1]
VERSION='1.0.0-beta.8'

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--maven-repository',type=pathlib.Path,default=pathlib.Path.home()/'.m2/repository')
    args=parser.parse_args()
    installed=args.maven_repository/'ai/loomspan/loomspan-spring-boot-starter'/VERSION/('loomspan-spring-boot-starter-'+VERSION+'.jar')
    digest=hashlib.sha256(installed.read_bytes()).hexdigest()
    overlay=yaml.safe_load((ROOT/'compose.runtime.yaml').read_text())
    settings=overlay['services']['java']['environment']
    request_timeout=int(settings['LOOMSPAN_CONNECTIONS_MODEL_REQUESTTIMEOUT'].removesuffix('s'))
    mission_timeout=int(settings.get('LOOMSPAN_SESSION_MISSIONTIMEOUT','600s').removesuffix('s'))
    sidecar_settings=overlay['services']['sidecar']['environment']
    assert sidecar_settings['LOOMSPAN_CONNECTIONS_MODEL_REQUESTTIMEOUT']==str(request_timeout)+'s'
    assert sidecar_settings.get('LOOMSPAN_SESSION_MISSIONTIMEOUT','600s')==str(mission_timeout)+'s'
    usage_limits = [yaml.safe_load((ROOT/'config'/(name+'.yaml')).read_text(encoding='utf-8'))
                    ['loomspan']['session'].get('quotas', {}).get('max-usage-units', 200000)
                    for name in ['java', 'sidecar']]
    assert usage_limits[0] == usage_limits[1], 'Equivalent hosts must use the same usage quota'
    result={'framework':VERSION,'frameworkCommit':subprocess.check_output(['git','-C',str(ROOT.parent/'loomspan-framework'),'rev-parse','v1.0.0-beta.8^{commit}'],text=True).strip(),
            'sidecar':'1.0.0-beta.3',
            'sidecarCommit':'3eff6befd95f73b7d4091ed0da32498e0f64c488','buildMode':'pinned release source; installed release Framework artifact',
            'providerRequestTimeoutSeconds':request_timeout,'missionTimeoutSeconds':mission_timeout,
            'sessionMaxUsageUnits':usage_limits[0],
            'installedFrameworkSha256':digest,'artifacts':{},'configurationSha256':{}}
    for name,path in [('java',ROOT/'apps/java/target/equipment-java-1.0.jar'),
                      ('sidecar',ROOT/'.build/sidecar-1.0.0-beta.3/target/loomspan-sidecar-1.0.0-beta.3.jar')]:
        with zipfile.ZipFile(path) as jar:
            embedded=jar.read('BOOT-INF/lib/loomspan-spring-boot-starter-'+VERSION+'.jar')
        if hashlib.sha256(embedded).hexdigest()!=digest: raise RuntimeError(name+' packaged a different Framework artifact')
        result['artifacts'][name]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'frameworkSha256':digest}
    for path in [ROOT/'compose.runtime.yaml',*(ROOT/'config').rglob('*.yaml')]:
        result['configurationSha256'][path.relative_to(ROOT).as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
    (ROOT/'.runtime/build-baseline.json').write_text(json.dumps(result,indent=2))
    print('Both packaged hosts match the installed Framework release; build baseline recorded.')

if __name__=='__main__':main()
