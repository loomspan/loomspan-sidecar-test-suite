# Project agreement

Updated 2026-10-11. Phases 1 and 2 are complete; Phase 3 remains future work.

## Destination

Retain a coherent equipment-service process understandable to a business practitioner,
with equivalent embedded Java Framework and Python/FastAPI plus Sidecar applications.
The selected pack uses Sol/medium for technical assessment, all four option-feasibility
skills and comparison; Luna/medium coordinates resolveEquipment and planResolution.
These assignments are now the authored runtime configuration, not temporary overrides.

Two unchanged four-case Java batches passed business review with minor caveats.
See [Phase 2 summary](phase2-summary.md) for the bounded evidence and limitations.
No claim is made that this is the globally cheapest assignment or a production-certified
workflow. Keep stronger models where the responsibility needs them; pursue further
cost optimization only for a specific worthwhile opportunity. Include authoring time,
review, maintenance and fragility alongside model spend. No arbitrary effort budget
is imposed, but further tuning or paid runs do not follow automatically.

## Human business contract

The user originally authorized switching the maintained runtime to Sidecar `1.0.0-beta.3`
with Loomspan Framework `1.0.0-beta.8`; the TypeSafe direction below supersedes that
Framework version with the pinned beta.9 snapshot. Build from the pinned source,
update both integrations and verify locally with provider-free checks and frozen
reference replay. Preserve credentials, operational data, skills and model assignments.
This dependency update authorizes no paid evaluation, commit, push or release.

Responsibilities, decisions and handoffs must represent a sensible business process.
Methods, schemas and interfaces can change at any justified scale; a frozen trial is
an experimental control, not a permanent ban on improvement. Do not fragment the
process or add fixture-specific answers merely to make a weaker model pass.

Use lower-tier models where they reliably suffice. A stronger whole-tree baseline can
support later substitutions, but a demonstrated skill-specific reasoning or specialist
capability need can justify mixed assignment directly. No fixed stronger-call percentage
or mandatory whole-tree upgrade is required. Separate observations, promising practices
and hypotheses, and maintain the [design guide](mid-tier-skill-design.md).

## Business and execution boundaries

Assessment produces an immutable recommendation, not a commitment. Service request
creation verifies caller identity, role, site scope, spending authority, explicit
attendance/scope/cap approval and idempotency. It ends at PENDING_DISPATCH, not booking,
repair completion or clearance. Directory contacts do not grant permissions.
Loaner and replacement procurement remain external to the service-request workflow.
Keep independent business facts and Java/Sidecar behavior equivalent.

Use documented runtime helpers; normal provider access stays disabled. Agree concrete
scope before every paid experiment. No paid Sidecar, further evaluation, commit, push,
release or Phase 3 implementation is authorized by cleanup or documentation changes.

## Retention and next work

The user authorized a Phase 2 cleanup comparable to Phase 1: retain the working runtime,
current skills and useful validation tools; retire historical captures/results (including
old accepted samples), traces, experimental variations, synthetic test records and
one-off helpers. A verified recovery snapshot is outside the active repository.
Local credentials and build prerequisites are retained. Current summary and lessons
replace chronological experiment conversations in maintained documentation. Repository
cleanup does not delete this chat or rewrite Git history.

The small current runner, provider-free tests and smoke check are maintained tools,
not historical results. Keep observability available for future diagnosis without
requiring retired captures. Do not reconstruct Phase 1/2 archives as prerequisites.
Phase 3 will define durable regression and release-confidence scope. Additional mid-level
examples remain a future way to test transfer and authoring effort.

## Frozen reference replay

The user subsequently requested retaining the successful Sol/Luna responses as a
deterministic LLM for continued testing. Recover only the final accepted four-case
batch from the verified Phase 2 backup and maintain its compact fixtures under
`fixtures/reference`. These are current test assets, exempt from historical-result
cleanup. Keep their acceptance caveats and provenance; do not restore experiment history.

`run_suite.py mock` exercises the real Java and Sidecar integrations with those frozen
responses and provider access disabled. Changed business inputs, contracts or handoffs
must fail instead of silently selecting a canned answer or calling a provider. Replay
tests runtime behavior and preservation of the accepted reference, not current model
quality, general business reliability or full service-request regression. This work
authorizes no new paid evaluation, commit or push.

## Named integration suites

The user approved organizing this workspace into named integration suites, each also
serving as a readable user example, within the existing Java and Python/Sidecar apps.
The retained process is `equipment-service`; baseline, priority, capacity_shortfall
and later_start remain scenarios within it. This is an organization and runner change,
not Phase 3 release acceptance or authorization to create a second business example.

Keep shared skills and Sidecar REST declarations in parallel suite directories. Java
packages and Python modules separate suite APIs, Loomspan callbacks, result handling
and business rules from shared host infrastructure. Existing skill names, model
assignments and HTTP endpoints remain compatible; new suite routes use explicit prefixes.
Skill names are global runtime identities, not directory-local namespaces. New suites
must use distinct names; detect configuration collisions before startup.

The runner selects named suites or all, validates mode/scenario support, and writes
per-suite evidence with a top-level summary. Shared orchestration owns runtime restoration
and the workspace lock. Keep equipment fixtures at their existing paths, including the
unchanged frozen `fixtures/reference` pack; the suite catalog records their ownership.
See [suite boundaries](suites.md) for the extension contract. No paid evaluation,
commit, push or release is authorized by this restructuring.

## TypeSafe integration suite direction

On 2026-10-11 the user accepted a second suite, `typesafe-ai`, using customer-support
intake and triage as the cohesive example. Cover Choice, Noul and Score individually
and in mixed batches; fixed/dynamic criteria, structured instructions, input substitution,
direct/child invocation, forwarding, receiving output bindings and failure/fidelity cases.
Preserve the distinction between native answer passthrough and validation by a consuming
contract. Assessments inform application-owned decisions; they do not perform customer actions.

Use the Framework `1.0.0-beta.9-SNAPSHOT` source under evaluation, record revision and
artifact hashes, and align Java and Sidecar with the same Framework bytes. Both hosts
have now been rebuilt and started with that snapshot. Equipment-service replay must
continue to pass after the change; retain its original accepted fixture pack.

Pin direct TypeSafe to `jev-1.13.0`, the current stable version listed at
https://docs.typesafe.ai/models when checked on 2026-10-11. Do not use a moving latest
or preview alias. Reference `LOOMSPAN_TYPESAFE_API_KEY` privately for an authorized
live run. Start with deterministic System One transport fixtures; distinguish authored
protocol fixtures from subsequently captured and reviewed real responses. Agree a concrete
live scope before paid calls. Existing frozen equipment fixtures remain unchanged.

The user authorized project-local authoring guidance. Installed copies under
`.agents/skills` contain `loomspan`, `loomspan-docs`, `loomspan-console` from the pinned
Framework source and the official `typesafe-ai` skill. `skills-lock.json` records their
origins and hashes. The neighboring Sidecar skill still targets Framework beta.8, so it
was not installed as snapshot-aligned guidance. These are authoring aids, separate from
the runtime skill trees under `config/skills`.

`config/runtime-source.json` pins Framework commit
`3265354b6c4975c8ae82ac9f111eff0ffcf77b9d`. Keep Sidecar beta.3 source and rebuild it with
an explicit Framework dependency override; this combination is under integration test,
not an upstream Sidecar release. The initial TypeSafe suite supported mock only.
Live/capture support and a reviewed real-provider response pack were initially deferred.

## First TypeSafe live batch

The user approved the proposed first live batch on 2026-10-11: six direct native cases
on each host, at most 12 TypeSafe requests total, pinned to `jev-1.13.0`, retries disabled,
and stop on an unexpected execution/transport/contract failure. No paid chat planning or
parent runs are included. Use `LOOMSPAN_TYPESAFE_API_KEY` privately and restore the
provider-disabled runtime afterward. This authorization does not imply automatic repeats,
another batch, commit, push or release.

`fixtures/typesafe-ai/live-cases.json` records expectations before sending: individual
Choice/Noul/Score, fixed mixed questions, dynamic criteria and structured instructions,
including ambiguous and incomplete contacts. Provisional semantic ranges flag issues for
review; they are not calibrated thresholds or automatic acceptance. Capture real responses
separately, review them with the user, and promote only agreed results to a separate
accepted replay pack. Existing synthetic protocol and accepted equipment fixtures stay intact.

The authorized batch completed: 12 sends total, with an assertion-boundary correction
and continuation using only five unused permits after the initial seven sends. Original
and combined evidence are preserved. All mechanical checks and 24 offline replays of
the captured responses passed. See the TypeSafe suite guide for the assistant's review;
the incomplete-contact severity remains a caveat. User agreement and promotion to an
accepted real-response pack are still pending. No additional paid batch is authorized.

## Delegated TypeSafe review and further evaluation

The user subsequently delegated semantic acceptance to the assistant and explicitly
authorized as many TypeSafe calls as useful to resolve the examples. This supersedes
the first batch's per-batch approval and pending-human-review restrictions. The
assistant will record its judgments, preserve disagreements and limits, and freeze
the responses it accepts separately from diagnostic captures. Continue using the
pinned model, exact-request permits, bounded batches and provider-disabled restoration;
this authorization covers native TypeSafe on both hosts, not paid chat planning.
No commit, push or release is implied. The next experiment tests evidence sufficiency
against six predeclared contrasting contacts on both hosts (12 calls).

That experiment and six additional holdout contacts completed with 24 further sends,
zero retries/chat calls and 288 mechanical checks. The assistant accepted the first
five original contacts and the 12 new evidence contacts, with question-level limits
and four preserved provisional-range misses. The resulting 34 recorded responses are
maintained in `fixtures/typesafe-ai/reference` and included in the normal native mock
suite. The two original sparse-contact responses remain diagnostic, not accepted.
Unknown-impact scores in the new examples are retained for fidelity only and explicitly
excluded from semantic acceptance. See `review.json` for exact reasons and source hashes.

## Application decisions and composition

The user approved adding equivalent Java/Python impact-decision policies, exercising
parent forwarding and output bindings with the captured real responses, then a focused
live evaluation. Keep raw results intact and expose a separate decision view with an
explicit configurable evidence threshold (default 0.80), returning an impact assessment
or NEEDS_CLARIFICATION. Invalid required judgments must not become asserted impact.
Use existing accepted captures unchanged for deterministic parent tests; chat planning
stays local. Predeclare fresh contacts covering incomplete information, conflicting
reports, history/current distinctions and ambiguous routing before native live calls.
Evaluate incorrect assessments separately from unnecessary clarification. The standing
TypeSafe authorization applies; use batches of at most 12 physical sends and restore
provider-disabled operation. No paid chat, customer action, commit or release is included.

Implementation and verification completed: both hosts expose the separate owner-only
execution `/impact` view; raw results stay intact. Fourteen derived recorded-response
composition scenarios and 15 authored consumer-policy scenarios join the existing
native replay catalog. The full grouped replay passed 232 executions; Java and Python
policy tests passed. Six fresh policy contacts plus two routing contacts used 16 native
sends. Policy outcomes were four correct assessments, six correct clarifications,
and two unnecessary clarifications of one regional outage, with no unsupported
assessment or incorrect exposed impact in this sample. Routing judgments were accepted.
Keep the 0.80 default and preserve the regional miss; multi-site scope is a candidate
for a separately predeclared question-design experiment. Provider access was restored
to disabled and all existing accepted references were preserved.

## SDK v1 integration direction (2026-10-18)

The reconciled Sidecar SDK plans in the neighboring Sidecar repository's
`ai/thoughts/phases/2026-10-11-java-spring-sdk-roadmap.md` define this new work.
This SDK effort has its own Phase 1 implementation/integration and Phase 2 completion
verification; those names do not reopen this suite's completed business phases.
SDK coverage is delivered incrementally by the linked Sidecar tickets; see
[SDK lane](sdk-lane.md) for the current executable scenarios and evidence limits.

Use the simplest implementation and proportional tests. Replace superseded SDK
contracts and fixtures directly, without compatibility machinery; apply Sidecar's
`ai/thoughts/design-lens.md#simplicity-and-technical-debt`. No data reset is required
by this agreement update. Preserve existing credentials, operational data, business
examples, the beta.9 embedded and Python/Sidecar lane, and all maintained reference
packs including `fixtures/reference`. Do not reconstruct discarded SDK work.

Add a separate SDK lane against the actual Sidecar revision and its pinned Framework
beta.8 dependency. Establish a small harness foundation early, then provide each
feature's necessary composed coverage with that feature. Tickets may reuse or extend
existing scenarios; one scenario can satisfy several tickets. Keep detailed rule
variants in component tests, adding a composed scenario only for behavior existing
scenarios cannot demonstrate. This retains the three recipes and meaningful failure
cases without requiring a new integration scenario per ticket.
All future ticket artifacts belong in the
Sidecar repository; no tickets are created by this reconciliation.

Build three real recipes: Local localhost HTTP, Standard direct HTTPS and Hardened
Caddy-managed mTLS in both directions. Test invocation, callbacks, JWT/user
permissions and relevant transport rejection. The hardened reference uses app/Caddy
and Sidecar/Caddy shared network namespaces, loopback backend/outbound listeners,
fixed proxy destinations and separate browser ingress. Verify no external bypass.
Other compositions remain permitted and untested, not unsupported or experimental;
do not build a configuration cross-product or runtime recipe allowlist. Include
focused no-callback coverage rather than duplicating every security test.

If apps share a Sidecar, they trust each other in every way. A group shares signing
identity, issuer, callback audience, user directory and exact role vocabulary.
Use a small second application in one recipe to exercise that arrangement, not
independent app issuers or an isolation matrix. Spring-issued and trusted custom
identity feed the same execution issuer. SDK authenticates callbacks; application
method annotations/business checks authorize them. Test documented callback prefix
and chain ordering in reference apps, not arbitrary Spring matcher analysis.

Use colocated/provided signing and current-file JWKS trust. Test missing/invalid/
empty trust stopping acceptance, correction recovering it, same-issuer key rotation,
colocated restart, queued-token current-trust/expiry checks and callback expiry.
Provided private signing keys load at application startup only; replacing them
requires restarting affected applications. Exercise that restart in the existing
rotation scenario, with public JWKS trust still reloading independently. No
private-key hot-reload or uninterrupted-rotation tests are required.
Relevant future tickets explicitly keep JWKS file sourcing in both file/database
application configuration modes; do not add a database trust store or management API.
Existing management accounts/tokens remain unchanged.

The SDK client is blocking only. Each request is sent once; bounded wait polls
successful status responses and stops on a failed read. Lost/unusable submission
responses mean acceptance unknown, never automatic resubmission. Use simple attempt
and synthetic-effect counters for response-loss/no-replay coverage. No custom futures,
retry/backoff or proxy-origin classification system, business ledger, transactional
deduplication or crash-recovery fixture is required.

DevOps owns TLS certificate lifecycle using standard Spring Boot and Caddy facilities.
Generate temporary certificates for transport integration positives/negatives; do not
add certificate renewal/replacement/rollover/revocation-propagation or live-reload
tests, a CA service, or committed certificate material. JWT signing/trust lifecycle
remains a separate test responsibility.

Use deterministic model fixtures and form login; no provider calls or separate login
provider deployment. Keep the runner small, readable and formatted. The canonical
Sidecar acceptance matrix owns the bounded test inventory. Completion includes builds,
consumer packaging, integration, documentation and independent security review; no
release/version/publication decisions, commit or push are authorized by this work.


### Deployment verification ownership (2026-10-18)

The Sidecar simplification ticket restores the plain-Java Local fixture using
public JWKS/current execution JWT claims and application-port 8080 readiness.
The same SDK runner also owns `deployment-transport-baseline`,
`shutdown-completion` and `shutdown-cutoff`; see [SDK lane](sdk-lane.md) for evidence
and limits. No certificate-lifecycle tests are moved here. These baselines do not
complete the future form-login/reference-app callback or full Standard/Hardened
recipes in Sidecar PRs 8.1.5–8.1.8. Empty recipe selectors continue to fail explicitly.
One root Sidecar component build remains per SDK run; no recursive smoke or suite
invocation is introduced. Business-lane configuration/data/reference packs remain
outside this isolated SDK lane, and no development-data reset is required.
