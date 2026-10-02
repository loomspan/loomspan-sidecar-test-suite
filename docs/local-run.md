# Local build and evidence

## Reviewed offline assessment replay

Current approved fixture: `fixtures/replay/business-reviewed-v1.json`, bound by
`business-reviewed-v1-approval.json`. Source captures and semantic reviews remain
required local provenance inputs; the runner rejects missing/changed sources or
fixture content. Do not substitute historical rejected or authored diagnostic data.

Preserve runtime evidence before recreating fixtures, then disable provider access:

```powershell
.venv/Scripts/python.exe scripts/preserve_runtime.py --no-package-copy
docker compose --env-file .runtime/compose.env -f compose.yaml -f compose.snapshot.yaml -f compose.offline.yaml up -d --no-deps --force-recreate fixtures
.venv/Scripts/python.exe scripts/capture_reviewed_replay.py --scenario baseline
.venv/Scripts/python.exe scripts/capture_reviewed_replay.py --scenario priority
```

Run the two commands sequentially (shared PKCE callback port). Each prints a new
capture directory. Review it with `scripts/review_reviewed_replay.py CAPTURE --output
REVIEW/review.json`, writing outside the capture. Then run the eight assertions in
`tests/test_delivery_evidence.py` and `tests/test_planner_evidence.py` with
`CAPTURE_DIRECTORY` pointing to it. Review accepts only unchanged source output,
exact canonical inputs, actual trace response equality and zero business commitments.
Source provider usage/cost metadata remains historical; these runs make no paid calls.

Regenerate candidates explicitly with `scripts/curate_business_replay.py` only when
reviewed source selection changes; a changed fixture hash invalidates the separate
approval record and requires renewed offline verification. Fault diagnostics are
separate fixtures. This replay scope does not approve remaining first-delivery scenarios.

## Muse verification and comparison correction

The user authorized useful Muse calls without a spending-confirmation step on
2026-10-02. Keep Muse/medium and the installed PR 14/15 snapshot. Provider access
was restored by recreating fixtures without `compose.offline.yaml`; applying that
overlay disables it again. Preserve runtime evidence before host recreation. For
YAML-only changes, `scripts/preserve_runtime.py --no-package-copy` records package
identities without creating a redundant package archive. Re-record the snapshot
baseline and recreate Java/Sidecar to load changed skill YAML; no package rebuild
is needed when application/dependency bytes are unchanged.

```powershell
# Full baseline or priority pair, followed by independent review:
.venv/Scripts/python.exe scripts/capture.py --parallel
.venv/Scripts/python.exe scripts/capture.py --parallel --priority
.venv/Scripts/python.exe scripts/inspect_capture.py evidence/live-RUN --output evidence/review-live-RUN/mechanical-review.json
.venv/Scripts/python.exe scripts/review_correction_capture.py evidence/live-RUN --output evidence/review-live-RUN/trace-correlated-inventory.json
# Comparison-only controlled missing-field fault using a complete real source:
.venv/Scripts/python.exe scripts/capture_comparison_correction.py evidence/live-SOURCE --offline
.venv/Scripts/python.exe scripts/capture_comparison_correction.py evidence/live-SOURCE
.venv/Scripts/python.exe scripts/review_comparison_correction.py evidence/comparison-correction-live-RUN --output evidence/review-comparison-correction-live-RUN/review.json
```

Wait for each command to finish authentication/submission before launching another
capture process: the browser login helper uses one local PKCE callback port. Path
execution within each `--parallel` command remains concurrent. The correction
harness uses captured content with case-ID normalization and deliberate removal of
`nextDecision`; only the one correction stage per path can call the provider, and
unexpected attempts fail without fallback. Quotes are reissued and checked exactly.
The rehearsal correction is synthetic; live correction is new Muse output. Neither
approves its source capture, a full business baseline or full-mission recovery.
Mechanical review now checks bulletin applicability in the actual assessment
child input, not only complete sibling results available to the parent.

The current runtime has `loomspan.session.quotas.max-usage-units: 400000` on both
paths; request timeout remains 240s and snapshot mission timeout 1200s. A preserved
Java priority run exhausted the previous 200000 limit after successful local
corrections. This supported runtime setting changes no business approval cap.
`record_snapshot_build.py` records the shared quota; mechanical review verifies it
against the actual root trace's configuredLimits. For intentionally one-path follow-up
captures, pass `inspect_capture.py --path java` (or `--path sidecar`) and run capture
assertions with the matching pytest `-k` filter. The report explicitly marks its
single-path scope; missing paths are not silently treated as verified.

## Deployed offline business workflow diagnostic

This exercises both actual Framework paths with preserved captured stages, authored
business comparisons/parent finals, intentional selectedOption fault and synthetic
correction. It makes no paid calls, does not approve the source captures and does
not establish real-model adherence. Independent actions match by their task-graph
dependencies, allowing either arrival order. The provider credential is disabled in
the fixture while this overlay is active.

```powershell
.venv/Scripts/python.exe scripts/preserve_runtime.py
mvn -o -B -ntp -f apps/java/pom.xml '-Dloomspan.version=1.0.0-beta.8-SNAPSHOT' -DskipTests clean package
.venv/Scripts/python.exe scripts/record_snapshot_build.py
docker compose --env-file .runtime/compose.env -f compose.yaml -f compose.snapshot.yaml -f compose.offline.yaml up -d --build java python fixtures
docker compose --env-file .runtime/compose.env -f compose.yaml -f compose.snapshot.yaml -f compose.offline.yaml up -d --force-recreate --no-deps sidecar
.venv/Scripts/python.exe scripts/readiness.py
.venv/Scripts/python.exe -u scripts/capture_business_diagnostic.py
# Substitute the returned capture path and a NEW external review filename:
.venv/Scripts/python.exe scripts/review_business_diagnostic.py evidence/business-workflow-offline-RUN --output evidence/review-business-workflow-offline-RUN/review.json
```

No Sidecar package rebuild is needed when its installed dependency/package is
unchanged and passes the byte check. Preserve runtime evidence before any host
recreation. A later explicitly selected provider phase must recreate fixtures
without the offline overlay; do not silently restore provider access in this phase.

## Offline business-output checks (no provider calls)

The hand-edited examples in `fixtures/replay/business-output-diagnostic-v1.json`
retain Muse source provenance and every authored mutation. They are unapproved and
are not registered as complete replay scripts. Run the focused local checks without
the live `harness` fixture or a service restart:

```powershell
.venv/Scripts/python.exe -m pytest tests/test_business_output.py tests/test_quote_publication.py tests/test_capture_review.py tests/test_fixture_replay.py tests/test_fixture_proxy.py -q
mvn -o -f apps/java/pom.xml '-Dloomspan.version=1.0.0-beta.8-SNAPSHOT' -DskipTests compile
```

Archive existing compiled classes before compiling if they must be retained. The
compile command leaves packaged JARs intact. `tests/offline/BusinessOutputCheck.java`
checks Java publication against both example payloads, using a scripted caller and
fresh temporary SQLite databases. Compile/run it with the application classes and
packaged dependency JARs on the classpath; see the retained evidence summary for
the exact commands used. This does not establish authentication or Framework
acceptance. No revised configuration has been deployed by these checks.

**Latest Muse verification (2026-10-02):** both paths complete on the installed
PR 14/15 snapshot; eight capture assertions and 53 mechanical checks pass. Java
schema recovery succeeds, but PR 14 step-action recovery is not exercised in that full run.
Business findings keep captures unapproved. See
[review](../evidence/review-live-20261002-000544/summary.md) and implementation status.

The subsequent [isolated controlled fault](../evidence/review-controlled-step-live-20261002-004937/summary.md)
demonstrates real PR 14 recovery on both paths. It uses synthetic planning/final
markers, a captured malformed action and one actual Muse correction response per
path. It is not a full business replay baseline. Both model answers omit the large
optional context; the deterministic lookup reads authoritative records using IDs.

## Isolated correction diagnostic

Only run the live command when a new paid correction check is explicitly wanted.
`controlled-live` has exactly one matched provider stage per case, with no fallback
for unexpected/repeated requests. Preserve active traces/logs before recreating hosts
(this execution retained all 16 active traces in `evidence/pre-controlled-correction-20261002-004519`).
The fixture tests and `--offline` rehearsal make no provider calls.

```powershell
.venv/Scripts/python -m pytest tests/test_fixture_proxy.py tests/test_fixture_replay.py
docker compose --env-file .runtime/compose.env -f compose.yaml -f compose.snapshot.yaml -f compose.correction.yaml up -d --build fixtures java sidecar
.venv/Scripts/python -u scripts/capture_step_correction.py --offline
# Explicit opt-in: one Muse/medium correction call per path.
.venv/Scripts/python -u scripts/capture_step_correction.py
# Review the newly returned capture path, writing outside that original capture:
.venv/Scripts/python scripts/review_step_correction.py evidence/controlled-step-live-RUN --output evidence/review-controlled-step-live-RUN/review.json
docker compose --env-file .runtime/compose.env -f compose.yaml -f compose.snapshot.yaml up -d java sidecar
.venv/Scripts/python scripts/readiness.py
```

The diagnostic invokes only the real entitlement leaf. Original captured syntax is
retained with case-ID-only substitution. The synthetic terminal marker is diagnostic
scaffolding, not a model-produced business assessment. Restore normal configuration
after evidence is exported, even if correction fails.

The new artifact was verified offline against both captured trailing-brace failures
before two compatibility probes and exactly one workflow per path. Do not repeat
those paid runs merely to verify feedback. Current read-only capture review accepts
both historical `Execute skill` and PR 15 `Fulfill the mission for skill` wording.
Initial obsolete-matcher reports remain preserved beside corrected reports.

Before using the `clean package` snapshot commands below, archive any previous
packages needed as evidence. `record_snapshot_build.py` must pass before deployment;
it catches stale nested Framework bytes even when ordinary packaging succeeds.

Use PowerShell at the repository root, Docker Desktop, Java 21 via Maven and Python 3.13. Provider credentials remain in the existing `LOOMSPAN_OPENROUTER_API_KEY` environment variable. Never paste credentials into a command, source file or report.

## Focused offline continuation checks

```powershell
.venv/Scripts/python -m pytest tests/test_contract_diagnostic.py tests/test_quote_publication.py tests/test_deterministic.py tests/test_fixture_replay.py tests/test_fixture_proxy.py tests/test_capture_review.py
```

These tests make no provider calls. The contract diagnostic uses unapproved Sol
responses with original provenance, deliberately combined as a synthetic correction
sequence. It does not publish an assessment or establish real-model correction.
See `fixtures/replay/README.md`. Source capture files are read-only inputs.
The revised quote schema uses only the supported Framework vocabulary; count and
exact authoritative equality are enforced by each application.

Access was verified on both paths after the account-setting change in
`evidence/compatibility-20261001-215426`; no further unchanged probe is needed.
`scripts/compatibility.py` makes a small check on each path,
verifies actual emitted model/reasoning, and retains both failures and successes.
Full live workflow commands below are explicit opt-in recipes, not an instruction
to run them before the offline fixes pass or without an identified evidence gap.

## Authorized beta.8-SNAPSHOT test

The user installed Framework `1.0.0-beta.8-SNAPSHOT` locally and authorized this test on 2026-10-01. Both hosts can consume it without publishing Framework or releasing Sidecar. The separate Sidecar export at `.build/sidecar-1.0.0-beta.2-framework-beta.8-SNAPSHOT` is unchanged beta.2 source. To create it in a fresh workspace, export tag `v1.0.0-beta.2` from the neighboring Sidecar checkout into that directory, preserving the earlier beta.2 build.

```powershell
mvn -B -ntp '-Dloomspan.version=1.0.0-beta.8-SNAPSHOT' -f apps/java/pom.xml clean package
mvn -B -ntp '-Dloomspan.version=1.0.0-beta.8-SNAPSHOT' -DskipTests -f .build/sidecar-1.0.0-beta.2-framework-beta.8-SNAPSHOT/pom.xml clean package
.venv/Scripts/python scripts/record_snapshot_build.py
docker compose --env-file .runtime/compose.env -f compose.yaml -f compose.snapshot.yaml up -d --build java sidecar
.venv/Scripts/python scripts/readiness.py
.venv/Scripts/python -u scripts/capture.py --path both --parallel
```

The overlay sets supported `loomspan.connections.model.request-timeout: 240s` through Spring environment binding in both containers. The initial mission budget of 600 seconds expired on both paths after calls beyond 60 seconds successfully completed. The local snapshot overlay now uses `loomspan.session.mission-timeout: 1200s`; the polling harness allows 30 additional seconds to observe terminal cleanup. `--parallel` runs the two independent paths concurrently with separate cases and clients, not a load acceptance claim. `record_snapshot_build.py` verifies both packaged Framework JARs against the local installed artifact and records hashes/configuration in ignored `.runtime/build-baseline.json`. Capture/check manifests use that record and reject mismatched running host JARs or timeout values. Evidence is labeled as a local snapshot build, not the published Sidecar binary. Sidecar packaging above skips its tests; runtime suite results are reported separately. Java currently has no Maven tests.

Use the snapshot overlay on subsequent container recreation, including before adding `compose.authorization.yaml`. The original build recipe below remains the released baseline. To return to it, rebuild Java with its default beta.7 dependency, deploy the base Compose services, and remove the active `.runtime/build-baseline.json` only after archiving it with the snapshot evidence. Do not label snapshot execution as a release run.

## Released baseline setup

```powershell
python scripts/prepare.py
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.lock
.venv/Scripts/python -m playwright install chromium
.venv/Scripts/python scripts/seed_sources.py
.venv/Scripts/python scripts/author_workflow.py
mvn -B -ntp -DskipTests -f .build/sidecar-1.0.0-beta.2/pom.xml package
mvn -B -ntp -DskipTests -f apps/java/pom.xml package
docker compose --env-file .runtime/compose.env up -d --build
.venv/Scripts/python scripts/readiness.py
```

`prepare.py` checks exact tag commits and writes generated local-only Keycloak passwords/control credentials to ignored `.runtime`. It exports releases into ignored `.build`, leaving neighboring checkouts unchanged. Existing realm data is not reset by running prepare. The quoted Maven commands compile/package; they do not run tests.

Manual browser login (the access token goes only into ignored `.runtime`):

```powershell
.venv/Scripts/python scripts/login.py --manual --user maya
```

For the seeded demonstration user's password, consult the local `.runtime/secrets.json` yourself; do not attach that file to reports. The automated helper uses separate browser sessions for Maya and Luis.

## Executable checks

```powershell
.venv/Scripts/python scripts/compatibility.py
.venv/Scripts/python -m pytest tests/test_deterministic.py --junitxml=evidence/deterministic-junit.xml
```

The compatibility command makes small live-provider requests through both paths and downloads Framework traces. Deterministic checks make no provider calls. They are compatibility/business-skill checks, not full first-delivery acceptance.

Resume verification on 2026-10-01 found no newer Framework/Sidecar release or supported timeout override. Do not repeat live captures until that dependency changes. The read-only capture preflight checks completion, paired provider evidence, final synthesis, authoritative records and trace checksums; it never approves semantic correctness or replay provenance:

```powershell
.venv/Scripts/python scripts/inspect_capture.py evidence/live-RUN --output evidence/review-RUN.json
.venv/Scripts/python -m pytest tests/test_fixture_replay.py tests/test_fixture_proxy.py tests/test_capture_review.py
```

The report must be a new file outside the source capture. Exit 1 means rejection; exit 0 means semantic review is still needed. Historical journals lack per-request IDs and cannot establish unambiguous response pairing under concurrency. New captures record those IDs without altering provider request/response JSON. No approved baseline or replay exporter is supplied yet.

The controlled nested-authorization configuration is explicitly opt-in:

```powershell
docker compose --env-file .runtime/compose.env -f compose.yaml -f compose.authorization.yaml up -d --build fixtures java sidecar
$env:AUTHORIZATION_DIAGNOSTICS = '1'
.venv/Scripts/python -m pytest tests/test_nested_authorization.py --junitxml=evidence/nested-diagnostic-junit.xml
Remove-Item Env:AUTHORIZATION_DIAGNOSTICS
docker compose --env-file .runtime/compose.env up -d java sidecar
```

This uses handcrafted negative diagnostic responses, explicitly labeled as such. It proves the denied capability is absent from the nested planner's available list, its proposed use receives real correction feedback and terminal rejection, durable requests remain unchanged, and Sidecar makes no creation-endpoint call. It does **not** replace full acceptance: otherwise-valid approval, reviewed capture-derived replay and Luis's durable-creation positive control still require a completed assessment. Task-count constraints may mention the denied skill name; the available-capability list is the authorization assertion. The normal configuration exposes neither test parent and never adds creation to assessment. Fixture restarts clear registrations; retained journals and databases remain on disk.

Full live workflow reproduction (beta.7 preserves dependent evidence; completion is currently limited by the documented provider timeout):

```powershell
.venv/Scripts/python -u scripts/capture.py --path both
# Optional changed-priority run after obtaining a complete baseline:
.venv/Scripts/python -u scripts/capture.py --path both --priority
$env:CAPTURE_DIRECTORY = 'C:/absolute/path/to/evidence/live-RUN'
.venv/Scripts/python -m pytest tests/test_planner_evidence.py tests/test_delivery_evidence.py --junitxml=evidence/delivery-junit.xml
```

Do not treat capture as review or success. Review the actual model inputs, returned evidence, terminal application result and NDJSON artifacts. No suitable reviewed replay baseline is shipped while the complete workflow fails; no command silently regenerates scripts or substitutes a model. `fixtures/server.py` supports explicit registered replay steps, but its development scaffolding is not accepted provenance.

Endpoints: Java `http://localhost:18081`, Python `http://localhost:18082`, Sidecar execution `http://localhost:18083`, fixture controls `http://localhost:18090`, Keycloak `http://localhost:18080`.

Both apps expose `POST /assessments`, `GET /assessments/{id}`, `POST /service-requests`, and `GET /service-requests/by-key/{key}`. Public-boundary diagnostic invocation uses `POST /v1/skills/{name}/executions` and `GET /v1/executions/{id}`. Assessment input is in `fixtures/base-case.json`, with a unique registered `caseId`. Commitment fields are `assessmentVersion`, `option`, `quoteId`, `attendance`, `scope`, `cap`, `idempotencyKey`, and `approved: true`; these must match an actual published assessment and its authoritative quote.

Evidence lives under ignored `evidence/<run>`. Credentials and raw Docker environment inspection must not be copied there. Trace artifacts retain exact downloaded bytes, with an external SHA-256/case/path index. The application databases in `.runtime/java` and `.runtime/python` contain independent persistent business records. Preserve failures as well as successes. `docker compose --env-file .runtime/compose.env down` stops this stack; it does not remove volumes or evidence.
