"""Label new captures from the shared mounted model configuration."""
import environment as target_env
from pathlib import Path
import subprocess
import yaml

ROOT = Path(__file__).resolve().parents[1]


def model_profile():
    profiles = []
    for path in ('java', 'sidecar'):
        raw = (ROOT / 'config' / (path + '.yaml')).read_text(encoding='utf-8')
        mounted = subprocess.check_output(
            target_env.execute(path, 'cat', '/config/runtime.yaml'), text=True)
        if yaml.safe_load(raw) != yaml.safe_load(mounted):
            raise RuntimeError('Mounted model configuration differs for ' + path)
        model = yaml.safe_load(raw)['loomspan']['models']['reasoning']
        if model['thinking-levels'] != ['medium']:
            raise RuntimeError('Capture expects the selected medium reasoning level')
        profiles.append({'model': model['provider-model'], 'reasoning': 'medium'})
    if profiles[0] != profiles[1]:
        raise RuntimeError('Integration paths must select the same model profile')
    return profiles[0]
