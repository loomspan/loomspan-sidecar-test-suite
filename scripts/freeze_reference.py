"""Explicitly freeze one reviewed capture; never promotes a new model run automatically."""
import argparse
import io
import json
from pathlib import Path
import sys
import zipfile

from replay_reference import ROOT, sha, source_hash, contract_hash

sys.path.insert(0, str(ROOT))
from fixtures.replay import request_contract
from fixtures.responses import text_response


def freeze(bundle_raw, report_raw, review, output):
    if output.exists():
        raise ValueError('Reference destination must be new; never overwrite accepted fixtures')
    report = json.loads(report_raw)
    if not (review.get('accepted') and review.get('status') == 'BUSINESS_PASS_WITH_MINOR_CAVEATS'
            and review['runId'] == report['runId'] and review['bundleSha256'] == sha(bundle_raw)
            and review['reportSha256'] == sha(report_raw)):
        raise ValueError('Capture requires its matching accepted business review')
    selected = [case for case in report['cases'] if case['path'] == 'java']
    if (len(selected) != len(report['scenarios'])
            or {case['scenario'] for case in selected} != set(report['scenarios'])
            or any(not case['checks'] or not all(case['checks'].values()) for case in selected)):
        raise ValueError('Expected one complete accepted Java case per scenario')
    files = {}
    manifest = {'formatVersion': 2, 'sourceRunId': report['runId'], 'sourceIntegration': 'java',
                'sourceBundleSha256': sha(bundle_raw), 'sourceReportSha256': sha(report_raw),
                'businessStatus': review['status'], 'reasoning': report['reasoning'],
                'acceptanceBasis': review['acceptanceBasis'], 'nonBlockingCaveats': review['nonBlockingCaveats'],
                'limits': review['limits'], 'scenarios': report['scenarios'],
                'skillModels': {}, 'skillContracts': {}, 'sourceHashes': {}}
    with zipfile.ZipFile(io.BytesIO(bundle_raw)) as z:
        checks = json.loads(z.read('checksums.json'))
        if not all(sha(z.read(n)) == value for n, value in checks.items()):
            raise ValueError('Capture checksum failure')
        if json.loads(z.read('report.json')) != report:
            raise ValueError('Bundle/report mismatch')
        for skill_file in sorted((ROOT / 'config/skills/equipment-service').glob('*.yaml')):
            name = skill_file.stem
            original = z.read('source/config/skills/equipment-service/' + skill_file.name)
            if contract_hash(original) != contract_hash(skill_file.read_bytes()):
                raise ValueError('Business contract differs from accepted capture: ' + name)
            manifest['skillContracts'][name] = contract_hash(original)
            manifest['skillModels'][name] = report['skillModels'].get(name, report['model'])
        for name in ['fixtures/base-case.json', 'fixtures/business.json']:
            original = z.read('source/' + name)
            if source_hash(original) != source_hash((ROOT / name).read_bytes()):
                raise ValueError('Business source differs from accepted capture: ' + name)
            manifest['sourceHashes'][name] = source_hash(original)
        for case in selected:
            name = case['scenario']; prefix = name + '/java/'
            journal = json.loads(z.read(prefix + 'journal.json'))
            requests = [e for e in journal if e['event'] == 'model-request']
            responses = {e['requestId']: e for e in journal if e['event'] == 'model-response'}
            if len(requests) != len(responses):
                raise ValueError('Unpaired provider traffic')
            steps = []
            for event in requests:
                response = responses[event['requestId']]['response']
                if response.get('status') != 'completed':
                    raise ValueError('Only completed Responses results may be frozen')
                messages = [item for item in response['output'] if item['type'] == 'message']
                if len(messages) != 1 or any(p['type'] != 'output_text' for p in messages[0]['content']):
                    raise ValueError('Expected one text result')
                content = ''.join(p['text'] for p in messages[0]['content'])
                json.loads(content)  # The selected run needs no fence/schema correction accommodations.
                contract = request_contract(event['request'])
                if any(s['requestContract'] == contract for s in steps):
                    raise ValueError('Ambiguous reference requests')
                steps.append({'requestContract': contract, 'sourceRequestId': event['requestId'],
                              'sourceResponseSha256': sha(json.dumps(response, sort_keys=True).encode()),
                              'provenance': 'accepted-reference:' + report['runId'],
                              'response': text_response(content, event['request']['model'],
                                                        'replay-' + event['requestId'])})
            terminal = json.loads(z.read(prefix + 'terminal.json'))
            if terminal['status'] != 'COMPLETED':
                raise ValueError('Incomplete accepted case')
            expected = terminal['result']
            if isinstance(expected, str): expected = json.loads(expected)
            files[name + '.json'] = {'caseId': case['caseId'], 'input': json.loads(z.read(prefix + 'input.json')),
                                     'steps': steps, 'expected': expected}
    raw_files = {n: (json.dumps(v, indent=2, ensure_ascii=False) + '\n').encode() for n, v in files.items()}
    manifest['files'] = {n: sha(raw) for n, raw in raw_files.items()}
    output.mkdir(parents=True)
    for n, raw in raw_files.items(): (output / n).write_bytes(raw)
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('capture', type=Path, help='Directory with bundle.zip, report.json and accepted business-review.json')
    parser.add_argument('--output', type=Path, required=True, help='New fixture directory')
    args = parser.parse_args()
    freeze((args.capture / 'bundle.zip').read_bytes(), (args.capture / 'report.json').read_bytes(),
           json.loads((args.capture / 'business-review.json').read_bytes()), args.output)
