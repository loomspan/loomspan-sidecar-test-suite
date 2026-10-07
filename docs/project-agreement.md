# Project agreement

Current direction agreed 2026-10-06, clarified 2026-10-07.

## Demanding reference example and transfer — agreed 2026-10-07

Continue investing in the equipment-service example as a demanding reference case.
Do not impose an arbitrary authoring-effort budget or pause this example merely
because it requires substantial work. The objective is repeatable complete-business
success while preserving a process a human practitioner would recognize. One passing
batch is insufficient; the concrete confirmation scope remains to be agreed.

Judge progress both by business correctness and by transferable design lessons.
Distinguish reusable Framework improvements, general skill-authoring practices and
domain-specific requirements. Larger changes to responsibilities, evidence flow or
interfaces are welcome when business-justified. Avoid accumulating scenario-specific
reminders merely to make the fixed cases pass.

Once repeatable success is demonstrated, freeze this example as a reference and
develop several mid-level examples to test whether the lessons reduce subsequent
authoring and maintenance effort. Measure that effort without setting an arbitrary
limit. The present investment does not establish that ordinary practitioners should
need comparable effort, or that the approach already generalizes economically.

The next step is provider-free review of the quote/comparison boundary: examine the
authoritative price breakdown a human reviewer would expect and the distinction
between information absent from a local assessment and information absent from the
underlying evidence. This is an investigation direction, not a demonstrated remedy.
Paid experiments still require agreed concrete scope; this direction authorizes no
new paid run, accepted-evidence promotion, commit or push. Preserve Java/Sidecar
equivalence and disabled provider access.

## Current model-selection priorities

These priorities supersede the earlier default of upgrading individual skills
first or pursuing an all-Luna result through continued decomposition. Targeted
mixed-tier assignment remains explicitly available under priority 4.

1. Start with a competently authored, human-recognizable skill and its complete
   tree. Out of the box, find the lowest reasonable general-purpose model tier
   that passes the full end-to-end business evaluation. Start with reasonable
   candidates and move upward when needed; do not exhaust implausibly weak models
   or repeatedly reshape the process around one failing model. User examples of
   the lower candidate range are Luna, GLM and Mimo; Sol or Astra can be the upper
   end if needed. Intermediate candidates may emerge, such as the user-mentioned
   Muse Spark Contributor. These are illustrative candidates, not a verified
   current ranking, availability list, or permanent ladder.
2. If the lowest successful whole-tree model is relatively high tier, preserve
   that working baseline and find which coherent business responsibilities can
   use lower-tier models. Measure full-workflow correctness as well as cost,
   latency and correction burden. The resulting allocation is discovered; no
   fixed target percentage is imposed.
3. If a reasonable lower-tier model already passes the complete workflow, keep
   that simpler assignment. Mixed-tier orchestration is unnecessary unless it
   serves an evidenced requirement. Confirm reliability before treating a single
   successful sample as an established baseline.
4. A skill-specific capability requirement can justify a mixed pack: use a
   higher-tier general-purpose model only for the skills that need its stronger
   reasoning, while retaining lower-tier models for the remaining skills where
   they suffice. This exception is not limited to specialist model types. It also
   includes vision, unusually low latency/high speed, and specialized models
   (the user cited typescript.ai as an example). Explain the requirement for each
   assignment and evaluate the complete process, including all model handoffs.
   Verify actual capabilities and available model IDs when defining an experiment.

Mixed-tier packs are explicitly supported by both priorities 2 and 4. Priority 2
is optimization from a successful higher-tier whole-tree baseline; priority 4
permits targeted assignment when a particular skill's capability requirement is
already established. Neither requires promoting the entire tree because one skill
needs a stronger model. Use higher tiers only where the responsibility needs them,
and validate the resulting complete workflow. Do not add artificial skill boundaries
solely to minimize the percentage of higher-tier calls.

A pass includes execution, faithful data transport and reviewed business outcomes
across the agreed cases; structural checks alone are insufficient. Out of the box
means the readable authored baseline before model-specific compensating rewrites,
not an absence of schemas, tools, clear instructions or business rules. Human
recognizability is a design requirement throughout all four priorities. The initial
audit was documentation/design review; the subsequently authorized readable
baseline is now implemented with provider-free validation only. No new paid run
or model assignment is implied.
See [the current process audit](foundation.md#human-business-contract-audit).

## Phases

1. **Framework exploration — complete.** Exercise realistic workflows, uncover
   bugs and identify useful Framework features and refinements.
2. **Business-readable skills and model assignment — current.** Establish a
   recognizable business process, find the lowest reasonable model tier that can
   pass its full workflow, then optimize mixed-tier allocation if needed, with
   targeted capability-based mixed packs also allowed under priority 4.
3. **Regression and release confidence — future.** Stabilize a durable testing
   system covering Framework features and behavior. Coverage and acceptance criteria
   remain to be designed.

The user authorized a deep Phase 1 cleanup, retaining both apps with all current
skills/configuration as the Phase 2 foundation. Old tests, reports, copied baselines,
replay captures and investigation history are retired from the active project after
an external recoverable snapshot. The two Phase 1 summaries replace that history.
Sol's historical reference designation is retired; no previous model is the oracle
for future experiments.

## Foundation and business boundary

Java embeds real Framework and exposes deterministic SkillMethods. Python/FastAPI
uses real Sidecar and equivalent REST skills. Both demonstrate the same equipment
assessment and explicit approval-bound service-request process. Compare justified
business outcomes, not identical wording or model call counts.

Assessment produces a persisted, immutable recommendation. It creates no service
commitment. Request creation validates a selected assessment/quote, caller identity,
site scope, spending authority, explicit scope/cap approval and idempotency. It ends
at PENDING_DISPATCH, not booking, repair completion or technical clearance.

Keycloak supplies separate user identities through Authorization Code with PKCE.
Maya may assess; Luis may also request service. Contact records and model-authored
fields do not grant authority. Loaner procurement is outside the implemented service
request workflow. Preserve the independent business source facts and authorization
boundary when designing experiments.

## Working boundaries

Keep current apps, skills/configuration and fixtures as the initial Phase 2 starting
point. The cleanup itself makes no skill optimization or model-default change.
The initial experiment is described below; further designs, success criteria and
paid-run budgets remain to be agreed.
Explicit authorization is required for paid runs. Normal provider access stays disabled.
Do not embed the answer to a fixed example as a substitute for a general skill method.

Separate execution/transport fidelity from business judgment. New findings may still
identify Framework defects, but Phase 2's focus is skill design. The small smoke check
only verifies a runnable foundation; comprehensive regression work belongs to Phase 3.

No replay promotion, commit, push or release is authorized by the cleanup. Preserve
local credentials and business databases. New experiment results should have clear
identities and scope without reintroducing the retired Phase 1 dependencies.

## Simple four-mode runner — agreed 2026-10-06

Use one runner for `mock`, `live`, `evaluate` and `capture`, with shared execution,
collection and reporting. Edit the current skills directly. Compare a focused change
with the last accepted result; commit accepted improvements or revert the specific
unsuccessful edits while preserving other work. No variant registry, experiment trees
or comparison matrix are needed. Runner implementation is authorized; no paid run or
Git commit is authorized by that implementation request.

Record the model, scenarios, authored skill/configuration hashes, effective runtime
configuration and artifact identities. Keep a latest result and a manually maintained
accepted result instead of accumulating every attempt. The default latest report/bundle
is replaced; named outputs must be new directories. Capture never approves a fixture.
Mock remains explicitly unavailable until compatible approved fixtures and their replay
support are established. It must not load obsolete captures or fall back to paid calls.

The initial runner covers baseline and priority assessment scenarios. Scenario checks
are separate from orchestration; full service-request regression and broad release
coverage remain future work. Human business review remains distinct from execution
and exact-preservation checks. Repeated evidence of improvement is a working practice,
not an experiment-management subsystem.

## Phase 2 learning objective — clarified 2026-10-06

Choose a plausible lower-tier model, inspect saved failures where available, and
use focused skill changes to learn how skill composition can improve mid-tier
model performance. The objective includes transferable understanding of task
decomposition, intermediate contracts and reasoning responsibilities, beyond
getting this particular workflow to pass. Keep observations separate from causal
hypotheses and test proposed improvements against independent business facts.

Read-only inspection of historical evidence may inform this diagnosis without
restoring the retired runner or making archives a runtime dependency.

The agreed first target is Luna 6 at medium reasoning on embedded Java. Start
with an explicit, structured feasibility assessment before strategy selection,
changing one aspect of skill composition at a time. Use MiMo later to investigate
whether improvements transfer to another model. The user authorized proceeding
with the baseline and priority Java evaluation on Luna 6/medium and waived a
separate budget requirement for Luna runs. Do not repeatedly request Luna budget
approval within the agreed work. This does not authorize other paid models or
Sidecar evaluations; further experiment scope changes remain to be agreed.

Keep all model experimentation on Java until the Java skill work is working
successfully across the agreed scope. Defer Sidecar testing until then, rather
than confirming each intermediate improvement on both integrations, to avoid
duplicate runs. Equivalent behavior is the expectation, not an observed Phase 2
result; continue preserving equivalent business and authorization behavior in
both applications.

The first implementation makes `context.candidateReasoning` a required structured
input to `compareOptions`, authored in the existing `planResolution` model action.
It assesses each offer's completion timing, access, production fit, expiry and
approval prerequisites before selecting a strategy. The comparison must verify
those findings against source evidence and retain unresolved prerequisites.
This adds no skill invocation and preserves existing source bindings and public
output contracts. Schema validity alone does not establish success.

The first authorized Java evaluation (2026-10-06, run
`c08d430bd0ee49e19b6e56a8ab7c216c`) is not accepted. Baseline failed after two
malformed comparison tool actions; priority recovered from one malformed action,
passed 13/13 automated checks, and retained the technician-overrun access condition
in its final recommendation. Total reported provider cost was $0.027913975.
Provider-disabled runtime was restored. That run's review separated observed
improvement on the targeted reasoning from new execution failures. Its latest
artifacts have since been replaced by the following experiments, under the agreed
retention policy. The current edits remain experimental, not accepted.

The user authorized the next experiment on 2026-10-06: one shallow feasibility
result per option, with Framework transporting and assembling the results for
comparison. Four named option skills share one method and flat output contract;
their inputs and the comparison's feasibility inputs are fully bound. This tests
decomposition plus output-shape simplification together, not their isolated causal
effects. Run baseline and priority on Java with Luna 6/medium and review both
execution and business reasoning. The Luna budget waiver continues to apply.

The first shallow-output run, `76f6266e507a4172a4da13ecb8003fae`, completed both
scenarios with 13/13 automated checks, 15 calls each, no rejected actions or failed
model attempts, and $0.04188183 total reported cost. All eight per-option results
were forwarded exactly; both final recommendations retained technician access
beyond normal hours. This is an observation from two cases, not reliability proof.
Review also found irrelevant rental-period calculations and procurement approval
incorrectly described as application-verified in priority. The per-option inputs
omitted the parent reservation flag. The follow-up supplies reservation/source-id
bindings and clarifies activity durations and the external procurement boundary,
then repeats the same two Java scenarios. These findings prevent unqualified
business acceptance of the first shallow-output run.

The follow-up run `e307bd5636a34750af28908f3d50d474` also completed both cases with
13/13 checks, 15 calls each, zero rejected actions/failed model attempts/plan retries,
and $0.04159702 total reported cost. All eight feasibility inputs and forwarded
results passed exact-value review. Model call envelopes were 100-117 characters
with empty arguments; feasibility responses were 2,330-3,004 characters. The
loaner duration and procurement-boundary corrections held, and both final outputs
retained technician access beyond 18:00. The priority comparison nevertheless
changed a correct '2-4 hours beyond the recoverable-delay window' finding to
'2-4 hours after the 06:00 start', which should be 4-6 hours. Existing equipment
assessment wording also calls recurrence counts unspecified despite acknowledging
three recurrences. Full business acceptance is therefore still pending.

These runs support shallow per-option generation plus Framework-owned transport
on the observed cases; they do not isolate schema depth from task decomposition or
establish general reliability. Final synthesis preserving intermediate reference
points is the next identified issue. Nested input bindings still cause small
model-driven dispatches under the installed Framework's top-level-only direct
dispatch proof. No Framework changes, paid Sidecar runs or commits were made.

The next authorized continuation targets business consistency within the existing
shallow composition. The equipment skill separates established observations from
missing attributes before writing questions and uncertainty. Feasibility and
comparison retain quantity, unit, activity and reference event together, recalculate
when a reference changes, and avoid assuming unspecified lead-time start triggers.
This is a prompt-method experiment with unchanged contracts and skill boundaries,
not a demonstrated remedy yet. Repeat the baseline and priority Java Luna evaluations
and review intermediate findings as well as the published decision.

Run `3c107f1076bc47bb91edaeec4ae634bd` completed both cases with 13/13 checks,
15 calls each, no rejected actions/failed attempts/plan retries, and $0.044760045
reported cost. All 30 responses parsed and all eight feasibility inputs and results
passed exact-value checks. Both final comparisons now retain the distinct production
and recoverable-delay reference points; both assessments preserve the known recurrence
count, and both replacement findings leave the lead-time trigger unknown. These are
targeted improvements on two cases, not a reliability claim. Review still found
baseline attribution of later recurrence to the original work order, priority omission
of the short-test versus symptom-onset comparison, ambiguous dollar-symbol/cent prose
in baseline replacement feasibility, and priority loaner wording calling the offered
window scheduled. The follow-up keeps the same structure and asks for source-specific
attribution, comparison of test conditions against symptom onset, explicit currency
conversion, and offered-versus-confirmed wording. It also limits unnecessary arithmetic
and requires source IDs rather than field names in citations. Business acceptance
remains pending; normal provider-disabled runtime was restored after this run.

Run `788e70c20679439c8ea3b1b549912b80` completed both cases with 13/13 checks,
15 calls each, zero rejected actions/failed attempts/plan retries, and $0.043940590
reported cost. All 30 responses parsed and all eight feasibility inputs/results
passed exact-value checks. The earlier corrections held; both assessments explicitly
compared the short prior test with later symptom onset and separated the original
work order from the later incident. Currency notation and offered-versus-confirmed
wording improved. Full review still found a weakening observation categorized as
supporting an optical-path hypothesis in priority and procurement feasibility
language importing caller/site-grant requirements from the service process.

The next revision separates service and procurement approval instructions in the
shared generator, supplying only the relevant method to each feasibility skill.
Contracts, bindings and the skill graph remain unchanged. Equipment assessment
also distinguishes evidence that favors a hypothesis from contrary observations
and missing information, allowing empty evidence arrays instead of filling them
with merely relevant facts. Repeat the same Java Luna scope. These are combined
prompt changes; their independent effects are not isolated. Normal provider-disabled
runtime was restored after the preceding run.

Run `6c7f71575aa8489ab91d1a7064f77746` completed both cases with 13/13 checks,
15 calls each, no rejected actions/failed attempts/plan retries, and $0.046361965
reported cost. All 30 responses parsed and all eight feasibility inputs/results
passed exact-value checks. The earlier corrections held; evidence was classified
consistently and procurement findings no longer imported service-app permissions.
Agent business review accepts the conditional recommendations for the two agreed
scenarios. Matching report, summary, bundle and checksum-linked business review
were copied to `evidence/accepted`; this is not replay approval or release acceptance.

The final prompt revision has one two-case evaluation. No unchanged repeat, new
boundary cases, independent reviewer, other model or paid Sidecar run establishes
broader reliability. Residual verbosity and redundant questions remain improvement
opportunities rather than material decision failures in this review. Baseline's
unspecified risk preference permits a conditional recommendation, not an invented
authorization to spend. Total reported cost for this three-run continuation was
$0.135062600. Normal provider-disabled runtime was restored after every run.
No business fixtures, application authorization rules, skill contracts or bindings
were changed in this continuation; no commits or pushes were made. The next useful
validation is an unchanged repeat followed by relevant constraint variations;
this note does not expand the agreed paid-run scope.

## Unchanged repeats and model transfer — agreed 2026-10-06

The user authorized two further Luna 6/medium evaluations of baseline and priority
on Java with the accepted skills unchanged, followed by GLM 5.3 on the same skills
and cases without advance tuning. This explicitly authorizes the GLM paid evaluation
and supersedes MiMo as the next transfer candidate. Preserve accepted evidence and
review each run before replacing latest. Record unchanged source hashes and separate
execution, transport and business findings, including regressions. Constraint
variations follow this comparison; define their inputs and expected implications
before running them. No paid Sidecar runs, commits or pushes are authorized.

The first unchanged repeat, `bd7e93a72764414dbc3160d633a8347d`, passed 13/13
automated checks in both cases, used 15 calls per case with zero rejected actions,
failed attempts or retries, and cost $0.044218170. All recorded source hashes match
the accepted run, all 30 raw responses parse, and all eight feasibility input/result
checks passed. Business review rejects priority: replacement feasibility ignored
its bound 11:00 expiry and called the deadline unknown; comparison repeated that
false unknown. Comparison also omitted the expedited-work late-access prerequisite
while preserving it for the loaner. This disproves repeatability of full business
success in the observed pair; it does not invalidate the earlier successful sample
or exact transport findings. Skills stay frozen for the remaining comparisons.
Compact checksum-linked reviews are recorded in `evidence/validation-review.json`
before latest is replaced, preserving the agreed latest-plus-accepted raw retention.

The second unchanged repeat, `4dfdc2daee104a33b142644c830b1d80`, also passed
13/13 checks in both cases with 15 calls each, zero rejected actions/failed attempts/
retries, exact source hashes and feasibility transport, and 30 parseable responses.
Reported cost was $0.045181965. Replacement expiry and both late-access conditions
held. Core business decisions were defensible, including baseline selecting
expedited alone with explicit residual risk and priority selecting the combined
strategy. Review still found missing inspection evidence categorized as contrary
and omission of the explicit incomplete/disputed-coverage reviewer handoff in the
priority final recommendation. It was not promoted over the accepted reference.
The GLM transfer evaluation uses exact provider ID `z-ai/glm-5.3`, with requested
medium reasoning (not a claim of equal reasoning effort across model providers).

GLM run `ff8b3b5c85954d59b81e6327042fd809` completed both cases with 13/13
checks, exact source hashes and feasibility transport, but is rejected on business
review. It cost $0.406493430, using 17 baseline and 15 priority calls. Baseline
equipment assessment needed two schema-advisor corrections (missing `contrary`
fields, then undeclared `uncertainty_note` fields). Existing failed-attempt/plan-retry
counters do not include those corrections; all 32 raw responses were valid JSON.
Material errors include double-counting the included premium, conflating elapsed
and billable hours, importing procurement approval into service, using attendance
end rather than access end for an access condition, and post-expiry fallback advice.
Priority equipment assessment also invents an incident date. No GLM tuning is made.

The authorized input-variation stage uses Luna/medium on Java with frozen skills
and two explicitly selected scenarios; default runs remain baseline and priority.
`capacity_shortfall` changes only the priority case's minimum capacity to 25/minute:
the 20/minute loaner cannot meet the full need; any partial benefit requires explicit
shortfall and cannot be called sufficient or assumed combinable with unknown repaired
capacity. `later_start` changes only baseline production start to September 30 at
16:00: standard arrival at 10:00-12:00 is 4-6 hours before start, not after it;
elapsed work/restoration are still unknown and no unconditional completion claim is
justified. The recoverable-delay endpoint becomes 18:00. Unchanged expiry, approval,
access and charging conditions still apply. These expectations are review criteria,
not fixture answers injected into skills. Only scenario construction/default selection
changes; business source records, skills and model settings remain unchanged.

Variation run `03bc8e3a72c24ea2aae5e889eb5b7812` passed 13/13 checks in both
cases and met both predeclared business implications. It cost $0.046427705, with
16 capacity-shortfall calls and 15 later-start calls. Exact comparison confirmed
the intended single operating-need change in each case, unchanged skills and
business fixtures, and all eight feasibility input/result checks. The capacity
equipment assessment initially emitted a trailing comma after an empty `contrary`
array; the schema advisor requested one correction and the next response succeeded.
Thirty of 31 raw responses parsed as JSON; broad retry counters still read zero.
Minor review findings include one mistyped quote ID in feasibility prose and a
plural reference to repair-quote attendance where only expedited had that window.
The targeted implications pass, but this run is not promoted over the accepted
reference as a fully clean result.

This validation continuation comprised four evaluations/eight case executions,
123 model calls and $0.542321270 reported cost. Normal provider-disabled runtime
was restored after every evaluation. No skill edits, paid Sidecar runs, commits
or pushes were made. The accepted reference remains a successful sample, not proof
of repeatability. Next work should address known-fact retention, faithful publication
of each pursued option's prerequisites, and nested equipment-output corrections;
the evidence does not justify declaring either model generally successful yet.

## Durable skill-design guidance — agreed 2026-10-06

Maintain [From business processes to reliable skills](mid-tier-skill-design.md) as
the durable, generalized guide to business-process decomposition for mid-tier
models. Its purpose is to improve the starting design of future skill trees across
domains and conversation contexts. Keep it focused on transferable practices and
their limitations, separate from this application's scenarios and experiment log.
Distinguish observed mechanisms, working recommendations, and untested hypotheses.
Use explicit evidence statuses rather than numerical rankings: demonstrated in a
defined scope, promising but not established, and proposed for testing. Each
material practice should state what supports it and what remains to demonstrate;
an observed failure does not prove its proposed remedy. Revise statuses and scope
when repeated evidence, counterexamples, or regressions warrant it.
Read it when designing skill trees and revise it when evidence adds, qualifies,
or contradicts a general lesson. The README and AGENTS.md make it discoverable
to future sessions. Creating or maintaining the guide does not authorize commits
or additional model evaluations.

## Direct publication and shallow equipment assessment — agreed 2026-10-06

Continue Java Luna 6/medium with a combined design experiment: Framework binds
the original incident into equipment assessment, and source expiry, reservation
state and snapshot identity into each option result. It publishes every accepted
option assessment directly in the final result. Comparison still judges the
tradeoff and must explicitly identify any correction to provisional findings.
Equipment hypotheses become self-contained strings identifying support, contrary
evidence or its absence, and missing evidence, removing nested generated objects.
Shared Java/Sidecar contracts change together; paid Sidecar remains deferred.

Evaluate baseline, priority, capacity-shortfall and later-start cases with frozen
skills. Review faithful publication separately from business correctness, including
expiry action, both access conditions, approval routing, charge interpretation,
provenance and uncertainty. Inspect schema corrections as well as raw JSON. The
combined change cannot establish which individual modification caused an effect.
Additional exact-publication checks are transport checks, not semantic acceptance.

Run `04cd2ed928d948fca25f70b4acff8eb5` evaluated all four cases with frozen
skills. Each passed 22/22 checks; all 60 responses parsed as JSON and detailed
traces contained no schema corrections. Sixteen option input/result paths, final
option publication and source metadata, and four original-incident publications
were exact. Reported cost was $0.089411250. Provider-disabled runtime was restored.

The baseline core business review passed with minor wording caveats. Priority
retained pursued-option conditions but summarized a whole arrival range using
only its earliest endpoint's delay. Capacity-shortfall correctly identified the
five-unit/minute deficit, then wrongly added dispatch confirmation before expiry
as a requirement for price preservation. Later-start correctly recalculated the
production timing, then unnecessarily disputed an elapsed-work estimate; its bare
source label also leaves interpretive ambiguity. Several equipment assessments
asked about the physical cleaning performer without retaining the known record
author, although author and performer are not necessarily identical. Detailed
review is in `evidence/latest/business-review.json` and the consolidated review.

Retain the structural improvements as promising; do not promote this run to the
accepted reference or claim repeatability. The next design target is comparison's
responsibility and contract: selection/tradeoffs with references to published
conditions, avoiding a second reconstruction of operational procedures. Clarifying
quantity semantics at their producer boundary is a separate hypothesis. The guide
now distinguishes demonstrated publication fidelity from unproven semantic benefit
and records that broad verification can introduce unnecessary corrections.

## Narrow comparison responsibility — agreed 2026-10-06

Proceed with Java Luna/medium on the same four cases. Remove comparison-generated
changeConditions and responsibleParty, add explicit pursuedOptions and optional-
in-meaning (required array, possibly empty) reviewConcerns, and constrain the
remaining fields to selection, tradeoffs, portfolio uncertainty and residual risk.
nextDecision points to published option conditions instead of reconstructing their
procedures. Per-option service assessments now explicitly retain post-approval
scope/attendance/cap changes and pending/disputed coverage review. No source
fixtures or quantity semantics change in this experiment; those remain separate.

The public shared contract changes equally for both applications. Add a structural
portfolio consistency check, then assess whether all published operational
conditions remain complete and whether comparison introduces new claims. Review
concrete conflicts rather than assigning a general re-audit. Keep the existing
flat equipment output and exact-publication bindings unchanged. This tests a
combined contract and responsibility change, not a prompt-only isolated effect.

Run `0f58d23b82c247cea69ed4e700465fe6` completed all four cases with 23/23
checks each, 60 valid JSON responses, no schema corrections and exact publication
of all option findings and metadata. Cost: $0.086298925; runtime restored with
provider access disabled. Thirty provider-free tests passed.

Compared with the immediately preceding run, compact JSON for model-owned final
fields fell from 31,709 to 9,002 characters across the four cases (71.6% reduction;
not a token or isolated latency comparison). The three prior comparison errors
did not recur. The capacity and later-start implications were preserved, and
explicit portfolios were consistent with the primary selection. reviewConcerns
was empty in every case, which is not proof that leaf reasoning was correct.

Business review still rejects full acceptance. Baseline service findings assigned
Erin Cole (dispatch) to the separate unnamed warranty-review contact. Five of eight
service findings omitted explicit renewed approval for changed attendance, scope
or cap despite its relocation into the generic unresolved list. Some equipment
hypotheses still treat generic relevance as support or unrelated observations as
contrary evidence. The consolidated review and latest business review preserve
these findings; the previous accepted sample remains unchanged.

Retain the narrowed comparison as promising, with no repeatability claim. The next
proposed structural experiment is small explicit fields for mandatory service
conditions and source-record references for owners, rather than a larger prompt
or another general reviewer. Equipment evidence classification remains a separate
open issue. No paid Sidecar evaluation, fixture changes, commit or push occurred.

## Explicit service conditions and owner references — agreed 2026-10-06

Run the full four-case Java Luna/medium evaluation after introducing service-only
chargeCondition, scopeChangeCondition and coverageReviewCondition text fields,
plus dispatchOwnerSourceIds and coverageReviewerSourceIds arrays. Framework binds
an unchanged ownerDirectory from source contacts into each service output. Model
handoffs reference IDs rather than completing or joining contact personal names.
Missing rules or unmatched roles remain explicitly unknown/empty. Procurement
outputs, equipment reasoning, narrowed comparison, fixtures and quantity semantics
remain unchanged; shared schemas are updated at all consumers for both runtimes.

The structural checks verify condition presence, reference existence/uniqueness
and exact directory publication, not semantic role selection or rule correctness.
Review all eight service outputs for charging interpretation, full renewed-approval
conditions, pending/disputed review and correct role references. Also review whole
workflow decisions, diagnostic evidence and both operating-need variations. This
is a combined dedicated-field and source-reference experiment; benefits cannot
be individually isolated or assumed repeatable. No paid Sidecar run is included.

The completed run `d4e921b068e04bb6beba031946df9476` passed27/27 structural
checks in all four full end-to-end Java cases. All eight service outputs met the
targeted condition and owner-role review. All61 responses parsed as JSON; baseline
expedited omitted both owner-reference arrays initially and succeeded after one
schema correction. Cost was $0.092637040; runtime was restored with provider access
disabled. Thirty-eight provider-free tests passed. Remaining equipment fact-handling,
evidence-classification and temporal-wording gaps prevent full business acceptance.
The latest and consolidated business reviews preserve the detailed findings.

## Human business contract and mixed-model routing — agreed 2026-10-06

The user clarifies that business-process recognizability is a design requirement.
A business reader should recognize the skill tree as a sensible decomposition of
their work, even if it differs from their own decomposition. Do not distort that
process, fragment coherent judgment into artificial microsteps, or accumulate
scenario-specific instructions merely to obtain an all-Luna pass. Review current
experimental boundaries against this criterion rather than treating them as fixed.

The desired outcome is a coherent business skill tree using stronger models for
reasoning-intensive responsibilities and mid-tier models where they are reliable.
Sol for selected responsibilities and Luna for the rest is an intended solution,
not an experimental failure. Choose routing from observed capability needs and
business responsibilities, not a target percentage of expensive calls. Preserve
runtime-owned transport, deterministic calculations/enforcement, and reviewable
source provenance without making implementation mechanics the business process.

First review and articulate the human-recognizable process and candidate model
assignments. Technical evidence assessment is a candidate for Sol given observed
reasoning gaps; feasibility and comparison assignments still require evidence.
Prefer clear per-skill routing initially over untested self-confidence escalation.
No mixed-model evaluation has been performed or authorized by this discussion
alone; agree its concrete scope before paid execution. Existing Java-first and
no paid Sidecar boundaries remain. This discussion takes precedence over continuing
the previously proposed all-Luna tuning sequence.

## Boundary/instruction reassessment — 2026-10-06

Completed a source-based review of the current generator, contracts and generated
skill graph against the human business contract. The assessment/feasibility/
recommendation/authorization boundaries remain defensible. Four option-specific
routes are implementations of a repeated business assessment, not four invented
human roles. Keep coherent causal reasoning in equipment assessment; do not split
it further merely to force a lower-tier pass.

The recommended next authored baseline should simplify arbitrary sentence limits,
blanket bans on useful restatement, and repetitive combination warnings; distinguish
business methods from transport instructions; and present source references as
readable business handoffs. Retain explicit financial/approval/coverage conditions,
source provenance, missing-evidence distinctions, and deterministic transport and
authorization. Do not assume that a rule added after a model failure is invalid:
several encode real business or evidentiary requirements.

The detailed keep/simplify/reconsider decisions and proposed readable process live
in foundation.md. Current runtime manifests and contracts are unchanged by this
review, preserving the evaluated experimental state. Before another model trial,
implement and review the readable baseline, then apply the whole-tree model ladder
above. A Sol-only technical-assessment trial is no longer the default next step;
it is a later mixed-tier candidate if the full-tree baseline warrants it.

## Readable baseline prepared — 2026-10-06

The user authorized implementing the audited baseline before selecting individual
skills for stronger models. Business methods and handoffs now precede separate
Framework instructions in the eight reasoning manifests. Consolidated corrective
guidance, removed arbitrary sentence limits, and restored comparison's explicit
accountability for decision-critical facts and material conflicts. Updated matching
schema descriptions without changing output shapes or validation constraints.
Business conditions, workflow boundaries, bindings and model assignments remain.

All 38 provider-free tests passed; both integrations loaded the shared manifests
and passed the provider-disabled smoke check with zero model calls. No paid run,
new accepted result, model selection, commit or release followed from this work.
The latest captured run predates these edits. An independent readability review in
a fresh context is a useful next step, then agree the concrete Java evaluation.
See foundation.md's prepared-baseline section for retained choices and limitations.

## Independent baseline review — 2026-10-06

The user authorized source-based review, clearly justified cleanup and provider-free
validation before choosing another model trial. The review retained the business
tree and aligned remaining schema/method contradictions around procurement offers,
approval families, completion windows and comparison corrections. It made financial
exposure and the decision handoff explicit using existing fields. Field shapes,
bindings, source records and model assignments remain unchanged.

See [the review and proposed trial](foundation.md#independent-review-of-the-prepared-baseline--2026-10-06).
The proposed next trial is one Java Luna/medium whole-workflow batch covering baseline,
priority, capacity_shortfall and later_start, with complete business review. This is
a recommendation awaiting concrete scope agreement, not renewed paid-run authority;
earlier Luna authorizations do not authorize this revised-baseline trial. Repeats,
stronger models and mixed packs require their own agreed scope. Paid Sidecar remains
deferred. Preserve accepted evidence, accumulated work and provider-disabled runtime;
no commit or push is authorized.

Validation completed: all 38 provider-free tests passed, regeneration was stable,
embedded contracts matched, and both integrations passed provider-disabled smoke
checks with zero model calls. Accepted/latest evidence remained unchanged. This
establishes configuration compatibility, not model business acceptance.

## Readable-baseline trial authorized — 2026-10-06

The user approved proceeding with the proposed one-batch Java whole-workflow
evaluation: `openai/gpt-6-luna`, medium reasoning, baseline, priority,
capacity_shortfall and later_start. Freeze the reviewed skills and use the detailed
business acceptance criteria in foundation.md. Review the full captured outputs,
preserve accepted evidence, and restore provider-disabled runtime. This authorizes
this batch only, not repeats, other models, paid Sidecar, commits or pushes.

The authorized run `a702010c55224d29b085a37631828eee` completed all four cases with
27/27 structural checks each, 60 valid JSON responses, zero schema corrections and
$0.088279740 reported cost. Source and transport checks passed; normal provider-disabled
runtime was independently verified and accepted evidence remained unchanged.

Full business acceptance is rejected. Two standard-service findings inferred elapsed
completion from billable repair hours; capacity-shortfall comparison invented an
elapsed-work/repair-scope conflict; later-start comparison inverted the fully covered
maximum's premium meaning. Technical fact-handling gaps remain. Dedicated service
conditions and owner references held, and both variation implications passed.
See foundation.md and the latest/consolidated business reviews for evidence and limits.

Keep the reviewed tree frozen. The next recommendation is one whole-tree Java
Sol/medium batch on the same four cases and criteria, subject to separate agreement.
This is not authorized by the completed Luna run. No all-Luna compensating rewrite,
repeat, paid Sidecar run, commit or push follows automatically.

## Whole-tree Sol trial authorized — 2026-10-06

The user approved the proposed next batch: Java `openai/gpt-6-sol`, medium reasoning,
on baseline, priority, capacity_shortfall and later_start. Keep the exact readable
tree and sources from the preceding Luna run and use the same full business criteria.
Preserve accepted evidence and the consolidated Luna review, then replace latest
through the shared runner. Restore provider-disabled runtime. This authorizes one
batch, not repeats, mixed packs, paid Sidecar runs, commits or pushes.

Run `734b09c4c74e47eebeb39dba36a3c1de` completed with identical source hashes to
the preceding Luna run, 27/27 checks per case, 60 valid JSON responses, no schema
corrections and $1.505192300 reported cost. Runtime restoration/provider disabling
and accepted-evidence preservation were independently checked.

Sol avoided Luna's material duration, false-scope-conflict and premium errors, with
defensible core decisions and both variation implications preserved. Full acceptance
is withheld for a published unsupported zero-setup-hours inference and unqualified
local loaner unknowns; see foundation.md and the checksum-linked business reviews.
Source ambiguities remain separately identified rather than attributed solely to
model capability. The stronger whole-tree assignment is promising, not a proven
baseline or justification for another automatic tier increase.

The recommendation is provider-free source/interface review before agreeing another
Sol confirmation batch. No additional paid run, mixed pack, Sidecar evaluation,
skill change, accepted-result promotion, commit or push is implied.

## Source/interface follow-up — 2026-10-07

The user approved the provider-free follow-up. Reviewed timing semantics, published
option scope and implementation authority; clarified the shared option method and
schema descriptions without changing the tree, shapes, bindings, assignments or
business sources. Access calculations require established activity dates, local
unknowns must not become case-wide absence claims, and ambiguous arrival/setup
semantics remain explicit questions rather than invented facts.

Static inspection confirms both request implementations accept only Luis and caps
up to $1,000; no larger-service Priya path is implemented. This qualifies the prior
source-boundary caveat without changing captured reviews or granting permissions.
The loaner source interpretation remains a business-source clarification, not an
authorization to manufacture a completion guarantee. No source values were changed.

The amended baseline has provider-free validation only. A four-case Java Sol/medium
confirmation is recommended under the existing acceptance criteria, but requires
separate agreement. Paid Sidecar, repeats, accepted promotion, commits and pushes
remain outside this follow-up.

Validation completed: 38 tests passed, regeneration was stable, embedded contracts
matched and both integrations passed provider-disabled smoke checks with zero model
calls. Captured/accepted evidence, fixture values and application code were unchanged.

## Sol confirmation authorized — 2026-10-07

The user approved one Java `openai/gpt-6-sol`/medium confirmation batch on baseline,
priority, capacity_shortfall and later_start using the amended option methods and
descriptions. Freeze this baseline and review the complete business results, including
dated access calculations, scoped unknowns and arrival/setup ambiguity. Preserve
accepted evidence and restore provider-disabled runtime. No additional repeats,
mixed packs, paid Sidecar runs, commits or pushes are authorized.


The confirmation completed as run `ad12aaba4d514fabb5c17def0dde3c7e`: 27/27
checks per case, exact reviewed handoffs and $1.5304466 reported cost. Sixty of 61
responses were valid JSON; a malformed capacity comparison recovered through one
correction. Targeted date/scope/window clarifications held, with defensible core
decisions. Full acceptance is withheld because later-start comparison invents expiry
of procurement approval alongside offer expiry. See foundation.md and the linked
latest/consolidated reviews for the narrow defect and nonblocking caveats.

Skills remained frozen, accepted evidence unchanged and provider access disabled
after independently verified restoration. The next recommendation is one unchanged
four-case Java Sol/medium repeat to measure recurrence before further changes; it
requires separate agreement. No repeat, additional tier upgrade, mixed pack, paid
Sidecar evaluation, accepted promotion, commit or push is authorized by this result.


## Mixed pack authorized — 2026-10-07

The user approved one Java mixed-pack batch on baseline, priority, capacity_shortfall
and later_start. Use Sol/medium for assessEquipment, assessExpeditedFeasibility,
assessStandardFeasibility and compareOptions; Luna/medium for resolveEquipment,
planResolution, assessLoanerFeasibility and assessReplacementFeasibility. This
supersedes the proposed all-Sol repeat and exercises the capability-specific exception.
Prior failures justify technical assessment, service feasibility and comparison as
stronger-model candidates; the paired service skills form one coherent responsibility.
The remaining Luna assignments are experimental, not proven reliable.

Keep methods, schemas, source facts and business boundaries fixed. Apply temporary
runner model overrides, capture effective routing, and verify each skill's model
from traces. Evaluate complete business outputs under the existing criteria and
report total cost, per-model usage, corrections and transport separately. Preserve
accepted evidence and restore provider-disabled runtime. No repeat, paid Sidecar,
accepted promotion, commit or push is authorized.



The authorized mixed run `689ab4210f1242658c2b7e802e47f678` completed all four
cases with 27/27 checks each, exact independently reviewed handoffs, 60 valid JSON
responses and no corrections. Verified usage was 16 Sol calls ($0.49692480) and
44 Luna calls ($0.05567843), totaling $0.55260323. This is 63.9% below the previous
all-Sol batch; it is not an equal-accepted-quality or repeatability claim.

Core decisions and targeted service conditions held. Full acceptance remains withheld
for unsupported procurement supplier-role assignments in Luna findings; Sol also
reopened a known test duration. The latest/consolidated reviews and foundation record
source-linked findings and their limits. The mixed strategy remains promising; the
result does not authorize a repeat, another assignment, paid Sidecar or further skill
rewrites. Provider access is disabled, accepted evidence and authored defaults are
unchanged, and no commit/push occurred. Runner support passed 41 provider-free tests.


## Six-Sol/two-Luna trial authorized — 2026-10-07

The user approved one Java batch on baseline, priority, capacity_shortfall and
later_start with Sol/medium for assessEquipment, all four option-feasibility skills
and compareOptions. Retain Luna/medium for resolveEquipment and planResolution.
Only the loaner and replacement assignments change from the preceding mixed pack;
methods, schemas, source facts and business boundaries stay frozen. This tests
whether stronger procurement assessment avoids unsupported supplier handoffs and
service/procurement rule mixing, while reviewing all outputs including Sol's
known-test-duration regression. Record effective routing, corrections, total and
per-model cost. Preserve accepted evidence and restore provider-disabled runtime.
No repeat, paid Sidecar, accepted promotion, commit or push is authorized. A passing
batch would remain a single sample; reliability repeats need separate agreement.


Run `387bca13bebb4ee386e548fd4c1d2414` completed the authorized six/two batch:
27/27 checks per case, exact reviewed handoffs, sixty valid JSON responses and no
corrections. Verified usage was 24 Sol calls ($0.65695000) and 36 Luna calls
($0.04398581), totaling $0.70093581. It cost 26.8% more than four/four and 54.2%
less than the all-Sol confirmation; these are individual batch observations.

Procurement handoff defects and the known-duration question did not recur. Core
decisions passed review, but full acceptance remains withheld: later-start Sol
expedited unresolved prose implies scope overrun by comparing elapsed work hours
with billable repair hours, despite correct distinctions elsewhere. Preserve the
candidate and inspect that localized inconsistency before reliability repeats;
no additional run, skill edit or coordination-model upgrade is authorized. Accepted
evidence/defaults are unchanged and provider-disabled restoration was verified.


## Business-readable refinement reaffirmed — 2026-10-07

The user explicitly reaffirmed that skill improvements are welcome provided the
process remains understandable to a human business practitioner. Freezing methods
within an experiment supports comparison; it is not a standing prohibition on
revising methods, schemas or handoffs. Do not treat every observed failure as either
a mandatory model upgrade or a reason to add a scenario-specific instruction.

The user approved the provider-free clarification of elapsed visit time versus
billable repair scope. The shared service method now connects elapsed time to
scheduling, repair labor to its charging allowance, and renewed approval/new quotes
to the supplied change-of-attendance/scope/cap rules. Included diagnosis can occupy
elapsed time without consuming repair-labor allowance. Unknown required repairs
leave an overrun unestablished. Matching charge and scope descriptions were aligned
at producers and consumers. No business facts, output shapes, bindings, tree or
model defaults changed; the six/two assignment remains the candidate for a separately
agreed confirmation. No paid evaluation, accepted promotion, commit or push is
implied by this refinement.


Validation of the elapsed-time/scope refinement: all 41 provider-free tests passed;
regeneration was byte-stable and producer/embedded service contracts matched.
Parsed before/after checks confirmed only methods and descriptions changed, with
shapes, constraints and bindings preserved. Both integrations reloaded the shared
manifests through the runtime helpers and passed provider-disabled smoke checks with
zero model calls and previous business records preserved. Smoke added its documented
isolated quote rows. All captured/accepted evidence and source fixtures remained
unchanged. This establishes compatibility, not post-edit business acceptance.


## Scope clarification confirmation authorized — 2026-10-07

The user approved one Java confirmation batch with the amended service methods and
matching descriptions: baseline, priority, capacity_shortfall and later_start;
Sol/medium for technical assessment, all four feasibility skills and comparison;
Luna/medium for resolveEquipment and planResolution. Freeze this version within the
batch. Review all business outputs, especially elapsed work versus billable repair
scope, actual approval triggers, supplier handoffs and technical evidence. Report
routing, corrections and cost. Preserve accepted evidence and restore provider-disabled
runtime. No repeat, paid Sidecar, accepted promotion, commit or push is authorized.

Scope confirmation outcome: run `10511fac0dee462ab9dffdcf8b5e69ff` completed all four
cases with 27/27 checks each, exact independently verified transport and 60 valid
JSON responses without corrections. Usage was 24 Sol calls ($0.659913900) and 36
Luna calls ($0.043826495), totaling $0.703740395. The elapsed-time/scope implication
did not recur, and full review supports a single-batch business pass with minor
caveats. Baseline redundantly asks duration while stating the known 20 minutes;
other wording and the incomplete-coverage owner ambiguity are recorded in the
checksum-linked review. This is not perfect compliance or demonstrated reliability.

Retain the current candidate for a proposed two unchanged four-case Java repeats
(about $1.41 combined at observed cost), subject to separate agreement. No new run
is authorized by this recommendation. Accepted evidence and model defaults remain
unchanged; provider-disabled restoration was independently verified. The business
pass does not authorize accepted-reference promotion, paid Sidecar, commit or push.

## Two unchanged Java repeats authorized — 2026-10-07

The user approved two further four-case Java batches on the version confirmed by
run `10511fac0dee462ab9dffdcf8b5e69ff`: baseline, priority, capacity_shortfall and
later_start. Keep Sol/medium for assessEquipment, all four feasibility skills and
compareOptions; Luna/medium for resolveEquipment and planResolution. Freeze methods,
schemas, bindings, source facts and assignments across both batches. Review each
complete result against the existing business criteria, including the recorded
minor caveats; preserve each checksum-linked review before replacing latest.
Report individual and combined usage/cost. The approximate $1.41 estimate is not a
guarantee. Restore provider-disabled runtime after each batch and preserve accepted
evidence. No additional retry, paid Sidecar, accepted promotion, commit or push is
authorized.

Both authorized repeats completed without changing the frozen candidate. Run
`1ee7f7e930d943098d2806a53fe0795e` cost $0.705831760; run
`917e33b863974d9da619a2ae3c290d64` cost $0.702238010. Combined cost was $1.408069770
for 48 Sol and 72 Luna calls. All eight cases passed 27/27 checks, with exact
independently verified inputs/results and 120 valid JSON responses, no corrections.

The second batch passed business review with minor caveats. The first was withheld:
capacity-shortfall replacement feasibility questioned applicability of the supplied
expiry because parent and child source identifiers differ. The contract already
explains those fields; comparison did not correct the false uncertainty. Core
portfolios remained defensible, and the elapsed-time/scope correction held in all
sixteen service findings and eight final decisions. Seven of eight complete results
passed the material-correctness review; this is a bounded observation, not a stable
success-rate estimate. Complete business repeatability is not established.

Recommend a provider-free review of supplied offer terms versus genuine source
conflicts at the existing assessment and comparison responsibilities. That is a
proposed next step, not a completed fix or authorization for more paid testing.
Keep the human business contract and the current candidate; do not reflexively add
instructions, fragment the tree or upgrade the entire pack. Both reviews are retained
in the consolidated evidence; latest contains the second. Provider-disabled restoration
and unchanged accepted evidence/defaults were verified after each batch. No further
paid run, Sidecar evaluation, accepted promotion, commit or push occurred.

## Complete offer and publication review redesign — 2026-10-07

The user approved proceeding with the proposed redesign at whatever scale is
justified by a human-readable business process. This scope is provider-free:
complete offer context, clear separation of supplied terms from unconfirmed
arrangements, and material review of every published finding, including deferred
options. Keep the existing business responsibilities and candidate six/two medium
assignment; authored model defaults remain unchanged. No paid trial is authorized.

The existing deterministic quote operation now also assembles four complete offer
records in both hosts, retaining original details, snapshot terms/provenance,
monetary units and the exact service quote where applicable. It adds one continuity
source retrieval rather than a new skill. Assessors receive their whole offer instead
of separate parent metadata and both service quotes. Comparison receives the same
records alongside original sources and now explicitly reviews all material published
claims, retaining original findings and stating governing corrections in reviewConcerns.
Shapes of published decisions, permissions, quote arithmetic and fixture facts are
unchanged. Input contracts and bindings changed and require a future full workflow
evaluation; provider-free success cannot establish improved model consistency.

Validation: 44 provider-free tests passed, Java packaged successfully, and both
integrations passed disabled-provider smoke checks including exact complete-offer
assembly, quote amounts, permissions and prior-record preservation, with zero model
calls. Original latest/consolidated/accepted evidence remains unchanged. Maintained
documentation distinguishes this untested reasoning proposal from prior observations.
The runtime uses the documented helpers and provider access remains disabled.


## Complete offer confirmation authorized — 2026-10-07

The user approved one Java confirmation of the redesigned complete-offer handoffs
and publication review: baseline, priority, capacity_shortfall and later_start.
Keep Sol/medium for technical assessment, all four feasibility skills and comparison;
Luna/medium for resolveEquipment and planResolution. Freeze this candidate within
the batch. Independently verify complete offer transport and review every published
finding against the existing business criteria. Report actual cost and corrections,
preserve accepted evidence and restore provider-disabled operation. This approval
does not include further repeats, paid Sidecar, accepted promotion, commit or push.

Confirmation outcome: run `74621db70bbd44b89419749256b91ef0` passed all four complete
business cases with minor caveats. All 108 structural checks passed, complete-offer
transport/publication was exact, and 60 responses were valid JSON with no corrections.
Reported cost was $0.729449095: 24 Sol calls ($0.682674400) and 36 Luna calls
($0.046774695). The supplied-expiry and elapsed-time/repair-scope defects did not recur.
This does not establish repeatability or the broader review's ability to correct a
material error; no such correction was exercised. The published decisions remain
materially usable, with unnecessary arrival/attendance clarification, some compressed
deadline wording and a less explicit final operations handoff recorded as caveats.

The next recommendation is provider-free clarification of the deterministic quote
attendance meaning, preserving its source arrival value and genuine loaner setup
uncertainty. This is a proposal, not a further implemented change or paid-run approval.
Keep the six/two candidate and human business contract. Provider access is disabled;
accepted evidence and authored model defaults remain unchanged. Latest and consolidated
reviews retain the bounded findings. No repeat, paid Sidecar, promotion, commit or push
occurred beyond the authorized confirmation.

## Attendance semantics clarification — 2026-10-07

The user approved the proposed provider-free clarification. Both producers already
copy source arrival into quote attendance; no application logic or data values needed
changing. Shared quote schema descriptions now define attendance as the offered
technician arrival window, without implying visit end, elapsed duration, restoration
or dispatch confirmation. The service-approval field describes exact matching to that
quote window. Regenerated shared manifests preserve field names, shapes, bindings,
business methods and model defaults. The loaner's genuinely unspecified setup timing
remains unchanged.

All 44 provider-free tests passed, including changed arrival intervals in the existing
offer-preservation test. Both real integrations passed provider-disabled smoke checks
with explicit quote/source arrival equality, zero model calls and prior rows preserved.
Generation is byte-stable; application sources, fixtures and all captured/accepted
evidence are unchanged. Shared schemas were reloaded through documented runtime helpers.
This verifies compatibility and source preservation, not removal of the model's
unnecessary questions. The latest model review predates this clarification.

A proposed next paid scope is one fresh Java confirmation on all four existing cases,
with six Sol/two Luna at medium, checking the complete business criteria and whether
known service-window semantics coexist with genuine loaner setup uncertainty. At the
last observed batch cost, budget approximately $0.73; this is not a cost guarantee or
authorization. Paid Sidecar, further runs, accepted promotion, commit and push remain
outside this completed provider-free scope.


## Attendance clarification confirmation authorized — 2026-10-07

The user approved one four-case Java confirmation: baseline, priority,
capacity_shortfall and later_start. Keep six Sol/two Luna at medium, freeze the
clarified candidate within the batch, verify exact handoffs and review all published
business findings. Check known service arrival semantics while retaining genuine
setup uncertainty. Report actual cost and corrections, retain accepted evidence,
and restore provider-disabled operation. No additional repeat, paid Sidecar,
accepted promotion, commit or push is authorized.

Attendance confirmation outcome: run `0d5ec617e2e541779cacbdeb6c087446` completed the
four cases with 108/108 checks, exact handoffs and 60 valid JSON responses, no schema
corrections. Cost was $0.711329490 (24 Sol calls: $0.664921200; 36 Luna calls:
$0.046408290). Business review passed with one explicit correction and minor caveats:
comparison superseded a loaner timing error with the correct 10–12-hour margin and
retained readiness/capacity limits. Provider access is disabled, accepted evidence
unchanged, and no additional run or commitment occurred.

The targeted definition reached coordinator requests but no service assessment or
comparison request. Therefore the trial does not establish that the new schema
description improved consumer reasoning; priority expedited still requested unnecessary
clarification. Actual consumer visibility should have been checked before paid testing.
The next proposal is a provider-free correction to delivery of that business meaning,
verified through the effective request-construction path. Keep the six/two assignment
and human business process. This recommendation authorizes no paid repeat, Sidecar,
promotion, commit or push.


## Consumer-visible definition delivery — 2026-10-07

The user approved the provider-free follow-up. One shared service-window definition
now appears in the business instructions of expedited assessment, standard assessment
and comparison. Its scope is service quotes; genuine loaner setup uncertainty remains.
No schema, binding, business fact, application behavior or model default changed.

All 44 tests passed and generation was stable. Six direct request probes verified
the definition in actual system messages for the three consumers on both integrations.
The local fixture deliberately rejected every request with provider credentials disabled:
zero upstream calls, zero model responses and no business-row changes. Expected failed
probe executions establish request delivery, not business quality. The probes reused
only current Phase 2 input objects, without replaying answers or plans or restoring
retired machinery. Both regular smoke checks passed with zero model calls; their normal
isolated quote rows were added and prior rows preserved. Captured and accepted evidence
is unchanged; provider access remains disabled.

A fresh four-case Java confirmation at the same six/two medium assignment is proposed,
with full business review and verification that the definition reaches consumer requests.
Recent cost is approximately $0.71–$0.73 per batch, not a guarantee. No paid evaluation,
Sidecar trial, accepted promotion, commit or push is authorized by this completed edit.


## Consumer-visible definition confirmation authorized — 2026-10-07

The user approved one Java batch: baseline, priority, capacity_shortfall and
later_start, with six Sol/two Luna at medium. Freeze this candidate; verify the
service-window definition in actual consumer requests and review every published
finding under the existing business criteria. Report actual cost and corrections,
preserve accepted evidence and restore provider-disabled operation. No additional
repeat, paid Sidecar, accepted promotion, commit or push is authorized.

Consumer-definition confirmation outcome: run `3da6f57214b34131994a611b2c1e54a1`
completed all four cases with 108/108 structural checks, exact handoffs and 60 valid
JSON responses, no schema corrections. Cost was $0.702841970: 24 Sol calls
($0.658566600) and 36 Luna calls ($0.044275370). The definition reached all 12 intended
consumer requests; the service-window question did not recur and genuine loaner
setup uncertainty remained.

Three cases pass business review with caveats; full acceptance is withheld for
later_start. Comparison incorrectly superseded supported per-part pricing with an
uncertainty despite receiving the manual identities and rate card. The primary
portfolio and quote cap remain defensible, but the published governing correction
fails the complete-business criterion. This is not an execution or delivery failure.

Retain the targeted consumer clarification. The next proposal is a provider-free
review of the quote/comparison boundary, including whether the deterministic quote
should expose its authoritative item-level amounts for business readers and local
assessors. Assess the tradeoffs before implementing it; do not reflexively add another
reminder or upgrade the whole pack. No further paid run is authorized. Provider access
is disabled, accepted evidence remains unchanged, and no Sidecar evaluation, promotion,
commit or push occurred. Latest and consolidated evidence retain the result.


## Quote itemization and reconciliation refinement — 2026-10-07

The user approved proceeding with provider-free review and business-justified
improvements. Both hosts now expose the existing deterministic quote calculation
as a persisted price breakdown with rate provenance, labor, identified parts and
attendance premium. Comparison must reconcile local information gaps with its wider
case evidence before publishing uncertainty or a governing correction. Preserve
conditional charging, existing prices, approval scope/cap checks and coherent skill
responsibilities. This implements a candidate remedy, not demonstrated reasoning
improvement. Latest/accepted evidence is retained and no paid trial is authorized.

Provider-free validation is complete: 44 tests, Java packaging, both integration
smoke checks and six locally rejected consumer delivery probes passed. Generation
is stable, prior business records and all evidence/fixtures remain unchanged, and
provider access is disabled. Compatibility and delivery are established in this
scope; model consistency is untested. The next proposed four-case Java six/two-medium
confirmation is documented in foundation.md and still requires agreement.


## Itemized quote Java confirmation authorized — 2026-10-07

The user approved one four-case Java confirmation of the itemized quote and evidence
reconciliation candidate: baseline, priority, capacity_shortfall and later_start.
Use six Sol/two Luna at medium, with technical assessment, four feasibility skills
and comparison on Sol; resolveEquipment and planResolution on Luna. Freeze the
candidate throughout the batch. Review exact itemization transport and all published
business findings against existing criteria, including supported corrections and
conditional charging. Report actual cost and corrections. Preserve accepted evidence
and restore provider-disabled operation. No further repeat, paid Sidecar, accepted
promotion, commit or push is authorized.


Itemized-quote confirmation outcome: run `d0cf8adf039d4def98f6edc7d1a1eafa` passes
all four business cases with minor caveats. All 108 structural checks passed; sixty
responses were valid JSON with no schema corrections. Exact quote/offer/publication
transport and itemization delivery to all twelve consumers were verified. Cost was
$0.719029125 (24 Sol calls: $0.672036500; 36 Luna calls: $0.046992625).
The false part-price uncertainty did not recur. Priority comparison made a supported
coverage-owner correction; minor inherited owner precision and redundant prose remain.
This is one batch, not demonstrated reliability. Keep this candidate unchanged and
propose two four-case Java repeats, about $1.44 combined at observed cost, subject to
separate agreement. Provider-disabled restoration and unchanged accepted evidence
were verified; no additional paid run, promotion, commit or push occurred.


## One unchanged Java repeat authorized — 2026-10-07

The user reduced the proposed two repeats to one because costs are accumulating.
Run exactly one unchanged four-case Java batch on the itemized-quote candidate,
with the same six Sol/two Luna medium assignment and complete business review.
The approximately $0.72 estimate is not a guarantee. No second repeat or automatic
paid retry is authorized. Report actual and combined candidate cost, preserve accepted
evidence, and restore provider-disabled operation. No paid Sidecar, promotion, commit
or push. Respect this preference when proposing subsequent spending.


## Model-optimization cost reflection — 2026-10-07

While the single repeat ran, the user emphasized diminishing returns from continued
mid-tier optimization: use lower tiers where they suffice and Sol where needed,
rather than keep optimizing the model mix. Evaluate authoring time, review effort
and fragility alongside model-call spend. Keep the current six/two assignment unless
a concrete worthwhile opportunity justifies reconsideration; no further paid runs
or tuning follow automatically from this repeat. This does not impose an arbitrary
effort budget or abandon the human business contract.

Distinguish necessary business/interface work from optional allocation optimization.
Historical all-Sol runs improved core decisions but still had material business-review
defects; they were not a fully accepted baseline. Some subsequent refinements benefit
either tier. Diminishing returns is a project lesson and practical preference, not a
measured universal break-even threshold or proof that mid-tier models are unsuitable.


Single-repeat outcome: `f11193ccd3024844bb38cc69d53e0d2c` passes all four complete
business cases with minor caveats. All 108 checks passed, sixty responses were valid
JSON and no schema corrections occurred. Cost was $0.718357850 (Sol $0.673290200;
Luna $0.045067650), or $1.437386975 including the preceding confirmation. All candidate
hashes and accepted evidence remain unchanged; provider access is disabled. Two
unchanged batches provide bounded repeated success, not general reliability. No
second repeat, further tuning, paid Sidecar, promotion, commit or push was performed.
Retain this practical assignment and documented caveats; further work needs a distinct
purpose rather than automatic model-cost optimization.
