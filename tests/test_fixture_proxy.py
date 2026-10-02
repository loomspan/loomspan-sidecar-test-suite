"""The recorder must not withhold upstream headers/keepalives until JSON is complete."""
import asyncio, importlib, json
import httpx

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
