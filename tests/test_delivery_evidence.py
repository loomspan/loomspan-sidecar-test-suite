"""Independent first-delivery evidence assertions. Run explicitly on a capture."""
import json, os, pathlib
import pytest
capture=os.getenv('CAPTURE_DIRECTORY')
pytestmark=pytest.mark.skipif(not capture,reason='Set CAPTURE_DIRECTORY to a complete live capture; no acceptance implied')
@pytest.mark.parametrize('path',['java','sidecar'])
def test_required_evidence_reaches_equipment_assessment(path):
    events=json.loads((pathlib.Path(capture)/'journal.json').read_text(encoding='utf-8'))
    requests=[e['request'] for e in events if e['event']=='model-request' and e.get('path')==path]
    assessment=[r for r in requests if any("Execute skill 'assessEquipment'" in str(m.get('content','')) for m in r['messages'])]
    assert assessment,'equipment model responsibility was not exercised'
    material=json.dumps(assessment[0])
    for required in ['WO-0820','NOTE-0916','SB-2','20-minute','42 minutes']:
        assert required in material,f'{path}: required upstream evidence {required} missing from actual assessment model input'
@pytest.mark.parametrize('path',['java','sidecar'])
def test_complete_assessment_and_trace(path):
    directory=pathlib.Path(capture)
    result=json.loads((directory/(path+'-assessment.json')).read_text(encoding='utf-8'))
    assert result['status']=='COMPLETED',result
    assert result.get('assessmentVersion'),'immutable assessment was not published'
    value=json.loads(result['result'])
    assert value['assetId']=='NB-P240-017'
    assert value['uncertainty'] and value['acceptedRisk'] and value['citations']
    quotes={q['option']:q for q in value['quotes']}
    assert quotes['expedited']['maxExposure']==78000
    assert quotes['expedited']['fullyCoveredScopeMaximum']==30000
    index=json.loads((directory/'trace-index.json').read_text(encoding='utf-8'))
    assert any(t['path']==path and value['caseId'] in t['cases'] and (directory/t['file']).exists() for t in index)
