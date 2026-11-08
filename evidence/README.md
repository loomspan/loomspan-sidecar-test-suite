# Integration verification evidence

Organize new reports by capability, suite or deployment recipe, not PR number.
See the [coverage map](../docs/coverage.md) for the maintained verification entry
points. Existing report names remain provenance; they do not define active coverage.
Business reports identify the selected scenarios and runtime artifacts. SDK reports
under `sdk/` identify their language/recipe and artifact identities separately.
An unrun capability is not implied to pass by another report.

Historical Phase 1 and Phase 2 results, traces and accepted samples were retired after
verified external recovery snapshots. The retained conclusions are in the phase summaries.
No capture is needed to start the runtime or run provider-free checks.

For business regression or separately authorized live evaluations, the runner writes `latest/<suite>/report.json`,
`latest/<suite>/summary.md` and `latest/<suite>/bundle.zip`, with a selection index at
`latest/summary.md`. Named output directories must be new.
Results are not automatically accepted or promoted. Keep secrets out of artifacts.
See the [runner guide](../docs/runner.md). This directory authorizes no paid activity.

The current accepted deterministic replay pack lives in `fixtures/reference-namespaced`, outside
replaceable run output. `run_suite.py mock` writes fresh replay results here but
cannot overwrite the frozen pack. Preserve both it and its original review source
in `fixtures/reference` during historical cleanup.

TypeSafe mock evidence lives separately under `latest/typesafe-ai`. Its fixture pack
includes authored `fixtures/typesafe-ai/cases.json` plus the separately reviewed
real responses in `fixtures/typesafe-ai/reference`. Preserve both maintained packs.
`PROTOCOL_PASS` establishes integration fidelity, not a new model judgment.
Question-level semantic acceptance is recorded in the reference review, separately
from capture reports. `mock --suite all` groups native and equipment evidence explicitly.
