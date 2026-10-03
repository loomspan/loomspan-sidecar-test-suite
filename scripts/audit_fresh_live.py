"""Read-only revalidation of the retained live checkpoint; never calls a provider."""
import hashlib
import json
from pathlib import Path
from acceptance_report import checksums, junit_counts
from review_fresh_live import review

ROOT = Path(__file__).resolve().parents[1]
REVIEW = 'evidence/review-fresh-live-20261002'
QUALIFIED = 'REVIEWED_WITH_PRIORITY_RESPONSE_QUALIFICATION'


def read(path):
    return json.loads(path.read_bytes())


def verify_bindings(root, bindings):
    for name, expected in bindings.items():
        file = (root / name).resolve()
        if not file.is_relative_to(root.resolve()) or hashlib.sha256(file.read_bytes()).hexdigest() != expected:
            raise ValueError('Live evidence binding mismatch: ' + name)


def verify_semantics(semantic):
    if (semantic['status'] != QUALIFIED or semantic['approvedForReplay'] is not False or
            not any(c['area'] == 'priority responsiveness' and
                    c['result'] == 'JAVA_INCONCLUSIVE_SIDECAR_OBSERVED' for c in semantic['conclusions'])):
        raise ValueError('Live semantic disposition or Java qualification changed; review required')


def verify(build):
    directory = ROOT / REVIEW
    review_files = checksums(directory)
    report = read(directory / 'report.json')
    semantic = read(directory / 'semantic-review.json')
    verify_semantics(semantic)
    if report['status'] != QUALIFIED or report['approvedForReplay'] is not False:
        raise ValueError('Unexpected live report disposition')
    ledger = read(directory / 'phase-ledger.json')
    integrity = read(directory / 'integrity-final.json')
    verified = {}
    for item in integrity['captureIntegrity']:
        if item['failures']:
            raise ValueError('Live phase integrity failure')
        verified[item['directory']] = checksums(ROOT / item['directory'])
    for item in ledger:
        verify_bindings(ROOT / item['capture'], {'checksums.json': item['captureChecksumsSha256']})
    results = {}
    assertions = 0
    for label, name in [('baseline', 'live-20261002-201004'), ('priority', 'live-20261002-201657')]:
        capture = ROOT / 'evidence' / name
        verify_bindings(capture, semantic['sourceBindings'][name])
        manifest = read(capture / 'manifest.json')
        if manifest['artifacts'] != build['artifacts'] or manifest['configurationSha256'] != build['configurationSha256']:
            raise ValueError('Live checkpoint differs from current packages/configuration')
        verify_bindings(ROOT, manifest['configurationSha256'])
        prior = read(directory / ('final-' + label + '-review.json'))
        # Resolve by basename so preserved evidence can be relocated together.
        before = ROOT / 'evidence' / Path(prior['beforeCapture']).name
        checksums(before)
        result = review(capture, before)
        if (result['status'] != 'NEEDS_SEMANTIC_REVIEW' or len(result['checks']) != 128 or
                not all(c['passed'] for c in result['checks'])):
            raise ValueError('Retained live process review failed: ' + label)
        counts = junit_counts(directory / ('final-' + label + '-junit.xml'))
        if counts != {'tests': 8, 'passed': 8, 'failures': 0, 'errors': 0, 'skipped': 0}:
            raise ValueError('Incomplete live workflow assertions: ' + label)
        assertions += counts['passed']
        results[label] = result
    runtime = read(directory / 'runtime.json')
    if not all(runtime[k] for k in ['ready', 'providerDisabled', 'normalConfiguration', 'artifactsUnchanged']):
        raise ValueError('Live checkpoint runtime was not restored')
    return {'status': QUALIFIED, 'approvedForReplay': False, 'reviewDirectory': REVIEW,
            'reviewFilesVerified': review_files, 'phaseEvidenceVerified': verified,
            'reviewIndexSha256': hashlib.sha256((directory / 'checksums.json').read_bytes()).hexdigest(),
            'processChecksRevalidated': sum(len(r['checks']) for r in results.values()),
            'retainedWorkflowAssertionsVerified': assertions, 'newPaidCalls': 0,
            'semanticReview': semantic, 'processReviews': results,
            'scope': 'Read-only revalidation of fresh live checkpoint, not a new live execution or semantic approval.'}
