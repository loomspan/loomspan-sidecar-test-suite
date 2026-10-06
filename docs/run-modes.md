# Model run modes

Start at [README](../README.md). Use `scripts/run_suite.py` as the supported
evaluation entry point on the [post-PR-20 baseline](post-pr20-baseline.md). Other
capture/review scripts below are implementation or maintenance helpers, not alternate
comparison workflows. Historical mock replay remains incompatible; replay migration
and full mock acceptance are separate future work. Commands below describe capabilities,
not authorization to execute paid runs or refresh fixtures during cleanup.

Run from the initialized workspace using `.venv/Scripts/python.exe` on Windows.
The suite uses the configured Compose project and preserves databases. Run one
mode at a time; `run-suite.lock` prevents overlapping new runner operations.
Legacy scripts do not participate in this lock.

```powershell
# 1. Complete mock acceptance: both real Framework integrations, zero paid calls.
.venv/Scripts/python.exe scripts/run_suite.py mock

# 2. Both integrations, all model stages live. Default: Muse Contributor/medium.
.venv/Scripts/python.exe scripts/run_suite.py live
.venv/Scripts/python.exe scripts/run_suite.py live --model provider/model --reasoning none

# 3. Evaluate the model on one integration; default path is Java.
.venv/Scripts/python.exe scripts/run_suite.py evaluate --model provider/model --reasoning medium
.venv/Scripts/python.exe scripts/run_suite.py evaluate --path sidecar --model provider/model --reasoning none

# 4. Capture both integrations for replacement of the normal business fixtures.
.venv/Scripts/python.exe scripts/run_suite.py capture --model provider/model --reasoning medium
```

Live modes require `LOOMSPAN_OPENROUTER_API_KEY` in the process environment.
They create private copies of runtime/model and skill configuration, archive
existing runtime evidence, recreate the selected hosts and recording fixture,
then restore normal configuration and disabled provider access in `finally`.
They never edit the authored model configuration or automatically fall back to a
different model. `--reasoning none` omits skill thinking levels and the expected
provider reasoning parameter; it does not ask the provider for a level named none.
No model catalogue compatibility is assumed. An unsupported profile should fail.

The evaluation mode submits executions and collects model traces only for the
chosen integration. Shared runtime readiness/preservation still inspects the
installed stack; this is not a standalone installation of one integration.

## Current compatibility boundary

The normal contracts were strengthened on 2026-10-04. Historical business and fault
replay payloads are incompatible with parts of this baseline. Until a suitable new
capture and explicit replay migration pass full acceptance, mock mode is not an
accepted current baseline. Preserve historical fixtures and their source evidence.
See [current results](implementation-status.md).

## Coverage and results

Mock mode runs the existing six scenario groups: baseline, changed priority,
controlled malformed-output recovery, service creation/recovery, gated isolation,
and nested authorization, plus focused tests. Existing historical live evidence
is audited offline; this does not make paid calls.

Live/evaluate/capture run **baseline and changed-priority assessment
workflows followed by service creation/recovery**, including every planner, assignment, child model and native parent
completion. They apply the existing source-fidelity, quote, identity, business
publication and Framework-trace checks against the requested model. Controlled
fault and authorization responses remain in mock mode; live mode is not a claim
that those scripted scenarios have been converted into live tests. Service checks
use the actual live baseline's quotes and published assessment, exercise approval,
direct permission denial, lost-result recovery and expiry/idempotency, and make no
additional model calls. Gated isolation and deliberately scripted nested
authorization remain covered by mock acceptance.

Each run retains a JSON report, JUnit XML and Markdown summary, linked original
requests/responses, public results, business records and Framework traces.
Failed/incomplete captures produce a nonzero exit. A passing live run is labeled
`AUTOMATED_CHECKS_PASS`, with semantic review pending. Completion alone is not
business correctness or model reliability; repeated evaluations are separate runs.

## Diagnostic summary

The live/evaluate/capture summary separates execution from business correctness.
Each scenario and integration has a diagnostic category, the public execution
status, a business-check status, the next investigation, and links to observed
provider responses or Framework exceptions. The original failed assertions remain
in an expandable list and JUnit; diagnostic classification never changes pass/fail.

| Category | Meaning |
| --- | --- |
| Suspected Framework defect | An unexpected exception originates in Framework code; reproduce and investigate before declaring a defect. |
| Provider error / response protocol | HTTP failure, error inside HTTP 200, missing completion envelope, or provider SDK error. |
| Provider request timeout / connection | Provider attempt timed out or transport failed; the network, proxy, provider and configured limit need investigation. |
| Execution deadline / budget | A mission/polling deadline or usage budget was reached. |
| Model output rejected; correction exhausted | Framework rejected the model's action/output and could not obtain a valid replacement. This is different from an internal crash. |
| Completed; business checks failed | Execution completed, but evidence transfer, planning, fidelity, citations or other business checks failed. Inspect outputs, prompts, sources and application publication; this alone does not prove limited model intelligence. |
| Completed; automated checks passed | The recorded automated checks passed; business judgment still needs semantic review. |
| Unclassified failure / evidence gap | Available evidence cannot support reliable attribution. |

Recovery counters distinguish actual recorded provider retries from model
correction requests, rejected step actions, truncated responses and invalid JSON.
A provider error envelope is not counted as malformed model JSON. Failed provider
calls or rejected actions followed by a response or validated action are reported
as recovered, even if a later tool execution fails; attempts exhausted
does not necessarily mean any retry was permitted. Concurrent parent propagation
of the same failure ID is not counted as a separate defect. Multiple causes remain
visible rather than being hidden by the primary investigation category.

Business quality is `NOT_ASSESSED` when execution or required diagnostic evidence
is incomplete; cascaded failed assertions are retained. Service checks blocked by
the invalid baseline are explicitly `NOT RUN`. Runner/environment/restoration
errors appear separately. Categories are conservative diagnostic suggestions,
not automatic bug findings or semantic model ratings. Missing/corrupt traces or
checksum mismatches cannot produce a clean diagnostic result.

Regenerate a historical live suite report offline into a **new** directory:

```powershell
.venv/Scripts/python.exe scripts/report_run.py evidence/evaluate-suite-RUN/report.json --output evidence/diagnostic-view-RUN
```

This command makes no provider calls, writes a new summary/JSON/JUnit view, and
preserves the original report and captures. Output cannot be inside the original
suite or capture directories and cannot overwrite an existing output directory.
The new JSON binds its source report by checksum. Recorded runtime restoration is
historical; this command does not inspect or change the current runtime.

## Replacing business fixtures

Capture mode writes `semantic-review-template.json` next to `report.json` after
automated checks pass. Review the actual outputs for evidence fidelity, uncertainty,
commercial terms, feasible alternatives and response to changed priority. Complete
each path's rationale and set `SUITABLE_FOR_REPLAY_CURATION` only for suitable
outputs. Keep the suite-report and capture checksum bindings. Save the completed
review separately; do not modify original captures.

```powershell
.venv/Scripts/python.exe scripts/refresh_replay.py --suite evidence/capture-suite-RUN/report.json --semantic-review evidence/capture-suite-RUN/semantic-review.json --version model-name-v1
```

This second phase derives unedited, case-ID-normalized responses into a new
`fixtures/replay/versions/VERSION` directory. It validates original checksums,
recomputes live checks, binds semantic review, and runs the complete mock suite
with the candidate selected. Only a successful full run atomically updates
`fixtures/replay/active-business.json`. Failures leave the active selection alone
and retain candidate evidence. A version name cannot overwrite an existing version.
When a successful live workflow required Framework correction, normal replay uses
the last captured response for that stage. Omitted failed-attempt IDs are recorded
explicitly; their original requests/responses remain in the live capture. Repeated
stages without explicit Framework correction feedback are rejected. This does not
change any deliberately authored fault script or fabricate a model answer.

Refresh affects normal baseline/priority business responses, including those used
to prepare service, isolation and nested authorization cases. Hand-authored nested
authorization actions and the original, provenance-bound full-correction bundle
remain unchanged by that command. Contract changes require separate compatibility
review and migration of these fixtures and any retained-evidence audits before full
acceptance can pass. Mock runs deliberately contain mixed model provenance.

The activation record retains the previous fixture path and the successful
acceptance checksum. To inspect an old version without activation, set
`LOOMSPAN_BUSINESS_FIXTURE` to its repository-relative business JSON for a mock run.
Restore the previously retained activation record to roll back an active version;
for the original version, remove only the active pointer. Never delete source
fixtures or evidence. Unsupported stage sequences are rejected during strict
curation; retain that failure for inspection instead of inventing a replay plan.

## Verification status

See [implementation status](implementation-status.md) for actual validation runs.
No newly captured model fixture is activated merely by adding these commands.
