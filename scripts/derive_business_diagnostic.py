"""Offline, hand-edited business examples from preserved Muse output; never approval."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
from inspect_capture import mission


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def derive(source):
    source = Path(source).resolve()
    journal = json.loads((source / 'journal.json').read_bytes())
    manifest = json.loads((source / 'manifest.json').read_bytes())
    samples = {}
    for path, storage in [('java', 'java'), ('sidecar', 'python')]:
        calls = [e for e in journal if e['event'] == 'model-request'
                 and e.get('path') == path and mission(e['request'], 'compareOptions')]
        if len(calls) != 1:
            raise ValueError('Expected exactly one comparison request: ' + path)
        call = calls[0]
        replies = [e for e in journal if e['event'] == 'model-response'
                   and e.get('requestId') == call['requestId'] and e.get('path') == path
                   and e.get('caseId') == call['caseId']]
        if len(replies) != 1 or replies[0].get('status') != 200 or replies[0].get('provenance') != 'live OpenRouter':
            raise ValueError('Missing unique live response: ' + path)
        if call['request'].get('model') != manifest['model'] or call['request'].get('reasoning_effort') != manifest['reasoning']:
            raise ValueError('Model identity mismatch')
        text = replies[0]['response']['choices'][0]['message']['content']
        original = json.loads(text)
        terminal = json.loads((source / (path + '-assessment.json')).read_bytes())
        if terminal['status'] != 'COMPLETED' or json.loads(terminal['result']) != original:
            raise ValueError('Comparison differs from published assessment')
        records = json.loads((source / (storage + '-business-records.json')).read_bytes())
        quotes = {row['id']: json.loads(row['body']) for row in records['quotes']}
        if len(original['quotes']) != 2 or any(quotes.get(q['quoteId']) != q for q in original['quotes']):
            raise ValueError('Authoritative quote mismatch')
        candidate = copy.deepcopy(original)
        edits = []

        def set_field(key, value, reason):
            if candidate[key] != value:
                edits.append({'field': key, 'before': candidate[key], 'after': value, 'reason': reason})
                candidate[key] = value

        def replace_once(value, old, new):
            if value.count(old) != 1:
                raise ValueError('Source wording changed; review the new capture explicitly')
            return value.replace(old, new)

        access = ('Expedited arrival is within 08:00-18:00, but the 2-4 hour work estimate '
                  'can extend a 16:00 arrival to 20:00, beyond 18:00 access. Dispatch must arrange later access '
                  'with Luis Romero or limit work to permitted hours; later access and restoration '
                  'are unconfirmed. The two authorized chargeable repair hours are a scope cap, '
                  'not the total elapsed work estimate (SITE-WEST, RESOURCES-017).')
        if path == 'java':
            rationale = replace_once(candidate['rationale'], 'expedited fits site access 08:00-18:00',
                                     'expedited arrival fits site access 08:00-18:00 but work may extend beyond it')
            alternatives = candidate['alternatives'].copy()
            alternatives[0] = replace_once(alternatives[0], 'still pays diagnosis/travel included and repair only if justified',
                'diagnosis and travel remain included even if unresolved (S-3); only actual authorized repair labor and installed parts are chargeable, subject to warranty and the cap')
            set_field('alternatives', alternatives, 'Clarify S-3 without introducing diagnosis/travel charges')
        else:
            rationale = replace_once(candidate['rationale'], 'Expedited occurs within site access 08:00-18:00 without after-hours arrangement',
                                     'Expedited arrival occurs within site access 08:00-18:00, but completion may require later access')
        set_field('rationale', rationale + ' ' + access, 'Separate attendance from work completion')
        uncertainty = [u for u in candidate['uncertainty'] if 'expedited and standard fit' not in u]
        set_field('uncertainty', uncertainty + [access], 'Remove unconditional access claim and retain explicit uncertainty')
        set_field('selectedOption', 'expedited', 'Canonical option name; no silent quote-ID normalization')
        expedited = next(q for q in candidate['quotes'] if q['option'] == 'expedited')
        set_field('nextDecision',
            f"Luis Romero must approve and submit the approved expedited service request before {expedited['expiresAt']} "
            'to preserve quoted prices for the approved scope (S-5). Approval alone does not preserve prices; '
            'submission does not reserve stock or confirm attendance. Changes to attendance, repair scope or cap '
            'require renewed approval; matching dispatch confirmation or later quote expiry alone does not. '
            'Separately decide on the USD 2400.00 LOAN-017 offer before its 11:00 expiry, with separately '
            'verified Priya Shah approval above Luis USD 1000.00 ceiling and Luis access arrangements for '
            '20:00-22:00 delivery. Service submission does not extend the loaner offer. Dispatch must also '
            'arrange potential expedited work beyond 18:00 with Luis. No approval or commitment is made here.',
            'Explicit approved-request submission and separate continuity/access handoff')
        set_field('citations', list(dict.fromkeys(candidate['citations'] +
            ['W-2', 'W-5', 'S-3', 'S-4', 'S-5', 'SITE-WEST', 'RESOURCES-017', 'AUTH-NB', 'LOAN-017'])),
            'Retain technical sources and add applicable commercial/context sources')
        if path == 'sidecar':
            set_field('responsibleParty', 'Luis Romero for service submission and access; Priya Shah for separately verified loaner approval above Luis ceiling; Maya may not commit',
                      'Distinguish service authority from procurement routing')
        samples[path] = {'provenance': {'sourceCapture': source.name, 'sourcePath': path,
            'caseId': call['caseId'], 'requestId': call['requestId'], 'provider': replies[0]['provenance'],
            'model': manifest['model'], 'reasoning': manifest['reasoning'],
            'originalContentSha256': digest(text.encode()),
            'originalRequestSha256': digest(json.dumps(call['request'], sort_keys=True).encode())},
            'original': original, 'candidate': candidate, 'edits': edits}
    return {'formatVersion': 1, 'approved': False, 'status': 'OFFLINE_HAND_EDITED_DIAGNOSTIC',
        'purpose': 'Review examples and contract regression only; not model correction, Framework execution or approved replay',
        'sourceCapture': source.name, 'sourceDisposition': 'REJECTED_FOR_REPLAY',
        'normalization': 'None; original case IDs, quotes and equipment assessments retained',
        'sourceSha256': {name: digest((source / name).read_bytes()) for name in
            ['manifest.json', 'journal.json', 'trace-index.json', 'java-assessment.json',
             'sidecar-assessment.json', 'java-business-records.json', 'python-business-records.json']},
        'samples': samples}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('capture', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.resolve().is_relative_to(args.capture.resolve()):
        parser.error('Write outside the preserved capture')
    value = derive(args.capture)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as out:
        json.dump(value, out, indent=2)
    print('Offline diagnostic derived; approved=false; no provider calls.')


if __name__ == '__main__':
    main()
