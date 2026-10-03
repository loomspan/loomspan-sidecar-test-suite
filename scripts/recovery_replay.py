"""Explicit full-workflow fault derivation; never changes the approved fixture."""
import copy
import hashlib

FEEDBACK = 'The previous response could not be parsed as JSON.'


def recovery_steps(steps):
    steps = copy.deepcopy(steps)
    matches = [i for i, s in enumerate(steps) if s['stageSkill'] == 'compareOptions']
    if len(matches) != 1:
        raise ValueError('Expected one reviewed comparison')
    index = matches[0]
    valid = copy.deepcopy(steps[index])
    raw = valid['response']['choices'][0]['message']['content']
    invalid = steps[index]
    invalid['response']['choices'][0]['message']['content'] = raw + '}'
    invalid.setdefault('excludes', []).append(FEEDBACK)
    invalid['provenance'].update(kind='Deliberate malformed JSON mutation of approved comparison',
        mutations=['Append one extra closing brace to captured content; provider envelope unchanged'],
        validContentSha256=hashlib.sha256(raw.encode()).hexdigest())
    for step in steps:
        step['after'] = [i + 1 if i >= index else i for i in step['after']]
    valid['after'] = [index]
    valid['contains'].append(FEEDBACK)
    valid['provenance'].update(kind='Offline correction replay of unchanged reviewed comparison',
        correctionProvenance='Original valid Muse content reused; no new model correction judgment')
    steps.insert(index + 1, valid)
    return steps
