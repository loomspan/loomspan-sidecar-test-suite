"""Replay must reject changed business evidence, not merely serve plausible outputs."""
import copy
import asyncio
import json
from pathlib import Path
import shutil
import sys

import pytest
import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts'))
from fixtures.replay import request_contract, request_matches
from replay_reference import load_reference, bind_case


def request():
    return {'model': 'model', 'reasoning_effort': 'medium', 'messages': [
        {'role': 'system', 'content': '--- ASSIGNED TASK ---\nID: task\nExact capability/tool: check\n\n--- COMPLETED TASK EVIDENCE ---\n' +
         json.dumps([{'taskId': 'b', 'skillName': 'quote', 'result': '{"cap":78000,"covered":false}'},
                     {'taskId': 'a', 'skillName': 'source', 'result': '{"arrival":"14:00"}'}])},
        {'role': 'user', 'content': "Fulfill the mission for skill 'parent'\nCanonical mission input:\n" +
         json.dumps({'caseId': 'case-one', 'context': {'capacity': 25}})}]}


@pytest.mark.parametrize('change', ['mission', 'evidence', 'task', 'model', 'reasoning', 'extra_message', 'missing_evidence'])
def test_request_mismatch_rejected(change):
    body = request(); expected = request_contract(body)
    if change == 'mission': body['messages'][1]['content'] = body['messages'][1]['content'].replace('25', '20')
    if change == 'evidence': body['messages'][0]['content'] = body['messages'][0]['content'].replace('78000', '48000')
    if change == 'task': body['messages'][0]['content'] = body['messages'][0]['content'].replace('ID: task', 'ID: other')
    if change == 'model': body['model'] = 'other'
    if change == 'reasoning': body['reasoning_effort'] = 'low'
    if change == 'extra_message': body['messages'].append({'role': 'assistant', 'content': '{}'})
    if change == 'missing_evidence': body['messages'][0]['content'] = 'No completed evidence'
    assert not request_matches(body, expected)


def test_parallel_evidence_order_and_nested_json_encoding_do_not_change_meaning():
    body = request(); expected = request_contract(body)
    prefix, raw = body['messages'][0]['content'].split('--- COMPLETED TASK EVIDENCE ---\n')
    items = json.loads(raw)[::-1]
    for item in items: item['result'] = json.loads(item['result'])
    body['messages'][0]['content'] = prefix + '--- COMPLETED TASK EVIDENCE ---\n' + json.dumps(items, sort_keys=True)
    assert request_matches(body, expected)
    items.append(items[0])
    body['messages'][0]['content'] = prefix + '--- COMPLETED TASK EVIDENCE ---\n' + json.dumps(items)
    assert not request_matches(body, expected)


def test_frozen_reference_integrity_unique_requests_and_identity_rebinding():
    manifest, cases = load_reference()
    assert len(cases) == 4 and len(manifest['skillModels']) == 8
    for case in cases.values():
        assert len(case['steps']) == 15
        contracts = [json.dumps(s['requestContract'], sort_keys=True) for s in case['steps']]
        assert len(set(contracts)) == 15
        bound = bind_case(case, 'fresh-case')
        assert bound['input']['caseId'] == bound['expected']['caseId'] == 'fresh-case'
        assert all(q['quoteId'].startswith('fresh-case-') for q in bound['expected']['quotes'])
        assert bind_case(bound, case['caseId']) == case
        assert all(s['response']['usage']['cost'] == 0 for s in bound['steps'])
        assert all(s['response']['usage']['total_tokens'] == 0 for s in bound['steps'])


@pytest.mark.parametrize('file', ['fixtures/reference/baseline.json', 'fixtures/business.json', 'config/skills/compareOptions.yaml'])
def test_stale_or_modified_reference_rejected(tmp_path, file):
    shutil.copytree(ROOT / 'fixtures', tmp_path / 'fixtures', ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copytree(ROOT / 'config', tmp_path / 'config')
    target = tmp_path / file
    if file.endswith('.yaml'):
        target.write_text(target.read_text(encoding='utf-8').replace('Business responsibility', 'Changed responsibility'), encoding='utf-8')
    elif file == 'fixtures/business.json':
        value = json.loads(target.read_bytes())
        value['serviceTerms']['rates']['expedited'] += 1
        target.write_text(json.dumps(value), encoding='utf-8')
    else:
        target.write_bytes(target.read_bytes() + b' ')
    with pytest.raises(ValueError, match='changed|checksum'):
        load_reference(tmp_path)


def test_fixture_consumes_once_and_never_falls_back_to_provider(tmp_path, monkeypatch):
    from fixtures import server
    monkeypatch.setattr(server, 'DATA', tmp_path)
    monkeypatch.setattr(server, 'cases', {})
    monkeypatch.setenv('CONTROL_KEY', 'test-control')
    monkeypatch.setenv('OPENROUTER_API_KEY', 'present-but-never-used')
    body = request()
    expected = request_contract(body)
    response = {'choices': [{'message': {'content': '{"ok":true}'}}]}
    async def exercise():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=server.app), base_url='http://fixture') as client:
            monkeypatch.setattr(server.httpx, 'AsyncClient', lambda *a, **k: pytest.fail('Paid fallback attempted'))
            registered = await client.post('/control/cases/case-one', headers={'X-Control-Key': 'test-control'},
                json={'mode': 'replay', 'path': 'java', 'steps': [{'requestContract': expected, 'response': response}]})
            assert registered.status_code == 200
            altered = copy.deepcopy(body)
            altered['messages'][1]['content'] = altered['messages'][1]['content'].replace('25', '20')
            assert (await client.post('/model/java/v1/chat/completions', json=altered)).status_code == 409
            assert server.cases['case-one']['used'] == []
            assert (await client.post('/model/sidecar/v1/chat/completions', json=body)).status_code == 409
            actual = await client.post('/model/java/v1/chat/completions', json=body)
            assert actual.status_code == 200 and actual.json() == response
            assert (await client.post('/model/java/v1/chat/completions', json=body)).status_code == 409
    asyncio.run(exercise())
