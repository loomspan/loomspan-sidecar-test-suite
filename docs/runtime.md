# Running the foundation

Use Docker Compose for all five services and the local Python environment for tooling.
Always use `scripts.environment.compose()` through the provided startup script so the
snapshot, provider-disabled and optional isolated/supplied-artifact overlays are applied.
Do not use bare `docker compose up`, which omits those overlays.

## Initialized workspace

```powershell
.venv/Scripts/python.exe scripts/start.py
.venv/Scripts/python.exe scripts/readiness.py
.venv/Scripts/python.exe scripts/smoke.py
```

The smoke check logs in through real PKCE, invokes deterministic quote tools through
both integrations, checks unauthenticated denial and Maya's request-creation denial,
and verifies no model requests and no changes to previous business rows. It adds two
quote rows per app under new smoke case IDs. Results are in `.runtime/smoke.json`.
It is a foundation check, not full business acceptance or model evaluation.

Default ports: Keycloak 18080, Java 18081, Python 18082, Sidecar 18083,
fixtures 18090 and Sidecar readiness 19091. An isolated workspace may offset them.
Local secrets, realm configuration, business databases and build identity are ignored
under `.runtime`. Never print credentials or delete databases during ordinary cleanup.

## Building from source

Prerequisites: Docker, Java 21+, Maven, Python 3.13 and the Maven-installed Framework
`1.0.0-beta.8-SNAPSHOT`. The pinned Sidecar beta.2 source is exported into
`.build/sidecar-1.0.0-beta.2-framework-beta.8-SNAPSHOT`; the initialized workspace
already contains it. `scripts/prepare.py` can export it from the neighboring
`loomspan-sidecar` checkout for a fresh workspace and generate local credentials.
It does not overwrite an existing source export.

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.lock
.venv/Scripts/python.exe -m playwright install chromium
.venv/Scripts/python.exe scripts/prepare.py
mvn -B -ntp '-Dloomspan.version=1.0.0-beta.8-SNAPSHOT' -f apps/java/pom.xml clean package
mvn -B -ntp '-Dloomspan.version=1.0.0-beta.8-SNAPSHOT' '-Dmaven.test.skip=true' -f .build/sidecar-1.0.0-beta.2-framework-beta.8-SNAPSHOT/pom.xml clean package
.venv/Scripts/python.exe scripts/record_snapshot_build.py
.venv/Scripts/python.exe scripts/start.py --build
.venv/Scripts/python.exe scripts/smoke.py
```

For a fresh isolated workspace, run `scripts/configure_isolated.py --project NAME
--port-offset OFFSET` before preparing credentials; NAME must differ from
`equipment-acceptance` and OFFSET must be nonzero. Use the Python environment above.
Do not reconfigure the current initialized workspace.

The build recorder verifies that both packaged hosts embed the installed Framework
bytes. Sidecar packaging skips its incompatible pinned test sources; this remains a
limitation, not test acceptance. Current provider/mission/proxy limits are 480/2400/510s.
The authored default model is Muse/medium. Provider access remains disabled by the
normal Compose overlays regardless of whether the shell has a provider key.

The cleanup did not rebuild or alter application source, current skill definitions,
Compose configuration or business fixture values. Rebuild commands are operational
instructions, not a claim that a fresh rebuild was performed during cleanup.

## Portable installation

`package_runtime.py --output NEW_DIRECTORY` packages the current verified JARs and
source/configuration without credentials or local databases. On a fresh extracted
workspace, `install_runtime.py` verifies the supplied hashes, creates an isolated
provider-disabled configuration and generates credentials. Start with `start.py --build`
and run `smoke.py`. Packaging/install scripts require the same local Python environment.
These tools are retained; a new portable installation was not performed during cleanup.

## Skill experiments

Current model/planning declarations live in `config/skills`; Sidecar's deterministic
REST declarations live in `config/rest-skills`. Current generation tools and contracts
remain in `scripts/author_workflow.py` and `scripts/workflow_contracts.json`.
Keep Java and Python business/authorization behavior equivalent during skill changes.

Use the [shared four-mode runner](runner.md) for an authorized evaluation. Work directly
on current skills; there is no variant registry. The historical Phase 1 replay machinery
and captures remain retired. The runner uses `evidence/latest` by default, replacing
its three output files rather than accumulating run directories. Keep an accepted
result separately when a skill improvement is accepted. Paid calls still require
explicit authorization; no paid run was performed when implementing the runner.
