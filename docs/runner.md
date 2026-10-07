# One runner, four modes

Use `scripts/run_suite.py`. Edit the current skills directly; use Git for accepted
improvements and targeted rollback. There are no experiment variants to register.

| Mode | Scope |
|---|---|
| `evaluate` | Selected scenarios on one integration; Java by default, or `--path sidecar`. |
| `live` | Selected scenarios on both integrations, sequentially, using the selected real model. |
| `capture` | Same execution as live, with an explicit unreviewed candidate-review document. No automatic fixture approval. |
| `mock` | Reserved provider-free regression mode. Currently exits with UNAVAILABLE (code 2): compatible approved fixtures/replay support are not established. No runtime changes or paid fallback. |

The default scenarios are `baseline` and `priority` assessments. Both are selected
by default; repeat `--scenario` to select cases. Optional Phase 2 variations are
`capacity_shortfall` (priority with a 25/minute capacity need) and `later_start`
(baseline with a September 30 16:00 production start). These change mission inputs
only; their expected business implications are defined in the project agreement,
and business review remains manual. Inputs and checks live in
`scripts/scenarios.py`, separately from orchestration. Full service-request regression
is not part of this first runner; `scripts/smoke.py` remains the independent foundation check.

## Preview without running

```powershell
.venv/Scripts/python.exe scripts/run_suite.py --help
.venv/Scripts/python.exe scripts/run_suite.py evaluate --model provider/model --dry-run
.venv/Scripts/python.exe scripts/run_suite.py capture --model provider/model --scenario priority --dry-run
.venv/Scripts/python.exe scripts/run_suite.py mock
```

Dry-run selection requires no provider key and touches no services or records.
There is no automatic model fallback. Real runs require explicit authorization and
`LOOMSPAN_OPENROUTER_API_KEY` in the process environment; never put the value in a report.

```powershell
# Only after authorizing a paid run and setting the provider key privately:
.venv/Scripts/python.exe scripts/run_suite.py evaluate --model provider/model --reasoning medium
.venv/Scripts/python.exe scripts/run_suite.py evaluate --path sidecar --model provider/model --scenario priority
.venv/Scripts/python.exe scripts/run_suite.py live --model provider/model --reasoning none
.venv/Scripts/python.exe scripts/run_suite.py capture --model provider/model
```

The runner acquires one workspace lock, checks readiness and running JAR identities,
makes temporary model/reasoning overrides without editing authored files, and checks
the mounted configuration. It restores normal provider-disabled configuration in
`finally`, including after startup failure, execution error or keyboard interruption.
The temporary overlay is not an experiment variant and is removed after use.
It refreshes login between cases and never automatically retries a failed paid scenario.

Do not edit skills, rebuild hosts or run smoke/start tools concurrently with an evaluation.
A killed process or machine failure can bypass cleanup: check running processes before
removing a stale `.runtime/run-suite.lock`, and use `scripts/start.py` to restore the
normal configuration. A report with `runtimeRestored: false` requires restoration;
it is never reported as a successful run.

## Results and retention

By default, the next run replaces these three files in `evidence/latest`:

- `summary.md`: compact checks, usage and manual-review areas.
- `report.json`: execution/check status, model selection, identities and hashes.
- `bundle.zip`: matching report, checksums, source/effective configuration, case inputs,
  provider journal, raw correlated traces, accepted plans, terminal output and case-specific
  persisted business records. Capture also includes `candidate-review.json` marked UNREVIEWED.

The ZIP is self-contained and checksummed. A newer report does not alter a previous
accepted result. When accepting an improvement, save those three files in a manually
maintained `evidence/accepted` directory before the next run. Keep latest plus accepted;
no permanent history of every unsuccessful attempt is required. For a result that must
not replace latest, `--output NEW_DIRECTORY` writes a separate result and refuses an
existing directory. There is no automatic retention or fixture-promotion service.

Checks cover completed execution, exact issued quotes, persisted publication, accepted
assessment/comparison result preservation, unchanged prior rows, no service commitment,
model selection and provider request/response pairing. Nine added checks verify
the original incident, each published option result, and its source metadata
against traced inputs/results. A portfolio check verifies valid, unique pursued
options and consistency with the primary selection (empty for defer/undecided).
Four service checks also verify dedicated condition fields and owner references
against the exact source contact directory. Role meaning remains manual review.
Offer metadata is checked against the complete record in the assessor's context.offer;
the public output retains offerExpiresAt, offerReserved and offerSourceId. Full business
review includes deferred findings and any explicit governing corrections in reviewConcerns.
The current total is 27 checks per case without claiming semantic correctness.
The bundle contains accepted
Framework plans; raw fenced model JSON is not misclassified as a planning failure.
This is not the retired comprehensive binding auditor or a Phase 3 release suite.

`CHECKS_PASS_REVIEW_REQUIRED` (exit 0) means these automated checks passed, not that the
recommendation is correct. `FAIL` (exit 1) includes execution, collection, preservation
or restoration failures. Usage includes observed calls, rejected actions, failed model
attempts, direct dispatches, token counts, reported cost and trace duration. Missing
usage is unknown, not zero. Review business reasoning independently and use repeated
observations when deciding whether a change is a real improvement.

The current `failedModelAttempts` and `planRetries` counters do not include output
schema-advisor corrections. Inspect `ADVISOR_REQUEST_MUTATION_RECORDED` events with
`kind: retry_requested` when explaining extra model calls; record these separately
in the business review. Valid raw JSON can still violate the output schema.

## Implementation verification

```powershell
.venv/Scripts/python.exe -m pytest tests/test_runner.py -q
```

Thirty-eight provider-free tests verify selection, safe overrides, lock handling, restoration
after failures/interruption, evidence integrity and credential rejection, preservation
checks, fenced-response tolerance and CLI report publication using simulated services.
No real provider run was performed as part of implementing the runner.


Per-skill experiments can add repeatable `--skill-model SKILL=PROVIDER/MODEL`
arguments to the default `--model`. Overrides apply only to temporary manifests and
model aliases on either integration; authored skills remain unchanged. The report
records `skillModels`, the bundle captures effective configuration, and mixed-run
checks validate each trace request's skill/model pair and provider model counts.
All assignments share the selected `--reasoning` setting. These options do not
authorize paid execution by themselves.
