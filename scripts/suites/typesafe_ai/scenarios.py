"""Independent authored wire expectations; no imports from skill or application generators."""
import json
import hashlib
import copy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACK = ROOT / 'fixtures/typesafe-ai/cases.json'
REVIEW_AREAS = ['Authored protocol fixtures establish integration behavior, not Jev judgment accuracy.',
                'No ticket routing, cancellation of customer accounts, or other business action is performed.']


def load_protocol(root=ROOT):
    pack = json.loads((root / 'fixtures/typesafe-ai/cases.json').read_bytes())
    if pack['model'] != 'jev-1.13.0' or pack['origin'] != 'authored-protocol-fixtures':
        raise ValueError('Unexpected TypeSafe fixture provenance/model')
    cases = pack['cases']
    if len({c['name'] for c in cases}) != len(cases):
        raise ValueError('Duplicate TypeSafe case names')
    return {'scenarios': [c['name'] for c in cases], 'fixtureOrigin': pack['origin']}, cases


def reviewed_pack(directory):
    review = json.loads((directory / 'review.json').read_bytes())
    raw = (directory / 'cases.json').read_bytes()
    if (review['status'] != 'ACCEPTED_BY_DELEGATED_REVIEW'
            or hashlib.sha256(raw).hexdigest() != review['casesSha256']):
        raise ValueError('TypeSafe accepted reference review/checksum mismatch')
    pack = json.loads(raw)
    if pack['model'] != 'jev-1.13.0' or pack['origin'] != 'reviewed-live-typesafe':
        raise ValueError('Unexpected accepted TypeSafe provenance/model')
    accepted = pack['cases']
    if not accepted or {c['name'] for c in accepted} != set(review['accepted']):
        raise ValueError('Unreviewed TypeSafe reference case')
    return accepted, review


def load(root=ROOT):
    manifest, cases = load_protocol(root)
    # The recorded wire payloads stay independent of the executor declarations.
    # Version-specific expectations use the original responses, including errors.
    bad_request = next(c['responses'] for c in cases if c['name'] == 'http_400')
    for case in cases:
        name = case['name']
        if name == 'boundary_singleton_null':
            case['outcome'] = 'FAILED'
            case['responses'] = []
        elif name == 'case_collision':
            # Case-distinct keys now reach the provider. Use the pack's terminal 400.
            case['responses'] = copy.deepcopy(bad_request)
        elif name in {'missing_answers', 'null_answers', 'array_answers', 'string_answers', 'read_timeout'}:
            case['outcome'] = 'COMPLETED'
            case['expected'] = case['responses'][0]['body'].get('answers')
    structured = copy.deepcopy(next(c for c in cases if c['name'] == 'structured_substitution'))
    structured.update(name='structured_parent', skill='tsTriageStructuredForward',
                      childSkill='tsTriageStructured', parent=True)
    structured['coverage'].append('planning-structured-transform')
    cases.append(structured)
    manifest['scenarios'].append(structured['name'])
    directory = root / 'fixtures/typesafe-ai/reference'
    if directory.exists():
        previous, _ = reviewed_pack(directory)
        revised, review = reviewed_pack(directory.parent / 'reference-partial-outage')
        accepted = [c for c in previous if c['skill'] != 'tsTriageEvidence']
        for c in revised:
            if c['skill'] != 'tsTriageEvidence':
                raise ValueError('Expected a scoped evidence replay case')
            c['policyExpected'] = review['accepted'][c['name']]['policyExpected']
        if not {c['name'] for c in previous if c['skill'] == 'tsTriageEvidence'} <= {c['name'] for c in revised}:
            raise ValueError('Missing evidence regression case after question revision')
        accepted += revised
        cases += accepted
        # Derived scenarios keep the accepted pack immutable. Expected assembly is
        # an explicit test contract; planner replies are still authored locally.
        for source in accepted:
            if source['skill'] == 'tsTriageFixed':
                for parent in ('tsTriageForward', 'tsTriageSummary'):
                    c = copy.deepcopy(source)
                    c.update(name=source['name'] + '__' + parent, skill=parent, parent=True,
                             childSkill='tsTriageFixed', coverage=['reviewed-live-composition'])
                    if parent == 'tsTriageSummary':
                        a = source['expected']
                        c['expected'] = {'department': a['department']['choice'],
                            'repeatProbability': a['repeat']['noul'], 'impact': a['impact']['score']}
                    cases.append(c)
            if source['name'] in {'reference_evidence_sparse_java', 'reference_evidence_partial_java',
                    'reference_evidence_normal_sidecar', 'reference_evidence_conflict_sidecar', 'reference_evidence_outage_java'}:
                for parent in ('tsTriageEvidenceForward', 'tsTriageEvidenceSummary'):
                    c = copy.deepcopy(source)
                    c.update(name=source['name'] + '__' + parent, skill=parent, parent=True,
                             childSkill='tsTriageEvidence', coverage=['reviewed-live-composition', 'impact-policy'])
                    cases.append(c)
        wire = next(c['request'] for c in accepted if c['skill'] == 'tsTriageEvidence')
        for fixture in json.loads((root / 'fixtures/typesafe-ai/impact-policy-cases.json').read_bytes()):
            if fixture['threshold'] != .8: continue  # Override is covered by the shared policy contract and API check.
            request = copy.deepcopy(wire)
            request['state'] = {'caseId': '__CASE__', 'message': 'Explicit application-policy protocol fixture.'}
            cases.append({'name': 'policy_' + fixture['name'], 'skill': 'tsTriageEvidence',
                'input': {'context': request['state']}, 'request': request, 'outcome': 'COMPLETED',
                'expected': fixture['answers'], 'policyExpected': fixture['expected'],
                'responses': [{'body': {'model': 'jev-1.13.0', 'answers': fixture['answers'],
                    'usage': {'input_tokens': 0, 'output_tokens': 0}}}],
                'usagePrecision': 'EXACT', 'coverage': ['authored-consumer-policy']})
        if len({c['name'] for c in cases}) != len(cases):
            raise ValueError('Duplicate TypeSafe reference case names')
        manifest = {'scenarios': [c['name'] for c in cases],
                    'fixtureOrigin': 'authored-protocol-and-reviewed-live-typesafe'}
    return manifest, cases


NAMES = tuple(load()[0]['scenarios'])
DEFAULT_NAMES = NAMES


def bind(case, identity):
    return json.loads(json.dumps(case).replace('__CASE__', identity))
