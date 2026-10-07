# Working foundation

Phases 1 and 2 are complete. The current equipment-service example is the retained
reference; [Phase 2 summary](phase2-summary.md) describes its validation and limits.

## Applications and infrastructure

- Java/Spring Boot embeds Loomspan Framework and deterministic SkillMethods.
- Python/FastAPI implements equivalent business operations and calls Loomspan Sidecar.
- Keycloak supplies separate Maya and Luis identities through Authorization Code with PKCE.
- The fixture service supplies versioned fictional source records and the controlled
  provider boundary. Historical responses are not needed for operation.
- SQLite persists assessments, issued quotes and service-request receipts. Sidecar
  retains its own operational configuration store separately.

Public hosts expose `/assessments`, `/service-requests`, `/service-requests/by-key/{key}`,
`/v1/skills/{skill}/executions`, `/v1/executions/{id}` and `/health`. Java listens on
18081; Python on 18082; Sidecar on 18083. See [runtime](runtime.md) for startup and ports.

## Responsibilities and handoffs

| Skill | Responsibility | Model |
| --- | --- | --- |
| resolveEquipment | Gather evidence and coordinate the whole assessment | Luna/medium |
| assessEquipment | Reconstruct chronology, assess hypotheses and identify investigation needs | Sol/medium |
| planResolution | Obtain offers/quotes and coordinate feasibility and comparison | Luna/medium |
| assessExpeditedFeasibility | Assess expedited service timing, cost and conditions | Sol/medium |
| assessStandardFeasibility | Assess standard service timing, cost and conditions | Sol/medium |
| assessLoanerFeasibility | Assess temporary capacity, setup and external procurement | Sol/medium |
| assessReplacementFeasibility | Assess permanent replacement and external procurement | Sol/medium |
| compareOptions | Select a portfolio and review all materially published findings | Sol/medium |

Deterministic tools retrieve assetContext, serviceHistory, referenceEvidence, serviceTerms,
entitlements, serviceResources and continuityOptions. quoteOptions reads authoritative
inputs and assembles complete offers with original details, source identity/revision,
expiry, reservation state, monetary units and exact service quotes. Quotes publish
rate provenance, repair-labor allowance, identified part amounts and attendance premium.

Framework bindings supply evidence and preserve accepted findings. Assessors receive
one complete offer, applicable terms and operating needs. Service findings include
charging, scope-change and coverage-review conditions plus source-linked owners.
Comparison receives original evidence, quotes and all feasibility findings. It chooses
pursuedOptions and a primary selectedOption, explains risk and the next decision, and
records supported corrections or genuine unresolved conflicts in reviewConcerns.
Original findings remain published unchanged; superseding interpretations must be explicit.
Equipment hypotheses use self-contained prose with support, contrary evidence and unknowns.

The generator and shared contract source are `scripts/author_workflow.py` and
`scripts/workflow_contracts.json`. Both hosts share `config/skills`; Sidecar's deterministic
REST declarations and routes are separate. Regeneration is deliberate, not a startup
prerequisite. The `reasoning` alias selects Sol; `coordination` selects Luna.

## Business boundaries

The fictional revision-B P240 has recurring warm-up E17 after a sensor replacement and
cleaning. A prior 20-minute test is shorter than the reported 35-50-minute onset; its
initial conditions remain unknown. Bulletin applicability is not diagnosis. Qualified
personnel own internal findings, justified work and return-to-service clearance.

Service attendance means offered technician arrival, not visit end or restoration.
Elapsed work, billable repair hours and rental duration have different meanings.
Setup and lead-time triggers remain unknown where records do not establish them.
Compare full activity periods against access, production start and the delay endpoint.

Service caps are $780 expedited and $480 standard, using integer USD cents. The $300
expedited premium is included and payable on attendance even without resolution.
Diagnosis and travel are included. Actual authorized repair labor and installed parts
remain conditional on findings, coverage and scope; caps are not invoices. Itemization
is part of the exact persisted quote, and altered quotes cannot be saved as authoritative.

Luis's recorded $1,000 ceiling makes him a possible service approver after verified
identity, role, site scope and explicit approval checks. Maya cannot commit. Approved
service submission before expiry preserves scoped prices, not booking or stock.
Changed attendance/scope/cap requires renewed approval; work beyond scope/cap requires
a new quote and approval. Request creation ends at PENDING_DISPATCH and uses immutable
assessment/quote matching, same-content idempotency and lost-result recovery.

The $2,400 loaner requires separate procurement approval and provider acceptance.
The replacement's installation and capacity need verification. Contact directories
never grant authority. Assessment itself creates no commitment. Independent facts
remain in [the source pack](equipment-service-source-pack.md) and `fixtures/business.json`;
this documentation is not a worked answer injected into prompts.

## Limits

Current packages use Framework 1.0.0-beta.8-SNAPSHOT and Sidecar beta.2 source built
against it. Nested bindings do not always eliminate model call envelopes; the final
observed workflow used fifteen model calls per case. Optimizing call count is separate
from business correctness. Mixed assignment does not guarantee reliable review.
Phase 3 will define broader regression and release confidence. See the phase summary
for remaining reasoning caveats; no retired trace or sample is required to start either host.
