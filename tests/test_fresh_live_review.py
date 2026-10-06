"""Regression checks for native-parent fidelity and complete evidence comparison."""
from copy import deepcopy
from review_fresh_live import final_response_matches, contains, contains_source, planning_checks


def test_citations_accept_only_issued_quote_ids_or_known_sources():
    import re
    from review_fresh_live import citation_is_known
    pattern = re.compile(r'S-\d+')
    def valid(value):
        return citation_is_known(value, {'S-3'}, {'this-case-expedited-v1'}, pattern)
    assert valid('this-case-expedited-v1')
    assert valid('Included services (S-3)')
    assert not valid('other-case-expedited-v1')
    assert not valid('this-case-invented-v1')
    assert not valid('operatingNeeds')
    assert not valid('S-999')


def test_native_parent_envelope_preserves_business_result():
    value = {'citations': ['S-3', 'S-5'], 'equipmentAssessment': {'chronology': ['first', 'later']}}
    assert final_response_matches({'stepAction': 'FINAL_RESPONSE', 'finalResponse': deepcopy(value)}, value)
    assert final_response_matches(deepcopy(value), value)
    assert not final_response_matches({'stepAction': 'CALL_SKILL', 'finalResponse': value}, value)


def test_parent_cannot_drop_citation_or_rewrite_actual_child():
    value = {'citations': ['S-3', 'S-5'], 'equipmentAssessment': {'chronology': ['first', 'later']}}
    for mutated in [dict(value, citations=['S-3']),
                    dict(value, equipmentAssessment={'chronology': ['later', 'first']})]:
        assert not final_response_matches({'stepAction': 'FINAL_RESPONSE', 'finalResponse': mutated}, value)
        assert not final_response_matches(mutated, value)


def test_complete_source_match_rejects_truncation_despite_same_marker():
    source = {'id': 'SB-2', 'applicability': {'serialRangeInclusive': ['0400', '0799']}, 'text': 'complete'}
    assert contains({'context': {'sources': [deepcopy(source)]}}, source)
    assert not contains({'context': {'sources': [{'id': 'SB-2', 'text': 'complete'}]}}, source)


def test_technical_assessment_must_not_wait_for_commercial_terms():
    skills = ['assetContext', 'serviceHistory', 'referenceEvidence', 'serviceTerms',
              'assessEquipment', 'planResolution']
    deps = [[], ['0'], ['0'], ['0'], ['1', '2'], ['3', '4']]
    plan = {'tasks': [{'taskId': str(i), 'capabilityName': name, 'dependsOn': deps[i],
                      'parallelGroup': 'reads' if i in [1, 2, 3] else None}
                     for i, name in enumerate(skills)]}
    assert all(planning_checks(plan, 'resolveEquipment').values())
    plan['tasks'][4]['dependsOn'].append('3')
    result = planning_checks(plan, 'resolveEquipment')
    assert not result['technical assessment depends on technical evidence without commercial reads']
    assert sum(not v for v in result.values()) == 1


def test_source_collection_reordering_is_not_evidence_loss():
    source = [{'id': 'MAN-3.3', 'text': 'hypotheses'}, {'id': 'MAN-3.4', 'text': 'verification'}]
    assert contains_source({'context': list(reversed(source))}, source)
    assert not contains_source({'context': source[:1]}, source)
    assert not contains_source({'context': [source[0], source[0]]}, source)
    assert not contains_source({'context': source + [source[0]]}, source)


def test_identifier_only_reads_use_joined_unit_order_without_redundant_dependencies():
    skills = ['assetContext', 'serviceHistory', 'referenceEvidence', 'serviceTerms',
              'assessEquipment', 'planResolution']
    deps = [[], [], [], [], ['0', '1', '2'], ['3', '4']]
    tasks = [{'taskId': str(i), 'capabilityName': name, 'dependsOn': deps[i],
              'parallelGroup': 'reads' if i in [1, 2, 3] else None}
             for i, name in enumerate(skills)]
    key = 'independent evidence reads share a parallel group after asset scope'
    assert all(planning_checks({'tasks': tasks}, 'resolveEquipment').values())
    # Reads before scope, overlap with scope, or a split group violate sequencing.
    before = tasks[1:4] + [tasks[0]] + tasks[4:]
    overlap = deepcopy(tasks)
    overlap[0]['parallelGroup'] = 'reads'
    split = tasks[:2] + [tasks[4]] + tasks[2:4] + [tasks[5]]
    for invalid in [before, overlap, split]:
        assert not planning_checks({'tasks': invalid}, 'resolveEquipment')[key]
    missing_input = deepcopy(tasks)
    missing_input[4]['dependsOn'] = ['0', '1']
    assert not planning_checks({'tasks': missing_input}, 'resolveEquipment')[
        'technical assessment depends on technical evidence without commercial reads']
