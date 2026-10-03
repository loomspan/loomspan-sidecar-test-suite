"""Assemble a credential-free operator distribution from approved runtime artifacts."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    if out.exists():
        raise ValueError('Use a new output directory')
    names = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard'], cwd=ROOT, text=True).splitlines()
    names = sorted(set(n for n in names if (ROOT / n).is_file() and not n.startswith('evidence/')))
    build = json.loads((ROOT / '.runtime/build-baseline.json').read_bytes())
    source = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in names}
    jars = {'java': ROOT / 'apps/java/target/equipment-java-1.0.jar',
            'sidecar': ROOT / '.build/sidecar-1.0.0-beta.2-framework-beta.8-SNAPSHOT/target/loomspan-sidecar-1.0.0-beta.2.jar'}
    for name, path in jars.items():
        if hashlib.sha256(path.read_bytes()).hexdigest() != build['artifacts'][name]['sha256']:
            raise ValueError('Package changed: ' + name)
    known = [s.encode() for s in json.loads((ROOT / '.runtime/secrets.json').read_bytes()).values()]
    for name in names:
        if any(secret in (ROOT / name).read_bytes() for secret in known):
            raise ValueError('Credential detected; refusing runtime export')
    out.mkdir(parents=True)
    manifest = {'distributionMode': 'on-prem Compose with supplied pinned runtime packages',
                'buildReference': build, 'sourceSha256': source,
                'suiteCommit': subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                'providerAccess': 'disabled', 'credentials': 'generate at installation',
                'retainedEvidence': 'supplied separately for optional offline acceptance; not fresh results'}
    with zipfile.ZipFile(out / 'equipment-runtime.zip', 'x', zipfile.ZIP_DEFLATED) as archive:
        for name in names:
            archive.write(ROOT / name, name)
        for name, file in jars.items():
            archive.write(file, 'runtime-artifacts/' + name + '.jar')
        archive.writestr('runtime-artifacts/manifest.json', json.dumps(manifest, indent=2))
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2))
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}
    (out / 'checksums.json').write_text(json.dumps(hashes, indent=2))
    print('Created on-prem runtime distribution; no credentials or databases copied.')


if __name__ == '__main__':
    main()
