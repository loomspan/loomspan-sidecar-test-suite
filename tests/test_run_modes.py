"""Model selection, failure accounting, and immutable fixture activation boundaries."""
import json
from pathlib import Path
from types import SimpleNamespace
from contextlib import contextmanager
import pytest
import yaml
import run_suite
import model_profile
import replay_selection
import refresh_replay


def test_model_override_preserves_prompts_and_does_not_edit_originals(tmp_path):
    original = (run_suite.ROOT / 'config/skills/resolveEquipment.yaml').read_bytes()
    overlay = run_suite.make_overlay(tmp_path / 'profile', ('java',), 'example/model', None)
    config = yaml.safe_load(overlay.read_text())
    assert set(config['services']) == {'fixtures', 'java'}
    copied = yaml.safe_load((overlay.parent / 'skills/resolveEquipment.yaml').read_text())
    source = yaml.safe_load(original)
    source.pop('thinking_level')
    assert copied == source
    assert (run_suite.ROOT / 'config/skills/resolveEquipment.yaml').read_bytes() == original
    assert yaml.safe_load((overlay.parent / 'java.yaml').read_text())['loomspan']['models']['reasoning'] == {
        'connection': 'model', 'provider-model': 'example/model', 'thinking-levels': []}


def test_single_path_profile_does_not_require_other_model(monkeypatch, tmp_path):
    raw = 'loomspan:\n  models:\n    reasoning:\n      provider-model: example/model\n      thinking-levels: []\n'
    (tmp_path / 'java.yaml').write_text(raw)
    monkeypatch.setenv('LOOMSPAN_MODEL_CONFIG_DIRECTORY', str(tmp_path))
    monkeypatch.setattr(model_profile.subprocess, 'check_output', lambda *a, **k: raw)
    assert model_profile.model_profile(('java',)) == {'model': 'example/model', 'reasoning': None}


def test_restore_runs_even_when_preservation_fails(monkeypatch, tmp_path):
    monkeypatch.setenv('LOOMSPAN_OPENROUTER_API_KEY', 'test-only')
    calls = []
    def preserve():
        calls.append('preserve')
        if calls.count('preserve') == 2: raise RuntimeError('failed preservation')
    monkeypatch.setattr(run_suite, 'preserve', preserve)
    monkeypatch.setattr(run_suite, 'command', lambda args, **kwargs: calls.append(('command', bool(__import__('os').getenv('LOOMSPAN_RUN_OVERLAY')))))
    monkeypatch.setattr(run_suite, 'ready', lambda: None)
    import capture_reviewed_replay
    monkeypatch.setattr(capture_reviewed_replay, 'require_offline_provider', lambda: True)
    with pytest.raises(RuntimeError):
        with run_suite.live_runtime(tmp_path / 'run', ('java',), 'example/model', None): pass
    assert ('command', False) in calls
    assert 'LOOMSPAN_RUN_OVERLAY' not in __import__('os').environ


def test_fixture_selection_cannot_escape_fixture_directory(monkeypatch, tmp_path):
    monkeypatch.setattr(replay_selection, 'ROOT', tmp_path)
    monkeypatch.setenv('LOOMSPAN_BUSINESS_FIXTURE', '../unrelated.json')
    with pytest.raises(ValueError): replay_selection.business_fixture()


def test_failed_candidate_never_changes_active_selection(monkeypatch, tmp_path):
    (tmp_path / '.runtime').mkdir()
    (tmp_path / '.runtime/secrets.json').write_text('{}')
    fixture = tmp_path / 'business.json'; fixture.write_text('{}')
    pointer = tmp_path / 'active-business.json'; pointer.write_text('old')
    monkeypatch.setattr(refresh_replay, 'ROOT', tmp_path)
    monkeypatch.setattr(refresh_replay, 'POINTER', pointer)
    monkeypatch.setattr(refresh_replay, 'business_fixture', lambda: tmp_path / 'old.json')
    monkeypatch.setattr(refresh_replay.subprocess, 'run', lambda *a, **k: SimpleNamespace(returncode=1, stdout='failed', stderr=''))
    with pytest.raises(RuntimeError): refresh_replay.verify_and_activate(fixture)
    assert pointer.read_text() == 'old'


def test_semantic_review_requires_exact_report_binding(tmp_path):
    report = tmp_path / 'report.json'
    report.write_text(json.dumps({'mode': 'capture', 'status': 'AUTOMATED_CHECKS_PASS', 'paths': ['java', 'sidecar']}))
    semantic = tmp_path / 'semantic.json'; semantic.write_text('{"suiteReportSha256":"wrong"}')
    with pytest.raises(ValueError, match='bound'): refresh_replay.validate_sources(report, semantic)


def test_successful_activation_binds_candidate_and_keeps_previous(monkeypatch, tmp_path):
    (tmp_path / '.runtime').mkdir()
    (tmp_path / '.runtime/secrets.json').write_text('{}')
    fixture = tmp_path / 'fixtures/replay/versions/new/business.json'
    fixture.parent.mkdir(parents=True); fixture.write_text('{}')
    acceptance = tmp_path / 'evidence/accepted'; acceptance.mkdir(parents=True)
    (acceptance / 'checksums.json').write_text('{}')
    (acceptance / 'manifest.json').write_text(json.dumps({'status': 'PASS', 'fixtureSha256': refresh_replay.digest(fixture), 'paidCalls': 0}))
    pointer = tmp_path / 'fixtures/replay/active-business.json'
    old = tmp_path / 'fixtures/replay/business-reviewed-v1.json'
    monkeypatch.setattr(refresh_replay, 'ROOT', tmp_path)
    monkeypatch.setattr(refresh_replay, 'POINTER', pointer)
    monkeypatch.setattr(refresh_replay, 'business_fixture', lambda: old)
    monkeypatch.setattr(refresh_replay, 'checksums', lambda p: True)
    monkeypatch.setattr(refresh_replay.subprocess, 'run', lambda *a, **k: SimpleNamespace(
        returncode=0, stdout='PASS; report ' + str(acceptance / 'summary.md') + '\n', stderr=''))
    refresh_replay.verify_and_activate(fixture)
    selected = json.loads(pointer.read_bytes())
    assert selected['fixtureSha256'] == refresh_replay.digest(fixture)
    assert selected['previousFixture'] == old.relative_to(tmp_path).as_posix()
    assert selected['acceptanceChecksumsSha256'] == refresh_replay.digest(acceptance / 'checksums.json')


def test_historical_fixture_review_ignores_new_active_selection(monkeypatch, tmp_path):
    monkeypatch.setattr(replay_selection, 'ROOT', tmp_path)
    monkeypatch.setenv('LOOMSPAN_BUSINESS_FIXTURE', 'fixtures/replay/versions/new/business.json')
    assert replay_selection.business_fixture('fixtures/replay/business-reviewed-v1.json') == tmp_path / 'fixtures/replay/business-reviewed-v1.json'


def test_changed_active_bytes_fail_closed(monkeypatch, tmp_path):
    root = tmp_path / 'fixtures/replay'; root.mkdir(parents=True)
    file = root / 'business.json'; file.write_text('changed')
    pointer = root / 'active-business.json'
    pointer.write_text(json.dumps({'fixture': 'fixtures/replay/business.json', 'fixtureSha256': 'old'}))
    monkeypatch.delenv('LOOMSPAN_BUSINESS_FIXTURE', raising=False)
    monkeypatch.setattr(replay_selection, 'ROOT', tmp_path)
    monkeypatch.setattr(replay_selection, 'POINTER', pointer)
    with pytest.raises(ValueError, match='hash mismatch'): replay_selection.business_fixture()


@pytest.mark.parametrize('mode,path,wanted', [('evaluate','java',('java',)), ('evaluate','sidecar',('sidecar',)), ('live','java',('java','sidecar'))])
def test_run_submits_only_selected_integrations_and_includes_service_checks(monkeypatch, tmp_path, mode, path, wanted):
    captures = []
    @contextmanager
    def runtime(directory, paths, **profile):
        assert paths == wanted
        assert profile == {'model': 'example/model', 'reasoning': None}
        yield
    def capture(selected, priority, parallel):
        assert selected == ('both' if len(wanted)==2 else wanted[0])
        assert parallel == (len(wanted)==2)
        captures.append(priority)
        directory = tmp_path / ('capture-' + str(priority)); directory.mkdir()
        return directory
    def service(source, paths):
        assert source == tmp_path / 'capture-False' and paths == wanted
        return source
    monkeypatch.setattr(run_suite, 'ROOT', tmp_path)
    monkeypatch.setattr(run_suite, 'live_runtime', runtime)
    monkeypatch.setattr(run_suite, 'capture', capture)
    monkeypatch.setattr(run_suite, 'finalize', lambda _: None)
    monkeypatch.setattr(run_suite, 'observations', lambda _: {})
    monkeypatch.setattr(run_suite, 'checked_review', lambda *a: {'status':'NEEDS_SEMANTIC_REVIEW','checks':[{'check':'business result','passed':True}]})
    import capture_service_requests, review_service_requests
    monkeypatch.setattr(capture_service_requests, 'run', service)
    monkeypatch.setattr(review_service_requests, 'inspect', lambda *a: {'status':'PASS','checks':[{'check':'service receipt','passed':True}]})
    assert run_suite.run_live(SimpleNamespace(mode=mode,path=path,model='example/model',reasoning='none')) == 0
    assert captures == [False, True]
    report=json.loads(next((tmp_path/'evidence').glob('*/report.json')).read_bytes())
    assert [s['scenario'] for s in report['stages']] == ['baseline','priority','service-requests']


def test_alternate_profile_requires_actual_matching_requests(tmp_path):
    from inspect_capture import inspect
    profile={'model':'example/model','reasoning':None}
    for name,value in {
        'manifest.json':{'mode':'live',**profile,'results':[{'path':'java','caseId':'case','status':'FAILED'}]},
        'journal.json':[{'event':'model-request','path':'java','caseId':'case','requestId':'r',
                         'request':{'model':'wrong/model','messages':[]}}],
        'trace-index.json':[], 'running-identities.json':{},
        'java-assessment.json':{'status':'FAILED'}, 'java-business-records.json':{}
    }.items(): (tmp_path/name).write_text(json.dumps(value))
    report=inspect(tmp_path,('java',),profile)
    checks={c['check']:c['passed'] for c in report['checks']}
    assert checks['explicit selected live model and reasoning']
    assert not checks['every request uses selected model/reasoning']
    assert report['status']=='REJECTED_FOR_REPLAY'


def test_refresh_uses_final_correction_but_rejects_unexplained_duplicate_calls():
    from copy import deepcopy
    from curate_business_replay import successful_stage_calls
    first={'requestId':'original','request':{'messages':[
        {'role':'system','content':'Return the assessment'},
        {'role':'user','content':"Mission objective:\nFulfill the mission for skill 'assessEquipment' using the provided mission input object."}]}}
    corrected=deepcopy(first);corrected['requestId']='corrected'
    corrected['request']['messages'].append({'role':'user','content':'The previous response could not be parsed as JSON. Repair it.'})
    selected,omitted=successful_stage_calls([first,corrected])
    assert selected == [corrected] and omitted == ['original']
    duplicate=deepcopy(first);duplicate['requestId']='duplicate'
    with pytest.raises(ValueError,match='without explicit'): successful_stage_calls([first,duplicate])
