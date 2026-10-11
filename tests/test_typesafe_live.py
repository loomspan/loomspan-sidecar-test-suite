import asyncio
import copy
import json
from pathlib import Path
from types import SimpleNamespace
import sys
import pytest
from fastapi import HTTPException
import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts'))
from fixtures.typesafe import reserve_live, forward_live
from suites.typesafe_ai.live import selection, answer_contract, runtime


def permit(tmp_path, monkeypatch):
    run = 'a' * 32
    monkeypatch.setenv('TYPESAFE_LIVE_RUN', run)
    monkeypatch.setenv('LOOMSPAN_TYPESAFE_API_KEY', 'test-only')
    body = {'model': 'jev-1.13.0', 'state': 'sample', 'questions': {}}
    file = tmp_path / ('typesafe-live-' + run + '.json')
    file.write_text(json.dumps({'runId': run, 'permits': {'case': {'path': 'java', 'request': body, 'used': False}}}))
    return body, file


def test_permit_survives_restart_and_rejects_changed_request(tmp_path, monkeypatch):
    body, file = permit(tmp_path, monkeypatch)
    with pytest.raises(HTTPException): reserve_live(tmp_path, 'case', 'java', {**body, 'state': 'changed'})
    assert not json.loads(file.read_bytes())['permits']['case']['used']
    reserve_live(tmp_path, 'case', 'java', body)
    with pytest.raises(HTTPException): reserve_live(tmp_path, 'case', 'java', body)
    assert json.loads(file.read_bytes())['permits']['case']['used']


def test_disabled_live_never_consumes_permit(tmp_path, monkeypatch):
    body, file = permit(tmp_path, monkeypatch)
    monkeypatch.delenv('TYPESAFE_LIVE_RUN')
    with pytest.raises(HTTPException): reserve_live(tmp_path, 'case', 'java', body)
    assert not json.loads(file.read_bytes())['permits']['case']['used']


def test_transport_failure_consumes_permit_without_retry(tmp_path, monkeypatch):
    body, file = permit(tmp_path, monkeypatch)
    calls = []
    async def fail(self, url, **kwargs):
        calls.append(url)
        raise httpx.ReadTimeout('simulated')
    monkeypatch.setattr(httpx.AsyncClient, 'post', fail)
    harness = SimpleNamespace(DATA=tmp_path, lock=asyncio.Lock(), journal=lambda *a, **kw: None)
    with pytest.raises(HTTPException): asyncio.run(forward_live(harness, 'case', 'java', body, 'request'))
    with pytest.raises(HTTPException): asyncio.run(forward_live(harness, 'case', 'java', body, 'request2'))
    assert calls == ['https://api.typesafe.ai/v1/systemone']


def test_selection_excludes_mock_failures_and_parents():
    args = SimpleNamespace(model='jev-1.13.0', skill_model=[], reasoning='medium', scenario=None, mode='capture', path=None)
    cases, paths = selection(args, ROOT)
    assert len(cases) * len(paths) == 12
    for name in ('retry_recovers', 'forward', 'read_timeout'):
        args.scenario = [name]
        with pytest.raises(ValueError): selection(args, ROOT)


def test_evidence_cases_have_predeclared_rubrics_and_live_selection():
    from suites.typesafe_ai.live import review_flags
    args = SimpleNamespace(model='jev-1.13.0', skill_model=[], reasoning='medium',
        scenario=['evidence_sparse', 'evidence_partial'], mode='capture', path=None)
    cases, paths = selection(args, ROOT)
    assert paths == ['java', 'sidecar']
    assert not review_flags(cases[0], {'impactEvidence': {'noul': .05}})
    assert review_flags(cases[0], {'impactEvidence': {'noul': .9}})
    assert review_flags(cases[1], {'impactEvidence': {'noul': .9}, 'impact': {'score': 2}})


@pytest.mark.parametrize('where', ['startup', 'body'])
def test_live_runtime_restores_without_leaving_gate_enabled(tmp_path, monkeypatch, where):
    import os
    import shutil
    (tmp_path / 'config').mkdir()
    shutil.copy(ROOT / 'config/java.yaml', tmp_path / 'config/java.yaml')
    directory = tmp_path / 'overlay'; directory.mkdir()
    monkeypatch.delenv('LOOMSPAN_RUN_OVERLAY', raising=False)
    calls = []
    def command(args):
        calls.append(os.getenv('LOOMSPAN_RUN_OVERLAY'))
        if len(calls) == 1 and where == 'startup': raise RuntimeError('startup')
    core = SimpleNamespace(ROOT=tmp_path, require_offline_provider=lambda: None, ready=lambda: None,
        verify_mounted=lambda *a: None, command=command, environment=SimpleNamespace(compose=lambda: []))
    report = {'runId': 'a'*32}
    with pytest.raises(RuntimeError):
        with runtime(core, directory, ['java'], report): raise RuntimeError('body')
    assert len(calls) == 2 and calls[0] and calls[1] is None
    assert report['runtimeRestored']


def test_contract_detects_invalid_distribution_and_fractional_score():
    questions = {'impact': {'type': 'score', 'criteria': ['working', 'blocked']}}
    answers = {'impact': {'type': 'score', 'score': .75, 'confidence': .4, 'probabilities': {'0': .25, '1': .75}}}
    assert answer_contract(answers, questions)
    wrong = copy.deepcopy(answers); wrong['impact']['probabilities']['1'] = .9
    assert not answer_contract(wrong, questions)


def test_score_tolerance_includes_decimal_boundary_without_float_false_failure():
    questions = {'impact': {'type': 'score', 'criteria': ['none', 'partial', 'blocked']}}
    answers = {'impact': {'type': 'score', 'score': 1.8, 'confidence': .71,
                          'probabilities': {'0': 0.0, '1': .19, '2': .81}}}
    assert answer_contract(answers, questions)
    answers['impact']['score'] = 1.79
    assert not answer_contract(answers, questions)
