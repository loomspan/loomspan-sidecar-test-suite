"""Read-only live-process review; semantic judgment and replay approval are separate."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
from inspect_capture import inspect, mission, system
from review_correction_capture import review as inventory


def canonical(request):
    text = next(m['content'] for m in request['messages'] if m.get('role') == 'user'
                and m.get('content', '').startswith('Mission objective:'))
    return json.JSONDecoder().raw_decode(text.split('Canonical mission input:\n', 1)[1].lstrip())[0]


def contains(node, wanted):
    if node == wanted:
        return True
    if isinstance(node, dict):
        return any(contains(v, wanted) for v in node.values())
    return isinstance(node, list) and any(contains(v, wanted) for v in node)


def contains_source(node, wanted):
    """Independent source records may reorder; missing, changed or duplicate records fail."""
    if not isinstance(wanted, list):
        return contains(node, wanted)
    if isinstance(node, list):
        encode = lambda value: json.dumps(value, sort_keys=True)
        if Counter(map(encode, node)) == Counter(map(encode, wanted)):
            return True
        return any(contains_source(v, wanted) for v in node)
    return isinstance(node, dict) and any(contains_source(v, wanted) for v in node.values())


def source_ids(node):
    found = set()
    if isinstance(node, dict):
        if isinstance(node.get('id'), str):
            found.add(node['id'])
        for value in node.values():
            found.update(source_ids(value))
    elif isinstance(node, list):
        for value in node:
            found.update(source_ids(value))
    return found


def final_response_matches(envelope, expected):
    """Native final synthesis can return the result directly or an action envelope."""
    if not isinstance(envelope, dict) or not isinstance(expected, dict):
        return False
    return envelope == expected or (envelope.get('stepAction') == 'FINAL_RESPONSE'
                                    and envelope.get('finalResponse') == expected)


def planning_checks(plan, skill):
    """Check business dependencies without requiring particular task IDs or prose."""
    tasks = plan.get('tasks', []) if isinstance(plan, dict) else []
    by_id = {t['taskId']: t for t in tasks}
    by_skill = {t['capabilityName']: t for t in tasks}
    def ancestors(name):
        pending = list(by_skill.get(name, {}).get('dependsOn', []))
        seen = set()
        while pending:
            ident = pending.pop()
            if ident in seen:
                continue
            seen.add(ident)
            pending.extend(by_id.get(ident, {}).get('dependsOn', []))
        return {by_id[i]['capabilityName'] for i in seen if i in by_id}
    def parallel(names):
        group = [by_skill.get(n, {}).get('parallelGroup') for n in names]
        return all(group) and len(set(group)) == 1 and all(
            not (ancestors(n) & set(names)) for n in names)
    if skill == 'resolveEquipment':
        evidence = ['serviceHistory', 'referenceEvidence', 'serviceTerms']
        return {
            'root plans all required business responsibilities': set(by_skill) ==
                {'assetContext', *evidence, 'assessEquipment', 'planResolution'} and len(tasks) == 6,
            'independent evidence reads share a parallel group after asset scope': parallel(evidence) and
                all(ancestors(n) == {'assetContext'} for n in evidence),
            'technical assessment depends on technical evidence without commercial reads':
                ancestors('assessEquipment') == {'assetContext', 'serviceHistory', 'referenceEvidence'},
            'resolution waits for assessment and commercial terms':
                {'assessEquipment', 'serviceTerms'} <= ancestors('planResolution'),
        }
    evidence = ['entitlements', 'serviceResources', 'continuityOptions']
    return {
        'nested plan checks resources and continuity before recommendation': set(by_skill) ==
            {*evidence, 'quoteOptions', 'compareOptions'} and len(tasks) == 5,
        'independent option checks share a parallel group': parallel(evidence),
        'quotes wait for applicable entitlement and resource checks':
            {'entitlements', 'serviceResources'} <= ancestors('quoteOptions'),
        'comparison waits for authoritative quotes and all checked options':
            {*evidence, 'quoteOptions'} <= ancestors('compareOptions'),
    }


def review(directory, before_directory, paths=('java', 'sidecar'), expected_profile=None):
    directory, before_directory = Path(directory).resolve(), Path(before_directory).resolve()
    selected_paths = tuple(paths)
    base = inspect(directory, selected_paths, expected_profile)
    checks = base['checks']
    def check(path, name, passed):
        checks.append({'path': path, 'check': name, 'passed': bool(passed)})
    def read(name):
        return json.loads((directory / name).read_text(encoding='utf-8'))
    manifest, events = read('manifest.json'), read('journal.json')
    check(None, 'finalized capture hashes remain exact', all(
        (directory / name).resolve().is_relative_to(directory) and
        hashlib.sha256((directory / name).read_bytes()).hexdigest() == expected
        for name, expected in read('checksums.json').items()))
    check(None, 'two distinct complete live cases' if len(selected_paths) == 2 else 'one selected live case',
          len(manifest['results']) == len(selected_paths) and
          {r['path'] for r in manifest['results']} == set(selected_paths) and
          len({r['caseId'] for r in manifest['results']}) == len(selected_paths))
    check(None, 'selected live profile matches requested model and reasoning' if expected_profile else 'selected live profile is Muse with medium reasoning',
          all(manifest.get(k) == v for k, v in (expected_profile or
              {'model': 'meta/muse-spark-1.3-contributor', 'reasoning': 'medium'}).items()))
    try:
        provenance = inventory(directory)
    except (StopIteration, KeyError, AssertionError, ValueError) as error:
        provenance = {'error': type(error).__name__}
        check(None, 'complete trace-correlated model inventory available', False)
    paths = {}
    for selected in manifest['results']:
        path, case = selected['path'], selected['caseId']
        storage = 'python' if path == 'sidecar' else 'java'
        local = [e for e in events if e.get('caseId') == case]
        requests = [e for e in local if e['event'] == 'model-request']
        responses = {e['requestId']: e for e in local if e['event'] == 'model-response'}
        returned = {e['kind']: e['result']['data'] for e in local if e['event'] == 'returned'}
        terminal = read(path + '-assessment.json')
        try:
            value = json.loads(terminal.get('result', '{}'))
        except (ValueError, TypeError):
            value = {}
        def calls(skill):
            return [e for e in requests if mission(e['request'], skill)]
        def decoded_response(event):
            try:
                return json.loads(responses[event['requestId']]['response']['choices'][0]['message']['content'])
            except (KeyError, ValueError, TypeError):
                return None
        assessment = next((v for e in reversed(calls('assessEquipment'))
                           if isinstance(v := decoded_response(e), dict)), None)
        comparisons = calls('compareOptions')
        comparison = next((v for e in reversed(comparisons)
                           if isinstance(v := decoded_response(e), dict)), None)
        for skill in ['resolveEquipment', 'planResolution']:
            plans = [v for e in calls(skill) if isinstance(v := decoded_response(e), dict) and 'tasks' in v]
            for name, passed in planning_checks(plans[-1] if plans else {}, skill).items():
                check(path, name, passed)
        check(path, 'all four model responsibilities use live responses', all(calls(s) for s in
              ['resolveEquipment', 'assessEquipment', 'planResolution', 'compareOptions']) and
              all(e.get('provenance') == 'live OpenRouter' for e in responses.values()))
        check(path, 'both parents genuinely return unchanged actual comparison', comparison and
              all(any('All required plan tasks are already COMPLETE.' in system(e['request']) and
                      final_response_matches(decoded_response(e), comparison) for e in calls(skill))
                  for skill in ['planResolution', 'resolveEquipment']) and value == comparison)
        for kind in ['assetContext', 'serviceHistory', 'referenceEvidence']:
            check(path, 'complete ' + kind + ' reaches actual assessment input',
                  kind in returned and calls('assessEquipment') and all(
                      contains_source(canonical(e['request']), returned[kind]) for e in calls('assessEquipment')))
        for kind in ['assetContext', 'serviceHistory', 'referenceEvidence', 'serviceTerms',
                     'entitlements', 'serviceResources', 'continuityOptions']:
            check(path, 'complete ' + kind + ' reaches actual comparison input',
                  kind in returned and comparisons and all(
                      contains_source(canonical(e['request']), returned[kind]) for e in comparisons))
        check(path, 'actual child assessment copied unchanged into comparison input and output',
              assessment and comparison and comparisons and all(
                  contains(canonical(e['request']), assessment) for e in comparisons) and
              comparison.get('equipmentAssessment') == assessment)
        context = read(path + '-input.json')['context']
        check(path, 'operating priorities survive into comparison mission', comparisons and all(
              all(contains(canonical(e['request']), v) for v in context.values()) for e in comparisons))
        ids = source_ids(returned)
        citations = value.get('citations', [])
        child_citations = assessment.get('citations', []) if assessment else []
        citation_tokens = re.compile(r'(?:MAN-\d+\.\d+|SB-\d+|[WS]-\d+|WO-\d+|NOTE-\d+|MAINT-\d+|INCIDENT-\d+|ASSET-\d+|AUTH-NB|SITE-WEST|CONTACT-[A-Z]+|WC-\d+|SA-NB-\d+|RATE-\d+|PARTS-\d+|SLOT-(?:EXP|STD)-\d+|LOAN-\d+|REPLACE-\d+|RESOURCES-\d+|CONTINUITY-\d+|FINDINGS-\d+)')
        references = [token for citation in citations + child_citations for token in citation_tokens.findall(citation)]
        check(path, 'cited source identifiers exist in actual returned evidence',
              citations and child_citations and references and
              all(citation_tokens.findall(c) for c in citations + child_citations) and
              all(token in ids for token in references))
        check(path, 'commercial citation coverage independently present', all(
              any(clause in citation_tokens.findall(c) for c in citations)
              for clause in ['W-2', 'W-5', 'S-3', 'S-4', 'S-5']))
        check(path, 'comparison citations have no duplicate entries',
              citations and len(set(citations)) == len(citations))
        before = json.loads((before_directory / (storage + '-business-records.json')).read_text(encoding='utf-8'))
        after = read(storage + '-business-records.json')
        check(path, 'all prior durable records remain byte-equivalent as decoded rows', all(
              row in after[table] for table in ['assessments', 'quotes', 'requests'] for row in before[table]))
        check(path, 'requests unchanged across live assessment phase', before['requests'] == after['requests'])
        check(path, 'exactly one new immutable assessment for this case',
              sum(json.loads(row['body']).get('caseId') == case for row in after['assessments']) == 1)
        check(path, 'durable assessment retains authenticated Maya ownership and asset', any(
              row['version'] == terminal.get('assessmentVersion') and row['owner'] == 'maya' and
              row['asset'] == 'NB-P240-017' for row in after['assessments']))
        check(path, 'published disposition preserves authorization boundary',
              value.get('disposition') in ['AWAITING_APPROVAL', 'ESCALATE', 'NEEDS_INFORMATION'])
        x = provenance.get('paths', {}).get(path, {})
        check(path, 'every provider response matches actual Framework trace', x.get('providerContentsMatchFrameworkTrace'))
        roots = [t for t in x.get('traces', []) if t.get('entrySkill') == 'resolveEquipment']
        frame_ids = {e['frameId'] for e in terminal.get('events', []) if e.get('frameId')}
        actual_ids = {json.loads(line).get('frameId') for t in roots
                      for line in (directory / t['file']).read_text(encoding='utf-8').splitlines() if line}
        check(path, 'public execution uniquely correlates to actual root trace', len(roots) == 1 and
              (roots[0]['sessionId'] == terminal['sessionId'] if terminal.get('sessionId') else
               bool(frame_ids) and frame_ids.issubset(actual_ids)))
        paths[path] = {'caseId': case, 'selectedOption': value.get('selectedOption'),
                       'disposition': value.get('disposition'), 'citations': citations,
                       'sourceIds': sorted(ids), 'modelRequests': len(requests),
                       'reportedProviderCost': x.get('reportedProviderCost'),
                       'durationSeconds': x.get('durationSeconds')}
    return {'status': 'NEEDS_SEMANTIC_REVIEW' if all(c['passed'] for c in checks) else 'FAIL',
            'capture': str(directory), 'beforeCapture': str(before_directory), 'checks': checks,
            'paths': paths, 'inventory': provenance, 'approvedForReplay': False,
            'scope': 'Fresh complete live business process; mechanical review is not semantic approval.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('capture', type=Path)
    parser.add_argument('--before', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.resolve().is_relative_to(args.capture.resolve()):
        parser.error('Write reviews outside original capture')
    result = review(args.capture, args.before)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as file:
        json.dump(result, file, indent=2)
    print(result['status'], [(c['path'], c['check']) for c in result['checks'] if not c['passed']])
    raise SystemExit(result['status'] == 'FAIL')
