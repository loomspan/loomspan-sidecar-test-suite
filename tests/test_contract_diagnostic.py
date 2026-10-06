"""Captured response reuse through real Frameworks, explicitly not approved replay."""
import copy
import json
import uuid
from conftest import ROOT
from capture import wait
from test_deterministic import invoke, register


def test_authoritative_asset_and_approval_context(harness,target):
    path,api=target;h=harness;case=register(h,path)
    rejected=h['client'].post(api+'/v1/skills/assetContext/executions',
        json={'caseId':case,'assetId':'NB-P240-017','context':{'serial':'forged'}},
        headers={'Authorization':'Bearer '+h['tokens']['maya']})
    assert rejected.status_code==400
    value=invoke(h,api,'assetContext',{'caseId':case,'assetId':'NB-P240-017'})
    data=value['data']
    assert data['serial']=='AP24B-0517' and data['model']=='P240' and data['hardwareRevision']=='B'
    assert data['site']['siteId']=='NB-WEST' and data['approvalContext']['luisMaximumCustomerExposure']==100000
    assert data['approvalContext']['monetaryUnit']=='cents' and data['approvalContext']['mayaMayCommit'] is False
    assert any(c.get('name')=='Priya Shah' for c in data['contacts'])
    (h['out']/(path+'-asset-context.json')).write_text(json.dumps(value,indent=2))


def test_captured_quote_contract_correction_diagnostic(harness,target):
    path,api=target;h=harness
    source=json.loads((ROOT/'fixtures/replay/quote-contract-diagnostic-v1.json').read_text())
    assert source['approved'] is False
    case='contract-'+path+'-'+uuid.uuid4().hex;h['cases'].append(case)
    def normalized(sample,value):
        return json.loads(json.dumps(value).replace(sample['caseId'],case))
    invalid=source['samples']['java'];valid=source['samples']['sidecar']
    steps=[]
    for i,sample in enumerate([invalid,valid]):
        steps.append({'contains':[case], 'after':list(range(i)),
                      'response':normalized(sample,sample['response']),
                      'provenance':{'kind':'unapproved captured contract diagnostic','sourceCapture':source['sourceCapture'],
                          'sourceSha256':source['sourceSha256'],'requestId':sample['requestId'],**sample['provenance'],
                          'normalization':'caseId only','syntheticCorrectionSequence':True}})
    r=h['client'].post('http://127.0.0.1:18090/control/cases/'+case,json={'mode':'replay','path':path,'steps':steps},
                       headers={'X-Control-Key':h['secrets']['control']});r.raise_for_status()
    body=normalized(valid,copy.deepcopy(valid['input']))
    result=invoke(h,api,'compareOptions',body)
    expected=json.loads(normalized(valid,valid['response'])['choices'][0]['message']['content'])
    assert result==expected
    events=h['client'].get('http://127.0.0.1:18090/control/journal',headers={'X-Control-Key':h['secrets']['control']}).json()
    requests=[e for e in events if e.get('caseId')==case and e['event']=='model-request']
    assert len(requests)==2,'Captured invalid quote output must trigger actual Framework correction'
    feedback=json.dumps(requests[1]['request'])
    assert 'quotes' in feedback and ('validation' in feedback.lower() or 'schema' in feedback.lower())
    assert 'integer USD cents' in json.dumps(requests[0]['request'])
    assert all(e.get('provenance')!='live OpenRouter' for e in events if e.get('caseId')==case)
    (h['out']/(path+'-contract-diagnostic.json')).write_text(json.dumps({'approved':False,'result':result,
        'sourceSha256':source['sourceSha256'],'scope':'Schema correction only; captured response still semantically incomplete'},indent=2))


def test_source_money_units_and_applicability(harness,target):
    path,api=target;h=harness;case=register(h,path)
    body={'caseId':case,'assetId':'NB-P240-017'}
    terms=invoke(h,api,'serviceTerms',body)['data']
    offers=invoke(h,api,'continuityOptions',body)['data']
    passages=invoke(h,api,'referenceEvidence',body)['data']
    assert terms['rates']['monetaryUnit']=='cents' and terms['rates']['currency']=='USD'
    assert terms['rates']['expedited']==30000 and terms['rates']['repairHourly']==15000
    assert offers['monetaryUnit']=='cents' and offers['currency']=='USD'
    assert offers['loaner']['price']==240000 and offers['replacement']['price']==1250000
    assert offers['replacement']['currency']=='USD'
    assert terms['certificate']['serial']=='AP24B-0517'
    bulletin=next(p for p in passages if p['id']=='SB-2')
    assert bulletin['applicability']['serialRangeInclusive']==['AP24B-0400','AP24B-0799']
