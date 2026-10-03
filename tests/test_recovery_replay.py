"""Fault derivation preserves source and requires actual parser-feedback matching."""
import asyncio
import copy
import importlib
import json
import pytest
from fastapi import HTTPException
from conftest import ROOT
from curate_business_replay import CASE
from recovery_replay import FEEDBACK, recovery_steps
from capture_reviewed_replay import require_offline_provider


@pytest.mark.parametrize('status', ['disabled', 'enabled'])
def test_offline_capture_fails_closed_with_provider_enabled(monkeypatch, status):
    from types import SimpleNamespace
    monkeypatch.setattr('capture_reviewed_replay.subprocess.run',
                        lambda *args, **kwargs: SimpleNamespace(stdout=status+'\n'))
    if status == 'disabled':
        assert require_offline_provider() is True
    else:
        with pytest.raises(RuntimeError, match='credential disabled'):
            require_offline_provider()


@pytest.mark.parametrize('path', ['java', 'sidecar'])
def test_recovery_requires_feedback_and_preserves_dependency_graph(monkeypatch, tmp_path, path):
    sample = json.loads((ROOT / 'fixtures/replay/business-reviewed-v1.json').read_bytes())['scenarios']['baseline'][path]
    original = copy.deepcopy(sample['steps'])
    steps = recovery_steps(original)
    assert original == sample['steps']
    index = next(i for i,s in enumerate(steps) if s['stageSkill']=='compareOptions')
    invalid, valid = steps[index:index+2]
    assert invalid['response']['choices'][0]['message']['content'] == valid['response']['choices'][0]['message']['content']+'}'
    assert valid['after']==[index]
    assert steps[index+2]['after']==[index+1]
    assert all(not s.get('live') for s in steps)
    for i,s in enumerate(steps):
        assert all(dep<i for dep in s['after'])
    with pytest.raises(json.JSONDecodeError):
        json.loads(invalid['response']['choices'][0]['message']['content'])
    assert json.loads(valid['response']['choices'][0]['message']['content'])==sample['expected']
    monkeypatch.setenv('FIXTURE_DATA', str(tmp_path))
    server = importlib.import_module('fixtures.server')
    monkeypatch.setattr(server, 'DATA', tmp_path)
    monkeypatch.setattr(server, 'lock', asyncio.Lock())
    monkeypatch.setattr(server, 'cases', {CASE:{'mode':'replay','path':path,'used':list(range(index)), 'steps':steps}})
    def forbidden(*args, **kwargs):
        raise AssertionError('Provider prohibited')
    monkeypatch.setattr(server.httpx, 'AsyncClient', forbidden)
    class Request:
        def __init__(self, feedback=False):
            self.body = {'messages': [
                {'role':'user','content':"Mission objective:\nFulfill the mission for skill 'compareOptions' using the provided mission input object.\nCanonical mission input:\n"+json.dumps(valid['missionInputEquals'])}]}
            if feedback:
                self.body['messages'].append({'role':'user','content':FEEDBACK+' Extra closing brace.'})
        async def json(self):
            return self.body
    async def run():
        assert await server.model(path, Request())==invalid['response']
        with pytest.raises(HTTPException):
            await server.model(path, Request())
        assert server.cases[CASE]['used']==list(range(index+1))
        assert await server.model(path, Request(True))==valid['response']
    asyncio.run(run())
