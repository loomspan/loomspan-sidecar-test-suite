"""Full-workflow fault with one genuine correction and actual-result parent envelopes."""
import copy
import json
from recovery_replay import recovery_steps


def stages(sample_steps, response=None, provenance=None):
    steps = recovery_steps(sample_steps)
    index = next(i for i,s in enumerate(steps) if s['stageSkill']=='compareOptions') + 1
    correction = steps[index]
    correction.pop('response')
    correction['contains'].append("Unexpected close marker '}'")
    if response is None:
        correction['live'] = True
        correction['provenance'] = {'kind':'One authorized genuine Muse correction to actual full-workflow parser feedback'}
    else:
        correction['response'] = copy.deepcopy(response)
        correction['provenance'] = copy.deepcopy(provenance)
    plans = {s['stageSkill']:s['tasks'] for s in steps if s['stageKind']=='plan'}
    for step in steps:
        if step['stageKind'] != 'final':
            continue
        child = 'compareOptions' if step['stageSkill']=='planResolution' else 'planResolution'
        tasks = [t for t in plans[step['stageSkill']] if t['capabilityName']==child]
        if len(tasks)!=1:
            raise ValueError('Expected unique completed parent child')
        step.pop('response')
        step['responseFromCompletedTask'] = {'taskId':tasks[0]['taskId'],'skillName':child}
        step['provenance'] = {'kind':'Explicit offline parent envelope copying actual completed child unchanged',
                              'scope':'No invented result and no paid parent synthesis'}
    return steps
