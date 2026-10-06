# Local development and evaluation

Use the repository's PowerShell virtual environment and Docker Compose stack.
For a supplied-artifact installation, follow the [on-prem operator runbook](on-prem-runtime.md).
Its historical verification applies to the recorded artifacts, not automatically
to the current contracts. See [current status](implementation-status.md).

## Existing initialized workspace

```powershell
.venv/Scripts/python.exe scripts/readiness.py
.venv/Scripts/python.exe scripts/run_suite.py evaluate --model provider/model --reasoning medium
# Both paths, fresh live baseline and priority, with capture for possible review:
.venv/Scripts/python.exe scripts/run_suite.py capture --model meta/muse-spark-1.3-contributor --reasoning medium
```

Live modes require `LOOMSPAN_OPENROUTER_API_KEY` in the process environment, preserve
existing evidence, use temporary model configuration and restore disabled provider
access. Run one mode at a time. The [run-mode guide](run-modes.md) covers reports,
semantic review, refresh and rollback. Do not run historical diagnostic recipes
against the active stack without checking their contract compatibility.

## Authoring and build changes

Canonical workflow contracts are in `scripts/workflow_contracts.json`; generate
configuration with `scripts/author_workflow.py`. Deterministic boundaries also live
in Java method signatures and Python request models. Keep both integrations equivalent
and run their contract checks after changes. Freeze them before comparing models.

Before rebuilding or recreating services, preserve the current runtime:

```powershell
.venv/Scripts/python.exe scripts/preserve_runtime.py
```

The current local snapshot build uses the separately exported Sidecar beta.2 source
at `.build/sidecar-1.0.0-beta.2-framework-beta.8-SNAPSHOT`. Both builds consume the
Maven-installed Framework snapshot:

```powershell
mvn -B -ntp '-Dloomspan.version=1.0.0-beta.8-SNAPSHOT' -f apps/java/pom.xml clean package
mvn -B -ntp '-Dloomspan.version=1.0.0-beta.8-SNAPSHOT' '-Dmaven.test.skip=true' -f .build/sidecar-1.0.0-beta.2-framework-beta.8-SNAPSHOT/pom.xml clean package
.venv/Scripts/python.exe scripts/record_snapshot_build.py
```

`record_snapshot_build.py` verifies packaged Framework identities against the installed
artifact. Sidecar packaging above skips test compilation and execution: its pinned beta.2
test source uses the old SkillDescriptor constructor, incompatible with PR 20.
Production code compiles; this downstream test-source gap remains unresolved.
Runtime acceptance is separate.
Use `scripts.environment.compose()` when automating recreation so the configured
project, snapshot, offline and any isolated/supplied-artifact overlays are retained.
Do not use bare Compose commands that drop these overlays. Run readiness afterwards.
Provider/mission/proxy limits are 480/2400/510 seconds for all comparison models.

## APIs and evidence

Default ports are Java 18081, Python 18082, Sidecar 18083, fixtures 18090 and
Keycloak 18080; isolated projects may offset them. Both apps expose `POST /assessments`,
`GET /assessments/{id}`, `POST /service-requests` and `GET /service-requests/by-key/{key}`.
Use a unique registered case and actual published assessment/quote for commitment.
The model cannot create approval authority.

Evidence is local under `evidence/<run>`; [the index](../evidence/README.md) selects
current results. Tokens, passwords and raw environment inspection stay out of reports.
Business databases in `.runtime/java` and `.runtime/python` persist independently.
Do not reset them as part of evaluation cleanup. Exact trace bytes and capture
checksums remain original; write new analyses to new directories.

[Archived recipes](../archive/2026-10-04-before-muse-baseline/README.md) document
historical released builds and investigations. They are not current setup instructions.
