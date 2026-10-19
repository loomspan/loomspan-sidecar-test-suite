package ai.loomspan.sdk.example;

import ai.loomspan.sdk.*;
import java.net.URI;
import java.nio.file.Path;
import java.time.Duration;
import java.util.List;

/** Disposable app-owned candidate signer; credential delivery stays on loopback. */
public final class RotationProbe {
    public static void main(String[] args) {
        var keys = SigningKeys.initialize(new SigningSettings("provided", null,
                new SigningSettings.Provided("PEM", Path.of("/replacement/signer-key.pem"), null,
                        null, null, Path.of("/replacement/signer.pem"), Path.of("/public/candidate.json"))));
        var issuer = new ExecutionTokenIssuer(keys, new IssuanceSettings("loomspan-app", Duration.ofMinutes(5),
                List.of(), List.of("ROLE_ORDER_EDITOR", "ORDER_EDITOR")));
        try (var capture = SidecarClient.builder().baseUrl(URI.create("http://127.0.0.1:8090/rotation/capture/candidate"))
                .responseTimeout(Duration.ofSeconds(3)).build()) {
            capture.listSkills(issuer.issue(new AuthenticatedIdentity("alice", List.of("ROLE_ORDER_EDITOR"))));
        }
    }
}
