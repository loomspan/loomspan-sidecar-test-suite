# Continuation handoff

Current direction: the user has declared **Phase 1 Framework exploration complete**
and moved to **Phase 2 skill-level optimization**. Explore how skills are composed,
used and optimized to improve success with models below Sol's demonstrated capability.
Discuss experiment design next; no particular skill change or new paid run has been
selected by this phase transition. Preserve Phase 1 evidence and comparison anchors.
Phase 3 will stabilize the suite for long-term regression and release confidence;
exhaustive coverage and acceptance criteria remain future work. See the
[agreement](project-agreement.md#three-phase-direction--agreed-2026-10-05).

Latest: [Sol and MiMo PR24/25 verification](../evidence/pr25-sol-mimo-20261005/summary.md)
is complete. Four scenarios each use seven model calls/eight direct dispatches with
43 exact input/18 output bindings, no correction and exact publication. Sol 67/67 both;
MiMo baseline 67/67, priority original 63/67 due to a fenced-plan parsing mismatch in
the reviewer, separately verified 67/67 against the accepted trace plan. Both service
suites 33/33. Evaluator and original evidence unchanged.
Sol cost falls 67.68% versus PR20 (multiple contract changes), MiMo 39.91% versus PR23.
Sol preserves business distinctions; MiMo still has access/commercial/authorization
advice errors despite better priority overrun planning. Historical Sol reference remains
unchanged. No replay approval. Runtime ready/provider-disabled, prior work/evidence
preserved. No additional paid run, replay refresh, commit, push or release authorized.

Previous: [Luna live PR24/25 verification](../evidence/pr25-luna-20261005/summary.md)
is complete: 67/67 both scenarios and 33/33 service, eight direct dispatches and seven
model calls per scenario, exact 43 input/18 output bindings. Total reported cost falls
32.02% versus PR23 Luna; total trace time rises 2.08%. Citation coverage improves,
but both outputs omit technician-overrun access planning. No replay approval.
Runtime ready/provider-disabled, existing work and prior evidence preserved. No further
paid evaluation, replay refresh, commit, push or release is authorized.

Previous: [PR24/25 adoption](../evidence/pr25-adoption-20261005/summary.md) is complete
without paid model calls. Both hosts use `7d47269`; offline controlled cases verify
eight direct dispatches, seven retained model interactions, exact input/output bindings
and corrected optional-argument guidance. [Current baseline](post-pr25-baseline.md).
PR23 source/jars/evidence preserved. Runtime ready/provider-disabled. No replay approval
or fresh model comparison; the next paid model needs explicit authorization.

Previous: [MiMo on PR22/23](../evidence/pr23-mimo-20261005/summary.md) is complete:
67/67 both scenarios, 33/33 service, 43 exact input and 18 exact output bindings
per scenario, no root synthesis. Baseline completes where PR21 failed; priority
recovers one unknown argument field. Semantic gaps remain: technician-overrun
access omitted, priority cap/premium ambiguity, and service-approval misrouting.
No replay approval. Runtime restored/provider-disabled; existing work and frozen
evidence preserved. No further evaluation or behavior changes are authorized.

Previous: [PR22/23 adoption and Luna](../evidence/pr23-adoption-20261005/summary.md) are complete.
Both scenarios verify 43 input and 18 output bindings, exact final preservation and
no root synthesis. Corrected review is 66/67 baseline (missing W-2 citation), 67/67
priority (semantic technician-access gap persists). One optional candidateReasoning
JSON correction in baseline; service skipped. A chunked-payload reviewer bug was
fixed offline; original reports and evaluator remain intact. Both hosts use the
[new baseline](post-pr23-baseline.md); runtime restored/provider-disabled. No other
model or replay work is authorized. Discuss these results before further changes.

Previous: [both DeepSeek PR21 evaluations](../evidence/pr21-deepseek-20261005/summary.md)
are complete. Flash 66/67 both (missing W-2 citations); Pro 67/67 baseline, 64/67
priority (minor root preservation edits), 33/33 service. All four scenarios verify
43 exact bindings. Business review remains necessary: Pro baseline has approval/access
errors, Flash omits technician late-access reasoning. No replay approval.
Runtime restored/provider-disabled. Discuss before further work.

Previous authorized run: [GLM-5.3-Flash on PR21](../evidence/pr21-glm-flash-20261005/summary.md).
Baseline completed 61/67 (four fenced-plan review parsing failures plus two real
root-preservation failures); priority timed out at comparison after recovering a
bound-override attempt. Both verify 43 exact bindings. Service checks skipped.
Runtime is restored/provider-disabled. Discuss before further paid work or changes.

PR 21 adoption on 2026-10-05 supersedes the active PR 20 configuration described
below. See [the binding baseline](post-pr21-baseline.md). GLM-5.3 is the first
authorized Java comparison and is now complete (67/67 both scenarios, 33/33 service).
Bindings preserve source evidence, but semantic gaps remain. Read the
[PR 21 GLM review](../evidence/pr21-adoption-20261005/summary.md). The subsequently
authorized Luna run is complete: 67/67 baseline, 65/67 priority, 33/33 service.
Bindings are exact, but priority root rewording violates preservation and technician
access remains incomplete. Read the [Luna review](../evidence/pr21-luna-20261005/summary.md)
before further changes or paid runs. MiMo is now also complete: baseline failed on
malformed optional reasoning, priority passed 67/67 with exact bindings and final
preservation, and service follow-up was skipped. Read the
[MiMo review](../evidence/pr21-mimo-20261005/summary.md) for remaining cost/expiry wording
issues. The selected PR21 set is complete; discuss before any further paid run.
Historical captures and the Sol reference remain unchanged.

Read [README](../README.md), [current agreement](project-agreement.md) and
[current results](implementation-status.md) first. For scenario work, read both
customer-facing claims documents and the business source pack. The agreed scope
is two equivalent reference microservices, with assessment and approval-bound
request creation ending at `PENDING_DISPATCH`.

The normal skills now use the model-independent [audited contracts](input-contract-audit.md).
Do not restore the old experimental overlay or tune prompts per model. `planResolution`
now forwards `compareOptions` through `output_from`; the outer parent still synthesizes. The current
Framework is the installed PR 20 snapshot; exact build identity is captured in
`.runtime/build-baseline.json` and each run's evidence.

Use the [frozen PR 20 baseline](post-pr20-baseline.md) and
the user-designated [Sol comparison reference](model-reference.md), evaluated once
on embedded Java. A separate paid Sidecar run is not required to establish it. Use
`scripts/run_suite.py` with [run modes](run-modes.md) for new work. Compare additional models on the same
baseline and record profile differences. Review completion, source fidelity,
business judgment, latency, corrections and provider failures separately. A good
live result still needs bound semantic review and full mock acceptance before
becoming the active replay fixture.

Historical replay and acceptance scripts depend on old captures discarded during
the user-authorized evidence reset. Their old passing counts are not current
acceptance. Future migration must bind new provenance and fail closed; do not loosen
checks to activate a candidate.
Keep any remaining blocker explicit in implementation status.

The user selected two or three further model comparisons before replay migration.
Non-Flash `z-ai/glm-5.3`, `openai/gpt-6-luna` and `deepseek/deepseek-v4.1-flash`
have now run on Java. See current results for execution, fidelity and semantic
findings. This completes the three selected additional comparisons. Do not replace
the Sol reference or activate replay without the separate migration work.

The user subsequently selected full DeepSeek Pro. Its leading tilde is required:
`~deepseek/deepseek-pro-latest` resolved to `deepseek/deepseek-v4-pro-0813` and has
now run on Java. Baseline missed citations; priority failed on an Ionstream nested
502 network error. The earlier attempt without the tilde was an assistant identifier
interpretation error and is not a model-quality result.

The user's final selected comparison, `xiaomi/mimo-v2.6-pro`, has run at medium
reasoning on Java. Baseline timed out at assessEquipment; priority exhausted one
correction for malformed compareOptions tool-call JSON. No final recommendation.
The selected comparison set is complete; review aggregate results before further
paid work. Sol remains the reference; replay migration and selected Sidecar
confirmation remain separate future work.

Preserve runtime evidence and durable records before recreation. Restore provider-
disabled normal services after live work. Retain the fresh comparison captures while they are the current baseline. The
user superseded retention of older source captures; those have been discarded. Superseded decisions, run
recipes and investigations are in the [archive](../archive/2026-10-04-before-muse-baseline/README.md),
not instructions for the next run. No broad delivery claim, commit, push or release
follows automatically from this handoff.
