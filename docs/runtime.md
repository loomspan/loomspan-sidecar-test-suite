# Running the foundation

Use Docker Compose for all five services and the local Python environment for tooling.
Always use `scripts.environment.compose()` through the provided startup script so the
runtime, provider-disabled and optional isolated/supplied-artifact overlays are applied.
Do not use bare `docker compose up`, which omits those overlays.

## Initialized workspace

```powershell
.venv/Scripts/python.exe scripts/start.py
.venv/Scripts/python.exe scripts/readiness.py
.venv/Scripts/python.exe scripts/smoke.py
```

The smoke check logs in through real PKCE, invokes deterministic quote tools through
both integrations, verifies complete offer records and exact service quotes against
source fixtures (including quote attendance equaling source arrival), checks the mounted eight-skill mixed-model assignment,
unauthenticated denial and Maya's request-creation denial,
and verifies no model requests and no changes to previous business rows. It adds two
quote rows per app under new smoke case IDs. Results are in `.runtime/smoke.json`.
It is a foundation check, not full business acceptance or model evaluation.

Default ports: Keycloak 18080, Java 18081, Python 18082, Sidecar 18083,
fixtures 18090 and Sidecar readiness 19091. An isolated workspace may offset them.
Local secrets, realm configuration, business databases and build identity are ignored
under `.runtime`. Never print credentials or delete databases during ordinary cleanup.

## Building from source

Prerequisites: Docker, Java 21+, Maven, Python 3.13 and the Maven-installed Framework
`1.0.0-beta.8`. The pinned Sidecar beta.3 source is exported into
`.build/sidecar-1.0.0-beta.3`. `scripts/prepare.py` can export it from the neighboring
`loomspan-sidecar` checkout for a fresh workspace and generate local credentials.
It does not overwrite an existing source export.

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.lock
.venv/Scripts/python.exe -m playwright install chromium
.venv/Scripts/python.exe scripts/prepare.py
mvn -B -ntp -f apps/java/pom.xml clean package
mvn -B -ntp -f .build/sidecar-1.0.0-beta.3/pom.xml clean package
.venv/Scripts/python.exe scripts/record_build.py
.venv/Scripts/python.exe scripts/start.py --build
.venv/Scripts/python.exe scripts/smoke.py
```

For a fresh isolated workspace, run `scripts/configure_isolated.py --project NAME
--port-offset OFFSET` before preparing credentials; NAME must differ from
`equipment-acceptance` and OFFSET must be nonzero. Use the Python environment above.
Do not reconfigure the current initialized workspace.

The build recorder verifies that both packaged hosts embed the installed Framework
bytes. Both POMs pin Framework beta.8; Sidecar's release tag is checked before export.
Source export disables Git's Windows line-ending conversion so release-workflow
text checks receive the tagged LF content.
Current provider/mission/proxy limits are 480/2400/510s.
The authored pack uses Sol/medium for six judgment skills and Luna/medium for the
two coordinators. The generator preserves this assignment. Provider access remains disabled by the
normal Compose overlays regardless of whether the shell has a provider key.

The 2026-10-07 dependency upgrade passed the 58 provider-free suite tests, both-host
smoke and all eight frozen-reference replay cases. Both running JARs matched the
recorded build identity and embedded identical Framework beta.8 bytes; portable
package input/hash verification also passed. Sidecar's source tests reported 252
passes and three skips initially; the sole failed release-workflow line-ending
check passed on rerun after restoring the exported workflows to their tagged LF bytes.
No paid calls were made. These checks do not establish full release acceptance.

Phase 2 cleanup retained packaged hosts and business methods and made the tested
mixed assignment the normal configuration. Historical synthetic business records,
results and traces were retired into an external recovery snapshot; credentials and
Sidecar operational configuration were retained. Startup recreates the normal running
services; smoke adds fresh isolated quotes. No paid validation was performed during cleanup.

## Portable installation

`package_runtime.py --output NEW_DIRECTORY` packages the current verified JARs and
source/configuration without credentials or local databases. On a fresh extracted
workspace, `install_runtime.py` verifies the supplied hashes, creates an isolated
provider-disabled configuration and generates credentials. Start with `start.py --build`
and run `smoke.py`. Packaging/install scripts require the same local Python environment.
These tools are retained; a new portable installation was not performed during cleanup.

## Deterministic assessment replay

After startup, run `.venv/Scripts/python.exe scripts/run_suite.py mock` to exercise
all four accepted assessment cases on both real integrations using frozen Sol/Luna
responses. It requires no provider key and keeps provider access disabled. The maintained
`fixtures/reference` pack travels with source packages and is never replaced by run
output. Each replay creates fresh synthetic assessment/quote rows while preserving
existing rows. It checks runtime behavior against the accepted reference, not new
model reasoning or the full service-request workflow. See [the runner guide](runner.md).

## Skill experiments

Current model/planning declarations live in `config/skills`; Sidecar's deterministic
REST declarations live in `config/rest-skills`. Current generation tools and contracts
remain in `scripts/author_workflow.py` and `scripts/workflow_contracts.json`.
Keep Java and Python business/authorization behavior equivalent during skill changes.

Use the [shared four-mode runner](runner.md) for an authorized evaluation. Work directly
on current skills; there is no variant registry. Historical Phase 1 and Phase 2 captures remain retired. The runner uses `evidence/latest` by default, replacing
its three output files rather than accumulating run directories. Keep an accepted
result separately when a skill improvement is accepted. Paid calls still require
explicit authorization; no paid run was performed when implementing the runner.
