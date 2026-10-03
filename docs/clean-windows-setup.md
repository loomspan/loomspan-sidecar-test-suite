# Clean Windows setup validation

**Superseded historical plan:** the user selected Docker Compose only and a
separate project on this host, installed as an on-prem operator would use it.
Follow [the verified runtime procedure](on-prem-runtime.md) and
[setup evidence](../evidence/clean-compose-20261002/summary.md). Do not provision
Hyper-V/cloud resources. The VM procedure below was prepared but never executed;
a same-host project does not establish a clean Windows/toolchain installation.

This procedure targets a **separate disposable Windows VM**. It must never run in
the retained workspace. Preparation is not clean-setup acceptance. The current
preparation findings are in [the evidence bundle](../evidence/clean-setup-preparation-20261002/summary.md).

## Environment and supplied inputs

Have an administrator supply a Windows VM with its own user home, virtual disk,
network and Docker Desktop Linux engine. The VM must support the virtualization
needed by Docker Desktop. Allocate resources without starving the retained stack;
16 GB RAM, four virtual CPUs and 100 GB available guest storage are planning
estimates, not measured minimums. The present host has only about 17 GB free and
its current session cannot manage Hyper-V. Do not reclaim retained evidence or
stop its stack to make space. A separate host is an acceptable VM location.

Supply Windows installation media/licensing and administrator access for guest
installation. Record actual guest OS, Docker Desktop/engine/Compose, Git, JDK,
Maven and Python versions. The retained toolchain is Python 3.13.13, Maven 3.9.6,
JetBrains JDK 21.0.2, engine 29.8.1 and Compose v5.5.1. Those observed versions
are reproduction targets, not proof that installers remain available. Set
`JAVA_HOME` explicitly; the retained shell finds Java through Maven, not PATH.

Export the inputs from the retained workspace, without preparing or rebuilding it:

```powershell
.venv/Scripts/python.exe scripts/prepare_clean_inputs.py --output evidence/clean-inputs-NEW
```

The new directory contains Git bundles for the suite, Framework and Sidecar;
`workspace-inputs.zip` with exact current suite bytes (including uncommitted audit
work) and retained evidence; `input-inventory.json` with per-file hashes and input
classification; and `checksums.json` for the transport files. Keep this checksum
index alongside the separately transferred archive and verify it before extraction.
The inventory follows existing evidence references, including rejected regression
captures, scoped approvals, live-phase archives and protected source hashes.
It is intentionally conservative; all transferred evidence remains an input.

Framework is pinned to `900cc86bc2ba619d38647688008b138a07108af6`, with beta.7's tag
also supplied because `prepare.py` checks it. Sidecar beta.2 is pinned to
`da3bb8f8ae6087955f9b3a6bd02b9706d3b582e7`. The suite's exact revision and working
changes are in the inventory. A clone alone is insufficient.

No runtime secrets, tokens, databases, Docker volumes, Python environment or Maven
settings/cache are supplied. Historical JSON business-record snapshots are retained
review evidence only; never import them as guest databases. The reference baseline
is under `clean-input-reference`, not active `.runtime`. Pinned Python packages,
Playwright Chromium, Maven dependencies/plugins, container images and Sidecar's
apt packages still require registry access. Model-provider access remains disabled.
Record resolution/download failures; do not silently loosen versions. Python has
version pins but no wheel hashes, and Sidecar's curl installation is not apt-version
pinned; record actual resolved artifacts. This is not an air-gapped installation.

## Guest-only preparation and build

Use a fresh `C:\clean-validation` directory in the guest and put the supplied
transport directory at `C:\clean-inputs`. In PowerShell, stop after any nonzero
native command exit code; PowerShell does not do that automatically. Capture
command, exit code and redacted stdout/stderr for every step in a new guest evidence
directory. Do not record environment dumps, Compose rendered secrets or tokens.

```powershell
$ErrorActionPreference = 'Stop'
Remove-Item Env:LOOMSPAN_OPENROUTER_API_KEY -ErrorAction SilentlyContinue
Remove-Item Env:OPENROUTER_API_KEY -ErrorAction SilentlyContinue
$inputRoot = 'C:\clean-inputs'
$hashes = Get-Content "$inputRoot\checksums.json" -Raw | ConvertFrom-Json
foreach ($entry in $hashes.PSObject.Properties) {
    if ((Get-FileHash -LiteralPath (Join-Path $inputRoot $entry.Name) -Algorithm SHA256).Hash.ToLower() -ne $entry.Value) { throw "Input checksum mismatch: $($entry.Name)" }
}
New-Item -ItemType Directory C:\clean-validation
Set-Location C:\clean-validation
git clone C:\clean-inputs\framework.bundle loomspan-framework
git clone C:\clean-inputs\sidecar.bundle loomspan-sidecar
git clone C:\clean-inputs\suite.bundle loomspan-sidecar-test-suite
Set-Location loomspan-sidecar-test-suite
# Restore exact working bytes after clone, avoiding Git CRLF conversion differences.
Expand-Archive C:\clean-inputs\workspace-inputs.zip -DestinationPath . -Force
```

Verify every `input-inventory.json` file SHA256 after extraction with the same
`Get-FileHash` comparison, resolving names beneath the guest suite root. Assert the
Framework/Sidecar revisions above and a clean working tree in those two source
repositories. Record the suite overlay status; it is expected and hash-bound.

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.lock
.venv/Scripts/python.exe -m playwright install chromium
.venv/Scripts/python.exe scripts/prepare.py
New-Item -ItemType Directory .build/sidecar-1.0.0-beta.2-framework-beta.8-SNAPSHOT
git -C ../loomspan-sidecar archive --format=tar --output=../loomspan-sidecar-test-suite/.build/sidecar-snapshot-source.tar v1.0.0-beta.2
tar -xf .build/sidecar-snapshot-source.tar -C .build/sidecar-1.0.0-beta.2-framework-beta.8-SNAPSHOT
mvn -B -ntp -f ../loomspan-framework/pom.xml -DskipTests clean install
mvn -B -ntp -f apps/java/pom.xml '-Dloomspan.version=1.0.0-beta.8-SNAPSHOT' clean package
mvn -B -ntp -f .build/sidecar-1.0.0-beta.2-framework-beta.8-SNAPSHOT/pom.xml '-Dloomspan.version=1.0.0-beta.8-SNAPSHOT' -DskipTests clean package
.venv/Scripts/python.exe scripts/record_snapshot_build.py
```

`prepare.py` generates fresh local credentials and a fresh realm import. Its release
exports are prerequisites, not the snapshot build. Framework/Sidecar builds above
skip their tests; the suite acceptance results must be reported separately.
Do not run `seed_sources.py` or `author_workflow.py` over supplied configuration as
a setup step. These outputs are already supplied and hash-bound. Check regeneration
in scratch space (`test_workflow_generation.py` does this for workflow YAML), then
compare the full generated bytes before accepting any proposed change.

## Identity gate before startup

Compare the newly generated `.runtime/build-baseline.json` with
`clean-input-reference/build-baseline.json`: `installedFrameworkSha256`, both
`artifacts`, all `configurationSha256`, Framework/Sidecar commits and timeout/quota
settings must match. Keep both records. Do not copy the reference over the new
baseline or overwrite original evidence.

The existing live audit intentionally requires exact host JAR hashes. A fresh Maven
build may change ZIP timestamps, build metadata or dependency bytes. If identity
differs, stop before deployment and compare ZIP entry names, uncompressed entry
hashes, timestamps, manifests, embedded POMs and dependency versions against the
retained packages. Obtain comparison artifacts separately by their recorded hashes
if needed; never substitute them silently for the guest build. Matching source or
class files alone does not establish exact package identity. Record the cause and
any supported reproducible-build fix; do not weaken the audit or edit approved
captures. Baseline selection requires a documented disposition of this mismatch.

## Guest-only execution and evidence

After the identity gate passes, create fresh runtime directories and start every
service with the offline overlay from its very first startup:

```powershell
New-Item -ItemType Directory .runtime/java,.runtime/python,.runtime/fixture -Force
docker compose --env-file .runtime/compose.env -f compose.yaml -f compose.snapshot.yaml -f compose.offline.yaml up -d --build
.venv/Scripts/python.exe scripts/readiness.py
.venv/Scripts/python.exe -c "import sys; sys.path.insert(0,'scripts'); from capture_reviewed_replay import require_offline_provider; require_offline_provider(); print('Provider disabled')"
.venv/Scripts/python.exe scripts/login.py --user maya
.venv/Scripts/python.exe scripts/login.py --user luis
.venv/Scripts/python.exe -u scripts/run_acceptance.py
```

Keep the offline overlay on every later Compose invocation. Do not run historical
`capture.py`, compatibility/live commands or fixture curation for this validation.
PKCE tokens stay in ignored guest runtime. Fresh credentials and empty application
databases must originate in the VM, with new case IDs and guest-produced traces.

Retain the input inventory, toolchain and resolved artifact identities, command
logs/exit codes, failures/fixes, identity comparisons, readiness/PKCE outcomes and
the new acceptance bundle with every linked capture and preservation archive.
Keep imported evidence marked `retained-evidence-input`; label new outputs
`fresh-VM-result`. Export results before disposing of the VM, without credentials or
runtime databases. Revalidate transferred checksums. The expected prior checkpoint
is 311 checks/56 assertions/86 focused tests; only newly observed results can close
clean setup. Java's stronger continuity-priority response remains inconclusive,
and broader load/publication/restart/shutdown/CI remain outside this task. A green
offline command alone does not declare full delivery.
