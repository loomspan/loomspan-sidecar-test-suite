"""Isolation must never fall back to the retained project's ports or containers."""
import json
import pytest
import environment
import configure_isolated


def test_retained_defaults_are_unchanged(monkeypatch, tmp_path):
    monkeypatch.setattr(environment, 'ROOT', tmp_path)
    assert environment.issuer() == 'http://localhost:18080/realms/equipment'
    assert environment.port(18765) == 18765
    command = environment.execute('java', 'sha256sum', '/app/app.jar')
    assert command[command.index('-p') + 1] == 'equipment-acceptance'
    assert command[-5:] == ['exec', '-T', 'java', 'sha256sum', '/app/app.jar']


def test_isolated_target_has_distinct_ports_and_provider_disabled(monkeypatch, tmp_path):
    monkeypatch.setattr(environment, 'ROOT', tmp_path)
    monkeypatch.setattr('sys.argv', ['configure_isolated', '--project', 'equipment-clean', '--port-offset', '10000'])
    configure_isolated.main()
    assert environment.issuer() == 'http://localhost:28080/realms/equipment'
    assert environment.port(18765) == 28765
    overlay = (tmp_path / '.runtime/compose.isolated.yaml').read_text()
    for port in [28080, 28081, 28082, 28083, 28090, 29091]:
        assert f'127.0.0.1:{port}:' in overlay
    assert 'OPENROUTER_API_KEY: ""' in overlay
    assert overlay.count('ports: !override') == 5
    command = environment.execute('sidecar', 'printenv', 'LOOMSPAN_SKILLS_LOCATIONS')
    assert command[command.index('-p') + 1] == 'equipment-clean'
    assert str(tmp_path / '.runtime/compose.isolated.yaml') in command
    assert not (tmp_path / '.runtime/secrets.json').exists()


@pytest.mark.parametrize('project,offset', [('equipment-acceptance', 10000), ('equipment-clean', 0), ('../retained', 10000)])
def test_inconsistent_target_fails_closed(monkeypatch, tmp_path, project, offset):
    monkeypatch.setattr(environment, 'ROOT', tmp_path)
    (tmp_path / '.runtime').mkdir()
    (tmp_path / '.runtime/environment.json').write_text(json.dumps({'project': project, 'portOffset': offset}))
    with pytest.raises(ValueError):
        environment.compose()


def test_missing_overlay_cannot_use_default_ports(monkeypatch, tmp_path):
    monkeypatch.setattr(environment, 'ROOT', tmp_path)
    (tmp_path / '.runtime').mkdir()
    (tmp_path / '.runtime/environment.json').write_text(json.dumps({'project': 'equipment-clean', 'portOffset': 10000}))
    with pytest.raises(ValueError, match='overlay missing'):
        environment.compose()


def test_configure_refuses_existing_runtime(monkeypatch, tmp_path):
    monkeypatch.setattr(environment, 'ROOT', tmp_path)
    (tmp_path / '.runtime').mkdir()
    marker = tmp_path / '.runtime/keep'
    marker.write_text('retained')
    monkeypatch.setattr('sys.argv', ['configure_isolated', '--project', 'equipment-clean', '--port-offset', '10000'])
    with pytest.raises(ValueError, match='new workspace'):
        configure_isolated.main()
    assert marker.read_text() == 'retained'
