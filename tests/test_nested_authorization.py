"""Partial authorization diagnostic; handcrafted scripts are NOT approved replay.

Run with compose.authorization.yaml. Full acceptance also requires otherwise-valid
approval and Luis's durable-creation positive control after a reviewed assessment.
"""
import json
import os
import sqlite3
import subprocess
import uuid
import pytest

from conftest import ROOT
from capture import wait

pytestmark=pytest.mark.skipif(os.getenv('AUTHORIZATION_DIAGNOSTICS')!='1',
    reason='Opt in with AUTHORIZATION_DIAGNOSTICS=1 and compose.authorization.yaml; partial diagnostic only')


def envelope(value):
    return {'id':'diagnostic-'+uuid.uuid4().hex,'object':'chat.completion','created':1790851200,
            'model':'openai/gpt-6.1-sol','choices':[{'index':0,'finish_reason':'stop',
            'message':{'role':'assistant','content':json.dumps(value)}}]}


def plan(parent, child):
    return {'capabilityName':parent,'createdAt':'2026-10-01T00:00:00Z','status':'VALID',
            'tasks':[{'taskId':'delegate','title':'Delegate supplied approval','status':'PENDING',
                      'capabilityName':child,'intent':'Pass the supplied approval unchanged.',
                      'dependsOn':[],'expectedOutputs':['Receipt'],'parallelGroup':None,'note':''}]}


def test_nested_capability_filter_and_rejection(harness,target):
    path,api=target; h=harness
    case='nested-denial-'+path+'-'+uuid.uuid4().hex; h['cases'].append(case)
    # Intentionally incomplete: this diagnostic proves capability filtering only.
    # Do not substitute it for the approval-bound denial/positive-control pair.
    body={'caseId':case,'approval':{'idempotencyKey':case,'approved':True}}
    steps=[
        {'contains':[case], 'systemContains':['"capabilityName": "authorizationParent"','Create an ordered flight plan'],
         'response':envelope(plan('authorizationParent','authorizationNested'))},
        {'contains':[case], 'systemContains':['Exact capability/tool: authorizationNested'], 'after':[0],
         'response':envelope({'stepAction':'CALL_TOOL','taskId':'delegate','toolName':'authorizationNested','toolArguments':body})},
        {'contains':[case], 'systemContains':['"capabilityName": "authorizationNested"','Create an ordered flight plan',
          'Available sub-skills (use these exact names for task capabilityName):\n(none)'], 'after':[1],
         'response':envelope(plan('authorizationNested','createServiceRequest'))},
    ]
    steps.append({'contains':[case], 'systemContains':['"capabilityName": "authorizationNested"',
        "value 'createServiceRequest' is not an exact visible capability name."], 'after':[2],
        'response':envelope(plan('authorizationNested','createServiceRequest'))})
    for step in steps: step['provenance']='hand-authored negative diagnostic; not reviewed real-model replay'
    r=h['client'].post('http://127.0.0.1:18090/control/cases/'+case,
        json={'mode':'replay','path':path,'steps':steps},headers={'X-Control-Key':h['secrets']['control']});r.raise_for_status()
    db=ROOT/'.runtime'/('python' if path=='sidecar' else 'java')/'equipment.db'
    def records():
        with sqlite3.connect(f'file:{db.as_posix()}?mode=ro',uri=True) as c:
            return c.execute('SELECT owner,key,content,receipt FROM requests ORDER BY owner,key').fetchall()
    before=records()
    # The independent server access log establishes absence of REST invocation.
    def creation_calls():
        run=subprocess.run(['docker','logs','equipment-acceptance-python-1'],capture_output=True,text=True,check=True)
        return sum('/skills/createServiceRequest ' in line for line in (run.stdout+run.stderr).splitlines())
    calls_before=creation_calls()
    r=h['client'].post(api+'/v1/skills/authorizationParent/executions',json=body,
                       headers={'Authorization':'Bearer '+h['tokens']['maya']});r.raise_for_status()
    result=wait(h['client'],api,r.json()['id'],h['tokens']['maya'],timeout=60)
    events=h['client'].get('http://127.0.0.1:18090/control/journal',headers={'X-Control-Key':h['secrets']['control']}).json()
    events=[e for e in events if e.get('caseId')==case]
    evidence={'scope':'Partial handcrafted nested denial diagnostic; positive control and valid approval not exercised',
              'caseId':case,'result':result,'requestsBefore':before,'requestsAfter':records(),
              'creationEndpointCallsBefore':calls_before,'creationEndpointCallsAfter':creation_calls()}
    (h['out']/(path+'-nested-denial.json')).write_text(json.dumps(evidence,indent=2),encoding='utf-8')
    assert result['status']=='FAILED',result
    assert not [e for e in events if e['event']=='model-rejected'], 'Unexpected scripted request is not authorization evidence'
    responses=[e for e in events if e['event']=='model-response']
    assert [e['stage'] for e in responses]==[0,1,2,3], 'Nested planner denial/correction was not reached'
    assert before==evidence['requestsAfter']
    if path=='sidecar': assert calls_before==evidence['creationEndpointCallsAfter']
    # Terminal rejection must be accompanied by the actual filtered planner request.
    nested=next(e['request'] for e in events if e['event']=='model-request' and
                any('"capabilityName": "authorizationNested"' in m.get('content','')
                    for m in e['request']['messages'] if m['role']=='system'))
    system='\n'.join(m['content'] for m in nested['messages'] if m['role']=='system')
    available=system.split('Available sub-skills (use these exact names for task capabilityName):',1)[1].split('Constraints:',1)[0]
    assert 'createServiceRequest' not in available and '(none)' in available
