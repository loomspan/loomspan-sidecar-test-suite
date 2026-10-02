"""Reviewed replay must reject changed evidence and never call a provider."""
import asyncio, copy, importlib, json
import pytest
from fastapi import HTTPException
from conftest import ROOT
from curate_business_replay import CASE, derive
from capture_business_diagnostic import normalized

@pytest.mark.parametrize('scenario',['baseline','priority'])
@pytest.mark.parametrize('path',['java','sidecar'])
def test_reviewed_replay_source_fidelity_and_strict_matching(monkeypatch,tmp_path,scenario,path):
    bundle=json.loads((ROOT/'fixtures/replay/business-reviewed-v1.json').read_bytes())
    sample=bundle['scenarios'][scenario][path]
    assert derive(ROOT/'evidence'/sample['sourceCapture'],path,ROOT/sample['semanticReview'])==sample
    steps=sample['steps']; assert all(not s.get('live') and s['provenance']['mutations']==[] for s in steps)
    source=ROOT/'evidence'/sample['sourceCapture']
    calls=[normalized(e['request'],sample['originalCaseId'],CASE) for e in json.loads((source/'journal.json').read_bytes()) if e['event']=='model-request' and e.get('path')==path and e.get('caseId')==sample['originalCaseId']]
    monkeypatch.setenv('FIXTURE_DATA',str(tmp_path)); server=importlib.import_module('fixtures.server')
    monkeypatch.setattr(server,'DATA',tmp_path); monkeypatch.setattr(server,'cases',{CASE:{'mode':'replay','path':path,'used':[],'steps':steps}})
    monkeypatch.setattr(server,'lock',asyncio.Lock())
    def forbidden(*args,**kwargs): raise AssertionError('Provider prohibited')
    monkeypatch.setattr(server.httpx,'AsyncClient',forbidden)
    class Request:
        def __init__(self,body): self.body=body
        async def json(self): return self.body
    altered=copy.deepcopy(calls[0])
    for m in altered['messages']:
        if m.get('role')=='user': m['content']=m['content'].replace('AP24B-0517','DIFFERENT-SERIAL').replace('NB-P240-017','DIFFERENT-ASSET')
    # Reverse independent branch requests while retaining graph dependencies.
    for skill in ['resolveEquipment','planResolution']:
        positions=[i for i,s in enumerate(steps) if s['stageKind']=='action' and s['stageSkill']==skill and len(s['after'])==1]
        swapped=[calls[i] for i in reversed(positions)]
        for i,c in zip(positions,swapped): calls[i]=c
    async def run():
        with pytest.raises(HTTPException): await server.model(path,Request(altered))
        assert server.cases[CASE]['used']==[]
        for c in calls:
            result=await server.model(path,Request(c)); index=server.cases[CASE]['used'][-1]
            assert result==steps[index]['response']
        with pytest.raises(HTTPException): await server.model(path,Request(calls[-1]))
        assert sorted(server.cases[CASE]['used'])==list(range(len(steps)))
    asyncio.run(run())

def test_rejected_capture_cannot_be_curated():
    with pytest.raises(ValueError,match='not suitable'):
        derive(ROOT/'evidence/live-20261002-100123','java',ROOT/'evidence/review-live-20261002-100123/semantic-review.json')
