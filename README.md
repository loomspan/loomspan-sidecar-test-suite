# Loomspan reference applications and acceptance suite

This project tests the same equipment-service business process through two real
Loomspan integrations: an embedded Java application and a Python/FastAPI application
using Loomspan Sidecar. Use deterministic replay to check Framework behavior,
live models to find compatibility and reasoning failures, and reviewed captures
to refresh the normal mock responses.

## Run the suite

Run the following PowerShell commands from the repository root in an initialized
workspace with Docker Compose services running and the Python virtual environment
installed. For initial setup, see the [operator runbook](docs/on-prem-runtime.md)
or [local development instructions](docs/local-run.md). Run one mode at a time;
the modes share runtime services and business records.

Modes 2–4 require `LOOMSPAN_OPENROUTER_API_KEY` in the process environment and make
real provider calls. Their default model is **Muse Spark Contributor**
(`meta/muse-spark-1.3-contributor`) with **medium** reasoning. In the examples,
replace `provider/model` with the exact OpenRouter model ID. Use `--reasoning none`
to omit the reasoning parameter; other accepted settings are `minimal`, `low`,
`medium`, `high`, and `xhigh`. The selected provider/model must support the setting.

### 1. Mock acceptance — Java and Sidecar

```powershell
.venv/Scripts/python.exe scripts/run_suite.py mock
```

Runs the complete deterministic acceptance suite against **both integrations**:
baseline assessment, changed operational priority, malformed-output recovery,
service creation/recovery, gated concurrent-case isolation, and nested authorization,
plus focused tests. Model stages use the active reviewed business fixtures and
static fault/authorization scripts through the real Framework provider client.
There are **zero live model calls**, and provider access must be disabled.
The suite also audits retained live evidence without contacting the provider.

Use this mode to check repeatable Framework and application behavior. Success means
all required scenario checks and assertions passed; unexpected requests or mismatched
replay stages fail rather than falling back to a live model.

### 2. Live workflows — Java and Sidecar

```powershell
# Default: Muse Spark Contributor, medium reasoning.
.venv/Scripts/python.exe scripts/run_suite.py live

# Choose another model and its reasoning setting.
.venv/Scripts/python.exe scripts/run_suite.py live --model provider/model --reasoning none
```

Runs baseline and changed-priority assessments through **both integrations**, with
every planner, assignment, child-model stage, and parent completion answered by the
selected live model. Checks cover evidence transfer, exact quotes, citations,
published results, identities, and Framework traces. A valid live baseline is then
used for service approval, direct permission denial, lost-result recovery,
idempotency, and expiry checks; those service operations need no additional model calls.

This is the live business-workflow track. Deliberately scripted malformed-output
and nested-authorization cases, and gated isolation, remain in mock mode. Live mode
does not replay mock answers to get a failing model through the workflow.

### 3. Model evaluation — one integration

```powershell
# Java is the default integration, with fewer transport layers to debug.
.venv/Scripts/python.exe scripts/run_suite.py evaluate --model provider/model --reasoning medium

# Choose Sidecar instead.
.venv/Scripts/python.exe scripts/run_suite.py evaluate --path sidecar --model provider/model --reasoning none
```

Runs the same live business scenarios as mode 2, but submits test executions only
to **Java or Sidecar**, selected with `--path java|sidecar`. Use this mode to explore
which models handle the example and inspect where they fail, without duplicating
the model workload across both integrations. Shared readiness and evidence
preservation still inspect the installed stack; the other integration need not
be removed or isolated.

### 4. Capture and refresh the normal mock responses

```powershell
.venv/Scripts/python.exe scripts/run_suite.py capture --model provider/model --reasoning medium
```

Runs the live scenarios on **both integrations** and retains the model responses
as potential sources for a new deterministic business fixture set. If automated
checks pass, the output directory includes `semantic-review-template.json`.
Capture alone **does not replace the active fixtures**.

Review the actual outputs for evidence fidelity, uncertainty, commercial terms,
feasible alternatives, and response to changed priority. Save a completed copy as
`semantic-review.json`, preserving its checksum bindings and recording a rationale
and `SUITABLE_FOR_REPLAY_CURATION` status for each suitable scenario/integration.
Then run the refresh phase, replacing `RUN` with the capture run's directory suffix
and choosing a new version name:

```powershell
.venv/Scripts/python.exe scripts/refresh_replay.py --suite evidence/capture-suite-RUN/report.json --semantic-review evidence/capture-suite-RUN/semantic-review.json --version model-name-v1
```

The refresh phase verifies the source and review, derives versioned normal business
responses, and runs the **complete mock suite** against that candidate. Only a
successful validation activates it. Previous versions remain available for rollback;
failed captures or candidates leave the active selection unchanged.

Static malformed-output and unauthorized-action scripts stay unchanged, including
the existing correction bundle's original business context. Where a normal live
stage needed correction, curation uses its final valid response and explicitly
records the earlier attempts omitted from normal replay. Original captures remain
intact. See the [detailed refresh and rollback procedure](docs/run-modes.md#replacing-business-fixtures).

### Results and runtime behavior

The runner prints the evidence/report location. Runs retain a Markdown summary,
JSON results, JUnit XML, request/response journals, business records, and actual
Framework traces. Live reports also record provider failures, malformed responses,
returned model IDs, and reported cost. A failed run returns a nonzero exit code;
inspect `$LASTEXITCODE` in PowerShell.

Live/evaluate/capture summaries separate suspected Framework defects, provider
errors, request timeouts, execution limits, exhausted model corrections, and
completed workflows that fail business checks. They show recovered retries and
corrections separately, with evidence links and a suggested next investigation.
Incomplete evidence leaves answer quality inconclusive. These categories guide
triage; they do not prove root cause or replace semantic review. To generate the
new diagnostic view of an old run without rerunning models or changing original
evidence, use [offline re-reporting](docs/run-modes.md#diagnostic-summary).

Live success is labeled `AUTOMATED_CHECKS_PASS`: semantic review is still required
before fixture refresh. Completion alone does not establish business correctness
or reliability across repeated runs. Live modes preserve runtime evidence, load
temporary model configuration, and restore normal configuration with provider
access disabled when they exit normally or handle an error. Existing databases
are preserved. For further details, see [run modes](docs/run-modes.md).

## Latest verification and historical checkpoints

**Model run modes verified (2026-10-03):**
The [final mock run](evidence/acceptance-offline-20261003-102249-5763db/summary.md)
passes 311 checks, 56 assertions and 110 focused tests. A new live Muse baseline
passes both paths; changed-priority runs expose a Sidecar step-action failure and
a Java citation-validation failure. Those captures remain unapproved for refresh.

**On-prem Compose installation verified (2026-10-02):** a separate project with
fresh credentials/databases passes **311 checks, 56 assertions and 96 focused
tests**, with zero paid calls. Follow the [operator runbook](docs/on-prem-runtime.md)
and [setup evidence](evidence/clean-compose-20261002/summary.md). A real fresh-start
database gap was fixed; the retained stack and original evidence remain unchanged.
This uses supplied local artifacts and host prerequisites; published assets follow
the user's planned releases. Java's stronger priority response remains inconclusive
and full delivery is not declared. Checkpoints below retain their historical scope.

This suite verifies capabilities of the system as a whole through two equivalent
applications and a complete business process. Scenarios and evidence establish
behavior under documented conditions.

**Current consolidated offline verification (2026-10-02):** all six paired scenario
groups pass **311 checks, 56 workflow assertions and 86 focused tests**, with no
failures or skips and zero paid calls, on the committed business configuration.
The [delivery audit](evidence/acceptance-offline-20261002-204252-34a71c/summary.md)
also revalidates the fresh live pair's 256 process checks and retained 16 assertions,
with content-bound semantic review. Genuine native live parent completion is
observed separately from controlled recovery replay's actual-child copying envelopes.
Java's stronger priority response remains inconclusive; Sidecar explicitly escalates.
Normal services are ready, provider access disabled, packages and prior evidence/
records preserved. Approved replay content is unchanged. First delivery remains
undeclared: clean-workspace setup is unverified; the
[next validation plan](docs/local-run.md#next-validation-clean-setup-in-a-separate-environment-not-yet-run)
uses a separate VM and leaves this workspace intact. Checkpoints below are historical.

**Fresh complete live workflows reviewed (2026-10-02):** baseline and continuity
priority complete through both applications using real Muse/medium at every model
stage, including native parent completion. The final matching pair passes 256
process checks, 16 workflow assertions and six focused tests. Complete source
evidence, original child results, authoritative quotes and comparison citations
survive through publication. Semantic review supports the business outcomes, with
Java's stronger response to continuity priority still inconclusive; Sidecar explicitly
escalates. Earlier failed attempts remain retained. Provider access is disabled,
all services ready and prior records preserved. See the
[complete review](evidence/review-fresh-live-20261002/summary.md).
No new replay approval or full-delivery declaration is implied. The offline counts
below remain the prior checkpoint, not a rerun after the prompt clarifications.

**Genuine malformed-output correction verified (2026-10-02):** both Muse corrections now pass
complete evidence, citation coverage and semantic review. Java retains every
decoded field; Sidecar changes only equivalent wording. Genuine corrected responses
are curated and approved after 42 offline checks and eight workflow assertions.
Consolidated recovery now uses those responses. Provider access is disabled again.
See [live-to-replay evidence](evidence/review-full-correction-live-20261002-171741/summary.md).

The [prior consolidated offline run](evidence/acceptance-offline-20261002-172357-b0ee31/summary.md)
passes **311 checks, 56 workflow assertions and 76 tests**, with no failures or skips.
The genuine correction-provenance gap is closed. Normal configuration and
provider-disabled runtime are restored; prior evidence and records remain intact.
Other delivery-audit qualifications remain explicit.

**Complete correction context verified offline (2026-10-02):** both applications now use the installed
Framework snapshot `900cc86` and send complete rejected responses in both schema
and step-action correction. All four actual candidates exceed the former 8192
limit and arrive exactly, including their malformed tails. Provider access remains
disabled. See [verification and artifacts](evidence/review-complete-correction-context-20261002/summary.md).
This resolves correction-context loss in the tested paths; genuine model citation
fidelity remains unverified on the new snapshot.

The [Consolidated offline process verification](evidence/acceptance-offline-20261002-153543-a71ccc/summary.md)
passes 310 checks, 56 workflow assertions and 73 focused tests with no failures or
skips. Normal configuration, provider-disabled runtime and prior durable evidence
are preserved. First delivery remains incomplete under the recorded audit.

**Latest correction result (2026-10-02):** scoped live corrections complete both
full workflows but remain rejected for citation fidelity. The revised prompt
preserves original child assessments exactly; Java drops comparison references
and Sidecar reorders them. Provider access is disabled, all evidence and durable
records retained, and no approved full-correction fixture exists. See
[review](evidence/review-full-correction-live-20261002-130627/summary.md) and
[status](docs/implementation-status.md). First delivery remains incomplete.

The subsequent [offline rerun](evidence/acceptance-offline-20261002-130917-a9bcef/summary.md)
passes all six groups: 310 checks, 56 workflow assertions and 69 focused tests,
with zero paid calls and normal provider-disabled runtime restored. See the
[next correction-context target](docs/correction-context-finding.md).

**Current checkpoint (2026-10-02):** one-command offline acceptance passes all six
scenario groups on both applications: 310 independent evidence checks, 56 workflow
assertions and 64 focused tests, with no failures or skips. Normal configuration is
restored; no paid calls. Original records and traces are retained. Run
`scripts/run_acceptance.py`; see the
[consolidated report](evidence/acceptance-offline-20261002-123044-813154/summary.md)
and [instructions](docs/local-run.md). Complete first delivery remains undeclared:
the full-workflow correction reuses original valid captured content; genuine model
correction captures remain isolated diagnostics. Setup verification uses this
retained snapshot workspace.

**Earlier checkpoint (2026-10-02):** full-workflow injected malformed-JSON recovery
passes on both applications (41 evidence checks/eight assertions). Gated read overlap
and two complete cases per application pass 100 checks/16 assertions;50 focused
offline tests pass. Maya's baseline blocks while Luis's priority case completes,
then resumes with its own results, quotes and identity. No paid calls or service
commitments. See [status](docs/implementation-status.md),
[recovery](evidence/review-full-workflow-recovery-20261002-121334/summary.md) and
[isolation](evidence/review-gated-isolation-20261002-121509/summary.md).
Complete first-delivery acceptance has not been declared.

**Earlier checkpoint (2026-10-02):** valid-approval nested authorization passes on
both applications: 32 evidence checks, eight assessment assertions and46 focused
offline tests. Maya cannot invoke creation; Luis reaches the same real restricted
leaf once and its matching durable receipt survives both parent completions.
No paid calls. Normal configuration restored; first delivery remains incomplete.
See [status](docs/implementation-status.md) and [review](evidence/review-nested-authorization-offline-20261002-115456/summary.md).

**Earlier checkpoint (2026-10-02):** approved service-request creation/recovery
passes on Java and Sidecar: 53 evidence checks, eight assessment assertions and
44 focused offline tests. Exact quote/scope/USD-cent approval creates one durable
request; denial, conflicting retry and new creation at expiry cannot add requests.
A lost completed-result response is recovered at expiry without duplication.
No paid calls or creation model calls. First delivery remains incomplete; see
[status](docs/implementation-status.md) and [review](evidence/review-service-requests-offline-20261002-114412/summary.md).

**Earlier checkpoint (2026-10-02):** versioned reviewed Muse fixtures now pass
baseline and continuity-priority offline workflows through both applications.
Each pair passes 34 evidence checks and eight workflow assertions; 39 focused
offline tests pass. Approved scope is deterministic assessment replay only.
Provider access is disabled; zero paid calls in this phase. Exact quotes, USD cents,
asset/approval context and original assessments are preserved. First delivery remains
incomplete; see [status](docs/implementation-status.md) and [approval record](fixtures/replay/business-reviewed-v1-approval.json).

**Earlier checkpoint (2026-10-02):** the five business-output fixes and follow-up
assessment-preservation refinements are verified. Thirty-four focused offline tests
pass; both real comparison corrections pass 28 evidence checks. Reviewed Muse/medium
baseline and priority outputs are suitable sources for replay curation on each path,
with distinct captured configuration provenance. The latest Java priority passes
31 mechanical checks and four scoped assertions. No shared replay or first-delivery
acceptance is approved. Provider access is enabled under the user's Muse authorization.
See [status](docs/implementation-status.md) and
[latest review](evidence/review-live-20261002-102148/summary.md).
Next: curate versioned strict offline replay from the reviewed sources, then verify
remaining accepted scenarios. Historical rejected captures remain regression evidence.

**Earlier deployed offline verification (2026-10-02):** both full diagnostic workflows
complete on the revised Java/Sidecar configuration. All 32 evidence checks pass,
including actual selection-schema rejection/correction, parent preservation and
zero service commitments. Thirty focused offline tests pass. Responses are captured
or explicitly authored; no new Muse judgment or replay approval. Provider access is
disabled in the fixture. See [review](evidence/review-business-workflow-offline-20261002-075008/summary.md).

**Earlier offline-only checkpoint (2026-10-02):** revised decision prompts, shared
option-name schemas and both publication guards; 27 offline pytest checks and
10 Java local publication checks pass. Java compiles offline on the installed
snapshot. Explicitly hand-edited Muse-derived examples remain unapproved; originals,
journals and traces are preserved. No paid calls or deployment in this phase.
See [status](docs/implementation-status.md) and
[offline evidence](evidence/business-output-offline-20261002/summary.md).

**Earlier Muse verification (2026-10-02):** both paths complete with Muse/medium on
the installed Framework snapshot. Eight workflow assertions and 53 mechanical checks
pass. Java exercises ordinary schema recovery. A subsequent
[isolated injected-fault diagnostic](evidence/review-controlled-step-live-20261002-004937/summary.md)
demonstrates invalid step-action recovery on both paths. Business wording findings
keep the full-workflow captures unapproved for replay.
See [review](evidence/review-live-20261002-000544/summary.md).

**Implementation authorized on 2026-10-01; first delivery remains incomplete.** Both
paths build and run with the user-authorized Framework beta.8-SNAPSHOT. The latest
full Muse pair completed on both paths; semantic review keeps the bundle unapproved.
See [implementation status](docs/implementation-status.md) and
[local build/run instructions](docs/local-run.md). Historical planning and
compatibility text below is not acceptance evidence.

This project will demonstrate and verify customer-facing Loomspan capabilities through two REST-only reference microservices implementing the same business workflow:

- An embedded Java application using Loomspan as a Maven dependency and deterministic operations exposed as `@SkillMethod` skills.
- A Python/FastAPI application integrating with Loomspan Sidecar and exposing equivalent operations as REST skills.

Shared scenarios will exercise complex skill trees, concurrent executions, failure handling, and configuration changes under load using deterministic dummy LLM and downstream services.

The shared acceptance runner is Python/pytest, initially running on Windows and exercising both applications through HTTP with independently authored expectations. Docker Compose runs the Java application, Python application, pinned Sidecar, Keycloak and Python/FastAPI fixture services. Fixtures run separately from the applications and runner, supplying scripted external responses, gates and independent request journals.

The dummy model serves non-streaming OpenAI Chat Completions at `/v1/chat/completions` through the real Framework provider client in both paths. Scripts are execution-specific, match stages/attempts and required evidence, and use separate harness controls for registration, gates and journals.

Each run will retain an evidence directory containing its manifest, independent fixture journals and business records, logs, Framework-generated trace files from both integration paths, and linked Markdown/machine-readable results. Supported Framework NDJSON collection is implemented and has produced actual trace files on both paths.

First delivery includes optional real-model execution for both applications. During the build, all prompts/model responsibilities will be exercised in complete real-model workflows; reviewed captures will seed versioned replay scripts with provenance and explicitly labeled fault mutations. Ordinary acceptance runs use those scripts without live-provider calls. The initial real-model baseline is OpenRouter `openai/gpt-6.1-sol` with `medium` reasoning for both versions. No project-level spending budget is required for this small test. The provider key is supplied through `LOOMSPAN_OPENROUTER_API_KEY`. Live compatibility and partial workflow captures exist; none is approved as a complete replay baseline.

Both applications will trust a local Keycloak instance for normal demonstrations and acceptance tests. Java will use Spring Security, and Python will use FastAPI security dependencies with PyJWT. Explicit role and token-audience contracts will govern authorization across application and skill boundaries; controlled token fixtures will support specialized negative tests.

Maya and Luis obtain access tokens using Authorization Code with PKCE through Keycloak's login page: a browser login helper supports manual demonstrations, and Playwright automates seeded-user login for acceptance tests against both versions.

Both versions use the accepted `ASSESS_EQUIPMENT` and `REQUEST_SERVICE` permissions in a top-level Keycloak `roles` array and shared logical resource audience `equipment-service`. Java and Sidecar map roles with the `ROLE_` authority prefix; Python checks unprefixed names. Site assignments and spending limits remain authoritative application records. Java propagates the verified caller in its security context; Python/Sidecar passes through the caller's access token. Keycloak 26.3.5 provisioning and PKCE login are implemented; broader authorization acceptance remains outstanding.

**Current stage: implementation and compatibility verification, first delivery incomplete.** The [implementation handoff](docs/implementation-handoff.md) still defines the delivery boundary. Reviewed full-workflow replay and acceptance must not be claimed from the passing compatibility checks.

Independent fixture/capture-review checks and controlled nested-denial diagnostics pass; both denial paths retain actual Framework traces. These handcrafted, incomplete-approval diagnostics do not replace valid-approval authorization acceptance or reviewed real-model replay. The subsequent local snapshot test is explicitly authorized; it does not require a new published release. See [status](docs/implementation-status.md) and [opt-in diagnostic instructions](docs/local-run.md).

**Active local test baseline:** Framework `1.0.0-beta.8-SNAPSHOT`, source reference `900cc86bc2ba619d38647688008b138a07108af6`, installed SHA256 `57824a5ffa711b5eef0a5d35b4af95820efdc2a1741bb62354ea33e8286610ef`, with identical Framework bytes packaged in both hosts. Sidecar uses beta.2 source (`da3bb8f8ae6087955f9b3a6bd02b9706d3b582e7`) with that dependency override. This is not the published Sidecar binary. Earlier snapshot and released beta.7/beta.2 build checks and evidence remain preserved.

## Start here

Read [Project agreement and conversation handoff](docs/project-agreement.md) before continuing design or implementation. It records the agreed direction, recommendations that remain open, and the next decisions.

For the next coding context, read the [implementation handoff](docs/implementation-handoff.md), which consolidates the baseline, recommended build sequence, completion criteria and starter prompt. Implementation is already authorized; resume from its current-state section rather than rebuilding the foundations.

Read [Equipment service resolution](docs/equipment-service-resolution.md) for the selected business problem, illustrative request, and model versus deterministic responsibilities.

For the accepted domain details and retained design history, read the [working design](docs/equipment-service-design-draft.md) and [fictional source pack](docs/equipment-service-source-pack.md). These describe the people, manual, warranty/service terms, repair history, skill tree, scenario portfolio, and business contracts. Apply the agreement’s accepted decisions; historical open/proposed wording does not reopen settled choices.

The initial customer-facing claims are maintained in:

- [Loomspan Framework claims](docs/loomspan-framework-claims.md)
- [Loomspan Sidecar claims](docs/loomspan-sidecar-claims.md)

These are claims to demonstrate, not completed verification results.

## Related projects

- [Loomspan Framework](https://github.com/loomspan/loomspan-framework), normally checked out beside this repository as `../loomspan-framework`.
- [Loomspan Sidecar](https://github.com/loomspan/loomspan-sidecar), normally checked out beside this repository as `../loomspan-sidecar`.

The current development environment is Windows with PowerShell and Docker. Local execution comes first; GitHub Actions follows later.
