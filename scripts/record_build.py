"""Stage the current Sidecar and record runtime package/configuration identities."""
import hashlib
import argparse
import json
import pathlib
import shutil
from xml.etree import ElementTree
import zipfile
import yaml

ROOT=pathlib.Path(__file__).resolve().parents[1]
SOURCE=json.loads((ROOT/'config/runtime-source.json').read_bytes())
VERSION=SOURCE['frameworkVersion']

def framework_identity(path, version):
    prefix = 'BOOT-INF/lib/loomspan-spring-boot-starter-'
    with zipfile.ZipFile(path) as jar:
        names = [name for name in jar.namelist() if name.startswith(prefix) and name.endswith('.jar')]
        if names != [prefix + version + '.jar']:
            raise ValueError('Missing, mixed or unexpected embedded Framework coordinate')
        return hashlib.sha256(jar.read(names[0])).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sidecar-checkout',type=pathlib.Path,default=ROOT.parent/'loomspan-sidecar')
    args=parser.parse_args()
    checkout = args.sidecar_checkout.resolve()
    pom = ElementTree.parse(checkout/'pom.xml').getroot()
    ns = {'m': 'http://maven.apache.org/POM/4.0.0'}
    sidecar_version = pom.findtext('m:version', namespaces=ns)
    if pom.findtext('m:properties/m:loomspan.version', namespaces=ns) != VERSION:
        raise ValueError('Sidecar must use the installed Framework coordinate: ' + VERSION)
    built = checkout/'target'/('loomspan-sidecar-'+sidecar_version+'.jar')
    framework_identity(built, VERSION)
    staged = ROOT/'runtime-artifacts/sidecar.jar'
    staged.parent.mkdir(exist_ok=True)
    shutil.copyfile(built, staged)
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
    result={'framework':VERSION, 'sidecar':sidecar_version,
            'buildMode':SOURCE['note'],
            'providerRequestTimeoutSeconds':request_timeout,'missionTimeoutSeconds':mission_timeout,
            'sessionMaxUsageUnits':usage_limits[0], 'artifacts':{},'configurationSha256':{}}
    for name,path in [('java',ROOT/'apps/java/target/equipment-java-1.0.jar'), ('sidecar',staged)]:
        result['artifacts'][name]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'frameworkSha256':framework_identity(path, VERSION)}
    for path in [ROOT/'compose.runtime.yaml',*(ROOT/'config').rglob('*.yaml')]:
        result['configurationSha256'][path.relative_to(ROOT).as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
    (ROOT/'.runtime/build-baseline.json').write_text(json.dumps(result,indent=2))
    print('Current host packages use the configured Framework coordinate; build baseline recorded.')

if __name__=='__main__':main()
