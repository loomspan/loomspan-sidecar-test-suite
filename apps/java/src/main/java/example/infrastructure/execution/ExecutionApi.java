package example.infrastructure.execution;
import ai.loomspan.api.SkillTemplate;
import java.util.*;
import java.util.concurrent.*;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.http.HttpStatus;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.oauth2.core.*;
import org.springframework.security.oauth2.jwt.*;
import org.springframework.security.oauth2.server.resource.authentication.*;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

@RestController
public class ExecutionApi {
    private final SkillTemplate skills;
    private final List<CompletionHandler> handlers;
    private final ConcurrentMap<String, Map<String, Object>> executions = new ConcurrentHashMap<>();
    private final ExecutorService workers = Executors.newVirtualThreadPerTaskExecutor();

    ExecutionApi(SkillTemplate skills, List<CompletionHandler> handlers) {
        this.skills = skills;
        this.handlers = handlers;
    }

    @GetMapping("/health")
    Map<String, String> health() {
        return Map.of("status", "up");
    }

    @PostMapping("/v1/skills/{skill}/executions")
    @ResponseStatus(HttpStatus.ACCEPTED)
    public Map<String, Object> submit(@PathVariable String skill, @RequestBody Map<String, Object> input) {
        skills.validate(skill, input);
        var auth = SecurityContextHolder.getContext().getAuthentication();
        var id = UUID.randomUUID().toString();
        var state = new ConcurrentHashMap<String, Object>();
        state.put("id", id);
        state.put("skillName", skill);
        state.put("owner", auth.getName());
        state.put("status", "RUNNING");
        executions.put(id, state);
        workers.submit(() -> {
            var context = SecurityContextHolder.createEmptyContext();
            context.setAuthentication(auth);
            SecurityContextHolder.setContext(context);
            try {
                var result = skills.invoke(skill, input, v -> state.put("sessionId", v.sessionId()));
                for (var handler : handlers)
                    if (handler.supports(skill)) handler.complete(skill, id, result, state);
                state.put("result", result);
                state.put("status", "COMPLETED");
            } catch (Exception e) {
                state.put("error",
                        Map.of("kind",
                                e instanceof org.springframework.security.access.AccessDeniedException ? "ACCESS_DENIED"
                                        : "SKILL_FAILURE",
                                "type", e.getClass().getSimpleName()));
                state.put("status", "FAILED");
            } finally {
                SecurityContextHolder.clearContext();
            }
        });
        return Map.of("id", id);
    }

    @GetMapping("/v1/executions/{id}")
    public Map<String, Object> poll(@PathVariable String id) {
        var s = executions.get(id);
        if (s == null || !s.get("owner").equals(SecurityContextHolder.getContext().getAuthentication().getName()))
            throw new ResponseStatusException(HttpStatus.NOT_FOUND);
        return Map.copyOf(s);
    }

}
