# Evaluation output

Historical Phase 1 and Phase 2 results, traces and accepted samples were retired after
verified external recovery snapshots. The retained conclusions are in the phase summaries.
No capture is needed to start the runtime or run provider-free checks.

For separately authorized future evaluations, the runner writes `latest/<suite>/report.json`,
`latest/<suite>/summary.md` and `latest/<suite>/bundle.zip`, with a selection index at
`latest/summary.md`. Named output directories must be new.
Results are not automatically accepted or promoted. Keep secrets out of artifacts.
See the [runner guide](../docs/runner.md). This directory authorizes no paid activity.

The accepted deterministic response pack lives in `fixtures/reference`, outside
replaceable run output. `run_suite.py mock` writes fresh replay results here but
cannot overwrite the frozen pack. Preserve that pack during historical cleanup.

TypeSafe mock evidence lives separately under `latest/typesafe-ai`. Its fixture pack
includes authored `fixtures/typesafe-ai/cases.json` plus the separately reviewed
real responses in `fixtures/typesafe-ai/reference`. Preserve both maintained packs.
`PROTOCOL_PASS` establishes integration fidelity, not a new model judgment.
Question-level semantic acceptance is recorded in the reference review, separately
from capture reports. `mock --suite all` groups native and equipment evidence explicitly.
