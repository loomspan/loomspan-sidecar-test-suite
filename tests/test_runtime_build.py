"""Portable package validation uses declared coordinates and package integrity."""
import hashlib
import json
from pathlib import Path
import sys
import zipfile
import yaml

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from record_build import framework_identity
from install_runtime import verify_inputs
import record_build

VERSION = '1.0.0-beta.9-SNAPSHOT'


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
    manifest = {'buildReference': {'framework': VERSION, 'artifacts': artifacts,
        'configurationSha256': {'config.yaml': digest(config)}}, 'sourceSha256': {'config.yaml': digest(config)}}
    (tmp_path/'runtime-artifacts/manifest.json').write_text(json.dumps(manifest))
    assert verify_inputs(tmp_path) == manifest
    config.write_text('changed: true')
    with pytest.raises(ValueError, match='mismatch'):
        verify_inputs(tmp_path)


def test_record_build_stages_current_checkout_without_framework_source(tmp_path, monkeypatch):
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
    monkeypatch.setattr(sys, 'argv', ['record_build.py', '--sidecar-checkout', str(checkout)])
    record_build.main()
    assert (root/'runtime-artifacts/sidecar.jar').read_bytes() == built.read_bytes()
    baseline = json.loads((root/'.runtime/build-baseline.json').read_bytes())
    assert baseline['framework'] == VERSION and baseline['sidecar'] == '1.0.0-beta.4-SNAPSHOT'
    assert set(baseline['configurationSha256']) == {'compose.runtime.yaml', 'config/java.yaml', 'config/sidecar.yaml'}
