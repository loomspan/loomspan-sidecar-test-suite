# SDK foundation lane

This separate lane builds the actual neighboring Sidecar checkout with its pinned
Framework beta.8 dependency and locally installs its Java SDK reactor. It does
not rebuild Framework. The retained embedded beta.9 and beta.3-source
Python/Sidecar business lanes keep their existing commands, configuration and data.

Prerequisites: Java 21 through `JAVA_HOME`, Maven and Docker on PATH, the normal
suite Python environment (including httpx, PyYAML and cryptography), and a
resolvable/installed Framework `1.0.0-beta.8`. Public Maven downloads and container
image pulls may occur. Provider credentials are unnecessary.

From this suite checkout:

```powershell
.venv/Scripts/python.exe scripts/run_sdk.py local
.venv/Scripts/python.exe scripts/run_sdk.py local --sidecar-checkout C:/opendev/code/loomspan-sidecar
.venv/Scripts/python.exe scripts/run_sdk.py standard
.venv/Scripts/python.exe scripts/run_sdk.py hardened
```

`local` selects only `foundation-smoke`. It runs root `clean verify` (including
tests), SDK `clean install`, and builds the actual checkout's Dockerfile. Its own
two-service Compose project uses an internal network, temporary file configuration
and tmpfs database, and a deterministic OpenAI fixture with no forwarding path.
Readiness is polled over container-local HTTP using the image's curl; neither
service publishes host ports. No business state or existing credentials are mounted.
Host provider/Java option variables
are not passed to child tools or containers.

Smoke requires readiness `UP`, a normal Sidecar stop with exit 0 or 143, Spring's
graceful-shutdown completion marker, and zero fixture model requests. It tears down
only its unique Compose project. The locally built Docker image remains available
under its unique `loomspan-sdk-smoke:sdk-...` tag; there are no persistent SDK
containers, networks or databases. This proves startup/lifecycle of the packaged
revision; SDK invocation and client behavior belong to subsequent feature tickets.
It adds no public placeholder SDK API or recipe security claims.

`standard` and `hardened` are recognized but currently have no scenarios. They
exit nonzero with `no-scenarios-for-recipe` and write explicit failed evidence.
Future tickets implement those recipe scenarios.

Every valid invocation creates `evidence/sdk/<unique-run-id>/report.json`. Use
`--output NEW_DIRECTORY` to select a different new destination; existing directories
are refused. Reports include recipe/scenarios, Git revision and dirty state,
packaged Sidecar SHA-256, Framework version read from the packaged JAR, SDK
coordinates/hashes, each build/runtime stage, readiness, graceful exit and cleanup.
Unavailable identities remain null. A dirty revision is identified by its build
hashes as well as HEAD; HEAD alone does not describe uncommitted build inputs.

Reports are initialized before preflight and atomically finalized after success,
failure or interruption. Failed commands expose fixed diagnostic categories,
never raw output, exceptions, container logs, credentials, private keys or payloads.
The private half of the temporary verification key is never serialized. If normal
shutdown fails, successful cleanup does not turn the smoke into a pass. Cleanup
failure also fails the run and preserves any primary failure.

Local harness checks:

```powershell
.venv/Scripts/python.exe -m pytest tests/test_sdk_runner.py -q
ruff format --check scripts/run_sdk.py scripts/sdk_lane tests/test_sdk_runner.py
ruff check scripts/run_sdk.py scripts/sdk_lane tests/test_sdk_runner.py
```

No development-data reset is required. Maintained fixture/reference packs and
the existing five-service runtime are outside this composition.
