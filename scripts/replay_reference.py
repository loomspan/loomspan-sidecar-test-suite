"""Load the accepted reference, reject stale contracts, and rebind only case identity."""
import hashlib
import json
from pathlib import Path
import yaml
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fixtures.responses import text_response

ROOT = Path(__file__).resolve().parents[1]
REFERENCE_DIRECTORY = 'fixtures/reference-responses'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def source_hash(raw):
    return sha(json.dumps(json.loads(raw), sort_keys=True, ensure_ascii=False).encode())


def contract_hash(raw):
    skill = yaml.safe_load(raw)
    # Alias spelling changed at phase close; effective assignment is checked separately.
    skill.pop('model', None)
    return sha(json.dumps(skill, sort_keys=True, ensure_ascii=False).encode())


def load_reference(root=ROOT):
    directory = root / REFERENCE_DIRECTORY
    manifest = json.loads((directory / 'manifest.json').read_bytes())
    if manifest['formatVersion'] not in (1, 2) or manifest['businessStatus'] != 'BUSINESS_PASS_WITH_MINOR_CAVEATS':
        raise ValueError('Unapproved or unsupported replay reference')
    for name, expected in manifest['files'].items():
        file = directory / name
        if file.parent != directory or sha(file.read_bytes()) != expected:
            raise ValueError('Frozen fixture checksum mismatch: ' + name)
    for name, expected in manifest['sourceHashes'].items():
        if source_hash((root / name).read_bytes()) != expected:
            raise ValueError('Reference source changed; explicit fixture review required: ' + name)
    for name, expected in manifest['skillContracts'].items():
        if contract_hash((root / 'config/skills/equipment-service' / (name + '.yaml')).read_bytes()) != expected:
            raise ValueError('Skill contract changed; explicit fixture review required: ' + name)
    for host in ['java', 'sidecar']:
        models = yaml.safe_load((root / 'config' / (host + '.yaml')).read_bytes())['loomspan']['models']
        for name, expected in manifest['skillModels'].items():
            skill = yaml.safe_load((root / 'config/skills/equipment-service' / (name + '.yaml')).read_bytes())
            if models[skill['model']]['provider-model'] != expected.removeprefix('openai/') or skill.get('thinking_level') != manifest['reasoning']:
                raise ValueError('Reference model assignment changed: ' + host + '/' + name)

    # Import the accepted historical wire recording without changing its files,
    # business JSON content, request evidence, or expected final result.
    references = {}
    for name in manifest['scenarios']:
        reference = json.loads((directory / (name + '.json')).read_bytes())
        for step in reference['steps']:
            step['requestContract']['model'] = step['requestContract']['model'].removeprefix('openai/')
            old = step['response']
            if manifest['formatVersion'] == 1:
                step['response'] = text_response(old['choices'][0]['message']['content'],
                    old['model'].removeprefix('openai/'), old['id'])
        references[name] = reference
    manifest = {**manifest, 'skillModels': {k: v.removeprefix('openai/') for k,v in manifest['skillModels'].items()}}
    return manifest, references


def bind_case(reference, case_id):
    # Case IDs also prefix deterministic quote IDs. No other values are rewritten.
    return json.loads(json.dumps(reference).replace(reference['caseId'], case_id))
