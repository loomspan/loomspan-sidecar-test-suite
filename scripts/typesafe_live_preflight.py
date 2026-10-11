"""Verify predeclared live request shapes on both hosts without provider access."""
import json
import argparse
from pathlib import Path
import zipfile
import httpx
import run_suite as core
from suites.registry import TYPESAFE
from suites.typesafe_ai.runner import execute


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture', type=Path, help='Replay a completed live suite bundle without accepting its judgments')
    args = parser.parse_args()
    core.ready()
    core.require_offline_provider()
    secrets = json.loads((core.ROOT / '.runtime/secrets.json').read_bytes())
    cases = json.loads((core.ROOT / 'fixtures/typesafe-ai/live-cases.json').read_bytes())['cases']
    bundle = core.Bundle(list(secrets.values()))
    report = {'runId': 'typesafe-live-preflight', 'suite': TYPESAFE.name, 'mode': 'mock',
        'fixtureOrigin': 'authored-protocol-fixtures', 'status': 'FAIL', 'cases': [], 'runtimeRestored': False}
    if args.capture:
        cases = []
        with zipfile.ZipFile(args.capture / 'bundle.zip') as archive:
            hashes = json.loads(archive.read('checksums.json'))
            if any(core.digest(archive.read(n)) != h for n, h in hashes.items()):
                raise ValueError('Capture checksum mismatch')
            captured = json.loads(archive.read('report.json'))
            if captured['suite'] != TYPESAFE.name or captured['status'] != 'CHECKS_PASS_REVIEW_REQUIRED' or not captured['runtimeRestored']:
                raise ValueError('A completed restored native capture is required')
            for result in captured['cases']:
                prefix = result['scenario'] + '/' + result['path']
                raw = archive.read(prefix + '/case.json').decode()
                case = json.loads(raw.replace(result['caseId'], '__CASE__'))
                events = json.loads(archive.read(prefix + '/journal.json'))
                responses = [e for e in events if e['event'] == 'native-response' and e.get('provenance') == 'live TypeSafe' and e['status'] == 200]
                if len(responses) != 1: raise ValueError('Expected one actual provider response')
                case['name'] += '__recorded_' + result['path']
                case.update(outcome='COMPLETED', expected=responses[0]['response']['answers'], usagePrecision='EXACT',
                    provenance='unreviewed-live-capture',
                    coverage=['unreviewed-capture-replay'], responses=[{'body': responses[0]['response']}])
                cases.append(case)
        report['fixtureOrigin'] = 'unreviewed-live-capture'
        report['sourceRunId'] = captured['runId']
        report['replayApproved'] = False
        bundle.add('capture-source-report.json', captured)
    with core.run_lock():
        try:
            report['build'] = core.baseline()
            token = core.login('maya')
            bundle.secrets.append(token)
            with httpx.Client(timeout=60, trust_env=False) as client:
                for case in cases:
                    if not args.capture:
                        case.update(outcome='COMPLETED', expected={}, usagePrecision='EXACT', coverage=['live-wire-preflight'],
                            responses=[{'body': {'model': 'jev-1.13.0', 'answers': {}, 'usage': {'input_tokens': 0, 'output_tokens': 0}}}])
                    for path in ('java', 'sidecar'):
                        result = execute(client, case, path, token, secrets, bundle, TYPESAFE, core)
                        report['cases'].append(result)
                        print(case['name'] + '/' + path + ': ' + result['status'], flush=True)
                        if result['status'] != 'PROTOCOL_PASS': raise RuntimeError('Live request preflight failed')
            report['status'] = 'CAPTURE_REPLAY_PASS_REVIEW_REQUIRED' if args.capture else 'PROTOCOL_PASS'
        finally:
            core.require_offline_provider()
            report['runtimeRestored'] = True
            output = 'evidence/latest-typesafe-capture-replay/typesafe-ai' if args.capture else 'evidence/latest-typesafe-preflight/typesafe-ai'
            core.write_report(report, bundle, core.ROOT / output)


if __name__ == '__main__': main()
