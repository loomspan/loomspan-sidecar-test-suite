"""Require complete large rejected candidates in actual offline correction requests."""
import argparse
import hashlib
import json
from pathlib import Path
from acceptance_report import checksums
from review_full_correction import inspect as schema_review
from review_step_correction import inspect as step_review


def decoded_candidate(request,kind):
    if kind=='schema':
        values=[m['content'] for m in request['messages'] if m['role']=='assistant']
        if len(values)!=1:raise ValueError('Correction lacks one unique assistant candidate')
        return values[0]
    marker='Rejected assistant response (JSON string): '
    values=[m['content'].split(marker,1)[1] for m in request['messages']
            if m['role']=='user' and marker in m.get('content','')]
    if len(values)!=1:raise ValueError('Correction lacks unique step-action evidence')
    return json.JSONDecoder().raw_decode(values[0])[0]


def exact_large_candidate(request,original,kind):
    return len(original)>8192 and decoded_candidate(request,kind)==original


def inspect(schema_directory,step_directory):
    checks=[];cases={};identities=[]
    def check(path,name,value):checks.append({'path':path,'check':name,'passed':bool(value)})
    for kind,directory,review_fn in [('schema',schema_directory,schema_review),('step',step_directory,step_review)]:
        d=Path(directory).resolve();manifest=json.loads((d/'manifest.json').read_bytes())
        report=review_fn(d);events=json.loads((d/'journal.json').read_bytes())
        check(None,kind+': finalized checksums and independent workflow review pass',
              checksums(d)>0 and report['status']=='PASS')
        check(None,kind+': explicitly offline execution',
              manifest['mode']==('offline full correction rehearsal' if kind=='schema' else 'controlled offline') and
              not any(e.get('provenance')=='live OpenRouter' for e in events))
        identities.append((manifest['frameworkCommit'],manifest['installedFrameworkSha256']))
        for path,item in report['paths'].items():
            case=item['caseId'];local=[e for e in events if e.get('caseId')==case]
            replies=[e for e in local if e['event']=='model-response']
            request=next(e['request'] for e in local if e['event']=='model-request' and
                         e['requestId']==item['correctionRequestId'])
            correction=next(e for e in replies if e['requestId']==item['correctionRequestId'])
            original=next(e['response']['choices'][0]['message']['content'] for e in replies
                          if e['stage']==correction['stage']-1)
            check(path,kind+': actual request contains exact complete candidate beyond old 8192 limit',
                  exact_large_candidate(request,original,kind))
            check(path,kind+': no candidate truncation notice',
                  not any('previous assistant candidate was truncated' in m.get('content','') for m in request['messages']))
            cases[kind+'-'+path]={'caseId':case,'candidateCodePoints':len(original),
                'candidateSha256':hashlib.sha256(original.encode()).hexdigest(),
                'correctionRequestId':item['correctionRequestId'],'sourceCapture':str(d),
                'candidateReceivedExactly':decoded_candidate(request,kind)==original,
                'scope':'Actual offline Framework request; scripted correction, not new model judgment'}
    check(None,'both paths and correction types use one exact Framework snapshot',
          len(set(identities))==1 and set(cases)=={'schema-java','schema-sidecar','step-java','step-sidecar'})
    return {'status':'PASS' if all(c['passed'] for c in checks) else 'FAIL','checks':checks,'cases':cases,
            'frameworkCommit':identities[0][0],'installedFrameworkSha256':identities[0][1],'paidCalls':0,
            'scope':'Complete correction-candidate preservation across both real integrations; business model fidelity remains separate'}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('schema',type=Path);p.add_argument('step',type=Path)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if any(a.output.resolve().is_relative_to(d.resolve()) for d in [a.schema,a.step]):p.error('Write outside source captures')
    result=inspect(a.schema,a.step);a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2)
    print(result['status'],[(c['path'],c['check']) for c in result['checks'] if not c['passed']])
    raise SystemExit(0 if result['status']=='PASS' else 1)
