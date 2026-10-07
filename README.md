# Loomspan equipment-service reference runtime

Phases 1 and 2 are complete. This workspace retains the working equipment-service
example, equivalent Java/Framework and Python/Sidecar integrations, and the selected
six-Sol/two-Luna model pack at medium reasoning. Provider access is disabled by default.

The process gathers technical evidence, assesses four service/continuity options,
compares them and publishes a recommendation. Creating a service request is a separate,
authenticated action requiring explicit approval; assessment never books service.

## Start here

- [Project agreement](docs/project-agreement.md): settled scope and boundaries.
- [Foundation](docs/foundation.md): architecture, skill ownership and business rules.
- [Runtime guide](docs/runtime.md): start, build, verify and package both integrations.
- [Phase 2 summary](docs/phase2-summary.md): journey, destination and validation limits.
- [Skill-design lessons](docs/mid-tier-skill-design.md): transferable practices and evidence limits.
- [Business source pack](docs/equipment-service-source-pack.md): independent fictional records.
- [Runner guide](docs/runner.md): explicitly authorized future evaluations.
- Phase 1 [purpose](docs/phase1-summary.md) and [accomplishments](docs/phase1-accomplishments.md).

```powershell
.venv/Scripts/python.exe scripts/start.py
.venv/Scripts/python.exe scripts/smoke.py
.venv/Scripts/python.exe -m pytest tests -q
.venv/Scripts/python.exe scripts/run_suite.py mock
```

The smoke check uses both real integrations without model calls. It verifies pricing,
complete offers, mounted model assignments and basic permission boundaries; it adds
isolated quote rows. These checks are not full release acceptance.

The selected pack passed a four-case Java confirmation and one unchanged repeat:
eight business passes with minor caveats, 216 structural checks and 120 valid JSON
responses without schema corrections. Combined reported cost was $1.437386975.
This is bounded evidence for the reference process, not broad production reliability.
Paid Sidecar and full service-request regression remain outside that validation.

Historical results, traces, diagnostic skills and one-off experiment helpers have
been retired after an external verified recovery snapshot. Ordinary operation does
not depend on them. Phase 3 and additional mid-level examples require separate scope.

The final accepted Sol/Luna responses are retained separately as maintained
[deterministic fixtures](fixtures/reference/README.md). `mock` runs all four cases on
both real integrations, with zero paid calls, and checks the published results against
the frozen reference. This verifies runtime regression behavior, not new model judgment.
