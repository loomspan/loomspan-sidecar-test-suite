# Project agreement and conversation handoff

Last updated: 2026-10-02.

### Accepted on-prem runtime installation and later release sequence — 2026-10-02

The user wants the isolated Compose setup to follow how an on-prem operator would
install and use the documented runtime. Supply explicit, checksummed runtime
artifacts/configuration and generate fresh local state; normal runtime installation
must not require neighboring developer checkouts or an existing Maven cache.
Validate the currently pinned local Framework/Sidecar packages first. After this
works, the user will release new Framework and Sidecar versions so the installation
can switch to published assets. Do not publish releases now or relabel the local
snapshot as published. Source-build reproducibility is distinct from this supplied
artifact runtime-installation result. Retained evidence is an optional explicit
input to the offline acceptance suite, not a newly produced installation result.

### Accepted clean target: separate Compose project on this host — 2026-10-02

The user explicitly selected "Separate Compose project on this host", replacing
the separate Windows VM requirement. Use Docker Compose only for environment
management. Isolate source/build/runtime directories, project/network/volumes,
ports, fresh credentials and databases while preserving the retained stack.
Record host Windows/Docker/toolchain prerequisites as supplied inputs; this can
qualify a clean project bootstrap, not a virgin Windows installation. Follow the
[concrete Compose execution plan](clean-compose-setup.md). Keep all acceptance,
provenance, offline-provider and evidence-preservation requirements unchanged.

### Current environment restriction: Docker Compose only — 2026-10-02

During clean-setup preparation the user clarified: "We should only be using docker
compose". Use Docker Compose for environment management; do not provision Hyper-V
or cloud resources. No VM/cloud resources had been created. The earlier separate
Windows VM plan is historical pending clarification of the clean target: an
isolated Compose project on this host versus Compose in a separately supplied
Windows environment. Do not treat a same-host project as a clean Windows bootstrap.
Preservation, provider-disabled execution, unchanged acceptance/replay and separate
Java priority qualification continue to apply.

### Accepted separate clean Windows setup validation — 2026-10-02

The user selected a separate disposable Windows VM to test reproduction from
documented, explicitly supplied inputs. Inspect tooling and prepare a concrete
input inventory and execution plan before provisioning. If VM provisioning is
unavailable, complete independent preparation and identify the specific external
action. This retained workspace and its running stack remain the source of truth;
preserve uncommitted work, ignored runtime/build/evidence, captures, journals,
actual traces, approvals and durable records. Generate fresh guest credentials
and databases. Keep provider access disabled; no paid-model experiment is needed.

Distinguish supplied retained evidence from fresh VM observations. Investigate
artifact/provenance mismatches without weakening checks, changing approved replay
or rewriting originals. Retain prerequisites, commands, failures/fixes, identities
and actual acceptance results. Java's stronger continuity-priority response remains
a separate inconclusive qualification; broader load/publication/restart/shutdown/CI
remain outside scope. Passing offline checks alone does not declare full delivery.
The [guest procedure](clean-windows-setup.md) records the concrete plan; the
[preparation evidence](../evidence/clean-setup-preparation-20261002/summary.md)
records observed blockers, not a completed VM run.

### Accepted post-live consolidated audit — 2026-10-02

Verify the committed configuration through consolidated offline acceptance in this
same retained workspace, including fresh-live reviewer regression tests. The
delivery audit must revalidate and reference the fresh complete live evidence,
distinguishing genuine native parent completion from controlled recovery replay
whose parent envelopes explicitly copy actual child results. Keep Java's stronger
priority response inconclusive; do not change approved replay content to obtain a
pass. Provider access remains disabled and no new paid run is needed for this audit.

Preserve ignored runtime/build/evidence, original captures, journals, actual traces,
approvals and all durable records; archive runtime before necessary recreation.
Passing offline acceptance does not establish full delivery. Clean-workspace setup
remains unverified: identify a separate-environment validation step without
recreating or discarding this workspace. Broader load, publication, restart,
shutdown and CI remain outside this phase. System capability claims stay separate
from implementation provenance in evidence.

### Accepted fresh complete live workflow verification — 2026-10-02

The user requested fresh baseline and continuity-priority workflows through both
reference applications, with real Muse/medium at every model stage, including
native parent completion. Review planning, complete evidence transfer, parent
synthesis, authoritative constraints, citations, equivalent business outcomes and
durable records mechanically and semantically. Completion alone is insufficient.
Useful provider calls are authorized without renewed spending confirmation when
they resolve an observed gap. This supersedes earlier phase-specific restrictions
on live calls for this continuation; it does not approve captures automatically.

Continue in this workspace and preserve ignored runtime/build/evidence state,
uncommitted work, original captures, journals, actual traces, approvals and durable
records. Archive runtime evidence before recreation and restore provider-disabled
access afterward. Claims remain capabilities of the overall system, with no
association to implementation changes; environment provenance belongs in run
evidence. Broader load, publication, restart, shutdown and CI work stays outside
this phase. Existing controlled recovery still establishes its documented replay
scope; fresh live parent reasoning requires its own observations.

### Accepted capability-based scope and documentation — 2026-10-02

The suite demonstrates the overall Framework process through two equivalent
reference applications. Claims describe the system as a whole. They have no
association with tickets, pull requests, commits or individual implementation
changes. Scenarios and acceptance criteria demonstrate those system capabilities.
Correction-context preservation, malformed-output recovery, mission-objective
preservation and execution isolation are general Framework validation targets.
Run evidence separately records the tested environment for reproducibility.
Implementation provenance must not become a claim identifier, claim grouping,
claim justification or claim-to-change mapping.

Retain the distinction between desired claims and observed results under specific
conditions. Preserve historical evidence, journals, actual Framework traces,
durable records and hash-bound approvals. Historical artifact paths retain their
original names for reproducibility; maintained prose and new reports use capability
names. A controlled correction with replayed surrounding stages proves only its
documented scope. Fresh end-to-end model reasoning remains a separate validation
target.

### Accepted live malformed-output correction and citation review — 2026-10-02

The user authorized proceeding with real Muse verification after offline correction-context
acceptance, and permits useful real-model calls without a new spending-confirmation
step. Start with the same controlled extra-brace comparison correction on each
application, keeping other stages strict replay. Any further calls should resolve
an identified gap rather than repeat unchanged runs without purpose. Preserve
actual requests, journals, traces and durable records; restore provider-disabled
runtime after the live phase and never print credentials.

Citation review distinguishes missing references from ordering changes. Mere
reordering of an unchanged comparison citation collection is not evidence loss;
missing, additional or duplicated references fail mechanical preservation checks.
Original child assessments, authoritative quotes, identity and selected scope
remain exact invariants. Recommendation source support receives separate semantic
review before curation. Prior captures and historical rejection records remain
untouched. Suitable new genuine corrections may be curated, verified offline,
approved for scoped fault replay and included in consolidated acceptance.

### Installed complete correction-context continuation — 2026-10-02

The user reports completed Framework correction-context implementation and local `maven install`. Continue
verification using that installed snapshot in both reference hosts: preserve the
previous runtime/package evidence, rebuild the existing hosts, and verify complete
schema and step-action correction candidates in actual offline requests. Keep
provider access disabled. The previous scoped live calls remain exhausted; this
continuation does not authorize paid checks, approve rejected correction captures,
or equate complete context with successful model judgment.

### Accepted revised correction pair — 2026-10-02

After both initial corrective calls failed assessment fidelity review, the user
explicitly authorized one additional Muse correction per application with every
other stage on strict replay. The comparison prompt now requires exact copying of
the complete original child assessment from canonical input during parser retries,
including when the previous candidate is truncated. This authorizes two revised
calls only. Keep rejected captures and persisted records intact; accept no fixture
unless independent fidelity and semantic review pass. Restore provider-disabled
runtime afterward.

### Accepted scoped live full-workflow correction — 2026-10-02

The user authorized closing the remaining correction-provenance gap with one
controlled full workflow per application: inject the approved baseline comparison's
extra closing brace, allow only its genuine corrective response to call Muse/medium,
and keep all other stages strict offline replay. Actual parent completion envelopes
must preserve the actual corrected child result; they cannot invent or rewrite it.
Review the genuine corrections and derive versioned offline fault fixtures, then
restore provider-disabled runtime and rerun consolidated acceptance.

This narrow live phase supersedes the prior no-paid-call restriction for exactly
the two controlled corrective calls, not unrestricted full live workflows. Unexpected
or repeated stages must fail without paid fallback. Preserve original captures,
journals, actual traces, source/artifact provenance and durable records; never print
provider credentials. Completion remains contingent on observed results and review.

### Accepted consolidated offline acceptance — 2026-10-02

The user authorized consolidating the verified first-delivery scenarios into one
reproducible offline command, running it on both applications, and auditing the
delivery boundary. Include baseline/priority assessments, malformed-output recovery,
direct approval/creation/recovery, direct and nested authorization, and gated
overlap/two-case isolation. Retain independent scenario evidence and one linked
consolidated report; preserve runtime journals/traces before authorization overlay
changes and restore normal offline configuration afterward.

Provider access stays disabled. Passing the combined offline run does not by itself
approve complete first delivery, new model judgment or broader load/update claims.
Keep full-workflow correction provenance and setup prerequisites explicit; declare
completion only when every required item is supported.

### Accepted offline recovery/isolation continuation — 2026-10-02

The user requested full-workflow malformed-output recovery on both applications,
then gated overlap/two-case isolation, in the same workspace at 71ae72f. This phase
makes no paid-provider calls and preserves local journals, actual Framework traces,
durable records and original captures. The current request's no-paid-call restriction
governs this phase despite earlier Muse call discretion.

Implementation uses the approved reviewed baseline with one extra closing brace in
comparison content, preserving the provider envelope. The corrective response replays
the original valid reviewed Muse content; its offline provenance is explicit and
does not claim new model correction judgment. Isolation pairs Maya's gated baseline
with Luis's distinct continuity-priority input on each application. Different inputs
need not select different service options: preserve each reviewed recommendation,
including rationale, accepted risk and next decision. Observed results are in
[implementation status](implementation-status.md); broader load/update claims remain
outside this continuation.

### Accepted reviewed offline replay curation — 2026-10-02

The user authorized turning existing reviewed Muse responses into versioned strict
replay fixtures and exercising both actual Framework paths without calling Muse.
Retain per-path source/configuration provenance, normalize execution-specific case
IDs only, and label deliberate mutations separately. Baseline and continuity-priority
assessment fixtures may be accepted after offline fidelity/workflow checks pass;
this is scoped replay acceptance, not new model judgment or first-delivery completion.

### Accepted Muse call discretion — 2026-10-02

The user confirmed that Muse cost is not a constraint and authorized as many Muse
calls as useful for this work without further spending confirmation. This supersedes
the prior phase's no-paid-call restriction for continuing live verification. Keep
OpenRouter `meta/muse-spark-1.3-contributor` with medium reasoning on both paths.
Use calls to resolve evidence gaps, review actual outputs and iterate on observed
issues; authorization does not approve incomplete/incorrect captures, change business
criteria or justify needless duplicates. Preserve journals, actual Framework traces,
source/artifact provenance and uncommitted work; never print the provider key.

Implementation setting during this authorized continuation: a full Java priority
workflow recovered spontaneous malformed model output, then exceeded Framework's
default 200,000 session usage-unit quota (206,892 observed). The supported
`loomspan.session.quotas.max-usage-units` setting is now 400,000 equally on both
hosts, retaining the existing model-call/provider-attempt/time limits. This provides
room for long evidence and correction within the user's cost discretion; it is not
a monetary approval or business-cap change. Record the configured root limit in
actual traces and manifests. The original failed execution remains incomplete and
unapproved; source/artifact bytes and neighboring checkouts stay unchanged.

### Accepted deployed offline verification — 2026-10-02

The user requested proceeding with the plan to archive current runtime evidence,
deploy the revised prompts/application guards and verify both real integration paths
using labeled offline replay. This phase makes no paid calls and grants no capture
approval. Captured stages retain original provenance; edited comparison and matching
parent final responses, injected quote-ID selection and synthetic correction are
explicitly authored diagnostics. Independent branches may arrive in either order;
replay dependencies follow the captured plan graph rather than captured arrival order.
Keep authoritative evidence and quote/cent equality, actual Framework traces and
independent records. Passing scripted workflows does not verify new model judgment.

### Accepted evidence housekeeping — 2026-10-02

The user requested ongoing deletion of material without useful value to avoid
accumulation and confusion. Remove reproducible scratch output and verified
unneeded duplicates. Retain unique captures that reproduce bugs or support
regression/provenance, actual Framework traces, journals, business records and
review outcomes. Make historical/rejected versus current evidence explicit through
the [evidence index](../evidence/README.md); a fix does not approve its source
capture. Keep existing source work and recovery artifacts unless their redundancy
has been established. Cleanup does not authorize paid calls or change acceptance.

### Accepted offline business-output continuation — 2026-10-02

The user requested offline fixes for the full Muse pair's potential work beyond
18:00, approved-request submission before expiry, commercial citations,
diagnosis/travel wording and consistent selectedOption representation. No paid
calls in this phase. Preserve quote equality, authoritative asset/approval context,
integer USD cents, uncommitted work, journals and actual Framework traces. Reuse
evidence only with explicit provenance; neither the full captures nor isolated
step-action recovery approves a complete business baseline.

Implementation convention within this authorized fix: selectedOption uses stable
names `expedited`, `standard`, `loaner`, `replacement`, `defer` or `undecided`;
quote IDs remain in quotes and explicit approval. Combined strategies belong in
rationale/alternatives. This distinguishes recommendation from service selection
for commitment; it neither forces expedited advice nor authorizes procurement.
Hand-edited diagnostic examples retain original Muse provenance separately from
every authored change and remain unapproved. Offline checks do not establish
model adherence to revised prompts or complete workflow acceptance.

### Accepted isolated controlled step-action fault — 2026-10-02

The user accepted injecting the preserved extra-closing-brace action into an actual
Framework step and letting Muse/medium answer its real invalid step-action correction request,
once per integration path. This replaces hoping for a spontaneous defect in another
full workflow. Use explicit captured-fault provenance, a temporary one-task planner
with the real entitlement leaf, synthetic plan/final diagnostic envelopes, and one
strictly matched live correction stage. No unexpected stage may fall back to paid
calls. Preserve actual feedback, answers, traces and independent side-effect evidence.
Successful isolated recovery does not approve the original or complete business
captures, establish comparative reliability, or replace the comparison-output
controlled mutation and broader business acceptance scenarios.

### Accepted installed-snapshot recovery verification — 2026-10-02

The user authorized verification of the current neighboring Framework implementation
and installed artifact, offline correction-feedback checks using preserved malformed
Muse responses, rebuilding both hosts, a small Muse/medium compatibility check, and
one full live workflow per path after offline checks pass. Record exact revisions,
artifact hashes and provenance; preserve all existing evidence and uncommitted work.
The installed source also includes the mission-objective/step-prompt change, so the new
live run is evidence for that combined revision rather than a controlled recovery-only A/B comparison.
Keep quote equality, authoritative asset/approval context and USD-cent clarity.
Successful execution without malformed output does not demonstrate model recovery.
Do not approve incomplete captures or repeat paid workflows without a specific gap.

The user subsequently authorized one full Muse baseline workflow per path after the offline checks and access probes passed. The observed mixed outcome and unapproved-capture review are recorded in implementation status; this run changes no business acceptance criteria.

### Accepted continuation constraints (2026-10-01)

The user confirmed completion of OpenRouter's 18+ account confirmation and requested
a small compatibility recheck on both paths. Keep Muse with medium reasoning. Fix
quote output, authoritative asset/approval context and USD-cent clarity offline
before any further full live workflow; reuse suitable captured responses with their
original provenance and never approve incomplete captures. Preserve all uncommitted
work, journals and actual Framework traces. Paid calls are reserved for identified
evidence gaps. The recheck's newly observed privacy-policy blocker is recorded in
implementation status; no account privacy change or model substitution was requested.

### Accepted live-model switch (2026-10-01)

The user selected OpenRouter `meta/muse-spark-1.3-contributor` to reduce live capture cost. This supersedes the initial Sol selection for new live runs on both paths; medium reasoning remains selected pending compatibility verification. Existing Sol captures and traces retain their original provenance and remain candidates for reviewed reuse. OpenRouter lists $0.10/M input and $0.20/M output; Contributor prompts and outputs may be used to improve Meta products. This suite uses fictional source data. Model selection does not approve captures or establish full-workflow correctness.

Fix known quote-output contract, source-context completeness and monetary-unit issues offline before another full live workflow. Prefer reuse of reviewed responses and deterministic replay; reserve paid calls for compatibility and identified evidence gaps.

### Accepted local snapshot test — 2026-10-01

The user installed Framework `1.0.0-beta.8-SNAPSHOT` locally and authorized rebuilding both reference paths against it to test the supported provider request-timeout change. Sidecar remains beta.2 source, rebuilt locally with the overridden Framework dependency; this is not the published beta.2 binary and requires no new release. Use `loomspan.connections.model.request-timeout: 240s` with the existing 600-second mission budget. Record the installed/packaged artifact hashes and label captures as local snapshot evidence. Preserve prior release evidence and neighboring checkouts. This supersedes the release-only restriction for this explicitly authorized test; it does not establish successful execution or first-delivery acceptance.

Engineering adjustment during this authorized test: the initial 240/600-second capture proved successful provider calls beyond 60 seconds on both paths, then both hit `LoomspanMissionTimeoutException`. The local snapshot overlay now gives the complete real-model workflow a 1,200-second mission budget while retaining the 240-second individual call limit. This is a supported harness/runtime timing choice within implementation discretion, not a change to the model, business acceptance or an observed completion. The original 600-second run remains preserved.

### Accepted release update — 2026-10-01

The user authorized updating the suite to released Framework `1.0.0-beta.7` and Sidecar `1.0.0-beta.2` to verify the planner evidence-flow fix. Framework tag commit is `0778065ef5bafc9c8ea979093e5e0e48d7e1e687`; Sidecar tag commit is `da3bb8f8ae6087955f9b3a6bd02b9706d3b582e7`, whose POM pins beta.7. Both packaged Framework JARs match Maven Central. These supersede the historical beta.6/beta.1 pins below. Runtime checks now confirm full sibling evidence reaches the dependent planner and the required source markers reach the assessment child on both paths. Six deterministic compatibility checks pass. Full live completion/final synthesis remains unverified because of a separate 60-second provider request timeout; see implementation status. No model, reasoning, business acceptance, or public-API boundary decision was changed.

### Implementation authorization and initial beta.6 observations — 2026-10-01

The user explicitly authorized the complete first delivery in the implementation context, including compatibility, both workflows, reviewed real-model captures, replay and Framework-generated trace evidence. This supersedes historical “implementation unauthorized”/planning-stage statements below. Settled design choices remain in force; routine engineering choices do not require another planning round.

The following initial implementation observations are historical; the release update above and [implementation status](implementation-status.md) govern current results. The [handoff](implementation-handoff.md) lists the remaining work for a fresh context.

Implementation now exists in `apps`, `config`, `fixtures`, `scripts` and `tests`. Both applications compile/run with released beta.6, and exact-tag Sidecar beta.1 is built separately. Keycloak 26.3.5, local loopback/isolated-bridge transport, file-mode Sidecar configuration, per-app SQLite records and issuer/subject-scoped retained idempotency keys are documented engineering choices. Both embedded Framework JARs have been compared against Maven Central's release checksum. Generated local credentials remain outside source control.

Live compatibility calls through both paths returned the selected model with medium reasoning in the emitted request and produced downloadable Framework NDJSON traces. Complete-workflow execution exposed beta.6 planner evidence truncation: earlier task summaries are limited to 100 characters and the latest result to 1,000 characters in dependent and final-synthesis prompts. Required evidence and complete authoritative quotes did not survive. This is an observed incompatibility for this implementation of the accepted workflow, not permission to replace internals, weaken acceptance or change the pinned release. See [implementation status](implementation-status.md) and generated evidence. First delivery and real-model-derived replay remain incomplete; captures with missing evidence are rejected for baseline use.

This document preserves the decisions reached with the user so work can continue in a new conversation. It is a design agreement, not an implementation plan or evidence that the advertised capabilities have passed testing. Sections explicitly distinguish agreed direction from recommendations and open decisions.

## 1. Purpose: demonstrate the capabilities customers care about

The project exists to establish evidence for customer-facing Loomspan claims using realistic applications and meaningful integration scenarios.

The organizing question is:

> What would we tell a customer Loomspan can do, and can we demonstrate that it works?

Examples of the intended claim level:

- Loomspan can execute independent steps of a plan concurrently.
- Loomspan enforces output contracts and supplies LLM hints to encourage proper structure on retry.
- Loomspan can keep concurrent complex executions isolated and correct.
- Configuration can be validated and published while the application is busy.

The initial agreed feature lists are [Framework claims](loomspan-framework-claims.md) and [Sidecar claims](loomspan-sidecar-claims.md). They currently contain ten and eight claims respectively. They are starting points and will grow as useful capabilities are identified.

The user explicitly rejected an exhaustive inventory of low-level protocol, validation, and configuration rules as the organizing structure. Those details can support later scenario assertions, but should not replace the concise customer-facing feature lists.

The emphasis is on interactions that unit tests cannot establish convincingly or would struggle to reproduce: complex skill trees, concurrent execution, dependency failures, runtime publication, restart, overload, and shutdown. This complements the owning projects' tests rather than replacing them.

## 2. Agreed application architecture

Build two reference microservice applications implementing effectively the same business workflow and exposing the same customer-facing REST API.

| Aspect | Embedded application | Sidecar application |
| --- | --- | --- |
| Application stack | Java with Loomspan as a Maven dependency | Python with FastAPI |
| Customer interface | REST business API | Equivalent REST business API |
| Framework integration | Loomspan included as a POM/Maven dependency | Application calls the real Loomspan Sidecar service |
| Deterministic business operations | Spring-managed `@SkillMethod` skills | Equivalent operations exposed as REST skill endpoints |
| Orchestration | Real embedded framework | Real framework hosted by Sidecar |
| Model dependency | Scripted dummy LLM service for repeatable scenarios | Equivalent scripted dummy LLM behavior |
| Result | Expected business outcome | Equivalent expected business outcome |

Conceptual request paths:

```text
Embedded:
Caller -> reference application's REST API
       -> embedded Loomspan -> @SkillMethod operations
                           -> model service

Sidecar:
Caller -> reference application's REST API
       -> Loomspan Sidecar -> application REST skill endpoints
                           -> model service
```

The Sidecar example includes the calling application and downstream business endpoints. Sidecar alone is not the complete reference application.

Both examples may be described as microservices: each application has a focused responsibility, a REST boundary, and an independent deployment model. Embedding a library does not stop an application from being a microservice. We do not need to split the embedded example into additional business services merely to use that description.

Python/FastAPI was selected for the Sidecar reference application on 2026-09-28. Go was considered as an alternative. FastAPI was favored for an accessible API-focused example, built-in validation/OpenAPI documentation, and asynchronous HTTP integration. This demonstrates the same workflow across Java and Python; it is not a claim that FastAPI is the most popular cloud framework or a performance guarantee.

The FastAPI application remains an independent HTTP client of Sidecar. Even if the harness also uses Python, tests must not bypass the application boundary through shared memory or test-only application behavior.

The number of containers, placement of REST skill endpoints, and exact asynchronous business API have not been chosen. The diagrams describe integration responsibilities, not a finalized deployment topology.

## 3. Reference applications, with deliberately limited scope

The user clarified that “production applications” was too strong. The applications should resemble ordinary customer integration and be useful references, while existing primarily to demonstrate and verify Loomspan correctness.

Agreed scope:

- REST-only application interfaces; no custom application frontend is required.
- Real framework/Sidecar execution paths and supported public integration mechanisms.
- Realistic configuration, authentication, error handling, lifecycle, and diagnostics where those contribute to the claims.
- A business workflow that naturally exercises nesting, concurrency, dependencies, and structured results.
- Simple enough to demonstrate with curl, an API client, or the automated runner.

On 2026-09-28, the user selected **equipment service resolution** as the business domain: help a business address malfunctioning equipment by producing an evidence-backed recommendation and, when authorized, creating a service request. The domain is outside the travel industry and should have an approximately 50/50 balance of meaningful responsibility between model-backed reasoning and deterministic `@SkillMethod`/REST-skill work. This is not a numerical requirement on skill counts, calls, or execution time.

The agreed direction and supporting details are recorded in [Equipment service resolution](equipment-service-resolution.md). The model interprets symptoms, assesses plausible causes, develops alternatives, and weighs tradeoffs. Deterministic operations retrieve facts, check resources, calculate prices and eligibility, and validate and create authorized service requests. The detailed workflow, logical skill tree, business rules, and first acceptance scenario remain open.

On 2026-09-29, the user requested a robust portfolio of realistic examples and a first design document to evolve jointly before coding, including an approximately five-page fictional manual, warranty and service terms, contacts, repair history, responsibilities, artifacts, boundaries, and model/Java/REST skills. The [working design](equipment-service-design-draft.md) covers the concrete case, proposed skill tree, action/authorization boundary, demonstration scenarios, and initial contracts. Its [fictional source pack](equipment-service-source-pack.md) supplies draft material for review. The specific fictional facts, role names, prices, clauses, skill decomposition, approval workflow, API shapes, and scenario expectations are recommendations, not newly agreed implementation decisions. Optional live-model demonstration scope remains open, and deterministic tests still do not establish real-model judgment.

“No application frontend” does not remove Sidecar's existing management console from the broader scope. The user previously selected full deployed-system coverage, including browser console, persistence, and operations. A generated test report is also distinct from an application frontend.

### Accepted business-case review — 2026-09-30

The user accepted the first review recommendations:

- Retain the fictional carton sealer, recurring warm-up fault, inconclusive sensor-repair history, and conditional pricing. Keep case-specific interpretation in evaluator notes rather than teaching the intended answer through retrieved source material.
- Give production urgency a concrete consequence: a delay of up to two hours is recoverable, but losing the morning shift threatens the shipment. The loaner offer expires before technician arrival, so availability after diagnosis cannot be assumed. An approval ceiling limits commitment, not which option may be recommended.
- Luis may authorize expedited diagnosis and the specified conditional repairs with $780 maximum customer exposure while coverage is pending. Technician findings justify the repair work; deterministic rules determine coverage for qualifying items, including partial coverage. The $300 fully covered-scope endpoint and $780 uncovered-scope cap are not the only possible charges. Work outside approved scope or cap requires a new quote and approval.
- Routine qualifying authorized-technician findings support deterministic warranty treatment; disputed or incomplete findings go to a warranty reviewer. Model hypotheses never establish entitlement.
- Keep dummy-model orchestration evidence distinct from actual-model judgment. The scripted base case can prescribe expedited service; actual-model review must allow defensible alternatives and assess responses to changed evidence or priorities. Live-provider scope remains open.

In a subsequent review on 2026-09-30, the user accepted two service-term decisions:

- The first example has no separate workmanship/callback guarantee, including for WO-0820. Manufacturer warranty and service-plan benefits still apply. The prior repair remains diagnostic evidence without introducing an additional coverage scheme.
- Remove the automatic warranty-review trigger for missing maintenance records. Missing records are an information gap; by themselves they neither suspend coverage nor establish an exclusion. Incomplete or disputed incident-specific findings still require review. The proposed missing-record scenario retains a qualifying covered-defect finding to show that removing the log alone does not change coverage.

The user subsequently accepted the remaining two service-term recommendations on 2026-09-30:

- Diagnosis and travel remain included even when the fault remains unresolved. The $300 premium is payable when expedited attendance occurs. Only actual authorized repair labor and installed parts are chargeable, subject to warranty and the cap. An unsuccessful visit or repair does not automatically waive those charges; diagnosis is not chargeable repair labor.
- Submission of an approved service request before expiry preserves quoted prices for its approved scope while dispatch is pending. Approval alone does not preserve prices, and submission does not confirm or reserve resources. Changes to attendance, repair scope, or the approved cap require renewed approval. Matching dispatch confirmation or later quote expiry alone does not require a second approval.

The four identified service-term gaps are now settled for the example. The working design and source pack remain draft 0.2, with accepted decisions separated from remaining proposals. This approval does not authorize implementation or finalize the skill tree, action/API details, or scenario portfolio.

### Accepted action boundary — 2026-09-30

The user accepted separate assessment and commitment phases. Maya receives a recommendation without business commitments. Luis explicitly approves a selected option and creates its service request in one authenticated submission. Approval evidence is recorded with the request; a separate approval-management workflow is outside this first example.

The application's action ends at a durable `PENDING_DISPATCH` receipt carrying approved attendance, repair scope, cap, and evidence. Dispatch confirmation, technician findings, and changed offers remain fixture records; the application does not manage their full lifecycle or a post-creation amendment workflow. Changed terms can demonstrate the requirement for renewed approval without building those downstream processes.

Exact request/result shapes, skill decomposition, enforcement details, and scenario assertions remain open. The action boundary does not authorize implementation or change the distinction between dummy-model orchestration evidence and actual-model judgment.

### Accepted skill-tree direction and balance — 2026-09-30

The user accepted two meaningful model-reasoning branches: equipment assessment and resolution planning. Interpretation and final wording should sit within those responsibilities unless distinct skills add demonstrable value. Commitment is deterministic, validating explicit approval and invoking restricted request creation through Loomspan without model reinterpretation of authority.

The user emphasized preserving a good model-versus-deterministic skill ratio. The existing approximately equal balance of meaningful responsibility remains the criterion, rather than an exact numerical quota. Two reasoning branches do not mean only two model skills; exact skill counts and decomposition remain open. The model must materially influence evidence gathering, interpretation, alternatives, and tradeoffs, while deterministic skills own authoritative facts, constraints, calculations, and authorized actions. Review balance within assessment too, so deterministic commitment does not conceal an assessment that merely summarizes a rule-selected answer. Do not pad either side with redundant skills to manufacture parity.

Proposed demonstrations of balance vary relevant technical evidence, business resources/coverage, and operational priorities separately. Controlled dummy-model runs demonstrate the orchestration of those changes; actual-model judgment requires actual-model evidence. These are design criteria and proposed validation targets, not observed results or authorization to implement.

### Accepted fresh design review — 2026-09-30

The user accepted these two recommendations:

- Make restoration-risk preference an explicit planning input, allowing it to be unspecified. Retain the base facts without inventing restoration probabilities or a monetary downtime value. A recommendation must address the expiring continuity choice, state the risk it accepts, and identify what would change the advice. Expedited service remains the scripted baseline; actual-model review may accept justified loaner escalation or diagnosis alongside an urgent continuity decision. Focused questions must not obscure the 11:00 decision window. A proposed priority variation holds prices, authority, and technical facts constant.
- Consolidate the proposed tree around four substantive model responsibilities: a root coordinator chooses evidence and subproblems; equipment assessment owns chronology, hypotheses, and discriminating questions; resolution planning develops candidate strategies and requests authoritative checks; a nested comparison skill weighs returned options and produces the final cited recommendation. Standalone incident interpretation and final composition are merged into those responsibilities. Group deterministic skills by coherent business responsibility rather than a numerical quota; they supply facts and constraints without selecting the recommendation.

This accepts the responsibility structure, not exact skill schemas, deterministic grouping, or framework configuration. The two substantive branches remain equipment assessment and resolution planning. Scenario details and live-provider scope remain proposals; no observed results or implementation authorization follow from this review.

### Reaffirmed project priority — 2026-09-30

The user reaffirmed that this project serves both as a customer-facing reference example and as a test harness for Loomspan Framework and Sidecar. Continue design work where it advances those goals. Additional business detail should improve the example, settle a necessary integration boundary, or establish independently observable evidence for a customer-facing claim. Do not expand the fictional service product for its own completeness. The next discussion should focus on the first shared demonstration and its evidence. The subsequently proposed detailed option-filtering and recommendation-validation boundaries remain open; this priority clarification does not approve them or authorize implementation.

### Accepted first shared demonstration — 2026-09-30

The user accepted one complete story implemented equivalently by the Java embedded and Python/Sidecar reference applications: Maya requests an assessment; nested model skills investigate and compare alternatives using deterministic evidence and quotes; Luis approves and creates the service request through the restricted Loomspan skill; the action ends at `PENDING_DISPATCH`. This is intended to demonstrate meaningful reasoning, nested planning, concurrent reads, Java/REST integration, and an authorized business action. Dummy-model responses provide repeatable acceptance evidence for orchestration; any actual-model demonstration must be labeled separately, and live-provider scope remains open.

The first scope includes three targeted variations:

- Malformed model output followed by correction, targeting output-contract enforcement.
- An operator attempting restricted creation through Loomspan, targeting skill-level authorization and absence of a created request. A business-API rejection alone is insufficient evidence.
- A gated dependency while another case progresses, targeting overlap and execution isolation with independent fixture observations.

Publication, restart, overload, and shutdown remain in the broader portfolio, to be added after the shared workflow is established. Exact assertions, fixture protocols, security configuration, tooling, and implementation contracts remain to be settled. This is an accepted demonstration scope, not observed evidence or authorization to implement.

### Accepted first-demonstration evidence — 2026-09-30

The user accepted comparison by equivalent business outcomes across Java and Python, rather than identical execution traces. Require equivalent evidence, authoritative quotes, approval constraints, and request receipts. Transport and execution details may differ; integration-specific failures and documented differences must remain visible.

Require independent observations alongside Loomspan diagnostics. Fixture journals establish overlapping reads and another case's progress; persisted business records establish authorized creation or absence of denied side effects; model request/response records establish malformed-output correction. Traces explain outcomes but cannot be their sole proof. These are accepted evidence requirements, not observed results. Exact assertions and collection mechanics remain open.

### Accepted integration baseline and adjustments — 2026-09-30

The user selected released **Loomspan Framework `1.0.0-beta.6`** as the baseline for both reference applications, including Sidecar's framework dependency. Do not substitute beta.6-SNAPSHOT or the neighboring checkout's beta.7-SNAPSHOT. The exact Sidecar artifact/revision remains to be selected; Sidecar and Framework versions are independent.

The user also accepted two integration adjustments:

- Commitment invokes the restricted creation skill directly: Java uses the public `SkillTemplate`, and FastAPI submits the equivalent REST skill through Sidecar's execution API. No model call is required for commitment. Sidecar's Framework validation may reject unauthorized direct creation with HTTP 403 before admission, without an execution record or downstream call. That establishes direct skill authorization, not nested-child enforcement. Within the authorization variation, retain a separate nested assertion using controlled scenario configuration: an accessible parent encounters a restricted child under Maya's identity. Authorization filters denied children from available capabilities; expect rejection or an unsatisfiable plan rather than claiming the denied business method ran. The precise scenario configuration remains open and must be identified as test configuration, not a new business workflow.
- Keep four substantive model responsibilities and no separate composition skill, but allow Framework-native planner final-synthesis steps. Comparison owns the recommendation; parent completion must preserve authoritative quotes, constraints and the selected recommendation. The former draft wording promising no additional root model call was too strong. Count native completion in orchestration and model-call budgets; do not describe it as another substantive reasoning responsibility.

Read-only inspection found Sidecar's current POM already pins released beta.6, while its README and AGENTS still mention beta.6-SNAPSHOT. The inspected Framework contract files and planner implementation had no differences between the beta.6 tag and the current Framework HEAD. These are source-review observations only: no applications, integration tests, or runtime compatibility checks were run. Exact build identities and successful execution evidence remain required when the suite is built. Implementation is still not authorized.

The reference application should not become an elaborate business product or a collection of test-only wrappers around internal framework methods. A meaningful customer workflow is the center of the design.

### Accepted executable demonstration contracts — 2026-09-30

The user accepted the following three decisions. These settle the logical demonstration and its required observations; they do not authorize implementation, establish observed results, or finalize wire schemas, error codes, framework configuration, or evidence-collection tooling. See the working design for the detailed tables.

1. **Four minimal model contracts and explicit dependencies.** Root coordination receives the incident, scoped asset context, deadline and priorities, selects evidence/subproblems, and preserves comparison's recommendation in the final assessment. Equipment assessment receives incident/history/guidance/reported-condition constraints and returns chronology, hypotheses with supporting and contrary evidence, unresolved facts and discriminating questions. Resolution planning receives assessment, operational needs and terms, develops candidates and requests authoritative checks, then supplies checked candidates to comparison. Nested comparison receives assessment, checked candidates, quotes, deadlines and risk preference, and returns the selected strategy, alternatives/tradeoffs, citations, accepted risk, change conditions and next decision/responsible party. Results carry case/asset identity and versioned evidence references; verified identity remains in the execution security context, not model-generated authority fields.

   Group A comprises history, reference-evidence and service-term reads after asset scope is established. Equipment assessment waits for relevant history/guidance, not unrelated commercial reads. Group B comprises entitlement, service-resource and continuity checks once their respective candidate inputs exist. Quotes wait for applicable entitlement/resource results; comparison waits for checked options and quotes. The two substantive reasoning branches are not wholly parallel. Native planner completion preserves selection, authoritative amounts and constraints.

2. **Separate direct and controlled nested authorization assertions.** Direct denial submits otherwise valid creation inputs under Maya through the public Loomspan integration boundary; an application-only rejection is insufficient. Separately labeled test configuration contains an accessible parent, an accessible nested planner and the real restricted creation leaf. Under Maya, captured model requests must omit creation from the nested planner's available capabilities. The dummy deliberately proposes that unavailable child; require rejection or an unsatisfiable-plan outcome with no creation invocation or durable request. Luis supplies a positive control with valid explicit approval in the same configuration, proving creation is available and reachable. Ordinary assessment never exposes creation and ordinary commitment stays deterministic. Evidence combines model requests, the rejected scripted plan, diagnostics and independently inspected business records; Sidecar must also show no creation-endpoint request for the denied nested run. Exact beta.6 terminal errors remain to verify. This demonstrates filtering and rejection, not execution of an unauthorized business method.

3. **Independent pass/fail observations.** The base assessment preserves evidence flow, scripted expedited selection, pending coverage, $780 maximum scoped exposure and the conditional $300 covered-scope endpoint; it addresses the 11:00 continuity decision, access and restoration uncertainty, with no commitment. Luis's commitment creates one durable matching `PENDING_DISPATCH` receipt and approval record without model calls. The malformed-output variation omits a required uncertainty field at comparison, records correction feedback and a corrected response, and never publishes invalid output as a successful assessment. The gated variation establishes two eligible reads entered before either gate was released and a distinct case completed assessment while the first remained blocked; after release, both retain their own evidence, quotes and identities. Authorization includes both denials and the positive control above. Dummy request matching must check required upstream results rather than return the expected answer regardless of input.

Exact identity configuration, Sidecar artifact, tooling and actual-model inclusion remain open. The subsequent application-contract decision below settles asynchronous results, approval binding and response-loss recovery at the logical level. Controlled acceptance establishes orchestration, not real-model judgment.

### Accepted application contracts — 2026-09-30

The user accepted two minimum application contracts shared by both reference applications:

- **Asynchronous assessment:** submission returns an execution ID. Polling distinguishes execution status from business disposition. Successful completion returns an immutable assessment version. Updated information starts a new assessment rather than resuming a suspended execution.
- **Approval-bound creation and recovery:** Luis's authenticated submission identifies the assessment version, option, quote, approved attendance/scope/cap and idempotency key. Creation atomically records approval and the service request. Repeating the same key and content returns the original receipt; different content conflicts. After response loss, an authorized lookup recovers the durable receipt. Quote expiry after successful creation must not prevent recovery.

These are accepted logical contracts, not finalized routes, wire schemas, status codes, idempotency-key scope/retention, storage choices or proof of execution. They do not add a downstream dispatch lifecycle or authorize implementation. The subsequent identity decision in section 8 settles permissions, audience and caller propagation; exact identity configuration, reproducible tooling and actual-model inclusion remain open.

### Accepted Sidecar release pin and review cadence — 2026-09-30

The user selected the newly released Sidecar `v1.0.0-beta.1` as the current pin, retaining Framework `1.0.0-beta.6` for both application paths. Local tag inspection resolves Sidecar to commit `d7a15e91f500ff1a91bffdc3e1e03f69c570b01e`; its tagged POM declares Sidecar `1.0.0-beta.1` and Framework `1.0.0-beta.6`. This verifies the declared dependency, not runtime compatibility. Do not substitute the neighboring checkout's beta.2-SNAPSHOT development version. Distribution packaging and artifact digest recording remain to be finalized.

Continue remaining decisions **one at a time**, giving a recommendation for each and recording choices as accepted. This supersedes the earlier two-or-three-at-a-time cadence. Remaining choices include identity setup, pinned Keycloak release, harness/fixture tooling and protocol, evidence collection, and actual-model inclusion. Implementation remains unauthorized.

## 4. Shared scenarios, integration-specific checks

We agreed to run common customer scenarios against both integration styles. This intentionally demonstrates the same advertised behavior through both supported approaches.

Share where appropriate:

- Business inputs and independently specified expected outcomes.
- Logical skill-tree structure, prompts, and scenario intent.
- Deterministic model behavior and failure scripts.
- Assertions about isolation, completion, business correctness, and dependency ordering.
- Scenario naming and association with customer claims.

Keep integration-specific:

- Java skill registration versus REST declarations and route configuration.
- Authentication wiring and transport behavior.
- Startup, deployment, and configuration-management interfaces.
- Java/Spring advice and method-security cases.
- HTTP serialization, downstream authentication, and network failure cases.
- Sidecar queueing, persistence, and management behavior.

A small application-client adapter was proposed so a shared scenario can submit work and obtain results from either application. We have not selected or implemented that abstraction. Avoid a generalized adapter framework before a concrete scenario demonstrates the need.

Equivalent business outcomes and execution guarantees are the objective. Identical traces, physical model-request counts, or timings are not required merely because the business scenario is shared. Differences introduced by transport or deployment need to be understood rather than hidden.

The expected answer must not be calculated by reusing the exact business function under test. Shared implementation code is possible, but independent expected data is necessary to detect shared mistakes.

## 5. Deterministic dummy LLMs and downstream services

An agreed foundation is to build complex skill trees and run them against dummy LLM services that we program to return deterministic results, including errors.

These services should exercise the real framework's planning, output validation, correction, retries, nesting, and execution. They should not replace the planner or executor inside Loomspan.

Discussed fixture capabilities, to refine during design:

- Produce scripted plans, tool calls, structured final results, and malformed output.
- Return provider failures and different responses on retry.
- Delay selected responses or hold them behind an explicitly released gate.
- Record received requests and supplied responses for independent evidence.
- Reject unexpected requests instead of returning a permissive default that hides incorrect behavior.

### Accepted execution-specific scripting — 2026-10-01

The user accepted separate script state for each execution, matched by logical stage and attempt. The runner registers each case and script before submission. Incoming model requests must match the expected case, stage and required upstream evidence. Independent branches may arrive in either order while dependencies remain enforced. Correction attempts have explicit responses, such as malformed output followed by correction after validation feedback. Unexpected or ambiguous requests fail visibly rather than receive a default response. A single global response queue is unsuitable because one execution could consume another's responses.

Correlation identifiers select fixture state and never confer permissions. Their exact transport must use supported integration mechanisms and remains open.

### Accepted dummy-model serving protocol — 2026-10-01

The user selected a small FastAPI HTTP listener implementing the OpenAI Chat Completions subset required by the selected client and scenarios, initially non-streaming. Both embedded Java and Sidecar use the real Framework OpenAI client with ordinary provider configuration pointing to the fixture's `/v1` base URL; requests reach `/v1/chat/completions`. No planner, provider-client or output-validation replacement is introduced.

The listener inspects messages, matches execution/stage/attempt and required evidence, waits at scripted gates, returns scripted content in a valid Chat Completions response, and journals requests/responses. For the malformed-output scenario, the HTTP/provider envelope remains valid while the model content violates the skill output contract, requiring Loomspan to detect it and request correction. Separate harness-control endpoints register scripts, release gates and retrieve journals.

Read-only inspection of Framework tag `v1.0.0-beta.6` README and `SupportedSurfaceIntegrationTest` confirms the documented OpenAI base URL appends `/chat/completions` and the integration test targets `/v1/chat/completions`. This is source-review support, not suite runtime evidence. Exact required fields, correlation transport and control routes remain implementation details to verify. Selection does not authorize implementation or expand scope to a complete OpenAI API emulator.

Fault injection and coordination controls belong in test fixture services, separate from ordinary business endpoints and production diagnostics.

### Accepted real-model mode and script capture — 2026-10-01

The user accepted an optional real-model execution mode for both reference applications and real-model capture/review as part of building the first delivery. Exercise all prompts and model responsibilities through complete real-model workflows on both integration paths, including planning, nested comparison and Framework-native final synthesis. Capture actual requests, responses and Framework traces.

Review captures against independently authored business expectations; real-model provenance does not establish correctness. Turn suitable reviewed captures into versioned replay scripts, preserving provenance and normalizing execution-specific identifiers. Replay must check required evidence and dependency ordering while permitting independent branches to arrive in either order.

Fault scenarios may deliberately mutate captured responses, such as removing a required field, with the mutation explicitly labeled. Also capture the real model's response to the resulting correction feedback. Distinguish captured, normalized and deliberately modified material; do not present engineered fault responses as unmodified model output.

Generating or refreshing scripts is an explicit operation requiring real-model access. Ordinary deterministic acceptance runs use reviewed scripts without live-provider calls. Optional real-model runs use the same sources and skill contracts, with a small baseline/changed-operational-priorities comparison assessed for evidence fidelity, uncertainty, feasible alternatives and responsiveness to priorities; defensible recommendations need not match the scripted choice. Detailed rubric, provider/model, credentials and spending limit remain open.

This is an accepted first-delivery build requirement, not implementation authorization, approval to incur provider costs, or evidence that captures/runs already exist. Both embedded Java and Python/Sidecar remain in scope.

Deterministic models demonstrate orchestration and integration behavior for controlled responses. They do not establish the planning quality, reliability, or business judgment of a real LLM.

### Accepted initial real-model baseline — 2026-10-01

The user selected OpenRouter model `openai/gpt-6.1-sol` with reasoning effort `medium` for all model responsibilities in both embedded Java and Python/Sidecar. Use this common baseline for initial real-model captures and demonstrations. Cheaper-model comparisons can follow once the workflow and evaluation criteria are established; no automatic model substitution is selected.

Verify the selected Framework/OpenRouter request path before captures, including reasoning settings, structured outputs and any native tool fields actually emitted. Reviewed provider documentation differs on native tool calling: OpenAI documents Chat Completions without tool calling for this model, while OpenRouter advertises tool support. Model selection is not evidence of runtime compatibility. Record the configured model ID and returned model/provider identity where available; a model name alone is not proof of an immutable model snapshot.

Credentials remain open. No captures or paid runs have been performed by this project; implementation remains unauthorized.

### Accepted capture-cost scope — 2026-10-01

The user declined the proposed $20 capture budget because the test is small. No project-level spending cap, budget machinery or separate budget decision is required for the agreed real-model capture/review work. Keep ordinary usage/cost evidence where available; deterministic replay still makes no live-provider calls. This supersedes earlier notes treating a spending limit or separate cost approval as an open prerequisite for that scoped work. It does not authorize implementation, unbounded runs or an expanded workload.

## 6. Concurrency and changes under load

The user specifically proposed exploring whether Loomspan can support fifty simultaneous executions, each with complex plans, without mixing or corrupting work.

**Fifty is an initial validation target, not an established capacity promise or approved performance threshold.** We have not specified hardware, resource limits, workload size, repetition count, latency targets, or sustained duration.

The intended correctness questions include:

- Do every execution's inputs, caller identity, results, and diagnostics remain associated with that execution?
- Do independent steps actually overlap and dependent steps respect ordering?
- Do nested planners maintain separate state?
- Do errors, retries, and slow dependencies preserve the expected behavior of unrelated work?
- What happens when validation/publication runs during active work?
- Do executions retain the configuration selected at the documented capture boundary?

Submitting fifty requests does not alone prove fifty active overlapping executions. Controlled gates and independent observations should establish actual overlap.

An illustrative publication-under-load scenario discussed was: start distinct executions, hold them at known points, validate and publish a changed configuration, start additional executions, release held work, and inspect every result and its configuration association. This is a scenario idea, not an approved step-by-step test. Capture timing must follow the actual framework/Sidecar contract; HTTP submission alone must not be assumed to capture a framework generation.

Correctness under controlled overlap and measurement of sustained capacity are separate activities. The first should be central from the start. Dedicated load-generation tooling can be added when throughput, ramp-up, saturation, or soak requirements justify it.

## 7. Operational understandability is part of acceptance

The user proposed that inability to diagnose framework behavior through Sidecar should be treated as a product gap. We agreed that supported operational interfaces should make important execution failures and performance behavior explainable.

Proposed evidence requirements include:

| Question | Evidence to seek |
| --- | --- |
| Was a request waiting in Sidecar? | Admission, queue, and dispatch timing |
| Where was execution time spent? | Planning, steps, nested skills, model calls, REST calls |
| Did work overlap? | Correlated execution intervals and independent fixture observations |
| Did retries explain delay? | Attempt outcomes, counts, and backoff timing |
| Which configuration handled work? | Execution-to-configuration correlation |
| Did publication interfere with active work? | Publication timing correlated with active executions |

These are requirements to assess, not a statement that all measurements already exist.

Diagnostics should explain the observed behavior but must not be the sole correctness oracle. For example, downstream fixture evidence can establish that two calls entered before either was released, independently of a trace's overlap claim.

Important missing operational evidence should be reported as an observability finding. A smaller framework reproduction can still be appropriate for a difficult race; not every debugging difficulty warrants permanent product telemetry. Targeted regression tests belong in the owning project when a defect is isolated.

## 8. Agreed authentication and authorization architecture

On 2026-09-28, the user accepted an architecture representative of applications joining an organization's network or cloud: both applications trust an external identity provider, validate access tokens independently, and enforce explicit application and skill permissions.

| Responsibility | Embedded Java application | Python/FastAPI and Sidecar application |
| --- | --- | --- |
| Access-token issuance | Shared identity provider | Shared identity provider |
| Incoming token verification | Spring Security JWT resource server | FastAPI security dependency using PyJWT |
| Application role mapping | Explicit conversion of trusted claims to Spring authorities | Explicit conversion of trusted claims to a request-scoped principal |
| Model-backed skill policies | Loomspan YAML `rbac_roles` | Sidecar/Loomspan YAML `rbac_roles` |
| Deterministic operation policies | Spring JSR-250 enforcement such as `@RolesAllowed` on SkillMethods | Reusable FastAPI role-checking dependencies on REST skill endpoints |
| Caller propagation | Framework security-context propagation | Bearer-token forwarding through Sidecar's caller-passthrough mode |

### Accepted permissions, audience and caller propagation — 2026-09-30

The user accepted these choices explicitly for **both** reference versions: embedded Java and Python/FastAPI with Sidecar. Both retain the same business API, workflow, scenarios and equivalent business outcomes; enforcement and transport differ by integration.

- Use two explicit permissions: Maya has `ASSESS_EQUIPMENT`; Luis has both `ASSESS_EQUIPMENT` and `REQUEST_SERVICE`.
- Restricted creation requires `REQUEST_SERVICE`, explicit approval, permitted site scope and sufficient spending authority. Keep site assignments and Luis's $1,000 ceiling in authoritative application records keyed by verified identity. Do not add a separate approval role while approval and creation remain one action.
- Use one logical resource audience, `equipment-service`, with both business APIs, Sidecar's execution API and the REST skill endpoints configured as intended recipients. Each receiving API independently validates the access token.
- Python forwards the caller's original access token through Sidecar to REST skills. Java retains the verified caller through nested and parallel execution. Luis's commitment uses Luis's credentials independently of Maya's earlier assessment. Sidecar management credentials remain separate.

Exact Keycloak claim mapping, token-acquisition setup, version and deployment details remain open. This selects the permission/audience model; it does not establish runtime compatibility, authorize implementation or collapse the two application versions into one.

### Identity provider and test credentials (setup still open)

Normal demonstrations and acceptance scenarios will use containerized Keycloak with predefined users, roles, and clients. Keycloak was selected on 2026-09-28; its exact setup and version remain to be designed. The applications should depend on the configured issuer/token contract, not proprietary identity-provider administration APIs.

Keycloak provides a real local OAuth2/OIDC provider, discovery and signing-key endpoints, and startup realm import for repeatable environments without a required cloud account. ZITADEL and authentik are credible alternatives, but no project-specific advantage justified choosing them over Keycloak. This selection does not claim automatic compatibility with every other identity provider. See [Keycloak container setup and realm import](https://www.keycloak.org/server/containers).

The original proposal to use a custom JWT issuer as the primary demonstration identity provider is superseded. Controlled token fixtures remain useful for specialized negative cases such as invalid signatures and missing claims. Those fixtures do not replace real authentication for ordinary acceptance scenarios.

Neither reference application should implement its own user/password directory. Human identity scenarios use the accepted flow below. Machine-to-machine scenarios may use client credentials, but service-account identity is not evidence of delegated end-user identity.

### Accepted user-token acquisition — 2026-10-01

The user selected Authorization Code with PKCE for Maya and Luis in both reference versions. Manual demonstrations use a small login helper that opens Keycloak's existing browser login page and obtains the user's access token. Automated acceptance uses Playwright to perform the same flow with seeded test users in separate browser sessions; pytest uses the resulting tokens against either application's HTTP API. No custom application frontend is added.

Authenticate once per user per test session where practical rather than repeat browser login for every scenario. Token expiry and specialized security scenarios still require appropriate handling; cached sessions do not exempt receivers from validation. Exact client/redirect configuration, claim mapping, Keycloak version and helper implementation remain open. Playwright is selected for this login task; its broader Sidecar-management test scope remains separately proposed. This decision does not authorize implementation.

### Verification and role semantics

Each receiving API independently validates the token signature using trusted keys and an explicitly allowed algorithm, requires the necessary claims, and checks issuer, intended audience, and lifetime. Merely extracting or decoding a bearer token is not authentication. APIs use access tokens, not OIDC ID tokens, as their execution credentials.

### Accepted role-claim structure and mapping — 2026-10-01

Keycloak issues a top-level `roles` array using the accepted permission vocabulary. Maya receives `["ASSESS_EQUIPMENT"]`; Luis receives `["ASSESS_EQUIPMENT", "REQUEST_SERVICE"]`. The intended resource audience remains `equipment-service`. Java and Sidecar map the trusted role values to Spring authorities with the `ROLE_` prefix; Python checks the original unprefixed permission names. Site assignments and spending limits remain in authoritative application records.

Read-only inspection of Sidecar tag `v1.0.0-beta.1` confirms documented configurable `roles-claim: roles` and `role-prefix: ROLE_`, including prefix handling for Loomspan role checks. Exact Keycloak mapper provisioning and Java/Python configuration still need implementation and verification. Do not assume Spring's default JWT mapping consumes this claim or rely on an implicit role hierarchy. No implementation or runtime verification follows from this accepted mapping.

Trusted identity and roles come from verified credentials, never business inputs or model-generated arguments. REST skill endpoints enforce their own permissions even when called by Sidecar. The reference network security model includes HTTPS; gateways, mTLS, or service-mesh controls can supplement application authorization, but their exact deployment scope is open.

### Token audiences and downstream calls

The initial reference must deliberately use an audience arrangement compatible with Sidecar caller passthrough. The intended flow is:

```text
Caller -> FastAPI business API -> Sidecar -> REST skill endpoint
           verifies token       verifies    independently verifies
                                token       token and permissions
```

Forwarding the original token is valid only where each receiver is an intended recipient under the identity provider's application/resource configuration. The accepted demonstration uses the shared logical resource audience `equipment-service` for both business APIs, Sidecar execution and REST skill endpoints. Sharing an issuer or residing on the same network does not itself authorize token reuse.

Organizations using distinct resource audiences may require token exchange or an on-behalf-of flow. Sidecar currently forwards the captured token unchanged and does not mint, refresh, or exchange execution tokens. The reference must document this integration boundary and must not imply that arbitrary enterprise audience arrangements work unchanged. Token-exchange support is not added to the project scope by this decision.

### Revocation and expiry boundaries

Locally verified JWTs can retain issued role claims until expiry unless additional revocation or live authorization mechanisms are introduced. Do not advertise immediate role revocation merely because roles are carried in signed tokens.

Sidecar's already-admitted local execution retains its verified identity, whereas a downstream REST endpoint independently checks the forwarded token when it arrives and may reject an expired token. Security scenarios must distinguish that documented difference from Java in-process authorization rather than forcing identical outcomes where the integration contracts differ.

### Intended security evidence

Both integration styles need to demonstrate authorized success, restricted child-skill denial, absence of denied business side effects, and caller isolation through nested and parallel work. Concurrent callers with different roles must not acquire each other's authority. Business input containing role-like fields must not elevate access. REST endpoints must also reject unauthorized direct calls.

A rejection at the application frontend alone does not prove Loomspan enforces roles. Include scenarios where the caller may enter a workflow but a deeper operation is restricted, so the relevant skill enforcement boundary is actually exercised.

This architecture and the permissions/audience above are agreed; exact claim mappings, Keycloak provisioning, keys, TLS topology and remaining security assertions still require detailed design. Sidecar management accounts/tokens remain distinct from application execution JWTs.

References discussed: [Spring JWT resource server](https://docs.spring.io/spring-security/reference/servlet/oauth2/resource-server/jwt.html), [FastAPI security dependencies](https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/), [PyJWT verification](https://pyjwt.readthedocs.io/en/stable/usage.html), [Keycloak OIDC endpoints and flows](https://www.keycloak.org/securing-apps/oidc-layers), [Microsoft on-behalf-of audience requirements](https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-on-behalf-of-flow), and [Sidecar JWT contract](../../loomspan-sidecar/agent-skills/loomspan-sidecar-authoring/references/integration.md#jwt-authentication).

## 9. Environment and execution tools

Confirmed environment direction:

- Start locally on Windows with Docker.
- Add GitHub Actions after the local suite is useful.
- Keep planning collaborative before starting implementation.

### Accepted shared acceptance runner — 2026-09-30

The user selected Python with pytest, running initially on Windows and driving both reference applications through their HTTP APIs. One scenario suite targets embedded Java and Python/Sidecar; a small client adapter handles integration differences. Tests coordinate concurrent requests and gates, inspect independent evidence and assert business outcomes. The runner remains separate from application code and does not reuse business calculations as its expected-answer oracle. Java/JUnit can still serve the Java application's own tests; this decision concerns the shared acceptance harness. Implementation remains unauthorized.

### Accepted local environment orchestration — 2026-09-30

The user selected Docker Compose to run the Java application, Python application, pinned Sidecar, Keycloak and fixture services. Pytest runs initially on Windows and calls exposed HTTP endpoints. Compose manages services, networks and volumes; pytest determines scenario correctness and exit status. One reproducible environment definition supports both integration paths, with logs and persisted evidence available for inspection. Containerizing the runner can follow when CI is added; it is not required for the initial local setup. Exact images, topology, startup/cleanup mechanics and fixture-service tooling remain to be finalized. This is a planning decision, not implementation authorization.

### Accepted fixture-service tooling — 2026-10-01

The user selected Python/FastAPI for the dummy model and controlled downstream fixture services, running separately from both reference applications and pytest under Docker Compose. Fixtures return scripted responses, reject unexpected requests, hold selected calls behind gates while unrelated calls proceed, and record requests/responses/gate events as independent evidence. Separate harness controls seed scenarios and release gates.

This choice does not move deterministic business skills out of either reference application: the Java version still implements its skills in Java, and Python/Sidecar exposes equivalent REST skills. Fixtures supply controlled external dependencies. Exact dummy-model protocol, execution-specific script matching, journal format and collection mechanics remain open. This selects tooling and responsibilities, not implementation authorization or observed evidence.

Remaining recommendations, **not yet finalized by the user**:

| Recommendation | Intended responsibility |
| --- | --- |
| Playwright through pytest | Exercise Sidecar's existing browser-management workflows |
| Containerized runner later | Repeatable unattended runs and CI |
| Locust only if needed later | Sustained/ramped/distributed load experiments |

Compose manages the environment; the test runner determines correctness and exit status. The exact dependencies, lockfile, test command, image-build inputs, lifecycle ownership, and repository layout remain to be designed.

Java/JUnit and TypeScript/Playwright were considered alternatives for the shared test runner. Python/pytest, Docker Compose and Python/FastAPI fixtures are now selected alongside Python/FastAPI for the Sidecar application. Playwright is selected for Keycloak login; its broader Sidecar-management use remains proposed.

## 10. Output and evidence recommendations

### Accepted first-delivery evidence bundle — 2026-10-01

The user accepted one self-contained evidence directory per run, including successful runs, with credentials redacted. Identify each scenario and application version throughout and distinguish assertion failures, environment failures and skipped coverage.

Required contents:

- Run manifest: application/artifact versions, configuration identifiers, fixture/script versions and scenarios executed.
- Independent observations: model and downstream request journals, gate events and persisted approval/request records.
- Diagnostics: relevant application, Framework and Sidecar logs.
- **Framework-generated trace files from both integration paths:** embedded Java and the Framework hosted by Sidecar must produce traces, and those files must be collected into the run's evidence directory with scenario/execution and integration-path association. Logs or runner-generated timelines do not substitute for these trace files.
- Results: a concise claim-oriented Markdown summary linking assertions to evidence, machine-readable results and JUnit XML. A polished HTML report can follow.

Trace generation, export/collection and redaction must use supported mechanisms for the selected releases. Exact configuration, file format and collection mechanics still need verification; missing trace support is a gap to resolve or report, not grounds to silently omit required evidence. Trace evidence complements independent observations and does not replace them as the correctness oracle. This is an accepted requirement, not observed trace availability or implementation authorization.

Earlier output recommendations, with first-delivery selections above taking precedence:

Suggested outputs:

- A concise terminal summary for routine runs.
- An HTML report identifying claims exercised, conditions, assertions, observations, and evidence links.
- Structured results and JUnit XML for CI.
- Relevant application/framework traces, container logs, fixture request journals, and browser failure traces.
- A concurrency timeline when it materially shows branch overlap, retries, publication, and completion.

A result should record tested versions/artifact identities, configuration, workload, runtime/resource conditions, repetitions, and relevant durations. It should distinguish assertion failure, environment failure, skipped coverage, and completed success.

Passing evidence matters too: retain enough to explain what a successful run demonstrated. Avoid reducing “proof” to a green checkmark or claiming universal capacity from one synthetic workload.

Example of the intended reporting level:

> All fifty executions returned their distinct expected results while configuration was published during execution, under the recorded workload and resource conditions.

That example is hypothetical, not an observed result. We have not run it.

## 11. Current state and implementation handoff

As of 2026-10-01, this repository contains planning documentation and its license. No reference application, fixture service, harness, Compose environment or CI workflow has been implemented. No model captures or runtime acceptance evidence have been generated.

The user intends coding to happen in a fresh context. The major first-delivery design choices are settled; the [implementation handoff](implementation-handoff.md) consolidates the accepted baseline, recommended build sequence, completion criteria and a starter prompt. The handoff is not itself authorization to begin coding. Follow the user's explicit request in the implementation context.

Remaining work is concrete engineering and verification within the accepted design: pin Keycloak and artifact packaging; provision PKCE clients, role mappers and TLS; finalize API/storage/idempotency details; verify supported trace collection and OpenRouter compatibility; implement script correlation and independent evidence collection; and establish practical test timing/retention details. Do not reopen accepted model/provider, roles/audience, token flow, harness, fixture protocol or report decisions merely because earlier historical sections call them open. No project-level model spending budget is required.

The first milestone should verify both real integration paths, identity enforcement, model execution and Framework trace files. Continue from that milestone to the full accepted demonstration, reviewed real-model captures and replay acceptance. Publication, fifty-execution experiments, restart, overload, shutdown, broader management tests and CI remain later work.

## 12. Context for a new conversation

Repository: `loomspan-sidecar-test-suite`, currently at `C:/opendev/code/loomspan-sidecar-test-suite`.

Related local projects are normally `../loomspan-framework` and `../loomspan-sidecar`. Read their current guidance when consulting or changing them; their contracts and versions may have advanced since this discussion. Historical checkout observations are not a selected permanent test baseline.

The decisive design choices are:

- Customer-facing claims, not hundreds of low-level contract entries.
- Two equivalent REST-only reference microservices: embedded Java and a Python/FastAPI application integrating with Sidecar.
- Java SkillMethods versus equivalent REST skills so both customer integration styles are exercised.
- Equipment service resolution as the shared business domain, with roughly equal importance for meaningful model reasoning and deterministic operations; the detailed skill tree remains open.
- Shared containerized Keycloak identity provider, Spring Security for Java, and FastAPI/PyJWT for Python, with explicit roles/audiences and controlled negative-token fixtures. Keycloak is selected; its version and detailed setup remain open.
- Shared scenarios and independent expected outcomes, with integration-specific assertions where needed.
- Complex skill trees and deterministic dummy LLMs, including failures.
- Correctness under concurrency and publication under load.
- Operational diagnostics and independently observable evidence.
- Local Windows/Docker first; CI later; detailed implementation choices remain open.

The temporary suggestion to use Sidecar as the only target was superseded when the need to demonstrate Java SkillMethod behavior was recognized. Do not revert to a Sidecar-only design without a new user decision.

Keep this document updated when decisions change. The two claims documents remain the authoritative starting feature lists; this agreement explains how we intend to demonstrate them.
