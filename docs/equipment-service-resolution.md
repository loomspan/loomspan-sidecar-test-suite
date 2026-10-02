# Equipment service resolution: reference workflow

Current implementation note (2026-10-01): implementation is authorized and underway on Framework beta.7 / Sidecar beta.2. This document retains domain/design history; any older release, authorization, “no captures,” or “not yet verified” statements describe that earlier planning stage. Apply the latest accepted decisions in [project agreement](project-agreement.md), resume from [implementation handoff](implementation-handoff.md), and use [implementation status](implementation-status.md) for observed results and remaining work.

Selected on 2026-09-28. This document records the agreed business direction and the details motivating it. It is planning documentation, not an implemented workflow or evidence of verified capabilities. The exact skill tree, business rules, API, and acceptance scenarios remain open.

On 2026-09-29, the user requested a substantial first planning draft with a realistic fictional manual, warranty, contracts, contacts, repair history, responsibilities, boundaries, and proposed model/Java/REST skills. Continue with the [working design](equipment-service-design-draft.md) and its [fictional source pack](equipment-service-source-pack.md). They cover the five planning topics: the concrete case, logical skill tree, action/authorization boundary, demonstration scenarios, and contracts required for the first slice. Their specific proposals are not yet finalized.

On 2026-09-30, the user accepted the first business-case review: retain the carton sealer and recurring fault, separate evaluator interpretations from source evidence, make a short production delay recoverable but a lost morning shift consequential, and recognize that the loaner offer expires before diagnosis. Luis may authorize the specified expedited diagnosis and conditional repairs up to $780 pending coverage, with findings supporting justified work and deterministic item-level coverage. Routine qualifying technician findings support warranty treatment; disputed or incomplete findings need review. The linked draft 0.2 documents and agreement distinguish these and subsequent accepted decisions from the remaining detailed contracts and implementation proposals.

## Business problem and intended outcome

Both reference applications will help a business decide how to address malfunctioning equipment. The domain is outside the travel industry and gives model reasoning and deterministic business operations roughly equal importance.

An illustrative request is:

> Our packaging machine intermittently stops after warming up. We cleaned the sensor, but it happened again. We have an important production run tomorrow. What should we do?

The intended outcome is an evidence-backed service recommendation and, when authorized, creation of the corresponding service request. The recommendation should explain relevant tradeoffs, uncertainty, and unresolved questions. The recurring carton-sealer case is accepted; its complete fixture details remain under review, without a commitment to support many equipment categories.

Subsequent reviews on 2026-09-30 settled the identified service-term gaps and the action boundary: assessment is separate from one authenticated approval-and-creation submission ending at `PENDING_DISPATCH`. Dispatch, findings, and changed offers remain fixture records. The fresh review also accepted explicit restoration-risk preference, which may be unspecified, without invented probabilities or downtime values. Recommendations must address the expiring continuity choice, the risk accepted, and what would change the advice. Expedited service remains the scripted baseline; actual-model review can accept justified alternatives.

The application remains a focused REST-only reference microservice. It should be understandable through a request and its result without becoming a complete maintenance-management product.

## Balance of model and deterministic work

The desired approximately 50/50 balance concerns meaningful responsibility. It is not an exact quota of skill definitions, model calls, tokens, or execution time. Neither half should be sufficient on its own.

| Model-backed responsibility | Deterministic SkillMethod / equivalent REST responsibility |
| --- | --- |
| Interpret the operator's description and identify missing information | Retrieve equipment details and service history |
| Assess plausible causes using symptoms, history, and maintenance guidance | Retrieve relevant troubleshooting documents |
| Develop useful alternatives: further diagnosis, repair, or replacement | Check parts availability, technician slots, and replacement stock |
| Weigh disruption, uncertainty, and operational needs | Calculate prices, warranty coverage, and contractual eligibility |
| Recommend an option, explain its tradeoffs, and identify unresolved questions | Validate and create an authorized service request |

These are responsibility boundaries for designing the workflow, not a finalized one-row-per-skill inventory. Java will expose deterministic operations through `@SkillMethod`; Python/FastAPI will expose equivalent REST skills used by Sidecar. Both applications should implement the same logical business behavior.

The model's assessment must affect the workflow or recommendation. For example, an intermittent fault after warming up may call for a different investigation than an immediate startup failure. Available parts may make repair attractive, while uncertainty about the cause may favor a technician assessment first. The model connects evidence and weighs alternatives rather than only formatting or summarizing records.

Authoritative facts, calculations, eligibility rules, and permission checks belong to deterministic operations. Model-generated recommendations or arguments do not grant authority to create a service request.

## Natural structure for the next skill-tree discussion

Equipment assessment and resolution planning provide useful candidates for nested model-backed skills. Independent information gathering can overlap, while later decisions and operations depend on earlier findings. For example, equipment history and maintenance guidance can inform an assessment; resource availability and calculated costs can inform the choice among feasible responses.

The fresh review accepted four model responsibilities within this direction: root evidence/subproblem coordination; equipment assessment covering chronology, hypotheses, and discriminating questions; resolution planning that develops strategies and requests authoritative checks; and nested comparison producing the final cited recommendation. Separate interpretation and final-composition skills are merged into these responsibilities. Exact inputs, outputs, deterministic groupings, and execution configuration remain open. Deterministic operations provide constraints without selecting the recommendation.

## Relationship to customer-facing claims

The authoritative starting lists remain the [Framework claims](loomspan-framework-claims.md) and [Sidecar claims](loomspan-sidecar-claims.md). This domain offers proposed ways to demonstrate them:

- Nested assessment and resolution planning can demonstrate complex planning and mixed model/deterministic capabilities.
- Independent information gathering can demonstrate concurrent steps, with subsequent decisions respecting dependencies.
- A structured recommendation can demonstrate output contracts and correction of malformed model responses.
- A restricted service-request operation can demonstrate authorization below an otherwise accessible workflow entry point.
- Slow or failing model and business dependencies can demonstrate failure handling and useful diagnostics.
- Distinct service cases and callers can supply meaningful business data for isolation and configuration-publication scenarios under concurrent execution.

These are validation opportunities, not selected acceptance assertions or observed results. Sidecar management, persistence, overload, and shutdown behavior will still need their own scenario design around the workflow.

For the subsequently accepted first demonstration, compare equivalent business evidence, quotes, approval constraints and receipts across the applications, without requiring identical traces. Independent fixture journals, persisted business records and model request/response records must support the relevant outcomes alongside Loomspan diagnostics. Exact assertions remain open; these evidence requirements are not observed results.

## Deterministic verification and model quality

The agreed dummy LLM will supply controlled assessments, plans, recommendations, and error responses through the real framework execution path. Scenarios should verify that those responses lead to the expected dependency ordering, deterministic operations, permissions, and business outcomes using independently specified expectations.

This establishes orchestration and integration behavior under controlled model responses. It does not establish an actual model's diagnostic accuracy or business judgment. Optional live-provider demonstrations remain an open scope decision.

## Decisions still to make

The first shared demonstration scope is accepted: Maya's assessment and Luis's authenticated approval/creation through Loomspan, ending at `PENDING_DISPATCH`, in both applications. It includes malformed-output correction, denied restricted creation, and a gated dependency while another case progresses. These target orchestration, integration, authorization, overlap and isolation using dummy-model responses and independent observations. Actual-model evidence remains separate. Exact assertions and implementation contracts are still open; no implementation is authorized.

The selected Framework baseline is released `1.0.0-beta.6` for both paths; the exact Sidecar artifact remains open. Commitment directly invokes the restricted deterministic skill without a model. Direct denial and a separate controlled nested-authorization assertion supply distinct evidence within the authorization variation. The four model responsibilities allow native planner final-synthesis calls, while comparison owns the recommendation and parent completion preserves its authoritative facts and selection. See the agreement for these accepted integration adjustments.

- Refine the accepted recurring carton-sealer case's remaining evidence and independently specified expectations.
- Define contracts for the accepted model responsibilities and coherent deterministic capabilities.
- Decide how missing information, uncertain assessments, and unavailable options are represented and handled.
- Refine enforcement and request details within the accepted separate assessment and authenticated approval/creation boundary.
- Specify request/result contracts, business rules, fixtures, and the first claims to validate.

Continue collaborative planning before implementation. No detailed skill tree or acceptance scenario is approved merely by appearing as a possibility here.
