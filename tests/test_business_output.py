"""Offline checks of labeled examples and publication; no provider or live harness."""
import copy
import hashlib
import json
import socket

import pytest
import yaml
from fastapi import HTTPException
from apps.python import business
from conftest import ROOT
from derive_business_diagnostic import derive


@pytest.fixture
def diagnostic(monkeypatch):
    def no_network(*args, **kwargs):
        raise AssertionError('Offline business checks must not open network connections')
    monkeypatch.setattr(socket.socket, 'connect', no_network)
    return json.loads((ROOT / 'fixtures/replay/business-output-diagnostic-v1.json').read_text())


@pytest.mark.parametrize('path', ['java', 'sidecar'])
def test_edited_examples_preserve_authority_and_explain_business_handoff(diagnostic, path):
    sample = diagnostic['samples'][path]
    original, candidate = sample['original'], sample['candidate']
    assert diagnostic['approved'] is False and diagnostic['sourceDisposition'] == 'REJECTED_FOR_REPLAY'
    assert candidate['quotes'] == original['quotes']
    assert candidate['equipmentAssessment'] == original['equipmentAssessment']
    assert candidate['caseId'] == original['caseId'] and candidate['assetId'] == original['assetId']
    assert candidate['selectedOption'] == 'expedited'
    quote = next(q for q in candidate['quotes'] if q['option'] == 'expedited')
    assert (quote['maxExposure'], quote['fullyCoveredScopeMaximum'], quote['coverage']) == (78000, 30000, 'PENDING')
    assert {'W-2', 'W-5', 'S-3', 'S-4', 'S-5', 'AUTH-NB', 'SITE-WEST', 'RESOURCES-017'} <= set(candidate['citations'])
    next_decision = candidate['nextDecision']
    assert 'submit the approved expedited service request before ' + quote['expiresAt'] in next_decision
    assert 'Approval alone does not preserve prices' in next_decision
    assert 'does not reserve stock or confirm attendance' in next_decision
    assert 'does not extend the loaner offer' in next_decision
    assert 'Priya Shah' in next_decision and 'USD 2400.00' in next_decision and 'USD 1000.00' in next_decision
    assert 'renewed approval' in next_decision and 'matching dispatch confirmation or later quote expiry alone does not' in next_decision
    assert all(term in candidate['rationale'] for term in ['2-4 hour', '16:00', '20:00', 'beyond 18:00', 'Luis Romero', 'scope cap'])
    assert 'without after-hours arrangement' not in json.dumps(candidate)
    assert 'still pays diagnosis/travel included' not in json.dumps(candidate)
    if path == 'java':
        assert 'diagnosis and travel remain included even if unresolved (S-3)' in candidate['alternatives'][0]
    assert {edit['field'] for edit in sample['edits']} == {key for key in candidate if candidate[key] != original[key]}


def test_diagnostic_rederives_exactly_without_mutating_capture(diagnostic):
    source = ROOT / 'evidence' / diagnostic['sourceCapture']
    before = {name: (source / name).read_bytes() for name in diagnostic['sourceSha256']}
    assert {name: hashlib.sha256(raw).hexdigest() for name, raw in before.items()} == diagnostic['sourceSha256']
    assert derive(source) == diagnostic
    assert before == {name: (source / name).read_bytes() for name in before}


@pytest.mark.parametrize('path', ['java', 'sidecar'])
@pytest.mark.parametrize('selection', ['quote-id', 'unknown', 'missing'])
def test_noncanonical_selection_never_publishes(monkeypatch, tmp_path, diagnostic, path, selection):
    monkeypatch.setattr(business, 'DB', str(tmp_path / 'business.db'))
    value = copy.deepcopy(diagnostic['samples'][path]['candidate'])
    with business.db() as c:
        for quote in value['quotes']:
            c.execute('INSERT INTO quotes VALUES(?,?)', (quote['quoteId'], json.dumps(quote)))
    if selection == 'missing':
        value.pop('selectedOption')
    else:
        value['selectedOption'] = value['quotes'][0]['quoteId'] if selection == 'quote-id' else 'Express'
    with pytest.raises(HTTPException):
        business.save_assessment('offline', json.dumps(value), {'sub': 'maya'})
    with business.db() as c:
        assert c.execute('SELECT COUNT(*) FROM assessments').fetchone()[0] == 0
        assert c.execute('SELECT COUNT(*) FROM requests').fetchone()[0] == 0


@pytest.mark.parametrize('skill', ['compareOptions', 'planResolution', 'resolveEquipment'])
def test_shared_decision_schema_rejects_original_java_quote_id(diagnostic, skill):
    config = yaml.safe_load((ROOT / 'config/skills' / (skill + '.yaml')).read_text())
    allowed = config['output_schema']['properties']['selectedOption']['enum']
    assert diagnostic['samples']['java']['original']['selectedOption'] not in allowed
    assert all(s['candidate']['selectedOption'] in allowed for s in diagnostic['samples'].values())
    assert {'standard', 'loaner', 'replacement', 'defer', 'undecided'} <= set(allowed)
    # Existing quote and authoritative-context/unit contracts stay present.
    assert config['output_schema']['properties']['quotes']['items']['additionalProperties'] is False
    assert 'integer USD cents' in config['prompt'] and 'authoritative assetContext' in config['prompt']
