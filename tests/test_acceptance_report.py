"""Consolidation cannot turn missing, skipped, mutated or one-path evidence into acceptance."""
import copy
import hashlib
import json
import pytest
from acceptance_report import SCENARIOS, checksums, consolidate, junit_counts


def passing_inputs():
    stages = [{'scenario':name,'freshCapture':True,'paidCalls':0,'evidenceVerified':True,
               'review':{'status':'PASS','checks':[{'path':p,'passed':True} for p in ['java','sidecar']]},
               'assertions':{'tests':16 if name=='isolation' else 8,'passed':16 if name=='isolation' else 8,
                             'failures':0,'errors':0,'skipped':0}} for name in SCENARIOS]
    runtime={'ready':True,'providerDisabled':True,'normalConfiguration':True,'artifactsUnchanged':True}
    integrity={'status':'PASS'}
    audit={'focusedTests':{'passed':50,'failures':0,'errors':0,'skipped':0},
           'requirements':[{'status':'PARTIAL'}]}
    return stages,runtime,integrity,audit


def test_offline_pass_does_not_approve_partial_delivery():
    result=consolidate(*passing_inputs())
    assert result['status']=='PASS' and result['workflowAssertions']==56
    assert result['firstDeliveryComplete'] is False


@pytest.mark.parametrize('mutation', ['missing-scenario','duplicate-scenario','empty-checks','one-path',
                                    'failed-check','skipped-test','paid-call','old-capture','provider-enabled',
                                    'restoration-failed','integrity-failed'])
def test_incomplete_or_failed_evidence_cannot_pass(mutation):
    stages,runtime,integrity,audit=copy.deepcopy(passing_inputs())
    if mutation=='missing-scenario': stages.pop()
    elif mutation=='duplicate-scenario': stages[-1]['scenario']='baseline'
    elif mutation=='empty-checks': stages[0]['review']['checks']=[]
    elif mutation=='one-path': stages[0]['review']['checks'].pop()
    elif mutation=='failed-check': stages[0]['review']['checks'][0]['passed']=False
    elif mutation=='skipped-test': stages[0]['assertions'].update(skipped=1,passed=7)
    elif mutation=='paid-call': stages[0]['paidCalls']=1
    elif mutation=='old-capture': stages[0]['freshCapture']=False
    elif mutation=='provider-enabled': runtime['providerDisabled']=False
    elif mutation=='restoration-failed': runtime['normalConfiguration']=False
    elif mutation=='integrity-failed': integrity['status']='FAIL'
    result=consolidate(stages,runtime,integrity,audit)
    assert result['status']=='FAIL' and result['firstDeliveryComplete'] is False


def test_checksum_verification_rejects_mutation_and_path_escape(tmp_path):
    file=tmp_path/'journal.json';file.write_text('original')
    index=tmp_path/'checksums.json'
    index.write_text(json.dumps({'journal.json':hashlib.sha256(file.read_bytes()).hexdigest()}))
    assert checksums(tmp_path)==1
    file.write_text('changed')
    with pytest.raises(ValueError,match='checksum mismatch'): checksums(tmp_path)
    index.write_text(json.dumps({'../outside': 'wrong'}))
    with pytest.raises(ValueError,match='checksum mismatch'): checksums(tmp_path)


def test_junit_counts_distinguish_skips_failures_errors(tmp_path):
    file=tmp_path/'junit.xml'
    file.write_text('<testsuites><testsuite tests="8" failures="1" errors="1" skipped="2"/></testsuites>')
    assert junit_counts(file)=={'tests':8,'passed':4,'failures':1,'errors':1,'skipped':2}
