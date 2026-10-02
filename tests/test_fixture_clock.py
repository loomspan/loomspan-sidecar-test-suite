"""Only authenticated per-case clock overrides affect expiry evidence."""
import asyncio, importlib, json
import pytest
from fastapi import HTTPException

@pytest.fixture
def server(monkeypatch,tmp_path):
    monkeypatch.setenv('FIXTURE_DATA',str(tmp_path));monkeypatch.setenv('CONTROL_KEY','unit-control')
    server=importlib.import_module('fixtures.server');monkeypatch.setattr(server,'DATA',tmp_path)
    monkeypatch.setattr(server,'cases',{'first':{},'second':{}})
    return server

def test_clock_is_authenticated_and_case_isolated(server):
    async def run():
        with pytest.raises(HTTPException) as error: await server.clock('first',{'now':'2026-09-29T11:00:00-07:00'},'wrong')
        assert error.value.status_code==403 and 'clock' not in server.cases['first']
        await server.clock('first',{'now':'2026-09-29T11:00:00-07:00'},'unit-control')
        assert (await server.records('first','clock'))['data']['now']=='2026-09-29T11:00:00-07:00'
        assert (await server.records('second','clock'))['data']['now']=='2026-09-29T09:05:00-07:00'
        journal=[json.loads(line) for line in (server.DATA/'journal.ndjson').read_text(encoding='utf-8').splitlines()]
        assert [e['caseId'] for e in journal if e['event']=='clock-set']==['first']
    asyncio.run(run())

@pytest.mark.parametrize('body',[{}, {'now':'invalid'}, {'now':'2026-09-29T11:00:00'}, {'now':None}])
def test_clock_rejects_invalid_timestamp(server,body):
    with pytest.raises(HTTPException) as error: asyncio.run(server.clock('first',body,'unit-control'))
    assert error.value.status_code==400 and 'clock' not in server.cases['first']
