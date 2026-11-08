"""Preflight and isolation checks for the installed Python reference recipes."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import run_python_sdk as runner
from test_runtime_build import VERSION, WHEEL, jar, sdk_wheel


def arguments(tmp_path, recipe='standard'):
    executable = tmp_path / 'sidecar.jar'
    jar(executable, [VERSION])
    return argparse.Namespace(recipe=recipe, sidecar_jar=executable,
        python_sdk_wheel=sdk_wheel(tmp_path / WHEEL), output=tmp_path / 'result',
        sidecar_checkout=tmp_path)


def test_preflight_rejects_ambiguous_output_and_invalid_artifact(tmp_path, monkeypatch):
    args = arguments(tmp_path)
    monkeypatch.setattr(subprocess, 'run', lambda *a, **k: pytest.fail('Preflight must run first'))
    args.output.mkdir()
    with pytest.raises(ValueError, match='new result directory'):
        runner.run(args)
    args.output.rmdir()
    args.python_sdk_wheel.write_bytes(b'invalid')
    with pytest.raises(ValueError, match='wheel archive'):
        runner.run(args)
    assert not args.output.exists()


@pytest.mark.parametrize('recipe', ['local', 'standard', 'hardened'])
def test_reference_topology_has_private_isolated_network_and_no_provider(tmp_path, recipe):
    document = runner.composition(tmp_path, 'test-unique', recipe, 'http://example.test')
    assert document['networks'] == {'reference': {'internal': True}}
    services = document['services']
    assert all('ports' not in service for service in services.values())
    assert all('provider' not in str(service.get('environment', {})).lower()
               and 'api_key' not in str(service.get('environment', {})).lower()
               for service in services.values())
    assert all('/signing' not in str(service.get('volumes', []))
               for name, service in services.items() if name != 'app')
    assert any(mount.endswith(':/trust:ro') for mount in services['sidecar']['volumes'])
    if recipe == 'standard':
        assert services['submit-fault']['network_mode'] == 'service:sidecar'
        assert services['callback-fault']['network_mode'] == 'service:app'
    if recipe == 'hardened':
        assert services['sidecar']['network_mode'] == 'service:sidecar-proxy'
        assert services['app']['network_mode'] == 'service:app-proxy'
        assert 'volumes' not in services['outsider']


def test_probe_and_cleanup_failures_are_reported(tmp_path, monkeypatch):
    args = arguments(tmp_path)
    monkeypatch.setattr(runner, 'configure',
                        lambda root, *unused: ((root / 'image').mkdir() or 'https://sidecar:8443'))
    monkeypatch.setattr(subprocess, 'check_output', lambda *a, **k: 'test-revision\n')
    commands = []
    def execute(command, **kwargs):
        commands.append(command)
        if 'exec' in command:
            return subprocess.CompletedProcess(command, 0, stdout='{"probeFailure":{"type":"AssertionError"}}')
        if 'down' in command:
            raise subprocess.CalledProcessError(1, command)
        return subprocess.CompletedProcess(command, 0)
    monkeypatch.setattr(subprocess, 'run', execute)
    with pytest.raises(SystemExit, match='recipe failed'):
        runner.run(args)
    report = json.loads((args.output / 'report.json').read_bytes())
    assert report['status'] == report['cleanup'] == 'FAIL'
    assert report['phase'] == 'probe'
    assert report['probeFailure'] == {'type': 'AssertionError'}
    assert report['project'].startswith('sdk-python-standard-')
    assert next(command for command in commands if 'down' in command)[3] == report['project']
