"""Validate suite skill identities and assemble Sidecar's single route catalog."""
from pathlib import Path
import os
import tempfile
import yaml


def prepare(root):
    names = {}
    for kind in ('skills', 'rest-skills'):
        for file in sorted((root / 'config' / kind).glob('*/*.yaml')):
            name = yaml.safe_load(file.read_bytes())['name']
            if name in names:
                raise ValueError(f'Duplicate runtime skill {name}: {names[name]} and {file}')
            names[name] = file
    combined = {'targets': {}, 'routes': {}}
    for file in sorted((root / 'config/routes').glob('*.yaml')):
        fragment = yaml.safe_load(file.read_bytes())
        for section in combined:
            for name, value in fragment.get(section, {}).items():
                if name in combined[section]:
                    raise ValueError(f'Duplicate {section} identity {name}: {file}')
                combined[section][name] = value
    for name, route in combined['routes'].items():
        if name not in names or route['target'] not in combined['targets']:
            raise ValueError('Unresolved route: ' + name)
    target = root / '.runtime/suite-routes.yaml'
    raw = yaml.safe_dump(combined, sort_keys=False).encode()
    if target.is_file() and target.read_bytes() == raw:
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as temporary:
        temporary.write(raw)
    os.replace(temporary.name, target)
