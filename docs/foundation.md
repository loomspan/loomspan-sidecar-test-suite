# Phase 2 foundation

## Applications and skills

- `apps/java`: Spring Boot application embedding Framework, deterministic Java tools,
  persistent assessments/quotes/requests and authenticated public endpoints.
- `apps/python`: equivalent FastAPI business application, authenticated REST tools and
  calls to Sidecar for orchestration.
- `config/skills`: current model/planning skills (`resolveEquipment`, `assessEquipment`,
  `planResolution`, `compareOptions`), four per-option feasibility skills and compatibility skill.
- `config/rest-skills`: Sidecar declarations for the corresponding deterministic tools.
- `scripts/workflow_contracts.json` and `scripts/author_workflow.py`: current contract
  definitions and skill-generation tooling. Regeneration changes authored configuration;
  use deliberately during an agreed experiment, not as a startup prerequisite.
- `fixtures/server.py`, `fixtures/business.json`, `fixtures/base-case.json`: independent
  business source records and the local provider boundary. The fixture server's existing
  controlled-response support remains available; historical replay data is removed.

Both public apps expose assessments and service requests as well as Framework skill
execution endpoints. Java uses port 18081; Python uses 18082; Sidecar is on 18083.
The runtime guide lists infrastructure ports and isolated-workspace support.

Declared input/output bindings preserve source facts and authoritative results.
Eligible fully bound tasks dispatch directly; optional model input still leaves the
step model-driven. The current structure is a foundation to explore, not a prescribed
optimal decomposition for Phase 2.

The current Phase 2 composition has four feasibility skills, one for each service
or continuity option. Each generates eight common flat fields with short text and
string arrays. Service outputs add three explicit condition fields and two owner-
reference arrays; Framework adds the unchanged contact directory. Framework also
adds source-bound expiry, reservation state and snapshot ID to every option.
The deterministic quote operation now assembles complete offer records containing
original details, applicable snapshot identity/revision/reservation/expiry, monetary
units and the exact service quote where applicable. Framework binds one whole offer
record, source terms and operating needs to each assessor; it forwards accepted results
into `compareOptions.context.feasibility`. The planning model supplies empty call
arguments instead of constructing or copying the combined feasibility tree.
Framework also publishes that tree unchanged as `optionAssessments`. Comparison
selects a portfolio (`pursuedOptions` plus the primary `selectedOption`) and explains
tradeoffs and residual risk. It reviews material accuracy across all published
technical and option findings, including deferred options, and records governing
corrections or genuine unresolved conflicts in `reviewConcerns`, which may be empty.
It preserves original findings and explicitly identifies any superseded claim.
Comparison-generated `changeConditions` and `responsibleParty` were removed;
per-option findings own operational conditions and handoffs. Exact publication
does not establish their correctness. Equipment hypotheses are now self-contained
strings distinguishing support, contrary evidence and missing evidence. Framework
adds the original `reportedIncident` unchanged to equipment assessment.

One Java Luna 6/medium run is retained in `evidence/accepted` as a successful sample
for baseline and priority. Two unchanged repeats have since exposed a false unknown
expiry, a lost expedited-access condition, and smaller classification/completeness
gaps. GLM 5.3 completed the same cases but failed business review, including premium
double-counting, approval-routing and duration-meaning errors. All three evaluations
matched the accepted source hashes; no skills were tuned during the comparison.

Two additional Luna input variations correctly recognized insufficient loaner
capacity and standard attendance before a later production start. They changed
only scenario construction/default selection, keeping skills and business fixtures
identical. The nested equipment assessment needed two schema corrections in GLM
baseline and one invalid-JSON correction in the Luna capacity variation. Shallow
feasibility results remained valid and forwarded exactly in the observed cases.
The runner's broad failed-attempt/plan-retry counters do not count those schema
advisor corrections; see the runner guide before interpreting zero retry counts.

Those eight case executions passed 13/13 automated checks, which do not establish
business success. `evidence/validation-review.json` retains checksum-linked reviews
before raw latest evidence is replaced. The accepted sample is preserved, but general reliability and repeatable
full business correctness remain unestablished. The generator supplies separate
service/procurement approval methods while retaining shared contracts and bindings.

The direct-publication/shallow-equipment experiment ran all four cases with
Luna/medium on Java: 22/22 checks each, 60 valid JSON responses, zero schema
corrections, $0.089411250. All 16 option results and source metadata and all four
original incidents were published exactly. Core access, approval and expiry
conditions survived. Final comparison nevertheless collapsed a range to its first
endpoint, added dispatch confirmation to the price-preservation deadline, and
unnecessarily challenged an elapsed-work estimate. Source-field semantics also
need clearer expression. This is transport success with business gaps, not a new
accepted reference.

The narrow-comparison experiment ran the same four cases with
Luna/medium on Java: 23/23 checks each, 60 valid JSON responses, no schema
corrections, $0.086298925. Comparison-generated compact JSON was about 72% shorter
across these cases, excluding runtime-bound fields. The previous comparison
errors did not recur. However, baseline service findings assigned the dispatch
contact's name to the separate warranty-review record; five of eight service
findings omitted explicit renewed approval for changed attendance/scope/cap.
Equipment evidence classification also remains uneven. This supports a promising
comparison boundary, not full workflow acceptance. The consolidated
`evidence/validation-review.json` retains this run's review.

The preceding explicit-service-condition experiment completed all four cases with
27/27 checks each, 61 valid JSON responses and one schema correction for omitted
owner arrays in baseline expedited. All eight accepted service outputs retained
the targeted rules and correct owner-role references. Cost was $0.092637040;
provider-disabled runtime was restored. Equipment known-fact handling and a
temporal-wording error remain. The run is not promoted as fully accepted.

The reviewed readable baseline has now also completed four Java Luna/medium cases:
27/27 checks each, 60 valid JSON responses, zero schema corrections, $0.088279740.
Quantity-meaning and final-synthesis failures still prevent business acceptance;
see the readable-baseline and whole-tree Sol evaluation results below.

The user now prioritizes a human-recognizable business process with model capability
assigned per responsibility. Review the current boundaries before further tuning;
a mixed Sol/Luna workflow is an intended solution. No mixed-model run has occurred.

Fully bound nested inputs do not qualify for automatic dispatch in the installed
Framework implementation, which requires top-level binding destinations. The latest
runs normally have 15 model calls per scenario, including seven small call envelopes with
empty arguments, and eight automatic dispatches. This experiment addresses model
output construction; minimizing call count is a separate possible improvement.

## Business facts and interpretation

The fictional P240 revision-B sealer has recurrent E17 after warm-up, sensor replacement
and cleaning. A prior 20-minute test is shorter than the reported 35–50-minute onset.
Bulletin applicability supports investigation, not a confirmed defect. Qualified
personnel own diagnosis and return-to-service decisions.

Expedited attendance is the afternoon before production; standard attendance is after
the next morning's production start. Work can outlast normal site access. The compatible
loaner arrives in the evening and needs separately arranged access, approval and setup.
Offers expire before diagnosis, so continuity decisions cannot assume later availability.
The base case leaves restoration-risk preference unspecified.

Quoted service caps are $780 expedited and $480 standard, in integer USD cents on the
wire. The $300 expedited premium is included in its cap and payable on attendance even
if unresolved. Diagnosis/travel are included; actual authorized repair labor and installed
parts depend on findings, coverage and the approved scope/cap. Coverage remains pending
without qualifying findings. Elapsed work estimates do not enlarge approved repair hours.

Luis's recorded $1,000 ceiling accommodates either service cap after identity/permission
and explicit approval checks. The $2,400 loaner requires separate procurement approval.
An approved service request submitted before expiry preserves quoted scope/prices but
neither reserves resources nor books attendance. Changed scope/cap requires renewed
approval. Lost-result recovery and same-content idempotency use the persisted receipt.

The [source pack](equipment-service-source-pack.md) and current fixtures supply the
facts; these explanatory notes are not injected as a worked answer into model prompts.

## Current limits

The existing local runtime uses installed Framework 1.0.0-beta.8-SNAPSHOT and Sidecar
beta.2 source built against it. Both are local builds. Provider, mission and fixture-proxy
limits are 480, 2400 and 510 seconds. Normal model configuration remains Muse at medium
reasoning; retaining that default is not a model recommendation.

Phase 2 has observed improved shallow-output serialization and some business-acceptable
outputs, alongside repeat and transfer failures. General reliability is not established.
The historical evaluation machinery and semantic
reviewers are retired. The [shared runner](runner.md) now provides the four agreed modes
without an experiment-management layer. Its 38 provider-free tests cover orchestration,
failure/restoration paths and selected preservation checks. The runner has now also
been exercised in Java model evaluations. The provider-free smoke check does not verify model judgment, full approval
recovery, every Framework feature or release readiness. Sidecar's pinned source tests
are not compatible with the installed Framework API; packaging currently skips those
tests, and the smoke check is no substitute for resolving full regression coverage.

## Human business contract audit

Reviewed 2026-10-06 against `scripts/author_workflow.py`,
`scripts/workflow_contracts.json`, the generated manifests, and captured business
reviews. This is a design assessment, not stakeholder sign-off or evidence that a
revised workflow has passed. No runtime changes or paid runs were made for this
audit. Model-selection policy is in the project agreement; it takes precedence
over the earlier suggestion to begin with a Sol technical-assessment substitution.

### The process a business reader should recognize

1. Establish the asset, reported problem, production need and relevant history.
2. Assess what the evidence supports, what remains uncertain, and what a qualified
   technician needs to investigate. Do not claim a confirmed defect without findings.
3. Establish coverage/terms, available service and continuity options, and quotes.
4. Assess each viable option against timing, capacity, access, cost and approval
   requirements. Service and procurement follow their own business procedures.
5. Recommend a course of action, including a combination where justified, its
   unresolved prerequisites, residual risks and the decision now required.
6. Obtain explicit authorization and submit the chosen service request through the
   application. This is a separate action after assessment; it does not happen
   automatically during the assessment and does not itself book or restore service.

The first five steps form the assessed workflow. The sixth is the existing
separate commitment path. The underlying tree may gather independent records in
parallel without changing this explanation. Technical transport is not another
business decision. A service manager should be able to follow the recommendation
and its conditions without understanding JSON pointers or tracing tool calls.

### Boundary decisions

| Current boundary | Decision | Business justification and follow-up |
| --- | --- | --- |
| `assetContext`, `serviceHistory`, `referenceEvidence`, `serviceTerms` | Keep as evidence retrieval | Different authoritative sources support distinct facts. Expose them as gathering case evidence; do not invent separate human decision roles for each lookup. |
| `assessEquipment` | Keep coherent | Evaluating chronology, test adequacy, applicability and competing explanations is one recognizable technical assessment. Further splitting merely to force a weak model to reason correctly would fragment this judgment. |
| `entitlements`, `serviceResources`, `continuityOptions`, `quoteOptions` | Keep deterministic boundaries | These retrieve/evaluate independent business records and calculate authoritative quotes. Model capability does not justify moving financial calculation or authorization into prose. |
| Four feasibility skills | Keep the repeated option-assessment responsibility; reconsider literal duplication during authoring cleanup | Assessing repair attendance, temporary equipment and replacement is natural. Expedited/standard are variants of service assessment; loaner/replacement are continuity alternatives. Current named routes serve the runtime graph, not four artificial departments. Per-option reasoning remains defensible because each assessment has its own complete constraints. A parameterized template or family-level wrapper is an implementation possibility, not a proven need to merge calls or replace working Framework support. |
| `compareOptions` | Keep | Someone must compare the options and own the recommendation, including combined strategies. It should use the findings and resolve material conflicts without reauthoring all procedures. It must remain able to question evidence that affects the decision. |
| `resolveEquipment`, `planResolution` | Keep coordination; simplify their business explanation | Case coordination and commercial planning are recognizable groupings. Fixed task dependencies, parallel groups and empty call arguments are implementation instructions. Do not describe planner envelope calls as business work. Whether more scheduling can be deterministic is a separate implementation question, not a prerequisite for the model-selection experiment. |
| `createServiceRequest` | Keep separate | Explicit approval and verified authorization precede commitment; assessment alone does not authorize it. |
| `compatibility` | Keep outside the business tree | This is a technical provider probe, not an equipment-service responsibility. |

### Instruction and output decisions

| Current design or instruction | Decision | Reason and concrete revision target |
| --- | --- | --- |
| Source applicability, chronology, supporting/contrary evidence, known facts versus missing attributes | Keep the reasoning method | These are valid technical assessment duties, even though failures motivated clearer instructions. Consolidate overlapping reminders into a short method; do not remove evidence standards to make a model pass. |
| Correct units, elapsed versus billable work, whole-period access, price preservation versus dispatch, service versus procurement approval | Keep the business distinctions | They affect real decisions. State each principle once in its responsible skill or shared contract, rather than accumulating examples from every failed output. |
| Mandatory charging, renewed-approval and coverage-review fields | Keep as business requirements | They are recognizable conditions in a service recommendation, not invented microtasks. Explicit fields improved observed completeness. Do not split each field into a separate skill solely to make generation easier. Render them as readable conditions, not schema labels. |
| Source-bound quotes, deadlines, reservation state and accepted findings | Keep Framework ownership | Exact transport is a sound interface design for any model tier. A stronger model should not be asked to copy authoritative trees unnecessarily. |
| Owner IDs, unchanged contact directories, binding rules and empty arguments | Keep internally; simplify presentation | Source identity avoids false associations. Business readers need the role and available contact details; reference resolution belongs in presentation/assembly. The two copied directories need not become two business-facing sections. No new contact rendering has been implemented by this audit. |
| Flat hypothesis strings and prohibition on nested hypotheses | Reconsider as a serialization experiment | The business result is possible cause plus evidence, counterevidence and unknowns. A short statement may be readable, but flattening should not sacrifice those relationships. Choose the output shape for readers and consumers; test stronger-model compatibility before treating a Luna workaround as a permanent requirement. Do not reintroduce model-authored bulk handoffs. |
| One or two sentences per field; one statement per alternative | Relax unless a product requirement justifies it | These are generation-length controls, not business rules. Prefer concise but sufficient explanations; use length measurements in evaluation rather than forcing a uniform sentence count. |
| Repeated warning that an option alone does not rule out combinations | Consolidate at comparison | It was useful corrective guidance, but current outputs repeat it even where no meaningful interaction is analyzed. Each assessor should report that option's capabilities and limits; comparison owns portfolio interactions. |
| Blanket instructions not to repeat timelines, diagnoses or procedures | Replace with scoped relevance | Avoid redundant reconstruction, but allow the decision-critical fact and its qualification when a reader needs them. A business recommendation should stand on its own with accessible supporting conditions. |
| No general audit; corrections only in `reviewConcerns` | Clarify decision accountability | Avoid an obligatory second full assessment, while requiring comparison to address material contradictions. Do not teach automatic deference to a possibly wrong leaf or suppress useful verification to protect a weaker model. |
| Repeated generate-only-unbound, no-copy and correction instructions | Keep necessary interface rules in a clearly separate contract section | These are technical safeguards. Consolidate repeated wording; their presence does not imply a new business step. Removing them without verifying Framework behavior would be unjustified. |

### Recommended baseline preparation

Retain the business responsibilities above. Rewrite business-facing descriptions
and methods in that vocabulary, consolidate repetitive instructions, and separate
technical generation/transport rules from the business method. Keep the explicit
service conditions and deterministic source preservation. Reassess presentation
of diagnostic evidence and owner references for readability, without presuming
that more nesting or fewer calls is inherently better.

Review that authored baseline for recognizable responsibilities, complete
conditions and decision accountability before new model trials. Then follow the
whole-tree model ladder: lowest reasonable successful tier first; lower selected
responsibilities only if that baseline requires a relatively high tier. A mixed
assignment is not yet the default next experiment. The capability-based mixed-pack
exception in the project agreement remains available. The audit supplied the
cleanup specification; its implementation and validation status follow.

### Prepared business-readable baseline

Implemented 2026-10-06 after the user authorized baseline preparation. The eight
reasoning manifests now lead with business responsibility and method, followed by
evidence/authority principles and a separate Framework contract. The generator
keeps common option-assessment methods shared, with service and procurement
procedures supplied only to the relevant family. Generated YAML presents methods
as readable text blocks before the schemas.

Removed arbitrary sentence limits, repeated combination reminders and blanket
bans on restating useful facts. Comparison must verify decision-critical findings,
address material source conflicts and explain the facts and qualifications needed
to understand its recommendation. Matching schema descriptions now express the
same responsibility. This does not require a second full technical assessment.

Retained the existing business boundaries, explicit service conditions, owner
references, authoritative bindings, field shapes, model assignments and workflow
dependencies. Diagnostic hypotheses remain self-contained prose entries keeping
cause, supporting/contrary evidence and unknowns together. This is a reasonable
readable representation for the current consumer, not a permanent ban on structured
evidence or proof that flattening is best. No new owner-reference UI rendering was
implemented; source directories and IDs remain published as before.

Validation: all 38 provider-free tests passed. Parsed-manifest comparison confirmed
that changes are confined to prompts and descriptions; schemas' structural rules,
bindings, routing and runtime settings are unchanged. Both integrations reloaded
the shared configuration and passed the provider-disabled smoke check with zero
model calls. These checks establish configuration/integration compatibility, not
business correctness under a model.

The latest captured evaluation still describes the preceding experimental skills.
Neither it nor the unchanged accepted reference establishes success for this
revision. The baseline retains lessons from prior tuning; it is not historically
untuned. Next: independently review readability and responsibility completeness,
then agree a Java-first whole-workflow model trial using the project priorities.
No individual Sol assignment or paid evaluation was made during this cleanup.

### Independent review of the prepared baseline — 2026-10-06

Reviewed the authored methods, contract descriptions and shapes, generated manifests,
input/output bindings, source pack and fixture records, and the latest/consolidated
business reviews. This is a source-based design review, not practitioner sign-off
or a model result. The current tree satisfies a defensible human business contract:
gather evidence, assess the technical problem, assess commercial options, recommend,
then obtain authorization through the separate service-request path.

The four option routes implement one repeated responsibility with two approval
families. They are not four human roles. The two planners primarily coordinate
dependencies; their small model-generated dispatch envelopes are a Framework
accommodation, not additional business judgment. Neither calls for another split.

Remaining inconsistencies were in the interface wording, not the business tree:

| Finding | Cleanup and rationale |
| --- | --- |
| The quote description put all unquoted offers in alternatives, although procurement can be pursued. | Keep only authoritative service quotes in `quotes`; explain that procurement offers can be pursued or deferred. `selectedOption` now clearly names the primary member of `pursuedOptions`. |
| Shared approval descriptions carried service identity and pending-coverage language into procurement. | Give service and procurement output descriptions their own approval procedure. Procurement records offered exposure, included items and material unquoted costs; service retains cap and permission requirements. |
| The completion description always demanded arrival plus duration, while sources can describe a work/setup window. | Interpret a supplied window as stated, otherwise calculate only from supplied elapsed duration. This does not certify readiness or reinterpret an ambiguous delivery label as guaranteed setup completion. |
| Comparison's prompt used `reviewConcerns`, but published-option descriptions sent corrections to rationale or alternatives. | Record the affected finding, evidence and governing interpretation/open question in `reviewConcerns`, and use it consistently in the recommendation. Preserve the original child output for traceability. |
| Residual-risk and next-decision descriptions still discouraged useful restatement. | Allow decision-critical conditions, urgency and an evidenced responsible role, with references for supporting detail. Do not reconstruct the entire procedure. |
| Offer assessment did not explicitly own offered exposure and unquoted costs. | Add this duty to the shared method and use procurement's existing approval field for its financial handoff. No new field or cost-estimation step is needed. |

Retained choices and limits:

- **Diagnostic prose:** a possible cause with evidence and unknowns is a sensible
  readable unit. Its flat representation originated partly in serialization
  experiments; it does not structurally enforce evidence relationships, and prose
  classification errors remain observed. Keep it for this trial; do not treat
  nesting as prohibited or further split technical judgment to help one model.
- **Explicit service conditions:** charging, changed scope/attendance/cap and
  coverage review are actual contractual duties. Separate fields are justified
  even though omissions motivated them. The prior eight accepted service outputs
  support promising completeness, with one schema correction, not reliability.
- **Owner references:** source-record identity is a sound interface requirement.
  Duplicate published directories and raw IDs are presentation overhead. A future
  reader-facing view should resolve each ID to its role and available contact
  details without borrowing missing names or granting permissions. No such view
  was implemented here; source-linked data alone is not proof of handoff usability.
- **Direct publication:** exact transport can preserve a wrong finding. A clear
  correction must govern the recommendation; conflicting instructions must not be
  left for a business reader to reconcile. The amended wording is an untested
  remedy, not evidence that comparison now catches every material error.
- **Closed scenario contract:** all four offers are required, quote coverage is
  constrained to PENDING, and fixtures do not exercise absent offers, other coverage
  outcomes or equipment red flags. These are current evaluation limits, not general
  business rules. Broadening them is a separate agreed scope, not necessary cleanup.

No skill boundaries, field shapes, validation constraints, bindings, source fixtures
or model assignments changed. Schema descriptions were updated at their embedded
consumer copies too. The design still needs model evaluation and practitioner review.

Provider-free validation after this review: 38 tests passed; a second regeneration
was byte-stable; parsed comparisons with a pre-review snapshot confirmed changes
only to prompts/descriptions and matching embedded producer/consumer contracts.
Both integrations reloaded the shared manifests through the documented runtime
helpers and passed smoke checks with zero model calls and prior rows preserved.
The smoke check added its isolated quote rows as documented. Accepted and latest
evidence hashes remained unchanged. No model evaluation, commit or push occurred.

### Readable-baseline whole-workflow experiment scope

The following proposal was authorized by the user's subsequent “proceed” and
completed as one batch. Its predeclared criteria are retained below; results follow.
No repeat or next-model run is authorized.

Run **one Java evaluation, four cases**, using the previously exercised provider ID
`openai/gpt-6-luna`, requested `medium`, for all eight reasoning skills and their
planning/action calls. Keep deterministic tools unchanged. This is a bounded test
of the revised readable baseline at a plausible lower tier, not another open-ended
all-Luna tuning sequence or a claim about current market rankings. The ID has local
execution evidence; recheck provider availability before an authorized run. Dry-run
selection validates runner arguments, not provider availability.

Freeze current authored skills, contracts, fixtures and runtime settings during the
batch; record source hashes and effective configuration. Use the existing runner:

```powershell
# Preview only. Remove --dry-run only after explicit scope agreement.
.venv/Scripts/python.exe scripts/run_suite.py evaluate --path java --model openai/gpt-6-luna --reasoning medium --scenario baseline --scenario priority --scenario capacity_shortfall --scenario later_start --dry-run
```

Cases and business acceptance:

| Case | Required implication; no single fixed answer |
| --- | --- |
| baseline | A defensible service/continuity choice with explicit restoration risk under unspecified risk preference. Do not silently assume procurement approval or that a loaner remains available after diagnosis. |
| priority | Honor the stated continuity preference: urgently pursue/escalate the feasible loaner approval while retaining diagnosis as justified; preserve both options' conditions. |
| capacity_shortfall | Recognize 20/minute against 25/minute as a 5/minute shortfall. Any partial benefit needs explicit limits; do not add unknown repaired capacity or call the loaner sufficient. |
| later_start | Standard arrival at 10:00–12:00 is 4–6 hours before 16:00 production; completion remains unestablished. The recoverable-delay endpoint is 18:00. Reconsider the tradeoff without promising restoration. |

Review every technical assessment, all sixteen option findings, all eight service
condition/owner handoffs, and all four final recommendations against sources:

1. Retain the reported three recurrences, attributed chronology, known 20-minute
   test and 35–50-minute onset. Unknown initial thermal state is distinct from known
   duration. Bulletin applicability is not diagnosis; relevant context is not
   automatically support or counterevidence. Questions must seek genuinely missing
   facts; no invented authors, dates, technical clearance or confirmed parts need.
2. Retain ranges, units, reference events and activity meanings. Expedited estimated
   work can extend to 20:00 beyond 18:00 access; loaner delivery/setup at 20:00–22:00
   also needs access arrangements. Standard elapsed work is unknown. A three-day
   rental is not setup time; two billable repair hours do not bound elapsed work.
   No interpretation should turn pre-start completion into time inside a post-start
   delay interval. Unknown replacement lead-time triggers/calendars stay unknown.
3. Preserve the 11:00 expiry implications: approved service submission preserves
   scoped prices, not resources; dispatch confirmation is not an added price-deadline
   prerequisite. Do not assume a post-diagnosis loaner fallback is available.
4. Explain $780/$480 service caps and the included $300 expedited premium without
   double-counting; caps are not invoices. Diagnosis/travel are included; justified
   actual repairs depend on findings, coverage and scope. Preserve renewed approval
   for changed attendance/scope/cap, new quote for extra work and incomplete/disputed
   coverage review. Select dispatch and warranty owners from their separate records.
5. Keep verified service permission and explicit cap approval separate from directory
   limits and external procurement. Explain the $2,400 loaner exposure and replacement's
   unquoted installation; do not invent approval, acceptance or fulfillment.
6. Make the recommendation readable with its primary option, pursued portfolio,
   urgency, handoff, conditions and residual risk. Address material conflicts with
   evidence and consistent consequences. An empty `reviewConcerns` is not a pass.

Execution acceptance requires all 27 structural checks per case, exact input/result
transport and publication, complete captures, no unintended commitment, unchanged
prior rows and provider-disabled restoration. Count raw JSON errors, schema
corrections, plan/action failures, calls, cost and latency separately. A corrected
response can yield an accepted outcome if the accepted result is sound; it cannot
be described as first-attempt success. Do not rerun a failed case automatically.

Business acceptance requires all four complete results to be materially correct,
internally consistent and usable, including published leaf findings. A correct final
choice does not excuse incorrect technical evidence or a misleading operational
condition. Clearly superseded provisional errors remain recorded defects; assess
their reader impact rather than counting exact publication as semantic success.
Minor stylistic differences are allowed. No paid service-request or Sidecar testing
is included. Preserve `evidence/accepted`; retain the existing checksum-linked review
before replacing latest under the documented retention policy.

A pass is one successful batch; propose two unchanged four-case repeats separately
before claiming repeatability. A material failure ends this candidate's trial on
this baseline: locate the first incorrect responsibility and propose either a
stronger whole-tree candidate or a justified capability-specific mixed pack under
priority 4. Neither further paid runs nor model-specific rewrites are preauthorized.

### Readable-baseline evaluation result — 2026-10-06

Run `a702010c55224d29b085a37631828eee` completed the agreed four Java cases using
Luna/medium with unchanged sources. Each passed 27/27 checks and used 15 model calls;
all 60 raw responses parsed as JSON, with no schema corrections, rejected actions,
failed model attempts or plan retries. Reported total cost was $0.088279740; case
trace durations were 106–110 seconds. All sixteen option inputs and forwarded/
published results, source metadata and four equipment handoffs were independently
verified. The runner restored normal runtime; provider-disabled status was checked
independently. Accepted evidence remained unchanged.

**Full business acceptance is rejected.** Core choices were mostly defensible,
and both constraint variations met their targeted implications. All eight service
outputs retained the dedicated charge/change/coverage conditions and correct owner
references. Those successes coexist with material errors:

- Priority and capacity-shortfall standard feasibility estimated completion at
  12:00–14:00 from two quoted billable repair hours. Standard elapsed work duration
  is unknown. Baseline and later-start correctly preserved that unknown.
- Capacity-shortfall comparison introduced a false conflict between expedited's
  2–4-hour elapsed work estimate and two authorized repair hours. Diagnosis is
  included in elapsed work; the difference alone does not require a new approval.
  The leaf's correct estimate was wrongly challenged in `reviewConcerns` and rationale.
- Later-start comparison said the $300 fully covered maximum excludes the premium,
  although it consists of the premium excluded from warranty. The leaf stated this
  correctly; other final prose retained the correct rule, leaving a contradiction.
- Later-start technical questions reopened the known test duration without naming
  unknown initial thermal state. Priority again treated the short no-recurrence
  test as limited contrary evidence without establishing a discriminating test.

Additional caveats include service/procurement approval wording beyond the selected
caps, a context-property citation, and service leaves making portfolio suggestions
without sibling-offer information. The loaner's `arrival` and `packageIncludes`
labels leave setup-window semantics ambiguous; conservative readiness uncertainty
is not itself a demonstrated failure. That producer clarification remains a separate
hypothesis, not an excuse to accept unsupported claims or to rewrite this run.

The combined cleanup cannot isolate which wording changes affected which outcomes.
Readable methods did not establish reliable quantity interpretation or synthesis.
Keep this baseline and its coherent responsibilities; do not fragment it further
to pursue an all-Luna pass. The checksum-linked full review is in
`evidence/latest/business-review.json` and `evidence/validation-review.json`.

**Next proposal, not authorized:** one Java `openai/gpt-6-sol`/medium batch on the
same frozen tree, four cases and acceptance criteria. The provider catalog lists
that ID and reasoning parameters; this is not a guarantee of capability or outcome.
Failures now span technical assessment, service feasibility and comparison, making
a whole-tree capability test useful before choosing a narrow substitution. A
capability-specific mixed pack remains permissible; whole-tree promotion is not
a prerequisite. No repeat, new paid evaluation, Sidecar run or skill rewrite followed.

### Whole-tree Sol evaluation result — 2026-10-06

The user subsequently authorized the proposed Sol batch. Run
`734b09c4c74e47eebeb39dba36a3c1de` used `openai/gpt-6-sol`/medium on the same
four Java cases and exactly the same source hashes as Luna. Each passed 27/27
structural checks and used 15 calls. All 60 raw responses parsed as JSON; detailed
traces had no schema corrections, rejected actions, failed model attempts or plan
retries. All sixteen option handoffs and four equipment paths were independently
verified, including source inputs and exact publication. Provider-disabled runtime
was independently verified after restoration; accepted evidence is unchanged.

Reported cost was $1.505192300, about 17.05 times the preceding Luna batch's
$0.088279740. Mean case trace duration was 88.33 seconds versus 108.53 seconds.
These are observations from one batch each, not stable cost/latency estimates or
a general capability ranking. Model configuration defaults remain unchanged.

Sol avoided the preceding Luna batch's billable-duration estimates, false
elapsed-work/scope conflict, premium inversion and reopening of known test duration.
All eight dedicated service-condition/owner outputs held. The four core choices
were defensible: baseline and later-start retained explicit cost/risk uncertainty,
priority honored continuity preference, and capacity-shortfall required evidence
of supplemental capacity before committing to the undersized loaner. The latter
is a valid conditional pursuit, not an assumption that unknown capacity can be added.
Later-start correctly recalculated standard timing while retaining unknown completion.

**Full acceptance remains withheld for published reasoning, not the portfolio
choices.** Capacity-shortfall replacement feasibility says ordinary access beginning
at the 08:00 delay endpoint leaves zero hours for setup before the deadline. That
implicitly restricts setup to the production morning without an established arrival
date; daily access also exists on the preceding day. The ten-business-day lead
independently makes replacement unsuitable, so the final rejection remains sound,
but the added operational rationale is unsupported. Service leaves in that case
also call loaner cost/availability unknown without qualifying their limited input
scope, alongside the complete published loaner offer. Exact publication preserves
these defects; a correct choice does not make every supporting finding correct.

Separate caveats are not counted as demonstrated capability failures: priority
reads the loaner delivery/setup window as conditional offered completion by 22:00,
while other cases preserve unknown setup completion; the mixed `arrival` and
`packageIncludes` labels leave that interpretation unclear. Larger-service approval
wording also inherits ambiguity from AUTH-NB, outside the selected caps. Clarifying
those business interfaces is different from tuning around model weakness.

The current latest and consolidated business reviews retain exact excerpts, source
bases and per-case conclusions. Do not promote this run, claim repeatability, or
assume the next step is another model upgrade. Recommended next work, not yet
authorized: a provider-free review of source time semantics, published per-option
scope and the unsupported access inference. Preserve the coherent tree. Agree any
resulting business/interface clarifications before a separate Sol four-case
confirmation; no paid repeat, mixed pack, Sidecar run or skill rewrite was performed.

### Provider-free source/interface review — 2026-10-07

The user authorized the recommended follow-up. Checked the captured findings against
the source pack, fixture records, authored methods, embedded schemas and both request
implementations. The remaining issues do not justify another business responsibility
or a larger input tree for every option assessor.

Implemented three general clarifications in the shared option method and matching
schema descriptions, including all embedded consumer copies:

- Apply recurring access hours to established activity dates. Without a dated work
  period, report the scheduling condition rather than inventing a total number of
  available hours. This addresses the unsupported inference without hard-coding
  a particular date, zero-hour example or preferred option.
- Scope findings and unknowns to the offer under assessment. Refer other-option
  questions to their assessments and comparison. A service assessment can correctly
  say a loaner is outside its quote; it should not claim the case lacks a loaner
  price just because that input belongs to a different assessor. The full portfolio
  remains comparison's responsibility; no extra model call or duplicate source
  binding was added.
- Interpret timing labels alongside offered scope. If arrival versus setup
  completion remains ambiguous, name that ambiguity for provider clarification.
  Do not manufacture a readiness guarantee or discard an explicit setup window.

The loaner source still uses `arrival` alongside `packageIncludes: delivery and
setup window`; the source pack calls it a delivery/setup window. This review does
not change those records or declare a new completion guarantee. An explicit
supplier event/window definition would improve the source interface, but choosing
its meaning is a business-source clarification, not a finding established by a
provider-free test. The pending confirmation should inspect whether the method
preserves that ambiguity usefully rather than choosing a convenient interpretation.

An implementation check qualifies the prior larger-service caveat: both Java
`Business.createServiceRequest` and Python `business.create` require subject `luis`
and reject approval caps above 100000 cents. Therefore the present application
does not implement a larger-service approval route through Priya either. The source
directory still describes broader business routing and cannot authorize that action.
This is static code evidence, not a newly executed authorization test or permission
change. Historical reviews remain unchanged; their statement that larger service
authorization was not exercised remains true.

The edits change only methods and field descriptions. Shapes, validation constraints,
bindings, model assignments, application code and fixture values are unchanged.
All captured and accepted evidence remains intact. These are proposed remedies with
no post-edit model result; the Sol batch evaluated the preceding wording.

Validation: all 38 provider-free tests passed; regeneration was byte-stable;
producer and embedded consumer contracts matched. Parsed before/after comparisons
confirmed that only prompts/descriptions changed. Both integrations reloaded the
shared manifests through the runtime helpers and passed smoke checks with provider
access disabled, zero model calls and previous business rows preserved. The smoke
check added its isolated quote rows as documented. Evidence, source fixtures and
application-code hashes remained unchanged.

Next proposed paid scope remains one Java Sol/medium confirmation on baseline,
priority, capacity_shortfall and later_start, using the existing complete business
criteria plus explicit review of dated access calculations, scoped unknowns and
window ambiguity. It would test the combined method/description clarification,
not isolate each change. No paid run or repeat is authorized by this review.


### Sol confirmation result — 2026-10-07

Authorized run `ad12aaba4d514fabb5c17def0dde3c7e` evaluated the amended frozen
baseline on Java Sol/medium across baseline, priority, capacity_shortfall and
later_start. Each passed 27/27 structural checks. All sixteen option source/result
paths and four equipment handoffs were independently verified. Of 61 raw responses,
60 parsed as JSON; capacity comparison used one successful correction after malformed
JSON. Detailed traces expose that correction despite zero broad retry/failure counters.
There were no separate schema-only corrections. Reported cost was $1.5304466; mean
case trace duration was 96.21 seconds. These are one-batch measurements.

The three targeted clarifications held: replacement findings retained unknown
activity dates, local unknowns were scoped, and every loaner finding named the
arrival/setup ambiguity. Capacity replacement still mentions no ordinary-access
time specifically on the production morning before 08:00; that limited statement
is true, but unnecessary. It no longer claims a total across unestablished dates.
All eight dedicated service-condition and owner findings held. Technical assessment
retained test duration, recurrence facts and qualified uncertainty. Capacity-shortfall
recognized the five-unit/minute deficit; later-start correctly recalculated standard
arrival margins without inferring elapsed completion from billable hours.

**Core decisions pass; full acceptance remains withheld.** Later-start comparison's
replacement alternative says: “Its separate procurement approval and unreserved
offer also expire at 11:00.” The source expires the offer, not approval. Approval
must be sought in time to pursue the offer; that does not establish an approval
expiry rule. The replacement leaf correctly separates these facts. This is a narrow
new final-stage defect in a deferred alternative, not failure of the primary portfolio
or the targeted fixes. It nevertheless prevents an unqualified claim that the
published business findings are correct. No automatic prompt patch follows.

Minor caveats remain: repetitive handoff prose, unnecessary questions about clearly
labeled service arrival, and a correctly qualified but unnecessary two-hour output
calculation for the undersized loaner. These do not independently block acceptance.
The checksum-linked review records excerpts, source bases and all case conclusions.
Source/configuration hashes and accepted evidence were verified unchanged through
the run; provider-disabled restoration was independently checked. Shared Java/Sidecar
skills and default assignments remain intact; paid Sidecar remains untested.

**Next proposal, not authorized:** one unchanged Java Sol/medium batch on the same
four cases. This tests recurrence before another capability attribution or compensating
rewrite. Apply the existing full business criteria to every published finding, including
approval versus offer expiry, and count formatting/schema corrections separately.
A passing repeat would be one passing sample, not repeatability proof. The observed
$1.53 batch cost is context, not a guaranteed budget. No additional paid run, accepted
promotion, mixed pack, commit or push is implied.


### Mixed-pack result — 2026-10-07

The user authorized the proposed four-Sol/four-Luna Java pack, replacing the proposed
all-Sol repeat. Run `689ab4210f1242658c2b7e802e47f678` kept the preceding batch's
business methods, schemas, bindings and source facts. Sol/medium handled
assessEquipment, assessExpeditedFeasibility, assessStandardFeasibility and
compareOptions. Luna/medium handled resolveEquipment, planResolution,
assessLoanerFeasibility and assessReplacementFeasibility. The runner now accepts
temporary per-skill model overrides for either integration; no authored default
changed. Its mixed routing checks verify trace skill/model pairs and provider counts.
All 41 provider-free tests passed, including both-host overlay and swapped-routing tests.

All four scenarios passed 27/27 checks. Sixty of sixty raw responses were valid JSON,
with no detailed schema/format corrections, rejected actions, failed model attempts
or plan retries. Independent review verified all sixteen option input/result paths,
metadata, quotes and four equipment handoffs. Captured effective configuration and
request traces confirm the intended assignments. There were four Sol and eleven Luna
calls per case; equal skill counts do not mean equal call counts.

| Model | Calls | Reported cost |
| --- | ---: | ---: |
| Sol | 16 | $0.49692480 |
| Luna | 44 | $0.05567843 |
| Total | 60 | $0.55260323 |

The total is 63.9% below the preceding all-Sol batch's $1.5304466. Mean case trace
duration was 108.98 seconds versus 96.21 seconds. These are observations from one
batch each; the earlier batch also incurred one correction. Neither batch is fully
business accepted, so this is not an equal-accepted-quality or stable latency claim.

**Core decisions pass; full business acceptance remains withheld.** Baseline and
later-start exposed unspecified risk preference and made conditional combined
pursuits. Priority honored the continuity preference. Capacity-shortfall retained
the five-unit/minute deficit and required an operations judgment about partial
benefit rather than assuming combined capacity. Later-start recalculated the 16:00
start and 18:00 delay endpoint without treating billable hours as elapsed completion.
All eight service-condition and owner findings held. All Luna procurement findings
retained timing uncertainty, separate approval/acceptance, price conversion and
arrival/setup ambiguity. No prior premium inversion or approval-expiry invention
appeared in final comparison.

Remaining defects are localized:

- Priority's Luna loaner finding identifies Beacon dispatch as the responsible
  provider role for setup and terms. Capacity's Luna replacement finding explicitly
  assigns supplier lead-time and acceptance work to Erin Cole. The directory names
  Erin for service dispatch, but the continuity offers supply no relationship
  establishing Beacon/Erin as their supplier. This can misroute a business handoff.
  Comparison leaves these published claims uncorrected.
- Priority's Sol equipment questions ask for the August test's duration despite
  preserving the supplied 20 minutes elsewhere. This violates the known-versus-missing
  evidence criterion; stronger-model assignment does not eliminate review needs.
- Later-start's Luna replacement expiry prose inserts service-only S-5 without an
  explicit applicability limit. It still asks for the replacement provider's process,
  so record ambiguous process mixing rather than a definite price-preservation promise.

The review links exact excerpts to source records and separates these findings from
stylistic caveats. Retain the coherent mixed design as promising, not an accepted
baseline. A supplier-role relationship must be sourced or remain unknown; a source
reference cannot validate an invented relationship. Do not automatically patch prompts,
add micro-skills or return to a whole-Sol run. These localized observations can justify
a separately agreed procurement-model comparison, while Sol's own evidence handling
still requires review. No further paid experiment is authorized by this result.

Provider-disabled restoration, unchanged authored/configuration sources and unchanged
accepted evidence were independently verified. Both runtime overlays remain equivalent;
paid Sidecar is deferred. No accepted promotion, commit or push occurred.


### Six-Sol/two-Luna result — 2026-10-07

Authorized run `387bca13bebb4ee386e548fd4c1d2414` moved loaner and replacement
feasibility to Sol/medium, retaining the other four Sol assignments and Luna/medium
coordination in resolveEquipment and planResolution. Methods, schemas, bindings,
source facts, authored defaults and runner code were unchanged. Temporary overrides
and captured trace routing establish the effective six/two assignment.

All four cases passed 27/27 checks. All sixty responses were valid JSON with no
schema/format corrections, rejected actions, failed model attempts or plan retries.
Independent checks verified all sixteen option paths, four equipment handoffs and
exact final publication. Usage was six Sol and nine Luna calls per case.

| Model | Calls | Reported cost |
| --- | ---: | ---: |
| Sol | 24 | $0.65695000 |
| Luna | 36 | $0.04398581 |
| Total | 60 | $0.70093581 |

Cost increased 26.8% from the four/four mixed batch, remaining 54.2% below the
all-Sol confirmation. Mean case trace duration was 107.79 seconds, versus 108.98
for four/four. These are single-batch measurements, not stable performance estimates
or comparisons of accepted-quality baselines.

The targeted procurement issues did not recur: all eight procurement findings leave
supplier responsibilities with an unnamed provider, retain supported internal contacts,
and separate procurement acceptance from service-request price preservation. No known
test duration was reopened. Baseline's expedited-only pursuit includes an explicit
pre-expiry decision on the loaner; priority honors continuity; capacity requires an
operations decision about the five-unit/minute shortfall; later-start recalculates
standard timing while retaining unknown completion. These are defensible choices.

**Full acceptance remains withheld for a narrow operational inconsistency.** In
later-start, assessExpeditedFeasibility's unresolved list says the 2–4-hour work
estimate exceeds the quote's two-hour repair-labor scope at its upper end, followed
by a new-quote/approval requirement for additional work. Elapsed work includes
non-billable diagnosis (S-3); four elapsed hours do not establish more than two
repair hours. New approval depends on actual changed/additional scope, not this
numerical difference. The same output's completion and scope fields correctly
distinguish these quantities, but comparison does not supersede the misleading
implication. No claim that all four hours were billed or that approval occurred is
made by this review. The earlier baseline final also juxtaposes these quantities
imprecisely, though less categorically; its leaf fields preserve the distinction.

All eight dedicated service charge/change/coverage fields and owner references held;
the defect lies in other published prose. This reinforces the need to review the
whole finding. Stronger assignment improved the targeted procurement outputs in
this sample but did not establish overall reliability. The technical duration
improvement occurred without changing that skill's model, so it cannot be attributed
to the procurement upgrade.

Preserve the six/two candidate. Investigate the localized elapsed-work/billable-scope
implication before reliability repeats; do not automatically upgrade the two
coordination skills or fragment the process. No further paid run or skill edit is
implied. The runner's existing 41 provider-free tests cover the unchanged override
mechanism; no code change required a fresh test run for this assignment-only trial.
Provider-disabled restoration, frozen sources and unchanged accepted evidence were
independently checked. Paid Sidecar remains deferred; no commit or push occurred.


### Elapsed time and repair scope clarification — 2026-10-07

The user authorized a provider-free skill refinement after reaffirming that readable
business-process improvements remain welcome. In the shared service method, elapsed
visit time now explicitly governs scheduling while repair labor is assessed against
its billable allowance. Included diagnosis or other included activities may contribute
to elapsed work. A numerical difference between the visit estimate and repair allowance
does not establish additional repair scope. Changes to attendance, repair scope or
cap still require the applicable approval; work beyond approved scope or cap still
requires the supplied new-quote procedure. Unknown repair requirements stay unknown.

Updated chargeCondition and scopeChangeCondition descriptions in the source contracts
and embedded consumers, then regenerated the shared manifests. This places the
clarification in the service assessor's existing responsibility and the meaning of its
published fields. Comparison already owns decision-critical verification; no new
reviewer, micro-skill, fixture-specific arithmetic or additional comparison reminder
was added. The tradeoff is slightly more explicit service guidance, in exchange for
stating the business trigger for action rather than merely naming different units.

The tree, schema shapes, validation constraints, bindings, model defaults and source
facts are unchanged. Prior captured outputs and reviews remain historical evidence;
this revision has not been evaluated with a model. The method's semantic benefit is
proposed, not demonstrated by passing provider-free checks. An eventual confirmation
should retain the six-Sol/two-Luna assignment and four cases, inspect all published
prose for scope implications, and preserve the complete business criteria; that paid
scope requires separate agreement.


Validation of the elapsed-time/scope refinement: all 41 provider-free tests passed;
regeneration was byte-stable and producer/embedded service contracts matched.
Parsed before/after checks confirmed only methods and descriptions changed, with
shapes, constraints and bindings preserved. Both integrations reloaded the shared
manifests through the runtime helpers and passed provider-disabled smoke checks with
zero model calls and previous business records preserved. Smoke added its documented
isolated quote rows. All captured/accepted evidence and source fixtures remained
unchanged. This establishes compatibility, not post-edit business acceptance.

### Scope clarification confirmation — 2026-10-07

Authorized Java run `10511fac0dee462ab9dffdcf8b5e69ff` tested the revised service
method and matching descriptions on baseline, priority, capacity_shortfall and
later_start. Sol/medium performed technical assessment, all four feasibility
assessments and comparison; Luna/medium retained resolveEquipment and planResolution.
The tree, schema shapes, bindings, fixtures and assignment match the prior six/two
batch. Methods and descriptions changed together, so their effects are not isolated.

All cases passed 27/27 structural checks. Independent review verified source and
bundle hashes, all sixteen option paths, equipment handoffs, exact final publication
and effective model routing. All 60 responses parsed as JSON; detailed correction
events, rejected actions, failed attempts and plan retries were zero.

| Model | Calls | Reported cost |
| --- | ---: | ---: |
| Sol | 24 | $0.659913900 |
| Luna | 36 | $0.043826495 |
| Total | 60 | $0.703740395 |

Mean case trace duration was 105.47 seconds. Observed cost was 54.0% below the earlier
all-Sol confirmation; those batches had different business outcomes, and neither
stable savings nor equal accepted quality follows from this comparison.

**Single-batch business pass with minor caveats.** Across all eight service outputs
and final comparisons, elapsed visit time no longer establishes a repair-scope
overrun. Included diagnosis/travel, conditional actual repair charges, the uncovered
attendance premium, approval changes and new-quote triggers remain intact. Standard
completion stays unknown. All procurement assessments retain appropriate unnamed
provider ownership and separate service versus procurement procedures.

Baseline and later-start pursue expedited with a conditional loaner, acknowledging
unspecified risk/spending preference. Priority selects the loaner with expedited
investigation. Capacity-shortfall escalates the five-unit/minute gap and requires a
credible capacity plan rather than inventing combined output. Later-start recalculates
standard's 4–6 hours before 16:00, retains unknown completion and the 18:00 delay
endpoint, and explicitly reviews loaner setup ambiguity. Technical assessments retain
the reported recurrence, test inadequacy, provenance and qualified-person boundary.

The baseline question asks the duration of “WO-0820's 20-minute test.” That is a
redundant question and misses the goal of asking only unknown facts, but its own
wording and chronology retain the correct duration. Unlike a missing fact or wrong
operational trigger, it does not change the diagnosis, approval or handoff. This
review applies the existing material-correctness threshold, not a claim of flawless
question compliance. Baseline also loosely calls the loaner offer a cap, while its
price, inclusions and unquoted extras remain clear. Capacity's general uncertainty
groups confirmation with expiry, but its concrete action correctly submits the
approved service request before expiry and obtains dispatch confirmation separately.

Capacity standard explicitly notes that no separate owner for incomplete coverage
findings is recorded. W-7 requires pending review with a responsible reviewer;
CONTACT-WARRANTY explicitly describes disputed findings. The assessment retains
pending status and that source reference, rather than inventing a named owner or
denial. Confirm ownership of incomplete-but-undisputed review in any operational
implementation. This is a source-role ambiguity to retain transparently, not a
reason to broaden directory authority silently. Framework field references and
repetitive assessment-boundary wording remain readability opportunities.

The combined clarification is now promising with an observed targeted success;
one batch does not prove causality or reliability. Keep this candidate unchanged
for two separately authorized Java repeats of the four cases, with the same full
business criteria and explicit monitoring of the caveats. At this batch's observed
cost, two repeats would total about $1.41; this is an estimate, not a spending cap
or authorization. Do not add micro-skills or upgrade coordination merely to erase
minor wording differences.

The revised sources had already passed 41 provider-free tests, stable regeneration
and both provider-disabled integration smoke checks. This trial made no further
implementation changes. Frozen source hashes, unchanged accepted evidence and
provider-disabled restoration were independently verified. Latest and consolidated
reviews contain the same checksum-linked business judgment. Business acceptance of
this sample does not promote `evidence/accepted`; defaults remain unchanged. No
paid Sidecar, repeat, commit or push occurred.

### Two unchanged mixed repeats — 2026-10-07

The user authorized two further four-case Java batches with the exact methods,
contracts, bindings, fixtures and six-Sol/two-Luna medium assignment from the scope
confirmation. Both completed; frozen and accepted-file hashes were checked before
and after, and runtime routing and all source/result handoffs were independently
verified. No implementation change occurred between runs.

| Batch | Run | Business result | Reported cost | Mean case trace |
| --- | --- | --- | ---: | ---: |
| Repeat 1 | `1ee7f7e930d943098d2806a53fe0795e` | 3/4 complete cases pass; batch withheld | $0.705831760 | 105.13 s |
| Repeat 2 | `917e33b863974d9da619a2ae3c290d64` | 4/4 pass with minor caveats | $0.702238010 | 130.79 s |

Each case passed 27/27 structural checks: 216/216 across both repeats. All 120 raw
responses were valid JSON, with no schema corrections, rejected actions, failed
model attempts or plan retries. Sol made 48 calls costing $1.323521900; Luna made
72 costing $0.084547870. Combined cost was **$1.408069770**, or $2.111810165 including
the preceding confirmation. The second later-start trace took 193.10 seconds without
extra calls; these observations do not establish stable latency or cost.

**Complete business repeatability is not established.** Repeat 1's capacity-shortfall
replacement expiryCondition says:

> CONTINUITY-017 is the bound offer source while the replacement is REPLACE-017:
> clarify whether this deadline applies to the replacement and what action, if any,
> preserves its price.

The parent snapshot supplies the deadline for its replacement offer. The input
description explicitly calls offerExpiresAt the expiry of this offer snapshot and
offerSourceId the parent snapshot's identifier. The exact input and final metadata
retain September 29 at 11:00. Provider acceptance/price-preservation actions are
legitimately unknown; the deadline's applicability is not. This finding invents
uncertainty from the parent/child identifiers. Comparison leaves it unresolved.
Replacement is deferred and the core portfolio remains defensible, but complete
acceptance includes the published nonselected findings. Correct metadata beside
misleading deadline prose does not cure it. The second repeat did not reproduce
this failure, which does not erase the first sample.

The elapsed-time/scope clarification held in all sixteen service findings and eight
final decisions from these repeats. Including confirmation, twenty-four service
findings across three batches avoided the targeted numerical scope-overrun inference.
The combined method/description refinement therefore has repeated support in these
fixed cases, while its separate contributions, transfer and overall reliability
remain unestablished. Both repeats retained supported service/procurement roles;
none reopened the known 20-minute test duration.

All eight core portfolios were defensible. Repeat 2 baseline selected expedited
alone with explicit fallback risk and a pre-expiry loaner decision; other baseline
and later-start cases conditionally pursued both. The unspecified risk preference
permits these differences. Both priority cases pursued the loaner with expedited
diagnosis; both capacity cases identified the five-unit/minute deficit without
inventing combined capacity. Later-start cases recalculated standard timing while
keeping completion unknown and the 18:00 delay endpoint separate.

Minor caveats remain. Repeat 1 baseline imprecisely distinguishes pending coverage
from the known conditional fully-covered maximum. Repeat 2 priority conservatively
questions whether estimated work covers the full visit without changing the estimate
or inventing extra charges. Repeat 2 capacity summarizes the September operator
entry as having no exceptions, although the source specifically reports no visible
window obstruction; precise chronology and the absence of internal findings remain
clear, and no technical clearance follows. Loose loaner-cap terminology, compressed
cleaning/recurrence wording and inconsistent repetition of the no-review-trigger
clause are recorded in the per-run reviews. They are not described as flawless
compliance, but do not change a material decision or introduce an operative false
rule in those cases.

Seven of eight complete repeat results passed review; one did not. These are
judgments on fixed scenarios, not independent statistical samples supporting a
general success rate. Preserve the candidate and investigate how existing offer
assessment and comparison responsibilities distinguish supplied terms from genuine
source conflicts. The relevant contract is already explicit, so another reminder
is a hypothesis, not an established remedy. A provider-free review is the recommended
next step; do not automatically add a skill or upgrade the pack, especially since
both the failing assessor and comparison already use Sol.

Both checksum-linked reviews are retained in `evidence/validation-review.json`,
with a separately scoped combined repeat review; latest holds the second batch.
The historical aggregate remains explicitly limited to its original experiments.
Provider-disabled restoration and unchanged accepted evidence/defaults were verified
after each batch. The existing 41 provider-free tests cover the unchanged runner;
no fresh implementation tests were needed. No further paid run, paid Sidecar,
accepted promotion, commit or push occurred.

### Complete offers and publication review — 2026-10-07

The user authorized a provider-free redesign after the unchanged repeats exposed
false uncertainty about a supplied expiry and a gap in review of deferred findings.
The revision keeps eight reasoning responsibilities and the six/two medium candidate
assignment. It changes the representation and accountability rather than adding a
micro-skill or naming a particular failing scenario in the method.

The existing `quoteOptions` operation returns its unchanged quotes and an additional
`offers` map. Each offer contains `option`, unchanged `details`, `expiresAt`,
`reserved`, `sourceId`, `sourceRevision`, `monetaryUnit`, and an exact `quote` for
service options. Procurement prices and scope remain in their original details;
no service quote is invented for them. Both Java and Python use the same source
records and arithmetic. The operation performs one additional continuity lookup;
its established quote persistence and authorization behavior remain intact.

Each feasibility skill receives one complete offer via a whole-object binding.
The old separate expiry/reservation/source fields and the array containing both
service quotes are removed from its input. Output metadata keeps its existing public
shape and is bound from the complete offer. Comparison receives the complete offers
alongside original source records and exact quotes, preserving evidence for checking
the assembly and findings. The structural publication check follows the new input
path; its count and business-neutral meaning remain unchanged.

The offer assessment method now establishes stated terms before evaluating estimates,
missing facts and outstanding arrangements. An unconfirmed booking does not make a
stated term unknown; a claimed conflict requires incompatible source evidence.
Comparison owns material accuracy across the full published assessment, including
technical findings and deferred options. It explicitly identifies affected claims,
source evidence, governing corrections or unresolved questions, and consequences for
the recommendation or future use. Original findings remain published unchanged for
traceability, so any superseded claim must be clear in reviewConcerns. This extends
review responsibility without requiring duplicated procedures in the final explanation.

Tradeoffs: deterministic assembly adds a source retrieval and another representation
alongside original sources. Whole-offer inputs reduce the assessor's need to join
terms or choose among unrelated quotes; comparison receives additional context and
broader review work. Cost, latency and semantic benefit have not been measured. The
reviewer can still miss an error or invent a conflict. The source directory's coverage
role ambiguity and genuine timing unknowns remain; the redesign does not fabricate
answers or silently change terms.

All 44 provider-free tests passed, including changed source expiry/reservation/price,
retention of optional offer attributes, exact persisted quote association, and the
new assessor/comparison bindings. Java packaged successfully; both runtimes loaded
the shared manifests through documented helpers. Both provider-disabled smoke checks
verified real deterministic complete-offer outputs against source records, exact
quotes, permissions and prior-record preservation, with zero model calls. Smoke adds
its normal isolated quote rows. No paid workflow or Sidecar evaluation occurred.

This is an implemented proposal, not demonstrated improved business consistency.
The latest captured repeat predates the redesign; all captured and accepted evidence
is preserved. A future separately agreed Java confirmation should retain all four
cases and the six/two medium assignment, verify whole-offer input transport and
published metadata, and review the complete existing business criteria—especially
known terms versus unknown arrangements and evidence-based correction of deferred
findings. No further paid run, accepted promotion, commit or push is implied.

### Complete-offer Java confirmation — 2026-10-07

After separate user approval, run `74621db70bbd44b89419749256b91ef0` evaluated the
redesigned workflow on baseline, priority, capacity_shortfall and later_start.
The assignment remained six Sol/medium responsibilities and two Luna/medium
coordinators. Methods, contracts, bindings, application assembly and fixtures were
frozen during this batch; the preceding redesign's 44 provider-free tests and both
disabled-provider smoke checks remain its implementation validation.

All four cases passed 27/27 structural checks. Independent checksum and trace review
verified each complete offer's original details, terms, source identity/revision,
units and applicable exact service quote, comparison inputs, technical handoffs and
published findings. All 60 responses were valid JSON with no schema corrections,
failed model attempts, rejected actions or plan retries. Prior records were retained
and no service commitment was created. Reported cost was $0.729449095: 24 Sol calls
cost $0.682674400 and 36 Luna calls cost $0.046774695. Mean case trace duration was
113.89 seconds. Cost is about 3.9% above the immediately preceding batch; this single
comparison does not isolate the redesign's cost or latency effect.

Full manual business review supports **a single-batch pass with minor caveats**:

- All four replacement findings retain the supplied expiry. The prior parent/child
  identifier challenge did not recur. Expedited elapsed work is never converted into
  an established repair-labor overrun; actual approval/extra-work triggers remain sound.
- Technical findings preserve attributed chronology, the known short prior test,
  three undated current recurrences, hypotheses and qualified-person boundaries.
  Service charges, pending coverage, dispatch versus warranty roles and separate
  procurement/provider acceptance remain materially usable.
- Baseline pursues expedited with a conditional loaner hedge; priority makes the
  loaner primary alongside expedited. Capacity-shortfall preserves the five-unit/minute
  deficit and unresolved usefulness of partial continuity, without assuming combined
  capacity. Its final handoff could more directly request the operations decision.
  Later-start recalculates standard arrival margins and defensibly favors earlier
  diagnosis plus a hedge while acknowledging its uncertain business value.

The revised comparison responsibility is not proven to catch errors: baseline lists
window concerns, while the other three reviewConcerns arrays are empty. No material
error was explicitly superseded in this sample. In fact, baseline comparison endorses
unnecessary service-window clarification. The quote's `attendance` is copied from
the source `arrival`; different labels do not establish incompatible evidence or a
whole-visit deadline. All four standard findings ask about that meaning, although
they preserve the correct arrival and unknown elapsed completion. This is overcautious
review noise, not an observed false completion commitment. The genuine loaner
arrival/setup ambiguity is different and remains appropriately unresolved.

Other caveats: two final uncertainty summaries group access and dispatch/provider
confirmation around expiry, while their governing service instructions correctly
require approved submission for price preservation and separate dispatch confirmation.
Repetitive cross-assessment reminders remain. The inherited source ambiguity about
who reviews incomplete-but-undisputed warranty findings is not resolved by assigning
the existing disputed-findings role more broadly. Exact excerpts and reader-impact
judgments are recorded in the checksum-linked business review.

Retain this candidate, but do not claim improved consistency from one passing batch
or attribute it solely to the offer shape: input representation and review instructions
changed together. The proposed next step is a provider-free semantic clarification
of quote attendance in both hosts and shared contracts, preserving values, authorization
and genuine timing unknowns. It is not yet implemented or authorized as a new paid
experiment. A changed interface would warrant a fresh agreed four-case confirmation
before unchanged repeats. No whole-pack upgrade or extra skill is justified by these
caveats alone.

Latest and consolidated evidence now include this review; the preceding review was
retained before replacement. Provider-disabled restoration, unchanged candidate source
hashes and unchanged accepted evidence were independently verified. No paid Sidecar,
additional repeat, accepted promotion, commit or push occurred.

### Attendance interface clarification — 2026-10-07

The user authorized provider-free clarification after the complete-offer confirmation.
Inspection established that both deterministic producers already assign source
`arrival` unchanged to quote `attendance`. The defect was missing interface semantics,
not different offered windows. Seven occurrences of the shared quote schema now
describe attendance as the offered technician arrival window, separate from elapsed
work, visit end, restored production and dispatch confirmation. The matching approval
field explains exact quote-window matching. Shared manifests were regenerated.

Keeping the existing field avoids changing immutable quote/approval matching or
public shapes; no extra timing field or model-specific reminder was added. Business
methods, bindings, monetary values, application code and model defaults are unchanged.
This definition follows the producer's actual mapping. It does not resolve the
loaner's arrival versus delivery/setup ambiguity, which is genuinely present in its
source terms. That distinction preserves the human business process.

All 44 provider-free tests passed. The existing assembly test now varies service
arrival intervals and checks exact preservation in persisted quotes. Both integrations
passed disabled-provider smoke checks with explicit arrival equality, unchanged prior
rows and zero model calls. Generation was byte-stable, schema shapes unchanged, and
all fixtures and captured/accepted evidence retained their hashes. Runtime helpers
reloaded the shared manifests; no application rebuild was needed for descriptions.

The earlier $0.729449095 model trial predates this clarification. The intended reduction
in false uncertainty remains a hypothesis. Propose one separately agreed four-case
Java confirmation with the same six/two medium assignment before unchanged repeats.
Keep full business acceptance, including deferred findings, alongside the targeted
service-window and genuine setup-unknown checks. No paid run occurred for this edit.

### Attendance clarification Java confirmation — 2026-10-07

The user approved one four-case Java batch after the description-only clarification.
Run `0d5ec617e2e541779cacbdeb6c087446` retained six Sol/two Luna at medium. All four
cases passed 27/27 structural checks, exact input/result/offer transport and publication,
with 60 valid JSON responses and no schema corrections, failed model attempts, rejected
actions or plan retries. Cost was $0.711329490: 24 Sol calls ($0.664921200) and 36 Luna
calls ($0.046408290). Mean case trace duration was 112.53 seconds. No requests or
commitments were created; prior records and accepted evidence were preserved, and
provider-disabled restoration was independently verified.

Manual review supports a **single-batch business pass with an explicit correction
and minor caveats**, not an error-free set of findings. The capacity-shortfall loaner
leaf calculates the 20:00–22:00 arrival to the next-day 08:00 delay endpoint as 8–10
hours. Comparison explicitly supersedes that claim with 10–12 hours, identifies the
affected field and source, and explains why readiness and the five-unit/minute deficit
remain unresolved. The governing correction is clear; the original defect remains
recorded. The final handoff explicitly asks operations to address the shortfall.
Other cases retain defensible conditional portfolios, correct service charges and
approval triggers, technical chronology and later-start margins. Known expiry and
elapsed-time versus repair-scope distinctions remain intact. Priority expedited still
asks an unnecessary attendance-versus-arrival question without deriving a false
completion deadline. Minor attribution, source-owner ambiguity and repetition remain
documented in the review.

**The intended consumer-level clarification was not delivered.** Inspection of every
captured MODEL_REQUEST_SENT payload found the new attendance definition in four
resolveEquipment calls and four planResolution calls, but none of the eight service
assessment calls or four comparison calls. It was absent from every Sol request.
The provider journal independently confirms this for the affected priority expedited
call. That request contains the business method, mission values and generated-output
instructions, not the added input-schema description. The schema was loaded and was
visible in coordinator context; this is not evidence of a deployment failure or of
a model ignoring a definition it received. Provider-free schema/binding checks had
not established consumer visibility. That should have been verified before the trial.

All four standard findings avoid the earlier unnecessary question, but that observation
cannot be attributed to a definition their models did not receive. The clarification's
reasoning benefit therefore remains untested. Full-publication review, separately,
has now shown one useful evidence-linked correction; it remains promising rather than
reliably established, and it did not remove priority's harmless over-caution.

Recommend provider-free placement of the authoritative service-window meaning in
consumer-visible context or methods for assessment and comparison, followed by
verification through the actual request-construction path before another paid batch.
Retain genuine loaner setup uncertainty and the current coherent tree/assignment;
do not add decomposition or model capability to compensate for missing delivery.
This follow-up is proposed, not implemented in this frozen evaluation. No further
paid run, paid Sidecar, accepted promotion, commit or push was performed. Latest and
consolidated reviews retain the correction and per-skill definition-visibility audit.

### Consumer-visible service window definition — 2026-10-07

The user approved provider-free delivery of the definition to its consumers. One
shared authoring paragraph now appears in the business instructions for expedited
assessment, standard assessment and comparison: service-quote attendance is the
offered technician arrival window copied from the source; it specifies neither visit
end nor elapsed work, and confirms neither dispatch nor restored production. The
definition is scoped to service quotes. Loaner setup ambiguity and all other methods
remain intact. Schemas, bindings, application logic, source facts and model defaults
are unchanged. The tradeoff is intentional repetition between interface documentation
and consumer instructions, because input-schema descriptions do not reach these
consumer requests; a single authoring constant keeps the three prompts aligned.

All 44 provider-free tests passed and generation was byte-stable. After reloading
the shared manifests through runtime helpers, six direct skill probes exercised the
three consumers on both Java and Sidecar. Each actual outgoing request contained the
definition in its system message. Each case used the existing local fixture with an
empty response list and disabled provider credentials, so its request was deliberately
rejected and its execution failed without a model answer or upstream call. These are
successful delivery checks, not successful model executions or business evaluations.
All business rows were unchanged by the probes. Details and raw request captures are
local under `.runtime/consumer-window-probe.json` and its referenced case files.

The probes used validated input objects from the current Phase 2 capture with fresh
case IDs. They did not replay answers, execute captured plans, restore retired Phase 1
machinery or enable the runner's unavailable mock mode. Ordinary smoke tests remain
independent of captures. Both regular integration smoke checks subsequently passed
with zero model calls and prior rows retained, adding only their normal isolated
quote rows. All existing captured and accepted evidence remains unchanged.

Delivery through both integrations is now demonstrated in this scope. Whether these
consumer-visible instructions reduce unnecessary questions remains a hypothesis.
The next proposed paid scope is one fresh Java batch with the existing four cases
and six-Sol/two-Luna medium assignment, full business review and request-visibility
verification. Recent comparable batches cost about $0.71–$0.73; this is an estimate,
not authorization or a guarantee. No paid run, accepted promotion, commit or push
occurred during this change.

### Consumer-definition Java confirmation — 2026-10-07

After user approval, run `3da6f57214b34131994a611b2c1e54a1` evaluated baseline,
priority, capacity_shortfall and later_start with six Sol/two Luna at medium.
Candidate methods, configuration, application code and source fixtures were frozen.
All 108 structural checks passed, and independent trace/bundle review verified exact
source, quote, offer and published-result transport. All 60 responses were valid JSON,
with no schema corrections, plan retries, rejected actions or failed model attempts.
Cost was $0.702841970: 24 Sol calls cost $0.658566600 and 36 Luna calls cost
$0.044275370. Mean case trace duration was 111.97 seconds. Provider-disabled restoration,
unchanged prior business rows, no commitments and unchanged accepted evidence were verified.

The definition appeared in all eight service-assessor requests and all four comparison
requests. None of the eight service findings reopened attendance-versus-arrival meaning;
all four loaner findings retained genuine setup uncertainty. This supports retaining
the targeted clarification as promising, with actual delivery verified. One fixed-case
batch does not establish reliable interpretation or a general causal effect.

**Three cases passed with minor caveats; full business acceptance is withheld.**
Baseline and priority retain defensible service/loaner portfolios. Capacity-shortfall
explicitly requires operations to judge partial output before commitment, without
assuming combined capacity. Later-start correctly calculates standard arrival margins
and makes a defensible primary recommendation, but its comparison publishes an
unsupported governing correction about component prices:

- MAN-4.2 identifies the revision B sensor as S17-B and connector kit as H17-B.
  RATE-09 prices sensor at 12,000 cents and connector at 6,000 cents; the issued quote
  names those parts in its scope. These sources support the $120/$60 explanation.
- Standard feasibility lacks the manual in its local input and notes the absence
  of an explicit code-to-rate mapping. Its cap remains correct. Comparison receives
  the manual as well as the rate card and exact scope; both were verified in its
  actual model request.
- Instead of resolving that local gap, comparison states that even those sources
  do not support definitive allocation and explicitly supersedes the expedited
  explanation until provider confirmation. No conflicting mapping or price is supplied.
  This is a false correction of supported information, not a successful review fix.

The total cap and primary portfolio are unchanged, but the correction governs how
readers use published pricing information. The existing complete-publication criterion
therefore withholds acceptance, just as correct primary decisions did not excuse
earlier misleading deferred-option conditions. This is not a transport failure or
an input-definition delivery failure. It is a source-reconciliation failure at comparison.

Minor findings include priority's unnecessary same-production-morning access observation
while actual installation dates remain unknown; compressed technical attribution and
repetitive cross-assessment reminders; the inherited incomplete-findings reviewer gap;
and later expedited's imprecise abbreviation of ordinary consumable wear to ordinary
wear without making an exclusion determination. Exact excerpts and impact judgments
are retained in the checksum-linked review.

Keep the consumer-window definition and stop paid testing under this completed scope.
The proposed next step is a provider-free review of the quote/comparison boundary.
Consider making the existing deterministic quote publish the item-level amounts it
already uses: a business-readable price breakdown could remove the need for local
assessors to reconstruct pricing from labels. Assess that interface change and its
approval/persistence implications before implementation; it is not yet a validated
remedy. Review should use its broader sources before superseding a supported claim.
Do not add scenario-specific instructions, micro-skills or a blanket model upgrade
in response to this sample. No additional run, paid Sidecar, accepted promotion,
commit or push occurred. The latest and consolidated reviews now contain this result.


### Issued quote itemization and evidence reconciliation — 2026-10-07

Provider-free review found that the quote operation already calculates identified
part prices and repair labor, but its output published only the scope and totals.
Local service assessors therefore had to reconstruct a price breakdown from rate
labels without the manual available to comparison. Comparison had sufficient evidence
in the last paid run, so this interface gap does not excuse its false correction.

Both deterministic hosts now publish `priceBreakdown` inside each issued service
quote: rate-card ID/revision, repair hours/hourly rate/maximum, identified parts with
amounts, and attendance premium. Values come from the existing calculation and
source rates, in integer USD cents. Labor maximum plus parts plus premium equals the
existing cap. Repair charges remain conditional on justified work and coverage;
included diagnosis/travel are not added. No prices, fixture facts or scope changed.

The shared service method uses this breakdown to explain the quote. Comparison now
explicitly reconciles local information gaps with complete case evidence before
raising an unresolved business question or superseding a claim. This is a general
review responsibility, not a rule to prefer one assessor or suppress genuine conflicts.
The business tree, bindings and model assignments are unchanged.

The tradeoff is a larger authoritative quote contract and persisted record. Seven
embedded quote schemas require the new field; Framework forwards it as part of the
whole quote. Approval input remains unchanged: scope, attendance and cap match the
selected issued quote; application persistence still rejects any altered quote.
Existing saved assessments, quotes and receipts are not rewritten. Old captured input
objects do not satisfy the new quote schemas unchanged; new trials use fresh case IDs.
The pre-existing same-case quote-ID reuse behavior is not redesigned here.

The intended reasoning benefit remains a hypothesis until a separately authorized
whole-workflow model evaluation. Latest model evidence predates these changes; do not
report its business conclusions as evaluation of the itemized contract.


Validation: all 44 provider-free tests passed; the extended offer test varies rates,
checks the persisted breakdown and cap arithmetic, and rejects a modified item price
when saving an assessment. Java packaging passed (no Java unit tests are present).
Both deployed integrations passed smoke checks for the exact breakdown, unchanged
caps, permissions, prior-record preservation and zero model calls. Six consumer probes
verified the new breakdown and relevant business instructions in actual requests to
both service assessors and comparison on both hosts. Requests were deliberately
rejected by the local fixture: no model responses, upstream calls or probe business-row
changes. Probe details are local in `.runtime/consumer-price-probe.json`.

Generation is byte-stable; fixture and all evidence checksums, including accepted,
are unchanged. Runtime was rebuilt/reloaded through documented helpers and provider
access remains disabled. Startup exposed unsupported JSON-schema `minimum` fields;
these were removed from the new contract to use the Framework's supported integer
shape before the successful integration checks. No paid evaluation was executed.

Proposed next experiment, pending agreement: one fresh Java batch on baseline,
priority, capacity_shortfall and later_start, retaining six Sol/two Luna at medium.
Freeze this revision and verify exact itemization transport, correct conditional
charging, evidence-supported review corrections, and all existing technical, timing,
capacity, authority and publication criteria. Review all findings, including deferred
options; retaining the right cap or primary choice alone is insufficient. Report actual
routing, retries and total/per-model cost. Recent batches were about $0.70-$0.73;
new request size can change cost. A pass would justify proposing unchanged repeats,
not declaring reliability. No paid Sidecar, accepted promotion, commit or push.


### Itemized quote Java confirmation — 2026-10-07

Run `d0cf8adf039d4def98f6edc7d1a1eafa` completed the authorized four-case Java batch
with six Sol/two Luna at medium. All 108 structural checks passed, independently
verified handoffs and published results were exact, and all 60 responses were valid
JSON with no schema corrections, plan retries, rejected actions or failed attempts.
Cost was $0.719029125: 24 Sol calls cost $0.672036500; 36 Luna calls cost $0.046992625.
Mean case trace duration was 105.02 seconds. All twelve intended consumer calls
received the itemized quote and their revised methods. Fixture, frozen implementation
and accepted-evidence hashes remained unchanged; provider-disabled restoration was
independently verified. No commitments or prior-row changes occurred.

**All four cases pass business review with minor caveats.** All eight service findings
use the correct part prices and conditional charging; the false mapping uncertainty
and false comparison correction did not recur. Service-window interpretation remains
sound, while genuine loaner setup uncertainty is retained. Baseline and later-start
retain defensible expedited/conditional-loaner portfolios; priority selects loaner
first; capacity-shortfall requires an operating-team plan before loaner commitment
and retains the 5/minute shortfall without invented combined capacity. Later-start
standard correctly has 4-6 hours before production and 6-8 before its delay endpoint.

Priority comparison explicitly supersedes an overly broad coverage-owner assignment:
CONTACT-WARRANTY identifies disputed-findings review, while W-7 does not name the
owner for incomplete-but-undisputed findings. This correction is supported. Other
cases retain the inherited compressed owner handoff, a minor precision limitation
under the existing reviews. Further caveats include redundant cross-assessment prose,
compressed author attribution, capacity's redundant question about the recorded test
technician, and imprecise wording for a loaner arrival range relative to closing.
These are recorded in the checksum-linked business review, not hidden by the pass.

Keep the candidate unchanged. Exact arithmetic/persistence and consumer delivery are
verified; improved reasoning remains promising, with itemization and method changes
not separately isolated. One successful batch does not establish repeatability.
Propose two unchanged four-case Java repeats at this assignment, about $1.44 combined
at observed cost, subject to agreement. Review all published findings and supported
corrections under the existing criteria. No further paid run, paid Sidecar, accepted
promotion, commit or push is authorized. Latest and consolidated reviews retain this
result; accepted evidence and authored defaults remain unchanged.


### One unchanged itemized-quote repeat — 2026-10-07

At the user's request, only one of the proposed two repeats was authorized and run.
Run `f11193ccd3024844bb38cc69d53e0d2c` used the same four Java cases and six-Sol/two-Luna
medium assignment as `d0cf8adf039d4def98f6edc7d1a1eafa`. Hash checks verify unchanged
methods, schemas, application sources, fixtures and bindings. All 108 structural
checks passed, all sixty responses were valid JSON, and there were no schema
corrections, plan retries, rejected actions or failed attempts. Independent checks
verified exact itemization, handoffs and publication, with the intended context and
methods present in all twelve consumer calls. Mean case trace duration was 109.53 seconds.

**All four complete business cases pass with minor caveats.** Prices, conditional
charges, service-window semantics and repair-labor distinctions remained sound.
Priority again selects the loaner first; capacity-shortfall explicitly requires an
operations decision about partial output before commitment; later-start retains the
correct standard-service 4-6/6-8-hour margins. Technical evidence and uncertainty
remain materially usable. No false price correction recurred. ReviewConcerns is empty
in all cases, so the batch did not exercise a supported material correction.

Retain the known warranty-owner precision limitation. Additional caveats are a
redundant service-request reminder in baseline's loaner expiry, later-start's ambiguous
wording about access coverage for the full two-hour offered arrival window, and an
uncertainty about dispatch confirmation before expiry despite correctly stated
approved-submission rules in the governing conditions. None establishes a new charge,
commitment, setup duration or price-preservation prerequisite when read with its
explicit conditions. Exact impact judgments are retained in the business review;
the pass is not a claim of perfect prose or error-free review.

Reported cost was $0.718357850: 24 Sol calls cost $0.673290200; 36 Luna calls cost
$0.045067650. Confirmation plus this repeat cost $1.437386975 for eight cases, 120
valid responses and 216 passing structural checks. Eight materially acceptable
fixed-case results across two unchanged batches are bounded repeated evidence, not
a statistical reliability estimate or proof of transfer.

Stop paid testing under this scope; no second repeat was run. Retain the working
six/two candidate and recorded caveats without automatically optimizing further or
adding instructions. The user emphasized diminishing returns from model-tier tuning;
include authoring, review and maintenance effort in future cost decisions. Accepted
evidence is unchanged and no promotion is implied. Provider-disabled restoration,
unchanged prior business rows and no commitments were verified. No paid Sidecar,
commit or push occurred. Latest and consolidated reviews retain the result.
