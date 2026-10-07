"""Scenario inputs and checks, independent of runner orchestration.

These assessment checks are deliberately smaller than release acceptance.
Business judgment remains a separate human review, never a keyword score.
"""
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_NAMES = ('baseline', 'priority')
NAMES = (*DEFAULT_NAMES, 'capacity_shortfall', 'later_start')
REVIEW_AREAS = [
    'Diagnostic uncertainty and evidence supporting each hypothesis',
    'Technician work/access and loaner delivery/setup before production',
    'Offer expiry versus diagnosis and timely approved submission',
    'Premium inclusion, conditional charges and elapsed versus billable hours',
    'Verified service authority versus separate procurement approval',
    'Justified tradeoff and explicit residual risk without invented facts',
]


def inputs(name, case):
    if name not in NAMES:
        raise ValueError('Unknown scenario: ' + name)
    value = json.loads((ROOT / 'fixtures/base-case.json').read_bytes())
    value = copy.deepcopy(value)
    value['caseId'] = case
    if name in ('priority', 'capacity_shortfall'):
        value['context']['restorationRiskPreference'] = (
            'Prioritize continuity despite higher cost; urgently escalate loaner approval '
            'while retaining diagnosis as needed.')
    if name == 'capacity_shortfall':
        value['context']['minimumCapacityPerMinute'] = 25
    if name == 'later_start':
        value['context']['productionStart'] = '2026-09-30T16:00:00-07:00'
    return value


def decoded(value):
    return json.loads(value) if isinstance(value, str) else value


def payload(record, records):
    if record.get('data') is not None:
        return record['data']
    meta = record['metadata']
    chunks = sorted((r for r in records if r['recordType'] == 'PAYLOAD_CHUNK_APPENDED'
                     and r['metadata'].get('payloadId') == meta.get('payloadId')),
                    key=lambda r: r['metadata']['chunkIndex'])
    if len(chunks) != meta.get('chunkCount') or [c['metadata']['chunkIndex'] for c in chunks] != list(range(len(chunks))):
        raise ValueError('Incomplete or duplicate trace payload chunks')
    return json.loads(''.join(c['data'] for c in chunks))


def review(terminal, mission, rows, trace):
    """Check persisted authoritative values and actual accepted child results."""
    checks = {'execution completed': terminal.get('status') == 'COMPLETED'}
    if not checks['execution completed']:
        return checks
    value = decoded(terminal['result'])
    checks['case and asset preserved'] = all(value.get(k) == mission[k] for k in ['caseId', 'assetId'])
    quotes = [json.loads(r['body']) for r in rows['quotes']]
    published = value.get('quotes', [])
    encode = lambda v: json.dumps(v, sort_keys=True)
    checks['authoritative quotes exact, without omissions or duplicates'] = (
        len(quotes) == 2 and sorted(map(encode, published)) == sorted(map(encode, quotes)))
    checks['assessment persisted exactly'] = (
        len(rows['assessments']) == 1 and json.loads(rows['assessments'][0]['body']) == value)
    checks['assessment created no commitment'] = not rows['requests']
    checks['decision fields present'] = all(value.get(k) for k in [
        'disposition', 'selectedOption', 'rationale', 'alternatives', 'uncertainty',
        'acceptedRisk', 'nextDecision', 'citations']) and all(
            isinstance(value.get(k), list) for k in ['pursuedOptions', 'reviewConcerns'])
    checks['pursued options consistent with primary selection'] = portfolio_valid(value)
    for skill, expected in [('assessEquipment', value.get('equipmentAssessment')), ('compareOptions', value)]:
        calls = [r for r in trace if r['recordType'] == 'TOOL_CALL_COMPLETED' and r.get('route') == skill]
        checks[skill + ' accepted result preserved exactly'] = (
            len(calls) == 1 and decoded(payload(calls[0], trace)['details']['result']) == expected)
    checks.update(publication_checks(value, trace))
    return checks


def portfolio_valid(value):
    options = value.get('pursuedOptions')
    allowed = {'expedited', 'standard', 'loaner', 'replacement'}
    if not isinstance(options, list) or any(not isinstance(x, str) or x not in allowed for x in options):
        return False
    if len(options) != len(set(options)):
        return False
    selected = value.get('selectedOption')
    return selected in options if selected in allowed else selected in {'defer', 'undecided'} and not options


def publication_checks(value, trace):
    """Transport checks only: an exact published finding may still be incorrect."""
    def single(kind, skill, field):
        calls = [r for r in trace if r['recordType'] == kind and r.get('route') == skill]
        return decoded(payload(calls[0], trace)['details'][field]) if len(calls) == 1 else {}
    checks = {}
    incident = single('TOOL_CALL_STARTED', 'assessEquipment', 'arguments').get('context', {}).get('incident')
    checks['original incident published exactly'] = (
        incident is not None and value.get('equipmentAssessment', {}).get('reportedIncident') == incident)
    for option in ['expedited', 'standard', 'loaner', 'replacement']:
        skill = 'assess' + option.title() + 'Feasibility'
        accepted = single('TOOL_CALL_COMPLETED', skill, 'result')
        published = value.get('optionAssessments', {}).get(option)
        checks[option + ' feasibility published exactly'] = bool(accepted) and published == accepted
        context = single('TOOL_CALL_STARTED', skill, 'arguments').get('context', {})
        offer = context.get('offer', {})
        checks[option + ' source metadata published exactly'] = isinstance(published, dict) and all(
            source_key in offer and published.get(key) == offer[source_key]
            for key, source_key in [('offerExpiresAt', 'expiresAt'),
                                    ('offerReserved', 'reserved'), ('offerSourceId', 'sourceId')])
        if option in ['expedited', 'standard']:
            conditions, references = service_conditions(published, context)
            checks[option + ' dedicated service condition fields present'] = conditions
            checks[option + ' owner references resolve to exact source directory'] = references
    return checks


def service_conditions(published, context):
    """Check presence and reference integrity, not rule meaning or role selection."""
    if not isinstance(published, dict):
        return False, False
    conditions = all(isinstance(published.get(k), str) and published[k].strip()
                     for k in ['chargeCondition', 'scopeChangeCondition', 'coverageReviewCondition'])
    contacts = context.get('assetContext', {}).get('contacts')
    if not isinstance(contacts, list) or published.get('ownerDirectory') != contacts:
        return bool(conditions), False
    ids = {c['id'] for c in contacts}
    valid = True
    for key in ['dispatchOwnerSourceIds', 'coverageReviewerSourceIds']:
        refs = published.get(key)
        valid = valid and isinstance(refs, list) and all(isinstance(x, str) and x in ids for x in refs)
        if valid:
            valid = len(refs) == len(set(refs))
    return bool(conditions), valid
