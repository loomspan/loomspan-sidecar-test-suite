# Loomspan integration suites

This workspace is a QA suite and staging ground for complex Loomspan integrations.
Coverage is organized by business capabilities, SDK contracts and deployment recipes,
not implementation PRs. It retains equivalent Java/Framework and Python/Sidecar
business applications and the selected six-Sol/two-Luna model pack at medium reasoning.
Provider access is disabled by default.

The process gathers technical evidence, assesses four service/continuity options,
compares them and publishes a recommendation. Creating a service request is a separate,
authenticated action requiring explicit approval; assessment never books service.

The workspace hosts named integration suites in one Java app and one Python/Sidecar
app. `equipment-service` retains the accepted business example; `typesafe-ai` exercises
the Decisions TypeSafe SkillExecutor for Choice, Noul and Score through customer-support triage. See [TypeSafe coverage](docs/typesafe-ai.md)
and [suite boundaries](docs/suites.md)
for the layout, selection and extension contract.

## Start here

- [Coverage map](docs/coverage.md): capabilities, verification entry points and evidence limits.
- [Project agreement](docs/project-agreement.md): settled scope and boundaries.
- [Foundation](docs/foundation.md): architecture, skill ownership and business rules.
- [Runtime guide](docs/runtime.md): start, build, verify and package both integrations.
- [SDK integration coverage](docs/sdk-lane.md) covers the Java consumers and the installed Python client and FastAPI callback recipes over HTTP, direct HTTPS and paired Caddy mTLS.
- [Phase 2 summary](docs/phase2-summary.md): journey, destination and validation limits.
- [Skill-design lessons](docs/mid-tier-skill-design.md): transferable practices and evidence limits.
- [Business source pack](docs/equipment-service-source-pack.md): independent fictional records.
- [Runner guide](docs/runner.md): explicitly authorized future evaluations.
- Phase 1 [purpose](docs/phase1-summary.md) and [accomplishments](docs/phase1-accomplishments.md).

```powershell
.venv/Scripts/python.exe scripts/start.py
.venv/Scripts/python.exe scripts/smoke.py
.venv/Scripts/python.exe -m pytest tests -q
.venv/Scripts/python.exe scripts/run_suite.py mock --suite all --output evidence/NEW_REGRESSION
```

`--suite all` runs both business suites, not the separate SDK recipes or isolated
commitment check. Use the coverage map to select those checks. Phases 1 and 2 are
completed business-development history, not test-suite partitions.

The smoke check uses both real integrations without model calls. It invokes all eight
lookup operations and verifies nested approval parsing/business rejection without a
service commitment. It verifies pricing,
complete offers, mounted model assignments and basic permission boundaries; it adds
isolated quote rows. These checks are not full release acceptance.

The Python host uses the installed Loomspan SDK for execution and callbacks.
The [runtime guide](docs/runtime.md) shows how to build and stage the wheel with
the two Java runtime packages. A separate commitment check uses frozen assessment
responses and writes one synthetic pending service request per host in a disposable
runtime.

In the historical Phase 2 evaluation, the selected pack passed a four-case Java
confirmation and one unchanged repeat:
eight business passes with minor caveats, 216 structural checks and 120 valid JSON
responses without schema corrections. Combined reported cost was $1.437386975.
This is bounded evidence for the reference process, not broad production reliability.
Paid Sidecar and full service-request regression were outside that historical validation.
The [beta.10 evaluation record](docs/beta10-evaluation.md) covers the subsequent direct
OpenAI Responses migration, fresh Java/Sidecar model comparisons and remaining gates.

Historical results, traces, diagnostic skills and one-off experiment helpers have
been retired after an external verified recovery snapshot. Ordinary operation does
not depend on them. Phase 3 and additional mid-level examples require separate scope.

The final accepted Sol/Luna responses are retained separately as maintained
[deterministic fixtures](fixtures/reference-responses/README.md). `mock` runs all four cases on
both real integrations, with zero paid calls, and checks the published results against
the frozen reference. This verifies runtime regression behavior, not new model judgment.

The TypeSafe suite uses 49 authored protocol fixtures, 10 primitive and mixed
responses from the [original reviewed pack](fixtures/typesafe-ai/reference/README.md),
and 36 [reviewed evidence responses](docs/partial-outage-evidence-review.md), pinned
`jev-1.13.0`, and Framework `1.0.0-beta.10-SNAPSHOT` in both hosts. Its mock results test
integration fidelity; the linked review records semantic acceptance and limits.
The example also exposes an [application impact policy](docs/typesafe-ai.md#application-impact-policy)
that requests clarification when evidence is insufficient, plus parent-composition tests
using the recorded real responses.
Local authoring skills are installed under
`.agents/skills`; see the runtime guide for source pins and build instructions.
