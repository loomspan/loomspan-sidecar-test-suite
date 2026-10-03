"""Derive versioned unedited replay candidates from path-specific reviewed Muse captures."""
import argparse
import hashlib
import json
from pathlib import Path
from inspect_capture import mission, system
from capture_business_diagnostic import normalized

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {'baseline': {'java': '093632', 'sidecar': '092503'},
           'priority': {'java': '102148', 'sidecar': '095046'}}
CASE = 'REPLAY_CASE_ID'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def dependencies(steps):
    plans = {s['stageSkill']: i for i,s in enumerate(steps) if s['stageKind']=='plan'}
    actions = {(s['stageSkill'],s['taskId']): i for i,s in enumerate(steps) if s['stageKind']=='action'}
    parents = {s['toolName']: i for i,s in enumerate(steps) if s['stageKind']=='action'}
    tasks = {(s['stageSkill'],t['taskId']): t for s in steps if s['stageKind']=='plan' for t in s['tasks']}
    last, finals = {}, {}
    for i,s in enumerate(steps):
        skill,kind=s['stageSkill'],s['stageKind']
        if kind=='plan': s['after']=[] if skill=='resolveEquipment' else [parents[skill]]
        elif kind=='action':
            task=tasks[(skill,s['taskId'])]
            s['after']=[plans[skill]]+[actions[(skill,d)] for d in task.get('dependsOn',[])]
        elif kind=='model':
            s['after']=[last.get(skill,parents[skill])]; last[skill]=i
        elif kind=='final':
            s['after']=[last['compareOptions']] if skill=='planResolution' else [finals['planResolution']]
            finals[skill]=i
    return steps

def successful_stage_calls(calls):
    """Use the final attempt of each normal stage; retain omitted attempt IDs as provenance."""
    groups = {}
    for i, call in enumerate(calls):
        skill = next(s for s in ['resolveEquipment','planResolution','assessEquipment','compareOptions'] if mission(call['request'],s))
        text = system(call['request'])
        if 'All required plan tasks are already COMPLETE.' in text:
            stage = 'final'
        elif 'Exact capability/tool: ' in text:
            stage = 'action:' + text.split('Exact capability/tool: ',1)[1].splitlines()[0].strip()
        elif 'Create an ordered flight plan' in text:
            stage = 'plan'
        else:
            stage = 'model'
        key = (skill,stage)
        correction = 'YOUR PREVIOUS ACTION WAS INVALID' in text or any(
            m.get('role') == 'user' and m.get('content','').startswith((
                'The previous response could not be parsed as JSON.',
                'The previous response is valid JSON but does not satisfy the configured output_schema.'))
            for m in call['request'].get('messages',[]))
        if key in groups and not correction:
            raise ValueError('Repeated model stage without explicit Framework correction feedback')
        groups[key] = i
    selected = set(groups.values())
    return [c for i,c in enumerate(calls) if i in selected], [c['requestId'] for i,c in enumerate(calls) if i not in selected]


def derive(source, path, review_file, normalize_corrections=False):
    source,review_file=Path(source),Path(review_file)
    review=json.loads(review_file.read_bytes()); disposition=review.get('paths',{}).get(path,review)
    if disposition.get('status')!='SUITABLE_FOR_REPLAY_CURATION':
        raise ValueError('Source path is not suitable for curation')
    checks=json.loads((source/'checksums.json').read_bytes())
    if any(digest(source/name)!=wanted for name,wanted in checks.items()):
        raise ValueError('Source checksum mismatch')
    manifest=json.loads((source/'manifest.json').read_bytes())
    terminal=json.loads((source/(path+'-assessment.json')).read_bytes())
    body=json.loads((source/(path+'-input.json')).read_bytes()); old=body['caseId']
    expected=json.loads(terminal['result'])
    if terminal['status']!='COMPLETED' or expected['caseId']!=old: raise ValueError('Incomplete source')
    events=json.loads((source/'journal.json').read_bytes()); steps=[]
    calls=[e for e in events if e['event']=='model-request' and e.get('path')==path and e.get('caseId')==old]
    omitted=[]
    if normalize_corrections: calls,omitted=successful_stage_calls(calls)
    for call in calls:
        replies=[e for e in events if e['event']=='model-response' and e.get('requestId')==call['requestId'] and e.get('path')==path and e.get('caseId')==old]
        if len(replies)!=1 or replies[0].get('status')!=200 or replies[0].get('provenance')!='live OpenRouter': raise ValueError('Invalid source response')
        response=replies[0]['response']; choice=response['choices'][0]
        if choice.get('finish_reason')=='error' or choice.get('error'): raise ValueError('Provider error completion')
        value=json.loads(choice['message']['content'])
        skill=next(s for s in ['resolveEquipment','planResolution','assessEquipment','compareOptions'] if mission(call['request'],s))
        step={'contains':[CASE,"Fulfill the mission for skill '"+skill+"'"], 'systemContains':[],
              'response':normalized(response,old,CASE),'stageSkill':skill,'stageKind':'model',
              'provenance':{'sourceCapture':source.name,'sourcePath':path,'requestId':call['requestId'],
                            'sourceContentSha256':hashlib.sha256(choice['message']['content'].encode()).hexdigest(),
                            'normalization':'caseId only','mutations':[]}}
        if value.get('stepAction')=='CALL_TOOL':
            step.update(stageKind='action',taskId=value['taskId'],toolName=value['toolName'])
            step['systemContains']=['Exact capability/tool: '+value['toolName']]
        elif 'tasks' in value:
            step.update(stageKind='plan',tasks=value['tasks']); step['systemContains']=['Create an ordered flight plan']
        elif 'All required plan tasks are already COMPLETE.' in system(call['request']):
            step['stageKind']='final'; step['systemContains']=['All required plan tasks are already COMPLETE.']
        # Exact mission input prevents an otherwise matching stage accepting altered business evidence.
        message=next(m['content'] for m in call['request']['messages'] if m.get('role')=='user' and m.get('content','').startswith('Mission objective:'))
        canonical=json.JSONDecoder().raw_decode(message.split('Canonical mission input:\n',1)[1].lstrip())[0]
        step['missionInputEquals']=normalized(canonical,old,CASE)
        steps.append(step)
    outputs=[json.loads(s['response']['choices'][0]['message']['content']) for s in steps if s['stageSkill']=='compareOptions' or s['stageKind']=='final']
    outputs=[json.loads(v['finalResponse']) if isinstance(v.get('finalResponse'),str) else v.get('finalResponse',v) for v in outputs]
    wanted=normalized(expected,old,CASE)
    if len(outputs)!=3 or any(v!=wanted for v in outputs): raise ValueError('Published child/parent mismatch')
    return {**({'normalizeCorrections':True,'omittedCorrectionAttemptIds':omitted,
                'correctionNormalization':'Final captured response per normal stage; earlier attempts remain in original capture; no response wording edits'} if normalize_corrections else {}),
            'sourceCapture':source.name,'sourcePath':path,'originalCaseId':old,
            'sourceSha256':{name:digest(source/name) for name in [*checks,'checksums.json']},
            'semanticReview':review_file.relative_to(ROOT).as_posix(),'semanticReviewSha256':digest(review_file),
            'sourceManifest':manifest,'input':normalized(body,old,CASE),'expected':wanted,'steps':dependencies(steps)}

def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--output',type=Path,default=ROOT/'fixtures/replay/business-reviewed-v1.json'); args=parser.parse_args()
    samples={scenario:{path:derive(ROOT/('evidence/live-20261002-'+stamp),path,ROOT/('evidence/review-live-20261002-'+stamp+'/semantic-review.json')) for path,stamp in paths.items()} for scenario,paths in SOURCES.items()}
    result={'formatVersion':1,'status':'CURATED_CANDIDATE','approved':False,'normalization':'caseId only, including nested quote IDs; no response wording edits','mutations':[], 'scenarios':samples}
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8'); print(args.output)
if __name__=='__main__': main()
