"""Run a provider-free installed Python reference against the actual Sidecar."""
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory
from uuid import uuid4

import yaml

from record_build import VERSION, framework_identity, wheel_identity
from sdk_lane import remote_material

ROOT = Path(__file__).resolve().parents[1]
RESULTS = {
    'local': {'positive', 'rolesAndOwner', 'queuedExpiry', 'javaCredential', 'trustReload'},
    'standard': {'positive', 'invocationTls', 'callbackTls', 'submissionLoss', 'callbackLoss'},
    'hardened': {'positive', 'invocationMtls', 'callbackMtls', 'privateBackend'},
}
ROLE = 'ROLE_ORDER_EDITOR'
JAVA_OPTIONS = '-Xmx384m'


def dump(path, document):
    path.write_text(yaml.safe_dump(document), encoding='utf-8')


def configure(directory, checkout, recipe):
    material = directory / 'material'
    remote_material.generate(material)
    for name in ('public', 'trust', 'config', 'image', 'java'):
        (directory / name).mkdir()
    key = remote_material.public_jwk(material / 'signing/signer-key.pem')
    java = directory / 'java'
    if recipe == 'local':
        maven = shutil.which('mvn')
        if maven is None:
            raise ValueError('Maven is required to issue the local Java fixture credential')
        subprocess.run([maven, '-B', '-ntp', '-o', '-f', 'sdks/java/pom.xml', '-pl', 'core',
                        '-Dtest=JavaCallbackIssuanceFixtureTest#issueForRunningPython', 'test'],
                       cwd=checkout, env=dict(os.environ, LOOMSPAN_JAVA_LIVE_CALLBACK_FIXTURES=str(java)),
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True, timeout=180)
        [overlap] = json.loads((java / 'jwks.json').read_bytes())['keys']
    else:
        overlap = remote_material.public_jwk(material / 'replacement/signer-key.pem')
    (directory / 'trust/sidecar.json').write_text(json.dumps({'keys': [key, overlap]}), encoding='utf-8')
    (directory / 'trust/callback.json').write_text(json.dumps({'keys': [overlap]}), encoding='utf-8')

    backend = {'local': 'http://app:8081', 'standard': 'https://app:8443',
               'hardened': 'http://127.0.0.1:9080'}[recipe]
    sidecar = {'local': 'http://sidecar:8080', 'standard': 'https://sidecar:8443',
               'hardened': 'http://127.0.0.1:9080'}[recipe]
    targets = {'app': backend}
    if recipe == 'standard':
        targets |= {'wrongHost': 'https://app-wrong:8443', 'wrongCa': 'https://app:9444',
                    'loss': 'https://app:9443'}
    if recipe == 'hardened':
        targets |= {'wrongClient': 'http://127.0.0.1:9083', 'wrongCa': 'http://127.0.0.1:9084'}
    directory_config = directory / 'config'
    skills = [('referenceGet', 'GET', 'owned', 'app', ROLE),
              ('referencePost', 'POST', 'owned', 'app', ROLE)]
    if recipe == 'local':
        skills += [('referenceLiteral', 'POST', 'owned', 'app', 'ORDER_EDITOR'),
                   ('referenceBlock', 'POST', 'block', 'app', ROLE)]
    for target in targets:
        if target != 'app':
            skills.append(('reference' + target[0].upper() + target[1:], 'POST', 'owned', target, ROLE))
    for name, method, route, target, role in skills:
        dump(directory_config / (name + '.yaml'), {
            'name': name, 'description': 'Fixed offline Python reference callback',
            'input_schema': {'type': 'object', 'additionalProperties': False},
            'rbac_roles': [role], 'executor': 'http',
            'config': {'target': target, 'method': method, 'path': '/loomspan/callbacks/' + route},
        })
    server = {'address': '127.0.0.1' if recipe == 'hardened' else '0.0.0.0', 'port': 8080}
    if recipe == 'standard':
        server |= {'port': 8443, 'ssl': {'enabled': True, 'certificate': 'file:/tls/sidecar-server.pem',
                                        'certificate-private-key': 'file:/tls/sidecar-server-key.pem'}}
    dump(directory_config / 'application.yaml', {
        'server': server,
        'loomspan-sidecar': {
            'configuration': {'mode': 'file'},
            'trust': {'mode': 'file', 'file': {'jwks': '/trust/sidecar.json'}},
            'executions': {'max-concurrent': 1, 'max-queued': 4, 'diagnostics': 'ALWAYS'},
        },
        'loomspan': {
            'executor-config': {'default': {'http': {'targets': {
                name: {'base-url': address, 'auth': {'mode': 'caller-passthrough'},
                       'connect-timeout': '2s', 'read-timeout': '15s' if recipe == 'local' else '3s',
                       'headers': {'X-Reference-Marker': 'installed-python'}}
                for name, address in targets.items()
            }}}},
            'skills': {'locations': ['file:/config/' + skill[0] + '.yaml' for skill in skills]},
            'observability': {'enabled': False},
        },
    })
    if recipe == 'hardened':
        for peer in ('app', 'sidecar'):
            text = (checkout / f'examples/remote/hardened/Caddyfile.{peer}').read_text()
            if peer == 'sidecar':
                outbound = text[text.index('http://:9080'):]
                text += '\n' + outbound.replace(':9080', ':9083').replace(
                    'sidecar-client', 'sidecar-wrong-ca-client')
                text += '\n' + outbound.replace(':9080', ':9084').replace('group-ca', 'other-ca')
            else:
                # The separate HTTPS listener exposes health only, never fixture controls.
                start, end = text.index('https://:8444'), text.index('http://:9080')
                text = text[:start] + '''https://:8444 {
    tls /tls/app-server.pem /tls/app-server-key.pem
    handle /health {
        reverse_proxy 127.0.0.1:8081
    }
    handle {
        respond 404
    }
}

''' + text[end:]
            (directory_config / ('Caddyfile.' + peer)).write_text(text, encoding='utf-8')
    return sidecar


def composition(directory, project, recipe, sidecar_url):
    def mount(path, target, read_only=True):
        return f'{(directory / path).as_posix()}:{target}' + (':ro' if read_only else '')

    # Deliver the TLS fixture and JWT key as separate mounts.
    def tls(*identities):
        names = ['group-ca.pem', 'other-ca.pem']
        for identity in identities:
            names += [identity + '.pem', identity + '-key.pem']
        return [mount('material/' + name, '/tls/' + name) for name in names]
    app_port = '8443' if recipe == 'standard' else '8081'
    app_command = ['uvicorn', 'python_reference:app', '--host',
                   '127.0.0.1' if recipe == 'hardened' else '0.0.0.0',
                   '--port', app_port, '--no-access-log']
    if recipe == 'standard':
        app_command += ['--ssl-certfile', '/tls/app-server.pem', '--ssl-keyfile', '/tls/app-server-key.pem']
    services = {
        'app': {'image': f'{project}-python', 'command': app_command,
                'environment': {'SIDECAR_URL': sidecar_url, 'REFERENCE_RECIPE': recipe},
                'volumes': [mount('material/signing', '/signing'), mount('public', '/public', False),
                            mount('trust', '/trust', recipe != 'local')]},
        'sidecar': {
            'image': 'eclipse-temurin:21-jre', 'user': '10001:10001', 'read_only': True,
            'tmpfs': ['/tmp:exec,mode=1777', '/sidecar/data:uid=10001,gid=10001,mode=0700'],
            'command': ['java', '-jar', '/sidecar.jar'],
            'environment': {'SPRING_CONFIG_ADDITIONAL_LOCATION': 'file:/config/application.yaml',
                            'JAVA_TOOL_OPTIONS': JAVA_OPTIONS},
            'volumes': [mount('sidecar.jar', '/sidecar.jar'), mount('config', '/config'),
                        mount('trust', '/trust')],
        },
    }
    if recipe == 'local':
        services['app']['volumes'].append(mount('java', '/java'))
    if recipe == 'standard':
        services['app']['volumes'] += tls('app-server')
        services['app']['networks'] = {'reference': {'aliases': ['app-wrong']}}
        services['sidecar']['networks'] = {'reference': {'aliases': ['sidecar-wrong']}}
        services['sidecar']['volumes'] += [
            mount('material/' + name, '/tls/' + name)
            for name in ('sidecar-server.pem', 'sidecar-server-key.pem', 'jvm-truststore.p12')
        ]
        services['sidecar']['environment']['JAVA_TOOL_OPTIONS'] += (
            ' -Djavax.net.ssl.trustStore=/tls/jvm-truststore.p12 -Djavax.net.ssl.trustStoreType=PKCS12'
            ' -Djavax.net.ssl.trustStorePassword=fixture-public-trust')
        for service, owner, mode in [('submit-fault', 'sidecar', 'submit'),
                                     ('callback-fault', 'app', 'callback'), ('wrong-ca', 'app', 'wrong-ca')]:
            identity = owner + ('-wrong-ca-server' if mode == 'wrong-ca' else '-server')
            services[service] = {'image': f'{project}-python', 'network_mode': 'service:' + owner,
                                 'volumes': tls(identity), 'command': ['python', 'python_fault.py', mode]}
    elif recipe == 'hardened':
        services['app']['volumes'] += tls('app-client', 'app-wrong-ca-client')
        for peer in ('app', 'sidecar'):
            owner = peer + '-proxy'
            services[peer]['network_mode'] = 'service:' + owner
            identities = [peer + '-server', peer + '-client']
            if peer == 'sidecar':
                identities.append('sidecar-wrong-ca-client')
            services[owner] = {'image': 'caddy:2.10.2', 'read_only': True, 'tmpfs': ['/config', '/data'],
                               'volumes': tls(*identities) + [mount('config/Caddyfile.' + peer, '/etc/caddy/Caddyfile')]}
        services['outsider'] = {'image': f'{project}-python', 'command': ['sleep', 'infinity']}
    for service in services.values():
        if 'network_mode' not in service and 'networks' not in service:
            service['networks'] = ['reference']
    return {'services': services, 'networks': {'reference': {'internal': True}}}


def run(args):
    output = args.output.resolve()
    if output.exists():
        raise ValueError('Use a new result directory')
    jar, wheel = args.sidecar_jar.absolute(), args.python_sdk_wheel.absolute()
    sdk = wheel_identity(wheel)
    embedded = framework_identity(jar, VERSION)
    checkout = args.sidecar_checkout.resolve()
    project = f'sdk-python-{args.recipe}-{uuid4().hex[:10]}'
    report = {'recipe': args.recipe, 'status': 'FAIL', 'project': project,
              'artifacts': {'wheel': sdk, 'sidecar': {'filename': jar.name, 'sha256': sha256(jar.read_bytes()).hexdigest(),
                                                     'framework': VERSION, 'frameworkSha256': embedded}},
              'providerAccess': 'disabled'}
    for name, root in [('suite', ROOT), ('sidecarCheckout', checkout)]:
        report[name] = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    sources = [Path(__file__), ROOT / 'requirements.lock', ROOT / 'apps/python/Dockerfile']
    sources += sorted((ROOT / 'scripts/sdk_lane').glob('python_*.py'))
    report['suiteSourceSha256'] = {path.relative_to(ROOT).as_posix(): sha256(path.read_bytes()).hexdigest()
                                   for path in sources}
    output.mkdir(parents=True, exist_ok=False)
    error = None
    with TemporaryDirectory(prefix=project + '-') as temp:
        directory = Path(temp)
        compose = ['docker', 'compose', '-p', project, '--project-directory', temp,
                   '-f', str(directory / 'compose.yaml')]
        image = False
        started = False

        def call(command, *, capture=False, timeout=180):
            return subprocess.run(command, cwd=directory, check=True, timeout=timeout, text=True,
                                  stdout=subprocess.PIPE if capture else subprocess.DEVNULL,
                                  stderr=subprocess.DEVNULL).stdout

        try:
            report['phase'] = 'configure'
            sidecar_url = configure(directory, checkout, args.recipe)
            shutil.copyfile(jar, directory / 'sidecar.jar')
            build = directory / 'image'
            for path in (wheel, ROOT / 'requirements.lock', *(ROOT / 'scripts/sdk_lane' / name
                         for name in ('python_reference.py', 'python_probe.py', 'python_fault.py'))):
                shutil.copyfile(path, build / path.name)
            base = (ROOT / 'apps/python/Dockerfile').read_text().splitlines()[0]
            (build / 'Dockerfile').write_text(
                base + '\nWORKDIR /reference\nCOPY . .\nRUN pip install --no-cache-dir -r requirements.lock '
                + f'./{wheel.name}[fastapi] && pip check\n', encoding='utf-8')
            dump(directory / 'compose.yaml', composition(directory, project, args.recipe, sidecar_url))
            report['phase'] = 'build'
            call(['docker', 'build', '-t', f'{project}-python', str(build)], timeout=300)
            image = True
            started = True
            report['phase'] = 'startup'
            call(compose + ['up', '-d'])
            report['phase'] = 'probe'
            stdout = call(compose + ['exec', '-T', 'app', 'python', 'python_probe.py', args.recipe], capture=True)
            evidence = json.loads(stdout)
            report.update(evidence)
            assert set(evidence.get('checks', {})) == RESULTS[args.recipe]
            if args.recipe == 'hardened':
                report['phase'] = 'outsider'
                call(compose + ['exec', '-T', 'outsider', 'python', 'python_probe.py', 'outsider'])
            report['status'] = 'PASS'
            report.pop('phase')
        except (OSError, ValueError, AssertionError, subprocess.SubprocessError) as failure:
            error = failure
            report['failureType'] = type(failure).__name__
        finally:
            try:
                if started:
                    call(compose + ['down', '--volumes', '--remove-orphans'])
                if image:
                    call(['docker', 'image', 'rm', f'{project}-python'])
                report['cleanup'] = 'PASS'
            except (OSError, subprocess.SubprocessError) as failure:
                error = error or failure
                report['cleanup'] = 'FAIL'
                report['status'] = 'FAIL'
            (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    if error is not None:
        raise SystemExit(f'{args.recipe} recipe failed ({type(error).__name__}); see report.json')
    print(f'{args.recipe}: installed Python reference passed')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('recipe', choices=tuple(RESULTS))
    parser.add_argument('--sidecar-jar', required=True, type=Path)
    parser.add_argument('--python-sdk-wheel', required=True, type=Path)
    parser.add_argument('--sidecar-checkout', type=Path, default=ROOT.parent / 'loomspan-sidecar')
    parser.add_argument('--output', required=True, type=Path)
    run(parser.parse_args())


if __name__ == '__main__':
    main()
