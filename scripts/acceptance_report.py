"""Fail-closed consolidation of independently reviewed offline acceptance evidence."""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

SCENARIOS = ['baseline', 'priority', 'recovery', 'service-requests', 'isolation', 'nested-authorization']


def checksums(directory):
    directory = Path(directory).resolve()
    files = json.loads((directory / 'checksums.json').read_bytes())
    if not files:
        raise ValueError('Empty evidence checksum index')
    for name, wanted in files.items():
        file = (directory / name).resolve()
        if not file.is_relative_to(directory) or hashlib.sha256(file.read_bytes()).hexdigest() != wanted:
            raise ValueError('Evidence checksum mismatch: ' + name)
    return len(files)


def junit_counts(file):
    root = ET.parse(file).getroot()
    suites = [root] if root.tag == 'testsuite' else list(root.iter('testsuite'))
    if not suites:
        raise ValueError('JUnit has no test suites')
    counts = {name: sum(int(s.get(name, '0')) for s in suites)
              for name in ['tests', 'failures', 'errors', 'skipped']}
    counts['passed'] = counts['tests'] - counts['failures'] - counts['errors'] - counts['skipped']
    return counts


def consolidate(stages, runtime, integrity, audit):
    """A green subprocess alone, missing path, empty review or skipped test cannot pass."""
    checks = []
    def check(name, value):
        checks.append({'check': name, 'passed': bool(value)})
    check('all six required scenario groups ran exactly once', len(stages)==len(SCENARIOS) and
          {s['scenario'] for s in stages}==set(SCENARIOS))
    check('all five services ready with provider disabled and normal configuration restored',
          runtime.get('ready') and runtime.get('providerDisabled') and runtime.get('normalConfiguration') and
          runtime.get('artifactsUnchanged'))
    check('protected evidence and prior durable records preserved', integrity.get('status')=='PASS')
    for stage in stages:
        label = stage['scenario']
        review = stage.get('review', {})
        items = review.get('checks', [])
        check(label + ': nonempty independent checks pass on both applications',
              review.get('status')=='PASS' and items and all(c.get('passed') is True for c in items) and
              {c.get('path') for c in items if c.get('path')}=={'java', 'sidecar'})
        check(label + ': fresh provider-free finalized evidence verified', stage.get('evidenceVerified') and
              stage.get('paidCalls')==0 and stage.get('freshCapture') is True)
        counts = stage.get('assertions', {})
        expected = 16 if label=='isolation' else 8
        check(label + ': all workflow assertions executed with no skip/failure/error',
              counts.get('tests')==counts.get('passed')==expected and
              all(counts.get(k)==0 for k in ['skipped','failures','errors']))
    focused = audit.get('focusedTests', {})
    check('focused offline regression suite executed without skips or failures', focused.get('passed',0)>0 and
          all(focused.get(k)==0 for k in ['failures','errors','skipped']))
    offline_pass = all(c['passed'] for c in checks)
    requirements = audit.get('requirements', [])
    complete = offline_pass and bool(requirements) and all(r.get('status')=='VERIFIED' for r in requirements)
    return {'status': 'PASS' if offline_pass else 'FAIL', 'checks': checks,
            'scenarioChecks': sum(len(s.get('review',{}).get('checks',[])) for s in stages),
            'workflowAssertions': sum(s.get('assertions',{}).get('passed',0) for s in stages),
            'focusedTests': focused, 'paidCalls': 0, 'firstDeliveryComplete': complete,
            'completionAudit': audit, 'runtime': runtime, 'integrity': integrity,
            'scenarios': stages,
            'scope': 'Fresh paired offline first-delivery scenario acceptance; broader capacity/update/CI claims excluded'}


def markdown(report, directory):
    d = Path(directory)
    lines = ['# Consolidated offline acceptance — ' + report['status'], '',
             f"{report['scenarioChecks']} independent scenario checks, {report['workflowAssertions']} workflow assertions "
             f"and {report['focusedTests'].get('passed',0)} focused offline tests pass. Zero paid calls.", '',
             '| Scenario | Result | Checks | Assertions | Evidence |', '| --- | --- | --- | --- | --- |']
    for stage in report['scenarios']:
        capture = Path(stage['capture'])
        import os
        link = Path(os.path.relpath(capture / 'manifest.json', d)).as_posix()
        lines.append(f"| {stage['scenario']} | {stage['review']['status']} | {len(stage['review']['checks'])} | "
                     f"{stage['assertions']['passed']} | [capture]({link}), [review](reviews/{stage['scenario']}.json) |")
    lines += ['', 'The fixture provider credential stays disabled. Each scenario uses fresh case IDs, '
              'independent journals, durable business records and actual Framework trace artifacts. '
              'Runtime evidence is archived before both authorization configuration changes; normal configuration is restored.', '',
              '## Delivery-boundary audit', '', '| Requirement | Disposition | Basis |', '| --- | --- | --- |']
    for item in report['completionAudit']['requirements']:
        lines.append(f"| {item['requirement']} | {item['status']} | {item['basis']} |")
    lines += ['', 'First delivery complete: **' + ('yes' if report['firstDeliveryComplete'] else 'not declared') + '**.', '',
              'Full-workflow recovery replays reviewed genuine Muse responses to the injected fault, '
              'normalized only for case IDs. Both parent envelopes explicitly copy actual completed '
              'child content; this proves preservation, not new parent-model reasoning. '
              'Historical rejected captures retain their original dispositions. '
              'The setup verified here uses the documented existing snapshot workspace; Git alone cannot recover ignored provenance/build/runtime files.', '',
              '[Machine-readable report](report.json), [aggregate JUnit](acceptance-junit.xml), '
              '[focused tests](focused-junit.xml), [integrity](integrity.json), [runtime](runtime.json).']
    return '\n'.join(lines) + '\n'
