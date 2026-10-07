# From business processes to reliable skills

## A living design guide for mid-tier models

Use this guide when translating a business process into a tree of model-driven
skills and deterministic operations. Its goal is a stronger starting point for
future designs: manageable reasoning responsibilities, small output contracts,
faithful handoffs, and explicit business boundaries.

The skill tree must satisfy a **human business contract**: a person responsible
for the process should recognize its responsibilities, decisions and handoffs as
a sensible way to do the work. This is a design requirement, not an empirical
claim about model performance. Mid-tier success is valuable within that contract;
using a stronger model for a coherent reasoning-intensive step is a valid outcome.

The central working principle is: **ask models to make bounded judgments and
produce compact findings; let the runtime transport evidence and assemble larger
structures.** Sophisticated business reasoning does not require every model call
to construct the whole workflow's data structure.

These practices come from local experiments and reviews, not a broad benchmark
across models and domains. “Mid-tier” describes the intended capability/cost range,
not a guarantee about a particular model. Use these practices as design defaults,
then validate them on the process and models being used.

## How to read the evidence

Use evidence status, not a numerical score or a ranking of importance. A critical
design issue can have an untested remedy; a modest transport practice can have
direct verification. Status describes support for a specific claim, not how
strongly we want it to be true.

| Status | Meaning | How to use it |
| --- | --- | --- |
| **Demonstrated in a defined scope** | The stated benefit has been directly verified in the identified conditions. The mechanism or comparison is clear enough to support that bounded claim. | Use as an established starting point within that scope; validate transfer outside it. |
| **Promising, not established** | Observations support the practice, but repetition, controlled comparison, or transfer is insufficient. Several changes may have contributed together. | Prefer as an experiment-informed starting point, while measuring whether it helps. |
| **Proposed for testing** | A plausible remedy or design approach has not yet demonstrated its intended benefit. The motivating failure may nevertheless be well observed. | Treat as an experiment, not an accepted solution. |

The sections below distinguish **observations**, **working practices**, and
**hypotheses** within each topic. Those describe the kind of statement, not its
evidence status. Observing a failure does not demonstrate that a proposed fix works.

### Current evidence map

| Practice or claim | Status | What the evidence supports | What remains to demonstrate |
| --- | --- | --- | --- |
| Runtime binding and forwarding preserve selected source values and accepted results | Demonstrated in a defined scope | Exact-value checks verified transport through the tested skill boundaries. This establishes preservation, not correctness of model-authored findings. | Compatibility and preservation at newly introduced boundaries and runtimes. |
| Trace review separates execution, transport, and reasoning failures | Demonstrated in a defined scope | Following inputs, accepted outputs, and final restatements localized distinct failures, including errors introduced after a correct intermediate result. | Diagnostic coverage for other failure modes; automatic semantic detection is not established. |
| Focused per-item skills with shallow outputs and runtime-owned collection | Promising, not established | The combined design completed observed cases, including a second model, without malformed feasibility handoffs; business failures still occurred. | Broader reliability and the separate effects of decomposition, output depth, and output length. |
| Explicit feasibility findings before strategy selection | Promising, not established | Previously omitted constraint interactions appeared in intermediate findings and final decisions in observed cases. | Reliable retention of every relevant constraint and benefits across other business processes. |
| Supplying parent metadata and clarifying process boundaries | Promising, not established | Targeted corrections improved outputs, but unchanged repeats still ignored supplied metadata or questioned its applicability because parent and child record identifiers differed, despite explicit descriptions. | Reliable interpretation of present terms, transfer, and separate contributions of input shape versus instructions; exact transport does not establish correct use. |
| Explicitly preserving reference points and separating known facts from missing attributes | Promising, not established | Targeted instructions improved time-reference consistency and retained known observations in subsequent cases, while leaving unspecified triggers unknown. | Repeated reliability and transfer; other attribution and interpretation errors remained. |
| Shared methods with responsibility-specific instructions | Promising, not established | Separating two approval procedures in otherwise shared assessment skills removed observed cross-process permission requirements in subsequent cases. | Repetition and transfer; source-input breadth and instruction scope were not separately compared. |
| Preserve observation provenance, assess test adequacy, and permit absent evidence | Promising, not established | Explicit methods improved attribution to original versus later records, interpretation of prior tests, and classification of supporting versus contrary evidence. | Repeated final-version success, new evidence patterns, and isolation of the individual changes. |
| Vary one operating constraint while keeping skills and source offers fixed | Demonstrated in a defined scope | Targeted cases showed recognition of an inadequate option and recalculation when a deadline moved; the same cases also exposed unrelated output defects. | Broader boundary coverage, new domains, and reliable retention of all other conditions. |
| Direct publication retains findings and source metadata | Demonstrated in a defined scope | Exact checks verified publication of accepted per-option findings and authoritative metadata across several cases. Final prose still introduced conflicting interpretations. | Reliable overall decisions and whether a narrower comparison contract reduces contradictions. |
| Flattening diagnostic evidence into self-contained statements | Promising, not established | Several assessments retained support, contrary evidence and unknowns without serialization or schema correction after removing nested generated objects. | Repetition, transfer, and isolation from other simultaneous changes; prose can still lose provenance. |
| Keep the final explanation focused on selection, tradeoffs and residual risk | Promising, not established | A compact contract reduced repetition, but review limited to selection-critical claims missed a material error in a published deferred option. Compact explanation must not imply narrow accountability. | Whether concise output and complete material review coexist reliably, plus repetition and transfer. |
| Present one complete business offer with its applicable terms and provenance | Promising, not established | Provider-free checks and one complete model batch preserved original terms and quotes; the previously observed false uncertainty about parent-term applicability did not recur. Some redundant label clarification remained. | Unchanged repetition, transfer, stable cost and isolation from simultaneous review-method changes; one passing batch does not establish improved consistency. |
| Match final review scope to all material content being published | Promising, not established | A reviewer corrected a wrong time margin, but a later review also superseded supported pricing information by failing to reconcile sources already in its context. | Reliable detection and supported correction across error types; an explicit correction can itself be the material defect. |
| Explicit fields for mandatory conditions and source-linked owner references | Promising, not established | Subsequent outputs retained required conditions and selected the correct separate owner records. One initial omission was corrected; a later readable-baseline batch retained all eight targeted service outputs without correction. | Unchanged-version repetition, new rules and owners, and separate effects of fields versus reference instructions; broader approval prose and final financial synthesis still failed. |
| Assign model capability by coherent business responsibility | Promising, not established | Mixed assignments preserved the tree and exact handoffs with fewer stronger-model calls. A business-readable refinement passed one complete batch; two unchanged repeats produced one pass and one failure on a supplied deadline's applicability in a stronger-model responsibility. | Consistent complete business correctness, transfer, the lowest sufficient assignment and stable cost/latency; a passing sample or stronger assignment alone does not establish reliability. |
| Test a more capable whole-tree model before further compensating decomposition | Promising, not established | On identical sources, a stronger-model batch avoided earlier quantity and financial synthesis errors without changing the business tree; smaller published-reasoning defects remained. | Unchanged repeats, complete business acceptance, cross-domain transfer and the lowest sufficient tier; one model comparison is not a general ranking. |
| Connect operational action to the governing business condition | Promising, not established | After a shared method and descriptions tied approval to actual changes instead of a numerical difference between unlike quantities, an initial batch and two unchanged repeats retained that distinction throughout relevant findings and decisions. An unrelated deadline-interpretation failure remained. | Transfer, separate contributions of method versus descriptions and consistent whole-workflow correctness; repeated targeted success on fixed cases does not establish general causality or reliability. |
| Typed quantities with explicit activity semantics | Promising, not established | After an ineffective schema-only placement, a definition delivered in consumer instructions coincided with correct service-window interpretation throughout one batch while genuine setup uncertainty remained. | Unchanged repetition, transfer and causal attribution; delivery is verified, consistent interpretation is not established. |
| Verify semantic instructions in the actual consumer request | Demonstrated in a defined scope | Input-schema descriptions were absent from consumers despite correct value bindings. After moving the meaning into consumer instructions, locally rejected requests verified its presence through both integrations without upstream calls or model answers. | Delivery behavior in other runtime paths and actual interpretation; presence is not evidence of compliance or business correctness. |
| Scope unknowns to the responsible assessment and date access calculations | Promising, not established | A subsequent four-case batch qualified local absence and retained unknown activity dates after shared method/description clarifications; ambiguous arrival/setup semantics were retained explicitly. | Unchanged repetition, reader usability, transfer and isolated contributions of the combined edits; final synthesis still introduced an unrelated approval-expiry claim. |
| Review business methods and schema descriptions as one contract | Promising, not established | Broad cleanup alone left quantity and synthesis defects. A focused method/description clarification retained its intended operational distinction in an initial batch and two unchanged repeats; another explicitly described input still suffered a meaning/applicability error. | Transfer, isolated contributions and practitioner comprehension; aligned text and repeated targeted success do not establish whole-workflow reliability. |
| Publish authoritative calculation detail at its business owner | Promising, not established | Provider-free arithmetic/persistence and request checks verified the breakdown; a four-case confirmation and one unchanged repeat retained supported prices without the previous false correction. | Broader repetition, new cases, transfer and separate effects of itemization versus simultaneous reconciliation-method changes; two fixed-case batches do not establish general reliability. |
| The complete design checklist improves new skill trees | Proposed for testing | Its components are informed by the observations above; the checklist as a whole has not been evaluated. | Prospective use on new processes, with success criteria defined before implementation. |

Do not interpret these statuses as a universal model capability ranking. The
shallow-output approach remains promising even though particular runs succeeded;
that success does not establish a general reliability improvement.

## 1. Decompose the business decision before designing the skill tree

**Working practice:** map what must be known, decided, authorized, and executed.
Then give each skill a bounded responsibility with a reviewable output.

Freezing a version for comparison is an experimental control, not a ban on refining
skills. Improve methods, contracts and handoffs when the revision expresses sound
business reasoning that a practitioner can recognize. Preserve coherent judgment;
avoid fixture-specific answers or artificial decomposition merely to accommodate a
model. This is a design policy, not a demonstrated performance result.

Explain the tree in business language before assigning models. Each boundary
should have a recognizable responsibility and useful handoff. Keep coherent
judgment together when further fragmentation would make the business process
harder to understand. Serialization, identifiers and assembly belong in the
implementation underneath that process; they should not dictate its narrative.

### Model-selection order

This is a working design policy, not a demonstrated model ranking:

1. Author a coherent, readable business process and test its complete skill tree
   on the lowest reasonable general-purpose tier. Move upward until a candidate
   passes the agreed end-to-end evaluation, including business review. Avoid
   rewriting the process repeatedly around the weaknesses of a single candidate.
2. If that lowest successful model is relatively capable or costly, retain its
   working whole-tree baseline and test lower-tier substitutions at coherent
   business responsibilities. Validate the complete workflow after substitutions;
   individual skills passing separately does not establish successful handoffs.
3. If the lower-tier candidate already succeeds reliably, keep the simple
   assignment. Mixed-tier routing is an optimization to justify, not an objective.
4. A skill-specific capability requirement can take precedence. This explicitly
   includes a mixed pack using a higher-tier general-purpose model only for the
   skills that need stronger reasoning, with lower-tier models for the remaining
   skills where they suffice. It also includes vision, low latency, or another
   specialized model type. State the requirement, select for that capability,
   and validate the resulting full process and model handoffs.

Both steps 2 and 4 support mixed-tier workflows. Step 2 starts from a successful
higher-tier whole-tree baseline and lowers selected responsibilities. Step 4
allows targeted higher-tier assignment where a particular capability need is
already established; it is not restricted to different modalities. One demanding
skill does not require upgrading the entire tree. Keep higher-tier use tied to
need within coherent business responsibilities, not to a fixed allocation quota.

The reasonable candidate set changes over time. Reassess actual capabilities,
availability, cost and latency when defining experiments; do not freeze brand
names into the method or assume price perfectly orders reasoning capability.
Do not target a fixed percentage of stronger-model calls. Confirm successful
samples with repetition and relevant variations before relying on them.

Out of the box means a competently authored business baseline before model-specific
compensating rewrites. Clear schemas, grounded reasoning instructions, legitimate
business rules and deterministic transport are still part of that baseline.
An already heavily tuned workflow should not be relabeled as an untuned baseline.

When reviewing an accumulated instruction set, separate the business responsibility
and method from runtime/schema mechanics. Retain evidence standards and real
conditions even when failures first exposed their importance. Reassess arbitrary
length limits, repeated corrective reminders and prohibitions that prevent a
decision owner from explaining or verifying material facts. Keep schema descriptions
consistent with the revised method. This is a design-review practice; clearer
authoring and successful configuration checks alone do not demonstrate better model
performance. Evaluate the revised whole workflow before promoting that claim.

Use the whole-tree result to justify allocation work under step 2, or an established
skill-specific capability requirement under step 4. Prefer explicit per-skill routing as a
testable starting point; confidence-based escalation needs its own evaluation.

| Responsibility | Typical owner | Result |
| --- | --- | --- |
| Retrieve authoritative records | Deterministic tool or integration | Source facts with identity and provenance |
| Calculate defined quantities or enforce rules | Code, where inputs and rules are established | Computation or validation result |
| Interpret evidence | Focused reasoning skill | Supported findings and unresolved questions |
| Assess one alternative | Focused reasoning skill | Constraints, feasibility, and prerequisites |
| Compare alternatives | Decision skill | Tradeoff against the user's objectives |
| Verify authority and execute commitments | Authenticated application or external process | Validated action and durable receipt |
| Assemble and publish | Runtime or application | Accepted results with authoritative fields preserved |

A useful starting sequence is retrieval, focused assessment, comparison, and
publication. Authorization and execution belong in an explicit action path when
the business process requires them.

Split where responsibilities or evidence needs differ. Do not create a skill for
every sentence or field: a boundary should reduce reasoning burden, reduce output
construction, or make a result independently verifiable. Keep tightly coupled
judgments together when splitting would force repeated reconstruction of context.

A shared template need not give every invocation identical instructions. Keep the
common reasoning method, then supply the procedure relevant to the item's business
responsibility. Observed outputs imported rules from a neighboring process when
both procedures appeared in every instruction set. Responsibility-specific
instructions improved subsequent cases without adding skills or changing contracts;
this remains a promising composition practice, not a universal rule to remove context.

## 2. Prefer small, shallow model-authored outputs

**Observed:** a model can express a correct business calculation inside a response
that cannot execute because its surrounding JSON is malformed. A deeply nested
tool-action argument can become a substantial generation task of its own.

**Working practice:** prefer one compact object per bounded judgment. Use scalar
fields and short arrays of strings where they express the result adequately. Avoid
requiring a model to generate a large collection of nested objects merely because
that is the final application's desired shape.

For repeated assessments, consider one invocation per option or item, using a
shared method and contract. Let the runtime collect the results. Keep a comparison
stage for interactions among options: an item that cannot satisfy the goal alone
may still be useful in a combined strategy.

Allow a semantically empty result when evidence is absent. A required array need
not contain an item: pressure to populate both supporting and contrary evidence
can encourage merely relevant facts to be placed on the wrong side. Define what
each field means, permit absence where justified, and distinguish missing evidence
from an observation that contradicts a hypothesis.

Semantic absence and syntactic omission are different. A required evidence field
may need an explicit empty array; omitting it violates the contract. Observed
corrections in a nested assessment included omitted fields, undeclared explanatory
fields, and a trailing comma after an empty array. The shallow sibling assessments
did not show those failures in the same evaluations. This motivates testing smaller
assessment outputs, but does not isolate nesting as the cause.

There is no established universal limit on fields, nesting depth, or response size.
Keep outputs inspectable and measure what the selected model produces. Flattening
a tree into one enormous prose field does not remove its reasoning burden.

One tested alternative to nested evidence objects was a short, self-contained
statement per hypothesis, retaining the possible cause, supporting observation,
contrary observation or its absence, and missing evidence together. Observed cases
needed no serialization or schema corrections, but attribution gaps remained.
This is promising for human-readable analysis. If downstream code needs to query
individual evidence relationships, strings may sacrifice necessary structure;
use smaller structured tasks and runtime assembly instead of hiding JSON in prose.

**Hypothesis:** reducing output size and depth improves serialization reliability.
Our observations support smaller tasks and shallower outputs together; they do not
yet isolate those two effects.

## 3. Separate reasoning results from tool-call construction

**Observed:** putting substantial analysis inside a tool-call envelope adds JSON
construction at the handoff. Moving the analysis into a skill result allowed much
smaller call envelopes in the observed workflows.

**Working practice:** let the planner identify dependencies and select operations,
the reasoning skill produce analysis, and the runtime bind inputs and forward
accepted results. Avoid making a planner reproduce evidence, perform the analysis,
and wrap everything in the next skill's arguments.

When all arguments are bound, use empty model-authored arguments if supported.
Input binding and automatic dispatch are separate capabilities: a runtime may
supply every argument while still requiring a small model-generated call envelope.
Verify actual dispatch behavior. Optimize call overhead separately from reasoning
quality and data preservation.

## 4. Narrow inputs without stripping their meaning

**Observed:** extracting an item from a larger record can omit parent metadata that
changes how the item should be interpreted.

**Working practice:** supply the evidence needed for the judgment, including
relevant source identity, observation time, validity period, status, units, scope,
and policy. An individual item may depend on metadata attached to its enclosing
snapshot. Select inputs by the question the skill must answer, not by whichever
JSON subtree is easiest to select.

Verify selected values against their source. Missing metadata must remain unknown;
the model must not borrow it from an unrelated item or neighboring record.

Preserve observation provenance as well as record identity. A later record linked
to an earlier event does not make its observation part of the earlier record.
Where earlier tests or checks influence a decision, ask whether their duration,
conditions and coverage could establish the claimed outcome. A successful test
under narrower conditions does not establish resolution under broader conditions.

Distinguish reading complexity from generation complexity. Failure to construct a
large output does not prove inability to use a large input. Remove irrelevant
evidence, but do not replace necessary source material with an unverified summary
merely to make the input small.

## 5. Establish constraints before choosing a strategy

**Observed:** general instructions to consider several constraints did not always
produce their required interaction. Explicit intermediate assessments made some
previously omitted interactions visible to downstream comparison.

**Working practice:** require the findings that support a decision before asking
for the preferred strategy. Depending on the process, these may cover eligibility,
capacity, timing, dependencies, exposure, authority, and unresolved conditions.

Give each field a distinct purpose. An assessment should answer a bounded question
and identify prerequisites, without prematurely selecting the winner. Require
concrete findings instead of a generic “checked” or “feasible” label.

**Source-review observation:** clearer business methods can coexist with stale
schema descriptions that route valid choices into the wrong category or apply one
commitment family's approval procedure to another. Review both as one contract,
including embedded consumer copies. Reuse shapes where useful without forcing
identical field meanings across distinct business procedures. Correcting textual
contradictions is justified design cleanup; its performance benefit remains proposed
for testing. A supplied completion window and a duration-derived estimate are also
different valid forms of timing evidence; a field should not require inventing one
merely because the other was supplied.

Teach a general method, not an example's answer. Require comparison of an activity's
entire duration with the available window, for example, rather than embedding a
particular deadline conflict in the prompt.

## 6. Keep quantities attached to their meaning and reference point

**Observed:** downstream reasoning can preserve a number while changing what it
is relative to. Models can also use a duration for the wrong activity even when
the arithmetic is valid.

**Working practice:** preserve quantity, unit, activity, reference event,
assumptions, and uncertainty together. “Hours after the start” and “hours beyond
the allowed delay” are different findings. A usage period is not a setup duration;
billable effort is not necessarily elapsed time.

Use deterministic arithmetic when inputs and calculation rules are established.
Interpretation is still needed to select the right quantities. Missing calendars,
start triggers, or duration estimates must not silently become assumptions.

State unknowns precisely. An unknown event timestamp does not make a supplied
event count unknown. Preserve established facts while identifying what is missing.

Targeted instructions to name reference events, recalculate changed comparisons,
and distinguish known observations from missing attributes improved subsequent
outputs in observed cases. This is promising evidence for a reasoning method,
not proof that asking for a self-check ensures consistency. Keep calculations
relevant to the decision: gratuitous margins add claims that also need validation.

**Counterexample after readable-method cleanup:** some assessments still used
billable repair allowances as elapsed completion estimates, while another stage
misidentified a longer elapsed-work estimate as an authorization conflict. Other
cases in the same batch preserved the distinction. Clear instructions therefore
remain promising, not sufficient. Clarifying producer semantics or selecting a
more capable model are separate hypotheses; neither remedy follows as proven from
the failure. Do not split a coherent assessment merely to avoid testing capability.

**Subsequent observation:** changing the whole-tree model with sources frozen
avoided those quantity confusions and a prior financial inversion in one batch.
It did not eliminate unsupported reasoning elsewhere: a daily access window was
treated as though only the deadline day's window could be used, without evidence
for that arrival date. Keep time calculations tied to an established activity date;
a correct rejection for another reason does not validate an unnecessary calculation.
Model capability and explicit source semantics are complementary questions, not
substitutes for one another.

## 7. Treat final synthesis as another possible failure point

**Observed:** exact transport of an intermediate finding does not guarantee a
faithful final recommendation. Comparison can introduce errors while paraphrasing
a correct child result.

**Working practice:** make comparison responsible for tradeoffs and consistency,
with explicit requirements to preserve reference points, conditions, and
uncertainty. Keep authoritative values and accepted results under runtime ownership
where they can be published directly instead of regenerated.

Intermediate findings remain model-authored interpretations, not a new authority.
Downstream skills should challenge them against source evidence when appropriate,
but should not silently change their meaning. Corrections should retain a
reviewable connection to the supporting evidence.

**Working practice; reliable correction remains unestablished:** when original findings are
published unchanged, designate where corrections are recorded and make the final
recommendation use the resolved interpretation consistently. Traceability preserves
the old finding; usability requires that readers can identify which interpretation
governs. Do not claim success merely because the final choice is right while its
published supporting conditions remain misleading. Source-linked owner IDs likewise
need a readable role/contact presentation; referential integrity alone does not
establish a usable human handoff.

**Subsequent observation:** an explicit correction field contained an unsupported
conflict and made the final recommendation less accurate than a correct child
finding. Another final summary inverted the meaning of an uncovered charge despite
correct source and child output. Explicit correction placement improves reviewability,
not correctness by itself. Review both the correction and the resulting decision;
readers must not be left with incompatible financial or operational instructions.

**Observed interface limit:** a per-item assessor can truthfully lack another item's
facts while the assembled output already contains them. Publishing an unqualified
“not supplied” claim can then mislead the reader. Keep local input limits distinct
from process-wide unknowns; comparison has the assembled evidence. Clear scope or
assembly-level reconciliation is a proposed remedy, not a demonstrated need for a
new reasoning skill. Similarly, mixed labels for an arrival versus a completion
window produced different conditional interpretations with the same source facts;
record that ambiguity separately from an established arithmetic error.

**Review practice:** distinguish a missing business fact, information held by another
responsibility, and a limitation of the current implementation. They call for different
handoffs. Check implementation limits directly when the question is what the application
can authorize; a directory is neither a grant nor a complete description of the implemented
approval path. Static inspection establishes the code's rule, not a successful execution
or broad business-policy endorsement. Preserve the prior experiment's evidence when a
later review qualifies an interpretation.

**Observed:** direct publication retained findings and source metadata exactly in
subsequent cases. Final prose still collapsed a range to one endpoint and added an
unsupported prerequisite to a deadline. An explicitly instructed reviewer also
challenged a valid estimate because its source label left room for another
interpretation. Making a correction explicit helps inspection; it does not make
the correction correct. A larger assembled result can remain reliable to transport
while its smaller model-authored explanation is inconsistent.

**Promising practice:** narrow the final contract to selection, tradeoffs and
residual risks, referring to published conditions rather than reconstructing
business procedures. A subsequent experiment removed duplicated procedural
fields, made the pursued portfolio explicit, and replaced general re-verification
with reporting of concrete decision-relevant conflicts. Comparisons became
substantially shorter and prior final-stage errors did not recur in those cases.
The contract and responsibility instructions changed together; the benefit is not
isolated or established as repeatable.

That narrower review scope later left a material error in a deferred finding
uncorrected even though the complete finding was published. Keep the final
explanation concise, but make someone accountable for the material accuracy of
the entire delivered assessment. **Proposed practice:** the existing decision owner
reviews published technical findings and every option, including deferred ones,
identifies supported corrections explicitly and distinguishes genuine unresolved
conflicts from missing confirmation. This need not introduce another skill or
rewrite every original finding. Broader review can cost more and can itself invent
conflicts. One subsequent batch did not exercise a material correction; another
explicitly superseded a wrong time margin, linked the source and explained the
consequence for the decision. This is promising evidence of usable correction,
not reliable detection. Redundant label clarification still showed a review limit.

**Promising representation:** assemble each business offer with its applicable
terms, price or conditional quote and provenance before reasoning about it. Preserve
the original details and the source relationship deterministically. This makes the
object recognizable as one offer while leaving booking, approval and fulfillment
as separate facts. Source-preserving assembly has been checked and one model batch
retained the applicable terms; improved consistency still needs unchanged repetition
and separation from simultaneous review changes. Do not conceal source contradictions or create
defaults merely to make the record appear complete.

Moving responsibility requires a completeness check at its destination. In the
same experiment, mandatory post-approval conditions were moved to a per-option
skill's generic unresolved list and omitted in several results despite explicit
instructions. Naming a responsibility in a prompt does not give it a reliable
place in the output. **Hypothesis:** give each mandatory condition a small explicit
field, permit a justified unknown or not-applicable result, and verify its meaning.
A required field guarantees neither correct content nor correct attribution.

In a subsequent experiment, dedicated condition fields and source-record owner
references retained the targeted rules and correct responsibilities across the
accepted outputs. One response initially omitted the required owner-reference
arrays; validation exposed the omission and a correction supplied them. This
supports completeness and detectable omission in the tested setting, with a
correction cost. It does not establish first-attempt reliability or general
business correctness, and the two changes were not isolated.

Asking for an owner can also encourage completion of a missing personal name:
observed findings joined one record's responsibility with another record's named
contact. Preserve record identity and missing attributes; test whether referencing
the responsible record directly reduces unnecessary regeneration of identity facts.

An observed mixed-model evaluation retained correct dedicated owner references for
one process while assigning those same contacts to another process without evidence.
**Working practice:** verify the relationship between a source record and the requested
responsibility, not merely whether the referenced record exists. A real name and a
valid identifier can still describe an invented handoff. Unspecified supplier ownership
should remain unknown or be presented as a contact to verify. This is an observed
failure mechanism. A later stronger-model assignment avoided the targeted relationship
errors in one batch, without new fields or instructions; repetition and transfer remain
unproven. It did not make the whole workflow reliable.

Clarifying ambiguous source quantities at their producer boundary remains a
separate hypothesis. Do not assume an extra summarizer, broader self-check or
reviewer will repair every mistake. Retaining exact source facts also does not guarantee
their use: known record authors and unknown physical performers should remain
distinct when requesting missing attribution.

## 8. Keep business authority separate from model reasoning

**Observed:** incorrect approval-routing advice can coexist with application guards
that correctly prevent unauthorized execution. Models can also assign an external
approval process to an application that does not implement it.

**Working practice:** define which system owns each decision and action.
Distinguish informational spending limits, roles, verified permissions, explicit
approval, submission, and confirmed fulfillment. These are separate facts.

Preserve the distinction between recommending an action and performing it. A skill
may propose a conditional strategy requiring external approval; it must not invent
that approval or add unsupported approval stages. Deterministic guards protect
execution, while business review must still assess the advice.

## 9. Evaluate execution, preservation, and judgment separately

**Working practice:** answer three different questions:

1. **Execution:** did the runtime accept the plan and actions, invoke the intended
   skills, and complete? Inspect corrections and provider failures separately.
2. **Preservation:** did skills receive the intended evidence, and did accepted
   outputs reach downstream consumers unchanged where required?
3. **Judgment:** were calculations, interpretations, tradeoffs, uncertainty, and
   authority boundaries correct and mutually consistent?

Schema validity is not business acceptance. Exact transport can preserve an
incorrect judgment. Raw formatting alone is also insufficient to establish runtime
failure: inspect the accepted plan or action and the runtime's diagnostics.

Count schema corrections separately from malformed JSON, plan retries and failed
provider requests. Observed output could parse as JSON yet omit required fields or
add undeclared ones; correction calls were visible in detailed traces while broad
retry counters stayed at zero. Check what each metric actually measures before
using a zero count as evidence of a clean first attempt.

Locate the first incorrect stage. Check source, bound input, skill result,
forwarded value, and final restatement before changing a prompt. Distinguish
missing-input problems, reasoning errors, and output-construction failures.
Do not silently repair malformed responses and count them as successful model runs.

A subsequent review found a final comparison attaching an offer's expiry to approval
itself, although the intermediate finding separated them correctly. **Working practice:**
keep deadlines attached to the business event or object they govern. Correct selection
and correct intermediate findings do not validate every final explanation. Record the
scope and practical impact of a defect; distinguish an unsupported business rule from
merely repetitive wording. This observation does not demonstrate a need for another
skill boundary or a scenario-specific corrective instruction.

Repeat the final configuration unchanged before describing success as repeatable.
Observed repeats retained valid execution and exact transport while regressing on
business facts and prerequisite retention. A successful sample remains useful
evidence, but does not establish a stable workflow. Record regressions alongside
successes, and compare business implications rather than requiring identical
wording or a single preferred strategy when the user's preferences leave room for
several defensible choices.

Test another model against unchanged skills before tuning for it. In an observed
transfer, shallow result generation and transport succeeded while units, included
charges, approval routing and deadline reasoning failed. That supports transport
portability in the observed cases, not portability of business correctness. A
shared reasoning-setting name across providers is not evidence of equal reasoning
effort. Preserve the effective configuration and review stage-level failures.

One mixed-model follow-up avoided the targeted handoff defects but introduced a
scope-overrun implication by comparing elapsed activity time with billable labor.
Other fields in the same finding distinguished those quantities correctly. **Observed:**
correct definitions and dedicated condition fields can coexist with contradictory
operational prose. Verify the implication that triggers action, not only the presence
of the right terms. This does not establish that more decomposition or a blanket
model upgrade would help.

**Observed follow-up:** a shared method and matching field descriptions connected
the approval action to its actual business trigger. An initial batch and two unchanged
repeats retained that distinction throughout the relevant findings and decisions.
The combined clarification remains promising: its components were not isolated,
the cases were fixed, and a separate supplied-deadline interpretation regressed.
Minor redundant questions persisted in the initial batch. Judge
their practical impact explicitly: a question that repeats a fact it also states is
different from treating that fact as unknown or deriving a false operational rule.
Record both without claiming flawless output or silently lowering the acceptance bar.

An unchanged repeat questioned whether a supplied offer deadline applied because
the parent snapshot and individual offer had different identifiers. The interface
already explained their relationship, and transport was exact. **Observed:** a
model can turn a known term into false uncertainty despite a clear description;
comparison may preserve it. A different identifier is not itself conflicting evidence.
**Working practice:** distinguish supplied terms, genuine source conflicts and
unconfirmed fulfillment when reviewing a decision. Another reminder or input-shape
change needs evaluation; do not infer that further decomposition or a blanket
capability upgrade is necessary from this failure alone.

**Observed follow-up:** one batch using complete source-preserving offer records and
broader publication review retained the applicable parent terms and passed material
business review with caveats. These changes were combined, and the batch did not
exercise correction of a material error. A later batch did explicitly correct a
timing error. Complete offers and full-publication review are promising; neither
is established as reliably preventing or catching errors.
Different labels on an original value and its deterministic copy also prompted
unnecessary clarification. **Hypothesis:** explicit producer/interface semantics can
reduce this noise. Preserve genuinely unknown timing rather than defining it away,
and do not treat different field names alone as incompatible business evidence.

**Observed delivery limit:** an input-schema description reached coordinating
models but was absent from the affected assessment and review model requests.
Successful schema validation and exact value forwarding did not establish delivery
of the semantic definition. Before paying to test a prompt or contract change,
inspect the effective consumer request: input descriptions, output descriptions,
bound values and methods can follow different runtime paths. Place the business
meaning where its consumer actually receives it, then verify that path provider-free
where possible. Do not interpret an absent instruction as a model-capability failure
or attribute a better sample to a definition the model never saw.

**Verified follow-up:** a shared business definition placed in consumer instructions
appeared in actual outgoing requests through both integrations. A local endpoint
rejected each request before upstream access, so request construction could be
checked without purchasing an answer. Such a probe establishes delivery only;
expected failed executions must not be reported as successful model behavior.
Keep semantic quality evaluation separate, and keep probes narrow rather than
reconstructing a workflow replay system for a prompt-delivery question.

**Observed source-reconciliation failure:** a local assessor lacked evidence linking
item identities to rate labels. The reviewer received that evidence but promoted the
local gap into global uncertainty and explicitly superseded a supported explanation.
Broader review had previously caught a real error; its correction field later became
the source of a false correction. **Working practice:** resolve a local unknown against
the reviewer's full evidence before declaring a contradiction or withdrawing a claim.
An authoritative itemized quote may be a useful interface improvement when deterministic
pricing already exists, but its effect on reasoning is a hypothesis until tested.

Review neighboring reasoning as well as the targeted defect. Correcting a time
reference or unknown attribute does not establish faithful source attribution,
sound interpretation of prior tests, or clear monetary units. An observed fix may
justify retaining a change while the overall workflow remains unaccepted.

## 10. Optimize reliable work, not the smallest call count

**Observed:** a more decomposed workflow used more calls while eliminating the
observed serialization failures in tested cases. This is a tradeoff, not a general
guarantee of lower cost or greater reliability.

**Working practice:** track total cost, latency, corrections, failures, and business
quality. Parallelize independent assessments when supported and keep dependencies
explicit. Extra skills add overhead and opportunities for inconsistent judgments;
retain boundaries that earn their cost through clearer responsibility or results.

Change one design dimension at a time when practical. If decomposition, prompts,
and output shape change together, attribute results to the combined design. Repeat
observations and vary relevant constraints before claiming generalization. Include
cases where a constraint is satisfied as well as violated. Test transfer to other
models separately rather than assuming it.

## Starting checklist for a new skill tree

- Would a business owner recognize the responsibilities and handoffs as their process?
- Has the lowest reasonable tier been tested on the complete readable baseline, or is a capability-based mixed pack justified at coherent responsibilities, including stronger general-purpose reasoning where needed?
- Can each reasoning skill's responsibility be stated in one sentence?
- Does each skill receive the evidence and parent metadata its judgment requires?
- Can each model generate a small result without copying large source objects?
- Does the runtime own forwarding, collection, and authoritative output assembly?
- Are units, reference points, unknowns, and unresolved prerequisites preserved?
- Are recommendations, authorization, execution, and external processes distinct?
- Can captured inputs and accepted outputs reveal the first incorrect stage?
- Does the effective model request include the semantic definitions needed by that responsibility, rather than only by its coordinator?
- Do validation cases cover both sides of important constraints and combined strategies?

## Maintaining this guide

Read this guide before designing or materially revising a skill tree. Update it
when experiments or reviews establish a transferable lesson, reveal a limitation,
or contradict existing advice. Keep observations, working practices, and hypotheses
distinct. For each material practice, maintain its evidence-map entry with a
bounded claim, current status, supporting observation, and remaining validation.

Change status when the evidence changes, not merely because a practice has been
used for longer. Repeated comparable successes, understandable failure mechanisms,
and relevant variations can justify a stronger bounded claim; there is no fixed
number of runs that proves generality. Broader claims require broader evidence.
Record counterexamples and regressions and narrow or downgrade a claim when
necessary. An unsuccessful proposal may be removed or retained with a clear
explanation of why it is not recommended; it need not progress through the statuses.

Keep detailed evidence and provenance in the project's experiment records. A
status change should be justified there, while this guide retains the general
lesson and its scope. Do not label a remedy demonstrated solely because its
motivating failure was observed or because its schema passed validation.

Keep domain-specific incidents, model rankings, run identifiers, costs, and detailed
results in experiment records and project notes. This guide must remain useful
without a particular run, fixture, or historical archive. Do not turn it into an
experiment log or a collection of prompts tailored to one case.

Keep the checklist aligned with the detailed guidance. Remove duplication and
superseded advice rather than only appending rules. A single successful run does
not promote a hypothesis into a universal best practice.

Last substantive review: 2026-10-07.


### Calculation ownership and review context

**Observed:** final review can mistake a local assessor's information gap for a gap
in the complete case, even when wider sources support the disputed claim.
**Working practice:** the operation that owns a commercial calculation should publish
its usable breakdown and provenance, keeping conditional maxima distinct from actual
charges. Review should consult the broader evidence before superseding an assessment;
disagreement between summaries alone is not a conflict between source records.
**Hypothesis:** authoritative itemization and explicit reconciliation reduce false
uncertainty without adding skills or scenario-specific reminders. One subsequent four-case batch passed with minor caveats and retained supported
pricing; comparison also made a supported owner correction in one case. These
combined edits are promising, not isolated causal evidence or established reliability.
Provider-free checks separately establish delivery and arithmetic preservation. The additional contract size and persistence implications
must be considered alongside the expected business benefit.


### Account for the cost of model optimization

**Working practice:** include authoring time, manual review, maintenance and failure
risk when judging savings from a lower-tier assignment. Keep a stronger model on a
coherent responsibility when it is needed; optimize further only for a worthwhile,
specific opportunity. Distinguish sound process/interface repairs from work undertaken
solely to lower model cost. This does not require an arbitrary effort limit.
**Observation and limit:** this project's repeated tuning prompted a user preference
to retain the practical mixed assignment. It supports caution about diminishing
returns, not a measured break-even point or a universal model-tier conclusion.
Historical stronger-model runs also contained business defects, so not all authoring
effort can be attributed to lower-tier accommodation.


The itemization candidate subsequently passed one unchanged four-case repeat with
minor caveats, giving two passing batches at the same assignment. Targeted pricing
and activity-semantics behavior held, but owner precision and ambiguous prose remain;
empty review-concern arrays do not demonstrate a flawless reviewer. This strengthens
bounded evidence for retaining the practical candidate, not a general reliability
claim or justification for further automatic optimization spending.
