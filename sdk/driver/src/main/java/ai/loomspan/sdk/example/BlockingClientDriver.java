package ai.loomspan.sdk.example;

import ai.loomspan.sdk.*;
import java.net.URI;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import tools.jackson.databind.ObjectMapper;

/** Plain consumer: only SDK core and its runtime transitives are on the classpath. */
public final class BlockingClientDriver {
    public static void main(String[] args) {
        try {
            run(args);
        } catch (Exception | AssertionError failure) {
            // No raw exception, token, business payload, server message or stack trace.
            System.err.println("SDK composed driver failed");
            System.exit(1);
        }
    }

    private static void run(String[] args) throws Exception {
        var credential = CredentialSnapshot.of(Files.readString(Path.of(args[0])).strip());
        var mapper = new ObjectMapper();
        var input = mapper.createObjectNode();
        var options = new WaitOptions(Duration.ofSeconds(30), Duration.ofMillis(100));
        try (var client = SidecarClient.builder().baseUrl(URI.create("http://sidecar:8080")).build()) {
            require(client.listSkills(credential).stream().anyMatch(skill -> skill.name().equals("default-sdkSmoke")));
            require(client.getSkill("sdkSmoke", credential).name().equals("default-sdkSmoke"));
            var accepted = client.submit("sdkSmoke", input, credential);
            var complete = client.await(accepted.id(), credential, options);
            require(complete.status() == ExecutionStatus.COMPLETED);
            require("fixture result".equals(complete.result()));
            require(client.getExecution(accepted.id(), credential).id().equals(accepted.id()));
            var failedId = client.submit("sdkFailure", input, credential).id();
            var failed = client.await(failedId, credential, options);
            require(failed.status() == ExecutionStatus.FAILED);
            require(failed.failure() != null && "SKILL_FAILURE".equals(failed.failure().kind()));
            require("HTTP 503\n{\"error\": \"fixed SDK fixture failure\"}".equals(failed.failure().message()));
        }
        boolean unknown = false;
        try (var proxy = SidecarClient.builder().baseUrl(URI.create("http://fixtures:8081")).build()) {
            try {
                proxy.submit("sdkEffect", input, credential);
            } catch (AcceptanceUnknownException expected) {
                require(expected.executionId() == null);
                unknown = true;
            }
        }
        require(unknown);
        System.out.println("{\"completed\":true,\"opaqueResultPreserved\":true,\"failed\":true,\"primaryFailurePreserved\":true,\"acceptanceUnknown\":true}");
    }

    private static void require(boolean condition) {
        if (!condition) throw new AssertionError("SDK composed assertion failed");
    }
}
