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
both integrations, invokes all eight flat lookup operations and verifies a nested
approval reaches business rejection without creating a request. It verifies complete offer records and exact service quotes against
source fixtures (including quote attendance equaling source arrival), checks the mounted eight-skill mixed-model assignment,
unauthenticated denial and Maya's request-creation denial,
and verifies no model requests and no changes to previous business rows. It adds two
quote rows per app under new smoke case IDs. Results are in `.runtime/smoke.json`.
It is a foundation check, not full business acceptance or model evaluation.

Default ports: Keycloak 18080, Java 18081, Python 18082, Sidecar 18083,
fixtures 18090. Sidecar readiness uses its application port 18083. An isolated workspace may offset them.
Local secrets, realm configuration, business databases and build identity are ignored
under `.runtime`. Never print credentials or delete databases during ordinary cleanup.

## Building from source

Prerequisites include Docker, Java 21+, Maven, Python 3.13, uv and the developer-installed
Framework `1.0.0-beta.9-SNAPSHOT`. Use the matching local Framework documentation.
The suite consumes the current neighboring Sidecar checkout and its tested dependency;
ordinary builds do not rebuild Framework or compare its source revision/artifact bytes.

```powershell
python -m venv .venv
uv build --out-dir C:/path/to/new-sdk-dist ../loomspan-sidecar/sdks/python
$sdkWheel = (Get-ChildItem C:/path/to/new-sdk-dist/*.whl).FullName
.venv/Scripts/python.exe -m pip install -r requirements.lock "${sdkWheel}[fastapi]"
.venv/Scripts/python.exe -m pip check
.venv/Scripts/python.exe -m playwright install chromium
.venv/Scripts/python.exe scripts/prepare.py
mvn -B -ntp -f ../loomspan-sidecar/pom.xml verify
mvn -B -ntp -f apps/java/pom.xml clean package
.venv/Scripts/python.exe scripts/record_build.py --sidecar-checkout ../loomspan-sidecar --python-sdk-wheel $sdkWheel
.venv/Scripts/python.exe scripts/start.py --build
.venv/Scripts/python.exe scripts/smoke.py
```

For a fresh isolated workspace, run `scripts/configure_isolated.py --project NAME
--port-offset OFFSET` before preparing credentials; NAME must differ from
`equipment-acceptance` and OFFSET must be nonzero. Do not reconfigure an initialized
workspace. Existing credentials, signing keys and databases remain in place.
`prepare.py` provisions a local RSA execution key in a new workspace. An initialized
workspace needs its existing PKCS#8 PEM. Python receives that PEM read-only and the
SDK publishes public keys to `.runtime/execution-trust/jwks.json` at startup.
Sidecar mounts the public directory read-only so it can observe atomic replacement
of the export.

Keycloak authenticates public app requests. The SDK issues an execution JWT from
the verified subject and allowlisted exact business roles. Its lifetime is
independent of the public login and defaults to 900 seconds. Set the positive
integer `EXECUTION_LIFETIME_SECONDS` in the Compose environment to override it.
Sidecar forwards the original execution credential. The SDK verifies it across
`/skills` before application role and record checks.

The build recorder stages the executable at `runtime-artifacts/sidecar.jar` and
the wheel under `runtime-artifacts/python-sdk/`. It checks both hosts' Framework
coordinate and records the SDK filename, version and digest with the other
package and configuration hashes. The staging directory holds one wheel. Both Python
images install that wheel with its FastAPI extra and check the locked dependencies.
Smoke and evidence capture compare the wheel in each running Python container with
the recorded digest.

When refreshing the tool lock, resolve the same wheel with the suite requirements.
Keep the wheel as a separate explicit install input so the lock works across paths.

```powershell
"${sdkWheel}[fastapi]" | uv pip compile requirements.txt - --python-version 3.13 --no-emit-package loomspan-sdk --no-annotate --no-header -o requirements.lock
```
Compose uses `deploy/sidecar.Dockerfile`. Current provider/mission/proxy limits are
480/2400/510s. Normal overlays disable provider access regardless of shell keys.
The authored pack uses six Sol/medium judgment skills and two Luna/medium coordinators.

## Portable installation

`package_runtime.py --output NEW_DIRECTORY` packages the verified JARs, SDK wheel
and source/configuration. On a fresh extracted workspace, run
`install_runtime.py --project NAME --port-offset OFFSET`. The installer verifies
the supplied inputs before creating isolated runtime state and provisioning local
credentials. Run `start.py --build` and `smoke.py` using the tooling virtual
environment. The extracted runtime uses the supplied artifacts to build images.

## Deterministic assessment replay

After startup, run `.venv/Scripts/python.exe scripts/run_suite.py mock` to exercise
all four accepted assessment cases on both real integrations using frozen Sol/Luna
responses. It requires no provider key and keeps provider access disabled. The maintained
`fixtures/reference-namespaced` pack travels with source packages and is never replaced by run
output. Each replay creates fresh synthetic assessment/quote rows while preserving
existing rows. It checks runtime behavior against the accepted reference, not new
model reasoning or the full service-request workflow. See [the runner guide](runner.md).

In a disposable isolated runtime, run `scripts/verify_sdk_commitment.py --output NEW_DIRECTORY`
to check an assessment, exact approval, owner recovery and repeated request handling.
The check creates one `PENDING_DISPATCH` record per host and records the input
fixture and contract hashes.

## Skill experiments

The `typesafe-ai` suite uses native TypeSafe declarations under `config/skills/typesafe-ai`,
with pinned model `jev-1.13.0`. All four native connection aliases point to the local
fixture server; the timeout/retry aliases exercise transport policy. These connections
have a dummy local transport key. Normal startup disables provider forwarding even when
the shell has `LOOMSPAN_TYPESAFE_API_KEY`. The explicit native live adapter temporarily
enables a gateway that requires a durable, one-use permit for every exact request,
then restores offline operation. See [TypeSafe coverage and live scope](typesafe-ai.md).

Project-local authoring guidance lives under `.agents/skills`; `skills-lock.json`
records its sources. The Framework documentation copy is refreshed from the matching
local Framework checkout. Consult that checkout and the current neighboring
Sidecar's `agent-skills/loomspan-sidecar-authoring` for supported contracts. The
TypeSafe skill is pinned to `65a39f393687675ce170e6094757de20370365b9`.
Authoring guidance is separate from runtime skill declarations.

Current model/planning declarations live in `config/skills/equipment-service`; Sidecar's deterministic
HTTP executor declarations live in `config/executor-skills/equipment-service`. Current generation tools and contracts
remain in `scripts/suites/equipment_service/author_workflow.py` and `scripts/suites/equipment_service/workflow_contracts.json`.
Keep Java and Python business/authorization behavior equivalent during skill changes.

Use the [shared four-mode runner](runner.md) for an authorized evaluation. Work directly
on current skills; there is no variant registry. Historical Phase 1 and Phase 2 captures remain retired. The runner uses `evidence/latest/equipment-service` by default, replacing
its three output files rather than accumulating run directories. Keep an accepted
result separately when a skill improvement is accepted. Paid calls still require
explicit authorization; no paid run was performed when implementing the runner.
