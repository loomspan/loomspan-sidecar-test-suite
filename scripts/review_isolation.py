"""Independent gate chronology, case/caller isolation and full source-fidelity review."""
import argparse
import hashlib
import json
from pathlib import Path
from review_reviewed_replay import inspect as replay_review


def inspect(directory):
    d = Path(directory).resolve()
    load = lambda file: json.loads(file.read_bytes())
    checks = []
    def check(path, name, value):
        checks.append({'path': path, 'check': name, 'passed': bool(value)})
    check(None, 'all finalized parent evidence checksums match', all(
        hashlib.sha256((d / name).read_bytes()).hexdigest() == wanted
        for name, wanted in load(d / 'checksums.json').items()))
    reviews = {scenario: replay_review(d / scenario) for scenario in ['baseline', 'priority']}
    for scenario, report in reviews.items():
        checks.extend({**c, 'check': scenario + ': ' + c['check']} for c in report['checks'])
    observations = load(d / 'observations.json')
    check(None, 'two observed integration paths', len(observations)==2 and {o['path'] for o in observations}=={'java','sidecar'})
    for obs in observations:
        path = obs['path']
        base, other = [next(i for i in load(d / scenario / 'manifest.json')['results'] if i['path']==path)
                       for scenario in ['baseline', 'priority']]
        check(path, 'distinct execution cases and verified callers', base['caseId'] != other['caseId'] and
              base['executionId'] != other['executionId'] and base['caller']=='maya' and other['caller']=='luis' and
              obs['blockedCaseId']==base['caseId'] and obs['otherCaseId']==other['caseId'])
        events = load(d / 'baseline' / 'journal.json')
        local = [e for e in events if e.get('caseId')==base['caseId']]
        gates = ['serviceHistory', 'referenceEvidence']
        entered = [e for e in local if e['event']=='entered' and e.get('kind') in gates]
        released = [e for e in local if e['event']=='released' and e.get('name') in gates]
        returned = [e for e in local if e['event']=='returned' and e.get('kind') in gates]
        check(path, 'both eligible reads enter before either gate releases', len(entered)==len(released)==2 and
              {e['kind'] for e in entered}==set(gates) and {e['name'] for e in released}==set(gates) and
              max(e['timeNs'] for e in entered) < min(e['timeNs'] for e in released))
        check(path, 'closed gates prevent both read returns', len(returned)==2 and all(
            next(e['timeNs'] for e in released if e['name']==r['kind']) < r['timeNs'] for r in returned))
        check(path, 'other full case completes while first remains blocked', obs['otherStatus']=='COMPLETED' and
              obs['blockedWhileOtherComplete']['status']=='RUNNING' and
              obs['blockedWhileOtherComplete']['id']==base['executionId'] and
              len(released)==2 and max(e['timeNs'] for e in entered) < obs['timeNs'] < min(e['timeNs'] for e in released) and
              base['status']==other['status']=='COMPLETED')
        check(path, 'cross-caller execution lookup denied both ways', len(obs['crossCallerPolls'])==2 and
              {o['executionId'] for o in obs['crossCallerPolls']}=={base['executionId'],other['executionId']} and
              all(o['httpStatus']==404 for o in obs['crossCallerPolls']))
        storage = 'python' if path=='sidecar' else 'java'
        for scenario, item, other_item in [('baseline', base, other), ('priority', other, base)]:
            folder = d / scenario
            terminal = load(folder / (path + '-assessment.json'))
            records = load(folder / (storage + '-business-records.json'))
            row = [r for r in records['assessments'] if r['version']==terminal['assessmentVersion']]
            check(path, scenario + ' durable assessment belongs to verified caller', len(row)==1 and row[0]['owner']==item['caller'])
            trace_index = [t for t in load(folder / 'trace-index.json') if t['path']==path and item['caseId'] in t['cases']]
            frames = []
            clean = True
            for t in trace_index:
                raw = (folder / t['file']).read_bytes()
                clean = clean and other_item['caseId'].encode() not in raw
                frames.extend(json.loads(line) for line in raw.decode().splitlines())
            roots = [t for t in trace_index if t['entrySkill']=='resolveEquipment' and t['outcome']=='SUCCEEDED']
            ids = {e['frameId'] for e in terminal.get('events',[]) if e.get('frameId')}
            correlated = len(roots)==1 and (roots[0]['sessionId']==terminal['sessionId'] if terminal.get('sessionId') else
                                          bool(ids) and ids.issubset({f.get('frameId') for f in frames}))
            check(path, scenario + ' actual root trace uniquely correlates with no other case data', clean and correlated)
        baseline_expected = load(d / 'baseline' / (path + '-expected.json'))
        priority_expected = load(d / 'priority' / (path + '-expected.json'))
        check(path, 'distinct priority input and recommendations survive isolation',
              any(baseline_expected[k] != priority_expected[k] for k in ['rationale', 'acceptedRisk', 'nextDecision']) and
              load(d / 'baseline' / (path + '-input.json'))['context'] != load(d / 'priority' / (path + '-input.json'))['context'])
    return {'status': 'PASS' if all(c['passed'] for c in checks) else 'FAIL', 'checks': checks,
            'replayReviews': reviews, 'paidCalls': 0,
            'scope': 'Gated concurrent reads and two complete distinct caller/case workflows per application; no capacity/update claim'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('capture', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.resolve().is_relative_to(args.capture.resolve()):
        parser.error('Write outside original capture')
    result = inspect(args.capture)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
    print(result['status'], [(c['path'], c['check']) for c in result['checks'] if not c['passed']])
    raise SystemExit(0 if result['status']=='PASS' else 1)
