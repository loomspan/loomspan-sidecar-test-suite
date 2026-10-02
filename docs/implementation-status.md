# Implementation and observed status — 2026-10-01

**Latest full Muse baseline (2026-10-01):** `meta/muse-spark-1.3-contributor`, medium reasoning, ran once on each path after offline fixes and successful access checks. Java failed on malformed step-action JSON after correction; Sidecar published its assessment with unchanged quotes and correct monetary units but has semantic wording findings. Focused assertions: 6 passed / 2 failed. Both Framework traces are retained. The capture remains unapproved for replay. See `evidence/review-live-20261001-220102/summary.md` and implementation status.

Implementation is authorized by the user's current request. **First delivery is incomplete.** The active local test uses user-authorized Framework beta.8-SNAPSHOT in embedded Java and unchanged Sidecar beta.2 source. Workflow, permissions, provider and evidence requirements remain unchanged.

## First full Muse baseline after offline fixes — 2026-10-01

Follow-up [JSON failure investigation](muse-json-failure-review.md) verified the exact
provider strings against Framework trace content and reproduced rejection using the
packaged codec/type offline. Muse emitted extra closing braces, but Framework step-action
recovery supplies only generic feedback without the failed candidate or parser details.
The application also asks the model to copy large context into a deterministic lookup
that only uses IDs. Prioritize recovery/contract improvements before attributing the
failure to general model capability. No paid calls or runtime changes were made for
this investigation; a causal prompt A/B remains unperformed.

The user authorized one new baseline workflow per path. Both ran concurrently with
separate cases on the existing snapshot stack. [Full review and evidence](../evidence/review-live-20261001-220102/summary.md)
record **Java FAILED / Sidecar COMPLETED**, with **6 passing / 2 failing** focused
capture assertions. All 32 provider calls returned HTTP 200 with Muse/medium verified
in the actual requests; there was no access or timeout failure. Java used 14 calls
and 364.43 seconds; Sidecar used 18 calls and 827.52 seconds. Both original Framework
traces and independent journals/records are retained, and original capture hashes
were verified unchanged. No second full run was made.

Java exhausted two attempts to produce valid step-action JSON for the first nested
resolution entitlement task. Its earlier root planner also omitted bulletin serial
range metadata from equipment-assessment arguments despite receiving it in full.
The model output then described bulletin eligibility and some supplied asset facts
as unknown. No Java assessment or service request was persisted. This is observed
model output/evidence behavior, not evidence of Framework truncation or a general
integration-path difference.

Sidecar completed all model responsibilities and native synthesis, persisted one
immutable assessment, preserved exactly the two authoritative service quotes, and
correctly expressed cent amounts as USD dollar prose. Full asset and approval
context reaches comparison. Parent synthesis preserves comparison unchanged; no
service commitment exists. However, nextDecision contradicts S-5 by suggesting
approval alone preserves prices/the loaner offer, acceptedRisk ambiguously says risk
is accepted pending approval, and the discussion incompletely addresses the two-hour
recoverable delay and possible expedited work beyond site hours. This mechanical
success is not approved semantic judgment.

A spontaneous real malformed-output correction succeeded for Sidecar's equipment
assessment; its original invalid response, actual feedback and corrected response
are preserved for reviewed reuse. It is not yet the controlled mutation scenario.
The two-path capture remains **REJECTED_FOR_REPLAY**. Next work should use these
responses for offline reliability/source-preservation/wording diagnostics before
another paid run. Changed-priority and remaining business acceptance are outstanding.

## Muse access verified after account-setting change — 2026-10-01

The user reported changing the account setting and requested another Muse check.
The [small compatibility recheck](../evidence/compatibility-20261001-215426/manifest.json)
passed on both embedded Java and Python/Sidecar. Each path made exactly one provider
request, received HTTP 200 and the expected structured COMPATIBLE result. The actual
requests specify `meta/muse-spark-1.3-contributor` with medium reasoning. Both actual
Framework traces report success and are retained with hashes, provider journals,
configuration, running artifact identities and independent records.

The previously observed age/privacy access blockers are no longer present in this
check. This verifies small-call access and structured-output compatibility only.
No full live workflow was run; the semantic, full-workflow, changed-priority and real
correction-response evidence gaps below remain. Existing captures stay unapproved.

## Offline contract fixes and access recheck — 2026-10-01

The two reference paths now expose `assetContext`, a scoped deterministic read of
ASSET-017, serial/model/revision, SITE-WEST, AUTH-NB and named routing contacts.
Root planning requires that read before the three parallel evidence reads and
instructs propagation through equipment assessment and nested comparison. Manual
and bulletin passages now carry model/revision applicability and the bulletin serial
range. Certificate/contract bindings and continuity package/currency details are
explicit. These are authoritative fixture facts, not model-issued permissions;
existing verified identity, site/spending and explicit-approval enforcement remains.

All three decision-output schemas now require complete closed service-quote objects
with typed cent amounts; prompts place unquoted loaner/replacement offers in
alternatives. Both application publication guards require the two case-specific
quote IDs exactly once and compare every field with the stored authoritative quote.
USD-cent units are explicit in prompts, quote descriptions, rates, offers and approval
routing. The original numeric quote format is retained for provenance-compatible reuse.

Offline checks passed:

- [Initial 10 checks](../evidence/contract-offline-20261001-junit.xml), with
  [run evidence](../evidence/checks-20261001-213958/manifest.json): both Frameworks
  reject the captured Java comparison's extra quote objects, issue real schema
  correction feedback, and accept the structurally valid captured Sidecar response.
  Both deterministic asset-context reads reject spoofed context values as authority;
  existing quote/permission/token checks also pass.
- [Extended 19 checks](../evidence/contract-offline-extended-20261001-junit.xml), with
  [run evidence](../evidence/checks-20261001-214046/manifest.json): repeat the four
  contract/context checks with monetary prompt assertions, add two source-unit and
  applicability checks, five isolated Python publication rejection cases (extra, missing,
  duplicate, dollar-scaled and foreign-case quotes), and eight fixture/review tests.
  This is 25 distinct checks across the two runs, not 29 distinct scenarios.
- Actual Framework traces and independent journals are retained for both paths.
  Java packages successfully against the installed snapshot (no Maven test sources).
  An initial unsupported-schema-key startup rejection is retained under
  `evidence/contract-schema-startup-20261001`; supported schema fields repaired it.
  Exact count/value enforcement lives in the applications because the Framework
  schema supports neither array cardinality nor numeric bounds.

The [derived diagnostic](../fixtures/replay/quote-contract-diagnostic-v1.json) retains
Sol provenance, paired request IDs, provider envelopes and source SHA-256 values.
It normalizes only case IDs at execution. Deliberately sequencing two different
captured responses is a synthetic contract diagnostic, **not real-model correction
provenance or approved replay**. Both original comparisons lack authoritative
context and use ambiguous raw monetary prose. The [new read-only review](../evidence/contract-capture-review-20261001.json)
rejects the full capture. All original capture checksums still match. Predeployment
logs, records, artifact identities and the prior build baseline are preserved in
`evidence/pre-contract-deploy-20261001-213643` (its configuration copy reflects the
newly authored files; the prior baseline records the old deployed configuration hashes).

[Compatibility recheck](../evidence/compatibility-20261001-214110/manifest.json):
exactly one provider request per path, both with Muse/medium verified in the actual
request; both HTTP 404 `paid-model-training-violation-by-account`. The earlier
age-confirmation error is no longer reported. Both failed Framework traces and the
provider journal are retained. OpenRouter identifies its
[privacy settings](https://openrouter.ai/settings/privacy) as the controlling account
policy. No account setting or model was changed. Compatibility access has **not**
passed; no full live workflow was run.

Remaining evidence gaps: model-driven propagation of the new asset/approval context
through the complete tree; accurate dollar prose and decision quality under the new
contracts; selected-Muse full-workflow behavior; changed-priority responsiveness;
and a genuine model response to actual malformed-output correction feedback.
The corrected configuration and deterministic boundaries pass focused offline checks,
but those checks do not fill these semantic/full-workflow gaps. Reserve new paid calls
for those gaps after access is resolved, reusing captured responses where suitable.
Reviewed full replay and the remaining first-delivery business scenarios stay incomplete.

## Authorized beta.8-SNAPSHOT verification — timeout fix verified

The user installed Framework `1.0.0-beta.8-SNAPSHOT` and authorized local testing of its provider request-timeout fix. Both hosts successfully package the installed artifact; SHA-256 comparison confirms that their nested Framework JARs match it. Framework source reference is `b7dbefee8ffca873e84efb455e5609234c59e119`. Sidecar is unchanged beta.2 tag source rebuilt with the dependency override, not the published binary. Neither neighboring checkout was modified and no release was published.

`compose.snapshot.yaml` configures the supported 240-second provider request timeout for both paths. Both containers start and all five services pass readiness. Earlier timeout findings below describe beta.7.

The [first snapshot live run](../evidence/live-20261001-203830/summary.md) proves successful calls beyond the old limit in **both** paths using independent provider timing and completed Framework model frames. Its assertions report **6 passed / 4 failed**: timeout and dependent-evidence checks pass; both missions hit the separate 600-second mission deadline before complete synthesis/publication. Both actual traces report `ABORTED` with `LoomspanMissionTimeoutException`. The captures are rejected for replay. Six deterministic compatibility checks also passed on the snapshot. The supported local mission budget was then increased to 1,200 seconds, keeping the provider budget at 240 seconds.

The [longer-budget capture](../evidence/live-20261001-205953/summary.md) reports **9 passed / 1 failed**. Both Framework traces report `SUCCEEDED`; all four model responsibilities and both native final-synthesis stages were exercised on both paths. Provider timeout and dependent/final-synthesis evidence assertions pass. Sidecar publishes an immutable assessment with both authoritative quotes unchanged.

Java's application correctly rejects the completed model result: its comparison includes the two correct service quotes **plus two non-authoritative loaner/replacement objects without quote IDs** in `quotes`. Parent synthesis preserves those additions. There is no longer an observed provider/mission timeout blocker in this capture; the failing assertion is Java immutable-assessment publication. No invalid assessment or service request was persisted. See the [quote review](../evidence/live-20261001-205953/quote-review.json) and original model journal. The two-path bundle is not approved for replay.

Next application work: constrain `quotes` to issued authoritative quote objects and keep unquoted continuity/replacement alternatives in their appropriate fields; clarify integer-cent monetary units in model-facing contracts; supply/review the agreed authoritative asset and approval-context facts without treating them as model-granted permissions. Then capture/review again. The completed Sidecar result is mechanical execution evidence, not automatically approved model judgment. Changed-priority capture, real malformed-output correction, approved replay, valid-approval creation/recovery and the remaining first-delivery scenarios are still outstanding. Both snapshot containers remain running with the 240/1,200-second settings.

## Resume verification and independent progress — 2026-10-01

Read-only remote refs still show Framework beta.7 as the latest release, with main at `e35ab4488e5cac5e1cc6fef5f0f0797b5deb703d` (begin beta.8-SNAPSHOT development), and Sidecar beta.2 as its latest release. Tagged beta.7 `SpringAiProviderIntegration.openAi()` and its connection options still expose no request-timeout override. The required external dependency remains a supported longer OpenAI-compatible provider request timeout in a user-authorized release usable by both hosts. No unchanged live workflow was repeated, no release was substituted, and no owning-project source was changed.

Independent progress:

- Fixture journals now assign a request ID to each model request, response and failure. Newly registered live cases bind to their integration path. Replay matching can distinguish system-stage text from user/evidence text, retains dependency checks, rejects duplicate/ambiguous calls and has no provider fallback.
- `scripts/inspect_capture.py` writes a new, read-only mechanical review report outside the source capture. It checks terminal publication, model provenance/pairing, comparison and native completion, persisted quotes/assessment, conditional amounts and trace integrity. It never approves semantic judgment or replay. Both previous beta.7 captures are rejected; their original files remain intact. Historical unpaired journals cannot establish unambiguous concurrent response provenance.
- **8 focused tests passed** for proxy relay, replay ordering/dependency/isolation/rejection, fail-closed capture review and correct mission identification. These are fixture/tool tests, not business acceptance. The **6 deterministic compatibility checks also passed** after restoring normal configuration; permission checks now compare request records before/after rather than assuming an empty database, preserving future successful-request evidence.
- **2 nested-denial diagnostics passed**, one per path, in [checks-20261001-132017](../evidence/checks-20261001-132017/summary.md). Both use explicit `compose.authorization.yaml` test configuration and handcrafted negative responses. Actual nested planner requests omit creation from available capabilities; the deliberate unavailable-child proposal receives `not an exact visible capability name` feedback, is repeated for the supported corrective attempt, and is rejected. Independent database records are unchanged; Sidecar's application access log shows no creation-endpoint call. Two downloaded Framework traces are retained with hashes.
- Two earlier diagnostic attempts failed because the matcher first confused task-count constraints with available capabilities, then lacked the corrective-attempt response. Their evidence is retained. Neither was counted as a successful authorization check.

The nested diagnostic uses incomplete approval and therefore **does not complete** the accepted valid-approval denial/Luis positive-control pair. Full base/changed-priority captures, real malformed-output correction, approved replay, creation/recovery and gated complete-case isolation remain unexecuted or blocked as listed below. Normal business configuration is restored after diagnostic execution; test skills remain available through the documented opt-in overlay.

## Beta.7 / Sidecar beta.2 verification

Both releases are available. The exact-tag source exports build, and both packaged Framework JARs match the released Maven Central SHA-1 `02f0969a50acbf06355c1391bf9a0449c90ae077`. See [build identities](../evidence/beta7-build-identities.json). Java and Sidecar containers were rebuilt on these versions.

The first unchanged live workflow rerun is [live-20261001-122349](../evidence/live-20261001-122349/manifest.json). Four evidence assertions pass: on both paths, full history, reference evidence and service terms match the independent fixture returns in the actual dependent planner request; all five formerly missing markers reach the equipment-assessment child model. Thus the previous dependent-evidence truncation is no longer observed.

Both executions subsequently fail on a model HTTP read timeout around 60 seconds: Java at `assessEquipment#mission-model`, Sidecar at `resolveEquipment#step-5-model`. Actual Framework traces retain `OpenAIIoException` with `SocketTimeoutException` while reading response headers. Four completion/final-synthesis assertions fail because these runs did not reach those stages. This is not evidence of continuing truncation, and not a successful first-delivery workflow.

The recording proxy buffered the complete upstream response before returning headers. It has been changed to relay upstream headers and body chunks promptly, retaining any upstream whitespace keepalives, without changing request JSON or response JSON. An isolated transport test verifies that the first upstream bytes are forwarded before the remainder is consumed and that the complete JSON is recorded unchanged. The selected model and reasoning setting remain unchanged. The [relay retry](../evidence/live-20261001-123114/manifest.json) still times out on Java at `resolveEquipment#step-4-model` and Sidecar at `resolveEquipment#step-5-model`, after 60 seconds. Both Framework traces show `java.io.InterruptedIOException: timeout` from `okhttp3.internal.connection.RealCall.timeoutExit`, while consuming the chunked response body. This rules out response-header buffering as the only cause. The retry reports **3 passed / 5 failed**: both full-sibling-record assertions and the Sidecar child-input assertion pass; Java does not reach that child in this retry, and neither path reaches final synthesis or application completion. The first run already verified the Java child input. Both retry traces are retained, and both captures are rejected as complete replay baselines.

Source inspection of the locally resolved Spring AI 2.0.0 source JAR confirms `AbstractOpenAiOptions.DEFAULT_TIMEOUT = Duration.ofSeconds(60)`, inherited by `OpenAiChatOptions` and applied as the OkHttp request timeout. Framework beta.7 `SpringAiProviderIntegration.openAi()` does not set a different timeout. Its public `ConnectionProperties` / `OpenAiOptions` expose no corresponding setting; the bundled connection documentation says unknown `loomspan.*` settings are rejected and `spring.ai.*` is not inherited. The configured mission timeout is already 600 seconds and does not override this provider request limit. No unsupported property, client replacement, or Framework patch was introduced.

The concrete remaining unblock is a supported way to configure a longer OpenAI-compatible request timeout (for example, 180–240 seconds within the 600-second mission budget), made available to both embedded and Sidecar paths. This is a separate finding from the repaired evidence truncation. Final-synthesis evidence preservation still needs a complete live run.

[Six deterministic regression checks](../evidence/checks-20261001-122409/junit.xml) passed on the new releases, covering the same limited compatibility scope as the historical run. These are not approval/recovery acceptance.

## Historical beta.6 blocker: complete evidence did not reach dependent planners

The pinned beta.6 planner builds each subsequent model request using the canonical original mission input, a summary truncated to **100 characters per completed task**, and the latest tool result truncated to **1,000 characters**. Earlier complete results are not provided to the dependent model. Final synthesis has the same latest-result limit. These are fixed implementation constants, not the configured output schema limit or provider context window.

Source inspected from Framework commit `50fa1a7dcf1974a3e73ebde2a41bd7ee49a28542`:

- `src/main/java/ai/loomspan/internal/runtime/step/StepPromptBuilder.java`: `MAX_LAST_RESULT_CHARS = 1000`, applied in assigned-step and final-response prompts.
- `src/main/java/ai/loomspan/internal/runtime/step/StepLoopMissionExecutionEngine.java`: completed task summaries call `truncate(success.result(), 100)`.

The live Java run retrieved the history, manufacturer passages and terms through real annotated skills. Its later equipment-assessment model explicitly reported unavailable history and guidance. Resolution planning inherited that gap. Comparison and native synthesis lost checked options and full quotes; native synthesis returned empty quote/citation arrays and described the truncated comparison. This is not a successful assessment, despite model/schema success. The application rejects missing or altered authoritative quotes before publishing an assessment.

The Sidecar run also reached equipment assessment with incomplete upstream evidence. Its terminal failure was separately caused by a provider connection closing mid-response (`httpx.RemoteProtocolError`) during resolution planning; the fixture initially surfaced this as HTTP 500. It did **not** reach comparison/final synthesis, so that terminal failure is not attributed to truncation. Fixture error handling now journals transport failures explicitly and returns a bounded 502. Both original Framework traces are retained.

The closed public API has no supported planner replacement or text-result storage/retrieval SPI. `ref://` resolution exists, but inspection and observed prompts did not establish an application-facing mechanism that automatically makes complete prior planner results available. Guessing reference paths, injecting fixture answers into provider requests, preloading all evidence into the root, or replacing Framework internals would defeat this demonstration. No such workaround or baseline change is made.

At the time, required resolution was an owning-project supported mechanism for complete dependent-result and final-synthesis evidence, verified against this reproduction. No Framework/Sidecar source was changed, no issue was published, and no release was substituted. The subsequent user-authorized release update and its observed results are recorded above.

## Implemented foundations

- Exact-tag Sidecar beta.2 source export/build; embedded Java uses released beta.7 through Maven. Both compile successfully.
- Compose deploys both apps, actual Sidecar, Keycloak 26.3.5 and separate FastAPI external fixtures.
- Keycloak seeded accounts with top-level role and audience mappings; browser Authorization Code + S256 PKCE, isolated Playwright sessions, no password grant.
- Independent receiving API token checks; Java security-context retention, Python/Sidecar original-token passthrough.
- Four substantive model responsibilities, explicit parallel groups/dependencies, deterministic annotated Java/REST skills, and versioned fictional source records excluding evaluator notes.
- SQLite authoritative quotes, immutable assessment versions, and atomic approval/request storage code. **Creation/recovery behavior has not yet passed end-to-end acceptance**, since the required valid assessment is blocked.
- Fixture registration, strict per-case script matching, independent journals and gates; explicit live recording mode. Unregistered/ambiguous model requests fail visibly.
- Supported Framework NDJSON artifact download, correlation and secret-value scan in both paths. No runner-generated substitute traces.

## Engineering choices

This local demonstration binds published ports to loopback and uses an isolated Compose bridge with HTTP inside that boundary. Keycloak runs development mode. This is a documented local transport choice, not a production/TLS deployment claim. Management authentication remains separate and is not used by the business caller.

Per-app SQLite databases persist on host mounts. Idempotency keys are scoped to verified issuer/subject and retained with receipts for the local database lifetime. Approval binds assessment, quote, option, attendance, repair scope and exact cap. The recovery path reads the original record before checking quote expiry. Money uses integer USD cents. Fixture business time remains separate from JWT security time.

Sidecar uses supported `configuration.mode=file`; publication and management-console workflows are outside this delivery. Provider calls use a recording proxy that forwards the actual Framework JSON request unchanged to OpenRouter; it never forwards application bearer tokens or records provider Authorization headers. Ordinary replay has no provider fallback.

## Not completed or not claimed

- Reviewed complete real-model baseline/changed-priority captures suitable for acceptance replay.
- Real malformed-output correction capture and reviewed fault-derived replay.
- Approved replay scripts, full base workflow acceptance, approval/creation/recovery acceptance.
- Controlled nested authorization denial/positive control; gated two-case isolation acceptance.
- Production TLS, broader management/publication/load/restart/shutdown, or CI.

Captured evidence is reviewed as **rejected for baseline provenance** when required evidence is lost. A model call or a green build does not establish the business claim. See generated evidence directories and test results for exact executed checks.

## Executed checks and retained evidence

- [Live compatibility manifest](../evidence/compatibility-20261001-005049/manifest.json): both paths returned the requested structured result with the selected real model. This folder contains actual Framework-generated traces for each path. It does not exercise the complete workflow.
- [Reviewed complete-workflow attempt](../evidence/live-20261001-005945/summary.md): both paths' actual requests/responses, independent downstream journal, two Framework traces and terminal results. Four [acceptance assertions failed](../evidence/live-20261001-005945/delivery-junit.xml); captures are rejected for replay baseline use. Sidecar's separate transport failure prevented its last responsibilities from running.
- [Deterministic compatibility rerun](../evidence/checks-20261001-011456/junit.xml): **6 passed** after correcting Java policy declarations to supported JSR-250 `@RolesAllowed` and enabling that enforcement. Covers authoritative quote amounts without model calls, Maya's direct public-boundary permission precheck, and rejection of missing tokens, on both paths. The permission precheck uses an empty approval body and is expressly **not** the required otherwise-valid approval denial/nested positive-control acceptance scenario.
- The successful rerun directory contains quote results, independent journals and database snapshots, current running artifact identities, build checksums, and real Framework traces for deterministic invocations. Original failed-run runtime image digests were not recovered after interruption/container removal; that gap is disclosed rather than filled using later artifacts.
- Python sources compile; Java application and exact-tag Sidecar package successfully. Maven package commands used `-DskipTests`; no Maven test success is implied.

The Docker stack is left running for inspection. No changes were made to neighboring Framework or Sidecar checkouts, no commits or issues were published, and the release baseline was updated with explicit user authorization.
