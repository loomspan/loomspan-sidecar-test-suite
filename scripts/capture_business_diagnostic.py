"""Full offline workflow diagnostic using captured stages plus explicit authored edits.

Not approved business replay or model judgment. Never registers a paid/live stage.
"""
import argparse
import copy
import hashlib
import json
import pathlib
import time
import uuid

import httpx
from baseline import baseline
from capture import collect, wait
from capture_step_correction import records
from finalize_evidence import finalize
from inspect_capture import mission, system
from login import login
from readiness import ready

ROOT = pathlib.Path(__file__).resolve().parents[1]


def normalized(value, old_case, case):
    return json.loads(json.dumps(value).replace(old_case, case))


def stages(source, diagnostic, path, case):
    events = json.loads((source / 'journal.json').read_text())
    sample = diagnostic['samples'][path]
    old_case = sample['provenance']['caseId']
    candidate = normalized(sample['candidate'], old_case, case)
    steps = []
    for call in [e for e in events if e['event'] == 'model-request' and e.get('path') == path]:
        replies = [e for e in events if e['event'] == 'model-response' and e.get('path') == path
                   and e.get('requestId') == call['requestId'] and e.get('caseId') == old_case]
        if len(replies) != 1 or replies[0].get('provenance') != 'live OpenRouter' or replies[0].get('status') != 200:
            raise ValueError('Missing unique live source response')
        skill = next(name for name in ['resolveEquipment', 'planResolution', 'assessEquipment', 'compareOptions']
                     if mission(call['request'], name))
        reply = normalized(replies[0]['response'], old_case, case)
        value = json.loads(reply['choices'][0]['message']['content'])
        final = 'All required plan tasks are already COMPLETE.' in system(call['request'])
        provenance = {**sample['provenance'], 'requestId': call['requestId'],
            'sourceContentSha256': hashlib.sha256(replies[0]['response']['choices'][0]['message']['content'].encode()).hexdigest(),
            'kind': 'Captured stage with case-ID normalization only', 'normalization': 'caseId only',
            'approvedBusinessReplay': False}
        step = {'contains': [case, "Fulfill the mission for skill '" + skill + "'"],
                'systemContains': [], 'systemExcludes': [], 'response': reply, 'provenance': provenance,
                'stageSkill': skill, 'stageKind': 'model'}
        if value.get('stepAction') == 'CALL_TOOL':
            step['systemContains'] = ['Exact capability/tool: ' + value['toolName']]
            step.update(stageKind='action', taskId=value['taskId'], toolName=value['toolName'])
        elif 'tasks' in value:
            step['systemContains'] = ['Create an ordered flight plan']
            step.update(stageKind='plan', tasks=value['tasks'])
        elif final:
            step['systemContains'] = ['All required plan tasks are already COMPLETE.']
            step['stageKind'] = 'final'
        if skill == 'compareOptions' or final:
            reply['choices'][0]['message']['content'] = json.dumps(candidate)
            provenance.update(kind='Hand-edited diagnostic comparison or synthetic matching parent final',
                              mutations=sample['edits'], syntheticCorrectionSequence=True)
        if skill == 'compareOptions':
            invalid = copy.deepcopy(step)
            invalid_value = copy.deepcopy(candidate)
            invalid_value['selectedOption'] = next(q['quoteId'] for q in candidate['quotes'] if q['option'] == 'expedited')
            invalid['response']['choices'][0]['message']['content'] = json.dumps(invalid_value)
            invalid['provenance'].update(kind='Intentional quote-ID selectedOption mutation of hand-edited diagnostic',
                                         injectedFault='selectedOption contains quoteId instead of option name')
            invalid['excludes'] = ['does not satisfy the configured output_schema']
            steps.append(invalid)
            step['contains'] += ['$.selectedOption', 'does not satisfy the configured output_schema']
            step['provenance']['kind'] = 'Synthetic valid correction; not a model correction answer'
        steps.append(step)
    # Captured arrival order is not a dependency: assigned parallel actions may race.
    plans = {s['stageSkill']: i for i, s in enumerate(steps) if s['stageKind'] == 'plan'}
    actions = {(s['stageSkill'], s['taskId']): i for i, s in enumerate(steps) if s['stageKind'] == 'action'}
    parents = {s['toolName']: i for i, s in enumerate(steps) if s['stageKind'] == 'action'}
    tasks = {(s['stageSkill'], t['taskId']): t for s in steps if s['stageKind'] == 'plan' for t in s['tasks']}
    last_model = {}
    finals = {}
    for i, step in enumerate(steps):
        skill, kind = step['stageSkill'], step['stageKind']
        if kind == 'plan':
            step['after'] = [] if skill == 'resolveEquipment' else [parents[skill]]
        elif kind == 'action':
            task = tasks[(skill, step['taskId'])]
            step['after'] = [plans[skill]] + [actions[(skill, dependency)] for dependency in task.get('dependsOn', [])]
        elif kind == 'model':
            step['after'] = [last_model.get(skill, parents[skill])]
            last_model[skill] = i
        elif kind == 'final':
            step['after'] = [last_model['compareOptions']] if skill == 'planResolution' else [finals['planResolution']]
            finals[skill] = i
    if any(s.get('live') for s in steps):
        raise ValueError('Live stage prohibited')
    return steps, candidate


def run():
    ready()
    build = baseline()
    source = ROOT / 'evidence/live-20261002-000544'
    diagnostic_file = ROOT / 'fixtures/replay/business-output-diagnostic-v1.json'
    diagnostic = json.loads(diagnostic_file.read_text())
    assert diagnostic['approved'] is False and diagnostic['sourceDisposition'] == 'REJECTED_FOR_REPLAY'
    for name, wanted in diagnostic['sourceSha256'].items():
        assert hashlib.sha256((source / name).read_bytes()).hexdigest() == wanted
    out = ROOT / 'evidence' / ('business-workflow-offline-' + time.strftime('%Y%m%d-%H%M%S'))
    out.mkdir()
    secrets = json.loads((ROOT / '.runtime/secrets.json').read_text())
    token = login('maya')
    results, cases = [], []
    before = records()
    (out / 'business-records-before.json').write_text(json.dumps(before, indent=2))
    with httpx.Client(timeout=300, trust_env=False) as client:
        try:
            for path, port in [('java', 18081), ('sidecar', 18082)]:
                case = 'business-diagnostic-' + path + '-' + uuid.uuid4().hex
                cases.append(case)
                steps, candidate = stages(source, diagnostic, path, case)
                registration = {'mode': 'replay', 'path': path, 'steps': steps}
                (out / (path + '-registration.json')).write_text(json.dumps(registration, indent=2))
                (out / (path + '-expected.json')).write_text(json.dumps(candidate, indent=2))
                body = json.loads((ROOT / 'fixtures/base-case.json').read_text())
                body['caseId'] = case
                (out / (path + '-input.json')).write_text(json.dumps(body, indent=2))
                r = client.post('http://127.0.0.1:18090/control/cases/' + case, json=registration,
                                headers={'X-Control-Key': secrets['control']})
                r.raise_for_status()
                api = f'http://127.0.0.1:{port}'
                r = client.post(api + '/assessments', json=body, headers={'Authorization': 'Bearer ' + token})
                r.raise_for_status()
                item = {'path': path, 'caseId': case, 'executionId': r.json()['id'], 'expectedCalls': len(steps)}
                results.append(item)
                terminal = wait(client, api, item['executionId'], token, timeout=300)
                item['status'] = terminal['status']
                (out / (path + '-assessment.json')).write_text(json.dumps(terminal, indent=2))
                print(path, terminal['status'], flush=True)
        finally:
            collect(client, out, cases, secrets, [token])
            after = records()
            (out / 'business-records-after.json').write_text(json.dumps(after, indent=2))
            (out / 'manifest.json').write_text(json.dumps({**build, 'mode': 'offline authored business diagnostic',
                'sourceCapture': source.name, 'sourceSha256': diagnostic['sourceSha256'],
                'diagnosticSha256': hashlib.sha256(diagnostic_file.read_bytes()).hexdigest(),
                'results': results, 'approved': False, 'paidCalls': 0,
                'scope': 'Captured workflow stages, authored business comparison/finals, injected selection fault and synthetic correction; not model judgment or approved replay'}, indent=2))
            finalize(out)
            print(out, flush=True)
    return out


if __name__ == '__main__':
    argparse.ArgumentParser(description=__doc__).parse_args()
    run()
