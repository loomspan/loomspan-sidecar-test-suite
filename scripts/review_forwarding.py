"""Verify declared nested forwarding against immutable Framework trace evidence."""
import hashlib
import json
from pathlib import Path
import yaml


def payload(record, records):
    if record.get('data') is not None:
        return record['data']
    metadata = record['metadata']
    chunks = sorted((r for r in records if r.get('recordType') == 'PAYLOAD_CHUNK_APPENDED'
                     and r['metadata'].get('payloadId') == metadata.get('payloadId')),
                    key=lambda r: r['metadata']['chunkIndex'])
    if len(chunks) != metadata.get('chunkCount'):
        raise ValueError('Incomplete trace payload')
    return json.loads(''.join(r['data'] for r in chunks))


def verify_records(records, parent, child):
    forwarded = [r for r in records if r.get('recordType') == 'RESULT_FORWARDED'
                 and r.get('metadata', {}).get('skillName') == parent]
    if len(forwarded) != 1:
        return {'valid': False, 'reason': 'Expected one forwarding event'}
    event = forwarded[0]
    meta = event['metadata']
    selected = [r for r in records if r.get('recordType') == 'TOOL_CALL_COMPLETED'
                and r.get('metadata', {}).get('capabilityName') == child
                and r['metadata'].get('linkedTaskId') == meta.get('linkedTaskId')]
    parents = [r for r in records if r.get('recordType') == 'TOOL_CALL_COMPLETED'
               and r.get('metadata', {}).get('capabilityName') == parent]
    recorded = [r for r in records if r.get('recordType') == 'EVIDENCE_RECORDED'
                and r.get('frameId') == event.get('frameId')
                and r.get('metadata', {}).get('capabilityName') == child
                and r['metadata'].get('linkedTaskId') == meta.get('linkedTaskId')]
    if meta.get('capabilityName') != child or not meta.get('planId') or not meta.get('linkedTaskId') or len(selected) != 1 or len(parents) != 1 or len(recorded) != 1:
        return {'valid': False, 'reason': 'Forwarded task identity is not uniquely supported'}
    child_text = payload(selected[0], records).get('details', {}).get('result')
    parent_text = payload(parents[0], records).get('details', {}).get('result')
    plans = [r for r in records if r.get('recordType') == 'PLAN_UPDATED'
             and r.get('metadata', {}).get('planId') == meta['planId']
             and r['sequence'] < event['sequence']]
    plan = payload(max(plans, key=lambda r: r['sequence']), records) if plans else {}
    tasks = plan.get('tasks', [])
    complete = bool(tasks) and all(t.get('status') == 'COMPLETED' for t in tasks)
    selection_matches = sum(t.get('taskId') == meta['linkedTaskId'] and
                            t.get('capabilityName') == child for t in tasks) == 1
    valid = (isinstance(child_text, str) and child_text == parent_text
             and complete and selection_matches
             and selected[0]['sequence'] < event['sequence'] < parents[0]['sequence']
             and recorded[0]['sequence'] < event['sequence'])
    return {'valid': valid, 'result': parent_text, 'event': event,
            'childSequence': selected[0]['sequence'], 'parentSequence': parents[0]['sequence'],
            'exactTextMatch': child_text == parent_text, 'allAcceptedTasksCompleted': complete}


def resolution_forwarding(directory, path, case):
    directory = Path(directory)
    config = directory / 'configuration/config/skills/planResolution.yaml'
    if not config.exists():
        return None
    skill = yaml.safe_load(config.read_text(encoding='utf-8'))
    if 'output_from' not in skill:
        return None
    if skill['output_from'] != {'skill': 'compareOptions'}:
        return {'valid': False, 'reason': 'Unsupported resolution forwarding declaration'}
    traces = [t for t in json.loads((directory / 'trace-index.json').read_bytes())
              if t['path'] == path and case in t['cases'] and t.get('entrySkill') == 'resolveEquipment']
    if len(traces) != 1:
        return {'valid': False, 'reason': 'Expected a unique case root trace'}
    raw = (directory / traces[0]['file']).read_bytes()
    if hashlib.sha256(raw).hexdigest() != traces[0]['sha256']:
        return {'valid': False, 'reason': 'Trace hash mismatch'}
    records = [json.loads(line) for line in raw.decode('utf-8').splitlines() if line]
    result = verify_records(records, 'planResolution', 'compareOptions')
    result['parentOutputValidationEvents'] = sum(r.get('recordType') == 'STRUCTURED_OUTPUT_RECORDED'
        and r.get('metadata', {}).get('skillName') == 'planResolution' for r in records)
    journal = json.loads((directory / 'journal.json').read_bytes())
    result['parentSynthesisRequests'] = sum(
        any(m.get('role') == 'user' and m.get('content', '').startswith('Mission objective:')
            and "'planResolution'" in m.get('content', '').split('Canonical mission input:')[0]
            for m in e['request'].get('messages', []))
        and any('All required plan tasks are already COMPLETE.' in m.get('content', '')
                for m in e['request'].get('messages', []))
        for e in journal if e.get('caseId') == case and e.get('path') == path and e['event'] == 'model-request')
    result['valid'] = result['valid'] and result['parentOutputValidationEvents'] == 0 and result['parentSynthesisRequests'] == 0
    return result
