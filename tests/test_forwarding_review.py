"""Forwarding must be proved by task identity, full completion and exact trace text."""
from copy import deepcopy
import pytest
from review_forwarding import verify_records


def records():
    def r(kind, seq, meta, data, frame='parent'):
        return dict(recordType=kind, sequence=seq, metadata=meta, data=data, frameId=frame)
    return [
        r('TOOL_CALL_COMPLETED', 1, {'capabilityName': 'child', 'linkedTaskId': 'selected'},
          {'details': {'result': '{ "citations": ["A", "B"] }'}}),
        r('EVIDENCE_RECORDED', 2, {'capabilityName': 'child', 'linkedTaskId': 'selected'}, {}),
        r('PLAN_UPDATED', 3, {'planId': 'plan'}, {'tasks': [
            {'taskId': 'selected', 'capabilityName': 'child', 'status': 'COMPLETED'},
            {'taskId': 'other', 'capabilityName': 'other', 'status': 'COMPLETED'}]}),
        r('RESULT_FORWARDED', 4, {'skillName': 'parent', 'capabilityName': 'child',
          'linkedTaskId': 'selected', 'planId': 'plan'}, {}),
        r('TOOL_CALL_COMPLETED', 5, {'capabilityName': 'parent', 'linkedTaskId': 'outer'},
          {'details': {'result': '{ "citations": ["A", "B"] }'}}),
    ]


def test_exact_forwarding_with_complete_work():
    assert verify_records(records(), 'parent', 'child')['valid']


@pytest.mark.parametrize('fault', ['text', 'wrong_task', 'wrong_plan', 'unfinished', 'missing', 'early', 'duplicate'])
def test_forwarding_rejects_unproven_or_changed_result(fault):
    r = deepcopy(records())
    if fault == 'text': r[-1]['data']['details']['result'] = '{"citations":["A","B"]}'
    if fault == 'wrong_task': r[3]['metadata']['linkedTaskId'] = 'another'
    if fault == 'wrong_plan': r[3]['metadata']['planId'] = 'another'
    if fault == 'unfinished': r[2]['data']['tasks'][1]['status'] = 'IN_PROGRESS'
    if fault == 'missing': r.pop(3)
    if fault == 'early': r[3]['sequence'] = 0
    if fault == 'duplicate': r.append(deepcopy(r[0]))
    assert not verify_records(r, 'parent', 'child')['valid']
