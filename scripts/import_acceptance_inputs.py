"""Import only immutable retained evidence from a verified preparation bundle."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bundle', type=Path)
    args = parser.parse_args()
    bundle = args.bundle.resolve()
    hashes = json.loads((bundle / 'checksums.json').read_bytes())
    for name in ['workspace-inputs.zip', 'input-inventory.json']:
        if sha(bundle / name) != hashes[name]:
            raise ValueError('Transport checksum mismatch: ' + name)
    inventory = json.loads((bundle / 'input-inventory.json').read_bytes())
    imported = {}
    with zipfile.ZipFile(bundle / 'workspace-inputs.zip') as archive:
        for name, info in inventory['files'].items():
            if info['kind'] != 'retained-evidence-input':
                continue
            dest = (ROOT / name).resolve()
            if not dest.is_relative_to(ROOT / 'evidence'):
                raise ValueError('Evidence path outside target')
            raw = archive.read(name)
            if hashlib.sha256(raw).hexdigest() != info['sha256']:
                raise ValueError('Evidence checksum mismatch: ' + name)
            if dest.exists():
                if sha(dest) != info['sha256']:
                    raise ValueError('Refusing to replace existing evidence: ' + name)
            else:
                dest.parent.mkdir(parents=True, exist_ok=True)
                with dest.open('xb') as stream:
                    stream.write(raw)
            imported[name] = info['sha256']
    record = {'classification': 'retained-evidence-input; not a fresh runtime result',
              'transportSha256': hashes['workspace-inputs.zip'], 'files': imported}
    output = ROOT / '.runtime/retained-inputs.json'
    if output.exists():
        raise ValueError('Input registration already exists; imported evidence retained')
    with output.open('x', encoding='utf-8') as stream:
        json.dump(record, stream, indent=2)
    print('Verified and imported ' + str(len(imported)) + ' retained evidence files; no source or runtime state imported.')


if __name__ == '__main__':
    main()
