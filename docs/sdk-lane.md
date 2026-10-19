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
`local-ownership`, `local-restart`, `local-trust-recovery`, `local-queue-expiry`,
`local-callback-authorization` and `local-callback-expiry`.
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
These are deployment baselines, not full Standard/Hardened SDK recipes. The separate
Local group exercises SDK Spring callback authentication. The separate remote
recipes below add bidirectional transport and provided-signing evidence;
trusted-group rotation remains a separate obligation.

`standard` runs positive form/SDK invocation and authenticated callback, invocation
wrong-CA server rejection, callback wrong-host and expired-server rejection, and
post-effect submission/callback response-loss scenarios. `hardened` runs the
same positive/no-replay obligations through two Caddy mTLS gateways, wrong-CA
clients and servers in both directions, and actual outsider no-bypass/fixed-
destination probes. Each command retains the full mandatory build path above.
See the neighboring Sidecar `docs/remote-recipes.md` and `examples/remote` for
the actual supplied Boot/Caddy fragments consumed by these compositions.

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
No TLS recipe completion is claimed by this Local group.


Previous Local evidence (before callback scenarios): [report 20261018T222714Z-48aad3a2b736](../evidence/sdk/20261018T222714Z-48aad3a2b736/report.json)
passes all ten scenarios, builds and cleanup in 518.105s. Root components:
61 classes / 261 tests, zero failures/errors/skips; focused harness: 66 passed;
full safe Python suite: 176 passed. Ruff/diff checks and independent exact-label
resource/external-key-volume absence checks passed. The report records both source
revisions/dirty state, Sidecar/SDK/plain-Java/Boot hashes and shipped sample hash.
The initial [failed report](../evidence/sdk/20261018T221808Z-eef7285741cc/report.json)
retains its Local readiness failure and not-run outcomes; the initial fixture's
unsupported connection key was replaced with beta.8 `request-timeout` before the
fresh complete run. No operational/reference data reset or provider call occurred.


## Callback authentication and application authorization

The reference app enables Spring method security and implements the fixed
`POST /loomspan/callbacks/owned` route within the SDK's default callback prefix.
The SDK authenticates execution JWTs independently of browser sessions; the app
uses `hasRole('ORDER_EDITOR')` and an Alice-owned record check to authorize the
operation. Its ordinary form-login chain and CSRF remain independent. Counters
are exposed only through authenticated `/callback-counts`, outside the callback
prefix; the arrival filter runs before security, while body and effect counters
separate method denial from record denial.

`local-callback-authorization` submits an admitted REST leaf with Sidecar
`caller-passthrough` to this fixed loopback route. Alice's verified issuer,
subject and exact `ROLE_ORDER_EDITOR` authority return with the callback result.
A scoped SDK capture client sends the same opaque submission credential to the
in-memory fixture first. The callback compares its verified JWT against that
captured credential through a fixed fixture endpoint; only the equality boolean
leaves the fixture. The literal `ORDER_EDITOR` user is deliberately admitted by a
separate skill but fails the callback's method role check. Bob has the role and
reaches the body, then fails ownership. Both failures retain HTTP 403 and produce
no effect. A subsequent form submission verifies ordinary CSRF and login behavior.

`local-callback-expiry` uses a distinct two-second credential and a deterministic
planning model barrier. The probe observes barrier entry and RUNNING before
holding past expiry, using fresh credentials for status reads. Release emits the
real planning protocol's fixed `CALL_TOOL` action for `localExpiryOwned`. The leaf requires a message input, so Framework cannot bypass the step-model action
using its zero-input dispatch optimization. The required
child failure propagates to the parent as exact `execution credential expired`;
the terminal failure plus all three unchanged counters and a bounded quiet interval
prove the sender made no callback request. This differs from queue expiry, whose
exact failure remains `execution credential expired before start`. No canned final
model response can turn the callback-expiry scenario into a success.

Both new scenarios have strict boolean/counter result schemas and independent
report stages; missing, false, wrongly typed or extra observations fail the run.
The focused harness verifies fixed routing, credential comparison, planner barrier
release/deadline, cleanup on scenario failure and report redaction. Detailed invalid
JWT/header permutations and trust reload belong to the starter component tests.
This implementation adds no provider calls, business-runtime changes or data reset.
The [current complete report 20261018T232143Z-36a99814fb53](../evidence/sdk/20261018T232143Z-36a99814fb53/report.json)
passes all 12 scenarios and every build/runtime/cleanup stage in 538.779s.
Root components: 61 classes / 261 tests; SDK: 25 core and 30 starter tests, all
zero failures/errors/skips. Both real consumers packaged. Final focused harness:
79 passed; full safe Python suite: 189 passed. Ruff/diff checks and independent
resource-absence checks passed. The report records actual artifact/sample hashes.

The [first callback attempt](../evidence/sdk/20261018T230730Z-15907b2c1449/report.json)
passed all builds and callback authorization but failed expiry's extra CALL_TOOL
oracle: beta.8 auto-dispatched the zero-input leaf. A dedicated required-message
leaf now forces that step-model action; targeted callbacks/expiry and cleanup,
then the complete final run passed. Both formal runs cleaned their unique projects
and external key volumes. The earlier ten-scenario report does not establish
callback behavior. This historical Local evidence does not establish remote
recipe behavior. Full rotation remains separate work.

## Remote recipe evidence and limits

Both compositions use SDK provided RSA signing. Only the reference app receives
the signing private key; its public JWKS export is checked against the supplied
signer and delivered read-only to Sidecar's exact file trust path. Certificates
and keys are newly generated per isolated startup variant under a temporary
directory and removed after scoped cleanup. No CA service, provider call or
certificate lifecycle procedure runs.

Standard positive traffic is direct Spring HTTPS in both directions with normal
chain/hostname verification. Its invalid callback-server variants necessarily
affect the same Spring browser listener: the isolated Python control driver pins
the exact supplied bad certificate solely to perform form login. Actual Java
callers always retain normal verification, and typed independent probes classify
the expected CA/SAN/expiry error. This driver treatment is absent from the valid
recipe and operator configuration.

Hardened app and Sidecar each share only their own Caddy namespace. HTTP backend,
outbound and fixture listeners bind loopback; an outsider checks refusal at each
namespace address. Browser ingress is server TLS on 8444 and rejects callback
paths; callback ingress on 8443 requires group client certificates. Caddy verifies
client CA/EKU membership rather than client DNS SANs. Outbound upstreams/server
names are literal and zero retry is explicit. Absolute-form/Host probes cannot
select the local effect fixture.

Loss instruments forward one fixed operation once, consume the accepted response
after receiver effect, then close the connection. Standard fault variants use
trusted TLS and verify the actual Spring receiver. Hardened fault variants sit
on receiver-local HTTP behind the real mTLS ingress. These instruments are test
fixtures, not operator gateways. Independent attempt/forward/acceptance/effect
counts must be one after a five-second quiet interval exceeding the three-second
Java response deadline. Direct loss is acceptance unknown; Caddy's HTTP 502 is
recorded as an HTTP failure. Callback loss remains a failed execution after its
one effect. No client/proxy automatically replays the operation.

The first complete Standard attempt,
[20261019T014109Z-545d2153ac89](../evidence/sdk/20261019T014109Z-545d2153ac89/report.json),
passed every build but failed app startup because the fixture overlaid provided
mode onto packaged Local colocated configuration. The app correctly rejected the
conflicting settings. Remote fixture configuration now replaces that Local
configuration source. Its failed report and successful scoped cleanup are retained.
Complete remote reports follow.

The complete [Hardened report 20261019T014927Z-b5ab2b9224e2](../evidence/sdk/20261019T014927Z-b5ab2b9224e2/report.json)
passed all eight scenarios and their startup/cleanup stages in 927.972s. Root,
SDK, both real consumers and checkout image builds passed. All eight exact
project-label container/network/volume listings were empty after cleanup.
The report records Sidecar source `e2aad75c40f4e6b524853a170c60d3c672a0a11c`,
suite source `61007447077a6907569876a289aa2601a00afa0e` (both dirty, uncommitted
ticket work), and Sidecar JAR SHA-256
`f9b563a60e8f0aec3211f1a28b98957c50e717dfc4342bbbaf23321b8ccbbbbd`.
SDK and consumer hashes are in that exact report. These are bounded composition
results, not certificate-lifecycle or arbitrary customer network guarantees.

The complete [Standard report 20261019T015656Z-c2445d463665](../evidence/sdk/20261019T015656Z-c2445d463665/report.json)
passed all six scenarios and their startup/cleanup stages in 777.899s, including
both post-effect loss cases. Every mandatory build passed, and all six exact
project-label container/network/volume listings were empty after cleanup.
Its Sidecar JAR SHA-256 is
`d18069e2a8f4ae7f46ff55e9cbe4001d616ee309e1bb9a25eb26db2bc3b9c462`;
source revisions are the same dirty ticket-working checkouts recorded above.
SDK/consumer artifact hashes and exact typed scenario observations are preserved
in each report. Standard's direct lost submission reports acceptance unknown;
Hardened's lost submission reports actual HTTP 502. Both callbacks remain failed
after their single observed effect, with no replay during the quiet interval.

Final verification: 103 focused SDK harness tests and 213 broad safe Python
tests passed; Ruff formatting/lint and both repository diff checks passed.
The actual final root build reports 61 classes / 261 tests, SDK core 25 and
starter 30, with zero failures/errors/skips. No production Sidecar/SDK TLS wiring
change was necessary. No tracked/untracked certificate or key file was added;
the failed and passing reports contain no PEM, bearer credential or JWT values.
No provider call, business runtime change, data reset, commit or release occurred.
