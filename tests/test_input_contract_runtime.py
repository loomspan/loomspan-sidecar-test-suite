"""Both deployed Framework boundaries reject invalid arguments without model calls."""
import uuid


def test_lookup_rejects_unused_context(harness, target):
    _, api=target
    body={'caseId': 'invalid-'+uuid.uuid4().hex, 'assetId': 'NB-P240-017', 'context': {}}
    response=harness['client'].post(api+'/v1/skills/assetContext/executions', json=body,
        headers={'Authorization': 'Bearer '+harness['tokens']['maya']})
    assert response.status_code == 400, response.text


def test_approval_requires_nested_scope(harness, target):
    _, api=target
    body={'approval': {'assessmentVersion':'missing', 'option':'standard', 'quoteId':'missing',
        'attendance':'window', 'cap':1, 'approved':True, 'idempotencyKey':uuid.uuid4().hex, 'scope':{}}}
    response=harness['client'].post(api+'/v1/skills/createServiceRequest/executions', json=body,
        headers={'Authorization': 'Bearer '+harness['tokens']['luis']})
    assert response.status_code == 400, response.text
