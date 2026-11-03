# SDK integration lane

This separate provider-free lane builds the actual neighboring Sidecar checkout
against the developer-installed Framework `1.0.0-beta.9-SNAPSHOT`, locally installs
its Java SDK reactor, and packages both plain-Java and Spring Boot consumers.
It does not rebuild Framework. Business data, credentials and reference packs are
outside the SDK projects.

Prerequisites: Java 21 through `JAVA_HOME`, Maven and Docker on PATH, and the normal
suite Python environment including httpx, PyYAML and cryptography. Public dependency
and image downloads may occur; model providers remain inaccessible.

```powershell
.venv/Scripts/python.exe scripts/run_sdk.py local --sidecar-checkout C:/opendev/code/loomspan-sidecar --output evidence/sdk/NEW_LOCAL
.venv/Scripts/python.exe scripts/run_sdk.py standard --sidecar-checkout C:/opendev/code/loomspan-sidecar --output evidence/sdk/NEW_STANDARD
.venv/Scripts/python.exe scripts/run_sdk.py hardened --sidecar-checkout C:/opendev/code/loomspan-sidecar --output evidence/sdk/NEW_HARDENED
```

Each invocation requires a new output directory, runs root `clean verify`, SDK
`clean install`, consumer packaging and image construction, then its complete
bounded scenario inventory. Reports contain source/artifact identity, each stage's
status and elapsed time, scenario observations and cleanup results. A failed or
unrun scenario prevents acceptance. Reports omit credentials and raw business content.
Only the unique project and temporary fixture resources are cleaned up; the unique
built image remains available. Host provider credentials/Java options are not inherited.

## HTTP configuration and client behavior

Generated HTTP leaves use `executor: http` with operation-local `config`; named
targets live under `loomspan.executor-config.default.http.targets`. Owned SDK
callbacks use POST with no configured body, including the required-input expiry
leaf. Equipment-service callbacks separately use whole-input bodies. No separate
route catalog is loaded. Remote target data comes from the shipped execution YAML.

The plain-Java consumer checks qualified catalog descriptor names, exact completed
text, terminal `SKILL_FAILURE` text including `HTTP 503` and the complete response
body, submission, status and bounded waiting. A fixed proxy forwards one synthetic
effect submission, consumes the response and drops the connection. The SDK must
report acceptance unknown; independent counters require one submission/forward/effect
and no later activity. Clients never automatically resubmit or replay callbacks.
This is bounded no-replay evidence, not an exactly-once guarantee.

The foundation uses a temporary in-memory RSA signer and short-lived execution JWT.
Only public JWKS goes to Sidecar; the plain driver and disposable shutdown client
receive the token mount. The header uses a matching `kid` and
`typ=loomspan-execution+jwt`; claims include `token_use=loomspan_execution` and the
configured audience. Issuer is an identity claim, not a Sidecar issuer property.

Shutdown scenarios admit nested work, wait for fixture entry and send real TERM.
Completion observes callback detail/finish; cutoff withholds release and checks the
single three-second Framework budget, normal exit/no OOM and no later effects.
Required HTTP clients remain alive for admitted work until completion/cutoff.

## Local form login and callback authorization

Local uses the shipped colocated composition, localhost HTTP, an isolated internal
network, temporary configuration and tmpfs databases. It proves form login/CSRF,
exact role issuance, owner-only reads with fresh polling credentials, colocated
restart, current-file trust withdrawal/recovery and queued credential expiry.

Callback checks verify original token fidelity and identity, bodyless arrivals,
method authorization, record ownership and preservation of ordinary form/CSRF
security. The SDK authenticates callbacks; application method security and business
checks authorize actions. A required-message callback child provides an explicit
planner barrier for expiry-before-dispatch; arrival/body/effect counters remain zero.
Literal role names and `ROLE_` names are distinct; no role prefix mapping occurs.

## Standard HTTPS and Hardened Caddy mTLS

Standard uses direct Spring HTTPS with normal hostname/CA/expiry validation in both
directions. It covers positive invocation/callback, invocation wrong-CA rejection,
callback wrong-host and expired-server rejection, submission/callback response loss,
trusted-group signing rotation and outbound-only operation.
The fixture supplies its public CA in a Java PKCS12 truststore through standard
`javax.net.ssl.trustStore` JVM properties. The store contains no private key;
the executor has no SSL bundle or client-certificate configuration.

Hardened uses paired Caddy processes with app/Sidecar shared network namespaces,
loopback backends/outbound listeners, fixed proxy destinations and separate browser
ingress. Caddy owns mutual TLS. Cases cover positive flow, invocation/callback peer
rejections, external bypass isolation, response loss and outbound-only operation.
The HTTP executor does not manage client certificates.

The deployment transport baseline also checks direct HTTPS trust failures, Caddy
fixed-upstream/header policy, ingress/redirect origin and backend refusal. Temporary
certificates test integration, not issuance/renewal/reload/revocation lifecycle.

## Trusted groups and outbound-only clients

Apps sharing a Sidecar trust each other in every way: signing identity, issuer,
user directory, audience and exact role vocabulary. Use separate Sidecars for
isolation. Standard's second app tests same-issuer signing replacement with explicit
app restart and independently reloaded public trust files. No private-key hot reload,
uninterrupted rotation or replica coordination is claimed.

Outbound-only recipes retain one model skill and remove callback leaves/targets.
They use non-web application processes and verify invocation plus absent callback
listeners; Hardened additionally checks isolation/egress. These are representative
compositions, not a prohibition on untested network arrangements.
