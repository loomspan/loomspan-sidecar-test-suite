# Evaluation output

Historical Phase 1 and Phase 2 results, traces and accepted samples were retired after
verified external recovery snapshots. The retained conclusions are in the phase summaries.
No capture is needed to start the runtime or run provider-free checks.

For separately authorized future evaluations, the runner writes `latest/report.json`,
`latest/summary.md` and `latest/bundle.zip`. Named output directories must be new.
Results are not automatically accepted or promoted. Keep secrets out of artifacts.
See the [runner guide](../docs/runner.md). This directory authorizes no paid activity.

The accepted deterministic response pack lives in `fixtures/reference`, outside
replaceable run output. `run_suite.py mock` writes fresh replay results here but
cannot overwrite the frozen pack. Preserve that pack during historical cleanup.
