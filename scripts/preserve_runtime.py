"""Archive actual active traces and existing runtime evidence before host recreation."""
import environment as target_env
import hashlib
import argparse
import json
import pathlib
import shutil
import time
import httpx
from finalize_evidence import finalize

ROOT = pathlib.Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--no-package-copy', action='store_true', help='YAML-only deployment; identify unchanged package by hash instead of duplicating it')
    args = parser.parse_args()
    out = ROOT / 'evidence' / ('pre-business-diagnostic-' + time.strftime('%Y%m%d-%H%M%S'))
    out.mkdir()
    secrets = json.loads((ROOT / '.runtime/secrets.json').read_text())
    index = []
    with httpx.Client(timeout=60, trust_env=False) as client:
        for path, port in [('java', target_env.port(18081)), ('sidecar', target_env.port(18083))]:
            base = f'http://127.0.0.1:{port}/_loomspan/observability/v1'
            headers = {'X-loomspan-Api-Key': secrets['observer']}
            response = client.get(base + '/traces', headers=headers)
            response.raise_for_status()
            page = response.json()
            if page.get('nextCursor') or page.get('nextPageToken'):
                raise RuntimeError('Trace listing paginated; preserve all pages before deployment')
            for item in page['items']:
                response = client.get(base + '/traces/' + item['traceId'] + '/artifact', headers=headers)
                response.raise_for_status()
                raw = response.content
                if any(secret.encode() in raw for secret in secrets.values()):
                    raise RuntimeError('Credential detected; refusing export')
                file = pathlib.Path(path) / 'traces' / ('loomspan-trace-' + item['traceId'] + '.ndjson')
                (out / file).parent.mkdir(parents=True, exist_ok=True)
                (out / file).write_bytes(raw)
                index.append({**item, 'path': path, 'file': file.as_posix(), 'sha256': hashlib.sha256(raw).hexdigest()})
    (out / 'trace-index.json').write_text(json.dumps(index, indent=2))
    for name in ['build-baseline.json', 'fixture/journal.ndjson']:
        source = ROOT / '.runtime' / name
        if source.exists():
            dest = out / 'previous-runtime' / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
    # Java package will be replaced; unchanged Sidecar package is only identified by hash.
    package = ROOT / 'apps/java/target/equipment-java-1.0.jar'
    if package.exists() and not args.no_package_copy:
        shutil.copy2(package, out / package.name)
    (out / 'manifest.json').write_text(json.dumps({'purpose': 'Predeployment preservation',
        'traceCount': len(index), 'paidCalls': 0,
        'packageCopySkipped': args.no_package_copy,
        'configurationCaveat': 'Mounted authored config is copied; existing hosts may have loaded the previous generation. Prior baseline hashes and trace prompts retain historical identity.'}, indent=2))
    finalize(out)
    print(out)


if __name__ == '__main__':
    main()
