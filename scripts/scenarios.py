"""Scenario inputs and checks, independent of runner orchestration.

These assessment checks are deliberately smaller than release acceptance.
Business judgment remains a separate human review, never a keyword score.
"""
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAMES = ('baseline', 'priority')
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
    if name == 'priority':
        value['context']['restorationRiskPreference'] = (
            'Prioritize continuity despite higher cost; urgently escalate loaner approval '
            'while retaining diagnosis as needed.')
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
        'acceptedRisk', 'changeConditions', 'nextDecision', 'responsibleParty', 'citations'])
    for skill, expected in [('assessEquipment', value.get('equipmentAssessment')), ('compareOptions', value)]:
        calls = [r for r in trace if r['recordType'] == 'TOOL_CALL_COMPLETED' and r.get('route') == skill]
        checks[skill + ' accepted result preserved exactly'] = (
            len(calls) == 1 and decoded(payload(calls[0], trace)['details']['result']) == expected)
    return checks
