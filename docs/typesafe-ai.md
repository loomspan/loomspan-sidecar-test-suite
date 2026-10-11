# Customer-support triage: TypeSafe integration suite

`typesafe-ai` demonstrates typed judgments about a support contact: Choice selects a
department, Noul estimates whether it describes an earlier support attempt, and Score
measures functional impact against supplied levels. The application receives judgments;
it does not route a ticket, refund a customer or perform another customer action.

Both hosts expose `POST /suites/typesafe-ai/evaluations/{skill}` and
`GET /suites/typesafe-ai/executions/{id}` using the shared authenticated execution API.
Java code lives in `example.suites.typesafeai`; Python code in `suites.typesafe_ai`.
There are no deterministic callbacks or business tables for this suite, so it needs no
REST-skill directory or route fragment. Existing equipment rows must remain unchanged.

Native leaves under `config/skills/typesafe-ai` use the `typesafe` driver and explicit
model `jev-1.13.0`. Two ordinary Luna/medium parents demonstrate `output_from` forwarding
and `output_bindings` assembly. Their local planning fixture selects the required native
child; the child dispatch requires no second planning call or chat synthesis.

For example, `tsTriageFixed` accepts this body through either host's authenticated
evaluation endpoint:

```json
{"context":{"message":"Again: checkout fails, but browsing still works. My prior support ticket is unresolved."}}
```

The mock runner additionally registers a unique `context.caseId` with the fixture
service; unregistered manual calls are rejected locally. Use `mixed_fixed` for the
complete runnable offline example. `tsTriageDynamic` accepts candidate descriptions,
Noul criteria and `parameters.levels`; the open parameters object preserves mixed
JSON descriptions until the native declaration validates the resolved score criteria.

## Running and evidence

```powershell
.venv/Scripts/python.exe scripts/run_suite.py mock --suite typesafe-ai --dry-run
.venv/Scripts/python.exe scripts/run_suite.py mock --suite typesafe-ai
.venv/Scripts/python.exe scripts/run_suite.py mock --suite typesafe-ai --scenario mixed_fixed
.venv/Scripts/python.exe scripts/run_suite.py mock --suite all
```

There are 49 authored protocol cases, 34 reviewed responses, 14 derived composition
cases, and 15 authored consumer-policy cases (112 scenarios),
each run through Java and Sidecar by default. The strict
fixture endpoint checks exact state, questions, model, API path and dummy bearer key.
Responses are single-use, except explicitly authored retry sequences. Mismatches stop
the suite; there is no provider fallback. `PROTOCOL_PASS` means the local integration
contract passed. Reports and trace bundles go to `evidence/latest/typesafe-ai`.

`fixtures/typesafe-ai/cases.json` is an independently authored protocol pack, **not a
recording of real TypeSafe judgments**. It retains expected requests, envelopes, outputs
and coverage labels. It is separate from the unchanged accepted equipment replay pack.
The model pin follows the [TypeSafe model catalog](https://docs.typesafe.ai/models),
checked on 2026-10-11; moving latest/preview aliases are not used.

| Area | Cases exercise |
|---|---|
| Primitives | Choice, Noul, Score alone and mixed; different support contacts |
| Criteria | Fixed/dynamic sets; alternate candidates; local limits and invalid resolved criteria |
| Substitution | Typed objects/arrays, structured instructions, pointer escaping/indexing, literal escaping, missing paths and invalid embedded objects |
| Composition | Direct entry, fully bound child dispatch, exact forwarding, assembled consumer schema, missing/invalid bound values |
| Fidelity | Empty/extended answers, unknown fields, missing/null/non-object answers, malformed JSON, complete provider envelope in traces |
| Usage | Exact zero and valid usage; absent, partial, fractional and negative usage precision |
| Transport | Preserved endpoint prefix, terminal 400/401/403/422, retry recovery/exhaustion/disabled policy, read timeout |
| Boundaries | Unauthenticated entry, denied role, invalid host input, no equipment data changes |

Local Framework criteria rules and native answer passthrough are deliberately tested
separately from a consuming schema. For example, singleton/null score criteria accepted
locally are not a claim that the real service accepts them. Unknown answer fields and
out-of-range values may pass through a native leaf; the assembled result has its own
contract. See the pinned Framework guidance and [TypeSafe API](https://docs.typesafe.ai/api).

## Limits and next step

On 2026-10-11, all 49 cases passed through both running hosts: 98 executions and
1,078 checks, reported as `PROTOCOL_PASS`. The grouped run also passed all eight
equipment frozen-reference executions with 240 checks. The 75 local tests and both-host
provider-free smoke passed. Provider access remained disabled and paid calls were zero.
Evidence is replaceable run output under `evidence/latest`, not a new accepted model pack.

These tests establish transport, binding and runtime behavior with deterministic data.
They do not establish provider availability, real semantic accuracy, calibration, current
service acceptance of boundary payloads, cancellation behavior or production reliability.
Framework's own source tests cover additional native contract behavior; passing those is
separate evidence from this application suite. Phase 3 remains outside this work.

The suite now supports a bounded direct-native live/capture adapter. An agreed paid
scope and private `LOOMSPAN_TYPESAFE_API_KEY` are required. Parent chat planning remains
excluded. Live results never automatically overwrite either fixture pack. The normal
runtime remains provider-disabled.

## First live evaluation

The approved batch is six cases on both hosts: 12 maximum TypeSafe sends to
`jev-1.13.0`, no retries, no chat calls, stop on unexpected mechanical failure.
`fixtures/typesafe-ai/live-cases.json` holds the inputs, exact wire expectations and
review rubric authored before the calls. Its semantic ranges are provisional flags,
not calibrated thresholds. Ambiguous department choices can both be acceptable;
incomplete impact evidence requires manual review regardless of the numeric output.

The structured live example uses `tsTriageStructuredLive`, with explicit instructions
and described criteria compatible with the published API. The original structured
mock declaration remains unchanged to protect Framework's broader local contract.

```powershell
.venv/Scripts/python.exe scripts/typesafe_live_preflight.py
.venv/Scripts/python.exe scripts/run_suite.py capture --suite typesafe-ai --model jev-1.13.0 --dry-run
# Within the user-authorized native TypeSafe scope:
.venv/Scripts/python.exe scripts/run_suite.py capture --suite typesafe-ai --model jev-1.13.0 --output evidence/typesafe-live-first
```

`evaluate --path java|sidecar` permits one host; `live` and `capture` run both.
Only predeclared live catalog cases are eligible. The original six remain the default;
select additional evidence cases with repeated `--scenario` arguments. Each batch
allows at most 12 sends. Each exact request has a durable,
one-use permit, consumed before forwarding; failed/uncertain sends cannot be retried
under that permit. The provider key exists only in the temporary fixture service
environment. The gateway forwards to the fixed official endpoint without redirects
or HTTP retries, while Framework retries are also disabled. The gateway waits up to
45 seconds of HTTP inactivity; Framework's live connection allows 60 seconds.
Normal configuration is restored even after failure or interruption.

Capture records exact requests/responses, traces, source/effective configuration,
provider usage and the send ledger. A sent request may be billable even without a
response. Unreported monetary cost stays unknown. `CHECKS_PASS_REVIEW_REQUIRED` means
mechanical checks passed; the capture remains an unreviewed candidate until semantic
review accepts the judgments. The user has delegated that review to the assistant.
The accepted real-response pack remains separate
from the synthetic protocol fixtures and the accepted equipment pack.

An interrupted batch can continue only from its existing send ledger with
`--resume-capture PRIOR_SUITE_DIRECTORY` and a new `--output` directory. Used permits
cannot be sent again. Continuation verifies the previous bundle checksums, unchanged
authored configuration and exact remaining requests; it preserves the initial bundle.
Any offline assertion reassessment is explicit in the combined report. Continuing must
remain within the original paid authorization; this is not permission for a new batch.

## Initial live observations, 2026-10-11

The approved batch completed with exactly 12 physical TypeSafe sends, zero retries and
zero chat calls. All 144 mechanical checks passed after an explicit offline reassessment
of the Score tolerance boundary described below. Framework returned the provider answers
unchanged on both hosts; full envelopes and exact usage were retained in traces.
Usage was 5,292 input and 586 output tokens. Monetary cost was not reported by the API.
Provider access was disabled again after the batch.

| Contact / case | Java result | Sidecar result | Assistant assessment (subsequently reviewed under delegation) |
|---|---|---|---|
| Duplicate invoice charge / Choice | billing | billing | Fits explicit billing evidence |
| Explicit first support contact / Noul | prior-contact probability 0.07 | 0.07 | Fits explicit first contact |
| Complete application outage / Score | 2.00 of 2 | 2.00 of 2 | Fits total functional loss |
| Repeated checkout failure, browsing works / fixed mixed | technical; repeat 0.98; impact 1.80 | technical; repeat 0.98; impact 1.69 | Both fit the predeclared range; checkout is blocked while browsing remains available |
| Late parcel and missing refund; app works / dynamic mixed | delivery 0.61, billing 0.37; repeat 0.03; impact 0.14 | delivery 0.52, billing 0.46; repeat 0.03; impact 0.17 | Reasonable ambiguity between two valid departments; little functional impact |
| “It doesn't work.” / structured mixed | other/technical tied 0.50; repeat 0.10; impact 1.54 | technical 0.57, other 0.43; repeat 0.09; impact 1.73 | Routing uncertainty is appropriate; impact lacks enough evidence for action |

The sparse contact is the main limitation: the model still supplies a fairly high
impact value despite missing detail. Its impact confidence was 0.32 on Java and 0.61
on Sidecar. Neither establishes that severity is known. A future application decision
should request clarification or explicitly assess evidence sufficiency before using
severity; that gate is not implemented or validated by this batch. No customer action
was taken. Different live calls used different correlation IDs, so these observations
do not establish identical outputs for byte-identical inputs or quantify repeatability.

The first segment stopped after seven sends because binary floating-point arithmetic
made the difference between 1.80 and 1.81 slightly greater than the intended 0.01
tolerance. A regression test now protects that inclusive boundary with numerical epsilon;
the tolerance was not widened materially. The original failure report remains intact.
Seven responses were reassessed offline; five unused permits completed the same batch,
without reissuing any completed send. The combined bundle preserves the original
evidence, source/configuration, and explicit reassessment.

The twelve captured real responses then passed 24 offline replays, each through both
hosts, with no additional provider access. The 83 local tests passed. This verifies
runtime fidelity and the bounded examples; it does not establish calibration or broad
model accuracy. These were initially pending review; the delegated acceptance below
supersedes that pending status without rewriting the original capture reports.

Evidence: [combined live capture](../evidence/typesafe-live-completed-2026-10-11/typesafe-ai/summary.md),
[original stopped capture](../evidence/typesafe-live-first-2026-10-11/typesafe-ai/summary.md),
and [offline capture replay](../evidence/latest-typesafe-capture-replay/typesafe-ai/summary.md).
To replay that candidate again without accepting it:

```powershell
.venv/Scripts/python.exe scripts/typesafe_live_preflight.py --capture evidence/typesafe-live-completed-2026-10-11/typesafe-ai
```

## Delegated semantic acceptance and evidence sufficiency

The user delegated acceptance judgment and authorized further useful TypeSafe calls.
I accept the first five original contacts. Billing and repeat-contact judgments fit
explicit facts. The original checkout impact of 1.69–1.80 is reasonable because its
highest level is **core operation blocked**; that is different from the new scale's
**all functionality blocked**. Delivery versus billing is a legitimate ambiguity in
the missing-refund/late-parcel example, not an error requiring forced confidence.
I reject interpreting the original sparse contact's impact as established severity.

`tsTriageEvidence` asks two independent questions over the same state:

- `impactEvidence` (Noul): whether supplied observations establish current functional
  extent, with explicit exclusions for vague, missing and contradictory evidence.
- `impact` (Score): normal operation, partial functional failure, or all functionality
  blocked; resolved history and emotional urgency do not set this scale.

The six initial evidence contacts and six fresh holdouts used the same question, with
expectations written before each batch. No prompt changes or retrospective threshold
adjustments were made. The 24 additional live calls passed 288 mechanical checks,
with zero retries or chat calls. Reported usage totaled 11,801 input and 888 output
tokens; monetary cost was not returned. Provider access was restored to disabled.

| Contact | Evidence probability Java / Sidecar | Impact Java / Sidecar | Review |
|---|---|---|---|
| Vague malfunction | 0.04 / 0.04 | 1.46 / 1.67 | Accept insufficiency; ignore impact |
| Urgency without symptoms | 0.02 / 0.02 | 0.48 / 0.50 | Accept insufficiency; ignore impact |
| Billing issue, explicit normal operation | 0.87 / 0.89 | 0.00 / 0.00 | Accept both judgments |
| CSV export fails, other functions work | 0.77 / 0.79 | 1.00 / 1.00 | Accept both judgments; provisional 0.80 range missed |
| Explicit total outage | 0.84 / 0.85 | 2.00 / 2.00 | Accept both judgments |
| Unresolved conflicting current reports | 0.04 / 0.04 | 1.53 / 1.56 | Accept insufficiency; ignore impact |
| Past outage, explicit current recovery | 0.90 / 0.90 | 0.00 / 0.00 | Accept both judgments |
| Billing issue, functionality unspecified | 0.08 / 0.08 | 0.55 / 0.29 | Accept insufficiency; ignore impact |
| Calm contact, explicit total outage | 0.81 / 0.79 | 2.00 / 2.00 | Accept both judgments; provisional 0.80 range missed |
| Angry contact, explicit normal operation | 0.81 / 0.79 | 0.00 / 0.00 | Accept both judgments; provisional 0.80 range missed |
| Checkout fails, other functions work | 0.85 / 0.86 | 1.00 / 1.00 | Accept both judgments |
| Detailed billing/delivery facts only | 0.14 / 0.12 | 0.57 / 0.45 | Accept insufficiency; ignore impact |

My judgment: the explicit-impact results are sound, and the evidence question catches
all the deliberately unsupported cases in this sample. The 0.77–0.79 results are
reasonable yes-leaning probabilities, but four clear cases missed my provisional
0.80 strong-yes range. I accept them with that caveat, preserving the original flags.
A consumer using 0.80 would conservatively defer those cases. This small set does not
establish a universal threshold or probability calibration. A Noul is not a substitute
for a stronger reasoning model on arbitrarily complex evidence.

For insufficient evidence, a Score still returns a value. Its distribution must not
be interpreted as known severity, even when concentrated. A consumer should ask for
clarification before using it. That initial experiment exposed raw judgments without
a decision gate. The subsequently approved application policy is described below.

The maintained [reviewed pack](../fixtures/typesafe-ai/reference/README.md) contains
34 responses: ten from the first five original contacts plus 24 from the new contacts.
Its [review](../fixtures/typesafe-ai/reference/review.json) specifies accepted and
ignored questions, caveats and exact source hashes. The original sparse-contact
responses remain excluded. These are regression samples, not a validation dataset
large enough to support an accuracy claim. Both captured host variants replay through
both current hosts, alongside the 49 authored protocol cases (83 scenarios total).

```powershell
# Everything, without provider access:
.venv/Scripts/python.exe scripts/run_suite.py mock --suite typesafe-ai
# One recorded response, through both hosts:
.venv/Scripts/python.exe scripts/run_suite.py mock --suite typesafe-ai --scenario reference_evidence_sparse_java
# Explicit live selection under the standing TypeSafe authorization:
.venv/Scripts/python.exe scripts/run_suite.py capture --suite typesafe-ai --model jev-1.13.0 --scenario evidence_sparse --scenario evidence_partial --dry-run
```

Evidence: [first evidence batch](../evidence/typesafe-evidence-live-2026-10-11/typesafe-ai/summary.md),
[holdout batch](../evidence/typesafe-evidence-holdout-2026-10-11/typesafe-ai/summary.md).
Original capture reports retain their pending-review status as historical artifacts;
the separate checksum-linked review records subsequent delegated acceptance.

Final verification: 86 local tests passed. The grouped offline replay passed all
166 TypeSafe executions (2,052 checks) and eight equipment executions (240 checks),
with zero paid calls and both evidence bundles checksum-verified. Provider access
remained disabled. See [grouped replay results](../evidence/typesafe-reviewed-replay-2026-10-11/summary.md).

## Application impact policy

Both hosts now provide an owner-authenticated decision view:

1. Submit `POST /suites/typesafe-ai/evaluations/tsTriageEvidence` with the normal
   `{ "context": { "message": "..." } }` input through the configured test transport.
2. Poll `GET /suites/typesafe-ai/executions/{id}` for the unchanged raw result.
3. Read `GET /suites/typesafe-ai/executions/{id}/impact` for the same execution and
   raw result plus `impactDecision`. This GET performs no inference or customer action.

The decision has `status`, `reason`, `evidenceProbability`, `evidenceThreshold` and
`impactScore`. At the default threshold 0.80, an evidence probability below 0.80
returns `NEEDS_CLARIFICATION / INSUFFICIENT_EVIDENCE`, with `impactScore: null`.
Otherwise the policy validates the Score's numeric range, probability distribution
and consistency before returning `ASSESSED / SUFFICIENT_EVIDENCE`. A fractional
Score remains fractional; it is not rounded into a severity label. Required missing,
wrongly typed, non-finite or inconsistent values return
`NEEDS_CLARIFICATION / INVALID_JUDGMENTS`, never an asserted impact. An unused Score
is deliberately ignored when evidence is already insufficient.

Use `?evidenceThreshold=0.75` for an explicit alternative; the threshold is echoed
in the decision. It must be finite and within 0–1, otherwise HTTP 400. Overrides
re-evaluate only the application policy over the retained result. They neither
change a model judgment nor calibrate a threshold. The default remains 0.80 despite
the previously observed unnecessary clarification. Requests for another owner's
execution or an unrelated skill/impact scale return 404. Pending or failed executions
retain their execution status and have no `impactDecision`.

The policy applies only to `tsTriageEvidence`, `tsTriageEvidenceForward`, and
`tsTriageEvidenceSummary`. It must not interpret `tsTriageFixed`'s different impact
scale. Java implements it in `example.suites.typesafeai.policy.ImpactPolicy`; Python
in `suites.typesafe_ai.policy`. Both are checked against the same independently
authored policy vectors, including boundary equality, type errors and unused branches.
Normal startup still disables provider access; manual inputs need registered fixture
requests. The suite runner provides the complete runnable examples.

## Real-response composition replay

The accepted reference files remain unchanged. The scenario loader derives 14 cases
from them: four through the existing Fixed forwarding/summary parents, and ten through
new Evidence parents using five representative captured responses. Every derived
scenario preserves the original native request/envelope and source identity.

`tsTriageEvidenceForward` returns the entire child answer unchanged.
`tsTriageEvidenceSummary` binds the complete `impactEvidence` and `impact` objects
into its receiving output contract, preserving distributions and provider extensions.
The application policy consumes the resulting objects. These small wrappers illustrate
Framework composition; direct invocation remains the simpler entry for this example.
Planning replies remain authored local fixtures: this tests Framework dispatch,
forwarding, assembly and application consumption, not live chat planning quality.

```powershell
.venv/Scripts/python.exe scripts/run_suite.py mock --suite typesafe-ai --scenario reference_evidence_sparse_java__tsTriageEvidenceForward
.venv/Scripts/python.exe scripts/run_suite.py mock --suite typesafe-ai --scenario reference_evidence_partial_java__tsTriageEvidenceSummary
```

The policy evaluation records semantic outcomes separately from mechanical checks:
`CORRECT_ASSESSMENT`, `CORRECT_CLARIFICATION`, `UNNECESSARY_CLARIFICATION`,
`UNSUPPORTED_ASSESSMENT`, and `INCORRECT_IMPACT`. Fresh live-case sufficiency and impact
expectations are authored before calls; a mechanically passing run does not imply
those semantic outcomes are all correct.

## Application-policy verification and live review, 2026-10-11

The Java package build and two JUnit tests passed, including the shared 16-case policy
contract. All 110 Python tests passed; the 24 focused policy tests also passed in
isolation after adding an oversized-number check. The full offline run passed all
224 native executions (3,242 checks) and eight equipment executions (240 checks).
All 14 derived composition scenarios ran on both hosts. A final focused replay on
the updated Python host passed all 15 consumer-policy scenarios (255 checks).
Reference responses and their acceptance checksum remain unchanged.

Six new policy contacts ran once on each host, followed by two routing contacts on
each host: **16 physical TypeSafe sends**, no retries or paid chat. All 228 mechanical
checks passed. Usage was 7,889 input and 744 output tokens; monetary cost was not
reported. Both live runs restored provider-disabled operation. Captures and replay
bundles were checksum-verified.

| Fresh policy contact | Evidence probability Java / Sidecar | Decision on both hosts | Semantic review |
|---|---|---|---|
| CSV export fails; other functions untested | 0.07 / 0.07 | Clarify; no usable score | Correct: partial versus total scope is unknown |
| Historical outage, all functions tested working today | 0.89 / 0.87 | Assess impact 0.00 | Correct current recovery |
| Equally credible conflicting current reports | 0.04 / 0.04 | Clarify; no usable score | Correct: conflict remains unresolved |
| East office blocked; west office working | 0.64 / 0.65 | Clarify; no usable score | Unnecessary clarification under the predeclared rubric; raw impact 1.17 / 1.18 reasonably describes partial impairment |
| Ticket marked resolved, current functionality untested | 0.03 / 0.03 | Clarify; no usable score | Correct: administrative resolution is not evidence of recovery |
| Calm contact, every function inaccessible to everyone | 0.84 / 0.85 | Assess impact 2.00 | Correct total loss despite low urgency |

Across these 12 executions: four correct assessments, six correct clarification
requests, two unnecessary clarifications, zero unsupported assessments and zero
incorrect exposed impact values. The two deferrals represent one regional contact,
not two independent problem categories. I regard the model's regional impact scores
as reasonable, but retain the evidence-range miss and conservative policy outcome.
Keep the default 0.80: this small study does not justify lowering it globally.
Clarifying whether functional extent is judged across sites/users or within one
affected group is a better next question-design experiment. That refinement is not
silently applied to the frozen examples or this trial.

For the lost-parcel/refund contact, Java's live call chose billing (0.55 versus delivery
0.43); Sidecar's chose delivery (0.76 versus billing 0.24). Both are valid by the
predeclared rubric. Marketing-email preferences correctly selected `other` on both
calls (0.99 and 1.00). Repeat-contact probabilities and functional-impact values were
appropriately low. I accept these routing judgments. Live output identity is not a
host-equivalence requirement; replaying the same responses through both hosts tests
equivalent handling. No ticket routing or customer action was performed.

Evidence: [full offline regression](../evidence/typesafe-policy-replay-2026-10-11/summary.md),
[final policy replay](../evidence/typesafe-policy-final-validation-2026-10-11/summary.md),
[policy capture](../evidence/typesafe-policy-live-2026-10-11/typesafe-ai/summary.md),
[policy semantic review](../evidence/typesafe-policy-live-2026-10-11/typesafe-ai/business-review.json),
[routing capture](../evidence/typesafe-routing-live-2026-10-11/typesafe-ai/summary.md),
and [routing semantic review](../evidence/typesafe-routing-live-2026-10-11/typesafe-ai/business-review.json).
These fresh captures are reviewed diagnostic evidence, not replacements for the
maintained reference pack. The sample size does not establish calibration or general
accuracy; live parent planning remains outside this test.
