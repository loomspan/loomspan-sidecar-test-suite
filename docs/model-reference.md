# Sol comparison reference

The user selected **Sol 6.1, medium reasoning, embedded Java only** as the
reference for comparing other models on the fixed [post-PR-20 baseline](post-pr20-baseline.md).
Reference ID: **sol-6.1-medium-java-20261004**. Recorded 2026-10-04.
The [machine-readable record](model-reference.json) binds the original suite report,
capture manifests, frozen baseline, semantic review and final integrity validation
by SHA-256. [Detailed review](../evidence/sol-reference-20261004/summary.md).

Both baseline and priority completed with **67/67 mechanical checks** and 16 model
requests each; deterministic service approval/recovery passed **33/33** with no
additional model requests. There were no corrections or provider failures.
Reported provider cost: **$1.2971662** total. Root trace durations were 537.534 seconds
for baseline and 492.740 seconds for priority, excluding capture/restoration overhead.

The semantic review found the recommendations suitable as a comparison reference.
Both favor loaner plus standard investigation with separately verified approvals,
access and readiness. Both account for expedited work potentially ending at 20:00,
after the 18:00 access cutoff, and distinguish elapsed work from billable repair
hours. The baseline explicitly leaves cost/risk preference unresolved; priority
explicitly favors continuity despite cost. Other justified choices remain possible.
The priority text's word “scheduled” describes an offered loaner window; its explicit
unreserved/conditional qualifications must be retained when interpreting it.

All five services were restored ready/provider-disabled. All 139 frozen files and
deployed artifact identities remain unchanged; 115 captured files passed checksum
verification. Prior business rows are intact; Java added two assessments, four quotes
and one approved request. Python records are unchanged.

Provider route: OpenRouter; requested model `openai/gpt-6.1-sol`. The normal runtime
default remains Muse. This reference does not require another paid Sidecar run.

Use the same scenarios, contracts, evaluator and 480/2400/510-second limits for
comparisons. Assess execution, evidence fidelity and business judgment separately
in the [current results](implementation-status.md). Compare whether the recommendation
is justified and feasible; a different selected option is not automatically wrong.
The source facts and independent criteria remain authoritative.

This is a retained empirical comparison reference, not an approved replay fixture.
Historical replay remains incompatible with current contracts. Replay migration,
full mock acceptance and selected Sidecar confirmation are separate future work.
