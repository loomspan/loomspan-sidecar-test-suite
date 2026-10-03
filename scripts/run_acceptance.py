"""One offline acceptance command; preserve runtime, review evidence and restore normal hosts."""
import environment as target_env
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid
import xml.etree.ElementTree as ET
from acceptance_report import checksums, consolidate, junit_counts, markdown
from baseline import baseline
from capture_reviewed_replay import require_offline_provider, verify_source, run as assessments
from capture_service_requests import run as service_requests
from capture_isolation import run as isolation
from capture_nested_authorization import run as nested_authorization
from capture_step_correction import records
from curate_business_replay import ROOT, digest
from model_profile import model_profile
from readiness import ready
from review_reviewed_replay import inspect as replay_review
from review_service_requests import inspect as service_review
from review_isolation import inspect as isolation_review
from review_nested_authorization import inspect as nested_review
from capture_full_correction import run as full_correction
from review_full_correction import inspect as full_correction_review
from curate_full_correction import verify_approval as correction_approval
from audit_fresh_live import verify as verify_fresh_live

FOCUSED = ['test_recovery_replay', 'test_reviewed_replay', 'test_fixture_replay', 'test_fixture_proxy',
           'test_fixture_clock', 'test_capture_review', 'test_business_output', 'test_quote_publication',
           'test_workflow_generation', 'test_comparison_mutation', 'test_nested_authorization_fixture',
           'test_business_workflow_replay', 'test_acceptance_report', 'test_full_correction', 'test_correction_context',
           'test_fresh_live_review', 'test_fresh_live_audit', 'test_environment', 'test_runtime_startup']
COMPOSE = target_env.compose()


def runtime_state(build):
    ready()
    require_offline_provider()
    observed = baseline()
    normal = True
    for name in ['java', 'sidecar']:
        mounts = subprocess.check_output(target_env.execute(name,'cat','/proc/self/mountinfo'),text=True)
        setting = subprocess.run(target_env.execute(name,'printenv','LOOMSPAN_SKILLS_LOCATIONS'),capture_output=True,text=True)
        if setting.returncode not in [0, 1]:
            raise RuntimeError('Unable to verify skill-location setting')
        normal &= '/config/authorization' not in mounts and 'authorization' not in setting.stdout
    return {'ready': True, 'providerDisabled': True, 'normalConfiguration': normal,
            'artifactsUnchanged': observed['artifacts']==build['artifacts'],
            'frameworkCommit':observed['frameworkCommit'], 'frameworkSha256':observed['installedFrameworkSha256']}


def provenance_preflight():
    file = ROOT/'fixtures/replay/business-reviewed-v1.json'
    bundle = json.loads(file.read_bytes())
    approval = json.loads((file.parent/'business-reviewed-v1-approval.json').read_bytes())
    if approval['status']!='APPROVED_FOR_SCOPED_OFFLINE_REPLAY' or approval['fixtureSha256']!=digest(file):
        raise ValueError('Reviewed fixture approval mismatch')
    for samples in bundle['scenarios'].values():
        for sample in samples.values():
            verify_source(sample)
    # Fail before running against an old fixture/application image; no automatic rebuild.
    for service, files in [('fixtures',['fixtures/server.py','fixtures/business.json']),
                           ('python',['apps/python/app.py','apps/python/business.py'])]:
        for name in files:
            actual = subprocess.check_output(target_env.execute(service,'sha256sum','/app/'+name),text=True).split()[0]
            if actual!=digest(ROOT/name):
                raise ValueError('Running '+service+' source differs: '+name+'; preserve evidence before rebuilding')
    return {'fixtureSha256':digest(file), 'approvalSha256':digest(file.parent/'business-reviewed-v1-approval.json'),
            **correction_approval()}


def main():
    ready(); require_offline_provider()
    build = baseline()
    if not runtime_state(build)['normalConfiguration']:
        raise RuntimeError('Start from the documented normal offline configuration')
    profile = model_profile()
    provenance = provenance_preflight()
    live_audit = verify_fresh_live(build)
    out = ROOT/'evidence'/('acceptance-offline-'+time.strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:6])
    out.mkdir()
    (out/'reviews').mkdir()
    def save(name, value):
        (out/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
    save('fresh-live-audit.json', live_audit)
    # Source bytes and original evidence remain immutable; no credentials are copied.
    source_hashes = {p.relative_to(ROOT).as_posix():digest(p) for directory in ['scripts','tests','config']
                     for p in (ROOT/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    source_hashes.update({name:digest(ROOT/name) for name in ['compose.yaml','compose.snapshot.yaml',
                          'compose.offline.yaml','compose.authorization.yaml','requirements.lock']})
    source_hashes.update({name:digest(ROOT/name) for name in ['fixtures/replay/full-correction-reviewed-v1.json',
                          'fixtures/replay/full-correction-reviewed-v1-approval.json']})
    live_directory = ROOT/live_audit['reviewDirectory']
    source_hashes.update({p.relative_to(ROOT).as_posix():digest(p) for p in live_directory.iterdir() if p.is_file()})
    save('suite-source-sha256.json',source_hashes)
    save('business-records-before.json',records())
    protected = json.loads((ROOT/'evidence/business-output-offline-20261002/preserved-source-sha256.json').read_bytes())
    save('protected-source-sha256.json',protected)
    secrets = list(json.loads((ROOT/'.runtime/secrets.json').read_bytes()).values())
    secrets += [v for k,v in os.environ.items() if ('API_KEY' in k or 'TOKEN' in k) and len(v)>15]
    commands, stages, archives = [], [], []
    aggregate = ET.Element('testsuites')

    def command(label, args, env=None):
        print(label, flush=True)
        result = subprocess.run(args,cwd=ROOT,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace')
        log = result.stdout + result.stderr
        for secret in secrets:
            log = log.replace(secret,'[REDACTED]')
        (out/(label+'.log')).write_text(log,encoding='utf-8')
        commands.append({'name':label,'arguments':args,'exitCode':result.returncode})
        save('commands.json',commands)
        if result.returncode:
            raise RuntimeError(label+' failed; see its redacted log')
        return result.stdout

    def preserve(label):
        output = command(label,[sys.executable,'scripts/preserve_runtime.py','--no-package-copy'])
        directory = Path(output.strip().splitlines()[-1]).resolve()
        if not directory.is_relative_to(ROOT/'evidence'):
            raise ValueError('Unexpected preservation directory')
        checksums(directory)
        archives.append(str(directory))
        save('preservation-archives.json',archives)

    def assertions(label, capture):
        env = dict(os.environ, CAPTURE_DIRECTORY=str(capture), PYTHONDONTWRITEBYTECODE='1')
        xml = out/(label+'-junit.xml')
        command(label,[sys.executable,'-m','pytest','-q','-p','no:cacheprovider',
                      'tests/test_delivery_evidence.py','tests/test_planner_evidence.py','--junitxml='+str(xml)],env)
        root = ET.parse(xml).getroot()
        aggregate.extend([root] if root.tag=='testsuite' else list(root))
        return junit_counts(xml)

    def scenario(label, capture_fn, review_fn):
        require_offline_provider()
        print('Scenario: '+label,flush=True)
        capture = Path(capture_fn()).resolve()
        # Keep the fresh directory attributable even if review fails.
        item = {'scenario':label,'capture':str(capture),'freshCapture':True,'paidCalls':0}
        stages.append(item); save('stages.json',stages)
        item['evidenceVerified']=checksums(capture)>0
        report=review_fn(capture);item['review']=report
        save('reviews/'+label+'.json',report)
        if report['status']!='PASS' or not report['checks'] or not all(c['passed'] for c in report['checks']):
            raise RuntimeError(label+' evidence review failed')
        folders = [capture/'baseline',capture/'priority'] if label=='isolation' else [capture]
        totals = {'tests':0,'passed':0,'failures':0,'errors':0,'skipped':0}
        for i, folder in enumerate(folders):
            count=assertions(label+('-'+str(i) if len(folders)>1 else ''),folder)
            for key in totals: totals[key]+=count[key]
        item['assertions']=totals;save('stages.json',stages)
        print(label+' PASS ('+str(len(report['checks']))+' evidence checks)',flush=True)

    error = None
    restoration_required = False
    try:
        scenario('baseline',lambda:assessments('baseline'),replay_review)
        scenario('priority',lambda:assessments('priority'),replay_review)
        scenario('recovery',lambda:full_correction(offline=True),full_correction_review)
        scenario('service-requests',service_requests,service_review)
        scenario('isolation',isolation,isolation_review)
        preserve('preserve-before-authorization')
        restoration_required = True
        command('enable-authorization',COMPOSE+['-f','compose.authorization.yaml','up','-d','--no-deps',
                                              '--force-recreate','java','sidecar'])
        ready(); require_offline_provider()
        scenario('nested-authorization',nested_authorization,nested_review)
    except Exception as exc:
        error = {'kind':type(exc).__name__,'message':str(exc)}
    finally:
        if restoration_required:
            try:
                preserve('preserve-before-restoration')
            except Exception as exc:
                error = {'kind':type(exc).__name__,'message':'Preservation before restoration failed: '+str(exc),
                         'earlierFailure':error}
                # A failed archive must not silently discard unique runtime traces.
                restoration_required = False
            if restoration_required:
                try:
                    command('restore-normal',COMPOSE+['up','-d','--no-deps','--force-recreate','java','sidecar'])
                    ready(); require_offline_provider()
                except Exception as exc:
                    error={'kind':type(exc).__name__,'message':'Normal runtime restoration failed: '+str(exc),'earlierFailure':error}
        save('failure.json',error)
        save('stages.json',stages)
        ET.ElementTree(aggregate).write(out/'acceptance-junit.xml',encoding='utf-8',xml_declaration=True)
    if error:
        save('manifest.json',{**build,'mode':'offline consolidated acceptance','status':'FAIL','paidCalls':0,
                              'stages':stages,'preservationArchives':archives,'error':error})
        print('FAIL; evidence retained at '+str(out),flush=True)
        return 1
    runtime=runtime_state(build);save('runtime.json',runtime)
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
    command('focused-tests',[sys.executable,'-m','pytest','-q','-p','no:cacheprovider',
                            *['tests/'+name+'.py' for name in FOCUSED],'--junitxml='+str(out/'focused-junit.xml')],env)
    focused=junit_counts(out/'focused-junit.xml')
    after=records();save('business-records-after.json',after)
    before=json.loads((out/'business-records-before.json').read_bytes())
    failures=[name for name,wanted in {**protected,**source_hashes}.items() if digest(ROOT/name)!=wanted]
    for stage in stages: checksums(stage['capture'])
    verify_fresh_live(build)
    # SQLite helper returns tuples; compare JSON-normalized snapshots.
    after=json.loads(json.dumps(after))
    preserved=all(row in after[path][table] for path in ['java','python'] for table in ['quotes','assessments','requests']
                  for row in before[path][table])
    requests_added={path:len(after[path]['requests'])-len(before[path]['requests']) for path in ['java','python']}
    integrity={'status':'PASS' if not failures and preserved and requests_added=={'java':2,'python':2} else 'FAIL',
               'protectedOriginalFilesVerified':len(protected),'suiteSourceFilesVerified':len(source_hashes),
               'changedFiles':failures,'priorDurableRecordsPreserved':preserved,'requestsAdded':requests_added,
               'expectedRequestsAddedPerApplication':2,'finalizedScenarioEvidenceVerified':True}
    save('integrity.json',integrity)
    audit={'focusedTests':focused,'requirements':[
        {'requirement':'Two equivalent authenticated REST applications and complete nested workflow', 'status':'VERIFIED',
         'basis':'Fresh six-group paired run, exact snapshot package identities and actual Framework traces.'},
        {'requirement':'Reviewed baseline/priority model capture provenance and strict offline scripts','status':'VERIFIED',
         'basis':'Approved fixture hash, per-path source hashes/semantic reviews and exact live-source derivation verified in preflight.'},
        {'requirement':'Approval-bound creation, loss/expiry recovery, authorization and isolation','status':'VERIFIED',
         'basis':'Fresh direct/nested creation, receipt recovery, negative controls and gated two-case evidence.'},
        {'requirement':'Full-workflow malformed-output recovery with reviewed real correction provenance','status':'VERIFIED',
         'basis':'Fresh paired fault replay uses unedited genuine Muse corrections from '+provenance['genuineCorrectionCapture']+
                 ', with approved fixture/source hashes, semantic review, complete corrective context and both actual-child parent envelopes. Parent envelopes are explicit replay scaffolding, not new model reasoning.'},
        {'requirement':'Complete live workflows including genuine native parent completion','status':'VERIFIED',
         'basis':'Fresh live baseline 201004 and priority 201657: 256 process checks revalidated, 16 retained assertions and hash-bound semantic review verified in [live audit](fresh-live-audit.json). Real Muse/medium at every model stage; no new paid execution or replay approval.'},
        {'requirement':'Strength of response to continuity priority','status':'QUALIFIED',
         'basis':'Sidecar explicitly escalates urgently. Java retains a defensible parallel pre-expiry loaner decision, but stronger escalation over baseline remains inconclusive. No claim of demonstrated priority-sensitive ranking on both paths.'},
        {'requirement':'Reproducible local setup/run and retained acceptance evidence','status':'VERIFIED_INITIALIZED_RUNTIME',
         'basis':'Single documented command passes on the recorded initialized runtime'+
                 (' using explicitly supplied pinned artifacts in Compose project '+build['runtimeIdentity']['composeProject'] if 'installationMode' in build else '')+
                 '. Fresh installation, prerequisite supply and retained-stack preservation require separate setup evidence; this acceptance command alone does not establish clean bootstrap or published-asset/source-build reproducibility.'}
    ]}
    report=consolidate(stages,runtime,integrity,audit)
    save('report.json',report)
    (out/'summary.md').write_text(markdown(report,out),encoding='utf-8')
    save('manifest.json',{**build,**profile,**provenance,'mode':'offline consolidated acceptance','status':report['status'],
                          'suiteCommit':build['runtimeSourceCommit'] if 'runtimeSourceCommit' in build else subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                          'paidCalls':0,'stages':[{k:v for k,v in s.items() if k!='review'} for s in stages],
                          'preservationArchives':archives,'firstDeliveryComplete':report['firstDeliveryComplete']})
    # Aggregate references bind sibling captures; do not duplicate their traces/journals.
    for file in out.rglob('*'):
        if file.is_file() and any(s.encode() in file.read_bytes() for s in secrets):
            raise RuntimeError('Credential detected in aggregate evidence')
    save('checksums.json',{p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='checksums.json'})
    print(report['status']+'; report '+str(out/'summary.md'),flush=True)
    return 0 if report['status']=='PASS' else 1


if __name__=='__main__':
    raise SystemExit(main())
