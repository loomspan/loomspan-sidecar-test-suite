"""Curate reviewed model captures, verify full offline acceptance, then activate business fixtures."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import uuid
from acceptance_report import checksums
from curate_business_replay import derive, digest, ROOT
from replay_selection import POINTER, business_fixture
from review_fresh_live import review
from run_suite import write


def validate_sources(report_file, semantic_file):
    report = json.loads(report_file.read_bytes())
    semantic = json.loads(semantic_file.read_bytes())
    if report['mode'] != 'capture' or report['status'] != 'AUTOMATED_CHECKS_PASS' or set(report['paths']) != {'java', 'sidecar'}:
        raise ValueError('A passing paired capture run is required')
    if semantic.get('suiteReportSha256') != digest(report_file):
        raise ValueError('Semantic review is not bound to this exact suite report')
    if {s['scenario'] for s in report['stages']} != {'baseline', 'priority', 'service-requests'} or len(report['stages']) != 3:
        raise ValueError('Baseline, priority and service-request validation required')
    samples = {}
    for stage in report['stages']:
        if stage['scenario'] == 'service-requests':
            from review_service_requests import inspect as service_review
            if service_review(Path(stage['capture'])) != stage['review'] or stage['review']['status'] != 'PASS':
                raise ValueError('Service-request review no longer matches')
            continue
        source = Path(stage['capture']).resolve()
        if source.parent != (ROOT / 'evidence').resolve():
            raise ValueError('Capture must be preserved in this workspace evidence directory')
        checksums(source)
        reviewed = semantic['captures'][source.name]
        if reviewed.get('checksumsSha256') != digest(source / 'checksums.json'):
            raise ValueError('Semantic review source binding mismatch')
        for path in ['java', 'sidecar']:
            if reviewed['paths'][path].get('status') != 'SUITABLE_FOR_REPLAY_CURATION' or not reviewed['paths'][path].get('rationale'):
                raise ValueError('Both integrations need substantive semantic review')
        current = review(source, stage['review']['beforeCapture'], ('java', 'sidecar'),
                         {k: report[k] for k in ['model', 'reasoning']})
        if current != stage['review'] or current['status'] != 'NEEDS_SEMANTIC_REVIEW':
            raise ValueError('Live mechanical review no longer matches the capture')
        samples[stage['scenario']] = (source, reviewed)
    return samples


def curate(report_file, semantic_file, version):
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}', version):
        raise ValueError('Version must be a short lowercase name')
    sources = validate_sources(report_file, semantic_file)
    directory = ROOT / 'fixtures/replay/versions' / version
    directory.mkdir(parents=True, exist_ok=False)
    samples = {}
    for scenario, (source, reviewed) in sources.items():
        review_file = directory / (scenario + '-semantic-review.json')
        write(review_file, {**reviewed, 'suiteReportSha256': digest(report_file),
                            'originalSemanticReviewSha256': digest(semantic_file)})
        samples[scenario] = {path: derive(source, path, review_file, normalize_corrections=True) for path in ['java', 'sidecar']}
    fixture = directory / 'business.json'
    write(fixture, {'formatVersion': 1, 'status': 'CURATED_CANDIDATE', 'approved': False,
                    'normalization': 'caseId only; no response wording edits', 'mutations': [], 'scenarios': samples})
    # Authorizes source-reviewed offline validation, not activation or full-delivery acceptance.
    write(directory / 'business-approval.json', {'status': 'APPROVED_FOR_SCOPED_OFFLINE_REPLAY',
        'fixtureSha256': digest(fixture), 'scope': 'Source-reviewed business replay; activation requires full offline acceptance',
        'suiteReportSha256': digest(report_file), 'semanticReviewSha256': digest(semantic_file)})
    return fixture


def verify_and_activate(fixture):
    fixture = fixture.resolve()
    before = business_fixture()
    env = dict(os.environ, LOOMSPAN_BUSINESS_FIXTURE=str(fixture))
    completed = subprocess.run([sys.executable, 'scripts/run_acceptance.py'], cwd=ROOT, env=env,
                               capture_output=True, text=True, encoding='utf-8', errors='replace')
    # The acceptance runner redacts its own evidence; redact its console output as well.
    log = completed.stdout + completed.stderr
    secrets = list(json.loads((ROOT / '.runtime/secrets.json').read_bytes()).values())
    secrets += [v for k, v in os.environ.items() if ('TOKEN' in k or 'API_KEY' in k) and len(v) > 15]
    for secret in secrets: log = log.replace(secret, '[REDACTED]')
    (fixture.parent / 'validation.log').write_text(log, encoding='utf-8')
    if completed.returncode:
        raise RuntimeError('Candidate offline acceptance failed; active fixture unchanged; see validation.log')
    # Bind the exact successful report advertised by this subprocess, not a "latest" directory.
    match = re.search(r'^PASS; report (.+summary\.md)\s*$', completed.stdout, re.M)
    if not match: raise ValueError('Acceptance did not identify its passing report')
    acceptance = Path(match[1].strip()).parent
    checksums(acceptance)
    manifest = json.loads((acceptance / 'manifest.json').read_bytes())
    if manifest['status'] != 'PASS' or manifest['fixtureSha256'] != digest(fixture) or manifest['paidCalls'] != 0:
        raise ValueError('Acceptance is not bound to candidate fixture')
    pointer = {'fixture': fixture.relative_to(ROOT).as_posix(), 'fixtureSha256': digest(fixture),
               'previousFixture': before.relative_to(ROOT).as_posix(), 'acceptance': str(acceptance),
               'acceptanceChecksumsSha256': digest(acceptance / 'checksums.json')}
    write(fixture.parent / 'activation.json', pointer)
    temporary = POINTER.with_name('active-business-' + uuid.uuid4().hex + '.tmp')
    write(temporary, pointer); temporary.replace(POINTER)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--suite', type=Path, required=True, help='capture-suite report.json')
    parser.add_argument('--semantic-review', type=Path, required=True)
    parser.add_argument('--version', required=True)
    args = parser.parse_args()
    lock = ROOT / '.runtime/run-suite.lock'
    handle = lock.open('x')
    try:
        with handle:
            handle.write(str(os.getpid())); handle.flush()
            fixture = curate(args.suite.resolve(), args.semantic_review.resolve(), args.version)
            print('Validating candidate with the complete offline suite; static faults unchanged.', flush=True)
            verify_and_activate(fixture)
            print('Activated ' + str(fixture))
    finally:
        lock.unlink()


if __name__ == '__main__':
    main()
