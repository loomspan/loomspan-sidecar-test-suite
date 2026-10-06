# PR 22/23 output binding baseline

Current identity: `post-pr23-output-bindings-reviewfix-20261005`; exact files and artifacts in
[the manifest](post-pr23-baseline.json). Framework commit `d9c0ff3` includes PR22
output assembly, PR23 shared output validation and cleanup. Both hosts package the
installed snapshot; Sidecar production packaging skips its known obsolete tests.

`compareOptions` binds caseId, assetId, quotes and equipmentAssessment from input;
its model generates the remaining decision fields. `resolveEquipment` binds IDs
from input, equipmentAssessment from assessEquipment and remaining fields from
planResolution. Its closed output is fully bound, eliminating final synthesis.
`planResolution` continues forwarding compareOptions through output_from.

Schemas, business facts, decision criteria and 480/2400/510-second limits stay fixed.
Only copy-ownership instructions change. Evaluators now read accepted RESULT_ASSEMBLED
values, check exact source provenance and model contribution, and prove root synthesis
is absent. The same business checks still apply; legacy review remains supported.
PR23 also unifies output validation policy (format is guidance, without coercion).

[PR21](post-pr21-baseline.md) and [PR20](post-pr20-baseline.md) remain frozen.
Previous sources and runtime were preserved under
`evidence/pr23-adoption-20261005`; two pre-existing Java formatting changes were
retained (identical token sequences to PR21). Sol medium remains the historical
reference, not a new PR23 run. Luna Java/medium is the first authorized comparison.
No replay promotion or general reliability claim follows from a single run.

The paid Luna run used initial identity `post-pr23-output-bindings-20261005`.
Its manifest and evaluator are preserved in
`evidence/pr23-adoption-20261005/initial-evaluator`. After execution, a chunked text
payload double-decode bug in the new reviewer was fixed with a regression test.
The current identity records only that reviewer/test correction; runtime artifacts,
skills and business criteria are unchanged. Original reports were not rewritten.
[Observed Luna result](../evidence/pr23-adoption-20261005/summary.md): 66/67 baseline,
67/67 priority after offline review, exact output preservation in both; not replay
approved. Both hosts are ready and provider-disabled.
