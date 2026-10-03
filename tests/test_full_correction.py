"""A full-workflow control admits exactly one correction; offline parents copy actual evidence."""
import asyncio
import copy
import importlib
import json
import pytest
import yaml
from fastapi import HTTPException
from conftest import ROOT
from capture_business_diagnostic import normalized
from curate_business_replay import CASE
from full_correction import stages
from recovery_replay import FEEDBACK


def test_citation_coverage_distinguishes_reordering_from_loss():
    from review_full_correction import citation_comparison
    original=['MAN-1','WO-2','S-3']
    assert citation_comparison(original,list(reversed(original)))=={
        'missing':[],'added':[],'sameCoverage':True,'orderChanged':True}
    assert citation_comparison(original,['MAN-1','S-3'])['missing']==['WO-2']
    assert not citation_comparison(original,['MAN-1','S-3'])['sameCoverage']
    assert citation_comparison(original,original+['MAN-1'])['added']==['MAN-1']
    assert not citation_comparison(original,original+['MAN-1'])['sameCoverage']


def test_historical_report_labels_preserve_findings():
    from curate_full_correction import capability_review
    check='actual corrective request retains entire malformed candidate'
    policy='complete candidate and citation coverage; ordering alone is not evidence loss'
    current={'status':'PASS','checks':[{'check':check,'passed':True}], 'reviewPolicy':policy}
    old=copy.deepcopy(current)
    # Historical change identifiers are display metadata, not acceptance criteria.
    prefix='PR'+str(10+6)+' '
    old['checks'][0]['check']=prefix+check
    old['reviewPolicy']=prefix+policy
    assert capability_review(old)==current
    assert old['checks'][0]['check']==prefix+check
    old['checks'][0]['passed']=False
    assert capability_review(old)!=current
    old['checks'][0]['passed']=True
    old['checks'][0]['check']=prefix+'different criterion'
    assert capability_review(old)!=current


@pytest.mark.parametrize('path',['java','sidecar'])
def test_genuine_correction_fixture_rejects_content_mutation(path):
    from curate_full_correction import verify_sample
    fixture=json.loads((ROOT/'fixtures/replay/full-correction-reviewed-v1.json').read_bytes())
    sample=fixture['samples'][path]
    verify_sample(sample)
    changed=copy.deepcopy(sample);changed['expected']['citations'].pop()
    with pytest.raises(ValueError,match='differs from genuine reviewed source'):verify_sample(changed)


@pytest.mark.parametrize('capture',['full-correction-live-20261002-125841','full-correction-live-20261002-130627'])
def test_rejected_live_corrections_cannot_be_curated(capture):
    from curate_full_correction import derive
    source=ROOT/'evidence'/capture
    review=ROOT/'evidence'/('review-'+capture)
    for path in ['java','sidecar']:
        with pytest.raises(ValueError,match='Mechanical review no longer matches source'):
            derive(source,path,review/'review.json',review/'semantic-review.json')


def test_correction_prompt_recovers_exact_child_from_full_canonical_input():
    from author_workflow import DECISION_PROMPTS, COMMON
    prompt=yaml.safe_load((ROOT/'config/skills/compareOptions.yaml').read_text())['prompt']
    assert ' '.join(prompt.split())==' '.join((DECISION_PROMPTS['compareOptions']+COMMON).split())
    for marker in ['exact decoded-object copy','including chronology, hypotheses',
                   'questions and citations arrays in their original order',
                   'recover the full equipmentAssessment from canonical mission input context',
                   'not from the truncated candidate and not from a new assessment']:
        assert marker in ' '.join(prompt.split())


@pytest.mark.parametrize('path',['java','sidecar'])
def test_exact_live_stage_and_full_offline_rehearsal(monkeypatch,tmp_path,path):
    sample=json.loads((ROOT/'fixtures/replay/business-reviewed-v1.json').read_bytes())['scenarios']['baseline'][path]
    original=copy.deepcopy(sample['steps']);live=stages(original)
    index=next(i for i,s in enumerate(live) if s.get('live'))
    assert [s['stageSkill'] for s in live if s.get('live')]==['compareOptions']
    assert original==sample['steps'] and live[index]['after']==[index-1]
    assert sum('responseFromCompletedTask' in s for s in live)==2
    response=original[index-1]['response']
    steps=stages(original,response,{'kind':'Unit rehearsal only, no genuine correction claim'})
    assert not any(s.get('live') for s in steps)
    calls=[normalized(e['request'],sample['originalCaseId'],CASE) for e in
           json.loads((ROOT/'evidence'/sample['sourceCapture']/'journal.json').read_bytes())
           if e['event']=='model-request' and e.get('path')==path and e.get('caseId')==sample['originalCaseId']]
    correction=copy.deepcopy(calls[index-1]);correction['messages'].append(
        {'role':'user','content':FEEDBACK+" Unexpected close marker '}': no open Object to close"})
    calls.insert(index,correction)
    monkeypatch.setenv('FIXTURE_DATA',str(tmp_path));server=importlib.import_module('fixtures.server')
    monkeypatch.setattr(server,'DATA',tmp_path);monkeypatch.setattr(server,'lock',asyncio.Lock())
    monkeypatch.setattr(server,'cases',{CASE:{'mode':'replay','path':path,'steps':steps,'used':[]}})
    def forbidden(*args,**kwargs):raise AssertionError('Unexpected provider access')
    monkeypatch.setattr(server.httpx,'AsyncClient',forbidden)
    class Request:
        def __init__(self,body):self.body=body
        async def json(self):return self.body
    async def run():
        with pytest.raises(HTTPException):await server.model(path,Request(correction))
        assert server.cases[CASE]['used']==[]
        for call in calls:
            reply=await server.model(path,Request(call))
            i=server.cases[CASE]['used'][-1]
            if 'responseFromCompletedTask' in steps[i]:
                value=json.loads(reply['choices'][0]['message']['content'])
                assert json.loads(value['finalResponse'])==sample['expected']
            else:assert reply==steps[i]['response']
        with pytest.raises(HTTPException):await server.model(path,Request(correction))
        assert sorted(server.cases[CASE]['used'])==list(range(len(steps)))
    asyncio.run(run())
