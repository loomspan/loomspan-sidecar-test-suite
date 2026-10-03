"""Run reviewed captured workflows through both Framework paths without provider access."""
from replay_selection import business_fixture, approval_file as business_approval
import environment as target_env
import argparse, hashlib, json, pathlib, subprocess, time, uuid
import httpx
from baseline import baseline
from capture import collect, wait
from capture_step_correction import records
from finalize_evidence import finalize
from login import login
from readiness import ready
from curate_business_replay import CASE, ROOT, digest, derive
from capture_business_diagnostic import normalized
from recovery_replay import recovery_steps

def require_offline_provider():
    result = subprocess.run(target_env.execute('fixtures', 'python', '-c',
        "import os; print('disabled' if not os.getenv('OPENROUTER_API_KEY') else 'enabled')"),
        capture_output=True, text=True, check=True)
    if result.stdout.strip() != 'disabled':
        raise RuntimeError('Offline capture requires fixture provider credential disabled via compose.offline.yaml')
    return True

def verify_source(sample):
    source=ROOT/'evidence'/sample['sourceCapture']
    if any(digest(source/name)!=wanted for name,wanted in sample['sourceSha256'].items()):
        raise ValueError('Source checksum mismatch')
    if digest(ROOT/sample['semanticReview'])!=sample['semanticReviewSha256']:
        raise ValueError('Semantic review changed; recurate explicitly')
    if any(s.get('live') for s in sample['steps']): raise ValueError('Live stage prohibited')
    if derive(source, sample['sourcePath'], ROOT/sample['semanticReview'], sample.get('normalizeCorrections',False)) != sample:
        raise ValueError('Fixture differs from reviewed source; recurate explicitly')

def run(scenario, recovery=False):
    ready()
    require_offline_provider()
    build = baseline()
    diagnostic_file = business_fixture()
    diagnostic = json.loads(diagnostic_file.read_bytes())
    approval = json.loads(business_approval().read_bytes())
    if approval['status'] != 'APPROVED_FOR_SCOPED_OFFLINE_REPLAY' or approval['fixtureSha256'] != digest(diagnostic_file):
        raise ValueError('Reviewed fixture approval/hash mismatch')
    samples = diagnostic['scenarios'][scenario]
    for sample in samples.values():
        verify_source(sample)
    out = ROOT / 'evidence' / (('full-workflow-recovery-' if recovery else 'business-reviewed-'+scenario+'-') + time.strftime('%Y%m%d-%H%M%S'))
    out.mkdir()
    secrets = json.loads((ROOT / '.runtime/secrets.json').read_text())
    token = login('maya')
    results, cases = [], []
    before = records()
    (out / 'business-records-before.json').write_text(json.dumps(before, indent=2), encoding='utf-8')
    with httpx.Client(timeout=300, trust_env=False) as client:
        try:
            for path, port in [('java', target_env.port(18081)), ('sidecar', target_env.port(18082))]:
                case = 'business-replay-' + path + '-' + uuid.uuid4().hex
                cases.append(case)
                sample = samples[path]
                steps = normalized(sample['steps'], CASE, case)
                if recovery:
                    steps = recovery_steps(steps)
                candidate = normalized(sample['expected'], CASE, case)
                registration = {'mode': 'replay', 'path': path, 'steps': steps}
                (out / (path + '-registration.json')).write_text(json.dumps(registration, indent=2), encoding='utf-8')
                (out / (path + '-expected.json')).write_text(json.dumps(candidate, indent=2), encoding='utf-8')
                body = normalized(sample['input'], CASE, case)
                (out / (path + '-input.json')).write_text(json.dumps(body, indent=2), encoding='utf-8')
                r = client.post(target_env.url(18090, '/control/cases/', '127.0.0.1') + case, json=registration,
                                headers={'X-Control-Key': secrets['control']})
                r.raise_for_status()
                api = f'http://127.0.0.1:{port}'
                r = client.post(api + '/assessments', json=body, headers={'Authorization': 'Bearer ' + token})
                r.raise_for_status()
                item = {'path': path, 'caseId': case, 'executionId': r.json()['id'], 'expectedCalls': len(steps)}
                results.append(item)
                terminal = wait(client, api, item['executionId'], token, timeout=300)
                item['status'] = terminal['status']
                (out / (path + '-assessment.json')).write_text(json.dumps(terminal, indent=2), encoding='utf-8')
                print(path, terminal['status'], flush=True)
        finally:
            collect(client, out, cases, secrets, [token])
            after = records()
            (out / 'business-records-after.json').write_text(json.dumps(after, indent=2), encoding='utf-8')
            (out / 'manifest.json').write_text(json.dumps({**build, 'mode': 'offline reviewed business replay', 'scenario': scenario,
                'sources': {p: {k: v for k, v in sample.items() if k not in ['steps','input','expected']} for p,sample in samples.items()},
                'diagnosticSha256': hashlib.sha256(diagnostic_file.read_bytes()).hexdigest(),
                'businessFixture': diagnostic_file.relative_to(ROOT).as_posix(),
                'recovery': recovery,
                'providerDisabledAtStart': True,
                'results': results, 'approved': False, 'paidCalls': 0,
                'scope': ('Full-workflow extra-brace comparison mutation with offline original-content correction; no new model judgment' if recovery else 'Unedited reviewed Muse stages; case-ID normalization only; candidate pending offline evidence review')}, indent=2), encoding='utf-8')
            finalize(out)
            print(out, flush=True)
    return out


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scenario', choices=['baseline','priority'], required=True)
    parser.add_argument('--recover', action='store_true')
    args=parser.parse_args(); run(args.scenario, args.recover)
