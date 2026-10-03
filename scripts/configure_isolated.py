"""Select a fresh workspace's isolated, provider-disabled Compose project."""
import argparse
import json
from pathlib import Path
import environment


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True)
    parser.add_argument('--port-offset', type=int, required=True)
    args = parser.parse_args()
    root = environment.ROOT
    runtime = root / '.runtime'
    if runtime.exists():
        raise ValueError('Configure isolation only in a new workspace without .runtime')
    if args.project == 'equipment-acceptance' or args.port_offset == 0:
        raise ValueError('The retained project and ports are forbidden for clean setup')
    runtime.mkdir()
    (runtime / 'environment.json').write_text(json.dumps({'project': args.project, 'portOffset': args.port_offset}, indent=2))
    environment.settings()
    value = environment.issuer()
    lines = ['services:']
    for name, original, target in [('keycloak', 18080, 8080), ('fixtures', 18090, 8080),
                                   ('python', 18082, 8080), ('java', 18081, 8080), ('sidecar', 18083, 8080)]:
        lines += [f'  {name}:', '    ports: !override', f'      - "127.0.0.1:{environment.port(original)}:{target}"']
        if name == 'sidecar':
            lines += [f'      - "127.0.0.1:{environment.port(19091)}:9091"']
        if name == 'keycloak':
            lines += [f'    command: [start-dev, --import-realm, "--hostname=http://localhost:{environment.port(18080)}"]']
        else:
            key = {'java': 'EQUIPMENT_ISSUER', 'python': 'ISSUER',
                   'sidecar': 'SPRING_APPLICATION_JSON', 'fixtures': 'OPENROUTER_API_KEY'}[name]
            setting = json.dumps({'loomspan-sidecar': {'auth': {'jwt': {'issuer-uri': value}}}}) if name == 'sidecar' else value if name != 'fixtures' else ''
            lines += ['    environment:', f'      {key}: {json.dumps(setting)}']
    (runtime / 'compose.isolated.yaml').write_text('\n'.join(lines) + '\n')
    print('Configured isolated project and ports; no containers or credentials created.')


if __name__ == '__main__':
    main()
