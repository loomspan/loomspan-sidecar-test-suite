# Live TypeSafe executor review, November 17, 2026

All 26 predeclared contacts ran once through embedded Java and once through Python/Sidecar with the actual TypeSafe API and pinned model `jev-1.13.0`. The five capture bundles passed checksum verification. Each case consumed one durable permit, made one upstream send and retained the exact executor request and full provider response. All 1,044 mechanical checks passed. Provider access was restored after each batch. There were zero chat calls.

| Batch | Live sends | Input tokens | Output tokens |
|---|---:|---:|---:|
| [primitives](../evidence/typesafe-executor-live-primitives/typesafe-ai/summary.md) | 12 | 5,284 | 586 |
| [evidence](../evidence/typesafe-executor-live-evidence/typesafe-ai/summary.md) | 12 | 5,865 | 444 |
| [holdouts](../evidence/typesafe-executor-live-holdouts/typesafe-ai/summary.md) | 12 | 5,943 | 444 |
| [policy](../evidence/typesafe-executor-live-policy/typesafe-ai/summary.md) | 12 | 5,979 | 444 |
| [routing](../evidence/typesafe-executor-live-routing/typesafe-ai/summary.md) | 4 | 1,906 | 300 |
| **Total** | **52** | **24,977** | **2,218** |

The API returned token counts. Monetary cost was not reported.

## Semantic review

Choice, Noul, Score, mixed, dynamic and structured cases passed the predeclared mechanical contract on both hosts. The duplicate charge routed to billing. Both hosts selected delivery for the competing lost-parcel/refund contact, with meaningful probability on billing (0.43 Java and 0.30 Sidecar). The marketing preference went to other on both hosts. The structured contact saying only “It doesn't work” yielded raw impact scores of 1.55 and 1.70. Its actual functional scope is indeterminate and those scores are excluded from semantic acceptance.

At the application’s 0.80 evidence threshold, 16 of the 36 evidence-bearing executions produced a correct assessment, 16 correctly requested clarification and four unnecessarily requested clarification. All exposed impact scores fell within the predeclared range. The four unnecessary clarifications came from two contacts, each observed once on both hosts. In the six scenarios specifically labeled for policy evaluation, the counts were four correct assessments, six correct clarifications and two unnecessary clarifications.

The CSV export failure with browsing, editing and saving working scored 1.00 for raw impact on both hosts. The regional outage scored 1.16 and 1.21. Both contacts justified partial impact under the rubric, but the evidence probabilities fell below threshold. The regional deferral also occurred in the earlier evaluation. No fixtures, model prompts or thresholds were changed. This sample supports integration fidelity and identifies two concrete evidence-policy misses. It does not measure general accuracy or establish a better threshold.

| Evidence or policy contact | Evidence probability, Java / Sidecar | Raw impact, Java / Sidecar (0–2) | Application outcome on both hosts |
|---|---:|---:|---|
| `evidence_sparse` | 0.04 / 0.04 | 1.41 / 1.66 | Correct clarification |
| `evidence_urgent` | 0.02 / 0.02 | 0.42 / 0.48 | Correct clarification |
| `evidence_normal` | 0.86 / 0.89 | 0.00 / 0.00 | Correct assessment |
| `evidence_partial` | 0.78 / 0.79 | 1.00 / 1.00 | Unnecessary clarification |
| `evidence_outage` | 0.83 / 0.83 | 2.00 / 2.00 | Correct assessment |
| `evidence_conflict` | 0.03 / 0.04 | 1.55 / 1.55 | Correct clarification |
| `evidence_resolved_history` | 0.89 / 0.90 | 0.00 / 0.00 | Correct assessment |
| `evidence_billing_unknown` | 0.08 / 0.08 | 0.66 / 0.43 | Correct clarification |
| `evidence_calm_outage` | 0.81 / 0.80 | 2.00 / 2.00 | Correct assessment |
| `evidence_emotional_normal` | 0.80 / 0.82 | 0.00 / 0.00 | Correct assessment |
| `evidence_partial_checkout` | 0.86 / 0.85 | 1.00 / 1.00 | Correct assessment |
| `evidence_detailed_nonfunctional` | 0.13 / 0.12 | 0.53 / 0.43 | Correct clarification |
| `policy_partial_unknown` | 0.07 / 0.08 | 1.00 / 1.00 | Correct clarification |
| `policy_history_current` | 0.88 / 0.87 | 0.00 / 0.00 | Correct assessment |
| `policy_conflict_current` | 0.04 / 0.04 | 1.39 / 1.46 | Correct clarification |
| `policy_regional_partial` | 0.67 / 0.63 | 1.16 / 1.21 | Unnecessary clarification |
| `policy_recovery_unverified` | 0.03 / 0.03 | 1.02 / 1.09 | Correct clarification |
| `policy_complete_calm` | 0.84 / 0.85 | 1.99 / 1.99 | Correct assessment |

Raw scores for insufficient evidence are retained for response fidelity. The application withholds those scores from its impact decision.
