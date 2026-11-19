"""Label new captures from the shared mounted model configuration."""
import environment as target_env
from pathlib import Path
import subprocess
import yaml
import os
import io
import re
import tarfile

ROOT = Path(__file__).resolve().parents[1]



def mounted_configuration(path):
    # One read per host avoids spawning Compose once for every skill. Never extract
    # archive paths to disk; compare the same expected files as the original checks.
    raw = subprocess.check_output(target_env.execute(
        path, 'tar', '-C', '/config', '-cf', '-', 'runtime.yaml', 'skills'))
    with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
        return {entry.name: archive.extractfile(entry).read()
                for entry in archive.getmembers() if entry.isfile()}


def typesafe_model(skill):
    transform = skill['input_transform']
    pins = re.findall(r'^  "model": "([^"]+)",$', transform['expression'], re.MULTILINE)
    if transform['language'] != 'jslt' or len(pins) != 1:
        raise ValueError('Expected one explicit TypeSafe model pin in ' + skill['name'])
    return pins[0]


def model_profile(paths=('java', 'sidecar')):
    profiles = []
    for path in paths:
        raw = (Path(os.getenv('LOOMSPAN_MODEL_CONFIG_DIRECTORY', ROOT / 'config')) / (path + '.yaml')).read_text(encoding='utf-8')
        mounted_files = mounted_configuration(path)
        mounted = mounted_files['runtime.yaml']
        if yaml.safe_load(raw) != yaml.safe_load(mounted):
            raise RuntimeError('Mounted model configuration differs for ' + path)
        model = yaml.safe_load(raw)['loomspan']['models']['reasoning']
        levels = model.get('thinking-levels', [])
        if len(levels) > 1:
            raise RuntimeError('Capture requires at most one reasoning level')
        models = yaml.safe_load(raw)['loomspan']['models']
        skill_models = {}
        skill_directory = Path(os.getenv('LOOMSPAN_MODEL_CONFIG_DIRECTORY', ROOT / 'config')) / 'skills'
        for file in sorted(skill_directory.rglob('*.yaml')):
            skill = yaml.safe_load(file.read_bytes())
            mounted_skill = yaml.safe_load(mounted_files['skills/' + file.relative_to(skill_directory).as_posix()])
            if skill != mounted_skill:
                raise RuntimeError('Mounted skill differs: ' + file.stem)
            selected = (typesafe_model(skill) if skill.get('executor') == 'typesafe'
                        else models[skill['model']]['provider-model'])
            skill_models[skill['name']] = {'model': selected,
                                          'reasoning': skill.get('thinking_level')}
        profiles.append({'model': model['provider-model'], 'reasoning': levels[0] if levels else None,
                         'skills': skill_models})
    if not profiles or any(p != profiles[0] for p in profiles):
        raise RuntimeError('Integration paths must select the same model profile')
    return profiles[0]
