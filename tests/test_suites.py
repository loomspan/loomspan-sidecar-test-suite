"""Suite selection, collision protection and adapter isolation, without providers."""
import asyncio
from dataclasses import replace
import json
from pathlib import Path
import sys

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT))
import run_suite as runner
from suite_config import prepare
from suites.registry import EQUIPMENT, SUITES


def test_all_rejects_unsupported_suite_before_running(monkeypatch):
    monkeypatch.setitem(SUITES, 'other', replace(EQUIPMENT, name='other', modes=('evaluate',)))
    monkeypatch.setattr(runner, 'run_selected', lambda *a: pytest.fail('Must validate every suite first'))
    with pytest.raises(SystemExit) as error:
        runner.main(['mock', '--suite', 'all'])
    assert error.value.code == 2


@pytest.mark.parametrize('selection', [['all', 'equipment-service'], ['equipment-service', 'all']])
def test_all_cannot_mix_with_names(selection):
    with pytest.raises(SystemExit):
        runner.main(['mock', '--dry-run', *[arg for name in selection for arg in ('--suite', name)]])


def test_suite_results_are_grouped_and_all_run_under_one_lock(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, 'ROOT', tmp_path)
    monkeypatch.delitem(SUITES, 'typesafe-ai')
    monkeypatch.setitem(SUITES, 'other', replace(EQUIPMENT, name='other'))
    calls = []
    def run(args, parser, suite):
        assert (tmp_path / '.runtime/run-suite.lock').exists()
        calls.append(suite.name)
        args.output.mkdir(parents=True)
        (args.output / 'report.json').write_text(json.dumps({'status': 'REPLAY_PASS', 'runtimeRestored': True}))
        return 0
    monkeypatch.setattr(runner, 'run_selected', run)
    monkeypatch.setenv('LOOMSPAN_OPENROUTER_API_KEY', 'test-only')
    assert runner.main(['evaluate', '--suite', 'all', '--model', 'test/model']) == 0
    assert calls == ['equipment-service', 'other']
    summary = (tmp_path / 'evidence/latest/summary.md').read_text()
    assert 'equipment-service/summary.md' in summary and 'other/summary.md' in summary
    assert not (tmp_path / '.runtime/run-suite.lock').exists()


def test_trial_does_not_change_other_suite_models_or_skills(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, 'ROOT', tmp_path)
    for suite, name in [('equipment-service', 'first'), ('other', 'second')]:
        file = tmp_path / f'config/skills/{suite}/{name}.yaml'
        file.parent.mkdir(parents=True)
        file.write_text(f'name: {name}\nmodel: reasoning\nthinking_level: medium\n')
    config = {'loomspan': {'models': {'reasoning': {'provider-model': 'normal/model', 'thinking-levels': ['medium']}}}}
    (tmp_path / 'config/java.yaml').write_text(yaml.safe_dump(config))
    directory = tmp_path / 'trial'
    directory.mkdir()
    runner.make_overlay(directory, ['java'], 'trial/model', 'low')
    effective = yaml.safe_load((directory / 'java.yaml').read_bytes())
    assert effective['loomspan']['models']['reasoning'] == config['loomspan']['models']['reasoning']
    assert (directory / 'skills/other/second.yaml').read_bytes() == (tmp_path / 'config/skills/other/second.yaml').read_bytes()
    first = yaml.safe_load((directory / 'skills/equipment-service/first.yaml').read_bytes())
    assert effective['loomspan']['models'][first['model']]['provider-model'] == 'trial/model'


def test_routes_combine_and_skill_collisions_fail(tmp_path):
    for suite in ('one', 'two'):
        skill = tmp_path / f'config/rest-skills/{suite}/{suite}.yaml'
        skill.parent.mkdir(parents=True)
        skill.write_text(f'name: {suite}\nrest: true\n')
        route = tmp_path / f'config/routes/{suite}.yaml'
        route.parent.mkdir(parents=True, exist_ok=True)
        route.write_text(yaml.safe_dump({'targets': {suite: {'base-url': 'http://python'}},
                                        'routes': {suite: {'target': suite, 'path': '/'+suite}}}))
    prepare(tmp_path)
    assert set(yaml.safe_load((tmp_path / '.runtime/suite-routes.yaml').read_bytes())['routes']) == {'one', 'two'}
    (tmp_path / 'config/rest-skills/two/two.yaml').write_text('name: one\nrest: true\n')
    with pytest.raises(ValueError, match='Duplicate runtime skill'):
        prepare(tmp_path)


def test_python_completion_dispatch_uses_one_poll(monkeypatch):
    monkeypatch.setenv('JWKS', 'http://unused.invalid/jwks')
    from apps.python import app as host
    from fastapi.responses import JSONResponse
    polls = []
    async def poll(ident, who):
        polls.append(ident)
        return JSONResponse({'status': 'COMPLETED', 'skillName': 'resolveEquipment', 'result': {}})
    monkeypatch.setattr(host, 'poll_execution', poll)
    monkeypatch.setattr(host.business, 'save_assessment', lambda *args: 'saved-version')
    result = asyncio.run(host.poll('execution', ({'sub': 'maya'}, 'Bearer test')))
    assert polls == ['execution']
    assert json.loads(result.body)['assessmentVersion'] == 'saved-version'
