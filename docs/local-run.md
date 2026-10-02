# Local build and evidence

**Latest full Muse baseline (2026-10-01):** `meta/muse-spark-1.3-contributor`, medium reasoning, ran once on each path after offline fixes and successful access checks. Java failed on malformed step-action JSON after correction; Sidecar published its assessment with unchanged quotes and correct monetary units but has semantic wording findings. Focused assertions: 6 passed / 2 failed. Both Framework traces are retained. The capture remains unapproved for replay. See `evidence/review-live-20261001-220102/summary.md` and implementation status.

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
mvn -B -ntp '-Dloomspan.version=1.0.0-beta.8-SNAPSHOT' -f apps/java/pom.xml package
mvn -B -ntp '-Dloomspan.version=1.0.0-beta.8-SNAPSHOT' -DskipTests -f .build/sidecar-1.0.0-beta.2-framework-beta.8-SNAPSHOT/pom.xml package
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
