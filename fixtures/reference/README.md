# Accepted deterministic reference

This is the final passing Sol/Luna batch `f11193ccd3024844bb38cc69d53e0d2c`:
four Java assessment cases, 60 responses, six Sol judgment skills and two Luna
coordinators at medium reasoning. Its business review passed with minor caveats,
retained in `manifest.json`. This is a test fixture, not a perfect business oracle.

The batch was recovered from the verified Phase 2 recovery snapshot after the user
requested deterministic testing. The original bundle and report hashes establish
provenance; every frozen case file has a checksum. No external recovery directory is
needed to run these tests. Historical experiments and credentials are not included.

Run from the workspace root after starting the documented runtime:

```powershell
.venv/Scripts/python.exe scripts/run_suite.py mock
.venv/Scripts/python.exe scripts/run_suite.py mock --path java --scenario baseline
```

Default coverage is baseline, priority, capacity_shortfall and later_start on both
Java and Python/Sidecar. Each run creates fresh case and quote identities, preserves
prior database rows, and never creates service commitments. Outputs go to
`evidence/latest`; they never overwrite this directory. The provider remains disabled.

Recorded response content is preserved, except replacing the original case ID with
the fresh case ID (also used in quote IDs). Provider billing/usage and envelope IDs
are replaced with explicit offline values. No new model judgment is generated.

Matching checks model/reasoning, skill, canonical mission input, assigned task and
completed-task evidence. JSON key order and nested JSON encoding are insignificant;
completed-task collection order is sorted by task identity because parallel completion
order is not meaningful. Other arrays and business values remain exact. Runtime plan
UUIDs, progress timestamps and explanatory framework scaffolding are not matched.
Authored skill contracts, effective assignments and source facts are checked separately.
Contract/source hashes use parsed content so JSON/YAML formatting is insignificant;
frozen fixture file hashes are byte-exact, with LF endings pinned for cross-platform checkouts.
All responses must be consumed exactly once and the complete final result must match.

Changed inputs or contracts fail closed. Updating fixtures requires a separately
reviewed capture and explicit promotion; `scripts/freeze_reference.py` verifies the
matching accepted review and checksums and refuses an existing destination. Neither
`mock` nor a paid run automatically changes the accepted fixture. Do not delete this
pack as part of historical-output cleanup.

This suite covers the assessment workflow and Java/Sidecar equivalence for these
fixed responses. It does not evaluate current provider behavior, prove new reasoning,
or replace future service-request and release-confidence coverage.
