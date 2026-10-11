"""API-level checks and semantic evaluation labels, separate from application code."""
SKILLS = {'tsTriageEvidence', 'tsTriageEvidenceForward', 'tsTriageEvidenceSummary'}


def verify(client, api, execution, headers, terminal, case, result, bundle, prefix):
    if case['skill'] not in SKILLS or terminal.get('status') != 'COMPLETED': return
    response = client.get(api + '/executions/' + execution + '/impact', headers=headers)
    response.raise_for_status()
    view = response.json()
    bundle.add(prefix + '/impact-view.json', view)
    decision = view['impactDecision']
    result['impactDecision'] = decision
    result['checks']['decision preserves raw result'] = view['result'] == terminal['result']
    result['checks']['explicit default policy'] = decision['evidenceThreshold'] == .8
    expected = case.get('policyExpected')
    if expected:
        result['checks']['predeclared impact decision'] = all(decision.get(k) == v for k, v in expected.items())
    result['checks']['deferred impact is absent'] = decision['status'] == 'ASSESSED' or decision['impactScore'] is None
    rubric = case.get('decisionRubric')
    if rubric:
        # Semantic failures remain visible even when all mechanical checks pass.
        if decision['status'] == 'NEEDS_CLARIFICATION':
            result['decisionReview'] = 'UNNECESSARY_CLARIFICATION' if rubric['sufficient'] else 'CORRECT_CLARIFICATION'
        elif not rubric['sufficient']:
            result['decisionReview'] = 'UNSUPPORTED_ASSESSMENT'
        else:
            lo, hi = rubric['impact']
            result['decisionReview'] = 'CORRECT_ASSESSMENT' if lo <= decision['impactScore'] <= hi else 'INCORRECT_IMPACT'
    if case['name'] == 'reference_evidence_partial_java':
        alternate = client.get(api + '/executions/' + execution + '/impact',
                               headers=headers, params={'evidenceThreshold': '.75'})
        alternate.raise_for_status()
        result['checks']['explicit threshold override'] = alternate.json()['impactDecision'] == {
            'status': 'ASSESSED', 'reason': 'SUFFICIENT_EVIDENCE', 'impactScore': 1.,
            'evidenceProbability': .77, 'evidenceThreshold': .75}
        for value in ('NaN', '-0.1', '1.1', 'not-a-number'):
            result['checks']['invalid threshold rejected: ' + value] = client.get(
                api + '/executions/' + execution + '/impact', headers=headers,
                params={'evidenceThreshold': value}).status_code == 400


def summarize(cases):
    labels = ('CORRECT_ASSESSMENT', 'CORRECT_CLARIFICATION', 'UNNECESSARY_CLARIFICATION',
              'UNSUPPORTED_ASSESSMENT', 'INCORRECT_IMPACT')
    return {label: sum(c.get('decisionReview') == label for c in cases) for label in labels}
