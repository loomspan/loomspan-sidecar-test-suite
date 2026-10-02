"""Review actual captured evidence against independently authored requirements."""
import hashlib,json,pathlib,sys
def review(directory):
    out=pathlib.Path(directory);events=json.loads((out/'journal.json').read_text());manifest=json.loads((out/'manifest.json').read_text()); findings=[]
    if manifest['framework']!='1.0.0-beta.6':
        raise ValueError('This historical review documents beta.6 only; review newer captures independently.')
    for path in ['java','sidecar']:
        requests=[e['request'] for e in events if e['event']=='model-request' and e.get('path')==path]
        responses=[e['response'] for e in events if e['event']=='model-response' and e.get('path')==path]
        equipment=[r for r in requests if any("Execute skill 'assessEquipment'" in str(m.get('content','')) for m in r['messages'])]
        missing=[s for s in ['WO-0820','NOTE-0916','SB-2','20-minute','42 minutes'] if not equipment or s not in json.dumps(equipment[0])]
        findings.append({'path':path,'review':'REJECTED','reason':'Required source evidence did not reach dependent equipment model','missingEvidence':missing,'modelRequests':len(requests),'modelResponses':len(responses),'emittedReasoningEfforts':sorted(set(r.get('reasoning_effort','absent') for r in requests)),'requestsWithNativeTools':sum(bool(r.get('tools')) for r in requests),'returnedModels':sorted(set(r.get('model','unknown') for r in responses)),'returnedProviders':sorted(set(r.get('provider','unknown') for r in responses)),'recordedUsage':{'promptTokens':sum(r.get('usage',{}).get('prompt_tokens',0) for r in responses),'completionTokens':sum(r.get('usage',{}).get('completion_tokens',0) for r in responses),'cost':sum(r.get('usage',{}).get('cost',0) for r in responses)}})
    review={'status':'REJECTED_FOR_REPLAY_BASELINE','findings':findings,'limitations':['Sidecar provider connection closed mid-response; comparison and final synthesis not reached.','Recorded usage covers received responses only.','Original running image/JAR digests were not captured before the interrupted run and container removal; exact selected source versions and Framework trace generations are recorded.']}
    (out/'review.json').write_text(json.dumps(review,indent=2));manifest['review']=review['status'];(out/'manifest.json').write_text(json.dumps(manifest,indent=2))
    (out/'summary.md').write_text('''# First-delivery capture: rejected

Neither integration path produced a valid assessment. This run is not acceptance success and must not seed an approved replay script.

| Assertion | Java | Python / Sidecar |
| --- | --- | --- |
| Required history reaches equipment model | FAIL: WO-0820 absent | FAIL: WO-0820 absent |
| Application publishes valid immutable assessment | FAIL | FAIL |
| Framework trace downloaded | YES | YES |
| Native comparison/final synthesis exercised | YES, lost complete results | NOT REACHED: provider transport failure |

[JUnit assertions](delivery-junit.xml), [review and usage](review.json), [independent model/downstream journal](journal.json), [trace index with SHA-256 and case associations](trace-index.json), [Java terminal result](java-assessment.json), [Sidecar terminal result](sidecar-assessment.json), [container logs](containers.log), [manifest](manifest.json).

The Java Framework trace reports SUCCEEDED: the generated JSON satisfied the model contract, but authoritative quotes were missing, so the application rejected it. That distinction is intentional. Sidecar independently lost history before a subsequent provider connection closed mid-response; do not attribute its terminal transport failure to truncation.

Pinned beta.6 builds dependent/final-synthesis requests with 100-character prior-result summaries and a 1,000-character latest-result preview. Source evidence exists in fixture journals but is missing from the dependent model requests. Assertions do not infer evidence flow from schema validation or completed skill calls.

Creation/recovery, corrected-output replay, nested authorization controls and gated isolation have not passed. No reviewed replay baseline is available. Original runtime image/JAR digests were not collected before interruption/container removal; do not substitute later build identities for this run.
''',encoding='utf-8')
    hashes={p.relative_to(out).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in out.rglob('*') if p.is_file() and p.name!='checksums.json'}
    (out/'checksums.json').write_text(json.dumps(hashes,indent=2));print('Reviewed both captures: rejected for replay baseline.')
if __name__=='__main__':review(sys.argv[1])
