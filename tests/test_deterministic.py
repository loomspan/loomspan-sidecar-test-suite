"""Public-boundary checks, deliberately separate from blocked full acceptance."""
import json, sqlite3, uuid
from conftest import ROOT
from capture import wait
def register(h,path):
    case='check-'+path+'-'+uuid.uuid4().hex;h['cases'].append(case)
    r=h['client'].post('http://127.0.0.1:18090/control/cases/'+case,json={'mode':'replay','steps':[]},headers={'X-Control-Key':h['secrets']['control']});r.raise_for_status();return case
def invoke(h,api,skill,body,user='maya'):
    r=h['client'].post(api+'/v1/skills/'+skill+'/executions',json=body,headers={'Authorization':'Bearer '+h['tokens'][user]});r.raise_for_status()
    result=wait(h['client'],api,r.json()['id'],h['tokens'][user]);assert result['status']=='COMPLETED',result
    return json.loads(result['result'])
def test_authoritative_quotes_no_model(harness,target):
    path,api=target;h=harness;case=register(h,path)
    value=invoke(h,api,'quoteOptions',{'caseId':case,'assetId':'NB-P240-017','context':{}})
    quotes={q['option']:q for q in value['quotes']}
    assert quotes['expedited']['maxExposure']==78000
    assert quotes['expedited']['fullyCoveredScopeMaximum']==30000
    assert quotes['standard']['maxExposure']==48000
    assert quotes['standard']['fullyCoveredScopeMaximum']==0
    assert all(q['coverage']=='PENDING' and not q['reservation'] and not q['restorationGuaranteed'] for q in quotes.values())
    assert quotes['expedited']['scope']=={'repairHours':2,'parts':['S17-B','H17-B'],'onlyIfJustifiedByTechnician':True}
    events=h['client'].get('http://127.0.0.1:18090/control/journal',headers={'X-Control-Key':h['secrets']['control']}).json()
    assert not [e for e in events if e.get('caseId')==case and e['event']=='model-request']
    (h['out']/(path+'-quotes.json')).write_text(json.dumps(value,indent=2))
def test_direct_permission_precheck(harness,target):
    # This proves role denial at the public boundary, not the full otherwise-valid
    # approved-assessment acceptance scenario (which is blocked upstream).
    path,api=target;h=harness
    db=ROOT/'.runtime'/('python' if path=='sidecar' else 'java')/'equipment.db'
    def records():
        if not db.exists(): return []
        with sqlite3.connect(f'file:{db.as_posix()}?mode=ro',uri=True) as c:
            return c.execute('SELECT owner,key,content,receipt FROM requests ORDER BY owner,key').fetchall()
    before=records()
    r=h['client'].post(api+'/v1/skills/createServiceRequest/executions',json={'approval':{}},headers={'Authorization':'Bearer '+h['tokens']['maya']})
    assert r.status_code==403,r.text
    assert records()==before
def test_missing_token_rejected(harness,target):
    _,api=target
    assert harness['client'].post(api+'/v1/skills/quoteOptions/executions',json={}).status_code==401
