package example.suites.typesafeai.api;

import example.infrastructure.execution.ExecutionApi;
import example.suites.typesafeai.policy.ImpactPolicy;
import tools.jackson.databind.json.JsonMapper;
import java.util.LinkedHashMap;
import java.util.Map;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

/** The application requests judgments; it does not route tickets or perform customer actions. */
@RestController
@RequestMapping("/suites/typesafe-ai")
public class TypeSafeApi {
    private final ExecutionApi executions;
    public TypeSafeApi(ExecutionApi executions) { this.executions = executions; }

    @PostMapping("/evaluations/{skill}")
    @ResponseStatus(HttpStatus.ACCEPTED)
    public Map<String, Object> evaluate(@PathVariable String skill, @RequestBody Map<String, Object> input) {
        if (!skill.startsWith("tsTriage")) throw new ResponseStatusException(HttpStatus.NOT_FOUND);
        return executions.submit(skill, input);
    }

    @GetMapping("/executions/{id}")
    public Map<String, Object> result(@PathVariable String id) { return executions.poll(id); }

    @GetMapping("/executions/{id}/impact")
    public Map<String, Object> impact(@PathVariable String id,
            @RequestParam(defaultValue = "0.80") String evidenceThreshold) {
        // Owner authorization precedes any access to the retained result.
        var execution = executions.poll(id);
        if (!ImpactPolicy.SKILLS.contains(execution.get("skillName")))
            throw new ResponseStatusException(HttpStatus.NOT_FOUND);
        double threshold;
        try {
            threshold = Double.parseDouble(evidenceThreshold);
            if (!Double.isFinite(threshold) || threshold < 0 || threshold > 1) throw new IllegalArgumentException();
        } catch (IllegalArgumentException e) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Invalid evidenceThreshold");
        }
        var view = new LinkedHashMap<String, Object>(execution);
        if ("COMPLETED".equals(execution.get("status"))) {
            Object answers;
            try { answers = JsonMapper.builder().build().readValue((String)execution.get("result"), Object.class); }
            catch (Exception e) { answers = null; }
            view.put("impactDecision", ImpactPolicy.decide(answers, threshold));
        }
        return view;
    }
}
