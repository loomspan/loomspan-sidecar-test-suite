package ai.loomspan.sdk.example;

import ai.loomspan.sdk.*;
import java.net.URI;
import java.net.http.*;
import java.time.Duration;
import java.util.List;
import org.springframework.boot.ApplicationRunner;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.ConfigurableApplicationContext;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import tools.jackson.databind.json.JsonMapper;

/** Non-web fixture process: export signer, await listener checks, submit exactly once, exit. */
@Configuration
@ConditionalOnProperty(name = "fixture.outbound-only", havingValue = "true")
public class OutboundOnlyRunner {
    private final HttpClient http = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(2)).build();
    private String fixed(String path, boolean post) throws Exception {
        var request = HttpRequest.newBuilder(URI.create("http://127.0.0.1:8090/outbound/" + path)).timeout(Duration.ofSeconds(3));
        if (post) request.POST(HttpRequest.BodyPublishers.noBody());
        var response = http.send(request.build(), HttpResponse.BodyHandlers.ofString());
        if (response.statusCode() != 200) throw new IllegalStateException("Fixture unavailable");
        return response.body();
    }
    @Bean ApplicationRunner outbound(SidecarClient client, ExecutionTokenIssuer issuer, ConfigurableApplicationContext context) {
        return args -> {
            long deadline = System.nanoTime() + Duration.ofSeconds(150).toNanos();
            while (true) {
                try { fixed("ready", true); break; }
                catch (Exception failure) {
                    if (System.nanoTime() >= deadline) throw new IllegalStateException("Fixture readiness deadline");
                    Thread.sleep(100);
                }
            }
            while (!fixed("status", false).contains("\"go\": true")) {
                if (System.nanoTime() >= deadline) throw new IllegalStateException("Invocation release deadline");
                Thread.sleep(100);
            }
            var identity = new AuthenticatedIdentity("alice", List.of("ROLE_ORDER_EDITOR"));
            client.listSkills(issuer.issue(identity));
            var id = client.submit("localModel", JsonMapper.builder().build().createObjectNode(), issuer.issue(identity)).id();
            while (true) {
                var result = client.getExecution(id, issuer.issue(identity));
                if (result.status().name().equals("COMPLETED")) {
                    if (!"fixture result".equals(result.result())) throw new IllegalStateException("Unexpected model result");
                    break;
                }
                if (result.status().name().equals("FAILED") || System.nanoTime() >= deadline)
                    throw new IllegalStateException("Execution did not complete");
                Thread.sleep(100);
            }
            fixed("completed", true);
            http.close();
            context.close();
        };
    }
}
