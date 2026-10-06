"""Verify accepted output assemblies against invocation-local trace sources.

Legacy captures without output_bindings continue through their original reviewer.
This changes where accepted output is read, not the business acceptance criteria.
"""
import hashlib
import json
from pathlib import Path
import yaml
from review_forwarding import payload


def select(value, pointer):
    if pointer == '':
        return value
    if not pointer.startswith('/'):
        raise ValueError('Expected an object pointer')
    for token in pointer[1:].split('/'):
        value = value[token.replace('~1', '/').replace('~0', '~')]
    return value


def unique(items):
    if len(items) != 1:
        raise ValueError('Expected one invocation-local trace record')
    return items[0]


def verify_assembly(records, skill, declaration, contribution_required):
    """Check provenance and exact decoded values; reject incomplete/ambiguous work."""
    try:
        event = unique([r for r in records if r.get('recordType') == 'RESULT_ASSEMBLED'
                        and r.get('metadata', {}).get('skillName') == skill])
        meta, frame = event['metadata'], event['frameId']
        assert meta['owningMissionFrameId'] == frame
        assert meta['modelContributionRequired'] is contribution_required
        opened = unique([r for r in records if r.get('recordType') == 'FRAME_OPENED'
                         and r.get('frameId') == frame and r['sequence'] < event['sequence']])
        mission_input = payload(opened, records)['missionInput']
        # Direct text payloads are strings; the shared chunk reader already
        # JSON-decodes concatenated text/plain chunks into the result object.
        raw_result = payload(event, records)
        result = json.loads(raw_result) if isinstance(raw_result, str) else raw_result
        entries = meta['outputBindings']
        assert len(entries) == len(declaration)
        assert {e['destination'] for e in entries} == set(declaration)
        tasks = []
        if meta.get('planId'):
            plans = [r for r in records if r.get('recordType') == 'PLAN_UPDATED'
                     and r.get('metadata', {}).get('planId') == meta['planId']
                     and r.get('frameId') == frame and r['sequence'] < event['sequence']]
            tasks = payload(max(plans, key=lambda r: r['sequence']), records)['tasks']
            assert tasks and all(t['status'] == 'COMPLETED' for t in tasks)
        for entry in entries:
            binding = declaration[entry['destination']]
            assert entry['parentMissionFrameId'] == frame
            assert entry['sourceKind'] == binding['from'] and entry['sourcePath'] == binding['path']
            source = mission_input
            if binding['from'] == 'child_result':
                assert entry['sourceSkill'] == binding['skill']
                task = unique([t for t in tasks if t['capabilityName'] == binding['skill']])
                assert task['taskId'] == entry['sourceTaskId']
                evidence = unique([r for r in records if r.get('recordType') == 'EVIDENCE_RECORDED'
                                   and r.get('frameId') == frame
                                   and r.get('metadata', {}).get('linkedTaskId') == task['taskId']
                                   and r['metadata'].get('capabilityName') == binding['skill']
                                   and r['sequence'] < event['sequence']])
                accepted = unique([r for r in records if r.get('recordType') == 'TOOL_CALL_COMPLETED'
                                   and r.get('metadata', {}).get('linkedTaskId') == task['taskId']
                                   and r['metadata'].get('capabilityName') == binding['skill']
                                   and r['sequence'] < evidence['sequence']])
                source = json.loads(payload(accepted, records)['details']['result'])
            else:
                assert binding['from'] == 'input'
            assert select(result, entry['destination']) == select(source, binding['path'])
        return {'valid': True, 'result': result, 'bindingCount': len(entries),
                'modelContributionRequired': contribution_required, 'frameId': frame}
    except (AssertionError, KeyError, ValueError, TypeError, IndexError):
        return {'valid': False, 'reason': 'Output assembly lacks exact invocation-local source proof'}


def output_assemblies(directory, path, case):
    directory = Path(directory)
    configs = {s: directory / ('configuration/config/skills/' + s + '.yaml')
               for s in ['compareOptions', 'resolveEquipment']}
    declarations = {s: yaml.safe_load(f.read_text(encoding='utf-8')).get('output_bindings')
                    for s, f in configs.items() if f.exists()}
    if not any(declarations.values()):
        return None
    try:
        trace = unique([t for t in json.loads((directory / 'trace-index.json').read_bytes())
                        if t['path'] == path and case in t['cases'] and t.get('entrySkill') == 'resolveEquipment'])
        file = (directory / trace['file']).resolve()
        assert file.is_relative_to(directory.resolve())
        raw = file.read_bytes()
        assert hashlib.sha256(raw).hexdigest() == trace['sha256']
        records = [json.loads(line) for line in raw.decode('utf-8').splitlines() if line]
        results = {s: verify_assembly(records, s, declarations[s], s == 'compareOptions')
                   for s in configs}
        assert all(r['valid'] for r in results.values())
        journal = json.loads((directory / 'journal.json').read_bytes())
        responses = {e['requestId']: e for e in journal if e['event'] == 'model-response'}
        calls = {s: [e for e in journal if e.get('caseId') == case and e.get('path') == path
                    and e['event'] == 'model-request' and any(
                        m.get('role') == 'user' and m.get('content', '').startswith('Mission objective:')
                        and "'" + s + "'" in m.get('content', '').split('Canonical mission input:')[0]
                        for m in e['request']['messages'])] for s in configs}
        assert not any('All required plan tasks are already COMPLETE.' in m.get('content', '')
                       for e in calls['resolveEquipment'] for m in e['request']['messages'])
        contribution = json.loads(responses[calls['compareOptions'][-1]['requestId']]
                                  ['response']['choices'][0]['message']['content'])
        # These skills bind top-level fields. Raw model output must contain only
        # unbound fields, exactly as retained in the accepted comparison.
        bound = {p[1:] for p in declarations['compareOptions']}
        assert all('/' not in p[1:] for p in declarations['compareOptions'])
        expected = {k: v for k, v in results['compareOptions']['result'].items() if k not in bound}
        assert contribution == expected
        terminal = json.loads((directory / (path + '-assessment.json')).read_bytes())
        assert json.loads(terminal['result']) == results['resolveEquipment']['result']
        return {'valid': True, **results, 'rootFinalModelRequests': 0,
                'comparisonContributionPreserved': True}
    except (AssertionError, KeyError, ValueError, TypeError, IndexError, OSError):
        return {'valid': False, 'reason': 'Assembly, model contribution or publication not proven'}
