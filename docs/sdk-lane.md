# SDK integration lane

This separate lane builds the actual neighboring Sidecar checkout with its pinned
Framework beta.8 dependency and locally installs its Java SDK reactor. It does
not rebuild Framework. The retained embedded beta.9 and beta.3-source
Python/Sidecar business lanes keep their existing commands, configuration and data.

Prerequisites: Java 21 through `JAVA_HOME`, Maven and Docker on PATH, the normal
suite Python environment (including httpx, PyYAML and cryptography), and a
resolvable/installed Framework `1.0.0-beta.8`. Public Maven downloads and container
image pulls may occur. Provider credentials are unnecessary.

From this suite checkout:

```powershell
.venv/Scripts/python.exe scripts/run_sdk.py local
.venv/Scripts/python.exe scripts/run_sdk.py local --sidecar-checkout C:/opendev/code/loomspan-sidecar
.venv/Scripts/python.exe scripts/run_sdk.py standard
.venv/Scripts/python.exe scripts/run_sdk.py hardened
```

`local` selects `foundation-smoke`, `blocking-client`, `shutdown-completion`,
`shutdown-cutoff`, `deployment-transport-baseline`, `local-issuance-roles`,
`local-ownership`, `local-restart`, `local-trust-recovery` and `local-queue-expiry`.
It runs root `clean verify`
(including tests), SDK `clean install`, packages the plain Java driver with its
runtime dependencies, packages `sdk/reference-app` against the locally installed
SDK Spring Boot starter, and builds the actual checkout's Dockerfile. Its baseline
two-service Compose project uses an internal network, temporary file configuration
and tmpfs database, and a deterministic OpenAI/REST fixture. Only the fixed lost-response proxy forwards a
submission, to one Sidecar path; model requests never reach a provider.
Readiness requires exactly `{"status":"UP"}` on application port 8080 over
container-local HTTP using the image's curl; neither
service publishes host ports. A Java 21 driver joins that network for invocation.
No business state or existing credentials are mounted.
Host provider/Java option variables
are not passed to child tools or containers.

Smoke requires readiness `UP`, zero model requests before driver invocation, a normal
Sidecar stop with exit 0 or 143, and Spring's graceful-shutdown completion marker. It tears down
only its unique Compose project. The locally built Docker image remains available
under its unique `loomspan-sdk-smoke:sdk-...` tag; there are no persistent SDK
containers, networks or databases.

The plain Java consumer has only `loomspan-sdk-core` as a direct runtime dependency.
It exercises discovery, submission, status and bounded waiting against the real
Sidecar. It checks a COMPLETED model execution preserves the exact `fixture result`
string and a FAILED REST execution preserves `SKILL_FAILURE` and its HTTP 503 message.
A reference proxy forwards one synthetic-effect submission to a fixed Sidecar path,
consumes its response and drops the client connection. The SDK must report acceptance
unknown. Independent synchronized counters must show one incoming submission, one
forward, one synthetic effect and no additional activity after the driver exits.
This is bounded no-replay evidence, not a production exactly-once guarantee.

The runner generates a short-lived execution JWT using an in-memory temporary RSA
key. Only public JWT verification material goes in Sidecar configuration. The driver
has the only resident-service token mount; shutdown admission uses a disposable
client with the same read-only mount. Tokens never appear on command lines or in
the Sidecar/resident-fixture mounts. This fixture
uses `loomspan-sidecar.trust.mode=file`, a public-only RSA JWKS at
`trust.file.jwks`, and `auth.jwt.audience`. Its header has a matching `kid` and
`typ=loomspan-execution+jwt`; claims include `token_use=loomspan_execution`. The
issuer is an identity claim, not a Sidecar issuer configuration property. No private
JWT key or retired PEM/issuer setting is persisted.

The shutdown baselines generate temporary planner/REST files, admit nested work,
wait for fixture entry, then send real TERM. Completion releases work and observes
detail/finish effects. Cutoff withholds release and checks the single 3s Framework
budget, normal exit/no OOM and absence of later effects.

The transport baseline uses separate per-run valid/expired direct Spring HTTPS
servers, verified positive readiness, wrong-CA/hostname/expired rejections, and
supplied Caddy with the shipped fixed-upstream/header policy. A separate namespace
client checks ingress, redirect origin, normalized headers and backend refusal. It
does not test certificate persistence, issuance, replacement, renewal or reload.
These are deployment baselines, not full Standard/Hardened SDK recipes or SDK Spring
callback authentication. Later tickets retain callback authorization,
bidirectional TLS/mTLS, provided signing and trusted-group rotation obligations.

`standard` and `hardened` are recognized but currently have no scenarios. They
exit nonzero with `no-scenarios-for-recipe` and write explicit failed evidence.
Future tickets implement those recipe scenarios.

Every valid invocation creates `evidence/sdk/<unique-run-id>/report.json`. Use
`--output NEW_DIRECTORY` to select a different new destination; existing directories
are refused. Reports include recipe/scenarios, Git revision and dirty state,
packaged Sidecar SHA-256, Framework version read from the packaged JAR, SDK
coordinates/hashes, both consumer JAR hashes, suite source revision/dirty state,
shipped sample hash, each build/runtime stage with elapsed seconds and total duration, explicit passed
scenario results, readiness,
driver outcome booleans, independent request/effect counters, graceful exit and cleanup.
Unavailable identities remain null. A dirty revision is identified by its build
hashes as well as HEAD; HEAD alone does not describe uncommitted build inputs.

Reports are initialized before preflight and atomically finalized after success,
failure or interruption. Failed commands expose fixed diagnostic categories,
never raw output, exceptions, container logs, credentials, private keys or payloads.
The temporary execution-JWT signing private key is never serialized. If normal
shutdown fails, successful cleanup does not turn the smoke into a pass. Cleanup
failure also fails the run and preserves any primary failure.

Local harness checks:

```powershell
.venv/Scripts/python.exe -m pytest tests/test_sdk_runner.py -q
ruff format --check scripts/run_sdk.py scripts/sdk_lane tests/test_sdk_runner.py
ruff check scripts/run_sdk.py scripts/sdk_lane tests/test_sdk_runner.py
```

No development-data reset is required. Maintained fixture/reference packs and
the existing five-service runtime are outside this composition.

The Sidecar root component build still runs once per SDK invocation. The suite never
invokes Sidecar's deployment smoke; Sidecar build/CI never invokes this suite. See
`../loomspan-sidecar/docs/verification.md` for the ownership inventory and current
evidence. A run rebuilds the actual checkout; there is no cached-artifact bypass.


Current deployment-ownership evidence: [Local report
20261018T211932Z-43ccfbc20a42](../evidence/sdk/20261018T211932Z-43ccfbc20a42/report.json)
passes all five scenarios and cleanup. Total 453.482s includes the root component
build (306.614s), SDK reactor (29.542s) and driver (6.308s). TERM process exits were
2.420s for completion and 3.912s for cutoff, both normal with expected effects.
The [Sidecar ownership inventory](../../loomspan-sidecar/docs/verification.md)
accounts for retired duplicate checks and distinguishes historical costs, failed
attempts and future full-recipe obligations.


## Local form-login and colocated integration

The Local app scenario group derives Compose from the supplied Sidecar checkout's
`examples/quickstart/compose.yaml`; evidence records its hash. It retains Sidecar's
loopback/colocated environment, UID 10001 and read-only public-key mount. The clean
Java app and deterministic fixture share Sidecar's namespace, with no host ports and
an internal network. The harness prepares one unique external key volume at UID
10001/mode 0700 before startup. App startup depends on Sidecar being started, because
the app must export JWKS before trust becomes ready. Test substitutions replace the
Python host, omit ingress/operational/mail placeholders, and supply temporary file-mode
skills, local models, one worker and tmpfs database. No business configuration is mounted.

Real Spring form login and CSRF establish Alice/Bob's exact `ROLE_ORDER_EDITOR`
authority and the negative user's `ORDER_EDITOR`. Fixed controller operations call
the SDK directly over loopback, issue a fresh credential per request, and propagate
only Sidecar HTTP statuses on failure. Assertions cover completion, exact-role 403
without dispatch, different-subject 404 and fresh-owner polling. A separately scoped
SDK capture client sends one credential to a fixed discovery fixture; its value stays
in fixture memory and can only be probed against the fixed Sidecar catalog path.

App-only restart changes the public kid and proves old-credential 401/new acceptance.
A disposable operator retains only public JWKS in memory, injects empty trust, observes
status-only readiness 503/authentication 401, atomically restores the file and observes
both recover. A model barrier holds the single worker while a two-second SDK credential
is observed QUEUED; fresh authenticated polls do not extend it. After release, the exact
`execution credential expired before start` failure and a separate zero effect counter
prove non-dispatch, including a quiet observation after recovery. All waits are bounded.
Cleanup attempts project teardown and explicit removal of its external key volume.
No callback authorization or TLS recipe completion is claimed by this Local group.


Current complete Local evidence: [report 20261018T222714Z-48aad3a2b736](../evidence/sdk/20261018T222714Z-48aad3a2b736/report.json)
passes all ten scenarios, builds and cleanup in 518.105s. Root components:
61 classes / 261 tests, zero failures/errors/skips; focused harness: 66 passed;
full safe Python suite: 176 passed. Ruff/diff checks and independent exact-label
resource/external-key-volume absence checks passed. The report records both source
revisions/dirty state, Sidecar/SDK/plain-Java/Boot hashes and shipped sample hash.
The initial [failed report](../evidence/sdk/20261018T221808Z-eef7285741cc/report.json)
retains its Local readiness failure and not-run outcomes; the initial fixture's
unsupported connection key was replaced with beta.8 `request-timeout` before the
fresh complete run. No operational/reference data reset or provider call occurred.
