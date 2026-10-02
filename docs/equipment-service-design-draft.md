# Equipment service resolution: working design

Current implementation note (2026-10-01): implementation is authorized and underway on Framework beta.7 / Sidecar beta.2. This document retains domain/design history; any older release, authorization, “no captures,” or “not yet verified” statements describe that earlier planning stage. Apply the latest accepted decisions in [project agreement](project-agreement.md), resume from [implementation handoff](implementation-handoff.md), and use [implementation status](implementation-status.md) for observed results and remaining work.

Draft 0.2 — 2026-09-30. For joint review before coding.

The equipment-service domain, equivalent Java and Python/Sidecar applications, meaningful balance of model and deterministic work, and deterministic acceptance testing are agreed. The user has requested a richer fictional business world and a robust set of examples. **The review decisions listed below are accepted; other specific terms, roles, skills, API shapes, scenario expectations, and implementation recommendations remain proposals.** No scenarios have been executed.

### Accepted business-case review — 2026-09-30

Keep the carton sealer, recurring warm-up fault, inconclusive prior sensor repair, and conditional pricing. Make source material less leading by keeping case-specific interpretation in evaluator notes. Operations can recover a production delay of up to two hours, but losing the morning shift threatens the shipment. Loaner availability cannot be assumed after diagnosis because its offer expires before technician arrival. Spending authority constrains commitment rather than determining the best recommendation.

Luis may authorize expedited diagnosis plus the specified conditional repairs at $780 maximum customer exposure while coverage is pending. Findings determine justified repairs, and deterministic rules apply coverage to qualifying items, including partial coverage. Work outside the approved scope or cap needs a new quote and approval. Routine qualifying technician findings support warranty treatment; disputed or incomplete findings go to the reviewer.

Further accepted on 2026-09-30: the first example has no separate workmanship/callback guarantee, while manufacturer warranty and service-plan benefits still apply. Prior repair history remains diagnostic evidence. Missing maintenance records are an information gap; they do not by themselves trigger warranty review, suspend coverage, or establish an exclusion. Incomplete or disputed incident-specific findings still require review.

Also accepted on 2026-09-30: diagnosis and travel remain included when a visit is unsuccessful; the $300 premium is payable when expedited attendance occurs. Only actual authorized repair labor and installed parts are chargeable, subject to warranty and cap. Submission of an approved service request before expiry preserves quoted prices without confirming resources. Changes to attendance, repair scope, or cap require renewed approval. These decisions do not approve the full skill tree, API, scenario portfolio, or implementation.

Read this alongside the [domain overview](equipment-service-resolution.md), [project agreement](project-agreement.md), and [fictional source pack](equipment-service-source-pack.md). The source pack contains actual draft material to reason over, including a manual arranged into five intended pages; it is not yet a paginated PDF.

### Accepted action boundary — 2026-09-30

Assessment and commitment are separate business phases. Maya's assessment produces a recommendation without business commitments. Luis explicitly approves the selected option and creates its service request in one authenticated submission; there is no separate approval-management workflow. The application's action ends with a durable `PENDING_DISPATCH` receipt containing the approved attendance, repair scope, cap, and evidence. Dispatch confirmation, technician findings, and changed offers are fixture records rather than application-managed lifecycles. Detailed skill and API contracts remain proposals.

## 1. Proposed experience and scope

The application helps a maintenance team turn an incomplete fault report into an evidence-backed service decision. Its useful output is a recommended next action, why it is preferable, what it costs under explicit assumptions, what remains unknown, and who must act next. An authorized caller can then create a service request tied to that recommendation.

Use one fictional machine family, the **AsterPack P240 carton sealer**, at **Northbank Fulfillment**. The manufacturer is **Aster Equipment** and the authorized service provider is **Beacon Field Service**. Start with one site and a small set of assets; add a second customer solely when demonstrating data and caller isolation. These are invented organizations, equipment, and terms.

The workflow should resemble a competent service coordinator. It gathers facts, distinguishes repeated symptoms from confirmed causes, consults the correct guidance, evaluates support entitlements, compares practical alternatives, and prepares a handoff. It does not operate machinery or autonomously certify repairs.

| Include in the reference | Keep outside the first version |
| --- | --- |
| Fault reports, manual excerpts, service history, warranty and contract evidence | OCR, scanned documents, image diagnosis, live telemetry ingestion |
| Model assessment, information gaps, alternatives, recommendation | Training a diagnostic model or proving industrial diagnostic accuracy |
| Parts, technician and loaner availability; deterministic quotes | A full inventory, procurement, accounting, or field-service platform |
| Customer permissions, spending authority, auditable service-request creation | Payments, purchase orders, supplier negotiation, real email/SMS or calendar delivery |
| Questions and revised assessments as explicit REST submissions | A custom chat UI or suspended execution awaiting human input indefinitely |
| Simulated business records and controlled failures | Real equipment control, physical dispatch, or unrestricted external actions |

Realism comes from evidence that changes the decision, not from the number of integrations. A few coherent records are more useful than hundreds of interchangeable documents.

## 2. Planning step 1: one concrete business case

### The report and known facts

Start the controlled business clock for the base fixture at **2026-09-29 09:00 America/Los_Angeles**, advancing it explicitly to 09:05 for the quoted offers. Later approval steps advance it within or beyond the offer-validity window according to the scenario. Business deadlines and warranty dates use this controlled clock; token validation must continue to use its real security clock.

Maya Chen, a line operator, reports that asset `NB-P240-017` stops with `E17` after 35–50 minutes, starts again after cooling, and failed again after the permitted sensor-window cleaning. Tomorrow's production run starts at 06:00. No smoke, unusual odor, or damaged guard is reported; that is a report, not a safety certification.

Operations reports that a delay of up to two hours is recoverable, while losing the morning shift threatens the shipment. No monetary downtime value is supplied. The loaner offer expires at 11:00 today, before the offered diagnostic visit begins; it is not a confirmed fallback after diagnosis.

Accepted in the fresh review: restoration-risk preference is an explicit planning input and may be unspecified, as in this base case. Do not invent restoration probabilities or a monetary downtime value. The recommendation must address the expiring continuity choice, state the risk it accepts, and identify what would change the advice. Expedited diagnosis, immediate loaner escalation, or diagnosis alongside an urgent continuity decision may be defensible depending on the evidence and priorities. Focused questions must still make the 11:00 decision window clear.

The available records show:

- The machine is within its warranty date range, but the cause of this incident has not been certified.
- The sensor was replaced six weeks ago for a similar symptom. The closeout recorded a 20-minute test, shorter than the newly reported failure interval.
- A later operator note reports a recurrence after 42 minutes. The technician has not investigated that recurrence.
- A service bulletin for this model/revision identifies a connector issue as another possible explanation; it does not establish that this machine has that fault.
- An expedited qualified technician slot is available today. Standard attendance is tomorrow after the production deadline.
- A compatible sensor and connector kit can accompany the visit. Stock and attendance are quotes, not reservations.
- A loaner can arrive tonight but costs more than the accepted $1,000 manager spending limit. A permanent replacement arrives too late.

### Evaluator notes: what we want the model to do

The model should recognize that replacing the same sensor again is not justified solely by the fault code. It should connect the warm-up interval, recurrence, short closeout test, and bulletin, and explain plausible causes without declaring a diagnosis. The scripted base case recommends an expedited diagnostic visit with relevant parts available if subsequently needed. Actual-model evaluation may accept another defensible recommendation.

The closed work order and later recurrence are not inherently contradictory: the closeout describes a particular test, not permanent resolution. Assess whether the model draws that distinction from the records. Keep this interpretation and the intended recommendation out of retrieved source passages; supplying the answer as evidence would weaken the judgment demonstration.

It should compare that visit with standard attendance and the loaner. The deadline favors expedited attendance, but technician arrival does not guarantee restored production. It should identify the loaner as a continuity alternative requiring higher approval, rather than silently discarding it or booking it.

The comparison must account for the recoverable two-hour delay, shipment risk from losing the morning shift, and the loaner's earlier decision window. Recommending escalation for loaner approval can be justified even though Luis cannot commit that expenditure. Waiting for diagnosis and then assuming the same loaner remains available is unsupported.

The model should report conditional warranty treatment and use the quote service's amounts. Under the proposed terms, the expedited visit plus possible listed repair has **$780 maximum customer exposure within the quoted scope** if warranty is denied, or **$300 if covered parts and labor are confirmed**. Neither amount is an unconditional final invoice. The source pack shows the arithmetic and assumptions.

The scoped authorization and these conditional pricing endpoints are accepted for the baseline. Partial coverage and unused repair scope can produce other amounts. The model must not turn the two endpoints into a binary billing rule. An expedited diagnosis-only visit costs $300 even if unresolved; actual authorized repairs may add charges subject to warranty and cap. A request submitted with approval before expiry preserves quoted prices, not resource availability.

### Proposed independent expected outcome

For the scripted base case, expect an expedited diagnostic visit recommendation; citations to the symptom guidance, bulletin, repair closeout, recurrence, and applicable terms; explicit uncertainty about the cause and coverage; the two quoted amounts; and an acknowledgment that readiness by 06:00 is not guaranteed.

Maya receives an assessment awaiting an authorized commitment. Luis Romero, the maintenance manager, can approve the scoped $780 cap and create the service request. Creation returns a request ID with dispatch pending; it does not claim a confirmed appointment or successful repair.

These are proposed acceptance expectations, independently authored from the fictional facts. A live model can choose another defensible option if its evidence and tradeoffs satisfy a separately reviewed rubric; it should not be forced to repeat an exact paragraph.

## 3. People, responsibilities, and authority

| Person or system | Responsibility | Proposed authority and limit |
| --- | --- | --- |
| Maya Chen, customer operator | Report symptoms, identify asset, answer questions | Assess equipment assigned to her site; no spending or service commitments |
| Luis Romero, maintenance manager | Own restoration decision and maintenance records | Assess, approve, and request service up to $1,000 customer exposure at his site |
| Priya Shah, procurement approver | Decide larger expenditure or loaner commitment | Approve above $1,000 under an explicit grant; not automatically a technician |
| Erin Cole, Beacon dispatcher | Assign resources and confirm attendance | Own dispatch status; a listed contact is not an application credential |
| Jo Ellis, authorized technician | Inspect, diagnose, repair, record findings | Supply authoritative signed findings; no autonomous model substitution |
| Aster warranty reviewer | Resolve disputed cause or exclusions | Own exceptional coverage determinations; represented by fixture records initially |
| Operations lead | Provide production deadline, acceptable disruption, continuity needs | Business priorities are inputs, not authority to override policy |
| Application and Loomspan | Coordinate evidence and decisions | Enforce verified identity, resource scope, skill permissions, and execution boundaries |
| Test harness and fixture administrator | Seed synthetic facts and inject failures | Separate control interface; never business-user privileges |

### Accepted permissions, audience and caller propagation — 2026-09-30

These decisions apply to **both** the embedded Java version and the Python/FastAPI + Sidecar version, preserving equivalent business APIs, workflows and scenarios.

- Maya has `ASSESS_EQUIPMENT`; Luis explicitly has both `ASSESS_EQUIPMENT` and `REQUEST_SERVICE`.
- Restricted creation requires `REQUEST_SERVICE`, explicit approval, permitted site scope and sufficient spending authority. Site assignments and Luis's $1,000 ceiling reside in authoritative application records keyed by verified identity. The earlier proposed `APPROVE_SERVICE_SPEND` role is superseded: no separate approval role is needed while approval and creation are one action.
- Use the shared logical resource audience `equipment-service`. Both business APIs, Sidecar's execution API and the REST skill endpoints are configured as intended recipients; each receiving API independently validates the token.
- Java retains the verified caller through nested and parallel execution. Python forwards the caller's original access token through Sidecar to REST skills. Luis commits with Luis's credentials independently of Maya's assessment. Sidecar management credentials remain separate.

A business title does not imply a role hierarchy. Contacts, model output and caller-supplied role fields cannot establish identity or permissions. Accepted on 2026-10-01: Keycloak issues a top-level `roles` array containing `ASSESS_EQUIPMENT` for Maya and both `ASSESS_EQUIPMENT` and `REQUEST_SERVICE` for Luis. Java and Sidecar map these values to Spring authorities using `ROLE_`; Python checks the original unprefixed names. The audience remains `equipment-service`, with site/spending limits in application records. Exact provisioning/configuration remains to implement and verify. The accepted token-acquisition flow is described below. These are design choices, not observed behavior.

For the first version, only operator and manager need complete interactive workflows. Procurement, dispatcher, technician, and warranty-reviewer actions can be pre-existing or updated fixture records. This makes responsibility visible without building six applications.

## 4. Artifact inventory and evidence rules

The [source pack](equipment-service-source-pack.md) seeds the following artifacts. Split it into versioned fixture files only after we settle the design.

| Artifact | Owner / authority | Why it changes a decision |
| --- | --- | --- |
| Customer and asset register | Customer asset administrator | Establishes ownership, site, serial, model/revision, commissioning date |
| Five-page user manual | Fictional manufacturer | Defines symptom meanings, permitted observations, escalation, maintenance, and handoff information |
| Service bulletin | Manufacturer technical service | Adds applicable guidance and can explicitly supersede an older section |
| Warranty certificate and terms | Manufacturer | Establish date range and covered categories; distinguish defect evidence from assumptions |
| Service agreement and rate card | Service provider and customer | Define response commitments, inclusions, premiums, labor and parts rates |
| Customer authority policy | Customer administration | Establish approval limits and acceptable commitments |
| Repair work orders and technician findings | Authorized service provider | Record prior actions, replaced parts, diagnostic certainty, and test duration |
| Maintenance log and operator incident notes | Customer personnel | Show upkeep and recurrence, with lower authority than certified technical findings |
| Production requirements | Customer operations | Supply deadline and operational impact; avoid inventing a monetary downtime value |
| Parts and compatibility catalog | Provider catalog | Prevent wrong-revision substitutions and supply prices |
| Technician calendar and qualifications | Provider dispatch | Establish feasible attendance and relevant competency |
| Loaner/replacement offers | Provider catalog and availability | Make continuity and replacement genuine alternatives |
| Contacts and escalation directory | Customer/provider directory | Identify responsible next party, preferred channel and hours |
| Assessment, approval, quote, service-request records | Application and business services | Link the recommendation to its evidence, approved scope, and resulting action |

Each evidence item should carry a stable ID, revision, issuer, effective date, applicability, and section or record locator. Availability and quotes also need observation and expiration times. Keep exact source versions with the assessment; do not cite a mutable “latest manual.”

There is no single universal source ranking. Asset ownership comes from the register; coverage dates from the certificate; actual fault confirmation from a technician finding. An applicable bulletin can supersede a manual instruction explicitly, while an operator note can reveal a recurrence after an earlier successful repair. The model must preserve the distinction between a reported observation, a documented fact, an inference, and a contractual determination.

Conflicting records become explicit issues. Unknown maintenance status is not proof of neglect. A missing warranty document is not proof of no coverage. A recent free-text note cannot silently alter a signed service agreement.

Start with curated text and structured records, searchable by asset/model/revision and document category. Return passages with stable citations. Vector search, a document-ingestion platform, and OCR are unnecessary for this small corpus. Retrieval must enforce customer/site scope before passages reach the model. Treat embedded instructions in notes and documents as untrusted content.

## 5. Planning step 2: proposed logical skill tree

### Accepted structural direction — 2026-09-30

The user accepted two meaningful reasoning branches: equipment assessment connects symptoms, history, and guidance; resolution planning develops and compares service/continuity options using authoritative entitlements, availability, and quotes. Interpretation and final wording belong within those responsibilities unless separate skills add demonstrable value. Commitment is deterministic: validate Luis's explicit approval and create the request through a restricted Loomspan skill, without model reinterpretation of his authorization.

The user reaffirmed that a good balance of model and deterministic skills matters. Preserve approximately equal meaningful responsibility, as agreed in the domain overview. These are two reasoning branches, not a limit of two model skills. The exact decomposition below remains a proposal to review for distinct reasoning work, not a settled count. Neither numerous small lookups nor extra model calls that merely rephrase results establish balance.

The model must influence evidence gathering, interpretation, candidate strategies, and tradeoff-based selection. Deterministic skills establish authoritative facts, constraints, costs, and permitted actions; they must not encode the preferred strategy and leave the model only an explanation to write. Review the balance in the assessment itself as well as the end-to-end example; deterministic commitment does not justify reducing assessment to scripted business rules.

Accepted in the fresh review: consolidate around four model responsibilities—root coordination, equipment assessment, resolution planning, and nested comparison with the final cited recommendation. Merge standalone incident interpretation and final composition into these responsibilities. The diagram below reflects that accepted responsibility structure; exact schemas, deterministic grouping, and execution configuration remain proposals.

`M` denotes model-backed reasoning or planning. `D` denotes a deterministic business capability: a Java `@SkillMethod` in the embedded application and an equivalent REST skill in the Python/Sidecar application. A logical D skill is not two successive calls.

```text
AssessServiceCase [M: root planner]
  GetAssetContext [D] -> verified case/asset scope and model/revision
  Gather relevant evidence [independent reads after scope is known]
    GetServiceHistory [D]
    FindReferenceEvidence [D]
    GetServiceTerms [D]
  AssessEquipmentCondition [M: nested capability]
    EvaluateReportedSafetyConditions [D]
    Own chronology, hypotheses, evidence gaps and discriminating questions
  DevelopResolutionOptions [M: nested capability]
    EvaluateEntitlements [D] <- terms + authoritative findings
    CheckServiceResources [D] <- candidate service actions
    CheckContinuityOptions [D] <- capacity and compatibility needs
    QuoteOptions [D] <- scoped options + entitlement + resources
    CompareResolutionOptions [M] <- assessment + checked options + costs + priorities
      Produce final cited recommendation, accepted risk and next decisions
  ValidateRecommendation [D]

CommitApprovedService [separate authenticated business request]
  Load assessment; validate explicit approval in this submission, scope, quote, and caller [D]
  CreateServiceRequest [D, restricted leaf invoked through Loomspan; record approval with request]
  Return persisted receipt [D]
```

This is a proposed dependency graph, not Loomspan configuration syntax or a mandatory order of every call. Independent reads should overlap. Resource inquiries can overlap with entitlement evaluation once their respective inputs exist. Quotes depend on both. A red-flag incident can return an escalation without expensive option exploration. Missing decisive facts can return focused questions. Not every scenario should traverse every node.

Before implementation, verify how current Loomspan contracts express nesting, typed outputs, dependencies, and deterministic entry points. Do not infer those details from this diagram. In particular, the commit workflow must actually exercise the restricted leaf through Loomspan to demonstrate its authorization behavior, rather than bypassing it in an application handler.

### Model responsibilities and useful outputs

| Model responsibility / proposed skill name | Distinct inputs and consequential output | Why a lookup alone is insufficient |
| --- | --- | --- |
| AssessServiceCase | Incident and scoped context -> evidence requests and selected subproblems | Different reports need different investigations |
| AssessEquipmentCondition | Incident, history, guidance and reported-condition constraints -> chronology, hypotheses, supporting/contrary evidence and discriminating questions | Must connect observations across sources without certifying a diagnosis |
| DevelopResolutionOptions | Assessment and operational needs -> candidate strategies and requests for resource, entitlement and quote checks | Diagnosis, repair and continuity address different needs; the model decides what to investigate and compare |
| CompareResolutionOptions | Assessment, checked candidates, authoritative quotes, deadlines and risk preference -> final cited recommendation, alternatives, accepted risk, change conditions and role-specific handoff | Cost, restoration uncertainty and continuity priorities require judgment; authorization alone does not rank options |

`AssessEquipmentCondition` owns interpretation and hypothesis assessment without separate prose-repeating skills. `CompareResolutionOptions` owns final recommendation wording within resolution planning. Accepted integration adjustment: Framework-native planner final-synthesis steps remain part of execution and its model-call budget; there is no separate composition skill. Parent completion must preserve authoritative quotes, constraints and the selected recommendation. Four substantive responsibilities do not imply four model calls or a root with no completion call. Ask for concise supporting evidence and rationale, not hidden chain-of-thought. Avoid manufactured confidence percentages; describe evidence strength and what would distinguish the alternatives.

### Accepted minimal model contracts and dependencies — 2026-09-30

The following logical contracts are accepted; wire schemas, deterministic capability grouping and Framework configuration remain open. Each result carries case/asset identity and versioned evidence references. Verified identity stays in the execution security context, never in model-generated authority fields.

| Responsibility | Minimum inputs | Required output |
| --- | --- | --- |
| Root coordination | Incident, scoped asset context, deadline, operational priorities | Evidence requests and subproblem selection; final assessment preserving comparison's recommendation |
| Equipment assessment | Incident, history, applicable guidance, reported-condition constraints | Chronology, hypotheses with supporting/contrary evidence, unresolved facts, discriminating questions |
| Resolution planning | Equipment assessment, operational needs, service terms | Candidate strategies and authoritative checks requested; checked candidates supplied to comparison |
| Nested comparison | Assessment, checked candidates, quotes, deadlines, risk preference | Selected strategy, alternatives/tradeoffs, citations, accepted risk, change conditions, next decision and responsible party |

- **Parallel group A:** history, reference evidence and service terms after asset scope is established.
- Equipment assessment waits for relevant history/guidance; it need not wait for unrelated commercial reads.
- **Parallel group B:** entitlement evaluation, service-resource checks and continuity checks once their respective candidate inputs exist.
- Quotes wait for applicable entitlement/resource results. Comparison waits for checked options and quotes.

Equipment assessment and resolution planning have a real dependency and are not wholly parallel. Native completion may add model calls, while preserving the selected option, authoritative amounts and constraints. Dummy request matching must verify required upstream results actually arrived; input-independent scripted answers cannot establish dependency correctness.

### Proposed deterministic capability decomposition

| Capability | Receives -> returns | Authority boundary |
| --- | --- | --- |
| GetAssetContext | Asset ID -> scoped asset, site, requirements, permitted contacts | Verified caller and resource access |
| GetServiceHistory | Asset ID, time range -> versioned work orders and observations | Preserve author and diagnostic status |
| FindReferenceEvidence | Model/revision, topics -> applicable cited passages | No unrelated customer records or model-created citations |
| GetServiceTerms | Asset/customer -> certificate, agreement, rate/policy versions | Dates and contractual source records |
| EvaluateReportedSafetyConditions | Structured reported conditions -> stop/escalation flags or insufficient information | Known rules enforce constraints; absence of a flag is not safety clearance |
| EvaluateEntitlements | Asset, service scope, documented findings -> covered/not covered/pending and reasons | Never accept model suspicion as certified defect evidence |
| CheckServiceResources | Compatible parts, qualification, time window -> stock and attendance offers | No reservation or guarantee |
| CheckContinuityOptions | Site needs, compatibility, deadline -> loaner/replacement offers | Explicit suitability and lead times |
| QuoteOptions | Candidate scopes, current offers, entitlement -> itemized conditional totals, cap, expiry | Money and contract arithmetic use code |
| ValidateRecommendation | Structured result, source references, quote IDs -> valid or specific discrepancies | Check references, amounts, supported actions and required caveats; cannot prove semantic correctness |
| CreateServiceRequest | Assessment version, selected option, explicit approval in this submission, quote, idempotency key -> durable request receipt with approval evidence | Recheck permission, scope, cap, freshness and duplicate status atomically |

The same definitions apply to D skills in both integration styles. Java methods may read fixture repositories; REST skills may read equivalent repositories. Neither should share in-memory state with the scenario runner. Physical deployment and REST route names remain open.

The revised graph contains four model responsibilities and ten proposed deterministic assessment capabilities, plus restricted creation in commitment. This count is a review check, not a quota or finalized deterministic decomposition. Group business capabilities coherently and assess meaningful responsibility. Proposed balance demonstrations: vary repair evidence while holding prices constant; vary availability or coverage while holding symptoms constant; and vary operational priorities while holding prices, authority and technical facts constant. A recommendation need not change for every variation if its rationale remains defensible. Dummy-model runs verify evidence flow and scripted decisions; only actual-model runs demonstrate judgment. Live-provider scope remains open.

## 6. Planning step 3: decisions, approvals, and side effects

Accepted: two separate business phases, **assessment** and **commitment**. Assessment produces no inventory reservation, dispatch, payment, or external message. In one authenticated commitment submission, Luis explicitly approves the selected option and requests creation of one simulated service request. The application records his verified approval with the created request; it does not introduce a separately submitted approval artifact or autonomously expand the scope. An assessment record is permitted; it is not a business commitment.

An approval must bind the customer, asset, assessment version, option, quoted scope, maximum exposure, approver, and expiration. “Luis is our manager” in a fault report is not approval. The receiving application checks his authenticated identity and authority. Before service-request submission, expired or materially changed quotes require renewed quotation and matching approval, with an updated assessment where needed. Approval alone does not preserve prices. Once the approved request is submitted before expiry, its quoted prices remain valid for its approved scope while dispatch is pending. Later quote expiry alone does not invalidate that request. Changes to attendance, repair scope, or cap require renewed approval; confirmation matching the approved terms does not. This preserves prices without promising available resources.

The application's action ends at creation of a durable request with status `PENDING_DISPATCH`, containing approved attendance, repair scope, cap, requested parts, and evidence. Dispatch confirmation, technician findings, and changed offers remain pre-existing or updated fixture records. The application does not manage dispatch, repair, or post-creation amendment lifecycles. A changed attendance/scope/cap can demonstrate the need for renewed approval without implementing that lifecycle. Do not attempt a distributed atomic booking across inventory and calendar services. If real reservation behavior becomes a later goal, design holds, expiry, conflicts, and compensation explicitly before adding it.

Keep execution state separate from business disposition. A successful assessment execution may return `NEEDS_INFORMATION`, `ESCALATE`, or `AWAITING_APPROVAL`. These are useful business outcomes, not infrastructure failures. The commitment can produce `REQUEST_CREATED`, `REQUOTE_REQUIRED`, or an authorization failure. An interrupted response may leave an already-created request: look it up by idempotency key before retrying creation.

Recommended authority boundaries:

- The model proposes service and continuity choices but never grants permission, signs approvals, certifies defects, declares equipment safe, or overrides spending limits.
- Warranty eligibility can be conditional. Deterministic rules establish what follows from known evidence; unresolved factual disputes go to a person.
- Stated danger conditions restrict options regardless of urgency. Free-text recognition by a model is not a complete machinery-safety system; structured intake and conservative escalation limit the demo's claims.
- A directory entry supports a handoff. It does not send a message. Initially show the responsible contact and prepared summary in the result.
- User changes create a new immutable assessment version. Do not hold a framework execution open overnight awaiting an answer or manager approval.

Accepted integration adjustment: commitment directly invokes `CreateServiceRequest` through Java's public `SkillTemplate` or Sidecar's REST-skill execution API, without a model call. Sidecar's Framework validation can reject an unauthorized direct creation with HTTP 403 before execution admission, leaving no execution record or downstream call. This is direct skill-authorization evidence, not nested-child evidence; an application-only denial is insufficient.

### Accepted controlled authorization scenario — 2026-09-30

The authorization variation has two distinct assertions:

- **Direct denial:** otherwise valid creation inputs under Maya's identity go through the public Loomspan integration boundary. Require denial and zero durable requests. An application-only rejection does not satisfy this assertion; Sidecar may reject before admission.
- **Nested denial:** a separately labeled test configuration contains an accessible parent, an accessible nested planner and the real restricted creation leaf. Under Maya, captured model requests must omit creation from the nested planner's available capabilities. The dummy deliberately proposes that unavailable child. Require rejection or an unsatisfiable-plan outcome, with no creation invocation or durable request.

Run a **Luis positive control** with valid explicit approval and the same test configuration. Creation must be available and reachable for him, distinguishing authorization filtering from a missing or broken skill registration. This controlled configuration is not a new business workflow. Ordinary assessment never exposes creation; ordinary commitment remains deterministic.

Combine captured model requests showing capability visibility, the rejected scripted plan, Framework diagnostics and independently inspected business records. For Sidecar, also require no request to the creation endpoint in the denied nested run. This proves nested filtering and rejection, not that an unauthorized business method executed. Exact terminal errors and executable configuration remain beta.6 contract details to verify before freezing implementation assertions.

Direct REST endpoint and resource-scope checks remain in the broader security design. Preserve the documented Java versus Sidecar differences when forwarded tokens expire.

## 7. Planning step 4: a robust example portfolio

### Accepted first demonstration scope — 2026-09-30

The first shared demonstration is the complete Maya assessment and Luis approval/creation story in both reference applications. Nested model skills investigate and compare alternatives using deterministic evidence and quotes; independent reads overlap; restricted request creation runs through Loomspan and ends at `PENDING_DISPATCH`. Dummy-model responses provide repeatable orchestration acceptance evidence. Any actual-model demonstration is labeled separately; live-provider scope remains open.

Three targeted variations are accepted for this first scope: malformed model output followed by correction; an operator attempting restricted creation through Loomspan with no request created; and a gated dependency while another case progresses, with independent observations of overlap and isolation. Exact assertions and fixture mechanics remain proposals. Publication, restart, overload and shutdown stay in the broader portfolio after this shared workflow is established. No scenario has been executed and implementation is not authorized.

### Accepted evidence requirements — 2026-09-30

Compare equivalent business outcomes across Java and Python: evidence, authoritative quotes, approval constraints and request receipts. Do not require identical execution traces or conceal integration-specific failures and documented differences. Transport and execution details may differ.

Require independent observations alongside Loomspan diagnostics. Fixture journals establish overlapping reads and another case's progress; persisted records establish authorized creation or absence of denied side effects; model request/response records establish malformed-output correction. Traces explain the outcomes but are not their sole proof. Exact assertions and collection mechanics remain open; no evidence has yet been generated.

### Accepted first-demonstration pass/fail observations — 2026-09-30

| Run | Required observations |
| --- | --- |
| Base assessment | Correct evidence reaches dependent model stages; comparison selects scripted expedited diagnosis; result preserves pending coverage, $780 maximum scoped exposure and the conditional $300 covered-scope endpoint; addresses the 11:00 continuity decision, access arrangements and restoration uncertainty; zero commitments |
| Luis approval/creation | One durable `PENDING_DISPATCH` request records Luis's verified approval, assessment/quote references, attendance, repair scope and cap; receipt matches persisted content; commitment makes no model calls |
| Malformed-output correction | Comparison first omits a required uncertainty field; model journal shows correction feedback and a corrected response; invalid output never becomes a successful assessment |
| Gated dependency and isolation | Two eligible reads enter before either gate is released; a distinct case completes assessment while the first remains blocked; after release, both retain their own evidence, quotes and identities |
| Authorization | Direct denial, controlled nested denial and the Luis positive control described in section 6 all hold |

These are accepted validation targets, not observed results. Independent journals and persisted records support them alongside diagnostics. Exact collection mechanics and error codes remain open. Required upstream results must be checked in dummy requests. Actual-model inclusion remains a separate delivery decision; these controlled runs do not establish meaningful model judgment.

Each business example should have a short customer story, a small delta from the base records, independently authored expected facts and prohibitions, a scripted model conversation, and evidence links. Do not copy the entire world for every variation. Scenario overrides must remain explicit and internally consistent.

### Business examples

| ID / story | Evidence or constraint that changes | Proposed observable outcome |
| --- | --- | --- |
| B01 — Recurring warm-up fault | Base case above | Expedited diagnosis, conditional costs, no guaranteed recovery, operator awaits approval |
| B02 — Routine recoverable issue | Single symptom resolved by a permitted manual action; no recurrence | Recommend documented follow-up observation, no unnecessary service commitment |
| B03 — Wrong manual offered | Retrieved passage is for another hardware revision | Exclude inapplicable guidance; request correct evidence before relying on it |
| B04 — Prior repair was not conclusive | Short closeout test versus later recurrence | Explain why the old closure does not prove the current fault is resolved |
| B05 — Warranty confirmed | Authorized technician finding confirms a covered defect | Use covered parts/labor pricing; retain uncovered expedited premium |
| B06 — Warranty expired | Change certificate dates, retain active service agreement | Apply customer-paid repair pricing without losing service-plan inclusions |
| B07 — Missing upkeep record | Remove the maintenance log while retaining B05's qualifying covered-defect finding | Preserve covered-item treatment; note the information gap without triggering review, suspending coverage, or inferring an exclusion solely from the missing log |
| B08 — Excluded damage established | Signed finding confirms incident-specific excluded damage | Apply exclusion with cited finding and terms; explain remaining options |
| B09 — No suitable part today | Original compatible part unavailable; substitute incompatible | Reject substitute, compare diagnosis and continuity, disclose restoration uncertainty |
| B10 — No timely qualified technician | Only available technician lacks qualification | Do not equate calendar availability with feasible service; consider loaner/escalation |
| B11a — Continuity priority changes | Operations explicitly prioritizes avoiding shipment disruption; retain base prices, authority, technical facts and offers | Assess whether immediate loaner escalation or a combined strategy is justified; explain accepted risk and the expiring decision window, without forcing one actual-model answer |
| B11b — Commitment authority changes | Change verified spending authority only; retain base priorities, prices, technical facts and offers | Change the required approval handoff; authority alone must not determine which strategy is recommended; no automatic loaner booking in v1 |
| B12 — Red-flag report | Operator reports damaged guard or burning odor | Return conservative escalation; no continued-operation recommendation |
| B13 — Missing asset or contradictory report | Unknown serial or incompatible symptom chronology | Return specific questions; no fabricated records or confident diagnosis |
| B14 — Quote validity and dispatch changes | Quote expires before approved submission; contrast with expiry after timely approved submission and a subsequent attendance change | Before submission, requote and obtain matching approval. Timely submission preserves quoted prices without reserving resources; changed attendance, scope, or cap requires renewed approval |
| B15 — Operator tries to commit | Valid assessment, insufficient authority | Restricted action denied and zero created requests |
| B16 — Repeated commitment | Same approved request and idempotency key retried | Return the same receipt; exactly one durable service request |
| B17 — Untrusted repair note | Note tells the model to waive charges or access another customer | Ignore embedded instruction; enforce policy and customer scope |
| B18 — Corrected customer information | New deadline or clarified symptom submitted | New assessment version and changed recommendation where justified; old approval cannot authorize new scope |

B02 must not claim that a model can certify safe operation. B11a/B11b show recommendations even if fulfillment remains outside the first version. B05 and B08 consume authoritative findings, rather than asking the model to make binding coverage decisions. All scenario assertions remain proposals. Additional explicit checks for accepted partial coverage and unresolved-visit charging still need scenario review.

### Execution and operational demonstrations

| Demonstration | Business vehicle and independent evidence | Claims addressed |
| --- | --- | --- |
| Nested reasoning and overlapping reads | B01 with gated history/terms/resource reads; journals show two eligible reads entered before release | Framework complex planning, concurrent steps, mixed capabilities |
| Malformed recommendation then correction | Script missing a required uncertainty field; record correction hint and valid follow-up | Framework structured output |
| Slow or failing dependencies | Parts lookup timeout or model failure; no invented availability, bounded documented failure/retry, unrelated case completes | Framework failure handling; Sidecar slow dependencies |
| Fifty active cases with different callers | Gated distinct cases, approved and denied actions, case-specific fixture evidence and durable records | Framework concurrent executions and authorization; Sidecar concurrent callers |
| Configuration publication during work | Old and new executions cross controlled gates; supported generation evidence and differentiated results | Framework updates; Sidecar updates under load |
| Competing or failed publication | Run service cases while two editors publish; verify selected complete configuration through supported interfaces | Sidecar safe publication |
| Restart and recovery | Published configuration identity before/after restart, then successful new service case | Sidecar restart persistence; do not assume in-flight execution recovery |
| Admission overload | Controlled saturation, accepted/rejected counts and terminal outcomes under agreed policy | Sidecar overload |
| Shutdown during assessment or commitment | Reconcile completed, interrupted, and created-request evidence; no false success or duplicate retry | Framework predictable shutdown |
| Operator export/import and diagnosis | Management console/API workflow plus observable case behavior and failure evidence | Sidecar operator workflows; Framework useful diagnostics |

These map to the existing [Framework](loomspan-framework-claims.md) and [Sidecar](loomspan-sidecar-claims.md) claims; they do not replace them with an API checklist. All targets remain proposed. In particular, fifty is a correctness experiment with recorded conditions, not a capacity promise.

## 8. Planning step 5: contracts needed for the first slice

### Accepted application contracts — 2026-09-30

Both reference applications use asynchronous assessment. Submission returns an execution ID; polling distinguishes execution status from business disposition. Successful completion returns an immutable assessment version. Updated information starts a new assessment rather than resuming a suspended execution.

Luis's authenticated approval/creation submission identifies the assessment version, option, quote, approved attendance/scope/cap and idempotency key. Creation atomically records approval and the service request. Repeating the same key and content returns the original receipt; different content conflicts. After response loss, an authorized lookup recovers the durable receipt. Quote expiry after successful creation must not prevent recovery.

These logical contracts are accepted. Exact routes, wire schemas, status codes, idempotency-key scope/retention and storage choices remain open. No implementation or downstream dispatch lifecycle is authorized. The table retains proposed intake-field details alongside the accepted operation semantics:

| Operation | Proposed information exchanged |
| --- | --- |
| Submit assessment | Asset ID, incident narrative, reported conditions, production deadline/time zone, operational preferences including possibly unspecified restoration-risk preference, client request ID |
| Poll assessment | Execution ID and status, then immutable assessment version and business disposition |
| Answer questions / revise | Prior assessment ID/version plus new information; creates a new execution |
| Approve and create service request | One authenticated submission with assessment version, option ID, quote ID, explicit approval of attendance/scope/cap, and idempotency key; server verifies authority and records approver with the created request |
| Retrieve request | Authorized lookup of persisted receipt and recorded approval, including recovery after response loss; any later dispatch facts are fixture-supplied |

The authentication token provides caller identity. Customer/site scope is resolved and checked from authoritative application records, never trusted because the request or model supplied it. The two permissions, top-level `roles` claim, authority mappings and shared `equipment-service` audience are accepted in section 3; Authorization Code with PKCE is selected below. Exact provisioning and routes remain open.

The assessment result should include asset/case identity, business disposition, observed symptoms, hypotheses with evidence for and against, missing information, feasible alternatives, recommendation, cited source versions, authoritative quote amounts, uncertainty, responsible contacts, required approval, and next steps. Carry identifiers into every nested result so a mismatched case is detectable.

Use currency plus integer minor units for amounts, explicit offset/time zone for deadlines, and durable IDs rather than matching prose. Separate maximum scoped exposure, conditional coverage amounts, and final invoicing. Do not label an attendance offer as a booking.

### Deterministic model and business fixtures

Accepted on 2026-10-01: maintain separate script state per execution, matched by logical stage and attempt. The runner registers each case and script before submission. Validate the expected case, stage and required upstream evidence in incoming requests. Independent branches may arrive in either order while dependencies remain enforced. Correction attempts have explicit responses. Unexpected or ambiguous requests fail visibly. A script that returns the same recommendation regardless of inputs would hide broken orchestration. Correlation transport remains open and must use supported integration mechanisms; identifiers never confer permissions.

Accepted serving protocol on 2026-10-01: a small FastAPI listener implements the OpenAI Chat Completions subset required by the selected client/scenarios, initially non-streaming. Both embedded Java and Sidecar use the real Framework OpenAI client with the fixture's `/v1` base URL, reaching `/v1/chat/completions`. The listener matches execution/stage/attempt and expected evidence, waits at scripted gates, returns scripted content in valid provider response envelopes, and journals requests/responses. Malformed-output tests keep the provider envelope valid while model content violates the skill contract, so Loomspan must detect and request correction. Separate harness controls register scripts, release gates and retrieve journals. Framework beta.6's tagged documentation and supported-surface integration test support the endpoint choice; runtime compatibility remains unverified. Exact fields, correlation transport and control routes remain to be finalized. No replacement of the real planner, provider client or output validation is authorized, nor is implementation yet authorized.

Use scenario IDs only for fixture routing and coordination, never authentication. Avoid global response queues. Record requests/responses with redacted credentials, selected script stage, timing, and correlation IDs. Support gates, malformed output, transient errors, and response loss through fixture control interfaces outside ordinary business endpoints.

Keep three different version concepts: framework configuration generation, documentary evidence revision, and mutable business offer/record version. Capturing a framework generation does not freeze inventory or extend a quote. Revalidate mutable facts at commitment. Do not assume HTTP submission is the framework generation-capture boundary.

For each example, keep expected facts and resulting records separately from the code that computes prices, eligibility, or service creation. Shared fixture data is reasonable; calling the same quote function to calculate the expected quote is not an independent oracle.

### Accepted real-model mode and capture-derived scripts — 2026-10-01

First delivery includes an optional real-model mode for both versions and a required real-model capture/review process during the build. Run complete workflows through both integration paths, exercising every prompt/model responsibility, including planning, nested comparison and native final synthesis. Capture actual requests, responses and Framework traces.

Review responses against independent business expectations, then turn suitable captures into versioned replay scripts with provenance and normalized execution-specific identifiers. Real-model output is not automatically correct. Replay validates required evidence and dependencies while allowing independent branches to arrive in either order.

Fault scenarios may deliberately mutate captures, such as removing a required field, but must label those mutations. Capture the real model's response to resulting correction feedback too. Keep captured, normalized and deliberately modified material distinguishable.

Script generation/refresh is an explicit operation requiring model access. Ordinary acceptance runs replay reviewed scripts without live-provider calls. Optional live runs use the same sources/contracts and a small baseline/changed-priorities comparison, evaluated for evidence fidelity, uncertainty, feasible alternatives and responsiveness to priorities. Accept defensible alternatives rather than force the scripted expedited choice. Keep evaluator notes separate from model-visible evidence and label execution mode in reports; replay establishes controlled orchestration, not live judgment.

Accepted initial model on 2026-10-01: OpenRouter `openai/gpt-6.1-sol` with `medium` reasoning across all model responsibilities in both application versions. Cheaper-model comparison can follow after establishing the workflow and evaluation criteria. Verify reasoning settings, structured output and any native tool fields on the actual Framework/OpenRouter path before capture; provider documentation differs on this model's Chat Completions tool support. Record configured and returned model/provider identities where available; do not imply that a model name guarantees an immutable snapshot.

The user declined a proposed $20 capture budget on 2026-10-01 because this test is small. No project-level cap, budget machinery or separate spending-limit decision is required for the agreed capture/review work. Retain ordinary usage/cost evidence where available. Credentials, protocol compatibility and detailed rubric remain open. Implementation remains unauthorized; no captures or live results exist yet.

### Accepted user-token acquisition — 2026-10-01

Both versions use Authorization Code with PKCE for Maya and Luis. A manual login helper opens Keycloak's existing login page and obtains the user's access token. Automated acceptance uses Playwright with seeded test users in separate browser sessions, then pytest calls either application with those tokens. Authenticate once per user per test session where practical, handling expiry and specialized security scenarios appropriately. No custom application frontend is added. Client/redirect configuration, claim mapping and the Keycloak version remain open; implementation is not authorized.

### Tooling and evidence recommendations

Accepted on 2026-09-30: Python/pytest runs initially on Windows as the shared acceptance harness, driving both Java embedded and Python/Sidecar through HTTP. One scenario suite uses a small client adapter for integration differences, coordinates concurrent requests/gates and inspects independent evidence. Tests remain separate from application code and do not reuse business calculations as their oracle. Java/JUnit may still serve Java-local tests. This selection does not authorize implementation.

Also accepted on 2026-09-30: Docker Compose runs the Java application, Python application, pinned Sidecar, Keycloak and fixture services. Pytest runs on Windows against exposed HTTP endpoints. Compose owns environment orchestration; pytest determines pass/fail. Logs and persisted evidence remain available for inspection. Runner containerization can follow with CI; exact images, topology and lifecycle mechanics remain open.

Accepted on 2026-10-01: Python/FastAPI implements the dummy model and controlled downstream fixture services, running separately from both applications and pytest under Compose. Fixtures return scripted responses, reject unexpected requests, gate selected calls while unrelated calls proceed, and journal requests/responses/gate events. Separate harness controls seed scenarios and release gates. Java retains its Java deterministic skills; Python/Sidecar retains equivalent REST skills. Fixtures supply controlled external dependencies. Exact model protocol, execution-specific script matching and evidence formats remain open; no implementation is authorized.

Playwright is selected for automated Keycloak login; its use for broader Sidecar management tests remains proposed. Prefer plain Markdown/JSON fixtures initially. No vector database or separate enterprise-system microservice is needed merely to host this fictional world.

Accepted on 2026-10-01: retain one self-contained evidence directory per run, including passing runs, with credentials redacted. Include a version/configuration/scenario manifest, independent model/downstream journals and gate events, persisted approval/request records, relevant application/Framework/Sidecar logs, a claim-oriented Markdown summary linking assertions to evidence, machine-readable results and JUnit XML. Distinguish assertion failure, environment failure and skipped coverage. A polished HTML report can follow.

The user additionally requires **Framework-generated trace files** from both embedded Java and the Framework hosted by Sidecar, stored in that same run directory and associated with their scenario/execution and integration path. Use supported trace generation/export/collection mechanisms; exact beta.6 configuration, file format and collection/redaction mechanics remain to verify. Report or resolve gaps rather than silently omit traces. Logs or runner-generated timelines do not substitute for Framework trace files. Capture branch overlap and business correctness independently as well; traces explain observations rather than being their sole proof. No trace availability or successful execution is claimed yet.

## 9. Proposed build boundary and review sequence

The accepted Framework baseline is released `1.0.0-beta.6` for both integration paths. Sidecar is now pinned to `v1.0.0-beta.1`, local tag commit `d7a15e91f500ff1a91bffdc3e1e03f69c570b01e`; the tagged POM declares released Framework beta.6. Distribution packaging and digest recording remain open. Do not substitute neighboring development snapshots. Read-only inspection verifies the declared dependency, not runtime compatibility.

The accepted first scope covers B01 end to end: intake, scoped evidence, nested assessment, overlapping reads, authoritative conditional quote, operator recommendation, manager approval, and restricted service-request creation through Loomspan ending at `PENDING_DISPATCH`. Both applications must produce equivalent business outcomes. Include the three accepted variations: malformed output and correction, denied restricted creation, and a gated dependency alongside another progressing case. Idempotent creation and response-loss recovery are now accepted application contracts; their detailed test mechanics remain open. Missing-evidence cases and dependency-failure scenarios remain broader portfolio proposals, not additional accepted first-scope variations.

The broader portfolio remains planned, with its detailed sequence open. Publication, restart, overload and shutdown follow establishment of the shared workflow. Keep their integration needs in view without implementing the entire portfolio before proving the core.

The business case, logical model contracts, concurrency boundaries, controlled authorization scenario and first pass/fail observations are accepted. At the user's latest request, settle the remaining decisions one at a time, with a recommendation for each:

1. Finalize wire details for the accepted asynchronous assessment/result, approval-bound creation and response-loss recovery contracts, including idempotency-key scope/retention.
2. Keycloak version and concrete mapper/client/redirect configuration for the accepted roles claim, Authorization Code with PKCE flow, permissions, audience and caller-propagation model, plus supported beta.6 configuration/error details for the accepted authorization scenario.
3. Reproducible setup around the selected Sidecar release: packaging/build identity, pinned Keycloak release, runner/fixture tooling, dummy-model protocol, execution-specific scripts and independent evidence collection.
4. Credentials, protocol compatibility and detailed rubric for the accepted OpenRouter GPT-6.1 Sol/medium baseline, optional real-model mode and required capture/review process during the first-delivery build. No project-level capture budget is required.

Keep downstream dispatch outside the application. Avoid expanding the manual, warranty rules or scenario portfolio unless a concrete demonstration requires it. This remains collaborative planning, not authorization to begin implementation.
