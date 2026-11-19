# Partial-outage evidence question review

November 17, 2026. The threshold was 0.80 throughout. Each wording was tested on the same 18 contacts, once per host with `jev-1.13.0`. Only the evidence Noul changed. The impact Score, state, and application policy stayed fixed. The original column uses the preceding live run. The other two columns use 72 new sends across six batches.

| Contact | Original evidence | Scope wording | Final wording | Final decision on both hosts |
|---|---:|---:|---:|---|
| `evidence_sparse` | 0.04 / 0.04 | 0.12 / 0.13 | 0.20 / 0.21 | correct clarification |
| `evidence_urgent` | 0.02 / 0.02 | 0.05 / 0.05 | 0.09 / 0.09 | correct clarification |
| `evidence_normal` | 0.86 / 0.89 | 0.84 / 0.86 | 0.96 / 0.96 | correct assessment |
| `evidence_partial` | 0.78 / 0.79 | 0.91 / 0.92 | 0.92 / 0.91 | correct assessment |
| `evidence_outage` | 0.83 / 0.83 | 0.86 / 0.87 | 0.90 / 0.88 | correct assessment |
| `evidence_conflict` | 0.03 / 0.04 | 0.07 / 0.07 | 0.22 / 0.23 | correct clarification |
| `evidence_resolved_history` | 0.89 / 0.90 | 0.93 / 0.93 | 0.94 / 0.94 | correct assessment |
| `evidence_billing_unknown` | 0.08 / 0.08 | 0.21 / 0.23 | 0.19 / 0.17 | correct clarification |
| `evidence_calm_outage` | 0.81 / 0.80 | 0.87 / 0.87 | 0.91 / 0.91 | correct assessment |
| `evidence_emotional_normal` | 0.80 / 0.82 | 0.77 / 0.78 | 0.95 / 0.95 | correct assessment |
| `evidence_partial_checkout` | 0.86 / 0.85 | 0.92 / 0.93 | 0.92 / 0.92 | correct assessment |
| `evidence_detailed_nonfunctional` | 0.13 / 0.12 | 0.34 / 0.33 | 0.16 / 0.17 | correct clarification |
| `policy_partial_unknown` | 0.07 / 0.08 | 0.11 / 0.10 | 0.24 / 0.21 | correct clarification |
| `policy_history_current` | 0.88 / 0.87 | 0.90 / 0.90 | 0.94 / 0.94 | correct assessment |
| `policy_conflict_current` | 0.04 / 0.04 | 0.09 / 0.09 | 0.19 / 0.18 | correct clarification |
| `policy_regional_partial` | 0.67 / 0.63 | 0.90 / 0.91 | 0.92 / 0.93 | correct assessment |
| `policy_recovery_unverified` | 0.03 / 0.03 | 0.07 / 0.07 | 0.11 / 0.12 | correct clarification |
| `policy_complete_calm` | 0.84 / 0.85 | 0.91 / 0.91 | 0.92 / 0.92 | correct assessment |

Each cell shows Java / Sidecar. The final wording produced 20 correct assessments and 16 warranted clarifications across these contacts. For insufficient evidence, a returned impact score is retained only for envelope fidelity.

The first revision fixed both original deferrals. It introduced two unnecessary clarifications on the angry billing contact that explicitly reported normal functioning. The final question asks for current operational evidence independent of the complaint’s tone or subject. That contact scored 0.95 on both hosts. No other contact lost a correct application decision in the final sample.

Five evidence probabilities exceeded the provisional 0.20 upper bound for insufficient evidence. The vague symptom scored 0.21 on Sidecar, the conflicting reports scored 0.22 / 0.23, and the untested CSV failure scored 0.24 / 0.21. All five still called for clarification at 0.80.

This is a comparison on reused contacts and earlier results informed the wording. It establishes observed behavior on these cases, not general calibration, independent validation or a probability of success on future contacts.

## Capture evidence

* The scope wording passed 756 mechanical checks and used 19,875 input and 1,332 output tokens. [batch 1](../evidence/typesafe-partial-outage-live/typesafe-ai/summary.md), [batch 2](../evidence/typesafe-partial-outage-continuity/typesafe-ai/summary.md), [batch 3](../evidence/typesafe-partial-outage-holdouts/typesafe-ai/summary.md).
* The final wording passed 756 mechanical checks and used 20,729 input and 1,332 output tokens. [batch 1](../evidence/typesafe-partial-tone-1/typesafe-ai/summary.md), [batch 2](../evidence/typesafe-partial-tone-2/typesafe-ai/summary.md), [batch 3](../evidence/typesafe-partial-tone-3/typesafe-ai/summary.md).

All capture checksums, send counts, request/response fidelity and provider-disabled restoration were verified. Dollar cost was not returned. The original reference pack remains intact. The active evidence cases use a separately checksummed pack of responses to the final question.

The full provider-disabled replay passed all 124 scenarios per host (248 executions and 5,144 checks). [Replay summary](../evidence/typesafe-partial-outage-replay/typesafe-ai/summary.md).
