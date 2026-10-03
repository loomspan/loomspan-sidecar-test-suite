"""Delivery evidence must remain content-bound and preserve semantic qualifications."""
import hashlib
import pytest
from audit_fresh_live import verify_bindings, verify_semantics, QUALIFIED


def test_semantic_binding_rejects_changed_original(tmp_path):
    source = tmp_path / 'assessment.json'
    source.write_text('original child result')
    bindings = {source.name: hashlib.sha256(source.read_bytes()).hexdigest()}
    verify_bindings(tmp_path, bindings)
    source.write_text('paraphrased child result')
    with pytest.raises(ValueError, match='binding mismatch'):
        verify_bindings(tmp_path, bindings)


@pytest.mark.parametrize('change', ['unqualified', 'replay-approved', 'missing-priority'])
def test_audit_cannot_upgrade_semantic_disposition(change):
    semantic = {'status': QUALIFIED, 'approvedForReplay': False,
                'conclusions': [{'area': 'priority responsiveness',
                                 'result': 'JAVA_INCONCLUSIVE_SIDECAR_OBSERVED'}]}
    verify_semantics(semantic)
    if change == 'unqualified': semantic['status'] = 'PASS'
    elif change == 'replay-approved': semantic['approvedForReplay'] = True
    else: semantic['conclusions'] = []
    with pytest.raises(ValueError, match='qualification changed'):
        verify_semantics(semantic)
