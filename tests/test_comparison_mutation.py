"""Retain source provenance and mutate only the named comparison field."""
import hashlib
import json
import pytest
from conftest import ROOT
from capture_comparison_correction import sample
from inspect_capture import mission


def test_missing_field_mutation_preserves_all_other_real_fields():
    source = ROOT / 'evidence/live-20261002-000544'
    before = (source / 'journal.json').read_bytes()
    events = json.loads(before)
    call = next(e for e in events if e['event'] == 'model-request' and e.get('path') == 'sidecar'
                and mission(e['request'], 'compareOptions'))
    reply = next(e for e in events if e['event'] == 'model-response' and e.get('requestId') == call['requestId'])
    original = json.loads(reply['response']['choices'][0]['message']['content'])
    body, injected, provenance = sample(source, 'sidecar', 'fresh-mutation-case')
    expected = json.loads(json.dumps(original).replace(call['caseId'], 'fresh-mutation-case'))
    expected.pop('nextDecision')
    assert injected == expected and 'nextDecision' not in injected
    assert body['caseId'] == 'fresh-mutation-case' and body['assetId'] == 'NB-P240-017'
    assert provenance['sourceRequestId'] == call['requestId']
    assert provenance['sourceContentSha256'] == hashlib.sha256(reply['response']['choices'][0]['message']['content'].encode()).hexdigest()
    assert provenance['approvedBusinessReplay'] is False
    assert before == (source / 'journal.json').read_bytes()


def test_already_invalid_selection_is_not_a_missing_field_source():
    with pytest.raises(ValueError, match='Source selection'):
        sample(ROOT / 'evidence/live-20261002-000544', 'java', 'fresh-mutation-case')


def test_comparison_source_requires_real_successful_provider_reply(tmp_path):
    source = ROOT / 'evidence/live-20261002-000544'
    events = json.loads((source / 'journal.json').read_text())
    for e in events:
        if e['event'] == 'model-response': e['provenance'] = 'synthetic'
    (tmp_path / 'journal.json').write_text(json.dumps(events))
    with pytest.raises(ValueError, match='unique real'):
        sample(tmp_path, 'sidecar', 'fresh-mutation-case')
