"""Reuse paired real responses for a narrow offline contract diagnostic, never approval."""
import argparse
import hashlib
import json
from pathlib import Path
from inspect_capture import inspect, mission


def derive(source):
    source=Path(source).resolve()
    raw=(source/'journal.json').read_bytes()
    events=json.loads(raw)
    manifest=json.loads((source/'manifest.json').read_text())
    samples={}
    for path in ['java','sidecar']:
        requests=[e for e in events if e['event']=='model-request' and e.get('path')==path
                  and mission(e['request'],'compareOptions')]
        if len(requests)!=1: raise ValueError('Expected one unambiguous comparison for '+path)
        request=requests[0]
        if request['request'].get('model')!=manifest.get('model') or request['request'].get('reasoning_effort')!=manifest.get('reasoning'):
            raise ValueError('Request does not match recorded model/reasoning')
        responses=[e for e in events if e['event']=='model-response' and e.get('requestId')==request.get('requestId')
                   and e.get('path')==path and e.get('caseId')==request['caseId']]
        if not request.get('requestId') or len(responses)!=1: raise ValueError('Unpaired response')
        response=responses[0]
        if response.get('status')!=200 or response.get('provenance')!='live OpenRouter':
            raise ValueError('Not a successful recorded provider response')
        prompt=next(m['content'] for m in request['request']['messages'] if m.get('role')=='user'
                    and m['content'].startswith('Mission objective:'))
        body=prompt.split('Canonical mission input:\n',1)[1]
        body=json.JSONDecoder().raw_decode(body.lstrip())[0]
        samples[path]={'caseId':request['caseId'],'requestId':request['requestId'],
                       'request':request['request'],'input':body,'response':response['response'],
                       'provenance':{'provider':response['provenance'],'model':manifest['model'],
                                     'reasoning':manifest['reasoning'],'sourcePath':path}}
    return {'formatVersion':1,'approved':False,'purpose':'Offline quote-schema diagnostic only; not business acceptance or real correction provenance',
            'sourceCapture':source.name,'sourceSha256':{'journal.json':hashlib.sha256(raw).hexdigest(),
                'manifest.json':hashlib.sha256((source/'manifest.json').read_bytes()).hexdigest()},
            'normalization':'None in this file. Runner replaces original case IDs with a fresh case ID in diagnostic copies only.',
            'mutations':'No response content correction. Runner deliberately splices Java invalid output then Sidecar structurally valid output; this is NOT a real-model correction pair.',
            'review':{'java':'Reject: extra unissued quote objects; missing authoritative context and unclear cents.',
                      'sidecar':'Structurally usable two-quote sample only. Missing identity/approval facts and raw monetary prose prevent semantic approval.'},
            'mechanicalReview':inspect(source),'samples':samples}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('capture',type=Path);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    if args.output.resolve().is_relative_to(args.capture.resolve()):p.error('Preserve the original capture; write outside it')
    result=derive(args.capture)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2)
    print('Diagnostic derived; approved=false; original capture unchanged.')


if __name__=='__main__':main()
