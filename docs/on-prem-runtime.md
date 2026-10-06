# On-prem reference runtime with Docker Compose

This is the supported operator path for the current reference installation test.
Use the supplied runtime distribution, not sibling development repositories.
Current artifacts are the explicitly pinned local Framework beta.8 snapshot and
Sidecar beta.2 host. After installation verification, new Framework/Sidecar releases
will provide published assets; that publication and migration have not occurred.

The historical [isolated installation check](../evidence/clean-compose-20261002/summary.md)
passed 311 checks, 56 assertions and 96 focused tests for its recorded artifacts.
Python initializes its empty database schema before health becomes ready. The normal
skill contracts have since changed; that result does not establish current replay
or installation acceptance. See [current status](implementation-status.md) before
selecting a distribution. Rebuild and verify supplied assets for the desired baseline.

## Prerequisites and supplied files

Use Windows with Docker Desktop's Linux engine and Docker Compose supporting
`!override` (the tested host has Compose 5.5.1), Python 3.13 and PowerShell 7.4+.
No local Java, Maven, Git checkout, provider account or existing application
database is required for this operator path. Host prerequisites are supplied;
the same-host validation does not prove a fresh Windows installation.

Use a project name and ports not already owned by another installation; inspect
`docker compose ls` first. The verification used existing host pip, Docker build
and Playwright browser caches, while installing a fresh venv and application
state. It does not establish an uncached download or air-gapped bootstrap.

Supply `equipment-runtime.zip`, its external `checksums.json` and `manifest.json`.
The distribution contains both exact executable JARs, pinned container bases,
Python source/dependency pins, business configuration, installers and verification
scripts. The manifest binds all source/configuration bytes and both embedded
Framework identities. It contains no credentials or application databases.
Building the images needs access to the pinned container registries, PyPI and
Sidecar's apt repository. Python dependencies are version-pinned; apt curl is not
version-pinned. Record resolved images/packages. This is not an air-gapped recipe.

The optional offline acceptance input bundle contains `workspace-inputs.zip`,
`input-inventory.json` and its own `checksums.json`. Its original captures, traces,
reviews and approvals are retained evidence inputs, not results of this install.
Do not copy its source overlay over the runtime distribution.

## Install into an empty directory

For the coexistence validation, use `C:\opendev\clean-validation\20261002\equipment`.
An operator may use another empty directory. Never run installation in the
retained development workspace or over existing `.runtime` state.

```powershell
$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $true
Remove-Item Env:LOOMSPAN_OPENROUTER_API_KEY -ErrorAction SilentlyContinue
Remove-Item Env:OPENROUTER_API_KEY -ErrorAction SilentlyContinue
# Set $distribution to the supplied directory before these commands.
$expected = Get-Content (Join-Path $distribution 'checksums.json') -Raw | ConvertFrom-Json
if ((Get-FileHash (Join-Path $distribution 'equipment-runtime.zip') -Algorithm SHA256).Hash.ToLower() -ne $expected.'equipment-runtime.zip') { throw 'Runtime archive checksum mismatch' }
Expand-Archive (Join-Path $distribution 'equipment-runtime.zip') -DestinationPath C:\opendev\clean-validation\20261002\equipment
Set-Location C:\opendev\clean-validation\20261002\equipment
python scripts/install_runtime.py --project equipment-onprem --port-offset 10000
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.lock
.venv/Scripts/python.exe -m playwright install chromium
```

The installer validates package/configuration hashes before generating fresh
Keycloak, observer and fixture-control credentials. They stay in ignored
`.runtime`; tokens and business databases are created there locally. No secrets
are printed or copied into reports. Reinstallation refuses an existing runtime.
Do not delete it to continue a run; preserve diagnostics and records first.

Project `equipment-onprem` uses host ports 28080 (Keycloak), 28081 (Java), 28082
(Python), 28083 (Sidecar), 28090 (fixture control), 29091 (Sidecar health), and
28765 (temporary PKCE callback). Choose a different project and port offset at
installation if these are occupied. Runtime bindings are loopback-only; this is
the agreed local reference environment, not an exposed production endpoint/TLS
deployment. Each project has its own network, volume, credentials and bind paths.

## Start and verify

All helpers select the same explicit Compose project and overlays, including
the provider-disabled overlay. Run from the installed directory:

```powershell
.venv/Scripts/python.exe -c "import sys,subprocess; sys.path.insert(0,'scripts'); from environment import compose; subprocess.run(compose()+['up','-d','--build'],check=True)"
.venv/Scripts/python.exe scripts/readiness.py
.venv/Scripts/python.exe scripts/login.py --user maya
.venv/Scripts/python.exe scripts/login.py --user luis
```

This launches the two reference applications, Sidecar, local Keycloak and the
fixture service. Readiness checks the expected issuer; PKCE uses the actual seeded
users and stores tokens locally without printing them. Both applications expose
the documented REST workflow. During this verification, offline scripts supply
the model responses; provider access stays disabled and no new model calls occur.

For status use the same helper command with `['ps']` instead of `['up', ...]`.
For logs use `['logs','--no-color']` and keep credentials out of exported output.
Do not use bare Compose commands with implicit project/configuration selection.
The installer does not stop or modify another project.

## Optional full offline acceptance

```powershell
.venv/Scripts/python.exe scripts/import_acceptance_inputs.py C:\path\to\supplied-evidence-bundle
.venv/Scripts/python.exe -u scripts/run_acceptance.py
```

The importer verifies transport and every retained evidence hash, imports only
evidence and writes `.runtime/retained-inputs.json` with its input classification.
Acceptance independently validates exact running package/configuration identities,
original scoped approvals and the retained live review. It then produces new
scenario captures, traces, journals, business records, JUnit and an aggregate
report under `evidence/acceptance-offline-*`. Keep all linked directories when
exporting that result. Fresh case IDs and fresh databases distinguish this run
from its supplied provenance. No skipped test or missing input is a passing result.

Record any setup failure and its fix. A runtime install with supplied binaries
proves that installation path, not a source rebuild or a published-asset install.
Java's stronger continuity-priority response remains inconclusive; full delivery
is not declared solely because offline acceptance passes. Load, publication,
restart, shutdown and CI remain outside this verification.
