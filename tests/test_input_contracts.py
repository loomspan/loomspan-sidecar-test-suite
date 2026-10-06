"""Contract boundaries are independent of model choice and source fixture answers."""
import copy
import importlib
import pytest
from pydantic import ValidationError
from apps.python.contracts import LookupInput, Approval
from author_workflow import CONTRACTS, DECISION_PROMPTS


def approval():
    return dict(assessmentVersion='v', option='standard', quoteId='q', attendance='window',
                scope=dict(repairHours=3, parts=['part'], onlyIfJustifiedByTechnician=True),
                cap=12345, idempotencyKey='key', approved=True)


@pytest.mark.parametrize('body', [dict(caseId='c'), dict(caseId='c', assetId='a', context={}),
                                dict(caseId='c', assetId=42)])
def test_lookup_rejects_unconsumed_or_invalid_inputs(body):
    with pytest.raises(ValidationError):
        LookupInput.model_validate(body)


def test_approval_has_structure_without_implying_permission():
    body=approval()
    assert Approval.model_validate(body).model_dump() == body
    body['approved']=False
    assert Approval.model_validate(body).approved is False  # Business code rejects it.
    for mutation in [dict(cap='12345'), dict(scope={}), dict(role='admin')]:
        bad={**body, **mutation}
        with pytest.raises(ValidationError):
            Approval.model_validate(bad)


@pytest.mark.parametrize('name', ['assetContext', 'createServiceRequest'])
def test_direct_rest_rejects_invalid_shape_before_business_call(monkeypatch, name):
    import asyncio
    monkeypatch.setenv('JWKS', 'http://unused.invalid/keys')
    module=importlib.import_module('apps.python.app')
    async def forbidden(*args, **kwargs):
        pytest.fail('Invalid input must not reach the business operation')
    monkeypatch.setattr(module.business, 'leaf', forbidden)
    monkeypatch.setattr(module.business, 'create', forbidden)
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as error:
        asyncio.run(module.deterministic(name, {'unexpected': True},
                    ({'roles': ['ASSESS_EQUIPMENT', 'REQUEST_SERVICE']}, 'unused')))
    assert error.value.status_code == 400


def test_contracts_separate_provided_derivation_and_raw_records():
    context=CONTRACTS['compareOptions']['properties']['context']
    assert 'entitlementDetermination' in context['required']
    assert 'determination' not in context['properties']['entitlements']['properties']
    assert context['properties']['entitlements']['additionalProperties'] is False
    # A name is genuinely optional in the source contact domain; cannot require
    # a field merely to make one captured model response copy it.
    contact=context['properties']['assetContext']['properties']['contacts']['items']
    assert 'name' not in contact['required']


def test_prompts_do_not_encode_the_demonstration_answer():
    text=' '.join(DECISION_PROMPTS.values())
    for fixture_value in ['Priya', 'Luis', '14:00', '11:00', '780', 'W-2', 'S-5', 'GLM', 'glm']:
        assert fixture_value not in text
