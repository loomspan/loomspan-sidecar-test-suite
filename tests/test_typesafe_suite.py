"""Protect offline native transport and the independent test catalog."""
import asyncio
import copy
import json
import shutil
from pathlib import Path
import sys
import httpx
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts'))
from suites.typesafe_ai.scenarios import load, load_protocol, bind
from fixtures import server


def test_pack_distinguishes_protocol_fixtures_from_recorded_judgments():
    manifest, cases = load_protocol()
    assert manifest['fixtureOrigin'] == 'authored-protocol-fixtures'
    assert len(cases) == 49
    assert {q['type'] for c in cases for q in c['request']['questions'].values()} == {'choice', 'noul', 'score'}
    assert all(c['request']['model'] == 'jev-1.13.0' for c in cases)
    assert {'forward', 'summary', 'role_denied', 'read_timeout', 'retry_recovers', 'retry_exhausts'} <= set(manifest['scenarios'])
    assert all((ROOT / 'config/skills/typesafe-ai' / (c['skill'] + '.yaml')).is_file() for c in cases)
    assert bind(cases[0], 'fresh')['input']['context']['caseId'] == 'fresh'


def test_reviewed_pack_is_separate_and_detects_tampering(tmp_path):
    manifest, cases = load()
    references = [c for c in cases if c.get('provenance') == 'reviewed-live-typesafe']
    assert references and manifest['fixtureOrigin'] == 'authored-protocol-and-reviewed-live-typesafe'
    assert all(c['expected'] == c['responses'][0]['body']['answers'] for c in references if not c.get('parent'))
    assert all(c['source']['bundleSha256'] and c['source']['runId'] for c in references)
    shutil.copytree(ROOT / 'fixtures/typesafe-ai', tmp_path / 'fixtures/typesafe-ai')
    file = tmp_path / 'fixtures/typesafe-ai/reference/cases.json'
    file.write_bytes(file.read_bytes() + b' ')
    with pytest.raises(ValueError, match='checksum'): load(tmp_path)


def test_freezer_requires_reviewed_capture_and_new_destination(tmp_path):
    from suites.typesafe_ai.reference import freeze
    with pytest.raises(ValueError, match='new'): freeze({}, {}, tmp_path)
    with pytest.raises(ValueError, match='semantic review'):
        freeze({}, {'status': 'UNREVIEWED'}, tmp_path / 'new')
    review = json.loads((ROOT / 'fixtures/typesafe-ai/reference/review.json').read_bytes())
    with pytest.raises(ValueError, match='exactly'):
        freeze({}, review, tmp_path / 'new')
    assert not (tmp_path / 'new').exists()


@pytest.mark.parametrize('change', ['none', 'model', 'state', 'questions', 'path', 'authorization', 'exhausted'])
def test_native_fixture_is_strict_and_cannot_call_provider(tmp_path, monkeypatch, change):
    monkeypatch.setattr(server, 'DATA', tmp_path)
    monkeypatch.setattr(server, 'cases', {})
    monkeypatch.setenv('CONTROL_KEY', 'control-test')
    # Presence of a provider credential must not create a native live path.
    monkeypatch.setenv('LOOMSPAN_TYPESAFE_API_KEY', 'unused-provider-key')
    case = bind(load()[1][0], 'native-test')
    async def run():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=server.app), base_url='http://fixture') as client:
            r = await client.post('/control/cases/native-test', headers={'X-Control-Key': 'control-test'}, json={
                'suite': 'typesafe-ai', 'mode': 'replay', 'path': 'java', 'nativeRequest': case['request'],
                'nativeResponses': case['responses']})
            assert r.status_code == 200
            request = copy.deepcopy(case['request'])
            if change == 'model': request['model'] = 'jev-latest'
            if change == 'state': request['state']['message'] = 'changed'
            if change == 'questions': request['questions']['department']['criteria']['other'] = 'changed'
            headers = {'Authorization': 'Bearer fixture-typesafe-transport'}
            if change == 'authorization': headers = {}
            url = '/typesafe/' + ('sidecar' if change == 'path' else 'java') + '/v1/systemone'
            if change == 'exhausted':
                assert (await client.post(url, json=request, headers=headers)).status_code == 200
            response = await client.post(url, json=request, headers=headers)
            assert response.status_code == (200 if change == 'none' else 409)
            if change == 'none': assert response.json() == case['responses'][0]['body']
    asyncio.run(run())


def test_native_skills_omit_chat_options_and_use_local_transport():
    forbidden = {'prompt', 'thinking_level', 'planning_mode', 'allowed_skills', 'output_schema', 'output_from'}
    for file in (ROOT / 'config/skills/typesafe-ai').glob('*.yaml'):
        skill = yaml.safe_load(file.read_bytes())
        if 'typesafe' in skill:
            assert not forbidden & set(skill)
            for host in ('java', 'sidecar'):
                config = yaml.safe_load((ROOT / 'config' / (host + '.yaml')).read_bytes())['loomspan']
                model = config['models'][skill['model']]
                assert model['provider-model'] == 'jev-1.13.0'
                connection = config['connections'][model['connection']]
                assert connection['driver'] == 'typesafe'
                assert connection['base-url'].startswith('http://fixtures:8080/typesafe/' + host)
                assert 'thinking-levels' not in model


def test_trace_catalog_follows_pages_without_dropping_earlier_runs():
    import run_suite
    def handle(request):
        if request.url.params.get('cursor') == 'next':
            return httpx.Response(200, json={'items': [{'traceId': 'old'}], 'hasMore': False})
        return httpx.Response(200, json={'items': [{'traceId': 'new'}], 'hasMore': True, 'nextCursor': 'next'})
    with httpx.Client(transport=httpx.MockTransport(handle)) as client:
        assert [x['traceId'] for x in run_suite.trace_catalog(client, 'java', 'test')] == ['new', 'old']
