"""One runner: mock, live, evaluate and capture. No variant registry or historical inputs."""
import argparse
import copy
from collections import Counter
from contextlib import contextmanager
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import tempfile
import time
import uuid
import zipfile

import httpx
import yaml
import environment
from baseline import baseline
from login import login
from readiness import ready
from smoke import require_offline_provider
import scenarios

ROOT = Path(__file__).resolve().parents[1]
PORTS = {'java': 18081, 'sidecar': 18082}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def json_bytes(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + '\n').encode('utf-8')


class Bundle:
    def __init__(self, secrets):
        self.secrets = [s for s in secrets if s]
        self.files = {}

    def add(self, name, value):
        raw = value if isinstance(value, bytes) else json_bytes(value)
        if any(s.encode() in raw for s in self.secrets):
            raise ValueError('Credential detected; artifact refused: ' + name)
        self.files[name] = raw

    def error(self, error):
        text = type(error).__name__ + ': ' + str(error)
        for secret in self.secrets:
            text = text.replace(secret, '[REDACTED]')
        return text


@contextmanager
def run_lock():
    path = ROOT / '.runtime/run-suite.lock'
    path.parent.mkdir(exist_ok=True)
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        raise RuntimeError('Runner lock exists. Check for an active run before manually removing a stale lock.') from None
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump({'pid': os.getpid()}, f)
        yield
    finally:
        path.unlink()


def command(args):
    # Do not echo Compose configuration or environment: they contain local credentials.
    subprocess.run(args, cwd=ROOT, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def make_overlay(directory, paths, model, reasoning, skill_models=None):
    skill_models = skill_models or {}
    skills = directory / 'skills'
    skills.mkdir()
    for source in (ROOT / 'config/skills').glob('*.yaml'):
        text = source.read_text(encoding='utf-8')
        text = re.sub(r'^thinking_level:.*\n', '' if reasoning == 'none' else 'thinking_level: ' + reasoning + '\n', text, flags=re.M)
        if source.stem in skill_models:
            text = re.sub(r'^model:.*$', 'model: trial-' + source.stem, text, flags=re.M)
        (skills / source.name).write_text(text, encoding='utf-8')
    services = {'fixtures': {'environment': {'OPENROUTER_API_KEY': '${LOOMSPAN_OPENROUTER_API_KEY:?Provider key required}'}}}
    for path in paths:
        config = yaml.safe_load((ROOT / 'config' / (path + '.yaml')).read_text(encoding='utf-8'))
        config['loomspan']['models']['reasoning'].update({'provider-model': model, 'thinking-levels': [] if reasoning == 'none' else [reasoning]})
        for skill, provider_model in skill_models.items():
            alias = 'trial-' + skill
            if alias in config['loomspan']['models']:
                raise ValueError('Trial model alias already exists: ' + alias)
            config['loomspan']['models'][alias] = copy.deepcopy(config['loomspan']['models']['reasoning'])
            config['loomspan']['models'][alias]['provider-model'] = provider_model
        target = directory / (path + '.yaml')
        target.write_text(yaml.safe_dump(config, sort_keys=False), encoding='utf-8')
        services[path] = {'volumes': [target.as_posix() + ':/config/runtime.yaml:ro', skills.as_posix() + ':/config/skills:ro']}
    overlay = directory / 'compose.yaml'
    overlay.write_text(yaml.safe_dump({'services': services}), encoding='utf-8')
    return overlay


def verify_mounted(directory, paths):
    for path in paths:
        pairs = [(directory / (path + '.yaml'), '/config/runtime.yaml')]
        pairs += [(f, '/config/skills/' + f.name) for f in (directory / 'skills').glob('*.yaml')]
        for source, mounted in pairs:
            actual = subprocess.check_output(environment.execute(path, 'cat', mounted))
            if yaml.safe_load(actual) != yaml.safe_load(source.read_bytes()):
                raise ValueError('Mounted configuration mismatch: ' + path + '/' + source.name)


@contextmanager
def live_runtime(directory, paths, model, reasoning, report, skill_models=None):
    if os.getenv('LOOMSPAN_RUN_OVERLAY') or os.getenv('LOOMSPAN_MODEL_CONFIG_DIRECTORY'):
        raise RuntimeError('An external runtime overlay is already active')
    require_offline_provider()
    overlay = make_overlay(directory, paths, model, reasoning, skill_models)
    report['runtimeRestored'] = False
    try:
        os.environ['LOOMSPAN_RUN_OVERLAY'] = str(overlay)
        command(environment.compose() + ['up', '-d', '--no-deps', '--force-recreate', 'fixtures', *paths])
        ready()
        verify_mounted(directory, paths)
        yield
    finally:
        os.environ.pop('LOOMSPAN_RUN_OVERLAY', None)
        command(environment.compose() + ['up', '-d', '--no-deps', '--force-recreate', 'fixtures', *paths])
        ready()
        require_offline_provider()
        report['runtimeRestored'] = True


def database(path):
    host = 'python' if path == 'sidecar' else path
    file = ROOT / '.runtime' / host / 'equipment.db'
    with sqlite3.connect('file:' + file.as_posix() + '?mode=ro', uri=True) as db:
        db.row_factory = sqlite3.Row
        return {t: [dict(r) for r in db.execute('SELECT * FROM ' + t)] for t in ['assessments', 'quotes', 'requests']}


def row_hashes(rows):
    return {t: {digest(json.dumps(r, sort_keys=True).encode()) for r in rs} for t, rs in rows.items()}


def wait(client, api, ident, headers, timeout):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        response = client.get(api + '/assessments/' + ident, headers=headers)
        response.raise_for_status()
        value = response.json()
        if value.get('status') in ['COMPLETED', 'FAILED', 'CANCELLED']:
            return value
        time.sleep(.5)
    raise TimeoutError('Assessment exceeded the configured mission timeout plus collection grace')


def trace_for(client, path, case, observer, bundle, prefix):
    port = 18081 if path == 'java' else 18083
    base = environment.url(port, '/_loomspan/observability/v1')
    headers = {'X-loomspan-Api-Key': observer}
    response = client.get(base + '/traces', headers=headers)
    response.raise_for_status()
    page = response.json()
    if page.get('nextCursor') or page.get('nextPageToken'):
        raise ValueError('Trace listing is paginated; capture cannot claim completeness')
    roots = []
    for item in page['items']:
        if item.get('entrySkill') != 'resolveEquipment':
            continue
        response = client.get(base + '/traces/' + item['traceId'] + '/artifact', headers=headers)
        response.raise_for_status()
        raw = response.content
        if case.encode() in raw:
            roots.append(raw)
    if len(roots) != 1:
        raise ValueError('Expected one correlated resolveEquipment trace')
    bundle.add(prefix + '/trace.ndjson', roots[0])
    return [json.loads(line) for line in roots[0].splitlines()]


def usage(events, trace):
    calls = [e for e in events if e['event'] == 'model-request']
    responses = [e for e in events if e['event'] == 'model-response']
    values = [e.get('response', {}).get('usage', {}) for e in responses]
    result = {'modelCalls': len(calls), 'responseCount': len(responses),
              'reportedCost': float(sum(Decimal(str(v['cost'])) for v in values)) if values and all(v.get('cost') is not None for v in values) else None,
              'directDispatches': sum(r['recordType'] == 'STEP_STARTED' and r.get('metadata', {}).get('dispatchOrigin') == 'framework' for r in trace),
              'rejectedActions': sum(r['recordType'] == 'STEP_ACTION_REJECTED' for r in trace),
              'failedModelAttempts': sum(r['recordType'] == 'MODEL_ATTEMPT_FAILED' for r in trace),
              'planRetries': sum(r['recordType'] == 'PLAN_RETRY_REQUESTED' for r in trace),
              'traceSeconds': max(r['timestamp'] for r in trace) - min(r['timestamp'] for r in trace) if trace else None}
    for field in ['prompt_tokens', 'completion_tokens']:
        result[field] = sum(v[field] for v in values) if values and all(field in v for v in values) else None
    return result


def model_assignment_matches(calls, trace, model, skill_models=None):
    if not calls:
        return False
    if not skill_models:
        return all(e['request'].get('model') == model for e in calls)
    requests = [r for r in trace if r['recordType'] == 'MODEL_REQUEST_SENT']
    if len(requests) != len(calls):
        return False
    for r in requests:
        meta = r.get('metadata', {})
        skill = meta.get('skillName')
        if not skill or meta.get('providerModel') != skill_models.get(skill, model):
            return False
    return Counter(r['metadata']['providerModel'] for r in requests) == Counter(e['request'].get('model') for e in calls)


def execute_case(client, name, path, token, secrets, bundle, timeout, model, skill_models=None):
    case = 'case-' + path + '-' + uuid.uuid4().hex
    prefix = name + '/' + path
    mission = scenarios.inputs(name, case)
    bundle.add(prefix + '/input.json', mission)
    before = database(path)
    headers = {'Authorization': 'Bearer ' + token}
    control = {'X-Control-Key': secrets['control']}
    result = {'scenario': name, 'path': path, 'caseId': case, 'checks': {}, 'businessReview': 'PENDING'}
    terminal, trace, events = {}, [], []
    api = environment.url(PORTS[path])
    try:
        response = client.post(environment.url(18090, '/control/cases/' + case), json={'mode': 'live', 'path': path}, headers=control)
        response.raise_for_status()
        response = client.post(api + '/assessments', json=mission, headers=headers)
        response.raise_for_status()
        result['executionId'] = response.json()['id']
        terminal = wait(client, api, result['executionId'], headers, timeout)
    except Exception as error:
        result['executionError'] = bundle.error(error)
    finally:
        # Collect each source independently so one missing artifact does not hide the others.
        bundle.add(prefix + '/terminal.json', terminal)
        try:
            response = client.get(environment.url(18090, '/control/journal'), headers=control)
            response.raise_for_status()
            events = [e for e in response.json() if e.get('caseId') == case]
            bundle.add(prefix + '/journal.json', events)
        except Exception as error:
            result['journalError'] = bundle.error(error)
        try:
            trace = trace_for(client, path, case, secrets['observer'], bundle, prefix)
            # Accepted plans are authoritative; raw fenced model text is not reparsed here.
            plans = [scenarios.payload(r, trace) for r in trace if r['recordType'] in ['PLAN_CREATED', 'PLAN_UPDATED']]
            bundle.add(prefix + '/accepted-plans.json', plans)
        except Exception as error:
            result['traceError'] = bundle.error(error)
        try:
            after = database(path)
            old, new = row_hashes(before), row_hashes(after)
            relevant = {t: [r for r in rows if case in (r.get('body') or r.get('receipt') or '')] for t, rows in after.items()}
            bundle.add(prefix + '/business-records.json', relevant)
            result['checks'].update(scenarios.review(terminal, mission, relevant, trace))
            result['checks']['prior database rows unchanged'] = all(old[t] <= new[t] for t in old)
            result['checks']['no service commitments created'] = old['requests'] == new['requests']
        except Exception as error:
            result['reviewError'] = bundle.error(error)
        calls = [e for e in events if e['event'] == 'model-request']
        responses = [e for e in events if e['event'] == 'model-response']
        result['checks']['complete provider pairing'] = bool(calls) and sorted(e['requestId'] for e in calls) == sorted(e['requestId'] for e in responses)
        result['checks']['requested model used'] = model_assignment_matches(calls, trace, model, skill_models)
        result['checks']['no provider failures'] = not any(e['event'] in ['provider-transport-failure', 'model-rejected'] for e in events) and all(e.get('status', 0) == 200 and not e.get('response', {}).get('error') for e in responses)
        result['usage'] = usage(events, trace)
        result['status'] = 'CHECKS_PASS_REVIEW_REQUIRED' if result['checks'] and all(result['checks'].values()) and not any(k.endswith('Error') for k in result) else 'FAIL'
    return result


def write_report(report, bundle, output):
    output.mkdir(parents=True, exist_ok=True)
    lines = ['# Run result', '', f"Mode: {report['mode']}; status: **{report['status']}**.",
             '', 'Business judgment requires review; automated success is not acceptance.', '',
             '| Scenario | Path | Checks | Calls | Reported cost | Trace seconds |', '|---|---|---|---|---|---|']
    for case in report['cases']:
        checks = case['checks']
        lines.append(f"| {case['scenario']} | {case['path']} | {sum(checks.values())}/{len(checks)} | {case['usage']['modelCalls']} | {case['usage']['reportedCost']} | {case['usage'].get('traceSeconds')} |")
    failures = [f"- {c['scenario']}/{c['path']}: {name}" for c in report['cases'] for name, ok in c['checks'].items() if not ok]
    failures += [f"- {c['scenario']}/{c['path']}: {value}" for c in report['cases'] for key, value in c.items() if key.endswith('Error')]
    if failures:
        lines += ['', 'Failures:', *failures]
    if report.get('error'):
        lines += ['', 'Runner error: ' + report['error']]
    lines += ['', 'Runtime restored/provider-disabled: ' + str(report['runtimeRestored']), '',
              'Manual review:', *['- ' + x for x in scenarios.REVIEW_AREAS]]
    summary = ('\n'.join(lines) + '\n').encode()
    if report['mode'] == 'capture':
        bundle.add('candidate-review.json', {'status': 'UNREVIEWED', 'replayApproved': False,
                   'runId': report['runId'], 'reviewAreas': scenarios.REVIEW_AREAS,
                   'note': 'Candidate evidence only. This runner does not promote or replay captures.'})
    bundle.add('report.json', report)
    bundle.add('summary.md', summary)
    bundle.add('checksums.json', {n: digest(raw) for n, raw in bundle.files.items()})
    temporary = output / ('bundle-' + report['runId'] + '.tmp')
    with zipfile.ZipFile(temporary, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, raw in bundle.files.items():
            archive.writestr(name, raw)
    # The ZIP includes its own matching report; it remains coherent if publication is interrupted.
    os.replace(temporary, output / 'bundle.zip')
    for name in ['report.json', 'summary.md']:
        temporary = output / (name + '.tmp')
        temporary.write_bytes(bundle.files[name])
        os.replace(temporary, output / name)


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode', choices=['mock', 'live', 'evaluate', 'capture'])
    p.add_argument('--model', help='Explicit provider/model identifier for paid modes')
    p.add_argument('--skill-model', action='append', default=[], metavar='SKILL=MODEL', help='Temporary per-skill model override; repeatable')
    p.add_argument('--reasoning', default='medium', choices=['none', 'minimal', 'low', 'medium', 'high', 'xhigh'])
    p.add_argument('--path', choices=['java', 'sidecar'], help='evaluate only; defaults to java')
    p.add_argument('--scenario', action='append', choices=scenarios.NAMES, help='Repeat to select scenarios; default both')
    p.add_argument('--output', type=Path, help='A new directory; default evidence/latest is replaced each run')
    p.add_argument('--dry-run', action='store_true', help='Print selection without provider access or runtime changes')
    return p


def main(argv=None):
    p = parser()
    args = p.parse_args(argv)
    if args.path and args.mode != 'evaluate':
        p.error('--path is only valid for evaluate; live/capture run both integrations')
    if args.mode == 'mock':
        print('UNAVAILABLE: no compatible approved mock fixtures. No runtime changes or model calls.')
        return 2
    if not args.model:
        p.error('--model is required for live, evaluate and capture')
    skill_models = {}
    for value in args.skill_model:
        skill, separator, provider_model = value.partition('=')
        source = ROOT / 'config/skills' / (skill + '.yaml')
        if not separator or not provider_model.strip() or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*', skill) or not source.is_file():
            p.error('Invalid skill override: ' + value)
        if skill in skill_models or yaml.safe_load(source.read_bytes()).get('model') != 'reasoning':
            p.error('Duplicate override or unsupported source model: ' + skill)
        skill_models[skill] = provider_model
    paths = [args.path or 'java'] if args.mode == 'evaluate' else ['java', 'sidecar']
    selected = list(dict.fromkeys(args.scenario or scenarios.DEFAULT_NAMES))
    if args.dry_run:
        print(json.dumps({'mode': args.mode, 'paths': paths, 'scenarios': selected,
                          'model': args.model, 'skillModels': skill_models, 'reasoning': args.reasoning, 'paidCalls': 0}, indent=2))
        return 0
    if not os.getenv('LOOMSPAN_OPENROUTER_API_KEY'):
        p.error('LOOMSPAN_OPENROUTER_API_KEY is required; no runtime changes made')
    output = args.output.resolve() if args.output else ROOT / 'evidence/latest'
    if args.output and output.exists():
        p.error('--output must be a new directory; accepted results are never overwritten')
    secrets = json.loads((ROOT / '.runtime/secrets.json').read_bytes())
    bundle = Bundle([*secrets.values(), os.environ['LOOMSPAN_OPENROUTER_API_KEY']])
    report = {'runId': uuid.uuid4().hex, 'mode': args.mode, 'model': args.model, 'reasoning': args.reasoning,
              'skillModels': skill_models, 'paths': paths, 'scenarios': selected, 'cases': [], 'status': 'FAIL', 'runtimeRestored': None,
              'scope': 'Assessment scenarios only; service-request regression is separate',
              'businessReview': 'PENDING', 'replayApproved': False,
              'captureCandidate': args.mode == 'capture'}
    with run_lock():
        try:
            ready()
            require_offline_provider()
            report['runtimeRestored'] = True
            report['build'] = baseline()
            report['gitCommit'] = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
            files = [*(ROOT / 'config').rglob('*.yaml'), *(ROOT / 'apps').rglob('*.py'), *(ROOT / 'apps').rglob('*.java'),
                     ROOT / 'fixtures/base-case.json', ROOT / 'fixtures/business.json', ROOT / 'fixtures/server.py',
                     ROOT / 'scripts/scenarios.py', ROOT / 'scripts/run_suite.py']
            report['sourceSha256'] = {f.relative_to(ROOT).as_posix(): digest(f.read_bytes()) for f in files}
            for f in files:
                bundle.add('source/' + f.relative_to(ROOT).as_posix(), f.read_bytes())
            with tempfile.TemporaryDirectory(prefix='runner-', dir=ROOT / '.runtime') as temporary:
                directory = Path(temporary)
                with live_runtime(directory, paths, args.model, args.reasoning, report, skill_models):
                    for file in directory.rglob('*.yaml'):
                        bundle.add('effective/' + file.relative_to(directory).as_posix(), file.read_bytes())
                    with httpx.Client(timeout=60, trust_env=False) as client:
                        for name in selected:
                            for path in paths:
                                print('Running ' + name + ' / ' + path, flush=True)
                                token = login('maya')
                                bundle.secrets.append(token)
                                case = execute_case(client, name, path, token, secrets, bundle,
                                                    report['build']['missionTimeoutSeconds'] + 60, args.model, skill_models)
                                report['cases'].append(case)
                                print(case['status'], flush=True)
                                if case.get('executionError'):
                                    raise RuntimeError('Execution interrupted or unreachable; stopping further scenarios and restoring runtime')
            if all(c['status'] == 'CHECKS_PASS_REVIEW_REQUIRED' for c in report['cases']):
                report['status'] = 'CHECKS_PASS_REVIEW_REQUIRED'
        except (Exception, KeyboardInterrupt) as error:
            report['error'] = bundle.error(error)
        finally:
            write_report(report, bundle, output)
    print(str(output / 'summary.md'))
    return 0 if report['status'] == 'CHECKS_PASS_REVIEW_REQUIRED' else 1


if __name__ == '__main__':
    raise SystemExit(main())
