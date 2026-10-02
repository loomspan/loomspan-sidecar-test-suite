# First-delivery implementation handoff

**Latest full Muse baseline (2026-10-01):** `meta/muse-spark-1.3-contributor`, medium reasoning, ran once on each path after offline fixes and successful access checks. Java failed on malformed step-action JSON after correction; Sidecar published its assessment with unchanged quotes and correct monetary units but has semantic wording findings. Focused assertions: 6 passed / 2 failed. Both Framework traces are retained. The capture remains unapproved for replay. See `evidence/review-live-20261001-220102/summary.md` and implementation status.

Updated 2026-10-01 after beta.7 / Sidecar beta.2 verification. Implementation is authorized and underway. Both applications, partial real-model captures and actual Framework traces exist; first-delivery acceptance remains incomplete. Resume the existing implementation, preserving its evidence.

Latest authorization: the user installed Framework beta.8-SNAPSHOT and authorized both local hosts to consume it, with a supported 240-second provider request timeout. Sidecar is rebuilt from unchanged beta.2 source. Use `compose.snapshot.yaml`, the active `.runtime/build-baseline.json`, and the latest status section. The release-only restriction and beta.7 timeout blocker below are historical for this explicitly authorized snapshot test.

Historical Sol result: after the first snapshot run reached the separate 600-second mission deadline, the mission budget was increased to 1,200 seconds. Both Framework workflows now complete and final-synthesis evidence checks pass. Sidecar publishes its assessment; Java rejects the model's two extra non-authoritative quote objects. Latest capture `evidence/live-20261001-205953` reports 9 passed / 1 failed and remains unapproved for replay. Resume with the quote/output-contract and source-context review described in status, not another timeout-release search. Preserve the exact captures and both Framework traces. Changed-priority, correction, reviewed replay and remaining business acceptance are still outstanding.

## Prior offline/access checkpoint (before the full Muse run)

Quote-contract, authoritative asset/approval context and USD-cent fixes are implemented
and pass focused offline checks on both paths. Existing captured comparisons are reused
only in an explicitly unapproved schema-correction diagnostic with original Sol
provenance. No new full live workflow has run. After the user changed account settings, both small Muse/medium probes pass
with HTTP 200 and successful Framework traces in `evidence/compatibility-20261001-215426`.
The earlier age-confirmation and privacy-policy failures remain preserved as history. See the newest status section for
exact evidence, retained traces and the remaining semantic/full-workflow gaps.

## Read first and source precedence

Read `AGENTS.md`, [README](../README.md) and [project agreement](project-agreement.md), then the [domain overview](equipment-service-resolution.md), [working design](equipment-service-design-draft.md), [source pack](equipment-service-source-pack.md) and both [Framework](loomspan-framework-claims.md) / [Sidecar](loomspan-sidecar-claims.md) claims documents.

The user's current request and accepted decisions govern. The agreement preserves decision history; later accepted decisions supersede earlier open/proposed wording. The working design supplies details, but unaccepted proposals are not requirements. This handoff is an implementation guide, not a new product specification. Keep claims, validation targets and observed results distinct.

## Resume here: current state and remaining work

Read [implementation status](implementation-status.md) for observed results, exact evidence paths and the current blocker, and [local run](local-run.md) for commands. Do not repeat historical compatibility discovery or interpret the build sequence below as a request to start over.

- Both paths build/run with Framework beta.7 and Sidecar beta.2. Their packaged Framework JARs match Maven Central. Keycloak, PKCE, SQLite persistence, four model responsibilities, deterministic skills, fixture controls and trace collection are implemented.
- Full sibling records reach the dependent planner in both paths; all five required source markers reached the assessment child in the first beta.7 capture. Final synthesis is still unverified.
- Six deterministic compatibility checks and one focused proxy transport test passed. Full live captures remain rejected as replay baselines. The first beta.7 evidence run reports 4 passed / 4 failed; the response-relay retry reports 3 passed / 5 failed, with the differences explained in status.
- Current blocker: the OpenAI-compatible provider client times out at 60 seconds despite a 600-second mission timeout. Response relaying did not remove the limit. No supported connection timeout override was found in beta.7. Verify any user-supplied fix/release before retrying; do not guess a property, change model/reasoning, patch Framework internals or repeatedly rerun an unchanged blocked setup.
- Resume verification still found only released beta.7 / beta.2 remotely. Independent work added request/response correlation, strict fixture matcher tests, read-only `inspect_capture.py`, and opt-in controlled nested denial diagnostics that passed on both paths with real traces. These handcrafted/incomplete-approval diagnostics are not approved replay or the required valid-approval positive-control pair. See status and local-run for exact scope and commands. Normal business configuration was restored afterward.

Continue in this order, doing independent implementation work while an external fix is pending:

1. Verify an available supported timeout solution and its release identities, following any new user release instruction. If none is available, report the exact dependency blocker and continue work that does not require successful live capture.
2. Complete real baseline and changed-priority workflows on both paths, including nested comparison and final synthesis. Review evidence and authoritative quotes against independent expectations; correct actual implementation/prompt defects without weakening acceptance.
3. Capture real malformed-output correction feedback/responses. Derive versioned deterministic scripts only from suitable reviewed captures, recording normalization and intentional fault mutations. Existing fixture replay scaffolding is not accepted provenance.
4. Complete shared acceptance: base assessment; Luis approval/creation/idempotency and recovery after response loss/quote expiry; otherwise-valid Maya direct denial; controlled nested denial and Luis positive control; gated overlap and two-case isolation.
5. Retain per-run manifests, independent journals/business records, logs, JUnit/results and actual Framework traces from both paths. Finish reproducible local live/replay instructions and report precisely what passed, failed or remains blocked.

Workspace continuity: implementation files are currently uncommitted/untracked; preserve them. `.runtime`, `.build`, `.venv` and generated `evidence` directories are ignored local state and will not follow a Git-only handoff. Use this same workspace for a fresh context. Never copy `.runtime/secrets.json` into reports. The provider credential is in `LOOMSPAN_OPENROUTER_API_KEY`; do not print it. The stack was last left healthy/running, but verify readiness on resume. Fixture registrations are in memory and reset on fixture restart; use fresh case IDs. `scripts/review_capture.py` is a historical beta.6 rejection review, not a generic approval tool for new captures.

## Fixed baseline

The user authorized these released versions on 2026-10-01. Historical pins remain only in decision history and old evidence.

| Area | Accepted choice |
| --- | --- |
| Applications | Two equivalent REST-only microservices: embedded Java with `@SkillMethod` operations; Python/FastAPI calling real Sidecar with equivalent REST skills |
| Releases | Framework `1.0.0-beta.7` (`0778065ef5bafc9c8ea979093e5e0e48d7e1e687`) in both paths; Sidecar `v1.0.0-beta.2` (`da3bb8f8ae6087955f9b3a6bd02b9706d3b582e7`); no implicit snapshots |
| Environment | Docker Compose for both applications, Sidecar, Keycloak and fixture services; Python/pytest runner initially on Windows |
| Identity | Keycloak; Authorization Code with PKCE; manual browser login helper and Playwright test-user login; separate user sessions |
| Permissions | Top-level `roles`: Maya has `ASSESS_EQUIPMENT`; Luis also has `REQUEST_SERVICE`. Java/Sidecar use `ROLE_` authorities; Python checks unprefixed names |
| Audience and limits | Shared `equipment-service` resource audience; independently verified tokens at each receiving API; site grants and Luis's $1,000 ceiling in authoritative application records |
| Propagation | Java retains verified security context; FastAPI/Sidecar forward the caller token to REST skills. Luis commits under his own identity. Management credentials are separate |
| Fixtures | Separate Python/FastAPI services; non-streaming Chat Completions at `/v1/chat/completions`; real Framework provider clients; separate control/journal endpoints |
| Scripts | Execution-specific state, stage/attempt and evidence matching, dependency checks, order-independent parallel branches, visible rejection of unexpected/ambiguous requests |
| Real model | OpenRouter `openai/gpt-6.1-sol`, `medium`, for all model responsibilities in both paths; optional live mode and required live capture/review during the build |
| Cost | No project-level spending budget or budget machinery for this small scoped test; retain ordinary usage/cost evidence |
| Evidence | One directory per run, including successes: manifest, independent journals/gates/business records, logs, Framework-generated trace files from both paths, linked Markdown summary, machine-readable results and JUnit XML |

Both versions remain required throughout. Compare equivalent business outcomes and evidence, not identical physical traces or model-call counts. Do not share application memory with the runner or calculate expected answers using the business function under test.

## Delivery boundary

Maya requests an asynchronous assessment of the recurring carton-sealer fault. Four substantive model responsibilities coordinate evidence, assess equipment, develop options and perform nested comparison. Independent deterministic reads overlap. Comparison owns the recommendation; native planner synthesis is allowed and must preserve its selection, constraints and authoritative quotes.

Submission returns an execution ID; polling separates execution status from business disposition. Successful results have immutable assessment versions. Updated information starts a new assessment.

Luis explicitly approves a selected option and creates its service request in one authenticated, deterministic submission through the restricted Loomspan skill. Bind assessment version, option, quote, attendance, repair scope, cap and idempotency key. Atomically persist approval and request. Same key/content returns the original receipt; changed content conflicts. Authorized lookup recovers after response loss, including after quote expiry when creation succeeded in time.

The action ends at durable `PENDING_DISPATCH`. Dispatch, technician findings and changed offers remain fixtures. No dispatch lifecycle, custom business frontend, broader fictional product, additional warranty system or expanded scenario portfolio is needed.

## Delivery sequence and requirements (partly implemented)

### 1. Verify integration and establish the smallest running paths

Inspect supported contracts at the selected release tags, reading related repositories' guidance. Choose and record exact dependency/image versions, including Keycloak; lock artifacts and capture build identities. Do not silently use neighboring development HEADs.

Establish both application skeletons and Compose environment, Keycloak realm/client/role mapping, PKCE login and caller propagation. Use real public Framework and Sidecar interfaces. Verify one model-backed execution and restricted deterministic creation under authorized/unauthorized identities. Java commitment uses public `SkillTemplate`; Python submits the equivalent REST skill to Sidecar.

Enable Framework trace generation and collect actual trace files from both paths into a run directory. Verify supported export/collection, correlation and credential redaction. Logs or runner-generated timelines are not substitutes.

Check the OpenRouter model path, medium reasoning, output validation and any native tool fields actually emitted. Provider documentation differs on this model's native Chat Completions tool support; test the real path rather than assume compatibility. Resolve supported configuration issues; report genuine release-contract blockers instead of replacing Framework internals, weakening assertions or changing baselines silently.

This milestone establishes compatibility, not completion of the delivery. Keep useful smoke checks as regressions where appropriate.

### 2. Implement the shared business workflow and fixtures

Translate the accepted source pack into small versioned fixtures and independently authored expected values. Preserve the controlled business clock separately from real token time. Keep evaluator interpretations out of model-visible sources.

Implement the four model contracts and coherent deterministic capabilities in both versions. Parallel group A: history, reference evidence and service terms after asset scope is known. Equipment assessment waits for relevant history/guidance. Parallel group B: entitlement, service-resource and continuity checks once their respective inputs exist. Quotes wait for applicable checks; comparison waits for checked options and quotes.

Implement assessment/results and approval-bound creation/recovery. Preserve conditional item-level coverage, $780 scoped maximum exposure, the conditional $300 covered-scope endpoint, the 11:00 continuity decision and access/restoration uncertainty. Neither quote endpoint is an unconditional invoice or restoration promise.

Build fixture script registration, stage/evidence matching, gates and independent journals. Correlation identifiers must travel through supported mechanisms and never confer authority. Temporary scaffolding scripts may aid development; delivered acceptance scripts must have the reviewed real-model provenance described next.

### 3. Capture real-model behavior and derive replay scripts

Exercise all prompts/model responsibilities in complete workflows through both applications, including native final synthesis. Capture requests, responses, usage and Framework traces. Use the same sources/contracts for a small baseline and changed-priority comparison.

Review responses against independent expectations. Correct prompts or implementation when necessary; do not redefine correctness to match a model's mistake. Convert suitable captures into versioned replay scripts, retaining provenance and normalizing execution-specific identifiers. Distinguish original captures, normalization and intentional mutations.

For malformed-output correction, mutate a captured content response while retaining a valid provider envelope, then capture the real model's response to actual correction feedback. Ordinary acceptance runs replay reviewed scripts without live-provider calls; generation/refresh and live demonstration are explicit modes.

Use configured credentials supplied outside source control and evidence. If access is unavailable, continue unaffected work and report capture/live verification as incomplete; never manufacture real-model provenance.

### 4. Complete shared acceptance and evidence

| Scenario | Required evidence/outcome |
| --- | --- |
| Base assessment | Required evidence reaches dependent stages; scripted expedited recommendation and authoritative constraints survive parent completion; no business commitment |
| Luis creation/recovery | One durable matching `PENDING_DISPATCH` record with verified approval and approved scope/cap; no commitment model call; same-content retry/recovery returns the original receipt |
| Malformed output | Invalid content triggers correction feedback; corrected response succeeds; invalid output is never published as successful assessment |
| Direct authorization denial | Otherwise valid Maya creation reaches the public Loomspan boundary and is denied with zero durable requests; application-only rejection is insufficient; Sidecar may reject before admission |
| Controlled nested denial | Separately labeled configuration has accessible parent and nested planner plus real restricted leaf; Maya's available capabilities omit creation; scripted unavailable-child proposal is rejected/unsatisfiable with no creation invocation or record; Sidecar has no creation-endpoint request |
| Nested positive control | Same controlled configuration under Luis with valid explicit approval exposes and reaches creation, ruling out broken registration |
| Overlap/isolation | Two eligible reads enter before either gate releases; another distinct case completes while the first is blocked; after release each retains its own evidence, quotes and identity |

Retain independent observations alongside traces for every assertion. Exact terminal errors must follow the release contracts. Document integration-specific differences, including forwarded-token expiry. Missing required evidence is a finding, not a passing result.

Provide reproducible local setup, run, capture/refresh, live-demo and evidence-inspection instructions. Keep passing and failing evidence attributable to versions/configuration and redact credentials. Report assertion failures, environment failures and skips separately.

## Implementation discretion and completion

The major design decisions are settled. Exact route/schema names, storage choice, idempotency key scope/retention, pinned Keycloak version, dependency locks, TLS/client/redirect provisioning, supported trace configuration, script correlation and reasonable test timeouts remain concrete engineering work. Recommend and document proportionate choices within the accepted contracts; these do not need a new broad planning round. Escalate actual incompatibilities or changes to agreed scope.

First delivery is complete when both applications execute the accepted workflow and variations, recovery semantics are verified, reviewed real-model-derived scripts drive ordinary offline acceptance, optional live mode works, and run evidence includes Framework trace files from both versions. Clearly disclose anything not run or blocked.

Publication under load, fifty-execution experiments, restart, overload, shutdown, broader Sidecar management tests, polished HTML reporting and GitHub Actions remain later work. No first-delivery result establishes those broader claims.

## Suggested prompt for the fresh context

> Continue the authorized first delivery in this existing workspace. Read AGENTS.md, README.md and docs/project-agreement.md first, then docs/implementation-handoff.md, docs/implementation-status.md, docs/local-run.md and the linked design/source/claims documents. Resume the implementation; preserve uncommitted files and local evidence. Framework beta.7 / Sidecar beta.2 are installed, dependent-evidence checks pass on both paths, and full live completion is blocked by a separate 60-second provider request timeout. First verify whether a supported timeout fix is available under my latest release instructions; otherwise report the concrete blocker and continue independent work. Do not repeat unchanged blocked live runs or replace Framework internals. Continue through reviewed complete real-model captures, deterministic replay and all first-delivery acceptance scenarios for both embedded Java and Python/FastAPI + Sidecar, including actual Framework-generated trace files. LOOMSPAN_OPENROUTER_API_KEY supplies the provider credential; never print it. Make and document routine engineering choices without reopening settled decisions. Keep observed results separate from claims; do not approve incomplete captures or claim unexecuted checks passed.
