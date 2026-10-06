# Post-PR-20 comparison baseline

Baseline ID: **post-pr20-20261004**. Accepted configuration, recorded 2026-10-04.
Start at [README](../README.md); observations live only in the
[current results table](implementation-status.md). This baseline is not full acceptance.

## Identity and fixed configuration

The machine-readable [identity manifest](post-pr20-baseline.json) freezes artifact,
application, configuration, fixture, evaluator and test SHA-256 identities from the
existing uncommitted working tree. The suite commit alone does not identify this
baseline. Compare these hashes before a future run and record any difference as a
new baseline; documentation-only edits do not change the evaluation identity.

- Framework: beta.8-SNAPSHOT, PR 20, commit
  `cb37a28e0acf892744c2bbafd6c7cb657be757b1`.
- Installed starter SHA-256:
  `501464a9e33256fc0690bdec5bb2d852f5de51215e0184d33681597f379a2e9d`.
- Java JAR SHA-256:
  `24b8b176ecb55939a46158f73227b24a7aa526a65691719b1f3116399cb0f3d3`.
- Sidecar JAR SHA-256:
  `d211274ae988cee78b86c55f2420ccf21aa58d38daa1108b274d89b7f74e88ad`.
- Sidecar beta.2 source commit `da3bb8f8ae6087955f9b3a6bd02b9706d3b582e7`,
  rebuilt with the local Framework snapshot; not a released Sidecar binary.
- Default: `meta/muse-spark-1.3-contributor`, medium reasoning.
- Shared limits: provider **480s**, mission **2400s**, proxy upstream read **510s**;
  session maximum **400000 usage units**. Model comparisons retain these limits.
- Strengthened normal input contracts remain in force. `planResolution` uses
  `output_from: {skill: compareOptions}`, with no duplicate output schema/retry
  policy or final-copy instruction. `resolveEquipment` retains ordinary synthesis.

The original historical verification captures were discarded by the user during
the evidence reset. The frozen manifest here retains the configuration identity.
The mutable `.runtime/build-baseline.json` describes installed packages; fresh
run captures record the deployed identity independently.

## Scenarios and evaluator

Use **scripts/run_suite.py** as the supported evaluation entry point. `evaluate`
selects one integration (Java by default); `live` selects both. Each runs the existing
baseline and changed-priority assessments, followed by deterministic service
approval/recovery when the baseline permits it. Fixed cases, source facts, quote
rules and expectations are identified in the manifest, not redefined here.

The evaluator checks execution, evidence transfer, issued quote IDs/citations,
published results, caller identity and Framework traces. It includes the accepted
model-independent quote-ID and joined-execution-unit corrections, and verifies
exact PR 20 forwarding with completed accepted work. Synthetic negative cases
reject changed text, wrong task/plan, incomplete work, early/missing forwarding and
duplicate results. Automated counts are diagnostic assertions, not accuracy scores.
Semantic review separately assesses feasibility, access hours and elapsed work,
commercial constraints, uncertainty, alternatives and response to priority.

`mock` retains the first-delivery scenario groups: baseline, changed priority,
malformed-output recovery, service creation/recovery, gated isolation and nested
authorization. **Historical replay is incompatible with current contracts.**
Its old successes cannot establish current mock acceptance. Replay migration and
full mock acceptance are separate future work requiring suitable reviewed captures,
preserved provenance and complete validation. `capture` never approves replay by itself.

## Known gaps and comparison boundary

- Fresh Java Sol, Muse, GLM Flash, non-Flash GLM, Luna and DeepSeek runs are recorded in current results.
  Full Pro was also evaluated via `~deepseek/deepseek-pro-latest`, resolving to
  V4 Pro 0813: baseline missed commercial citations; priority failed on an upstream
  network error inside HTTP 200. The earlier no-tilde rejection was not a model result.
  Final selected MiMo comparison: baseline provider timeout; priority malformed
  compareOptions tool-call JSON after correction; neither produced a final recommendation.
  The user-designated [Sol reference](model-reference.md) passed its automated suite
  and received separate comparison review; it is not replay-approved.
  Both GLM Flash executions failed; non-Flash GLM completed baseline but failed
  priority. Muse completed but its baseline citation check failed.
  Luna completed both, but changed a source contact in baseline and made calendar
  and access errors in priority despite that scenario's mechanical pass.
  DeepSeek completed both with source-contact changes at assessment input and
  continuity/access planning gaps; neither scenario passed all mechanical checks.
  Neither suite establishes full acceptance or repeated reliability.
- Muse's service-work access reasoning remains unsound: arrival during access
  hours does not ensure 2–4 hours of work finish before closing. The fresh Sol reference
  handles this constraint correctly. Captures remain unapproved for replay.
- Forwarding verification covers a model child on both hosts; it does not establish
  the complete Framework forwarding matrix. Outer synthesis can still alter results.
- Sidecar beta.2 tests use the obsolete `SkillDescriptor` constructor. Production
  compiled; packaging used `-Dmaven.test.skip=true`. Its own tests were not run.
- Full mock acceptance and service creation were not rerun in PR 20 verification.

The selected Java comparison set is complete: Sol reference, Muse, GLM Flash,
non-Flash GLM, Luna, DeepSeek Flash, full Pro and MiMo. See current results. Review
aggregate outcomes before further paid work. Selected Sidecar confirmation and
replay migration/full mock acceptance remain separate future work. Keep profiles,
contracts and criteria fixed unless the user explicitly selects a new baseline.
