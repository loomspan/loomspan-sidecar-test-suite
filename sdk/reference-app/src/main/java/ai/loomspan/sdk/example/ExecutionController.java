package ai.loomspan.sdk.example;

import ai.loomspan.sdk.*;
import ai.loomspan.sdk.spring.SpringExecutionTokenIssuer;
import java.net.URI;
import java.time.Duration;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import org.springframework.http.ResponseEntity;
import org.springframework.security.web.csrf.CsrfToken;
import org.springframework.web.bind.annotation.*;
import tools.jackson.databind.json.JsonMapper;

/** Fixed fixture operations; identity and authorities always come from Spring Security. */
@RestController
public class ExecutionController {
    private final SidecarClient client;
    private final SpringExecutionTokenIssuer issuer;
    private final SpringExecutionTokenIssuer shortIssuer;
    private final JsonMapper json = JsonMapper.builder().build();

    ExecutionController(SidecarClient client, SpringExecutionTokenIssuer issuer, SigningKeySource keys) {
        this.client = client;
        this.issuer = issuer;
        shortIssuer = new SpringExecutionTokenIssuer(new ExecutionTokenIssuer(keys,
                new IssuanceSettings("loomspan-app", Duration.ofSeconds(2), List.of(),
                        List.of("ROLE_ORDER_EDITOR", "ORDER_EDITOR"))));
    }
    @GetMapping("/csrf") Map<String, String> csrf(CsrfToken token) {
        return Map.of("token", token.getToken(), "header", token.getHeaderName());
    }
    @GetMapping("/skills") Map<String, Boolean> skills() {
        client.listSkills(issuer.issueCurrent());
        return Map.of("accepted", true);
    }
    @PostMapping("/capture") Map<String, Boolean> capture() {
        // Scoped SDK transport to one fixed capture route; opaque credentials stay opaque.
        try (var capture = SidecarClient.builder().baseUrl(URI.create("http://127.0.0.1:8090/capture"))
                .responseTimeout(Duration.ofSeconds(3)).build()) {
            capture.listSkills(issuer.issueCurrent());
        }
        return Map.of("captured", true);
    }
    @PostMapping("/submit/{skill}") Map<String, String> submit(@PathVariable String skill) {
        if (!Set.of("localModel", "localBlocker", "localEffect", "localOwned", "localLiteralOwned", "localCallbackPlanner").contains(skill))
            throw new IllegalArgumentException("Unknown fixture skill");
        var credential = (Set.of("localEffect", "localCallbackPlanner").contains(skill) ? shortIssuer : issuer).issueCurrent();
        if (Set.of("localOwned", "localLiteralOwned", "localCallbackPlanner").contains(skill)) {
            try (var capture = SidecarClient.builder().baseUrl(URI.create("http://127.0.0.1:8090/capture"))
                    .responseTimeout(Duration.ofSeconds(3)).build()) {
                capture.listSkills(credential);
            }
        }
        return Map.of("id", client.submit(skill, json.createObjectNode(), credential).id().toString());
    }
    @GetMapping("/executions/{id}") Map<String, Object> execution(@PathVariable UUID id) {
        var snapshot = client.getExecution(id, issuer.issueCurrent());
        return Map.of("status", snapshot.status().name(), "result", snapshot.result() == null ? "" : snapshot.result(),
                "failure", snapshot.failure() == null || snapshot.failure().message() == null ? "" : snapshot.failure().message());
    }
    @ExceptionHandler(HttpFailureException.class) ResponseEntity<Void> sidecarFailure(HttpFailureException failure) {
        return ResponseEntity.status(failure.status()).build();
    }
    @ExceptionHandler(Exception.class) ResponseEntity<Void> fixtureFailure(Exception failure) {
        return ResponseEntity.internalServerError().build();
    }
}
