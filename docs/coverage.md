# Capabilities and integration coverage

This repository is a QA suite and staging ground for complex Loomspan integrations.
Organize checks by the contract they verify, not by the PR that introduced them.
Run against a coherent current build: the Java business host embeds Framework,
while the Python business host uses the installed SDK and Sidecar. Separate SDK
consumers exercise Java and Python SDK behavior. Business equivalence does not
establish SDK parity, and equivalent permissions and outcomes do not require
identical framework APIs or execution envelopes.

## Coverage map

| Capability | Maintained entry point | What it establishes and its limits |
|---|---|---|
| Application contracts and harness behavior | `python -m pytest tests -q`; `mvn -B -ntp -f apps/java/pom.xml test` | Provider-free adapter, identity, policy, fixture matching, runner and packaging checks; Java policy tests. These do not replace deployed integration checks. |
| Deployed identity, callbacks and deterministic business operations | `scripts/smoke.py` | Both hosts, real login, exact quotes/offers, permissions, nested business rejection and mounted artifact/configuration checks. No model calls; adds two synthetic quotes per host. |
| Equipment assessment and result fidelity | `scripts/run_suite.py mock --suite equipment-service` | All four frozen scenarios on both hosts, strict response consumption, accepted results and persistence. Adds synthetic assessments/quotes; no service commitment or new model judgment. |
| TypeSafe Decisions SkillExecutor and application policy | `scripts/run_suite.py mock --suite typesafe-ai` | Full authored and reviewed catalog on both hosts, including native envelopes, bindings, impact decisions, validation, retry diagnostics and Framework accounting. See [TypeSafe coverage](typesafe-ai.md). |
| Service commitment and recovery | `scripts/verify_equipment_commitment.py --output NEW_DIRECTORY` | Both-host approval, owner recovery, exact repeat and conflicting repeat handling. Requires a disposable isolated runtime; writes a pending request per host. Bounded business coverage, not a complete commitment matrix. |
| SDK execution, authentication and lifecycle | `scripts/run_sdk.py local`; `scripts/run_python_sdk.py local` | Separate Java and Python SDK consumers, execution credentials, callback authentication, current trust and expiry. Inventories differ by consumer; see [SDK coverage](sdk-lane.md). |
| Verified transport and response-loss behavior | Both SDK runners with `standard` and `hardened` | Direct HTTPS and paired Caddy mTLS, rejection paths, isolation and bounded no-replay checks. Disposable projects; no certificate lifecycle or exactly-once guarantee. |
| New model judgment and complex live workflows | Explicitly scoped `evaluate`, `live` or `capture` selections | Staging with provider access requires a separately authorized scope and semantic review. Never implied by regression verification. |

Commands above use the workspace Python environment. SDK commands need the artifact
and output arguments documented in [SDK coverage](sdk-lane.md). Business scenario
selection and evidence semantics are in the [runner guide](runner.md).

## Provider-free regression sequence

Build and stage a coherent runtime using the [runtime guide](runtime.md) when code
or dependencies change. Do not rebuild or prepare credentials solely to reorganize
documentation. Against an initialized runtime:

```powershell
.venv/Scripts/python.exe -m pytest tests -q
mvn -B -ntp -f apps/java/pom.xml test
.venv/Scripts/python.exe scripts/start.py
.venv/Scripts/python.exe scripts/smoke.py
.venv/Scripts/python.exe scripts/run_suite.py mock --suite all --output evidence/NEW_REGRESSION
```

`--suite all` selects all registered business suites, not every SDK, transport or
commitment check in this repository. The full integration inventory includes those
separate checks. Run the affected SDK recipes for SDK/transport changes and the
isolated commitment check for approval/persistence changes. A focused run must name
what it selected and what remains unverified; never describe it as full acceptance.
Use all layers when seeking broad integration confidence, without enabling providers.

Do not run smoke, builds or other runtime-changing checks concurrently with business
replay. Replay owns the workspace lock and restores provider-disabled configuration.
Use fresh output directories to preserve existing evidence. Preserve credentials,
operational databases and every maintained fixture pack; normal checks may append
their documented synthetic records, never reset existing data.

## Maintaining coverage

Add a regression to its existing capability or business scenario when it exposes
a missing contract. Reuse composed scenarios; keep detailed variants in component
tests. Keep capability names in scripts, temporary project names and reports.
Fix tickets belong in the owning product repository. Historical PR references and
past evidence may remain as provenance, but do not define test selection or status.

Reports identify the tested artifacts, configuration, selected scenarios, outcomes
and evidence limits. A previous green report is evidence for its recorded build,
not an automatic pass for the current codebase. This map describes maintained
coverage, not a new release-certification claim or a change to the frozen fixtures.
