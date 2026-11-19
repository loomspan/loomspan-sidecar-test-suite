# Framework migration acceptance roadmap

## Current scope — November 15, 2026

The direct-OpenAI migration and model reassessment in docs/project-agreement.md
supersedes the live matrix below: remove OpenRouter live acceptance and defer Meta,
Ollama, Anthropic and Gemini. Historical matrix requirements are retained as deferred
coverage, not passing evidence. Direct OpenAI execution is authorized after offline
readiness, with reasonable batches and no fixed USD ceiling. Establish both-host
Sol/Luna business baselines, then all-Terra and all-Luna Java trials and selected
Sidecar confirmation. Preserve framework contract coverage separately from semantic
business review. The earlier no-paid-execution statements describe prior decisions.

This bounded migration/evaluation round is complete; see [results and remaining
gates](docs/beta10-evaluation.md). It does not close the broader acceptance matrix
below. The mixed model assignment is a reviewed candidate, not a default promotion.


## Ownership, sequencing and completion — agreed November 11, 2026

This is the authoritative home for test-suite implementation work and deployed/live
acceptance requirements moved from the Framework migration documents. Create tickets
in this project and implement this roadmap after Framework implementation is complete.
This document does not create tickets, implement suite changes or authorize paid calls.

Framework owns production migration, exhaustive deterministic tests, real
factory/advisor/tool-path request captures, applicable Console changes/tests and the
public-surface check. Its [open-blocker register and acceptance handoff](../loomspan-framework/ai/thoughts/phases/pr-30-blockers.md)
retain current limitations, closure requirements, and historical document retrieval.
The completed migration roadmap and schema research are archived in Framework Git
commit `7eb8ac489dd72a45175e3b9fadd02e7bcd01cc30`, at their original
`ai/thoughts/phases/` paths. Do not duplicate the suite plan there.

Framework implementation may complete before this roadmap. Overall migration
acceptance remains pending until all required deployed/provider-free and live gates
below pass. A missing, failed or unverified cell remains open. Moving work between
repositories does not weaken requirements or convert historical evidence into a pass.
Product defects discovered here are fixed in their owning repository; suite tickets
own harness, fixtures, scenarios, orchestration and acceptance evidence.

## Ticket sequence and evidence discipline

All work below is pending. After Framework implementation, create concrete tickets in
this project in dependency order, carrying the applicable detailed requirements below:

1. Inventory current coverage and migrated artifact prerequisites; establish the
   protected suite, required-coverage manifest and isolation/selection checks.
2. Migrate Responses fixture matching, envelopes, usage, controlled responses and
   proxy routing; migrate YAML authoring generators and their outputs together.
3. Add the missing deployed contract scenarios and six-endpoint orchestration,
   including the selected host coverage, route/effort manifest and bounded run controls.
4. Stage coherent artifacts and run applicable provider-free suite checks and
   both-host business/TypeSafe regressions, preserving accepted reference packs.
5. Verify credentials/access, routing, media, pricing and effective settings without
   claiming live success; obtain separate explicit authorization for a concrete paid run.
6. Execute the bounded matrix and retain per-cell evidence, costs and unresolved gates.

Before prescribing a change, trace the existing complete path and relevant assertions,
identify the accepted requirement and concrete delta, and reuse working coverage.
Distinguish inspected tests from tests run, historical/mock evidence from live capability,
and agreed policy from pending implementation. Do not rebuild working behavior or
invent restrictions, fallbacks, APIs or acceptance scope. Preserve diagnostic fidelity.

### Earlier OpenRouter checklist scope remains an audit question

Earlier Framework checklists requested a live non-native-Responses upstream and a
same-Meta-model direct-versus-routed comparison where available. Those entries were
not explicitly reconciled with the final initial matrix. Preserve the investigation;
do not silently treat the extra comparisons as completed, removed, or authorized.
The initial run uses only the final manifest and existing caps below. Before creating
any additional live-comparison ticket, resolve whether those earlier entries are stale
or separately scoped follow-up. Do not expand the initial matrix or budget. Retain
ordinary deterministic wire-shape and replay coverage regardless of that resolution.

## General acceptance obligations carried from Framework Phase 4

Apply these obligations within the final bounded matrix below; they do not authorize
extra sends or routes. Record any coverage the matrix cannot establish as unverified
and resolve its scope before further execution.

- Use opt-in bounded probes with explicit models and credentials. Cover text,
  supported reasoning settings, tool round trips, multiple rounds, parallel calls
  where supported, and output validation.
- Verify returned reasoning items and their actual replay. Record unsupported options
  and protocol differences; any required production compatibility fix belongs in
  Framework and must be justified by concrete evidence.
- Assess correctness, repeated tool work, latency, usage and context growth separately
  from protocol correctness. Use recorded pre-migration results or the old revision
  for comparison; do not retain a second runtime implementation for benchmarking.
- Publish configuration examples, limitations and reproducible results. Earlier Meta
  Chat smoke results do not establish Responses compatibility; the earlier Ollama
  reasoning/tool probe does not establish native structured output.
- Responses acceptance requires the selected OpenAI, Meta, OpenRouter and Ollama
  cases through the same adapter with stateless replay. Structured-output acceptance
  additionally requires selected skill-output and planning cases on all six endpoints,
  explicit route/model identities and limitations, including native formatting with
  tools where combined. Both workstreams must pass for overall migration acceptance.

## Preserved agreed requirements

The following requirements were agreed November 11, 2026 and relocated without
reducing acceptance scope. Source inspections and published capability/price statements
are historical evidence, not fresh verification. Recheck current prerequisites at
implementation/preflight. Policy is resolved except the earlier checklist clarification
identified above; implementation and passing acceptance evidence remain pending.

## Acceptance ownership, suite gaps and mandatory gates — agreed November 11, 2026

Use loomspan-framework for deterministic implementation coverage and the neighboring
loomspan-sidecar-test-suite for deployed migration acceptance. The latter already hosts
both an embedded Java Framework application and a Python/SDK/Sidecar application, plus
separate Java/Python SDK consumers. It is not merely an HTTP-only Sidecar test harness.
Reuse its capability-oriented suites, runtime orchestration, artifact recording and
provider-disabled restoration; do not create a second live acceptance harness here.
Fix tracking stays in the owning product repository, not PR-specific suite partitions.

| Acceptance area | Framework repository | Sidecar test suite |
| --- | --- | --- |
| Schema semantics and Java declarations | Exhaustive compiler/validator, generation, binding, recursion errors and resource checks | Representative deployed input/output and real Java declarations with equivalent Sidecar callbacks |
| Provider contracts | Actual request captures for all three integrations, schema/options fidelity, ordered replay and tool identities | Selected live endpoint/model/route compatibility through deployed integrations |
| Repairs/status/side effects | Deterministic refusal/incomplete, repair history, authorization and duplicate-side-effect prevention | Small controlled scenarios verifying deployed wiring and observable behavior |
| Planning/bindings/evidence | Detailed semantic, projection and isolation regressions | Existing composed workflows plus targeted missing integration cases |
| Attachments | Validation, direct Java resource handling, materialization and serialized requests | Real supported files on selected live routes through supported host entry points |
| TypeSafe | Declaration/metadata and native executor unit tests | Existing native protocol, passthrough, forwarding, bindings and policy regressions |
| Catalog/Console | Metadata and Console contract/rendering tests in framework/loomspan-console | Relevant external integration assertions only |

Inspected suite gaps to close:

1. fixtures/server.py serves /v1/chat/completions and proxies live chat to OpenRouter's
   Chat endpoint. fixtures/replay.py matches messages/reasoning_effort. Migrate request
   matching, response envelopes, controlled responses, usage reporting and live proxy
   handling to Responses for the migrated openai driver. Preserve maintained reference
   packs; derive new protocol fixtures separately. Reusing accepted business answers
   proves business regression, not ordered reasoning/tool replay fidelity.
2. Existing chat live orchestration is OpenRouter-specific. Add bounded selections for
   OpenAI, Meta, OpenRouter, Ollama, Anthropic and Gemini through existing orchestration.
   Host coverage is agreed below; run budgets are agreed below; model/route selections and timeouts are finalized below.
   Do not multiply the entire equipment workflow across every provider to prove protocol
   compatibility; use small capability-oriented cases.
3. Migrate maintained YAML and its authoring generators/contracts together, including
   explicit intended openness and accepted metadata vocabulary. Preserve business
   behavior and Java/Sidecar equivalence. Regeneration must not restore the old dialect.
4. Add focused scenarios for typed-map/unconstrained inputs, native schema-plus-tools,
   response refusal/incompleteness, and attachments where existing business scenarios
   do not establish these contracts. Keep exhaustive variants in framework tests.
5. Stage coherent migrated Framework artifacts in both Java and Sidecar hosts. Reuse
   build recording to identify actual artifacts/configuration and relevant source/suite
   revisions. A shared mutable snapshot coordinate alone is not migration acceptance.

The TypeSafe suite already covers fixed/dynamic questions, substitution, forwarding,
bindings, malformed envelopes, extra answers and native passthrough. Migrate its schemas
and chat-parent fixtures and rerun that coverage rather than invent a new native test
suite. New paid TypeSafe evaluation is not inherently required for this migration.
SDK TLS/mTLS and service-commitment checks are affected-path regressions, not tests to
repeat for every model. The suite's --suite all covers its business suites, not every
SDK/transport/commitment check; reports must name actual selections.

Mandatory acceptance gates for later tickets:

- Passing applicable deterministic framework tests, including the previously agreed
  numbered TBD cases, real factory/advisor/tool pipeline captures and public-surface
  architecture checks after production type changes. Isolated SDK proof is insufficient.
- Coherent migrated dependencies/artifacts in both deployed hosts, migrated authoring
  sources and provider-free business/TypeSafe integration regression with maintained
  fixtures preserved. Report selected checks and uncovered paths explicitly.
- Responses fixture and live-path readiness before claiming migrated integration
  coverage; no Chat fallback, old runtime implementation or successful legacy replay
  counted as proof of the new path. Native Anthropic/Gemini paths remain native.
- Selected live route cases for the required provider endpoints, with exact model/route,
  versions, schemas/requests, outcomes, local validation, usage, retries and limits
  recorded. Host coverage is agreed below; cases and budgets are agreed below; model/route and effort selections are finalized below; wall-clock settings are agreed below.
- Resolve relevant replay/schema mapper defects, including Anthropic root constraints
  and Gemini raw tool-schema fidelity. A successful final answer cannot substitute for
  preserved protocol state and schema evidence. Do not silently drop required features.
- Missing credentials, unavailable endpoints, unresolved dependencies/mapper defects,
  and failing required features remain explicit open completion gates. Independent work
  may continue; skipped/untested cases are not passes and trigger no automatic fallback.
- Keep deterministic correctness, deployed integration, live compatibility and observed
  quality/performance evidence distinct. Prior suite reports apply only to their recorded
  builds. Publish evidence references from this roadmap and link the acceptance outcome from the Framework roadmap.

Inspection sources (historical November 11 inspection): AGENTS.md, docs/project-agreement.md,
docs/coverage.md, docs/runtime.md, docs/typesafe-ai.md, fixtures/server.py,
fixtures/replay.py, scripts/run_suite.py and scripts/suites/registry.py. Inspection was
read-only: no tests, builds, runtime changes or paid calls were performed. Future paid
scope is not authorized by this documentation update; no tickets are created here.

## Live host coverage — agreed November 11, 2026

Use reduced live duplication within loomspan-sidecar-test-suite. Both hosts below are
owned by that suite: its embedded Java Framework app and its Python/SDK/Sidecar app.
Do not interpret Java-host acceptance as a new live harness in loomspan-framework.

| Coverage | Required host selection |
| --- | --- |
| Provider-free business/schema/callback and TypeSafe regression | Both suite hosts |
| Full bounded provider-compatibility cases for OpenAI, Meta, OpenRouter, Ollama, Anthropic and Gemini | Embedded Java host |
| Representative live tools-plus-structured-output case for each of the three integrations (OpenAI Responses, Anthropic, Gemini) | Python/Sidecar host |
| Host-specific or unexplained discrepancy | Reproduce on both hosts as needed to resolve it |

Meta, OpenRouter and Ollama receive full selected live-case coverage on the Java host;
their Sidecar configuration is checked deterministically. Use the OpenAI endpoint for
the representative Sidecar Responses case. Cases and run budgets are agreed below; timeout
settings are agreed below. The full matrix means the agreed bounded cases,
not every model, every schema keyword or the entire equipment workflow per endpoint.

Rationale: verify all required endpoints through deployed Framework and all three
integration paths through Sidecar without repeating the whole live matrix twice.
This does not establish live acceptance of every provider/host combination. Reports
must explicitly distinguish live verification from deterministic configuration checks.

Mandatory acceptance requirements: both-host provider-free results; Java-host live
results for all six selected endpoint routes; Sidecar live tools-plus-structured-output
results for the three selected integration representatives; deterministic Sidecar
configuration checks for remaining Responses routes; and resolved or explicitly open
host-specific discrepancies. Record host, artifact/configuration identity and route
for every result. Missing required cells remain open gates under the preceding rules;
do not infer live Sidecar route acceptance from the Java host's success.

This records agreed requirements; implementation and paid execution remain pending.

## Protected framework acceptance suite and Meta Contributor — agreed November 11, 2026

Maintain a durable framework-acceptance suite inside loomspan-sidecar-test-suite,
separate from business examples and SDK/transport suites. Own its scenarios, skills,
fixtures, provider/host matrix and expected results in dedicated suite locations using
the existing suite layout and explicit runner selection. This is framework contract
coverage, not a disposable migration-specific folder or PR partition.

Protect coverage through a checked-in manifest identifying required contracts and
host/provider cells. Verification must fail when a required case disappears or is
silently skipped. Business generators and fixture-refresh commands must not modify
framework-acceptance assets. Keep maintained accepted fixtures separate from fresh
run output; changing expectations requires a deliberate update with recorded rationale.
Shared runtime/reporting infrastructure remains reusable; changes to it require the
framework suite's applicable provider-free regressions. Protection means stable contract
coverage and reviewed updates, not permanently frozen provider IDs or protocol files.

Mandatory acceptance tests: explicit suite selection/discovery; required-case manifest
completeness; missing/skipped-cell failure; isolation from business authoring/refresh
commands; refusal to overwrite maintained fixtures with run output; independent fresh
result directories; framework regression selection for shared harness changes; and
reports distinguishing current tested artifacts, live/provider-free cells and gaps.
Keep existing business assignments and accepted reference packs unchanged.

Select muse-spark-1.3-contributor for direct Meta Responses acceptance, replacing the
previous standard-mode proposal. Meta documents the same model at discounted prices
in exchange for permission to use submitted content and responses for training.
Use deliberately authored synthetic acceptance data; this is not a content-masking
mechanism. Contributor does not offer max reasoning effort; use a supported setting
for continuation tests. Account access and actual route acceptance remain unverified.

Published prices checked November 11, 2026: Contributor input $0.10 and output $0.20
per million tokens, versus Standard $1.25/$4.25; cached Contributor input $0.002.
Source: https://dev.meta.ai/docs/pricing-rate-limits and
https://dev.meta.ai/docs/choose-a-model. Recheck pricing before an authorized run.
The earlier exclusion of Contributor was not a necessary compatibility boundary.

The final endpoint model selections below supersede earlier proposals. Bounded
cases, request/token caps and USD 5 ceiling are agreed below; timeout
settings are agreed below. Run deterministic checks first; use compact synthetic skills and tool
results, small real media files, and physical-provider-request accounting. No new paid
TypeSafe evaluation is required. No paid calls, production edits or tickets are
performed or authorized by this document update.

## Bounded live cases, token budgets and acceptance rules — agreed November 11, 2026

These are initial acceptance-run ceilings in the protected framework-acceptance suite,
not production defaults or targets. Execute only after deterministic readiness checks
and separate explicit paid-run authorization. Use tiny purpose-built skills, synthetic
identifiers, short tool-result objects and small real files. Do not substitute a full
business workflow or repeatedly sample until a desired outcome appears.

| Case | Required evidence | Maximum physical requests per route | Maximum generated tokens per request |
| --- | --- | --- | --- |
| Small structured result | Native output configuration, required/nullable fields, local acceptance | 1 | 1,024 |
| Two-tool chain to structured result | Typed-map and unconstrained arguments, tool-result use, ordered continuation, no duplicate execution | 3 | 4,096 |
| Small planned task | Actual planner contract, deterministic child execution, bindings/evidence handling, final result | 4 | 4,096 |
| Two small images plus tool | File association/order, media-bearing execution, tool continuation, structured result | 2 | 2,048 |
| One-page PDF plus tool | Real PDF acceptance, attachment continuation, structured result | 2 | 2,048 |
| Full route total | All cases above, through real framework execution | 12 | 37,888 aggregate generated tokens |

Run all five cases on six Java-host endpoints: at most 72 requests including 12 local
Ollama requests. Run only the two-tool-chain case on the Sidecar OpenAI, Anthropic and
Gemini representatives: at most nine additional requests. Overall ceiling is 81 requests,
of which 69 are cloud requests. These count physical sends, including planner and
continuation calls, not logical tests or skills. A request that fails or times out still
consumes its send allowance; do not assume it was unbilled.

Limit every request to 8,192 total input tokens, counting framework instructions,
schemas, retained history and media accounting. Across cloud requests the mathematical
maximum is 565,248 input tokens and 226,304 generated tokens (approximately 566,000 and
227,000 respectively). Generation allowances include reasoning and visible output;
verify each provider/adapter's budget semantics before running. Final visible responses
should ordinarily be under 200 tokens, but this is a fixture design target, not a new
production response restriction. Do not truncate protocol history or schema content to
force a request below the cap; simplify fixtures or record a blocked case.

The total cloud spending ceiling is USD 5 for this initial matrix, not USD 5 per route
or rerun. Recheck selected-route pricing at preflight and calculate a conservative
estimate from actual fixtures. Before sending, reserve the maximum estimated request
cost including input, media, replay and maximum billed generation/reasoning; reconcile
with usage without counting reasoning twice. Keep reservations for uncertain billed
outcomes. Stop before a send if remaining allowance is insufficient. If pricing/media
accounting cannot be bounded reliably, leave the case pending. This ceiling does not
guarantee matrix completion. Do not rely only on after-the-fact usage totals, assume
cache discounts, silently reset the ledger, or add paid provider tools. These are suite
run controls, not new Framework public configuration requirements.

Disable automatic transport retries and automatic schema-repair attempts for this
initial compatibility batch. Existing production retry/repair ownership remains intact
and is tested deterministically. Stop a failing case and diagnose offline; no automatic
increase of caps, effort, retries, model changes, fallback or weakened assertions.
Any subsequent rerun must retain previous spend accounting and have an explicit scope;
this agreement itself authorizes no paid sends.

Acceptance rules and mandatory ticket tests:

- Test request/token/cost reservations and stop behavior without paid calls: exact caps,
  one-over rejection, concurrent reservation safety if parallel sends are used, failed
  sends, uncertain billing, no implicit retries/repairs and no ledger resets on rerun.
- Demonstrate actual tool/planner/native-output paths and retained request evidence.
  Short successful text alone is not schema or reasoning-continuation proof. If no
  replayable reasoning is emitted, that assertion remains unverified, not passed.
- Unsupported PDF/media or combinations remain explicit gaps. Do not convert files,
  change protocols/models or silently skip cells into success. Missing access, adapter
  defects and exhausted budgets likewise leave required cells open.
- Pair live compatibility with deterministic invalid-result/argument rejection and
  side-effect checks. Refusal/incomplete responses, malformed arguments, repair history,
  and attachment preservation during corrections use controlled fixtures first.
- Preserve original requests, schema and diagnostics; compare accepted constraints and
  required item/order fidelity. Record host/route/model, actual usage/cost, attempts,
  local validation, artifacts and unverified assertions separately from task quality.
- A capped/incomplete generation is not successful validation. Initial batch failures
  cannot establish that the provider fundamentally lacks a capability without diagnosis.

Model/route, effort and wall-clock timeout settings are finalized below. Provider availability, credentials,
final dependency pins, adapter repairs and actual passing evidence are implementation/
execution gates, not facts established by this agreement. No paid calls have been made.

## Terra acceptance selection — agreed November 11, 2026

Use gpt-6.1-terra for direct OpenAI Responses acceptance and openai/gpt-6.1-terra
through OpenRouter's OpenAI standard endpoint (tag openai), replacing the prior Sol
proposal. Use the same direct Terra model for the Sidecar representative. Retain
explicit route restriction, disabled fallback and resolved-endpoint verification.
Business Sol/Luna assignments remain unchanged.

Official OpenAI documentation lists reasoning, function calling, image input and
structured outputs; tool calling requires Responses. The public OpenRouter endpoint
listing inspected November 11 advertises reasoning, tools and structured outputs for
its openai route, with text/image/file inputs. Both list standard short-context prices
of USD 1 per million input and USD 5 per million output tokens. This is half the
previous Sol proposal's USD 2/10 rates. Recheck prices/access before authorized runs.
Sources: https://developers.openai.com/api/docs/models/gpt-6.1-terra and
https://openrouter.ai/api/v1/models/openai/gpt-6.1-terra/endpoints.

Rationale: compact protocol/schema acceptance does not require Sol's model selection.
Retain all assertions, request/token limits and the total USD 5 ceiling; no automatic
fallback to Sol or budget increase if a case fails. Published capabilities are not
passing integration evidence; account access, PDF handling and exact combination
acceptance remain gates. No inference calls or runtime configuration changes occurred.

## Final model, route and effort manifest — agreed November 11, 2026

| Endpoint | Acceptance model | Protocol / route | Reasoning |
| --- | --- | --- | --- |
| OpenAI | `gpt-6.1-terra` | Direct Responses | Explicit medium |
| OpenRouter | `openai/gpt-6.1-terra` | Responses; OpenAI standard endpoint tag `openai` only; fallback disabled | Explicit medium |
| Meta | `muse-spark-1.3-contributor` | Direct Responses | Explicit medium |
| Ollama | `qwen3.5:4b-q4_K_M` | Local Responses | Thinking enabled; boolean-only model, not medium |
| Anthropic | `claude-sonnet-5-5` | Native Messages | Native output effort medium |
| Gemini | `gemini-3.8-flash` | Native Gemini Developer API | Native thinking level MEDIUM |

All six receive the bounded Java matrix; the three agreed Sidecar representatives
use the same direct OpenAI, Anthropic and Gemini selections. Business model assignments
remain unchanged. These selections supersede earlier proposals, not recorded historical
probe results. Medium is a provider-specific effort setting, not equal compute across
providers. Do not silently use defaults, lower effort, change models or expand budgets.

The inspected local baseline is Ollama 0.40.16, model digest
`2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05ee4eefd`.
Record/recheck the actual server version and digest before execution. The model reports
boolean thinking support; do not manufacture a numeric medium mapping. Verify the shared
Responses route can express enabled thinking; inability to do so remains a blocker.
OpenRouter must restrict routing to the standard OpenAI endpoint, disable fallback,
require support for requested parameters and record the resolved endpoint; a different
provider, Flex or priority route is not equivalent acceptance evidence.

Framework option-mapping implementation and deterministic request-capture requirements
are owned by the [Framework acceptance handoff](../loomspan-framework/ai/thoughts/phases/pr-30-blockers.md#later-deployed-and-live-acceptance).
The original TBD-14 requirements remain in the archived migration roadmap identified above.
Consume that evidence before suite preflight; missing adapter support remains a gate.

Mandatory ticket acceptance tests:

- Offline manifest checks pin all six model/route/effort combinations, the three Sidecar
  representatives and Ollama digest; preserve business suites and their assignments.
- Capture actual adapter requests proving native medium on the five cloud endpoints,
  enabled thinking on Ollama, and unchanged per-case generation caps. Cover initial,
  tool-continuation and planner calls, including option combination/model overrides.
- Prove Anthropic sends no rejected thinking budget and does not inflate max_tokens;
  Gemini sends native MEDIUM rather than the legacy numeric budget. Unsupported option
  combinations fail preflight without paid sends or implicit fallback.
- Prove OpenRouter routing restrictions and resolved-endpoint evidence; reject missing
  parameter support or route drift. Published capability flags alone do not pass a case.
- Record requested and effective settings, actual usage and incomplete statuses in live
  evidence. Missing reasoning material leaves continuity unverified; timeout or capped
  output is not a pass. Retain the USD 5 ledger and zero automatic retries/repairs.

Provider references inspected November 11, 2026:
[OpenAI Terra](https://developers.openai.com/api/docs/models/gpt-6.1-terra),
[OpenRouter endpoint inventory](https://openrouter.ai/api/v1/models/openai/gpt-6.1-terra/endpoints),
[Meta reasoning](https://dev.meta.ai/docs/reasoning),
[Sonnet migration guide](https://platform.claude.com/docs/en/models/sonnet-5-5/migration-guide),
[Gemini 3.8 Flash](https://aistudio.google.com/docs/models/gemini-3.8-flash).
These are configuration evidence, not executed acceptance. Wall-clock settings are
agreed below. No production changes, tickets or paid calls are authorized here.

## Acceptance timeout profile — agreed November 11, 2026

Use one acceptance-only profile for every selected provider and both suite hosts:

| Boundary | Limit |
| --- | --- |
| Each physical provider request | 180 seconds |
| Fixture proxy upstream request | 210 seconds |
| Each case's mission | 900 seconds |
| Runner deadline including evidence collection grace | 960 seconds |

Rationale: the largest bounded case permits four physical requests, leaving 180 seconds
for orchestration after four 180-second requests. The same profile gives local Ollama
headroom without separate provider tuning. The proxy has 30 seconds of margin beyond
the framework request boundary; the runner has 60 seconds beyond the mission boundary
for terminal-state observation and evidence collection. These are maximum waits, not
performance targets or authorization to send additional requests.

Implement as a protected framework-acceptance suite overlay using existing timeout and
runner mechanisms. The inspected compose.runtime.yaml business profile remains
480/510/2400 seconds for provider/proxy/mission. Do not change production defaults,
business suites, TypeSafe timeouts or callback limits solely to configure this matrix.
Record effective values in run evidence. Verify actual adapter timeout semantics;
a socket inactivity timeout alone must not be reported as a total elapsed deadline.
The runner's polling deadline must account for in-flight polling/collection work, not
merely check elapsed time before starting another blocking poll. Reuse existing
cancellation paths; do not introduce a new public Framework timeout API for this suite.

Mandatory ticket acceptance tests (provider-free, using controlled delays/clock control
or scaled test durations rather than waiting for the full live limits):

- Effective configuration proves 180/210/900/960 seconds for the selected suite on both
  hosts and all selected routes, including option combination, model overrides,
  planner and tool-continuation requests. Business profiles remain unchanged.
- A stalled provider request terminates at its configured boundary without automatic
  retry, schema repair, model fallback or a subsequent tool dispatch from a late reply.
  A timely response still follows the normal tool/result pipeline.
- Mission expiry prevents further provider sends/tool dispatch for that case and uses
  existing cancellation/terminal-state behavior. Preserve already completed tool effects;
  do not claim cancellation can undo a tool or guarantee the provider stopped billing.
- Runner timeout and evidence-collection work are bounded by the outer deadline;
  pending HTTP polls cannot silently extend it. Timeout/collection failure remains a
  failed or incomplete case, never a successful validation or silently skipped cell.
- Preserve available request, status, timing and diagnostic evidence on every timeout.
  Count the physical send, retain uncertain-cost reservations and previous spend, and
  prove no automatic rerun, token-cap increase or budget reset follows timeout.
- Check the proxy/framework boundary ordering and provider-disabled restoration after
  failure. A missing terminal result or incomplete artifact is reported explicitly.

The request/token/USD 5 ceilings still govern independently. No paid sends, production
changes or tickets were performed or authorized by this documentation decision.

TBD-14 review outcome: testing ownership, protected-suite isolation, host coverage,
bounded cases, models/routes/effort, budgets, timeout settings and completion rules are
resolved as policy. Implementation and acceptance remain pending. Remaining gates are
actual dependency/adapter readiness (including native effort and cap fidelity), suite
fixture/proxy migration, coherent deployed artifacts, deterministic regression results,
account/route availability, conservative pricing preflight, separately authorized live
execution and complete evidence for every required cell. A failed or unavailable cell
is an open gate; changing scope, limits or expectations requires a deliberate decision.
The detailed TBD-14 policy remains settled. The earlier OpenRouter checklist-scope
clarification above remains separate and must not expand the initial matrix implicitly.

