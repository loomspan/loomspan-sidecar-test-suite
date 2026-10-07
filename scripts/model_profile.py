"""Label new captures from the shared mounted model configuration."""
import environment as target_env
from pathlib import Path
import subprocess
import yaml
import os

ROOT = Path(__file__).resolve().parents[1]


def model_profile(paths=('java', 'sidecar')):
    profiles = []
    for path in paths:
        raw = (Path(os.getenv('LOOMSPAN_MODEL_CONFIG_DIRECTORY', ROOT / 'config')) / (path + '.yaml')).read_text(encoding='utf-8')
        mounted = subprocess.check_output(
            target_env.execute(path, 'cat', '/config/runtime.yaml'), text=True)
        if yaml.safe_load(raw) != yaml.safe_load(mounted):
            raise RuntimeError('Mounted model configuration differs for ' + path)
        model = yaml.safe_load(raw)['loomspan']['models']['reasoning']
        levels = model.get('thinking-levels', [])
        if len(levels) > 1:
            raise RuntimeError('Capture requires at most one reasoning level')
        models = yaml.safe_load(raw)['loomspan']['models']
        skill_models = {}
        skill_directory = Path(os.getenv('LOOMSPAN_MODEL_CONFIG_DIRECTORY', ROOT / 'config')) / 'skills'
        for file in sorted(skill_directory.glob('*.yaml')):
            skill = yaml.safe_load(file.read_bytes())
            mounted_skill = yaml.safe_load(subprocess.check_output(
                target_env.execute(path, 'cat', '/config/skills/' + file.name)))
            if skill != mounted_skill:
                raise RuntimeError('Mounted skill differs: ' + file.stem)
            selected = models[skill['model']]
            skill_models[skill['name']] = {'model': selected['provider-model'],
                                          'reasoning': skill.get('thinking_level')}
        profiles.append({'model': model['provider-model'], 'reasoning': levels[0] if levels else None,
                         'skills': skill_models})
    if not profiles or any(p != profiles[0] for p in profiles):
        raise RuntimeError('Integration paths must select the same model profile')
    return profiles[0]
