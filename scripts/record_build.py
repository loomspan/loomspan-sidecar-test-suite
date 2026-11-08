"""Stage the current Sidecar and record runtime package/configuration identities."""
import hashlib
import argparse
from email.parser import BytesParser
import json
import pathlib
import re
import shutil
from xml.etree import ElementTree
import zipfile
import yaml

ROOT=pathlib.Path(__file__).resolve().parents[1]
SOURCE=json.loads((ROOT/'config/runtime-source.json').read_bytes())
VERSION=SOURCE['frameworkVersion']
PYTHON_SDK_DIR = pathlib.Path('runtime-artifacts/python-sdk')


def wheel_identity(path):
    name = re.fullmatch(r'loomspan_sdk-([0-9][a-z0-9.]*)-py3-none-any\.whl', path.name)
    if not name or not path.is_file() or path.is_symlink():
        raise ValueError('Expected a regular Loomspan SDK wheel')
    version = name[1]
    prefix = f'loomspan_sdk-{version}.dist-info/'
    try:
        with zipfile.ZipFile(path) as wheel:
            if any(wheel.namelist().count(prefix + name) != 1 for name in ('WHEEL', 'METADATA', 'RECORD')):
                raise ValueError('Invalid Loomspan SDK wheel records')
            metadata = BytesParser().parsebytes(wheel.read(prefix + 'METADATA'))
            tags = BytesParser().parsebytes(wheel.read(prefix + 'WHEEL')).get_all('Tag')
    except zipfile.BadZipFile:
        raise ValueError('Invalid Loomspan SDK wheel archive') from None
    if metadata.get_all('Name') != ['loomspan-sdk'] or metadata.get_all('Version') != [version] or tags != ['py3-none-any']:
        raise ValueError('Invalid Loomspan SDK wheel metadata')
    return {'filename': path.name, 'version': version, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def _staged_sdk_directory(root):
    directory = root / PYTHON_SDK_DIR
    if (directory.parent.is_symlink() or directory.parent.is_junction()
            or directory.is_symlink() or directory.is_junction()
            or not directory.resolve().is_relative_to(root.resolve())):
        raise ValueError('Unsafe staged Loomspan SDK directory')
    return directory


def verified_wheel(root, identity):
    directory = _staged_sdk_directory(root)
    wheels = list(directory.glob('*.whl'))
    if len(wheels) != 1 or wheel_identity(wheels[0]) != identity:
        raise ValueError('Staged Loomspan SDK wheel identity mismatch')
    return wheels[0]

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
    parser.add_argument('--python-sdk-wheel', type=pathlib.Path, required=True)
    args=parser.parse_args()
    sdk = wheel_identity(args.python_sdk_wheel)
    checkout = args.sidecar_checkout.resolve()
    pom = ElementTree.parse(checkout/'pom.xml').getroot()
    ns = {'m': 'http://maven.apache.org/POM/4.0.0'}
    sidecar_version = pom.findtext('m:version', namespaces=ns)
    if pom.findtext('m:properties/m:loomspan.version', namespaces=ns) != VERSION:
        raise ValueError('Sidecar must use the installed Framework coordinate: ' + VERSION)
    built = checkout/'target'/('loomspan-sidecar-'+sidecar_version+'.jar')
    framework_identity(built, VERSION)
    staged = ROOT/'runtime-artifacts/sidecar.jar'
    directory = _staged_sdk_directory(ROOT)
    wheel = directory / sdk['filename']
    if (staged.is_symlink() or wheel.is_symlink()
            or any(path != wheel for path in directory.glob('*.whl'))):
        raise ValueError('Stage exactly one Loomspan SDK wheel in the artifact directory')
    directory.mkdir(parents=True, exist_ok=True)
    if wheel.resolve() != args.python_sdk_wheel.resolve():
        shutil.copyfile(args.python_sdk_wheel, wheel)
    verified_wheel(ROOT, sdk)
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
            'sessionMaxUsageUnits':usage_limits[0], 'artifacts':{'pythonSdk': sdk},'configurationSha256':{}}
    for name,path in [('java',ROOT/'apps/java/target/equipment-java-1.0.jar'), ('sidecar',staged)]:
        result['artifacts'][name]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'frameworkSha256':framework_identity(path, VERSION)}
    for path in [ROOT/'compose.runtime.yaml',*(ROOT/'config').rglob('*.yaml')]:
        result['configurationSha256'][path.relative_to(ROOT).as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
    (ROOT/'.runtime/build-baseline.json').write_text(json.dumps(result,indent=2))
    print('Current host packages use the configured Framework coordinate; build baseline recorded.')

if __name__=='__main__':main()
