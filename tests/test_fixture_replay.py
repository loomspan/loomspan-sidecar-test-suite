"""Exercise fixture matching without a provider or application substitute."""
import asyncio
import importlib
import json

import pytest
from fastapi import HTTPException


@pytest.fixture
def server(monkeypatch,tmp_path):
    monkeypatch.setenv('FIXTURE_DATA',str(tmp_path))
    server=importlib.import_module('fixtures.server')
    monkeypatch.setattr(server,'DATA',tmp_path)
    monkeypatch.setattr(server,'cases',{})
    monkeypatch.setattr(server,'lock',asyncio.Lock())
    return server


def request(case,stage):
    class Request:
        async def json(self):
            return {'messages':[{'role':'system','content':stage},{'role':'user','content':case}]}
    return Request()


def test_parallel_stage_order_dependency_and_duplicate_rejection(server):
    case='case-fixture-unit'
    server.cases[case]={'path':'java','mode':'replay','used':[],'steps':[
        {'contains':[case],'systemContains':['history'],'response':{'value':'history'}},
        {'contains':[case],'systemContains':['guidance'],'response':{'value':'guidance'}},
        {'contains':[case],'systemContains':['assessment'],'after':[0,1],'response':{'value':'assessment'}}]}
    async def run():
        assert await server.model('java',request(case,'guidance'))=={'value':'guidance'}
        with pytest.raises(HTTPException) as early:
            await server.model('java',request(case,'assessment'))
        assert early.value.status_code==409
        assert await server.model('java',request(case,'history'))=={'value':'history'}
        assert await server.model('java',request(case,'assessment'))=={'value':'assessment'}
        with pytest.raises(HTTPException): await server.model('java',request(case,'history'))
    asyncio.run(run())
    events=[json.loads(line) for line in (server.DATA/'journal.ndjson').read_text().splitlines()]
    requests={e['requestId'] for e in events if e['event']=='model-request'}
    terminals=[e['requestId'] for e in events if e['event'] in ['model-response','model-rejected']]
    assert len(requests)==5 and len(terminals)==5 and set(terminals)==requests


def test_wrong_path_cannot_consume_another_paths_script(server):
    server.cases['case-one']={'path':'java','used':[],'steps':[{'contains':['case-one'],'response':{}}]}
    with pytest.raises(HTTPException) as failure:
        asyncio.run(server.model('sidecar',request('case-one','stage')))
    assert failure.value.status_code==409
    assert server.cases['case-one']['used']==[]


def test_ambiguous_stage_does_not_consume_either_response(server):
    step={'contains':['case-one'],'response':{}}
    server.cases['case-one']={'used':[],'steps':[step,step.copy()]}
    with pytest.raises(HTTPException): asyncio.run(server.model('java',request('case-one','stage')))
    assert server.cases['case-one']['used']==[]


def test_user_text_cannot_satisfy_system_stage_match(server):
    server.cases['case-one']={'used':[],'steps':[{'contains':['case-one'],
        'systemContains':['expected-stage'],'response':{}}]}
    with pytest.raises(HTTPException):
        asyncio.run(server.model('java',request('case-one expected-stage','wrong-stage')))
    assert server.cases['case-one']['used']==[]
