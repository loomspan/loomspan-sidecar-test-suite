"""Freeze explicitly reviewed native captures without overwriting any reference."""
import hashlib
import json
import zipfile


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def freeze(captures, review, output):
    """captures maps review source names to completed capture directories."""
    if output.exists():
        raise ValueError('Reference destination must be new')
    if review['status'] != 'ACCEPTED_BY_DELEGATED_REVIEW':
        raise ValueError('Explicit semantic review required')
    cases = []
    for source, directory in captures.items():
        raw = (directory / 'bundle.zip').read_bytes()
        if sha(raw) != review['sources'][source]['bundleSha256']:
            raise ValueError('Reviewed capture hash mismatch')
        with zipfile.ZipFile(directory / 'bundle.zip') as archive:
            checksums = json.loads(archive.read('checksums.json'))
            if any(sha(archive.read(n)) != h for n, h in checksums.items()):
                raise ValueError('Capture checksum mismatch')
            report = json.loads(archive.read('report.json'))
            if (report['suite'] != 'typesafe-ai' or report['model'] != 'jev-1.13.0'
                    or report['status'] != 'CHECKS_PASS_REVIEW_REQUIRED' or not report['runtimeRestored']):
                raise ValueError('Completed restored native capture required')
            for result in report['cases']:
                name = 'reference_' + result['scenario'] + '_' + result['path']
                acceptance = review['accepted'].get(name)
                if acceptance is None or acceptance['source'] != source:
                    continue
                if not result['checks'] or not all(result['checks'].values()) or result.get('executionError'):
                    raise ValueError('Cannot accept a mechanically failing case')
                prefix = result['scenario'] + '/' + result['path']
                original = archive.read(prefix + '/case.json').decode()
                case = json.loads(original.replace(result['caseId'], '__CASE__'))
                journal = json.loads(archive.read(prefix + '/journal.json'))
                responses = [e for e in journal if e['event'] == 'native-response'
                             and e.get('provenance') == 'live TypeSafe' and e['status'] == 200]
                if len(responses) != 1 or responses[0]['response']['answers'] != result['answers']:
                    raise ValueError('Expected one matching real response')
                case.update(name=name, outcome='COMPLETED', expected=result['answers'],
                    usagePrecision='EXACT', coverage=['reviewed-live-replay'],
                    provenance='reviewed-live-typesafe', responses=[{'body': responses[0]['response']}],
                    source={'runId': report['runId'], 'host': result['path'],
                            'caseId': result['caseId'], 'bundleSha256': sha(raw)})
                cases.append(case)
    if len(cases) != len(review['accepted']) or {c['name'] for c in cases} != set(review['accepted']):
        raise ValueError('Review must identify exactly the captured cases to freeze')
    pack = {'model': 'jev-1.13.0', 'origin': 'reviewed-live-typesafe', 'cases': cases}
    raw = (json.dumps(pack, indent=2, ensure_ascii=False) + '\n').encode()
    review = {**review, 'casesSha256': sha(raw)}
    output.mkdir(parents=True)
    (output / 'cases.json').write_bytes(raw)
    (output / 'review.json').write_text(json.dumps(review, indent=2) + '\n', encoding='utf-8')
