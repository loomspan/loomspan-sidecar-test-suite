"""One runner: frozen offline replay, live evaluation and capture."""
import argparse
import copy
from collections import Counter
from contextlib import contextmanager, nullcontext
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import sys
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
from suites.equipment_service import scenarios
from suites.registry import EQUIPMENT, SUITES, select

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


def make_overlay(directory, paths, model, reasoning, skill_models=None, suite=EQUIPMENT):
    skill_models = skill_models or {}
    skills = directory / 'skills'
    skills.mkdir()
    for source in (ROOT / 'config/skills').rglob('*.yaml'):
        text = source.read_text(encoding='utf-8')
        if source.parent != ROOT / suite.skill_directory:
            target = skills / source.relative_to(ROOT / 'config/skills')
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read_bytes())
            continue
        text = re.sub(r'^thinking_level:.*\n', '' if reasoning == 'none' else 'thinking_level: ' + reasoning + '\n', text, flags=re.M)
        text = re.sub(r'^model:.*$', 'model: trial-' + suite.name, text, flags=re.M)
        if source.stem in skill_models:
            text = re.sub(r'^model:.*$', 'model: trial-' + source.stem, text, flags=re.M)
        target = skills / source.relative_to(ROOT / 'config/skills')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding='utf-8')
    services = {'fixtures': {'environment': {'OPENROUTER_API_KEY': '${LOOMSPAN_OPENROUTER_API_KEY:?Provider key required}'}}}
    for path in paths:
        config = yaml.safe_load((ROOT / 'config' / (path + '.yaml')).read_text(encoding='utf-8'))
        alias = 'trial-' + suite.name
        if alias in config['loomspan']['models']:
            raise ValueError('Trial model alias already exists: ' + alias)
        config['loomspan']['models'][alias] = copy.deepcopy(config['loomspan']['models']['reasoning'])
        config['loomspan']['models'][alias].update({'provider-model': model, 'thinking-levels': [] if reasoning == 'none' else [reasoning]})
        for skill, provider_model in skill_models.items():
            alias = 'trial-' + skill
            if alias in config['loomspan']['models']:
                raise ValueError('Trial model alias already exists: ' + alias)
            config['loomspan']['models'][alias] = copy.deepcopy(config['loomspan']['models']['trial-' + suite.name])
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
        pairs += [(f, '/config/skills/' + f.relative_to(directory / 'skills').as_posix()) for f in (directory / 'skills').rglob('*.yaml')]
        for source, mounted in pairs:
            actual = subprocess.check_output(environment.execute(path, 'cat', mounted))
            if yaml.safe_load(actual) != yaml.safe_load(source.read_bytes()):
                raise ValueError('Mounted configuration mismatch: ' + path + '/' + source.name)


@contextmanager
def live_runtime(directory, paths, model, reasoning, report, skill_models=None, suite=EQUIPMENT):
    if os.getenv('LOOMSPAN_RUN_OVERLAY') or os.getenv('LOOMSPAN_MODEL_CONFIG_DIRECTORY'):
        raise RuntimeError('An external runtime overlay is already active')
    require_offline_provider()
    overlay = make_overlay(directory, paths, model, reasoning, skill_models, suite)
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


def database(path, suite=EQUIPMENT):
    host = 'python' if path == 'sidecar' else path
    file = ROOT / '.runtime' / host / suite.database
    with sqlite3.connect('file:' + file.as_posix() + '?mode=ro', uri=True) as db:
        db.row_factory = sqlite3.Row
        return {t: [dict(r) for r in db.execute('SELECT * FROM ' + t)] for t in suite.tables}


def row_hashes(rows):
    return {t: {digest(json.dumps(r, sort_keys=True).encode()) for r in rs} for t, rs in rows.items()}


def wait(client, api, ident, headers, timeout, suite=EQUIPMENT):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        response = client.get(api + suite.endpoint + '/' + ident, headers=headers)
        response.raise_for_status()
        value = response.json()
        if value.get('status') in ['COMPLETED', 'FAILED', 'CANCELLED']:
            return value
        time.sleep(.5)
    raise TimeoutError('Assessment exceeded the configured mission timeout plus collection grace')


def trace_catalog(client, path, observer):
    base = environment.url(18081 if path == 'java' else 18083, '/_loomspan/observability/v1')
    items, seen, params = [], set(), {}
    while True:
        response = client.get(base + '/traces', headers={'X-loomspan-Api-Key': observer}, params=params)
        response.raise_for_status()
        page = response.json()
        items.extend(page['items'])
        cursor = page.get('nextCursor')
        if not cursor:
            if page.get('hasMore'):
                raise ValueError('Trace page is incomplete without a continuation')
            return items
        if cursor in seen:
            raise ValueError('Repeated trace continuation')
        seen.add(cursor)
        params = {'cursor': cursor}


def trace_for(client, path, case, observer, bundle, prefix, suite=EQUIPMENT, exclude_ids=()):
    port = 18081 if path == 'java' else 18083
    base = environment.url(port, '/_loomspan/observability/v1')
    headers = {'X-loomspan-Api-Key': observer}
    roots = []
    for item in trace_catalog(client, path, observer):
        if item.get('entrySkill') != suite.entry_skill or item['traceId'] in exclude_ids:
            continue
        response = client.get(base + '/traces/' + item['traceId'] + '/artifact', headers=headers)
        response.raise_for_status()
        raw = response.content
        if case.encode() in raw:
            roots.append(raw)
    if len(roots) != 1:
        raise ValueError('Expected one correlated ' + suite.entry_skill + ' trace')
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


def execute_case(client, name, path, token, secrets, bundle, timeout, model, skill_models=None, reference=None, suite=EQUIPMENT):
    scenarios = suite.scenarios
    case = 'case-' + path + '-' + uuid.uuid4().hex
    prefix = name + '/' + path
    mission = scenarios.inputs(name, case)
    bundle.add(prefix + '/input.json', mission)
    before = database(path, suite)
    headers = {'Authorization': 'Bearer ' + token}
    control = {'X-Control-Key': secrets['control']}
    result = {'suite': suite.name, 'scenario': name, 'path': path, 'caseId': case, 'checks': {}, 'businessReview': 'PENDING'}
    terminal, trace, events = {}, [], []
    api = environment.url(PORTS[path])
    try:
        registration = {'mode': 'live', 'path': path}
        if reference is not None:
            from replay_reference import bind_case
            reference = bind_case(reference, case)
            if reference['input'] != mission:
                raise ValueError('Scenario differs from frozen input')
            registration = {'mode': 'replay', 'path': path, 'steps': reference['steps']}
        response = client.post(environment.url(18090, '/control/cases/' + case), json=registration, headers=control)
        response.raise_for_status()
        response = client.post(api + suite.endpoint, json=mission, headers=headers)
        response.raise_for_status()
        result['executionId'] = response.json()['id']
        terminal = wait(client, api, result['executionId'], headers, timeout, suite)
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
            trace = trace_for(client, path, case, secrets['observer'], bundle, prefix, suite)
            # Accepted plans are authoritative; raw fenced model text is not reparsed here.
            plans = [scenarios.payload(r, trace) for r in trace if r['recordType'] in ['PLAN_CREATED', 'PLAN_UPDATED']]
            bundle.add(prefix + '/accepted-plans.json', plans)
        except Exception as error:
            result['traceError'] = bundle.error(error)
        try:
            after = database(path, suite)
            old, new = row_hashes(before), row_hashes(after)
            relevant = {t: [r for r in rows if case in (r.get('body') or r.get('receipt') or '')] for t, rows in after.items()}
            bundle.add(prefix + '/business-records.json', relevant)
            result['checks'].update(scenarios.review(terminal, mission, relevant, trace))
            result['checks']['prior database rows unchanged'] = all(old[t] <= new[t] for t in old)
            result['checks'].update(scenarios.preservation_checks(old, new))
        except Exception as error:
            result['reviewError'] = bundle.error(error)
        calls = [e for e in events if e['event'] == 'model-request']
        responses = [e for e in events if e['event'] == 'model-response']
        result['checks']['complete provider pairing'] = bool(calls) and sorted(e['requestId'] for e in calls) == sorted(e['requestId'] for e in responses)
        result['checks']['requested model used'] = model_assignment_matches(calls, trace, model, skill_models)
        result['checks']['no provider failures'] = not any(e['event'] in ['provider-transport-failure', 'model-rejected'] for e in events) and all(e.get('status', 0) == 200 and not e.get('response', {}).get('error') for e in responses)
        result['usage'] = usage(events, trace)
        if reference is not None:
            result['checks']['all frozen responses consumed exactly once'] = (
                sorted(e.get('stage', -1) for e in responses) == list(range(len(reference['steps'])))
                and len(calls) == len(reference['steps']))
            result['checks']['only offline reference responses'] = bool(responses) and all(
                e.get('provenance', '').startswith('accepted-reference:') for e in responses)
            result['checks']['published result matches frozen reference'] = (
                terminal.get('status') == 'COMPLETED' and scenarios.decoded(terminal['result']) == reference['expected'])
            result['businessReview'] = 'FROZEN_ACCEPTED_REFERENCE_NOT_NEW_MODEL_REVIEW'
            result['usage']['paidModelCalls'] = sum(e.get('provenance') == 'live OpenRouter' for e in responses)
        result['status'] = 'CHECKS_PASS_REVIEW_REQUIRED' if result['checks'] and all(result['checks'].values()) and not any(k.endswith('Error') for k in result) else 'FAIL'
        if reference is not None and result['status'] != 'FAIL':
            result['status'] = 'REPLAY_PASS'
    return result


def write_report(report, bundle, output):
    output.mkdir(parents=True, exist_ok=True)
    note = ('Frozen accepted responses exercised against current runtime; no new model judgment or paid calls.'
            if report['mode'] == 'mock' else 'Business judgment requires review; automated success is not acceptance.')
    if report.get('fixtureOrigin') == 'authored-protocol-fixtures':
        note = 'Authored protocol fixtures, not captured model judgments. No live provider calls or business acceptance claim.'
    if report.get('fixtureOrigin') == 'unreviewed-live-capture':
        note = 'Recorded real responses replayed offline; human judgment review and reference acceptance remain pending.'
    if report.get('fixtureOrigin') == 'authored-protocol-and-reviewed-live-typesafe':
        note = 'Authored protocol fixtures plus separately reviewed real TypeSafe responses. Offline replay checks integration fidelity; it does not re-evaluate model quality.'
    lines = ['# Run result', '', f"Mode: {report['mode']}; status: **{report['status']}**.",
             '', note, '',
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
              'Manual review:', *['- ' + x for x in report.get('reviewAreas', scenarios.REVIEW_AREAS)]]
    summary = ('\n'.join(lines) + '\n').encode()
    if report['mode'] == 'capture':
        bundle.add('candidate-review.json', {'status': 'UNREVIEWED', 'replayApproved': False,
                   'runId': report['runId'], 'reviewAreas': report.get('reviewAreas', scenarios.REVIEW_AREAS),
                   'note': 'Candidate evidence only; no automatic promotion. Mock replays only the separately frozen accepted reference.'})
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
    p.add_argument('--suite', action='append', choices=[*SUITES, 'all'], help='Repeat to select suites; default equipment-service')
    p.add_argument('--model', help='Explicit provider/model identifier for paid modes')
    p.add_argument('--skill-model', action='append', default=[], metavar='SKILL=MODEL', help='Temporary per-skill model override; repeatable')
    p.add_argument('--reasoning', default='medium', choices=['none', 'minimal', 'low', 'medium', 'high', 'xhigh'])
    p.add_argument('--path', choices=['java', 'sidecar'], help='evaluate defaults to java; mock defaults to both')
    p.add_argument('--scenario', action='append', help='Repeat to select scenarios; mock defaults to all four')
    p.add_argument('--output', type=Path, help='A new directory; default evidence/latest is replaced each run')
    p.add_argument('--dry-run', action='store_true', help='Print selection without provider access or runtime changes')
    p.add_argument('--resume-capture', type=Path, help='Native capture only: prior suite report directory; use unused permits from that same batch')
    return p


def mock_main(args, p, suite=EQUIPMENT):
    from model_profile import model_profile
    if args.model or args.skill_model or args.reasoning != 'medium':
        p.error('mock uses the frozen model assignment; overrides require a separate paid evaluation')
    manifest, references = suite.reference_loader(ROOT)
    paths = [args.path] if args.path else ['java', 'sidecar']
    selected = list(dict.fromkeys(args.scenario or manifest['scenarios']))
    if args.dry_run:
        print(json.dumps({'suite': suite.name, 'mode': 'mock', 'paths': paths, 'scenarios': selected,
                          'sourceRunId': manifest['sourceRunId'], 'paidCalls': 0}, indent=2))
        return 0
    output = args.output.resolve() if args.output else ROOT / 'evidence/latest'
    if args.output and output.exists() and not getattr(args, 'grouped', False):
        p.error('--output must be a new directory; accepted results are never overwritten')
    secrets = json.loads((ROOT / '.runtime/secrets.json').read_bytes())
    bundle = Bundle([*secrets.values(), os.getenv('LOOMSPAN_OPENROUTER_API_KEY')])
    report = {'runId': uuid.uuid4().hex, 'mode': 'mock', 'cases': [], 'status': 'FAIL',
              'paths': paths, 'scenarios': selected, 'runtimeRestored': False,
              'sourceRunId': manifest['sourceRunId'], 'referenceFiles': manifest['files'],
              'businessReview': 'FROZEN_ACCEPTED_REFERENCE_NOT_NEW_MODEL_REVIEW',
              'suite': suite.name, 'reviewAreas': suite.scenarios.REVIEW_AREAS,
              'scope': suite.scope + '; frozen replay, no new model judgment'}
    with (nullcontext() if getattr(args, 'grouped', False) else run_lock()):
        try:
            if os.getenv('LOOMSPAN_RUN_OVERLAY') or os.getenv('LOOMSPAN_MODEL_CONFIG_DIRECTORY'):
                raise RuntimeError('mock requires the normal provider-disabled runtime')
            ready()
            require_offline_provider()
            model_profile()  # Verify authored contracts and assignments on both real hosts.
            report['build'] = baseline()
            bundle.add('reference-manifest.json', manifest)
            with httpx.Client(timeout=60, trust_env=False) as client:
                for name in selected:
                    for path in paths:
                        print('Replaying ' + name + ' / ' + path, flush=True)
                        token = login('maya')
                        bundle.secrets.append(token)
                        case = execute_case(client, name, path, token, secrets, bundle, 180,
                                            'openai/gpt-6-sol', manifest['skillModels'], references[name], suite)
                        report['cases'].append(case)
                        print(case['status'], flush=True)
                        if case['status'] != 'REPLAY_PASS':
                            raise RuntimeError('Replay mismatch; stopped without a paid fallback')
            report['status'] = 'REPLAY_PASS'
        except (Exception, KeyboardInterrupt) as error:
            report['error'] = bundle.error(error)
        finally:
            try:
                require_offline_provider()
                report['runtimeRestored'] = True
            except Exception as error:
                report['error'] = bundle.error(error)
                report['status'] = 'FAIL'
            write_report(report, bundle, output)
    print(str(output / 'summary.md'))
    return 0 if report['status'] == 'REPLAY_PASS' else 1


def run_selected(args, p, suite):
    scenarios = suite.scenarios
    if args.mode != 'mock' and suite.live_runner:
        return suite.live_runner(args, p, suite, sys.modules[__name__])
    if args.path and args.mode not in ['evaluate', 'mock']:
        p.error('--path is only valid for evaluate/mock; live/capture run both integrations')
    if args.mode == 'mock':
        if suite.mock_runner:
            return suite.mock_runner(args, p, suite, sys.modules[__name__])
        return mock_main(args, p, suite)
    if not args.model:
        p.error('--model is required for live, evaluate and capture')
    skill_models = {}
    for value in args.skill_model:
        skill, separator, provider_model = value.partition('=')
        source = ROOT / suite.skill_directory / (skill + '.yaml')
        if not separator or not provider_model.strip() or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*', skill) or not source.is_file():
            p.error('Invalid skill override: ' + value)
        if skill in skill_models or yaml.safe_load(source.read_bytes()).get('model') not in ['reasoning', 'coordination']:
            p.error('Duplicate override or unsupported source model: ' + skill)
        skill_models[skill] = provider_model
    paths = [args.path or 'java'] if args.mode == 'evaluate' else ['java', 'sidecar']
    selected = list(dict.fromkeys(args.scenario or scenarios.DEFAULT_NAMES))
    if args.dry_run:
        print(json.dumps({'suite': suite.name, 'mode': args.mode, 'paths': paths, 'scenarios': selected,
                          'model': args.model, 'skillModels': skill_models, 'reasoning': args.reasoning, 'paidCalls': 0}, indent=2))
        return 0
    if not os.getenv('LOOMSPAN_OPENROUTER_API_KEY'):
        p.error('LOOMSPAN_OPENROUTER_API_KEY is required; no runtime changes made')
    output = args.output.resolve() if args.output else ROOT / 'evidence/latest'
    if args.output and output.exists() and not getattr(args, 'grouped', False):
        p.error('--output must be a new directory; accepted results are never overwritten')
    secrets = json.loads((ROOT / '.runtime/secrets.json').read_bytes())
    bundle = Bundle([*secrets.values(), os.environ['LOOMSPAN_OPENROUTER_API_KEY']])
    report = {'runId': uuid.uuid4().hex, 'mode': args.mode, 'model': args.model, 'reasoning': args.reasoning,
              'skillModels': skill_models, 'paths': paths, 'scenarios': selected, 'cases': [], 'status': 'FAIL', 'runtimeRestored': None,
              'suite': suite.name, 'scope': suite.scope, 'reviewAreas': scenarios.REVIEW_AREAS,
              'businessReview': 'PENDING', 'replayApproved': False,
              'captureCandidate': args.mode == 'capture'}
    with (nullcontext() if getattr(args, 'grouped', False) else run_lock()):
        try:
            ready()
            require_offline_provider()
            report['runtimeRestored'] = True
            report['build'] = baseline()
            report['gitCommit'] = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
            files = [*(ROOT / 'config').rglob('*.yaml'), *(ROOT / 'apps').rglob('*.py'), *(ROOT / 'apps').rglob('*.java'),
                     *(ROOT / name for name in suite.source_files), *(ROOT / 'scripts').rglob('*.py'),
                     *(ROOT / 'scripts/suites').rglob('*.json')]
            files = sorted(set(files))
            report['sourceSha256'] = {f.relative_to(ROOT).as_posix(): digest(f.read_bytes()) for f in files}
            for f in files:
                bundle.add('source/' + f.relative_to(ROOT).as_posix(), f.read_bytes())
            with tempfile.TemporaryDirectory(prefix='runner-', dir=ROOT / '.runtime') as temporary:
                directory = Path(temporary)
                with live_runtime(directory, paths, args.model, args.reasoning, report, skill_models, suite):
                    for file in directory.rglob('*.yaml'):
                        bundle.add('effective/' + file.relative_to(directory).as_posix(), file.read_bytes())
                    with httpx.Client(timeout=60, trust_env=False) as client:
                        for name in selected:
                            for path in paths:
                                print('Running ' + name + ' / ' + path, flush=True)
                                token = login('maya')
                                bundle.secrets.append(token)
                                case = execute_case(client, name, path, token, secrets, bundle,
                                                    report['build']['missionTimeoutSeconds'] + 60, args.model, skill_models, None, suite)
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


def main(argv=None):
    p = parser()
    args = p.parse_args(argv)
    try:
        suites = select(args.suite)
    except ValueError as error:
        p.error(str(error))
    if args.path and args.mode not in ['evaluate', 'mock']:
        p.error('--path is only valid for evaluate/mock; live/capture run both integrations')
    if args.mode == 'mock' and (args.model or args.skill_model or args.reasoning != 'medium'):
        p.error('mock uses the frozen model assignment; overrides require a separate paid evaluation')
    if args.mode != 'mock' and not args.model:
        p.error('--model is required for live, evaluate and capture')
    if len(suites) > 1 and args.skill_model:
        p.error('--skill-model requires one named suite')
    if args.resume_capture and (args.mode != 'capture' or len(suites) != 1 or not suites[0].live_runner):
        p.error('--resume-capture requires capture of the native suite')
    if args.mode != 'mock' and len(suites) > 1 and any(s.live_runner for s in suites):
        p.error('Native live evaluation requires one named suite to keep the paid scope bounded')
    for suite in suites:
        if args.mode not in suite.modes or (args.mode == 'mock' and suite.reference_loader is None):
            p.error(suite.name + ': unsupported mode ' + args.mode)
        catalog = suite.scenarios.NAMES
        if suite.live_runner and args.mode != 'mock':
            catalog = [c['name'] for c in json.loads((ROOT / 'fixtures/typesafe-ai/live-cases.json').read_bytes())['cases']]
        unknown = set(args.scenario or ()) - set(catalog)
        if unknown:
            p.error(suite.name + ': unknown scenarios ' + ', '.join(sorted(unknown)))
    if args.mode == 'mock':
        for suite in suites:
            manifest, _ = suite.reference_loader(ROOT)
            if set(args.scenario or ()) - set(manifest['scenarios']):
                p.error(suite.name + ': selected scenario has no frozen reference')
    if args.dry_run:
        return max(run_selected(args, p, suite) for suite in suites)
    output = args.output.resolve() if args.output else ROOT / 'evidence/latest'
    if args.output and output.exists() and not getattr(args, 'grouped', False):
        p.error('--output must be a new directory; accepted results are never overwritten')
    # One workspace lock covers the complete multi-suite selection.
    with run_lock():
        results = []
        for suite in suites:
            selected = copy.copy(args)
            selected.output = output / suite.name
            selected.grouped = True
            code = run_selected(selected, p, suite)
            results.append((suite.name, code))
            output.mkdir(parents=True, exist_ok=True)
            lines = ['# Suite results', '', '| Suite | Result |', '|---|---|']
            for name, result in results:
                report = json.loads((output / name / 'report.json').read_bytes())
                lines.append(f"| [{name}]({name}/summary.md) | {report['status']} |")
            (output / 'summary.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
            # Do not continue after runtime restoration failed.
            report = json.loads((output / suite.name / 'report.json').read_bytes())
            if not report['runtimeRestored']:
                for remaining in suites[len(results):]:
                    with (output / 'summary.md').open('a', encoding='utf-8') as summary:
                        summary.write(f'| {remaining.name} | NOT_RUN: runtime restoration failed |\n')
                return 1
        return max(code for _, code in results)


if __name__ == '__main__':
    raise SystemExit(main())
