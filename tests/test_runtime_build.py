"""Portable package validation uses declared coordinates and package integrity."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile
import yaml

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from record_build import framework_identity, wheel_identity
from install_runtime import verify_inputs
import baseline as runtime_baseline
import record_build

VERSION = '1.0.0-beta.9-SNAPSHOT'
WHEEL = 'loomspan_sdk-0.1.0.dev0-py3-none-any.whl'


def sdk_wheel(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, 'w') as archive:
        info = 'loomspan_sdk-0.1.0.dev0.dist-info/'
        archive.writestr(info + 'METADATA', 'Name: loomspan-sdk\nVersion: 0.1.0.dev0\n')
        archive.writestr(info + 'WHEEL', 'Tag: py3-none-any\n')
        archive.writestr(info + 'RECORD', '')
    return path


def jar(path, versions):
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, 'w') as archive:
        for version in versions:
            archive.writestr('BOOT-INF/lib/loomspan-spring-boot-starter-'+version+'.jar', b'framework')


@pytest.mark.parametrize('versions', [[], ['1.0.0-beta.8'], [VERSION, '1.0.0-beta.8']])
def test_missing_mixed_or_wrong_coordinate_rejected(tmp_path, versions):
    jar(tmp_path/'app.jar', versions)
    with pytest.raises(ValueError, match='coordinate'):
        framework_identity(tmp_path/'app.jar', VERSION)


def test_portable_manifest_validates_actual_framework_and_all_inputs(tmp_path):
    config = tmp_path/'config.yaml'
    config.write_text('test: true')
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    artifacts = {}
    for host in ('java', 'sidecar'):
        path = tmp_path/f'runtime-artifacts/{host}.jar'
        jar(path, [VERSION])
        artifacts[host] = {'sha256': digest(path), 'frameworkSha256': framework_identity(path, VERSION)}
    wheel = sdk_wheel(tmp_path/'runtime-artifacts/python-sdk'/WHEEL)
    artifacts['pythonSdk'] = wheel_identity(wheel)
    manifest = {'buildReference': {'framework': VERSION, 'artifacts': artifacts,
        'configurationSha256': {'config.yaml': digest(config)}}, 'sourceSha256': {'config.yaml': digest(config)}}
    (tmp_path/'runtime-artifacts/manifest.json').write_text(json.dumps(manifest))
    assert verify_inputs(tmp_path) == manifest
    second = sdk_wheel(wheel.with_name('other.whl'))
    with pytest.raises(ValueError, match='wheel identity mismatch'):
        verify_inputs(tmp_path)
    second.unlink()
    original = wheel.read_bytes()
    wheel.write_bytes(original + b'tampered')
    with pytest.raises(ValueError, match='wheel identity mismatch'):
        verify_inputs(tmp_path)
    wheel.unlink()
    with pytest.raises(ValueError, match='wheel identity mismatch'):
        verify_inputs(tmp_path)
    wheel.write_bytes(original)
    config.write_text('changed: true')
    with pytest.raises(ValueError, match='mismatch'):
        verify_inputs(tmp_path)


@pytest.mark.parametrize('junction', [
    None,
    pytest.param('runtime-artifacts', marks=pytest.mark.skipif(sys.platform != 'win32', reason='Windows junction')),
    pytest.param('runtime-artifacts/python-sdk',
                 marks=pytest.mark.skipif(sys.platform != 'win32', reason='Windows junction')),
])
def test_record_build_stages_current_checkout_without_framework_source(tmp_path, monkeypatch, junction):
    root, checkout = tmp_path/'suite', tmp_path/'sidecar'
    checkout.mkdir()
    (checkout/'pom.xml').write_text('<project xmlns="http://maven.apache.org/POM/4.0.0">'
        '<version>1.0.0-beta.4-SNAPSHOT</version><properties>'
        f'<loomspan.version>{VERSION}</loomspan.version></properties></project>')
    built = checkout/'target/loomspan-sidecar-1.0.0-beta.4-SNAPSHOT.jar'
    jar(built, [VERSION])
    jar(root/'apps/java/target/equipment-java-1.0.jar', [VERSION])
    (root/'.runtime').mkdir()
    (root/'config').mkdir()
    for host in ('java', 'sidecar'):
        (root/f'config/{host}.yaml').write_text('loomspan:\n  session:\n    quotas:\n      max-usage-units: 400000\n')
    (root/'compose.runtime.yaml').write_text(yaml.safe_dump({'services': {
        host: {'environment': {'LOOMSPAN_CONNECTIONS_MODEL_REQUESTTIMEOUT': '480s',
            'LOOMSPAN_SESSION_MISSIONTIMEOUT': '2400s'}} for host in ('java', 'sidecar')}}))
    monkeypatch.setattr(record_build, 'ROOT', root)
    source_wheel = sdk_wheel(tmp_path/WHEEL)
    monkeypatch.setattr(sys, 'argv', ['record_build.py', '--sidecar-checkout', str(checkout),
                                     '--python-sdk-wheel', str(source_wheel)])
    if junction is not None:
        linked = root / junction
        linked.parent.mkdir(parents=True, exist_ok=True)
        outside = tmp_path / 'other-artifacts'
        outside.mkdir()
        subprocess.run(['cmd.exe', '/d', '/c', 'mklink', '/J', str(linked), str(outside)],
                       check=True, capture_output=True)
        external_wheel = outside / (root / record_build.PYTHON_SDK_DIR).relative_to(linked) / WHEEL
        sdk_wheel(external_wheel)
        original = external_wheel.read_bytes() + b'unchanged external artifact'
        external_wheel.write_bytes(original)
        with pytest.raises(ValueError, match='Unsafe staged Loomspan SDK directory'):
            record_build.main()
        assert external_wheel.read_bytes() == original
        assert not (root / '.runtime/build-baseline.json').exists()
        return
    record_build.main()
    assert (root/'runtime-artifacts/sidecar.jar').read_bytes() == built.read_bytes()
    baseline = json.loads((root/'.runtime/build-baseline.json').read_bytes())
    assert (root/'runtime-artifacts/python-sdk'/WHEEL).read_bytes() == source_wheel.read_bytes()
    assert baseline['artifacts']['pythonSdk'] == {
        'filename': WHEEL, 'version': '0.1.0.dev0', 'sha256': hashlib.sha256(source_wheel.read_bytes()).hexdigest(),
    }
    assert baseline['framework'] == VERSION and baseline['sidecar'] == '1.0.0-beta.4-SNAPSHOT'
    assert set(baseline['configurationSha256']) == {'compose.runtime.yaml', 'config/java.yaml', 'config/sidecar.yaml'}


@pytest.mark.parametrize('stale_service', ['python', 'fixtures', None])
def test_runtime_baseline_checks_wheel_in_both_images(tmp_path, monkeypatch, stale_service):
    sdk = wheel_identity(sdk_wheel(tmp_path / WHEEL))
    build = {'artifacts': {'pythonSdk': sdk, 'java': {'sha256': 'java-hash'},
                          'sidecar': {'sha256': 'sidecar-hash'}},
             'providerRequestTimeoutSeconds': 60, 'missionTimeoutSeconds': 600}
    (tmp_path / '.runtime').mkdir()
    (tmp_path / '.runtime/build-baseline.json').write_text(json.dumps(build))
    monkeypatch.setattr(runtime_baseline, 'ROOT', tmp_path)
    monkeypatch.setattr(runtime_baseline.target_env, 'execute', lambda *args: args)
    monkeypatch.setattr(runtime_baseline.target_env, 'runtime_identity', lambda: {})
    monkeypatch.setattr(runtime_baseline.subprocess, 'check_output',
                        lambda args, **kwargs: f'{args[0]}-hash  {args[-1]}\n')
    checked = []

    def run(args, **kwargs):
        service, command, *_ = args
        if command == 'printenv':
            return subprocess.CompletedProcess(args, 1, '')
        assert args == (service, 'sha256sum', '--', '/sdk/' + WHEEL)
        checked.append(service)
        digest = 'stale-hash' if service == stale_service else sdk['sha256']
        return subprocess.CompletedProcess(args, 0, f'{digest}  {args[-1]}\n')

    monkeypatch.setattr(runtime_baseline.subprocess, 'run', run)
    if stale_service is None:
        assert runtime_baseline.baseline()['artifacts']['pythonSdk'] == sdk
        assert checked == ['python', 'fixtures']
    else:
        with pytest.raises(RuntimeError, match=f'Running {stale_service} SDK wheel differs'):
            runtime_baseline.baseline()
