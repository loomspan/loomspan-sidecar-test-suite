# Equipment service resolution: fictional source pack

Current implementation note (2026-10-01): implementation is authorized and underway on Framework beta.7 / Sidecar beta.2. This document retains domain/design history; any older release, authorization, “no captures,” or “not yet verified” statements describe that earlier planning stage. Apply the latest accepted decisions in [project agreement](project-agreement.md), resume from [implementation handoff](implementation-handoff.md), and use [implementation status](implementation-status.md) for observed results and remaining work.

Draft 0.2 — 2026-09-30. Companion to the [working design](equipment-service-design-draft.md).

**All equipment, organizations, people, records, prices, and contract terms below are fictional demonstration material.** The accepted decisions below establish part of the baseline; other details remain proposals. These are not instructions for real machinery or real legal/service terms. The manual is organized as five intended pages for review in Markdown; page layout and PDF production are later authoring tasks. Section IDs are proposed stable citation targets.

### Accepted review decisions — 2026-09-30

- Keep the carton sealer, recurring warm-up fault, inconclusive sensor-repair history, and conditional pricing. Source documents supply technical guidance and observations; case-specific interpretations belong in evaluator notes, not passages supplied as evidence to the model.
- A production delay of up to two hours is recoverable; losing the morning shift threatens the shipment. The loaner offer expires before technician arrival, so availability after diagnosis cannot be assumed. Higher approval requirements restrict commitment, not recommendation.
- Luis can authorize expedited diagnosis plus the specified conditional repairs with maximum customer exposure of $780 while coverage is pending. Technician findings justify the work; deterministic rules apply coverage to qualifying items. Partial coverage is possible. Work outside the approved scope or cap requires a new quote and approval.
- Routine qualifying technician findings support deterministic warranty treatment. Disputed or incomplete findings go to the warranty reviewer; a model hypothesis cannot establish entitlement.

Further accepted on 2026-09-30: this first example has no separate workmanship/callback guarantee; manufacturer warranty and service-plan benefits continue to apply. Missing maintenance records are an information gap and do not by themselves trigger warranty review, suspend coverage, or establish an exclusion. Incident-specific incomplete or disputed findings still require review.

Also accepted on 2026-09-30: diagnosis and travel remain included even when the fault is unresolved. The $300 premium is payable when expedited attendance occurs. Only actual authorized repair labor and installed parts are chargeable, subject to warranty and the approved cap. A timely submitted approved service request preserves quoted prices, while resource availability remains unconfirmed. Changes to attendance, repair scope, or the approved cap require renewed approval.

The baseline business snapshot is 2026-09-29 at 09:00 America/Los_Angeles (`2026-09-29T09:00:00-07:00`). Scenario variations must explicitly override the relevant baseline records. Amounts are USD; dates and clock times below use the site time zone unless stated otherwise.

Accepted in the fresh review: restoration-risk preference is an explicit planning input and may be unspecified. The base case supplies no such preference, restoration probability, or monetary downtime value. Recommendations must address the expiring continuity decision and accepted risk without inventing those facts. Evaluator expectations, including defensible alternative strategies, remain in the working design rather than retrieved evidence.

## A. Manufacturer user manual — MAN-P240-R2, revision 2.0

Issuer: Aster Equipment. Effective 2026-06-01. Applies to fictional P240 hardware revision B, including asset `NB-P240-017`. This operator manual does not authorize internal electrical/mechanical repair. The source pack intentionally supplies no detailed internal repair procedure.

### Intended page 1 — purpose, identity, and responsibilities

**MAN-1.1 — Equipment purpose.** The P240 seals pre-formed cartons on a packaging line. The controller monitors carton passage and stops the cycle when the expected passage signal is absent. A stopped cycle describes the observed state; it does not identify the failed component. The asset label, hardware revision, and controller event record are needed when requesting support.

**MAN-1.2 — Identify the equipment.** Record the asset identifier, manufacturer serial number, hardware revision, and site. Similar-looking P200 and P240 machines use different parts and guidance. Use documents applicable to the registered model and revision. An unverified photograph or a familiar product name is insufficient to choose a replacement part.

**MAN-1.3 — Operator and technician responsibilities.** Operators report symptoms and perform only site-approved actions designated for operators. Authorized technicians investigate internal faults, replace internal components, and determine whether the equipment can return to service. The service coordinator arranges assistance and records uncertainty; it does not grant technical clearance.

**MAN-1.4 — Conditions requiring escalation.** Reports of smoke, burning odor, exposed wiring, a damaged guard, or an active protective interlock require the site's stop-use and qualified-person escalation process. Production urgency does not justify bypassing a guard or protective function. Absence of these reported conditions is not a statement that the equipment is safe.

### Intended page 2 — observations and incident reporting

**MAN-2.1 — Useful observations.** Record the displayed event code, time since startup, whether the symptom repeats, carton type, recent changes, visible condition of the externally accessible sensor window, and actions already performed. Note whether a restart appears to restore operation and how long that restoration lasts. Do not repeatedly restart solely to conceal or work around a recurring fault.

**MAN-2.2 — Permitted operator care.** The externally accessible sensor window has an operator-cleaning procedure in the site's approved maintenance instructions. Operators must follow those instructions and applicable shutdown requirements. This reference manual does not provide a substitute physical procedure. Record that the permitted cleaning was completed, by whom, and whether the symptom recurred.

**MAN-2.3 — Event codes.** `E17` means the expected carton-passage signal was not received. Possible explanations include an obstructed viewing path, a sensor problem, or an intermittent connection. `E08` indicates a protective-interlock condition; it is not a sensor-cleaning prompt. Codes are evidence for investigation and must not be converted directly into a confirmed failed-part diagnosis.

**MAN-2.4 — Restart reports.** A report that the machine resumes after cooling is relevant to an intermittent fault. It does not establish which component is responsible, nor does it authorize continued operation. Record the warm-up and recurrence intervals so a technician can reproduce the reported condition using approved procedures.

### Intended page 3 — interpreting common symptoms

**MAN-3.1 — Isolated passage-signal event.** For a single E17 incident with a documented external obstruction, record the observation and the permitted action taken. If a qualified/site-authorized process permits follow-up observation and there is no recurrence, the service case may be handled as monitoring rather than an immediate parts replacement. The service coordinator must not manufacture a safety clearance.

**MAN-3.2 — Repeated E17 after warm-up.** Recurrence after an interval, especially after an apparently effective restart or cleaning, warrants technician assessment. Include warm-up duration, prior interventions, recent component changes, and any applicable service bulletin. Do not assume that the most recently replaced component has failed again.

**MAN-3.3 — Evidence that distinguishes explanations.** An external obstruction report supports one explanation. Recurrence after documented cleaning weakens that explanation but does not eliminate all optical or alignment causes. A temperature-linked pattern may justify considering a connection or component issue. Inspection findings are required before recording a specific confirmed defect.

**MAN-3.4 — Service test records.** Record test conditions, duration, observed events, and the responsible technician in the work-order closeout. Link subsequent incident reports to the relevant work order and retain the original closeout record.

### Intended page 4 — care records, parts, and technical handoff

**MAN-4.1 — Maintenance record.** The example site's maintenance schedule calls for an operator condition entry each working day and a qualified inspection every 90 days. Entries identify the asset, activity, date, author, and exceptions. Missing entries should be investigated. Their absence alone does not prove that maintenance was omitted or caused a fault.

**MAN-4.2 — Parts compatibility.** Revision B equipment uses sensor `S17-B` and connector kit `H17-B`. A revision A part with a similar description is not an approved substitute. Compatibility must come from the catalog or an authoritative supersession record. Stock quantity alone cannot make an incompatible part feasible.

**MAN-4.3 — Technician work.** Internal access, fault confirmation, internal part replacement, and return-to-service decisions belong to appropriately qualified personnel. A service recommendation can request investigation and identify potentially useful parts. It must distinguish parts to bring from parts already diagnosed as necessary.

**MAN-4.4 — Post-service evidence.** The closeout should state the observed cause, corrective work, installed part identifiers, test conditions and duration, remaining limitations, and the responsible technician. Where the original symptom was intermittent, explain how the verification addressed that symptom. Do not treat a service-request receipt as evidence that this work occurred.

### Intended page 5 — obtaining service and planning continuity

**MAN-5.1 — Service-request contents.** Provide the asset/serial, event code, symptom chronology, recurrence intervals, prior repair IDs, completed operator actions, applicable evidence, site contact, access restrictions, production deadline, and authorized scope. Include unresolved questions rather than filling gaps with guesses.

**MAN-5.2 — Attendance versus restoration.** A response or attendance commitment describes when support will respond or attend. It does not guarantee fault identification, availability of every required part, successful repair, or restored production by a particular time. Those depend on findings and resources.

**MAN-5.3 — Continuity options.** A compatible temporary unit can be considered when restoration is uncertain and continuity matters. Check capacity, site compatibility, delivery and setup requirements, availability, cost, and approval. A permanent replacement may have a longer lead time than a temporary unit. Do not describe either as ready merely because it appears in a catalog.

**MAN-5.4 — Warranty and service agreement.** Consult the asset's warranty certificate and current service agreement. Being within the warranty period is one condition, not confirmation that every incident is covered. Explain conditional charges and excluded premiums. The user manual does not override the contractual terms.

**MAN-5.5 — Escalation handoff.** Provide the next responsible party with the evidence summary, requested decision, urgency, contact details, and current uncertainty. If approval or further diagnosis is required, say so clearly. Preparing this information is distinct from sending a message or confirming a booking.

## B. Technical bulletin — SB-P240-06, revision 1

Issuer: Aster Equipment Technical Service. Effective 2026-07-15. Applicable to P240 revision B serials `AP24B-0400` through `AP24B-0799` inclusive.

**SB-1 — Reported pattern.** Repeated E17 incidents after warm-up have sometimes been associated with intermittent sensor-harness connections. Affected serial eligibility and a matching symptom are reasons to investigate, not proof of the condition.

**SB-2 — Assessment guidance.** When E17 recurs after sensor replacement or permitted external cleaning, an authorized technician should include the harness connection in the investigation. Avoid ordering another sensor solely because E17 appears. This supplements MAN-3.2 and does not supersede the manual's responsibility or escalation boundaries.

**SB-3 — Coverage.** The bulletin is not a recall, blanket replacement authorization, or warranty extension. Warranty determination still requires applicable terms and incident findings.

## C. Warranty certificate and terms — WC-017 / WT-24, revision 1

Issuer: Aster Equipment. Certificate applies to serial `AP24B-0517`, commissioned 2025-02-10. Coverage dates are **2025-02-10 inclusive through 2027-02-10 exclusive**, interpreted as site-local calendar dates for this fixture. Original customer: Northbank Fulfillment.

| Clause | Proposed fictional term |
| --- | --- |
| W-1 | During the certificate period, covered manufacturing defects qualify for the listed replacement parts and associated standard repair labor |
| W-2 | A qualified authorized technician must document the defect and its relationship to the incident; an operator report or model hypothesis alone yields pending determination |
| W-3 | Confirmed accidental damage, unauthorized modification causing the fault, and ordinary consumable wear are excluded; exclusions require evidence relevant to this incident |
| W-4 | Missing maintenance records are an information gap; their absence alone does not trigger warranty review, suspend coverage, or establish an exclusion. Incomplete or disputed incident-specific findings remain subject to W-7 |
| W-5 | Expedited attendance premiums, loaners, lost production, and unrelated upgrades are excluded from this warranty |
| W-6 | Warranty does not extend merely because a part was replaced during the original period; no separate replacement-part warranty is modeled in this draft |
| W-7 | Conflicting or incomplete findings produce pending review with a responsible reviewer; do not silently convert pending to covered or denied |

These terms are deliberately small enough to encode and test independently. The model explains their relevance and uncertainty. Code evaluates dates, required evidence, covered categories, and the amounts implied by known findings.

Accepted clarification: routine qualifying authorized-technician findings are sufficient for deterministic treatment under the terms; separate manufacturer approval is not required for every routine finding. Disputed or incomplete incident-specific findings remain pending review. Coverage applies to the relevant parts and associated labor individually, so some quoted items may qualify while others do not. Missing maintenance records alone do not change that treatment; W-4's former automatic review trigger is removed.

## D. Service agreement and rate card — SA-NB-2026 / RATE-09, revision 1

Parties: Northbank Fulfillment and Beacon Field Service. Agreement is active from 2026-01-01 inclusive to 2027-01-01 exclusive. Includes site `NB-WEST` and asset `NB-P240-017`. Coverage of this asset is independent of its manufacturer-warranty status.

| Clause | Proposed fictional term |
| --- | --- |
| S-1 | Standard service desk hours are weekdays 08:00–17:00 site time; requests submitted in that window receive acknowledgment within two business hours |
| S-2 | Standard attendance targets the next business day, subject to dispatch confirmation; this is not a guaranteed repair deadline |
| S-3 | For covered assets, diagnosis and travel are included even if the fault remains unresolved. Only actual authorized repair labor and installed parts are chargeable, subject to warranty and the approved cap. Diagnostic investigation is not chargeable repair labor |
| S-4 | Expedited same-day attendance may be offered for a $300 premium, subject to availability and authorization. The premium is payable when expedited attendance occurs, even if the fault remains unresolved; neither service agreement nor warranty pays it |
| S-5 | An approved service request submitted before quote expiry preserves the quoted prices for its approved scope. Approval alone does not preserve prices. Creating the request asks dispatch to confirm resources; it does not reserve stock or book an appointment. Changes to attendance, repair scope, or the approved cap require renewed approval |
| S-6 | Work beyond the approved scope/cap requires a new quote and approval. No tax applies in this synthetic fixture; this is not a statement about real taxation |
| S-7 | This first example provides no separate workmanship/callback guarantee for repeat repairs, including WO-0820. Manufacturer warranty and service-plan benefits still apply under their respective terms; a recurring symptom alone creates no additional free-repeat-work entitlement |

Rate card: diagnostic visit $250; travel $100; standard repair labor $150/hour; sensor `S17-B` $120; connector kit `H17-B` $60; expedited attendance $300. The example possible repair scope includes at most two labor hours and one of each listed part, after technician findings. Additional parts/hours are outside that scope.

**QUOTE-017-E1**, issued 09:05, expires 11:00 on the fixture date, proposes expedited diagnosis with conditional repair within this scope:

| Line | List amount | Active service-plan treatment | Pending-warranty customer exposure |
| --- | ---: | --- | ---: |
| Diagnostic visit | $250 | Included | $0 |
| Travel | $100 | Included | $0 |
| Up to two repair labor hours | $300 | Not included | $300 |
| Sensor and connector kit, if required | $180 | Not included | $180 |
| Expedited attendance | $300 | Not included | $300 |
| **Maximum within scope** | **$1,130** | **$350 included** | **$780** |

If warranty confirms both listed parts and labor as covered, the maximum customer amount for those same quoted items becomes $300, consisting of the expedited premium. The visit does not presume both parts will be installed. An unresolved fault or work outside the scoped repair requires a follow-up decision. No guarantee of complete repair is attached to the $780 cap.

Accepted authorization: Luis may approve the $780 maximum exposure while warranty remains pending. That authorizes diagnosis and only the specified repairs justified by technician findings; it does not require installing both parts or using all allowed labor. Coverage can be partial: $300 and $780 are endpoints for maximum exposure under the quoted expedited scope, not the only possible charges or final invoice amounts. Under S-3 and S-4, expedited attendance with diagnosis only costs $300 even if the fault remains unresolved. If authorized repair work is performed, actual repair labor and installed parts may add charges within scope and cap, subject to warranty; unsuccessful repair does not automatically waive those charges.

The standard-attendance equivalent has no expedited premium: maximum $480 if warranty is denied, or $0 for the covered quoted items if confirmed, with active service-plan inclusions in both cases. Its timing misses the requested production start. These are proposed fixed expectations; later code must reproduce them without being reused to define its own test oracle.

## E. Asset, people, and operational records

| Record | Baseline content |
| --- | --- |
| ASSET-017 v1 | `NB-P240-017`; serial `AP24B-0517`; P240 revision B; commissioned 2025-02-10; owned by Northbank; site `NB-WEST` |
| SITE-WEST v1 | America/Los_Angeles; equipment floor access 08:00–18:00; dispatcher must arrange later access with the site contact |
| PROD-0930 v3 | Production starts 2026-09-30 06:00; minimum required capacity 18 cartons/minute; operations reports that a delay of up to two hours is recoverable, but losing the morning shift threatens the shipment; restoration-risk preference unspecified; no agreed monetary downtime estimate |
| AUTH-NB v1 | Luis may approve customer exposure up to $1,000 for his site; larger commitments need Priya's separately verified approval; no permission derives from directory entries |
| CONTACT-MAYA v1 | Maya Chen, operator and incident reporter; maya.chen@northbank.example; ordinary site shift contact |
| CONTACT-LUIS v1 | Luis Romero, maintenance manager and access contact; luis.romero@northbank.example; 08:00–18:00; backup through site service desk |
| CONTACT-PRIYA v1 | Priya Shah, procurement approval contact; priya.shah@northbank.example; 09:00–17:00 |
| CONTACT-BEACON v1 | Erin Cole, dispatch; dispatch@beacon-service.example; weekdays 08:00–17:00; service-request queue is authoritative for status |
| CONTACT-WARRANTY v1 | Aster warranty-review queue; warranty@aster-equipment.example; resolves disputed findings, no promised immediate turnaround |

All addresses use reserved example domains. They are data for a proposed handoff, not recipients to contact. Grant records belong to the authenticated authorization model, separate from this directory.

## F. Maintenance and repair history

| Record / date | Author and observation | What it establishes and what it does not |
| --- | --- | --- |
| MAINT-0710 / 2026-07-10 | Qualified technician Jo Ellis completed scheduled inspection; no open exceptions | Inspection was recorded; not proof of condition in September |
| WO-0820 / 2026-08-20 | Authorized technician replaced S17-B after E17 report; closeout says “suspected sensor fault; 20-minute test without recurrence” | Part replacement and short successful test; no confirmed cause for the new incident |
| NOTE-0916 / 2026-09-16 | Maya reports E17 after 42 minutes; restart appeared effective temporarily; linked to WO-0820 | Later reported recurrence; not a certified diagnosis |
| MAINT-0928 / 2026-09-28 | Operator condition/cleaning entry complete, no visible window obstruction recorded | Recent documented care; does not exclude all sensor problems |
| INCIDENT-0929 / 2026-09-29 08:40 | Maya reports three warm-up recurrences of E17, 35–50 minutes after startup; cleaning did not resolve it; no reported red flags | Current incident narrative; no authority to clear equipment or classify the defect |

The next scheduled 90-day inspection after July 10 is October 8, so the baseline is not overdue on September 29. Interpretations of the closed work order and later recurrence belong in the working design's evaluator notes, not the source evidence returned to the model. The table's explanatory third column is authoring guidance; retrieval should supply the attributed records and observations rather than that commentary.

## G. Resource and continuity offers

Snapshot observed 2026-09-29 09:05; offers expire 11:00 unless replaced. Each is an offer only, with no hold on inventory or personnel.

For an approved service request submitted before expiry, S-5 preserves quoted prices for the approved scope after 11:00. It does not extend the resource-availability snapshot or guarantee attendance. Dispatch confirmation matching the approved attendance and scope does not itself require a second approval; a change to attendance, repair scope, or cap does.

Accepted planning constraint: the loaner offer expires before the expedited technician's 14:00–16:00 arrival window. A plan to wait for diagnosis and then obtain this loaner has no confirmed availability. Early escalation for continuity approval can be defensible even though Luis cannot authorize its price. The table's decision-significance column is authoring guidance, not additional supplier evidence.

| Offer | Baseline facts | Decision significance |
| --- | --- | --- |
| PARTS-017 v1 | Two S17-B sensors and one H17-B kit locally available; can accompany today's offered visit | Makes scoped investigation/repair practical without proving either part is needed |
| SLOT-EXP-017 v1 | Jo Ellis, P240 revision B qualification, arrival window today 14:00–16:00; estimated work 2–4 hours | Before production start but completion/access may extend beyond site hours; coordinate with Luis, do not promise restoration |
| SLOT-STD-017 v1 | Qualified standard attendance tomorrow 10:00–12:00 | Cheaper but after 06:00 production start |
| LOAN-017 v1 | Compatible temporary sealer, 20 cartons/minute; delivery/setup window tonight 20:00–22:00; $2,400 fixed three-day package including return | Meets capacity on paper and may support deadline; requires approved after-hours access, supplier confirmation, and higher spending approval |
| REPLACE-017 v1 | Compatible new P240 revision B, $12,500 equipment price, estimated lead time ten business days; installation not yet quoted | A longer-term alternative, not a remedy for tomorrow's start |

Do not hide the access issue in the expedited or loaner option. Site access arrangements are a specific handoff item. The 2–4 hour work estimate includes diagnosis and possible repair; the quote allows at most two chargeable repair hours, with additional repair work requiring a new approval. Do not treat the estimate as a guaranteed diagnosis or repair duration.

## H. Decision and action records: accepted boundary, proposed details

The assessment record should preserve which versions of A–G were consulted, the supported alternatives, selected option, quoted amounts, uncertainty, questions, required authority, and next contact. It should cite source IDs and sections, not fabricated URLs.

For the base example, Maya's assessment ends awaiting approval without creating business commitments. In one later authenticated submission, Luis explicitly approves the expedited scoped option with $780 maximum exposure and requests service-request creation while the quote remains valid. His verified approval is recorded with the request; there is no separate approval-management workflow. The created service request includes the incident, evidence references, approved attendance, requested parts to bring, pending coverage status, repair scope/cap, and site-access question. The application's action ends at a durable `PENDING_DISPATCH` receipt. It does not say “technician booked,” “warranty approved,” or “machine repaired.”

Dispatch confirmation, technician findings, and changed offers remain fixture records. They may inform assessments or demonstrate the need for renewed approval, but the first reference does not manage dispatch, repair, or post-creation amendment lifecycles. The boundary and single approval/creation submission were accepted on 2026-09-30; exact fields and error contracts remain to be designed.

A repeated commitment with the same idempotency key and same approved content returns that receipt. Reuse with different content must not create or silently substitute another request. The exact error/status contract remains to be designed.

## I. What remains to author after review

### Service-term review status

The identified callback, missing-record, unsuccessful-visit, and submission/dispatch terms are settled for this example in W-4 and S-3 through S-7. This is a scoped demonstration contract, not a complete billing system. Exact action contracts, dispatch representation, and scenario assertions remain to be reviewed before building.

Keep these initial documents small. We still need a reviewed version of the fictional manual/terms; machine-readable mirrors for dates, compatibility and prices; separate scenario deltas for the [example portfolio](equipment-service-design-draft.md#7-planning-step-4-a-robust-example-portfolio); independent expected results; and scripted model responses that check the actual evidence received.

Add only artifacts that change a decision or establish an observable claim. A diagram of machine components could improve a later presentation, but realistic drawings, a full maintenance ERP, and a document-search platform are not prerequisites for the first demonstration.
