package example.suites.typesafeai;

import example.suites.typesafeai.policy.ImpactPolicy;
import tools.jackson.databind.json.JsonMapper;
import java.nio.file.*;
import java.util.*;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class ImpactPolicyTest {
    @Test void sharedContract() throws Exception {
        var mapper = JsonMapper.builder().build();
        var file = Path.of("../../fixtures/typesafe-ai/impact-policy-cases.json");
        var rows = mapper.readValue(Files.readString(file), List.class);
        for (Object value : rows) {
            var row = (Map<?, ?>)value;
            var actual = ImpactPolicy.decide(row.get("answers"), ((Number)row.get("threshold")).doubleValue());
            assertEquals(row.get("expected"), actual, (String)row.get("name"));
        }
    }
    @Test void nonFiniteAndInvalidThresholds() {
        for (double threshold : new double[]{Double.NaN, Double.POSITIVE_INFINITY, -.1, 1.1})
            assertThrows(IllegalArgumentException.class, () -> ImpactPolicy.decide(Map.of(), threshold));
        var answers = Map.of("impactEvidence", Map.of("type", "noul", "noul", Double.NaN));
        assertEquals("INVALID_JUDGMENTS", ImpactPolicy.decide(answers, .8).get("reason"));
    }
}
