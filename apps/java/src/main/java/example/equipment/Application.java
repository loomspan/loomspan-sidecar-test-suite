package example.equipment;

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

@SpringBootApplication
@EnableMethodSecurity(jsr250Enabled = true)
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }

    @Bean
    JwtDecoder decoder(@Value("${equipment.issuer}") String issuer, @Value("${equipment.jwks}") String jwks) {
        var d = NimbusJwtDecoder.withJwkSetUri(jwks).build();
        OAuth2TokenValidator<Jwt> audience = j -> j.getAudience().contains("equipment-service")
                && j.getSubject() != null && !j.getSubject().isBlank()
                        ? OAuth2TokenValidatorResult.success()
                        : OAuth2TokenValidatorResult.failure(new OAuth2Error("invalid_token"));
        d.setJwtValidator(
                new DelegatingOAuth2TokenValidator<>(JwtValidators.createDefaultWithIssuer(issuer), audience));
        return d;
    }

    @Bean
    SecurityFilterChain security(HttpSecurity http) throws Exception {
        var roles = new JwtGrantedAuthoritiesConverter();
        roles.setAuthoritiesClaimName("roles");
        roles.setAuthorityPrefix("ROLE_");
        var converter = new JwtAuthenticationConverter();
        converter.setJwtGrantedAuthoritiesConverter(roles);
        return http.csrf(c -> c.disable()).authorizeHttpRequests(a -> a
                .requestMatchers("/health", "/_loomspan/observability/v1/**").permitAll().anyRequest().authenticated())
                .oauth2ResourceServer(o -> o.jwt(j -> j.jwtAuthenticationConverter(converter))).build();
    }
}

@RestController
class ExecutionApi {
    private final SkillTemplate skills;
    private final Business business;
    private final ConcurrentMap<String, Map<String, Object>> executions = new ConcurrentHashMap<>();
    private final ExecutorService workers = Executors.newVirtualThreadPerTaskExecutor();

    ExecutionApi(SkillTemplate skills, Business business) {
        this.skills = skills;
        this.business = business;
    }

    @GetMapping("/health")
    Map<String, String> health() {
        return Map.of("status", "up");
    }

    @PostMapping("/v1/skills/{skill}/executions")
    @ResponseStatus(HttpStatus.ACCEPTED)
    Map<String, Object> submit(@PathVariable String skill, @RequestBody Map<String, Object> input) {
        skills.validate(skill, input);
        var auth = SecurityContextHolder.getContext().getAuthentication();
        var id = UUID.randomUUID().toString();
        var state = new ConcurrentHashMap<String, Object>();
        state.put("id", id);
        state.put("owner", auth.getName());
        state.put("status", "RUNNING");
        executions.put(id, state);
        workers.submit(() -> {
            var context = SecurityContextHolder.createEmptyContext();
            context.setAuthentication(auth);
            SecurityContextHolder.setContext(context);
            try {
                var result = skills.invoke(skill, input, v -> state.put("sessionId", v.sessionId()));
                if (skill.equals("resolveEquipment"))
                    state.put("assessmentVersion", business.saveAssessment(id, result));
                if (skill.equals("createServiceRequest")
                        && !"PENDING_DISPATCH".equals(business.read(result).get("status")))
                    throw new IllegalStateException("Creation did not return a durable receipt");
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
    Map<String, Object> poll(@PathVariable String id) {
        var s = executions.get(id);
        if (s == null || !s.get("owner").equals(SecurityContextHolder.getContext().getAuthentication().getName()))
            throw new ResponseStatusException(HttpStatus.NOT_FOUND);
        return Map.copyOf(s);
    }

    @PostMapping("/assessments")
    @ResponseStatus(HttpStatus.ACCEPTED)
    Map<String, Object> assess(@RequestBody Map<String, Object> input) {
        business.scoped((String) input.get("assetId"));
        return submit("resolveEquipment", input);
    }

    @GetMapping("/assessments/{id}")
    Map<String, Object> assessment(@PathVariable String id) {
        return poll(id);
    }

    @PostMapping("/service-requests")
    @ResponseStatus(HttpStatus.ACCEPTED)
    Map<String, Object> commit(@RequestBody Map<String, Object> approval) {
        return submit("createServiceRequest", Map.of("approval", approval));
    }

    @GetMapping("/service-requests/by-key/{key}")
    Map<String, Object> recover(@PathVariable String key) throws Exception {
        return business.recover(key);
    }
}

@RestControllerAdvice
class InputErrors {
    @ExceptionHandler(ai.loomspan.api.SkillInputValidationException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    Map<String, String> invalid() {
        return Map.of("kind", "INPUT_VALIDATION");
    }
}
