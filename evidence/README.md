# New experiment results

Phase 1 captures and archives were retired after an external verified recovery snapshot.
This directory is reserved for new Phase 2 results. No historical captures are required
to start either app or run the provider-free smoke check.

The shared runner writes `latest/report.json`, `latest/summary.md` and `latest/bundle.zip`,
replacing those files on the next run. Keep the last accepted result separately in
`accepted` when a change is accepted. Named `--output` directories must be new.
There is no experiment registry or automatic capture promotion.

Distinguish automated checks from business review, and never store credentials.
No model run is authorized by this directory's presence. See [runner guide](../docs/runner.md).
