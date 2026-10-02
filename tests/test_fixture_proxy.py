"""The recorder must not withhold upstream headers/keepalives until JSON is complete."""
import asyncio, importlib, json
import httpx
import pytest
from fastapi import HTTPException

def test_live_proxy_relays_before_completion_and_records_unchanged_json(monkeypatch,tmp_path):
    monkeypatch.setenv('FIXTURE_DATA',str(tmp_path))
    monkeypatch.setenv('OPENROUTER_API_KEY','test-provider-key')
    server=importlib.import_module('fixtures.server')
    monkeypatch.setattr(server,'DATA',tmp_path)
    monkeypatch.setattr(server,'cases',{'case-relay':{'mode':'live'}})
    body={'messages':[{'role':'user','content':'case-relay'}],'stream':False}
    expected={'choices':[{'message':{'content':'unchanged'}}]}
    released=False
    class Upstream(httpx.AsyncByteStream):
        async def __aiter__(self):
            yield b' \n'
            assert released,'Proxy consumed the full response before forwarding its first bytes'
            yield json.dumps(expected).encode()
    async def handler(request):
        assert json.loads(request.content)==body
        return httpx.Response(200,headers={'content-type':'application/json'},stream=Upstream())
    real_client=httpx.AsyncClient
    monkeypatch.setattr(server.httpx,'AsyncClient',lambda **kw:real_client(transport=httpx.MockTransport(handler),**kw))
    class Request:
        async def json(self):return body
    async def run():
        nonlocal released
        response=await server.model('java',Request())
        assert response.status_code==200
        iterator=response.body_iterator
        first=await anext(iterator)
        assert first==b' \n'
        released=True
        chunks=[first]+[chunk async for chunk in iterator]
        assert json.loads(b''.join(chunks))==expected
    asyncio.run(run())
    events=[json.loads(line) for line in (tmp_path/'journal.ndjson').read_text().splitlines()]
    assert [event['event'] for event in events]==['model-request','model-response']
    assert events[-1]['response']==expected
    assert 'test-provider-key' not in (tmp_path/'journal.ndjson').read_text()


def test_controlled_live_only_for_explicit_once_matched_correction(monkeypatch,tmp_path):
    monkeypatch.setenv('FIXTURE_DATA',str(tmp_path))
    monkeypatch.setenv('OPENROUTER_API_KEY','test-provider-key')
    server=importlib.import_module('fixtures.server')
    monkeypatch.setattr(server,'DATA',tmp_path)
    monkeypatch.setattr(server,'lock',asyncio.Lock())
    steps=[{'contains':['case-controlled'],'systemContains':['initial'],'response':{'captured':'fault'}},
           {'contains':['case-controlled'],'systemContains':['correction'],'after':[0],'live':True}]
    monkeypatch.setattr(server,'cases',{'case-controlled':{'mode':'controlled-live','used':[],'steps':steps}})
    calls=[]
    async def handler(request):
        calls.append(json.loads(request.content))
        return httpx.Response(200,json={'choices':[{'message':{'content':'corrected'}}]})
    real_client=httpx.AsyncClient
    monkeypatch.setattr(server.httpx,'AsyncClient',lambda **kw:real_client(transport=httpx.MockTransport(handler),**kw))
    class Request:
        def __init__(self,stage):self.body={'messages':[{'role':'system','content':stage},{'role':'user','content':'case-controlled'}]}
        async def json(self):return self.body
    async def run():
        with pytest.raises(HTTPException):await server.model('java',Request('correction'))
        assert not calls
        assert await server.model('java',Request('initial'))=={'captured':'fault'}
        request=Request('correction');response=await server.model('java',request)
        assert json.loads(b''.join([c async for c in response.body_iterator]))['choices'][0]['message']['content']=='corrected'
        assert calls==[request.body]
        with pytest.raises(HTTPException):await server.model('java',request)
        assert len(calls)==1
    asyncio.run(run())


def test_live_steps_require_explicit_single_stage_mode(monkeypatch,tmp_path):
    monkeypatch.setenv('CONTROL_KEY','control-test')
    server=importlib.import_module('fixtures.server')
    monkeypatch.setattr(server,'cases',{})
    for body in [{'mode':'replay','steps':[{'live':True}]},
                 {'mode':'controlled-live','steps':[{'live':True},{'live':True}]},
                 {'mode':'controlled-live','steps':[]}]:
        with pytest.raises(HTTPException):asyncio.run(server.register('bad-case',body,'control-test'))
    assert not server.cases
