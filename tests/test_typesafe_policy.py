import copy
import json
import math
import sys
from pathlib import Path
import pytest
from apps.python.suites.typesafe_ai.policy import decide

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
CASES = json.loads((ROOT / 'fixtures/typesafe-ai/impact-policy-cases.json').read_bytes())


@pytest.mark.parametrize('case', CASES, ids=lambda c: c['name'])
def test_shared_policy_contract(case):
    original = copy.deepcopy(case['answers'])
    assert decide(case['answers'], case['threshold']) == case['expected']
    assert case['answers'] == original


@pytest.mark.parametrize('threshold', [True, '0.8', math.nan, math.inf, -.1, 1.1])
def test_invalid_threshold(threshold):
    with pytest.raises(ValueError): decide({}, threshold)


def test_non_finite_judgment():
    assert decide({'impactEvidence': {'type': 'noul', 'noul': math.nan}})['reason'] == 'INVALID_JUDGMENTS'
    assert decide({'impactEvidence': {'type': 'noul', 'noul': 10**1000}})['reason'] == 'INVALID_JUDGMENTS'


def test_real_response_composition_preserves_native_envelopes():
    from suites.typesafe_ai.scenarios import load
    cases = load()[1]
    by_name = {c['name']: c for c in cases}
    derived = [c for c in cases if 'reviewed-live-composition' in c['coverage']]
    assert len(derived) == 14
    for case in derived:
        source = by_name[case['name'].split('__')[0]]
        assert case['responses'] == source['responses']
        assert case['request'] == source['request']
        if case['skill'] != 'tsTriageSummary': assert case['expected'] == source['expected']
