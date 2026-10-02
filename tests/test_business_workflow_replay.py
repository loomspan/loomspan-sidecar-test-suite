"""Source-stage matching must be ordered, attributable and provider-free."""
import asyncio
import copy
import importlib
import json
import pytest
from fastapi import HTTPException
from conftest import ROOT
from capture_business_diagnostic import stages, normalized
from inspect_capture import mission, system


@pytest.mark.parametrize('path', ['java', 'sidecar'])
def test_business_stages_match_source_and_explicit_correction(monkeypatch, tmp_path, path):
    source = ROOT / 'evidence/live-20261002-000544'
    diagnostic = json.loads((ROOT / 'fixtures/replay/business-output-diagnostic-v1.json').read_text())
    case = 'offline-unit-' + path
    steps, candidate = stages(source, diagnostic, path, case)
    assert len(steps) == (19 if path == 'java' else 18)
    assert all(not step.get('live') and step['provenance']['approvedBusinessReplay'] is False for step in steps)
    monkeypatch.setenv('FIXTURE_DATA', str(tmp_path))
    server = importlib.import_module('fixtures.server')
    monkeypatch.setattr(server, 'DATA', tmp_path)
    monkeypatch.setattr(server, 'cases', {case: {'mode': 'replay', 'path': path, 'used': [], 'steps': steps}})
    monkeypatch.setattr(server, 'lock', asyncio.Lock())
    def no_provider(*args, **kwargs):
        raise AssertionError('Replay must not create a provider client')
    monkeypatch.setattr(server.httpx, 'AsyncClient', no_provider)
    calls = [e['request'] for e in json.loads((source / 'journal.json').read_text())
             if e['event'] == 'model-request' and e.get('path') == path]
    old = diagnostic['samples'][path]['provenance']['caseId']
    calls = [normalized(call, old, case) for call in calls]
    compare = next(i for i, call in enumerate(calls) if mission(call, 'compareOptions'))
    correction = copy.deepcopy(calls[compare])
    correction['messages'].extend([
        {'role': 'assistant', 'content': steps[compare]['response']['choices'][0]['message']['content']},
        {'role': 'user', 'content': 'The previous response is valid JSON but does not satisfy the configured output_schema. Issues: $.selectedOption is not an allowed enum value.'}])
    calls.insert(compare + 1, correction)
    # Reverse independent assigned actions to reproduce the source-order mismatch.
    for parent, children in [('resolveEquipment', ['serviceHistory', 'serviceTerms', 'referenceEvidence']),
                             ('planResolution', ['entitlements', 'serviceResources', 'continuityOptions'])]:
        positions = [i for i, call in enumerate(calls) if mission(call, parent) and
                     any('Exact capability/tool: ' + child in system(call) for child in children)]
        reversed_calls = [calls[i] for i in reversed(positions)]
        for i, call in zip(positions, reversed_calls): calls[i] = call
    class Request:
        def __init__(self, body): self.body = body
        async def json(self): return self.body
    async def run():
        with pytest.raises(HTTPException):
            await server.model(path, Request(correction))
        assert server.cases[case]['used'] == []
        for call in calls:
            result = await server.model(path, Request(call))
            used = server.cases[case]['used'][-1]
            assert result == steps[used]['response']
        with pytest.raises(HTTPException):
            await server.model(path, Request(calls[-1]))
        assert sorted(server.cases[case]['used']) == list(range(len(steps)))
    asyncio.run(run())
    assert all(step['provenance'].get('kind') != 'live OpenRouter' for step in steps)
    final_values = [json.loads(step['response']['choices'][0]['message']['content']) for step in steps
                    if 'All required plan tasks are already COMPLETE.' in step['systemContains']]
    assert final_values == [candidate, candidate]
