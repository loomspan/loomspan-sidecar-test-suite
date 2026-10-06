# Loomspan skill laboratory

Two equivalent equipment-service applications form the foundation for Phase 2:
Java embeds Loomspan Framework; Python/FastAPI uses Loomspan Sidecar. Their current
skills, configuration and business fixtures are retained unchanged.

Phase 2 explores skill composition and design to help less capable models succeed.
Specific experiments and paid runs are not selected yet. Phase 3 will turn the
result into long-term regression coverage and release confidence.

## Start here

- [Project agreement](docs/project-agreement.md): scope and working boundaries.
- [Foundation](docs/foundation.md): applications, skills, business rules and limitations.
- [Runtime guide](docs/runtime.md): start, build, smoke-check and package the apps.
- [Runner guide](docs/runner.md): mock, live, evaluate and capture through one entry point.
- [Business source pack](docs/equipment-service-source-pack.md): fictional domain evidence.

For the initialized local workspace:

```powershell
.venv/Scripts/python.exe scripts/readiness.py
.venv/Scripts/python.exe scripts/smoke.py
```

The smoke check uses both real integrations with provider access disabled. It checks
health, login, deterministic quotes and basic permission boundaries; it is not a
model evaluation or release-acceptance suite. It adds isolated smoke-test quote rows.

The historical Phase 1 test/evaluation/replay machinery, captures and archives have been retired.
The small shared runner in `scripts/run_suite.py` has no dependency on those archives.
Only its [purpose summary](docs/phase1-summary.md) and
[accomplishments](docs/phase1-accomplishments.md) remain as project history.
An independently verified recovery snapshot is outside the repository.
