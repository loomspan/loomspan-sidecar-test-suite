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
