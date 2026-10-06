"""Assembly evidence must establish exact values and accepted direct producers."""
from copy import deepcopy
import json
import pytest
from review_output_bindings import verify_assembly


DECLARATION = {'/caseId': {'from': 'input', 'path': '/caseId'},
               '/assessment': {'from': 'child_result', 'skill': 'child', 'path': ''}}


def records():
    def r(kind, seq, meta, data, frame='parent'):
        return dict(recordType=kind, sequence=seq, metadata=meta, data=data, frameId=frame)
    return [
        r('FRAME_OPENED', 0, {}, {'missionInput': {'caseId': 'case'}}),
        r('TOOL_CALL_COMPLETED', 1, {'capabilityName': 'child', 'linkedTaskId': 'selected'},
          {'details': {'result': '{"citations":["A","B"]}'}}, 'tool'),
        r('EVIDENCE_RECORDED', 2, {'capabilityName': 'child', 'linkedTaskId': 'selected'}, {}),
        r('PLAN_UPDATED', 3, {'planId': 'plan'}, {'tasks': [
            {'taskId': 'selected', 'capabilityName': 'child', 'status': 'COMPLETED'},
            {'taskId': 'other', 'capabilityName': 'other', 'status': 'COMPLETED'}]}),
        r('RESULT_ASSEMBLED', 4, {'skillName': 'parent', 'owningMissionFrameId': 'parent',
          'planId': 'plan', 'modelContributionRequired': False, 'outputBindings': [
              {'destination': '/caseId', 'sourceKind': 'input', 'sourcePath': '/caseId',
               'parentMissionFrameId': 'parent'},
              {'destination': '/assessment', 'sourceKind': 'child_result', 'sourcePath': '',
               'parentMissionFrameId': 'parent', 'sourceSkill': 'child', 'sourceTaskId': 'selected'}]},
          '{"caseId":"case","assessment":{"citations":["A","B"]}}'),
    ]


def test_exact_assembly_with_completed_work():
    assert verify_assembly(records(), 'parent', DECLARATION, False)['valid']


def test_chunked_text_assembly_matches_direct_text():
    r = records()
    text = r[-1]['data']
    r[-1]['data'] = None
    r[-1]['metadata'].update(payloadId='assembly', chunkCount=2, contentType='text/plain')
    for i, part in enumerate([text[:30], text[30:]]):
        r.append({'recordType': 'PAYLOAD_CHUNK_APPENDED', 'sequence': 5+i,
                  'metadata': {'payloadId': 'assembly', 'chunkIndex': i}, 'data': part})
    assert verify_assembly(r, 'parent', DECLARATION, False)['valid']
    r.pop()
    assert not verify_assembly(r, 'parent', DECLARATION, False)['valid']


@pytest.mark.parametrize('fault', ['changed', 'reordered', 'wrong_task', 'wrong_owner', 'wrong_path',
                                  'unfinished', 'missing', 'early', 'duplicate', 'model', 'foreign_evidence'])
def test_assembly_rejects_unproven_or_changed_sources(fault):
    r = deepcopy(records())
    meta = r[-1]['metadata']
    if fault in ['changed', 'reordered']:
        value = json.loads(r[-1]['data'])
        if fault == 'changed': value['caseId'] = 'other'
        else: value['assessment']['citations'].reverse()
        r[-1]['data'] = json.dumps(value)
    if fault == 'wrong_task': meta['outputBindings'][1]['sourceTaskId'] = 'another'
    if fault == 'wrong_owner': meta['owningMissionFrameId'] = 'another'
    if fault == 'wrong_path': meta['outputBindings'][0]['sourcePath'] = '/assetId'
    if fault == 'unfinished': r[3]['data']['tasks'][1]['status'] = 'IN_PROGRESS'
    if fault == 'missing': r.pop(2)
    if fault == 'early': r[-1]['sequence'] = 0
    if fault == 'duplicate': r.append(deepcopy(r[-1]))
    if fault == 'model': meta['modelContributionRequired'] = True
    if fault == 'foreign_evidence': r[2]['frameId'] = 'another'
    assert not verify_assembly(r, 'parent', DECLARATION, False)['valid']
