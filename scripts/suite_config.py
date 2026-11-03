"""Check runtime skill identities across model and executor declarations."""
import yaml


def prepare(root):
    names = {}
    for kind in ('skills', 'executor-skills'):
        for file in sorted((root / 'config' / kind).glob('*/*.yaml')):
            name = yaml.safe_load(file.read_bytes())['name']
            if name in names:
                raise ValueError(f'Duplicate runtime skill {name}: {names[name]} and {file}')
            names[name] = file
