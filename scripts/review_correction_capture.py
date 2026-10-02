"""Read-only correction/provenance inventory; never grants replay approval."""
import argparse, hashlib, json
from collections import Counter
from pathlib import Path

def review(directory):
    manifest=json.loads((directory/'manifest.json').read_text())
    events=json.loads((directory/'journal.json').read_text(encoding='utf-8'))
    traces=json.loads((directory/'trace-index.json').read_text())
    paths={}
    for selected in manifest['results']:
        path=selected['path']; case=selected['caseId']
        requests={e['requestId']:e for e in events if e.get('caseId')==case and e['event']=='model-request'}
        responses=[e for e in events if e.get('caseId')==case and e['event']=='model-response']
        malformed=[]; feedback=[]
        for e in responses:
            content=e['response']['choices'][0]['message'].get('content','')
            try: json.loads(content)
            except (TypeError,ValueError) as error:
                malformed.append({'requestId':e['requestId'],'error':str(error),'characters':len(content or ''),
                                  'finishReason':e['response']['choices'][0].get('finish_reason'),
                                  'contentSha256':hashlib.sha256((content or '').encode()).hexdigest()})
        for ident,e in requests.items():
            text=json.dumps(e['request'],ensure_ascii=False)
            schema_feedback=any(m.get('role')=='user' and m.get('content','').startswith(
                ('The previous response could not be parsed as JSON.',
                 'The previous response is valid JSON but does not satisfy the configured output_schema.'))
                for m in e['request'].get('messages',[]))
            if 'YOUR PREVIOUS ACTION WAS INVALID' in text or schema_feedback:
                feedback.append({'requestId':ident,'stepActionFeedback':'YOUR PREVIOUS ACTION WAS INVALID' in text,
                    'outputSchemaFeedback':schema_feedback,
                    'candidateEvidence':'REJECTED STEP ACTION EVIDENCE' in text,
                    'parserDiagnostic':'Parser reason' in text,
                    'omissionMarker':'omitted ' in text})
        frames=[]; trace_records=[]
        for trace in traces:
            if trace['path']!=path or case not in trace['cases']:continue
            raw=(directory/trace['file']).read_bytes()
            assert hashlib.sha256(raw).hexdigest()==trace['sha256']
            frames.extend(json.loads(line) for line in raw.decode().splitlines() if line)
            trace_records.append(trace)
        relevant=[f for f in frames if f.get('recordType') in ['STEP_ACTION_REJECTED','STEP_FAILED','TOOL_CALL_STARTED','TOOL_CALL_COMPLETED']]
        trace_contents=[]; response_links=[]
        for frame in frames:
            if frame.get('recordType')!='MODEL_RESPONSE_RECEIVED':continue
            payload=frame.get('data')
            if payload is None:
                ident=frame['metadata']['payloadId']
                chunks=sorted([f for f in frames if f.get('recordType')=='PAYLOAD_CHUNK_APPENDED'
                    and f['metadata'].get('payloadId')==ident],key=lambda f:f['metadata']['chunkIndex'])
                assert len(chunks)==frame['metadata']['chunkCount']
                payload=json.loads(''.join(c['data'] for c in chunks))
            content=payload['content'];trace_contents.append(content)
            response_links.append({'sequence':frame['sequence'],'route':frame['route'],
                'requestIds':[e['requestId'] for e in responses if e['response']['choices'][0]['message'].get('content')==content]})
        provider_contents=[e['response']['choices'][0]['message'].get('content','') for e in responses]
        started=next(f for f in frames if f.get('recordType')=='TRACE_STARTED')
        ended=next(f for f in frames if f.get('recordType')=='TRACE_COMPLETED')
        paths[path]={'caseId':case,'status':selected['status'],'providerCalls':len(requests),
            'httpStatuses':dict(Counter(str(e.get('status')) for e in responses)),
            'allRequestsMuseMedium':all(e['request'].get('model')=='meta/muse-spark-1.3-contributor' and e['request'].get('reasoning_effort')=='medium' for e in requests.values()),
            'promptTokens':sum(e['response'].get('usage',{}).get('prompt_tokens',0) for e in responses),
            'completionTokens':sum(e['response'].get('usage',{}).get('completion_tokens',0) for e in responses),
            'reportedProviderCost':sum(e['response'].get('usage',{}).get('cost',0) or 0 for e in responses),
            'invalidJsonResponses':malformed,'correctionFeedback':feedback,'traces':trace_records,
            'durationSeconds':round(ended['timestamp']-started['timestamp'],3),
            'providerContentsMatchFrameworkTrace':Counter(trace_contents)==Counter(provider_contents),
            'responseTraceLinks':response_links,
            'traceCorrectionEvents':[f for f in frames if f.get('recordType') in
                ['STRUCTURED_OUTPUT_RECORDED','ADVISOR_REQUEST_MUTATION_RECORDED','STEP_ACTION_REJECTED']],
            'traceActionEvents':relevant}
    return {'approved':False,'capture':str(directory),'frameworkCommit':manifest['frameworkCommit'],
            'installedFrameworkSha256':manifest['installedFrameworkSha256'],'paths':paths,
            'scope':'Inventory only; manually review response pairing, successful correction, tool effects and business semantics.'}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('capture',type=Path);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.resolve().is_relative_to(args.capture.resolve()):parser.error('Write outside original capture')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x',encoding='utf-8') as out:json.dump(review(args.capture),out,indent=2)
    print('Correction inventory retained; no replay approval granted.')
