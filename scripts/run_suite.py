"""Four explicit run modes: mock, live, evaluate, and capture."""
import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import uuid
import xml.etree.ElementTree as ET
import yaml
import environment as runtime
from capture import run as capture
from finalize_evidence import finalize
from readiness import ready
from review_fresh_live import review
from run_diagnostics import diagnose, render

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL = 'meta/muse-spark-1.3-contributor'


def write(file, value):
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def command(args, **kwargs):
    subprocess.run(args, cwd=ROOT, check=True, **kwargs)


def safe_error(error):
    text = str(error)
    file = ROOT / '.runtime/secrets.json'
    secrets = list(json.loads(file.read_bytes()).values()) if file.exists() else []
    secrets += [v for k, v in os.environ.items() if ('API_KEY' in k or 'TOKEN' in k) and v]
    for value in secrets:
        if value: text = text.replace(value, '[REDACTED]')
    return text


def preserve():
    command([sys.executable, 'scripts/preserve_runtime.py', '--no-package-copy'])


def make_overlay(directory, paths, model, reasoning):
    """Override only model settings in private copies; preserve authored YAML bytes otherwise."""
    directory.mkdir(parents=True, exist_ok=True)
    services = {'fixtures': {'environment': {'OPENROUTER_API_KEY': '${LOOMSPAN_OPENROUTER_API_KEY:?Provider key required}'}}}
    skills = directory / 'skills'; skills.mkdir()
    for source in (ROOT / 'config/skills').glob('*.yaml'):
        text = source.read_text(encoding='utf-8')
        text = re.sub(r'^thinking_level:.*\n', '' if reasoning is None else 'thinking_level: ' + reasoning + '\n', text, flags=re.M)
        (skills / source.name).write_text(text, encoding='utf-8')
    for path in paths:
        config = yaml.safe_load((ROOT / 'config' / (path + '.yaml')).read_text(encoding='utf-8'))
        config['loomspan']['models']['reasoning'].update({'provider-model': model, 'thinking-levels': [reasoning] if reasoning else []})
        file = directory / (path + '.yaml'); file.write_text(yaml.safe_dump(config, sort_keys=False), encoding='utf-8')
        services[path] = {'volumes': [file.as_posix() + ':/config/runtime.yaml:ro', skills.as_posix() + ':/config/skills:ro']}
    overlay = directory / 'compose.yaml'; overlay.write_text(yaml.safe_dump({'services': services}), encoding='utf-8')
    return overlay


@contextmanager
def live_runtime(directory, paths, model, reasoning):
    if not os.getenv('LOOMSPAN_OPENROUTER_API_KEY'):
        raise ValueError('Set LOOMSPAN_OPENROUTER_API_KEY before a live run')
    if os.getenv('LOOMSPAN_RUN_OVERLAY') or os.getenv('LOOMSPAN_MODEL_CONFIG_DIRECTORY'):
        raise ValueError('A run overlay is already active')
    overlay = make_overlay(directory, paths, model, reasoning)
    preserve()
    try:
        os.environ['LOOMSPAN_RUN_OVERLAY'] = str(overlay)
        os.environ['LOOMSPAN_MODEL_CONFIG_DIRECTORY'] = str(directory)
        command(runtime.compose() + ['up', '-d', '--no-deps', '--force-recreate', 'fixtures', *paths])
        ready()
        yield
    finally:
        # Attempt preservation first, but always restore provider-disabled normal hosts.
        try:
            preserve()
        finally:
            os.environ.pop('LOOMSPAN_RUN_OVERLAY', None)
            os.environ.pop('LOOMSPAN_MODEL_CONFIG_DIRECTORY', None)
            command(runtime.compose() + ['up', '-d', '--no-deps', '--force-recreate', 'fixtures', *paths])
            ready()
            from capture_reviewed_replay import require_offline_provider
            require_offline_provider()


def checked_review(directory, before, paths, profile):
    try:
        result = review(directory, before, paths, profile)
        manifest = json.loads((directory / 'manifest.json').read_bytes())
        if manifest.get('collectionError'):
            result['checks'].append({'path': None, 'check': 'complete evidence collection', 'passed': False})
            result['status'] = 'FAIL'
        return result
    except (KeyError, ValueError, TypeError, IndexError, StopIteration, OSError, AssertionError) as error:
        # Failed/incomplete captures are retained and count as failures, never as skipped tests.
        from inspect_capture import inspect
        try:
            checks = inspect(directory, paths, profile)['checks']
        except (KeyError, ValueError, TypeError, IndexError, OSError):
            checks = []
        return {'status': 'FAIL', 'checks': checks + [{'path': None, 'check': 'complete process review: ' + type(error).__name__, 'passed': False}], 'approvedForReplay': False}


def observations(directory):
    events = json.loads((directory / 'journal.json').read_bytes())
    requests = [e for e in events if e['event'] == 'model-request']
    responses = [e for e in events if e['event'] == 'model-response']
    malformed = []
    for event in responses:
        body = event.get('response') or {}
        choices = body.get('choices') if isinstance(body, dict) else None
        if not isinstance(body, dict) or event.get('status') != 200 or body.get('error') or not choices:
            continue
        if not isinstance(choices, list) or not isinstance(choices[0], dict):
            continue
        if choices[0].get('error') or choices[0].get('finish_reason') == 'error':
            continue
        try:
            json.loads(event['response']['choices'][0]['message']['content'])
        except (KeyError, IndexError, ValueError, TypeError):
            malformed.append(event['requestId'])
    bodies = [e['response'] for e in responses if isinstance(e.get('response'), dict)]
    return {'providerCalls': len(requests),
            'providerHttpFailures': [{'requestId': e['requestId'], 'status': e.get('status')} for e in responses if e.get('status') != 200],
            'transportFailures': sum(e['event'] == 'provider-transport-failure' for e in events),
            'invalidJsonResponseIds': malformed,
            'returnedModels': sorted({str(body.get('model', 'unknown')) for body in bodies}),
            'reportedCost': sum((body.get('usage') or {}).get('cost', 0) or 0 for body in bodies),
            'note': 'Observed symptoms; framework, provider, prompt and model responsibility require trace review.'}


def summary(out, report):
    for stage in report['stages']:
        if stage['scenario'] in ['baseline', 'priority'] and 'diagnostics' not in stage:
            try:
                stage['diagnostics'] = diagnose(stage['capture'], report['paths'], stage['review'])
            except (OSError, ValueError, KeyError, TypeError, IndexError, AttributeError) as error:
                # Diagnostic gaps must never prevent the original results being written.
                stage['diagnosticError'] = type(error).__name__
    write(out / 'report.json', report)
    suite = ET.Element('testsuite', name=report['mode'])
    lines = ['# ' + report['mode'] + ': ' + report['status'], '',
             'Model: ' + report['model'], 'Integrations: ' + ', '.join(report['paths']), '',
             'All model responses in live captures come from the selected provider model.',
             'Controlled fault/authorization regression scripts remain in mock acceptance.',
             'Passing automated checks still requires semantic review before fixture replacement.', '']
    if report.get('diagnosticReanalysis'):
        source = Path(report['diagnosticReanalysis']['sourceReport']).as_posix()
        lines += ['Offline diagnostic reanalysis of [the original report](<' + source + '>). '
                  'No new execution or semantic review. Restoration status below is historical.', '']
    lines += ['Runtime restoration: ' + ('confirmed; provider access disabled' if report.get('runtimeRestored')
                                       else 'not confirmed (run in progress or runner failed)'), '',
              '## Diagnostic overview', '',
              'Read each scenario\'s investigation category before its assertion list. '
              'Provider errors and exhausted corrections can propagate as Framework exceptions; '
              'that alone does not make them Framework defects. Timeouts identify a limit, not who is at fault.', '']
    for stage in report['stages']:
        lines += ['## ' + stage['scenario'], '', 'Capture: ' + stage['capture'], '']
        lines += render(stage)
        if stage.get('diagnosticError'):
            lines += ['Diagnostic analysis failed: ' + stage['diagnosticError'] + '. Attribution is unknown.', '']
        failed = sum(not c['passed'] for c in stage['review']['checks'])
        lines += ['Automated checks: ' + str(len(stage['review']['checks']) - failed) + ' passed, '
                  + str(failed) + ' failed.', '', '<details>', '<summary>All failed checks (including downstream consequences)</summary>', '']
        for check in stage['review']['checks']:
            name = str(check.get('path') or 'run') + ': ' + check['check']
            test = ET.SubElement(suite, 'testcase', classname=stage['scenario'], name=name)
            if not check['passed']:
                ET.SubElement(test, 'failure', message=name)
                lines.append('- FAIL: ' + name)
        lines += ['', '</details>', '']
    if report.get('errorType'):
        test = ET.SubElement(suite, 'testcase', name='runner completed and restored runtime')
        ET.SubElement(test, 'error', message=report['errorType'])
        lines += ['', 'Runner / environment / restoration error (separate from model quality): '
                  + report['errorType'] + ': ' + report.get('error', '')]
    suite.set('tests', str(len(suite)))
    suite.set('failures', str(sum(t.find('failure') is not None for t in suite)))
    suite.set('errors', str(sum(t.find('error') is not None for t in suite)))
    ET.ElementTree(suite).write(out / 'junit.xml', encoding='utf-8', xml_declaration=True)
    (out / 'summary.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def run_live(args):
    paths = ('java', 'sidecar') if args.mode != 'evaluate' else (args.path,)
    profile = {'model': args.model, 'reasoning': None if args.reasoning == 'none' else args.reasoning}
    ident = time.strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:6]
    out = ROOT / 'evidence' / (args.mode + '-suite-' + ident); out.mkdir(parents=True)
    report = {'mode': args.mode, **profile, 'paths': paths, 'status': 'FAIL', 'stages': [],
              'coverage': ['baseline', 'priority', 'service-requests'], 'semanticReview': 'PENDING', 'activated': False}
    try:
        with live_runtime(ROOT / '.runtime/model-runs' / ident, paths, **profile):
            before = out / 'before'; before.mkdir(); finalize(before)
            for scenario in ['baseline', 'priority']:
                print('Live scenario: ' + scenario, flush=True)
                directory = capture('both' if len(paths) == 2 else paths[0], scenario == 'priority', len(paths) == 2)
                result = checked_review(directory, before, paths, profile)
                report['stages'].append({'scenario': scenario, 'capture': str(directory), 'review': result,
                                        'observations': observations(directory)})
                summary(out, report)
                before = directory
            base = report['stages'][0]
            if base['review']['status'] == 'NEEDS_SEMANTIC_REVIEW':
                from capture_service_requests import run as service_requests
                from review_service_requests import inspect as service_review
                directory = service_requests(Path(base['capture']), paths)
                result = service_review(directory, paths)
                report['stages'].append({'scenario': 'service-requests', 'capture': str(directory), 'review': result})
            else:
                report['stages'].append({'scenario': 'service-requests', 'capture': base['capture'],
                    'review': {'status': 'FAIL', 'checks': [{'path': None, 'check': 'valid live baseline required for service approval', 'passed': False}]}})
        report['runtimeRestored'] = True
        if len(report['stages']) == 3 and all(s['review']['status'] in ['NEEDS_SEMANTIC_REVIEW', 'PASS'] for s in report['stages']):
            report['status'] = 'AUTOMATED_CHECKS_PASS'
    except Exception as error:
        report['errorType'] = type(error).__name__
        report['error'] = safe_error(error)
    finally:
        summary(out, report)
        print(out / 'summary.md', flush=True)
    if args.mode == 'capture' and report['status'] == 'AUTOMATED_CHECKS_PASS':
        template = {'suiteReportSha256': hashlib.sha256((out / 'report.json').read_bytes()).hexdigest(), 'captures': {}}
        for stage in report['stages']:
            if stage['scenario'] not in ['baseline', 'priority']: continue
            source = Path(stage['capture'])
            template['captures'][source.name] = {
                'checksumsSha256': hashlib.sha256((source / 'checksums.json').read_bytes()).hexdigest(),
                'paths': {path: {'status': 'PENDING', 'rationale': '',
                                'reviewAreas': ['evidence fidelity', 'diagnosis uncertainty', 'commercial constraints and citations',
                                                'feasible alternatives', 'priority responsiveness']} for path in paths}}
        write(out / 'semantic-review-template.json', template)
        print('Capture complete. Review business semantics, then use scripts/refresh_replay.py with this report and a bound semantic review.', flush=True)
    return 0 if report['status'] == 'AUTOMATED_CHECKS_PASS' else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['mock', 'live', 'evaluate', 'capture'])
    parser.add_argument('--model', default=DEFAULT_MODEL)
    parser.add_argument('--reasoning', choices=['none', 'minimal', 'low', 'medium', 'high', 'xhigh'], default='medium', help='none omits thinking_level and provider reasoning_effort')
    parser.add_argument('--path', choices=['java', 'sidecar'], help='evaluate only; defaults to java')
    args = parser.parse_args()
    if not args.model.strip() or '\n' in args.model or '\r' in args.model:
        parser.error('--model must be a nonempty model identifier')
    if args.path and args.mode != 'evaluate': parser.error('--path is only valid for evaluate')
    if args.mode == 'mock' and (args.model != DEFAULT_MODEL or args.reasoning != 'medium'):
        parser.error('mock replays the selected fixture set; model settings apply only to live modes')
    args.path = args.path or 'java'
    lock = ROOT / '.runtime/run-suite.lock'; lock.parent.mkdir(exist_ok=True)
    try:
        handle = lock.open('x')
    except FileExistsError:
        parser.error('Another suite owns .runtime/run-suite.lock; inspect its process before removing a stale lock')
    try:
        with handle:
            handle.write(str(os.getpid())); handle.flush()
            if args.mode == 'mock':
                return subprocess.run([sys.executable, 'scripts/run_acceptance.py'], cwd=ROOT).returncode
            return run_live(args)
    finally:
        lock.unlink()


if __name__ == '__main__':
    raise SystemExit(main())
