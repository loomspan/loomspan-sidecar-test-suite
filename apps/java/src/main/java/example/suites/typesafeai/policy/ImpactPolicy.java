package example.suites.typesafeai.policy;

import java.util.*;

/** Application-owned consumption policy, separate from Loomspan answer passthrough. */
public final class ImpactPolicy {
    public static final Set<String> SKILLS = Set.of("tsTriageEvidence", "tsTriageEvidenceForward", "tsTriageEvidenceSummary");
    private ImpactPolicy() {}

    private static boolean number(Object value, double low, double high) {
        return value instanceof Number n && Double.isFinite(n.doubleValue())
            && n.doubleValue() >= low && n.doubleValue() <= high;
    }

    public static Map<String, Object> decide(Object answers, double threshold) {
        if (!Double.isFinite(threshold) || threshold < 0 || threshold > 1)
            throw new IllegalArgumentException("evidenceThreshold must be finite and between 0 and 1");
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("status", "NEEDS_CLARIFICATION");
        result.put("reason", "INVALID_JUDGMENTS");
        result.put("impactScore", null);
        result.put("evidenceProbability", null);
        result.put("evidenceThreshold", threshold);
        if (!(answers instanceof Map<?, ?> a) || !(a.get("impactEvidence") instanceof Map<?, ?> evidence)
                || !"noul".equals(evidence.get("type")) || !number(evidence.get("noul"), 0, 1)) return result;
        double probability = ((Number)evidence.get("noul")).doubleValue();
        result.put("evidenceProbability", probability);
        if (probability < threshold) {
            result.put("reason", "INSUFFICIENT_EVIDENCE");
            return result; // Ignore the unused Score branch.
        }
        if (!(a.get("impact") instanceof Map<?, ?> impact) || !"score".equals(impact.get("type"))
                || !number(impact.get("score"), 0, 2) || !number(impact.get("confidence"), 0, 1)
                || !(impact.get("probabilities") instanceof Map<?, ?> p)
                || !p.keySet().equals(Set.of("0", "1", "2"))
                || !p.values().stream().allMatch(v -> number(v, 0, 1))) return result;
        double total = p.values().stream().mapToDouble(v -> ((Number)v).doubleValue()).sum();
        double weighted = ((Number)p.get("1")).doubleValue() + 2 * ((Number)p.get("2")).doubleValue();
        double score = ((Number)impact.get("score")).doubleValue();
        if (Math.abs(total - 1) > .001 || Math.abs(score - weighted) > .01 + 1e-12) return result;
        result.put("status", "ASSESSED");
        result.put("reason", "SUFFICIENT_EVIDENCE");
        result.put("impactScore", score);
        return result;
    }
}
