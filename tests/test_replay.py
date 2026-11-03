"""Replay must reject changed business evidence, not merely serve plausible outputs."""
import copy
import asyncio
import json
import hashlib
import re
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


@pytest.mark.parametrize('file', ['fixtures/reference-namespaced/baseline.json', 'fixtures/business.json', 'config/skills/equipment-service/compareOptions.yaml'])
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


def test_namespace_contract_changes_only_reviewed_framework_identity_positions():
    source, current = ROOT/'fixtures/reference', ROOT/'fixtures/reference-namespaced'
    review = json.loads((current/'namespace-review.json').read_bytes())
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    # The preserved worktree may predate its eol=lf attribute. Pin the Git
    # representation without rewriting that original reference manifest.
    manifest_lf = (source/'manifest.json').read_bytes().replace(b'\r\n', b'\n')
    assert hashlib.sha256(manifest_lf).hexdigest() == review['sourceManifestLfSha256']
    observed = []

    def compare(before, after, path):
        if before == after:
            return
        if isinstance(before, dict):
            assert isinstance(after, dict) and before.keys() == after.keys(), path
            for key in before:
                compare(before[key], after[key], path+'/'+key)
        elif isinstance(before, list):
            assert isinstance(after, list) and len(before) == len(after), path
            for i, (left, right) in enumerate(zip(before, after)):
                compare(left, right, path+'/'+str(i))
        elif re.fullmatch(r'.+/steps/\d+/response/choices/0/message/content', path):
            original, qualified = json.loads(before), json.loads(after)
            assert ('tasks' in original and 'capabilityName' in original) or original.get('stepAction') == 'CALL_TOOL', path
            # Qualification inserts only these exact structural prefixes; all
            # whitespace and prose bytes inside the recorded reply stay intact.
            assert re.sub(r'("(?:capabilityName|toolName)"\s*:\s*")default-', r'\1', after) == before
            compare(original, qualified, path+'/$json')
        else:
            if path.endswith('/requestContract/assignedTask'):
                expected, count = re.subn(r'(?m)^(Exact capability/tool: )([A-Za-z][A-Za-z0-9_]*)$', r'\1default-\2', before)
                assert count == 1 and after == expected, path
            else:
                assert re.fullmatch(r'.+/steps/\d+/(requestContract/(skill|completedEvidence/\d+/skillName)|response/choices/0/message/content/\$json/(capabilityName|toolName|tasks/\d+/capabilityName))', path), path
                assert after == 'default-'+before, path
            observed.append({'path': path, 'before': before, 'after': after})

    for name, original_hash in review['sourceFiles'].items():
        assert digest(source/name) == original_hash
        assert digest(current/name) == review['currentFiles'][name]
        compare(json.loads((source/name).read_bytes()), json.loads((current/name).read_bytes()), name)
    sort = lambda values: sorted(values, key=lambda change: change['path'])
    assert sort(observed) == sort(review['changes'])
    assert len(observed) == 316


def test_namespace_review_accepts_source_manifest_from_a_clean_lf_checkout(tmp_path, monkeypatch):
    for name in ('reference', 'reference-namespaced'):
        shutil.copytree(ROOT/'fixtures'/name, tmp_path/'fixtures'/name)
    manifest = tmp_path/'fixtures/reference/manifest.json'
    manifest.write_bytes(manifest.read_bytes().replace(b'\r\n', b'\n'))
    monkeypatch.setitem(test_namespace_contract_changes_only_reviewed_framework_identity_positions.__globals__, 'ROOT', tmp_path)
    test_namespace_contract_changes_only_reviewed_framework_identity_positions()


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
