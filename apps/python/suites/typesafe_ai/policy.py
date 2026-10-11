"""Application policy over retained judgments; no inference or customer action."""
import math

SUPPORTED_SKILLS = {'tsTriageEvidence', 'tsTriageEvidenceForward', 'tsTriageEvidenceSummary'}


def number(value, low, high):
    return type(value) in (int, float) and low <= value <= high and math.isfinite(value)


def decide(answers, threshold=0.80):
    if not number(threshold, 0, 1):
        raise ValueError('evidenceThreshold must be finite and between 0 and 1')
    result = {'status': 'NEEDS_CLARIFICATION', 'reason': 'INVALID_JUDGMENTS',
              'impactScore': None, 'evidenceProbability': None, 'evidenceThreshold': threshold}
    if not isinstance(answers, dict): return result
    evidence = answers.get('impactEvidence')
    if not isinstance(evidence, dict) or evidence.get('type') != 'noul' or not number(evidence.get('noul'), 0, 1):
        return result
    result['evidenceProbability'] = evidence['noul']
    if evidence['noul'] < threshold:
        result['reason'] = 'INSUFFICIENT_EVIDENCE'
        return result  # Deliberately ignore the unused Score branch.
    impact = answers.get('impact')
    if not isinstance(impact, dict) or impact.get('type') != 'score': return result
    probabilities = impact.get('probabilities')
    if (not number(impact.get('score'), 0, 2) or not number(impact.get('confidence'), 0, 1)
            or not isinstance(probabilities, dict) or set(probabilities) != {'0', '1', '2'}
            or not all(number(v, 0, 1) for v in probabilities.values())
            or abs(sum(probabilities.values()) - 1) > .001
            or abs(impact['score'] - sum(int(k)*v for k, v in probabilities.items())) > .01 + 1e-12):
        return result
    result.update(status='ASSESSED', reason='SUFFICIENT_EVIDENCE', impactScore=impact['score'])
    return result
