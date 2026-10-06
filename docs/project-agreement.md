# Current project agreement

Consolidated 2026-10-04. Implementation was authorized on 2026-10-01.
This document records accepted direction; observed results belong in
[implementation status](implementation-status.md). Earlier decisions and proposals
are preserved in the [history archive](../archive/2026-10-04-before-muse-baseline/README.md).

## Purpose and scope

### Three-phase direction — agreed 2026-10-05

The user has clarified the intended progression and declared Phase 1 complete:

1. **Framework exploration (complete):** exercise Framework through realistic use
   to find and fix bugs and discover needed features and refinements. This was the
   primary first goal of the suite. Phase completion records that exploratory goal;
   it does not claim exhaustive feature coverage or release acceptance.
2. **Skill-level optimization (current):** explore different ways to compose, use
   and optimize skills so models below Sol's demonstrated capability can succeed.
   The focus now shifts to skill design and how work is distributed among skills,
   rather than continuing model comparisons on one fixed skill design alone.
3. **Long-term regression and release confidence (future):** stabilize the suite
   as a durable testing and regression system covering Framework features and
   behavior for release confidence.

Preserve Phase 1 evidence, frozen baselines and the historical Sol reference as
comparison anchors. Phase 2 experimental designs, model selections, success criteria
and execution budgets remain to be agreed; this transition does not itself select
or authorize a paid experiment. Phase 3 coverage and acceptance criteria are future
design work. Newly discovered Framework defects can still be recorded during Phase 2.

Demonstrate customer-facing Loomspan capabilities through two equivalent reference
microservices: Java embeds real Framework and uses deterministic `@SkillMethod`
operations; Python/FastAPI calls real Sidecar and supplies equivalent REST skills.
Both expose the same business API and use supported public integration mechanisms.
Compare business outcomes and evidence, not identical traces or request counts.

Keep the [Framework claims](loomspan-framework-claims.md) and
[Sidecar claims](loomspan-sidecar-claims.md) at customer-capability level. Detailed
contract checks support scenarios; they do not replace the claims with an exhaustive
API inventory. These are reference applications, with no custom business frontend.

The accepted first demonstration is equipment-service assessment and explicitly
approved request creation. Four model responsibilities coordinate evidence, assess
equipment, plan resolution and compare options. Independent reads may run concurrently;
dependent stages must receive the evidence they need. Comparison owns the decision;
native parent synthesis must preserve its result, authoritative quotes and constraints.

Assessment is asynchronous, separates execution status from business disposition,
and publishes an immutable version. New information starts a new assessment.
Creation is deterministic and binds the assessment, selected quote, attendance,
repair scope, cap and idempotency key to Luis's explicit approval. Persist approval
and request atomically. Same key/content returns the original receipt; different
content conflicts. Authorized lookup recovers a successful request after response
loss, including after its quote expires. The action ends at `PENDING_DISPATCH`.
Dispatch, technician findings and changed offers are fixtures, not an implemented
service lifecycle.

## Identity and independent evidence

Use Keycloak, Authorization Code with PKCE, separate user sessions, and the shared
`equipment-service` audience. Each receiving API verifies its token. Top-level
`roles` grant Maya `ASSESS_EQUIPMENT`; Luis also has `REQUEST_SERVICE`. Java/Sidecar
map these to `ROLE_` authorities. Site scope and Luis's approval ceiling come from
authoritative business records. Forward verified caller identity to downstream
operations; model fields cannot grant authority. Management credentials are separate.

Demonstrate direct denial and separately labeled controlled nested denial, with a
valid Luis positive control. Ordinary assessment never exposes request creation.
Combine actual Framework traces with independent fixture journals and durable
business records. Use independent expected outcomes, not the business implementation
under test, as the oracle. Preserve failures, source/configuration identities and
exact trace bytes; never include credentials in evidence.

## Fixed model-comparison baseline

The all-skill contract audit and common timeout increase are accepted normal changes,
not an opt-in GLM experiment. See [contract boundaries](input-contract-audit.md).
Keep prompts, schemas, scenarios, evaluator criteria, quotas and limits fixed across
models; record provider/model and reasoning differences. Do not add model-specific
compensation or worked case answers to skills or Framework guidance.

Both hosts currently use the installed PR 20 Framework beta.8-SNAPSHOT; record exact
artifact hashes and configuration for each run. Sidecar uses the separate beta.2
source export built against that Framework. A local snapshot is not a released
binary. Shared limits are provider 480s, mission 2400s and proxy upstream read 510s.
Normal model configuration is `meta/muse-spark-1.3-contributor`, medium reasoning.
Alternative models are explicitly selected through the runner.

Structural validation does not prove complete or unchanged source transfer, correct
citations, or sound business reasoning. Investigate generated prompts, handoffs,
feedback and framework behavior before attributing a failure to model strength.
Separate observed results from causal hypotheses; one run cannot establish reliability.
The previously accepted timezone/full-name expansion of site-access wording remains
a semantic non-failure; historical exact-text check results stay intact.

The explicit current comparison identity is [post-pr20-20261004](post-pr20-baseline.md).
PR 19.1 runs are historical and cannot substitute for fresh post-PR-20 comparisons.

## Accepted fresh baseline and cleanup

The user approved a fresh Muse baseline and priority run on both integrations, a
business-semantic review, and replay refresh plus full mock acceptance only if the
captures are suitable. Muse does not define the expected answer. An exact persisted
quote ID is a valid citation; unknown or foreign quote IDs remain invalid. This
evaluator correction is explicit and historical reports are not rewritten. Sequencing
checks also respect Framework joining each execution unit before the next; identifier-
only reads need not invent data dependencies to prove an ordering already guaranteed.
Receiving skills still need explicit dependencies on results they actually consume.

Consolidate active documentation and archive superseded experiments and checkpoint
narratives. Retain original captures, regression sources, checksums and replay
provenance. Preserve durable records and runtime state before recreation. Do not
promote unsuitable captures or rewrite old outputs to make current contracts pass.

The user also authorized storage cleanup on 2026-10-04. Reclaim space while keeping
active services, databases and referenced evidence intact. Lossless filesystem
compression preserves evidence bytes and original paths; verify retained evidence
against pre-cleanup hashes. Unused Docker build cache older than a week may be
removed; active images, containers, volumes and current build packages are retained.

The bounded post-PR-20 cleanup is authorized: consolidate the starting document,
baseline and results table; inventory dependencies before verified disposable or
redundant deletion. Preserve source work, runtime, referenced captures and recovery
provenance. Use `scripts/run_suite.py` as the supported evaluation entry point.
This cleanup authorizes no paid runs, replay refresh, Framework pipeline, commit,
push or release. See the [retention record](cleanup-retention.md). Fresh Muse/GLM
comparisons followed by two additional Java models and selected Sidecar confirmation
are the recommended next sequence, not observed results.

## Execution and delivery boundary

The user approved a Framework ticket, PR 20, for explicit `output_from: {skill: ...}`
on planning skills: forward the unique required direct child's result after required
work succeeds, without parent synthesis or duplicate output validation. Model, Java
and REST children are supported by the proposed contract. Derive effective schema
metadata when available; an unspecified child schema stays unspecified. Update the
Framework skill documentation library with general authoring guidance. The user
subsequently reported PR 20 completed and Maven-installed, and authorized using it
here. Update only `planResolution` to forward `compareOptions`, retaining the outer
`resolveEquipment` synthesis to isolate the change. Rebuild both hosts, keep model,
business inputs and limits unchanged, and verify exact result forwarding and absence
of parent synthesis/duplicate validation on the priority scenario. Preserve earlier
captures as the previous baseline and distinguish feature verification from business
judgment. See [current results](implementation-status.md) for observed status.

Use Docker Compose only; Windows/Python runs the harness. Provider access is disabled
outside authorized live runs. Mock mode makes no paid calls; live/evaluate/capture
modes use the selected live model without fallback. Capture is not replay approval.
Refresh requires bound semantic review and complete mock validation before activation.

First delivery requires both equivalent applications, baseline and priority scenarios,
approval/recovery, malformed-output recovery, gated case isolation and nested
authorization, with reviewed model-derived ordinary replay and real traces. Controlled
faults are labeled separately; genuine model correction provenance must remain honest.

Publication under load, fifty-execution capacity experiments, broader restart/overload/
shutdown coverage, polished reporting and CI remain later work. A separate on-prem
Compose setup was selected instead of the earlier VM proposal; historical setup
results do not establish acceptance of subsequently changed contracts or artifacts.
No publication, release or Git push is authorized by this task.

## Superseding evidence-retention decision — 2026-10-04

The user explicitly classified older run data as disposable and authorized deleting
all old run evidence and export bundles, replacing them with the forthcoming fresh
Muse and GLM baselines. This supersedes the earlier requirement to preserve historical
captures, replay provenance and recovery bundles. Keep current source/configuration,
installed packages, active databases and credentials. Historical evidence-dependent
replay/audit checks will be unavailable after deletion; do not weaken their criteria
or claim historical/full mock acceptance. Fresh baselines have not yet been run.

The measured reset target is the repository `evidence/` directory: approximately
16.02 GB allocated. Execution policy blocked deletion despite explicit user
authorization; no evidence was removed. [Reset inventory and status](evidence-reset-20261004.json)
records the boundary and blocker. This decision does not authorize deletion of the
Docker virtual disk, runtime databases or source work, or start paid evaluations.

## Fresh comparison authorization — 2026-10-04

The user confirmed the old evidence was removed and requested fresh GLM and Muse
baselines. Run `evaluate` sequentially on Java, following the agreed Java-first
comparison sequence, with `z-ai/glm-5.3-flash` and
`meta/muse-spark-1.3-contributor`, medium reasoning. Keep the post-PR-20 source,
contracts, evaluator and limits unchanged. Include baseline, changed priority and
eligible deterministic service follow-up; inspect business semantics separately.
Restore provider-disabled runtime afterward. No replay refresh, release or commit
is implied. Historical preservation and deletion-blocker statements above now
refer to the period before the user's manual cleanup.

## Sol comparison reference — 2026-10-04

The user authorized one Sol 6.1 / medium evaluation on embedded Java only and
selected its retained result as the reference for subsequent model comparisons.
Use `openai/gpt-6.1-sol` with the existing evaluate entry point, including baseline,
changed priority and eligible service follow-up. Do not repeat on Sidecar just to
establish this reference. Keep PR 20 artifacts, contracts, evaluator and limits fixed.
Save actual outcomes, cost and semantic review, including shortcomings if any.
The reference is an empirical comparator, not an oracle replacing independent
business expectations and not automatic replay approval. No fixture activation,
commit, push or release is implied.

## Additional model comparisons — 2026-10-04

The user chose to test two or three more models before replay migration, starting
with `z-ai/glm-5.3` (non-Flash). Run this model through OpenRouter on embedded Java
with medium reasoning and the unchanged post-PR-20 baseline, including baseline,
priority and eligible deterministic service follow-up. Retain Sol as the comparison
reference and review business judgment independently. Other model identities remain
to be selected. Restore provider-disabled services after each authorized evaluation.

The user next selected `openai/gpt-6-luna`. Evaluate it once through OpenRouter on
embedded Java with medium reasoning, using the same baseline/priority/service scope
and fixed contracts, evaluator and limits. Sol remains the comparison reference.

The user selected `deepseek/deepseek-v4.1-flash` as the next comparison. Run once
through OpenRouter on embedded Java at medium reasoning, with the same frozen
baseline, priority and eligible service checks. Preserve Sol as the reference.

The user additionally selected `deepseek/deepseek-pro-latest` for one Java evaluation
at medium reasoning through OpenRouter under the same fixed conditions. The leading
tilde in the request is treated as punctuation. Record the returned model identity
because the requested identifier is a latest alias; do not substitute another model.

The user corrected the identifier: the leading tilde is intentional. Retry exactly
`~deepseek/deepseek-pro-latest` under the same Java/medium conditions. This supersedes
the earlier interpretation that the tilde was punctuation.

The user selected one last comparison: `xiaomi/mimo-v2.6-pro` through OpenRouter
on embedded Java at medium reasoning, with the unchanged post-PR-20 baseline,
priority and eligible service follow-up. Run once, preserve Sol as the reference,
and restore provider-disabled services. Review the completed comparison set before
any further paid work; replay migration remains separate.


## PR 21 adoption and first comparison — 2026-10-05

The user reports PR 21 completed and Maven-installed, and authorizes adopting its
child input bindings in both equivalent host configurations. Preserve the PR 20
frozen identity, source snapshot, original captures and Sol reference as the previous
baseline. Create a distinct PR 21 identity. Bind authoritative inputs at assessment,
resolution and comparison boundaries, including identifier-only lookup arguments.
Keep receiving schemas, business facts, assessment/comparison prompts, evaluator
criteria and limits unchanged. Adjust orchestration instructions only for bound
arguments and required direct dependencies. Retain outer synthesis and existing
planResolution output_from forwarding to isolate input binding adoption.

The selected candidates are non-Flash GLM-5.3, MiMo V2.6 Pro and Luna, medium reasoning
on Java. The user's subsequent sequencing instruction takes precedence: run only
z-ai/glm-5.3 first, once through the supported evaluate entry point, including baseline,
changed priority and eligible deterministic service follow-up. Discuss results before
running MiMo or Luna. Restore provider-disabled services afterward. Feature fidelity
and business judgment remain separate; one run does not establish reliability or
causal improvement. No replay refresh, commit, push, Framework pipeline or release.


## Luna on PR 21 — 2026-10-05

After reviewing GLM, the user authorized one `openai/gpt-6-luna` Java evaluation
at medium reasoning on the unchanged PR 21 binding baseline, including baseline,
priority and eligible deterministic service follow-up. Compare source transfer and
business judgment separately with retained Luna and Sol results. Restore provider-
disabled services afterward. MiMo remains unrun pending further direction. No replay
refresh, commit, push or release is implied.


## MiMo on PR 21 - 2026-10-05

After reviewing Luna, the user authorized one `xiaomi/mimo-v2.6-pro` Java evaluation
at medium reasoning on the unchanged PR 21 binding baseline, including baseline,
priority and eligible deterministic service follow-up. Compare evidence transfer,
completion and business judgment with retained MiMo and Sol evidence. Restore
provider-disabled services afterward. No replay refresh, behavior changes, commit,
push or release is implied.


## GLM Flash on PR21 - 2026-10-05

The user authorized one `z-ai/glm-5.3-flash` evaluation on embedded Java at medium
reasoning, using the unchanged PR21 baseline, priority and eligible service scope.
Compare with retained GLM Flash and Sol evidence; preserve original captures and
evaluator criteria. Restore provider-disabled runtime. No behavior change, replay
refresh, commit, push or release is implied.


## Two DeepSeek models on PR21 - 2026-10-05

The user authorized one evaluation each of `deepseek/deepseek-v4.1-flash` and the
exact `~deepseek/deepseek-pro-latest` alias, sequentially on Java at medium reasoning.
Keep the PR21 baseline, scenarios, evaluator and limits unchanged; include eligible
service follow-up and record returned model identity for the alias. Compare evidence
and business judgment with retained DeepSeek and Sol runs. Restore provider-disabled
services after each suite. No replay refresh, behavior change, commit, push or release.


## Output binding design direction - 2026-10-05

The user wants proposed output bindings to logically match existing input bindings
as closely as possible for human comprehension. Reuse existing terminology and
source-selection concepts rather than introducing a different binding notation.
The current input syntax maps destination JSON Pointers to source descriptors with
`from`, `path`, and `skill` when selecting a child result. A matching top-level
`output_bindings` map is the proposed syntax, not an implemented or finalized API.
Exact assembly rules, interaction with `output_from`, mixed model/framework output
and validation behavior remain design work. This discussion does not authorize
runtime changes, paid evaluations, replay refresh, commit, push or release.


## Output binding ticket - 2026-10-05

The user accepted declared output bindings matching the input-binding map syntax
and confirmed that `output_bindings` and `output_from` must be mutually exclusive,
with a configuration validation error when both are declared. Existing forwarding
and ordinary model-generated output remain available. The user requested the
Framework ticket using proposed PR number 22. It is saved at
`C:/opendev/code/loomspan-framework/ai/thoughts/tickets/loomspan-pr-22-declared-output-bindings.md`
using that repository write-ticket command. It specifies full and mixed assembly
and recommends the Full 5-Step Pipeline; the pipeline was not started. No runtime
changes, paid evaluations, commit, push or release were performed for this ticket.


## PR 22/23 adoption and Luna first — 2026-10-05

The user reports PR 22/23 implemented and Maven-installed, and authorizes adopting
output bindings and comparing Luna first on Java at medium reasoning. Bind
compareOptions identifiers, issued quotes and accepted assessment from its input.
Assemble resolveEquipment's existing output shape from its input identifiers,
assessEquipment and planResolution, with no root final model synthesis. Keep
planResolution output_from compareOptions. Both hosts use the same declarations.
Keep business schemas, scenarios, limits and decision criteria unchanged. Adapt
evaluator mechanics to verify accepted assembled results and provenance, retaining
legacy review paths and all original evidence. Preserve PR20/PR21 frozen baselines
and Sol's historical reference; record a distinct PR23 baseline. The shared PR23
validation policy treats schema format as guidance, not coercion. Run one Luna
baseline/priority evaluation and eligible service follow-up; restore provider-disabled
runtime. No other paid models, replay refresh, commit, push or release are implied.


## MiMo on PR22/23 - 2026-10-05

The user authorized one `xiaomi/mimo-v2.6-pro` Java evaluation at medium
reasoning using the current PR22/23 contracts and evaluator, including baseline,
priority and eligible deterministic service follow-up. Compare with retained PR21
MiMo evidence, separating Framework behavior, exact preservation and business
reasoning. Preserve existing uncommitted work and frozen evidence. Restore
provider-disabled runtime afterward. No replay refresh, commit, push or release.


## PR24/25 adoption without paid evaluation - 2026-10-05

The user reports PR24 and PR25 complete and Maven-installed and authorizes adoption:
preserve PR22/23 source/artifact/evidence identity, rebuild both equivalent hosts,
and verify automatic fully bound dispatch and contract-specific argument guidance
offline. Keep business contracts, scenarios, model defaults, evaluator criteria and
limits unchanged. Isolated controlled diagnostic response reuse is feature verification,
not replay refresh or semantic acceptance. Record a distinct PR25 baseline and leave
normal runtime provider-disabled. No paid model evaluation, replay promotion, commit,
push or release is authorized. Sol remains the historical comparison reference.


## Luna live verification on PR24/25 - 2026-10-05

The user authorized one `openai/gpt-6-luna` Java/medium evaluation on the unchanged
PR24/25 baseline, including baseline, priority and eligible deterministic service
follow-up. Compare with retained PR23 Luna evidence: direct-dispatch counts, exact
input/output preservation, actual usage/cost/timing and independent business review.
Seven calls per scenario is an expectation only when no corrections occur; historical
cost footprints are not guaranteed savings. Restore provider-disabled runtime afterward.
No Sol run, Sidecar paid evaluation, replay refresh, commit, push or release is authorized.

Observed: the authorized Luna evaluation completed with 67/67 checks in each
scenario and 33/33 service checks. Eight direct dispatches and seven model calls per
scenario preserve all 43 input/18 output bindings. Total reported cost falls 32.02%
versus PR23 Luna; total trace time rises 2.08% in this sample. Both outputs omit an
explicit technician-overrun access plan; no replay approval. Runtime restored ready
and provider-disabled. [Evidence](../evidence/pr25-luna-20261005/summary.md). No further
paid runs or behavior changes were authorized by this verification.

## Sol then MiMo PR24/25 verification - 2026-10-05

The user now authorizes one Java/medium evaluation each of `openai/gpt-6.1-sol`
and `xiaomi/mimo-v2.6-pro`, in that order, on the unchanged PR25 baseline.
Each includes baseline, priority and eligible deterministic service follow-up.
Compare framework/model friction, direct dispatch, exact preservation, independent
business reasoning, reported cost and trace duration. Sol's retained PR20 reference
includes earlier contract differences; MiMo's PR23 run is the closer PR24/25
comparison. Neither comparison alone isolates causality or establishes reliability.
Preserve existing work, frozen evidence and the historical Sol reference. Restore
provider-disabled runtime after each suite. No additional paid runs, replay refresh,
commit, push or release are authorized.

Observed: both authorized evaluations completed with seven model calls and eight
direct dispatches per scenario, exact 43 input/18 output bindings and no corrections.
Sol passes 67/67 both; MiMo priority original 63/67 is a fenced-plan reviewer mismatch,
separately verified 67/67 against the accepted trace plan. Both service suites pass
33/33. Sol retains material business distinctions; MiMo still has business-advice gaps.
No replay approval or historical reference replacement. Both runtimes restored ready
and provider-disabled. [Full results](../evidence/pr25-sol-mimo-20261005/summary.md).
