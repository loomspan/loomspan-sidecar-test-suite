"""Explicit per-workspace Compose target; defaults preserve the retained stack."""
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def settings():
    file = ROOT / '.runtime/environment.json'
    value = json.loads(file.read_bytes()) if file.exists() else {'project': 'equipment-acceptance', 'portOffset': 0}
    project, offset = value['project'], value['portOffset']
    if not re.fullmatch(r'[a-z0-9][a-z0-9_-]*', project) or type(offset) is not int or not 0 <= offset <= 40000:
        raise ValueError('Invalid isolated Compose target')
    if (project == 'equipment-acceptance') != (offset == 0):
        raise ValueError('An isolated project requires isolated ports')
    return value


def port(original):
    return original + settings()['portOffset']


def url(original, path='', host='127.0.0.1'):
    return f'http://{host}:{port(original)}{path}'


def issuer():
    return url(18080, '/realms/equipment', 'localhost')


def compose():
    value = settings()
    command = ['docker', 'compose', '--project-directory', str(ROOT), '-p', value['project'],
               '--env-file', str(ROOT / '.runtime/compose.env')]
    for name in ['compose.yaml', 'compose.snapshot.yaml', 'compose.offline.yaml']:
        command += ['-f', str(ROOT / name)]
    if value.get('runtimeMode') == 'supplied-artifacts':
        command += ['-f', str(ROOT / 'compose.onprem.yaml')]
    if value['portOffset']:
        overlay = ROOT / '.runtime/compose.isolated.yaml'
        if not overlay.is_file():
            raise ValueError('Isolated Compose overlay missing; refusing default ports')
        command += ['-f', str(overlay)]
    return command


def execute(service, *args):
    return compose() + ['exec', '-T', service, *args]


def services():
    raw = subprocess.check_output(compose() + ['ps', '--format', 'json'], text=True)
    raw = raw.strip()
    return json.loads(raw) if raw.startswith('[') else [json.loads(line) for line in raw.splitlines() if line]


def runtime_identity():
    return {'composeProject': settings()['project'], 'portOffset': settings()['portOffset'], 'issuer': issuer()}
