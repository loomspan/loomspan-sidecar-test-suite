"""Export explicit clean-VM inputs without changing the retained stack or evidence.

The output is a new directory, never a deployment target. Retained evidence is
copied byte-for-byte; credentials and runtime databases are prohibited.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = 'acceptance-offline-20261002-204252-34a71c'


def sha(file):
    with file.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args]).decode('utf-8').strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    if out.exists():
        raise ValueError('Use a new output directory; previous evidence is immutable')
    out.mkdir(parents=True)
    source = [ROOT / p for p in git(ROOT, 'ls-files', '--cached', '--others', '--exclude-standard').splitlines()]
    source = sorted(set(p for p in source if p.is_file() and p.parts[len(ROOT.parts)] != 'evidence'))
    directories = {p.name: p for p in (ROOT / 'evidence').iterdir() if p.is_dir() and p != out}
    selected = {CHECKPOINT, 'review-fresh-live-20261002', 'business-output-offline-20261002'}
    # Include explicit test inputs, including dynamically constructed rejected-review paths.
    for name in ['live-20261002-000544', 'live-20261002-100123',
                 'full-correction-live-20261002-125841', 'full-correction-live-20261002-130627']:
        selected.update([name, 'review-' + name])
    pattern = re.compile(r'[A-Za-z0-9_.-]+')

    def references(files):
        result = set()
        for file in files:
            if file.suffix in {'.json', '.py', '.md'} and file.name not in {'journal.json'}:
                result.update(set(pattern.findall(file.read_text(encoding='utf-8', errors='replace'))) & directories.keys())
        return result

    selected.update(references(p for p in source if p.parts[len(ROOT.parts)] in {'scripts', 'tests', 'fixtures'}))
    scanned = set()
    while selected - scanned:
        pending = selected - scanned
        scanned.update(pending)
        selected.update(references(p for n in pending for p in directories[n].rglob('*') if p.is_file()))
    print('Selected ' + str(len(selected)) + ' retained evidence directories.', flush=True)
    evidence = sorted(p for n in selected for p in directories[n].rglob('*') if p.is_file())
    # Exact known credentials are checked in memory; neither values nor their hashes are recorded.
    sensitive = list(json.loads((ROOT / '.runtime/secrets.json').read_bytes()).values())
    sensitive += [v for k, v in os.environ.items() if ('API_KEY' in k or 'TOKEN' in k) and len(v) > 15]
    sensitive = [v.encode() for v in sensitive if len(v) > 15]
    inputs = {}
    for p in [*source, *evidence]:
        if p.name in {'secrets.json', 'compose.env', 'realm.json', '.env'} or p.suffix in {'.db', '.sqlite', '.token'}:
            raise ValueError('Prohibited runtime input: ' + p.relative_to(ROOT).as_posix())
        raw = p.read_bytes()
        if any(value in raw for value in sensitive):
            raise ValueError('Known credential present; refusing export: ' + p.relative_to(ROOT).as_posix())
        inputs[p.relative_to(ROOT).as_posix()] = {
            'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw),
            'kind': 'retained-evidence-input' if p in evidence else 'suite-source-input'}
    build = json.loads((ROOT / '.runtime/build-baseline.json').read_bytes())
    repos = {}
    for name, repo, refs in [
        ('suite', ROOT, ['HEAD']),
        ('framework', ROOT.parent / 'loomspan-framework', ['HEAD', 'v1.0.0-beta.7']),
        ('sidecar', ROOT.parent / 'loomspan-sidecar', ['HEAD', 'v1.0.0-beta.2'])]:
        revision = git(repo, 'rev-parse', 'HEAD')
        status = git(repo, 'status', '--porcelain')
        if name != 'suite' and (status or revision != build[name + 'Commit']):
            raise ValueError(name + ' source differs from recorded baseline')
        subprocess.run(['git', '-C', str(repo), 'bundle', 'create', str(out / (name + '.bundle')), *refs], check=True)
        repos[name] = {'commit': revision, 'worktreeStatus': status.splitlines(), 'refs': refs}
    with zipfile.ZipFile(out / 'workspace-inputs.zip', 'x', zipfile.ZIP_DEFLATED) as archive:
        for name, info in inputs.items():
            file = ROOT / name
            if sha(file) != info['sha256']:
                raise ValueError('Input changed during export: ' + name)
            archive.write(file, name)
        # Comparison reference only. The VM must generate its own active baseline.
        archive.writestr('clean-input-reference/build-baseline.json', json.dumps(build, indent=2))
    manifest = {'status': 'PREPARED_NOT_VM_VERIFIED', 'cleanSetupVerified': False,
                'newPaidCalls': 0, 'repositories': repos, 'evidenceDirectories': sorted(selected),
                'files': inputs, 'buildReference': build,
                'exclusions': ['runtime credentials/tokens/databases', 'Maven cache/settings',
                               'Python environment', 'Docker volumes', 'active runtime'],
                'externalInputs': ['Windows VM with Docker nested virtualization and sufficient disk',
                                   'Java 21, Maven 3.9+, Python 3.13, Git, Docker Desktop',
                                   'network access to Maven/PyPI/Playwright/container and apt registries'],
                'scope': 'Source and retained evidence inputs only; no fresh VM results or rebuilt packages.'}
    (out / 'input-inventory.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    checksums = {p.name: sha(p) for p in out.iterdir() if p.is_file()}
    (out / 'checksums.json').write_text(json.dumps(checksums, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'output': str(out), 'files': len(inputs), 'evidenceDirectories': len(selected),
                      'uncompressedBytes': sum(v['bytes'] for v in inputs.values()),
                      'cleanSetupVerified': False}))


if __name__ == '__main__':
    main()
