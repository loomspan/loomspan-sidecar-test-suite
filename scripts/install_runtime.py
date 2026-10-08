"""Initialize a supplied on-prem runtime distribution without developer checkouts."""
import argparse
import hashlib
import json
import sys
import zipfile
import configure_isolated
import environment
import prepare


def verify_inputs(root):
    manifest = json.loads((root / 'runtime-artifacts/manifest.json').read_bytes())
    build = manifest['buildReference']
    for name, wanted in manifest['sourceSha256'].items():
        file = (root / name).resolve()
        if not file.is_relative_to(root.resolve()) or hashlib.sha256(file.read_bytes()).hexdigest() != wanted:
            raise ValueError('Runtime source/configuration input mismatch: ' + name)
    for name, wanted in build['configurationSha256'].items():
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != wanted:
            raise ValueError('Approved configuration mismatch: ' + name)
    for name in ['java', 'sidecar']:
        file = root / 'runtime-artifacts' / (name + '.jar')
        if hashlib.sha256(file.read_bytes()).hexdigest() != build['artifacts'][name]['sha256']:
            raise ValueError('Supplied package identity mismatch: ' + name)
        with zipfile.ZipFile(file) as archive:
            framework = archive.read('BOOT-INF/lib/loomspan-spring-boot-starter-1.0.0-beta.8.jar')
        if hashlib.sha256(framework).hexdigest() != build['installedFrameworkSha256']:
            raise ValueError('Embedded Framework identity mismatch: ' + name)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', default='equipment-onprem')
    parser.add_argument('--port-offset', type=int, default=10000)
    args = parser.parse_args()
    root = environment.ROOT
    if (root / '.runtime').exists():
        raise ValueError('Runtime already exists; this installer never replaces credentials or databases')
    manifest = verify_inputs(root)
    original = sys.argv
    try:
        sys.argv = ['configure_isolated', '--project', args.project, '--port-offset', str(args.port_offset)]
        configure_isolated.main()
    finally:
        sys.argv = original
    file = root / '.runtime/environment.json'
    settings = json.loads(file.read_bytes())
    settings['runtimeMode'] = 'supplied-artifacts'
    file.write_text(json.dumps(settings, indent=2))
    prepare.prepare_runtime()
    for name in ['java', 'python', 'fixture']:
        (root / '.runtime' / name).mkdir()
    build = dict(manifest['buildReference'], installationMode='verified supplied runtime artifacts; not rebuilt locally',
                 runtimeSourceCommit=manifest['suiteCommit'],
                 runtimeIdentity=environment.runtime_identity())
    (root / '.runtime/build-baseline.json').write_text(json.dumps(build, indent=2))
    print('Verified supplied packages/configuration and initialized fresh offline runtime. No services started.')


if __name__ == '__main__':
    main()
