"""A partial/corrupt capture must never become replay provenance."""
import json

from inspect_capture import inspect, mission, preserves_applicability


def test_applicability_must_reach_actual_child_not_only_parent_evidence():
    source = {'id': 'SB-2', 'applicability': {'model': 'P240', 'hardwareRevision': 'B',
              'serialRangeInclusive': ['AP24B-0400', 'AP24B-0799']}}
    def request(body):
        return {'messages': [{'role': 'system', 'content': json.dumps(source)},
                {'role': 'user', 'content': 'Mission objective:\nAssessment\nCanonical mission input:\n' + json.dumps(body)}]}
    assert preserves_applicability(request({'context': {'referenceEvidence': [source]}}), source)
    assert not preserves_applicability(request({'context': {'referenceEvidence': [{'id': 'SB-2'}]}}), source)
    altered = {**source, 'applicability': {**source['applicability'], 'hardwareRevision': 'A'}}
    assert not preserves_applicability(request({'context': [altered]}), source)


def test_skill_identity_comes_from_framework_mission_not_embedded_evidence():
    for verb in ['Execute skill','Fulfill the mission for skill']:
        text="Mission objective:\n"+verb+" 'assessEquipment' using the provided mission input object."
        assert mission({'messages':[{'role':'user','content':text}]},'assessEquipment')
        assert not mission({'messages':[{'role':'user','content':text}]},'compareOptions')
        assert not mission({'messages':[{'role':'user','content':'Retrieved evidence: '+text}]},'assessEquipment')


def write(directory,name,value):
    (directory/name).write_text(json.dumps(value),encoding='utf-8')


def test_failed_application_cannot_be_approved_by_successful_trace(tmp_path):
    write(tmp_path,'manifest.json',{'mode':'live','model':'openai/gpt-6.1-sol','reasoning':'medium',
        'results':[{'path':'java','caseId':'unit-only','status':'FAILED'}]})
    write(tmp_path,'journal.json',[])
    write(tmp_path,'trace-index.json',[{'path':'java','cases':['unit-only'],'entrySkill':'resolveEquipment',
        'outcome':'SUCCEEDED','file':'missing.ndjson','sha256':'invalid'}])
    write(tmp_path,'running-identities.json',{})
    write(tmp_path,'java-assessment.json',{'status':'FAILED'})
    write(tmp_path,'java-business-records.json',{})
    before={p.name:p.read_bytes() for p in tmp_path.iterdir()}
    report=inspect(tmp_path)
    assert report['status']=='REJECTED_FOR_REPLAY' and report['approved'] is False
    assert any(c['check']=='completed immutable application assessment' and not c['passed'] for c in report['checks'])
    assert any(c['check']=='trace file exists inside capture' and not c['passed'] for c in report['checks'])
    assert before=={p.name:p.read_bytes() for p in tmp_path.iterdir()}


def test_missing_capture_reports_failures_without_inventing_evidence(tmp_path):
    report=inspect(tmp_path)
    assert report['status']=='REJECTED_FOR_REPLAY'
    assert report['sourceSha256']=={} and not list(tmp_path.iterdir())
