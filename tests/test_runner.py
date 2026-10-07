"""Small provider-free runner tests; no historical captures or live credentials."""
from contextlib import contextmanager
import copy
import json
from pathlib import Path
import sys
import zipfile

import httpx
import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import run_suite as runner
import scenarios


@pytest.fixture
def root(tmp_path, monkeypatch):
    (tmp_path / '.runtime').mkdir()
    (tmp_path / 'config/skills').mkdir(parents=True)
    (tmp_path / 'config/skills/example.yaml').write_text('name: example\nthinking_level: medium\ninput_bindings: {}\n')
    config = {'loomspan': {'models': {'reasoning': {'provider-model': 'old/model', 'thinking-levels': ['medium']}}, 'session': {'mission-timeout': '2400s'}}}
    for name in ['java', 'sidecar']:
        (tmp_path / 'config' / (name + '.yaml')).write_text(yaml.safe_dump(config))
    monkeypatch.setattr(runner, 'ROOT', tmp_path)
    monkeypatch.delenv('LOOMSPAN_RUN_OVERLAY', raising=False)
    monkeypatch.delenv('LOOMSPAN_MODEL_CONFIG_DIRECTORY', raising=False)
    return tmp_path


def test_mock_and_preview_never_touch_runtime(monkeypatch, capsys):
    monkeypatch.setattr(runner, 'ready', lambda: pytest.fail('Must not access runtime'))
    monkeypatch.delenv('LOOMSPAN_OPENROUTER_API_KEY', raising=False)
    assert runner.main(['mock', '--dry-run']) == 0
    preview = json.loads(capsys.readouterr().out)
    assert preview['paidCalls'] == 0 and len(preview['scenarios']) == 4
    for mode in ['live', 'capture', 'evaluate']:
        assert runner.main([mode, '--model', 'test/model', '--dry-run']) == 0
        selection = json.loads(capsys.readouterr().out)
        assert selection['paths'] == (['java'] if mode == 'evaluate' else ['java', 'sidecar'])
        assert selection['scenarios'] == ['baseline', 'priority']


def test_preflight_requires_model_key_and_evaluate_only_path(monkeypatch):
    monkeypatch.delenv('LOOMSPAN_OPENROUTER_API_KEY', raising=False)
    for args in [['evaluate'], ['evaluate', '--model', 'test/model'], ['live', '--path', 'java', '--model', 'test/model']]:
        with pytest.raises(SystemExit) as error:
            runner.main(args)
        assert error.value.code == 2


@pytest.mark.parametrize('reasoning', ['medium', 'none'])
def test_overlay_changes_only_model_settings_and_never_authored_files(root, reasoning):
    before = {p: p.read_bytes() for p in (root / 'config').rglob('*.yaml')}
    directory = root / '.runtime/overlay'
    directory.mkdir()
    file = runner.make_overlay(directory, ['java', 'sidecar'], 'test/model', reasoning)
    overlay = yaml.safe_load(file.read_bytes())
    assert '${LOOMSPAN_OPENROUTER_API_KEY' in overlay['services']['fixtures']['environment']['OPENROUTER_API_KEY']
    for name in ['java', 'sidecar']:
        current = yaml.safe_load((directory / (name + '.yaml')).read_bytes())
        original = yaml.safe_load(before[root / 'config' / (name + '.yaml')])
        original['loomspan']['models']['reasoning'] = {'provider-model': 'test/model', 'thinking-levels': [] if reasoning == 'none' else ['medium']}
        assert current == original
    assert ('thinking_level:' in (directory / 'skills/example.yaml').read_text()) == (reasoning != 'none')
    assert all(p.read_bytes() == raw for p, raw in before.items())


@pytest.mark.parametrize('failure', ['none', 'startup', 'body', 'interrupt', 'restore'])
def test_runtime_restores_after_startup_body_or_interrupt(root, monkeypatch, failure):
    commands = []
    offline = []
    monkeypatch.setattr(runner.environment, 'compose', lambda: ['compose', 'live' if runner.os.getenv('LOOMSPAN_RUN_OVERLAY') else 'normal'])
    def command(args):
        commands.append(args)
        if (failure == 'startup' and len(commands) == 1) or (failure == 'restore' and len(commands) == 2):
            raise RuntimeError(failure)
    monkeypatch.setattr(runner, 'command', command)
    monkeypatch.setattr(runner, 'ready', lambda: None)
    monkeypatch.setattr(runner, 'verify_mounted', lambda *args: None)
    monkeypatch.setattr(runner, 'require_offline_provider', lambda: offline.append(True))
    report = {}
    directory = root / '.runtime/overlay'
    directory.mkdir()
    def run():
        with runner.live_runtime(directory, ['java'], 'test/model', 'medium', report):
            if failure == 'body':
                raise RuntimeError('body')
            if failure == 'interrupt':
                raise KeyboardInterrupt()
    if failure == 'none':
        run()
    else:
        with pytest.raises(KeyboardInterrupt if failure == 'interrupt' else RuntimeError):
            run()
    assert commands[-1][1] == 'normal'
    assert not runner.os.getenv('LOOMSPAN_RUN_OVERLAY')
    assert report['runtimeRestored'] == (failure != 'restore')
    assert len(offline) == (1 if failure == 'restore' else 2)


def test_lock_excludes_concurrent_runner_and_releases_after_failure(root):
    with pytest.raises(ValueError):
        with runner.run_lock():
            with pytest.raises(RuntimeError, match='lock exists'):
                with runner.run_lock():
                    pytest.fail('Concurrent runner entered')
            raise ValueError('run failed')
    assert not (root / '.runtime/run-suite.lock').exists()


def test_bundle_rejects_secrets_and_replaces_only_report_files(tmp_path):
    bundle = runner.Bundle(['private-token'])
    with pytest.raises(ValueError, match='Credential'):
        bundle.add('bad.json', {'token': 'private-token'})
    assert 'private-token' not in bundle.error(ValueError('private-token'))
    sentinel = tmp_path / 'accepted.json'
    sentinel.write_text('keep')
    report = {'runId': 'one', 'mode': 'capture', 'status': 'FAIL', 'cases': [], 'runtimeRestored': True}
    runner.write_report(report, bundle, tmp_path)
    with zipfile.ZipFile(tmp_path / 'bundle.zip') as archive:
        hashes = json.loads(archive.read('checksums.json'))
        assert all(runner.digest(archive.read(name)) == sha for name, sha in hashes.items())
        assert json.loads(archive.read('report.json')) == report
    assert sentinel.read_text() == 'keep'


def test_usage_missing_cost_is_unknown_and_fenced_response_is_not_failure():
    events = [{'event': 'model-request'}, {'event': 'model-response', 'response': {'choices': [{'message': {'content': '```json\n{}\n```'}}]}}]
    value = runner.usage(events, [])
    assert value['reportedCost'] is None
    assert value['failedModelAttempts'] == 0
    assert value['rejectedActions'] == 0


def sample():
    case = 'case-test'
    quotes = [{'caseId': case, 'option': 'standard'}, {'caseId': case, 'option': 'expedited'}]
    value = {'caseId': case, 'assetId': 'asset', 'quotes': quotes,
             'equipmentAssessment': {'cause': 'unknown', 'reportedIncident': 'Original incident'},
             'optionAssessments': {option: {'offerExpiresAt': 'deadline', 'offerReserved': False,
                                           'offerSourceId': 'source', 'accessCondition': 'unresolved'}
                                   for option in ['expedited', 'standard', 'loaner', 'replacement']}}
    value.update({k: 'present' for k in ['disposition', 'selectedOption', 'rationale', 'alternatives', 'uncertainty', 'acceptedRisk', 'nextDecision', 'citations']})
    value.update(selectedOption='expedited', pursuedOptions=['expedited', 'loaner'], reviewConcerns=[])
    for option in ['expedited', 'standard']:
        value['optionAssessments'][option].update(
            chargeCondition='Conditional charges', scopeChangeCondition='Renew approval',
            coverageReviewCondition='Pending review', dispatchOwnerSourceIds=['dispatch'],
            coverageReviewerSourceIds=['review'],
            ownerDirectory=[{'id': 'dispatch', 'responsibility': 'Dispatch'},
                            {'id': 'review', 'responsibility': 'Coverage review'}])
    rows = {'quotes': [{'body': json.dumps(q)} for q in quotes], 'assessments': [{'body': json.dumps(value)}], 'requests': []}
    trace = [{'recordType': 'TOOL_CALL_COMPLETED', 'route': skill, 'timestamp': i,
              'data': {'details': {'result': json.dumps(output)}}}
             for i, (skill, output) in enumerate([('assessEquipment', value['equipmentAssessment']), ('compareOptions', value)])]
    extra = [{'recordType': 'TOOL_CALL_STARTED', 'route': 'assessEquipment',
              'data': {'details': {'arguments': {'context': {'incident': 'Original incident'}}}}}]
    for option, output in value['optionAssessments'].items():
        skill = 'assess' + option.title() + 'Feasibility'
        context = copy.deepcopy(output)
        context['offer'] = {'expiresAt': context.pop('offerExpiresAt'),
                            'reserved': context.pop('offerReserved'),
                            'sourceId': context.pop('offerSourceId')}
        if 'ownerDirectory' in output:
            context['assetContext'] = {'contacts': copy.deepcopy(output['ownerDirectory'])}
        extra.extend([
            {'recordType': 'TOOL_CALL_STARTED', 'route': skill,
             'data': {'details': {'arguments': {'context': context}}}},
            {'recordType': 'TOOL_CALL_COMPLETED', 'route': skill,
             'data': {'details': {'result': copy.deepcopy(output)}}}])
    for record in extra:
        record['timestamp'] = 0
    return value, rows, extra + trace


@pytest.mark.parametrize('mutation', ['omitted', 'restated', 'metadata', 'incident'])
def test_publication_checks_detect_loss_or_rewriting(mutation):
    value, _, trace = sample()
    assert all(scenarios.publication_checks(value, trace).values())
    if mutation == 'omitted':
        del value['optionAssessments']['expedited']
    elif mutation == 'restated':
        value['optionAssessments']['expedited']['accessCondition'] = 'resolved'
    elif mutation == 'metadata':
        value['optionAssessments']['expedited']['offerExpiresAt'] = 'unknown'
    else:
        value['equipmentAssessment']['reportedIncident'] = 'rewritten'
    assert not all(scenarios.publication_checks(value, trace).values())


@pytest.mark.parametrize('selected,options,valid', [
    ('expedited', ['expedited', 'loaner'], True),
    ('expedited', ['loaner'], False),
    ('expedited', ['expedited', 'expedited'], False),
    ('loaner', ['loaner', 'invented'], False),
    ('defer', [], True),
    ('undecided', ['loaner'], False),
    ('loaner', 'loaner', False),
])
def test_portfolio_selection_consistency(selected, options, valid):
    assert scenarios.portfolio_valid({'selectedOption': selected, 'pursuedOptions': options}) is valid


@pytest.mark.parametrize('mutation,expected', [
    ('none', (True, True)), ('missing', (False, True)), ('blank', (False, True)),
    ('foreign', (True, False)), ('duplicate', (True, False)),
    ('directory', (True, False)), ('wrong_role', (True, True)), ('empty', (True, True)),
])
def test_service_conditions_check_structure_not_semantic_role(mutation, expected):
    value, _, _ = sample()
    published = value['optionAssessments']['expedited']
    context = {'assetContext': {'contacts': copy.deepcopy(published['ownerDirectory'])}}
    if mutation == 'missing':
        del published['scopeChangeCondition']
    elif mutation == 'blank':
        published['chargeCondition'] = ' '
    elif mutation == 'foreign':
        published['coverageReviewerSourceIds'] = ['invented']
    elif mutation == 'duplicate':
        published['coverageReviewerSourceIds'] = ['review', 'review']
    elif mutation == 'directory':
        published['ownerDirectory'][1]['name'] = 'Invented name'
    elif mutation == 'wrong_role':
        published['coverageReviewerSourceIds'] = ['dispatch']
    elif mutation == 'empty':
        published['coverageReviewerSourceIds'] = []
    assert scenarios.service_conditions(published, context) == expected


def test_exact_preservation_detects_rewritten_child_or_quote():
    value, rows, trace = sample()
    terminal = {'status': 'COMPLETED', 'result': json.dumps(value)}
    assert all(scenarios.review(terminal, value, rows, trace).values())
    changed = copy.deepcopy(value)
    changed['quotes'][0]['extra'] = 'invented'
    checks = scenarios.review({'status': 'COMPLETED', 'result': json.dumps(changed)}, value, rows, trace)
    assert not checks['authoritative quotes exact, without omissions or duplicates']
    assert not checks['compareOptions accepted result preserved exactly']


def test_trace_payload_rejects_duplicate_chunks():
    record = {'metadata': {'payloadId': 'p', 'chunkCount': 2}}
    chunks = [{'recordType': 'PAYLOAD_CHUNK_APPENDED', 'metadata': {'payloadId': 'p', 'chunkIndex': 0}, 'data': '{}'}] * 2
    with pytest.raises(ValueError):
        scenarios.payload(record, chunks)


def test_execute_case_collects_real_shape_and_accepted_fenced_plan(monkeypatch):
    value, rows, trace = sample()
    case = value['caseId']
    monkeypatch.setattr(runner.uuid, 'uuid4', lambda: type('ID', (), {'hex': 'test'})())
    case = 'case-java-test'
    value['caseId'] = case
    for q in value['quotes']:
        q['caseId'] = case
    rows['quotes'] = [{'body': json.dumps(q)} for q in value['quotes']]
    rows['assessments'] = [{'body': json.dumps(value)}]
    trace[-1]['data']['details']['result'] = json.dumps(value)
    trace.append({'recordType': 'PLAN_CREATED', 'timestamp': 2, 'data': {'capabilityName': 'resolveEquipment', 'tasks': []}})
    events = [{'event': 'model-request', 'caseId': case, 'requestId': 'r', 'request': {'model': 'test/model'}},
              {'event': 'model-response', 'caseId': case, 'requestId': 'r', 'status': 200,
               'response': {'usage': {'cost': .01, 'prompt_tokens': 100, 'completion_tokens': 10},
                            'choices': [{'message': {'content': '```json\n{}\n```'}}]}}]
    states = iter([{'assessments': [], 'quotes': [], 'requests': []}, rows])
    monkeypatch.setattr(runner, 'database', lambda _: next(states))
    monkeypatch.setattr(scenarios, 'inputs', lambda *args: {'caseId': case, 'assetId': 'asset'})
    def handle(request):
        path = request.url.path
        if path.endswith('/artifact'):
            raw = b'\n'.join(json.dumps(r).encode() for r in trace)
            return httpx.Response(200, content=raw)
        if path.endswith('/traces'):
            return httpx.Response(200, json={'items': [{'entrySkill': 'resolveEquipment', 'traceId': 'trace'}]})
        if path == '/control/journal':
            return httpx.Response(200, json=events)
        if path == '/assessments/id':
            return httpx.Response(200, json={'status': 'COMPLETED', 'result': json.dumps(value)})
        return httpx.Response(200, json={'id': 'id'})
    bundle = runner.Bundle(['private-auth-56789', 'control-secret', 'observer-secret'])
    with httpx.Client(transport=httpx.MockTransport(handle)) as client:
        result = runner.execute_case(client, 'baseline', 'java', 'private-auth-56789', {'control': 'control-secret', 'observer': 'observer-secret'}, bundle, 30, 'test/model')
    assert result['status'] == 'CHECKS_PASS_REVIEW_REQUIRED', result
    assert result['usage']['reportedCost'] == .01
    assert 'baseline/java/accepted-plans.json' in bundle.files


@pytest.mark.parametrize('mode,failure', [('evaluate', False), ('live', False), ('capture', False), ('evaluate', True)])
def test_cli_publishes_report_and_restores_without_external_services(root, monkeypatch, mode, failure):
    (root / 'fixtures').mkdir()
    (root / 'scripts').mkdir()
    for name in ['fixtures/base-case.json', 'fixtures/business.json', 'fixtures/server.py', 'scripts/scenarios.py', 'scripts/run_suite.py']:
        (root / name).write_text('{}')
    (root / '.runtime/secrets.json').write_text(json.dumps({'control': 'private-control-value', 'observer': 'private-observer-value'}))
    monkeypatch.setenv('LOOMSPAN_OPENROUTER_API_KEY', 'private-provider-value')
    monkeypatch.setattr(runner, 'ready', lambda: None)
    monkeypatch.setattr(runner, 'require_offline_provider', lambda: True)
    monkeypatch.setattr(runner, 'verify_mounted', lambda *a: None)
    monkeypatch.setattr(runner, 'baseline', lambda: {'missionTimeoutSeconds': 2400})
    monkeypatch.setattr(runner.subprocess, 'check_output', lambda *a, **kw: 'commit\n')
    monkeypatch.setattr(runner, 'login', lambda user: 'private-login-value')
    commands = []
    monkeypatch.setattr(runner, 'command', lambda args: commands.append((bool(runner.os.getenv('LOOMSPAN_RUN_OVERLAY')), args)))
    def execute(client, name, path, *args):
        if failure:
            raise RuntimeError('private-provider-value interruption')
        return {'scenario': name, 'path': path, 'checks': {'synthetic test': True},
                'usage': {'modelCalls': 0, 'reportedCost': None}, 'status': 'CHECKS_PASS_REVIEW_REQUIRED'}
    monkeypatch.setattr(runner, 'execute_case', execute)
    assert runner.main([mode, '--model', 'test/model']) == (1 if failure else 0)
    report = json.loads((root / 'evidence/latest/report.json').read_bytes())
    assert report['runtimeRestored'] is True
    assert report['replayApproved'] is False
    assert report['captureCandidate'] == (mode == 'capture')
    assert [enabled for enabled, _ in commands] == [True, False]
    assert not (root / '.runtime/run-suite.lock').exists()
    assert not list((root / '.runtime').glob('runner-*'))
    assert 'private-provider-value' not in json.dumps(report)
    if not failure:
        assert len(report['cases']) == (2 if mode == 'evaluate' else 4)
    with zipfile.ZipFile(root / 'evidence/latest/bundle.zip') as archive:
        assert ('candidate-review.json' in archive.namelist()) == (mode == 'capture')


def test_mixed_overlay_preserves_contracts_and_both_hosts(root):
    source = root / 'config/skills/example.yaml'
    source.write_text('name: example\nmodel: reasoning\nthinking_level: medium\nprompt: Keep business method\ninput_bindings: {}\n')
    before = source.read_bytes()
    directory = root / '.runtime/mixed'
    directory.mkdir()
    runner.make_overlay(directory, ['java', 'sidecar'], 'test/lower', 'medium', {'example': 'test/stronger'})
    effective = yaml.safe_load((directory / 'skills/example.yaml').read_bytes())
    original = yaml.safe_load(before)
    original['model'] = 'trial-example'
    assert effective == original
    assert source.read_bytes() == before
    for host in ['java', 'sidecar']:
        models = yaml.safe_load((directory / (host + '.yaml')).read_bytes())['loomspan']['models']
        assert models['reasoning']['provider-model'] == 'test/lower'
        assert models['trial-example']['provider-model'] == 'test/stronger'
        assert models['trial-example']['thinking-levels'] == ['medium']


def test_mixed_routing_check_rejects_swapped_skills_even_with_same_model_counts():
    calls = [{'request': {'model': m}} for m in ['test/lower', 'test/stronger']]
    def request(skill, model):
        return {'recordType': 'MODEL_REQUEST_SENT', 'metadata': {'skillName': skill, 'providerModel': model}}
    trace = [request('parent', 'test/lower'), request('expert', 'test/stronger')]
    assert runner.model_assignment_matches(calls, trace, 'test/lower', {'expert': 'test/stronger'})
    swapped = [request('parent', 'test/stronger'), request('expert', 'test/lower')]
    assert not runner.model_assignment_matches(calls, swapped, 'test/lower', {'expert': 'test/stronger'})
    assert not runner.model_assignment_matches(calls, trace[:1], 'test/lower', {'expert': 'test/stronger'})


def test_invalid_mixed_override_stops_before_runtime(root, monkeypatch):
    monkeypatch.setattr(runner, 'ready', lambda: pytest.fail('Must not access runtime'))
    for value in ['missing=test/model', '../example=test/model', 'example=', 'example']:
        with pytest.raises(SystemExit):
            runner.main(['evaluate', '--model', 'test/lower', '--skill-model', value, '--dry-run'])


def test_trial_overrides_replace_selected_pack_aliases(root):
    # A whole-tree trial must not silently retain a coordinator's normal model.
    skill = root / 'config/skills/example.yaml'
    skill.write_text('name: example\nmodel: coordination\nthinking_level: medium\n')
    directory = root / '.runtime/selected-pack-trial'
    directory.mkdir()
    runner.make_overlay(directory, ['java'], 'test/whole-tree', 'medium')
    generated = yaml.safe_load((directory / 'skills/example.yaml').read_bytes())
    config = yaml.safe_load((directory / 'java.yaml').read_bytes())
    assert config['loomspan']['models'][generated['model']]['provider-model'] == 'test/whole-tree'
    assert yaml.safe_load(skill.read_bytes())['model'] == 'coordination'
