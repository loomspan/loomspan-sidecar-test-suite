"""Derive strict offline full-workflow fault fixtures from genuine reviewed corrections."""
import argparse
import copy
import json
import re
from pathlib import Path
from acceptance_report import checksums,junit_counts
from capture_business_diagnostic import normalized
from capture_reviewed_replay import verify_source
from curate_business_replay import ROOT, CASE, digest
from full_correction import stages
from review_full_correction import inspect, digest_content


def capability_review(report):
    """Compare historical labels without rewriting hash-bound review records.

    Only an obsolete change-request prefix on the two capability labels is
    ignored. All findings, provenance, results and other labels remain exact.
    """
    result=copy.deepcopy(report)
    labels={'actual corrective request retains entire malformed candidate',
            'complete candidate and citation coverage; ordering alone is not evidence loss'}
    def label(value):
        stripped=re.sub(r'^PR\s*\d+\s+', '', value)
        return stripped if stripped in labels else value
    for check in result.get('checks',[]):
        check['check']=label(check['check'])
    if 'reviewPolicy' in result:result['reviewPolicy']=label(result['reviewPolicy'])
    return result


def derive(capture,path,review_file,semantic_file):
    capture,review_file,semantic_file=Path(capture).resolve(),Path(review_file).resolve(),Path(semantic_file).resolve()
    checksums(capture)
    reviewed=json.loads(review_file.read_bytes());semantic=json.loads(semantic_file.read_bytes())
    if capability_review(reviewed)!=capability_review(inspect(capture)) or reviewed['status']!='PASS':raise ValueError('Mechanical review no longer matches source')
    if semantic['paths'][path]['status']!='SUITABLE_FOR_FAULT_REPLAY_CURATION':raise ValueError('Correction lacks semantic approval')
    manifest=json.loads((capture/'manifest.json').read_bytes())
    if manifest['mode']!='controlled live full correction' or manifest['paidCalls']!=2:raise ValueError('Not genuine paired live correction capture')
    item=next(i for i in manifest['results'] if i['path']==path);old=item['caseId']
    events=json.loads((capture/'journal.json').read_bytes())
    response=next(e for e in events if e.get('caseId')==old and e['event']=='model-response' and e.get('provenance')=='live OpenRouter')
    request=next(e for e in events if e.get('requestId')==response['requestId'] and e['event']=='model-request')
    if semantic['paths'][path]['correctedContentSha256']!=digest_content(response['response']):raise ValueError('Semantic approval content hash mismatch')
    baseline=json.loads((ROOT/'fixtures/replay/business-reviewed-v1.json').read_bytes())['scenarios']['baseline'][path]
    verify_source(baseline)
    provenance={'kind':'Unedited captured genuine full-workflow Muse correction, case-ID normalization only',
        'sourceCapture':capture.name,'sourcePath':path,'sourceRequestId':response['requestId'],
        'sourceContentSha256':digest_content(response['response']),'sourceJournalSha256':digest(capture/'journal.json'),
        'sourceModel':request['request']['model'],'sourceReasoning':request['request']['reasoning_effort'],
        'normalization':'caseId only','mutations':[]}
    envelope=normalized(response['response'],old,CASE)
    return {'sourceCapture':capture.name,'sourcePath':path,'originalCaseId':old,
            'sourceSha256':{name:digest(capture/name) for name in [*json.loads((capture/'checksums.json').read_bytes()),'checksums.json']},
            'mechanicalReview':review_file.relative_to(ROOT).as_posix(),'mechanicalReviewSha256':digest(review_file),
            'semanticReview':semantic_file.relative_to(ROOT).as_posix(),'semanticReviewSha256':digest(semantic_file),
            'baselineFixtureSha256':digest(ROOT/'fixtures/replay/business-reviewed-v1.json'),
            'correction':provenance,'expected':json.loads(envelope['choices'][0]['message']['content']),
            'steps':stages(baseline['steps'],envelope,provenance),
            'scope':'Original captured stages, explicit extra-brace mutation, genuine captured correction, parent envelopes echo actual child'}


def verify_sample(sample):
    source=ROOT/'evidence'/sample['sourceCapture']
    if any(digest(source/name)!=wanted for name,wanted in sample['sourceSha256'].items()):raise ValueError('Correction source checksums changed')
    for kind in ['mechanicalReview','semanticReview']:
        if digest(ROOT/sample[kind])!=sample[kind+'Sha256']:raise ValueError('Correction review changed')
    if derive(source,sample['sourcePath'],ROOT/sample['mechanicalReview'],ROOT/sample['semanticReview'])!=sample:
        raise ValueError('Correction fixture differs from genuine reviewed source')
    if any(s.get('live') for s in sample['steps']):raise ValueError('Paid replay stage prohibited')


def verify_approval():
    file=ROOT/'fixtures/replay/full-correction-reviewed-v1.json'
    approval_file=file.with_name('full-correction-reviewed-v1-approval.json')
    approval=json.loads(approval_file.read_bytes())
    if approval['status']!='APPROVED_FOR_SCOPED_OFFLINE_REPLAY' or approval['fixtureSha256']!=digest(file):
        raise ValueError('Correction fixture approval/hash mismatch')
    bundle=json.loads(file.read_bytes())
    if set(bundle['samples'])!={'java','sidecar'}:raise ValueError('Both correction samples required')
    for sample in bundle['samples'].values():verify_sample(sample)
    verifications=approval['verifications']
    if len(verifications)!=1:raise ValueError('One paired correction fidelity verification required')
    proof=verifications[0];capture=ROOT/proof['capture'];review_file=ROOT/proof['review'];junit_file=ROOT/proof['junit']
    if digest(review_file)!=proof['reviewSha256'] or digest(junit_file)!=proof['junitSha256']:
        raise ValueError('Correction offline verification changed')
    report=json.loads(review_file.read_bytes())
    if capability_review(report)!=capability_review(inspect(capture)) or report['status']!='PASS':raise ValueError('Correction offline review mismatch')
    manifest=json.loads((capture/'manifest.json').read_bytes())
    if manifest['mode']!='offline full correction replay' or manifest['paidCalls']!=0 or manifest['correctionFixtureSha256']!=digest(file):
        raise ValueError('Correction approval not bound to actual offline fixture')
    counts=junit_counts(junit_file)
    if counts['tests']!=8 or counts['passed']!=8 or any(counts[k] for k in ['failures','errors','skipped']):
        raise ValueError('Correction workflow assertions incomplete')
    return {'correctionFixtureSha256':digest(file),'correctionApprovalSha256':digest(approval_file),
            'genuineCorrectionCapture':next(iter(bundle['samples'].values()))['sourceCapture']}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('capture',type=Path);p.add_argument('--review',type=Path,required=True)
    p.add_argument('--semantic',type=Path,required=True);p.add_argument('--output',type=Path,default=ROOT/'fixtures/replay/full-correction-reviewed-v1.json')
    a=p.parse_args()
    bundle={'formatVersion':1,'status':'CURATED_CANDIDATE','approved':False,
            'samples':{path:derive(a.capture,path,a.review,a.semantic) for path in ['java','sidecar']},
            'scope':'Fault-derived full-workflow recovery; unchanged genuine correction responses; candidate pending offline fidelity review'}
    with a.output.open('x',encoding='utf-8') as f:json.dump(bundle,f,indent=2)
    print(a.output)
