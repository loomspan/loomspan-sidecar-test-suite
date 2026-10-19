package ai.loomspan.sdk.example;

import jakarta.servlet.Filter;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;
import org.springframework.boot.web.servlet.FilterRegistrationBean;
import org.springframework.context.annotation.Bean;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationToken;
import org.springframework.web.bind.annotation.*;

/** Application-owned role and record checks, independent of SDK authentication. */
@RestController
@org.springframework.boot.autoconfigure.condition.ConditionalOnWebApplication(type = org.springframework.boot.autoconfigure.condition.ConditionalOnWebApplication.Type.SERVLET)
public class CallbackController {
    private final AtomicInteger arrivals = new AtomicInteger();
    private final AtomicInteger bodies = new AtomicInteger();
    private final AtomicInteger effects = new AtomicInteger();
    private final HttpClient http = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(2)).build();

    @Bean FilterRegistrationBean<Filter> callbackArrivals() {
        Filter filter = (request, response, chain) -> {
            arrivals.incrementAndGet();
            chain.doFilter(request, response);
        };
        var registration = new FilterRegistrationBean<>(filter);
        registration.addUrlPatterns("/loomspan/callbacks/*");
        registration.setOrder(Integer.MIN_VALUE);
        return registration;
    }

    @GetMapping("/callback-counts") Map<String, Integer> counts() {
        return Map.of("arrivals", arrivals.get(), "bodies", bodies.get(), "effects", effects.get());
    }

    @PostMapping("/loomspan/callbacks/owned")
    @PreAuthorize("hasRole('ORDER_EDITOR')")
    ResponseEntity<Map<String, Object>> owned(JwtAuthenticationToken identity) throws Exception {
        bodies.incrementAndGet();
        if (!"loomspan-app".equals(identity.getToken().getClaimAsString("iss"))
                || !"alice".equals(identity.getToken().getSubject()))
            return ResponseEntity.status(403).build();
        var comparison = http.send(HttpRequest.newBuilder(URI.create("http://127.0.0.1:8090/compare"))
                .timeout(Duration.ofSeconds(3)).header("Authorization", "Bearer " + identity.getToken().getTokenValue())
                .GET().build(), HttpResponse.BodyHandlers.ofString());
        if (comparison.statusCode() != 200 || !comparison.body().equals("{\"equal\": true}"))
            throw new IllegalStateException("Credential comparison failed");
        effects.incrementAndGet();
        return ResponseEntity.ok(Map.of("issuer", identity.getToken().getClaimAsString("iss"), "subject", identity.getToken().getSubject(),
                "roles", identity.getAuthorities().stream().map(authority -> authority.getAuthority()).sorted().toList(),
                "credentialEqual", true));
    }
}
