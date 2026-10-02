"""Observe released planner evidence in actual outbound provider requests."""
import json, os, pathlib
import pytest
capture=os.getenv('CAPTURE_DIRECTORY')
pytestmark=pytest.mark.skipif(not capture,reason='Set CAPTURE_DIRECTORY to captured runtime evidence')
def requests(path):
    return [e['request'] for e in json.loads((pathlib.Path(capture)/'journal.json').read_text(encoding='utf-8')) if e['event']=='model-request' and e.get('path')==path]
def system(request): return '\n'.join(m.get('content','') for m in request['messages'] if m['role']=='system')
def completed(text):
    block=text.split('--- COMPLETED TASK EVIDENCE ---\n',1)[1]
    return json.JSONDecoder().raw_decode(block[block.index('['):])[0]
@pytest.mark.parametrize('path',['java','sidecar'])
def test_complete_sibling_results_reach_dependent_assignment(path):
    steps=[system(r) for r in requests(path) if 'Exact capability/tool: assessEquipment\n' in system(r)]
    assert steps,'No equipment-assessment assignment request captured'
    items={item['skillName']:json.loads(item['result']) for item in completed(steps[0])}
    events=json.loads((pathlib.Path(capture)/'journal.json').read_text(encoding='utf-8'))
    case=items['serviceHistory']['caseId']
    for skill in ['serviceHistory','referenceEvidence','serviceTerms']:
        source=next(e['result'] for e in events if e['event']=='returned' and e.get('caseId')==case and e.get('kind')==skill)
        assert items[skill]['data']==source['data'],f'{skill}: returned fixture evidence was altered or truncated'
    assert len(json.dumps(items['referenceEvidence']))>1000
@pytest.mark.parametrize('path',['java','sidecar'])
def test_complete_nested_results_reach_final_synthesis(path):
    finals=[completed(system(r)) for r in requests(path) if 'All required plan tasks are already COMPLETE.' in system(r)]
    comparison=next((json.loads(i['result']) for f in finals for i in f if i['skillName']=='compareOptions'),None)
    resolution=next((json.loads(i['result']) for f in finals for i in f if i['skillName']=='planResolution'),None)
    assert comparison is not None,'Comparison result did not reach resolution final synthesis'
    assert resolution is not None,'Resolution result did not reach root final synthesis'
    for result in [comparison,resolution]:
        assert len(json.dumps(result))>1000
        assert result['quotes'] and result['citations'] and result['uncertainty'] and result['changeConditions']
        quote=next(q for q in result['quotes'] if q['option']=='expedited')
        assert (quote['maxExposure'],quote['fullyCoveredScopeMaximum'])==(78000,30000)
