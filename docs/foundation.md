# Phase 2 foundation

## Applications and skills

- `apps/java`: Spring Boot application embedding Framework, deterministic Java tools,
  persistent assessments/quotes/requests and authenticated public endpoints.
- `apps/python`: equivalent FastAPI business application, authenticated REST tools and
  calls to Sidecar for orchestration.
- `config/skills`: current model/planning skills (`resolveEquipment`, `assessEquipment`,
  `planResolution`, `compareOptions`) and compatibility skill.
- `config/rest-skills`: Sidecar declarations for the corresponding deterministic tools.
- `scripts/workflow_contracts.json` and `scripts/author_workflow.py`: current contract
  definitions and skill-generation tooling. Regeneration changes authored configuration;
  use deliberately during an agreed experiment, not as a startup prerequisite.
- `fixtures/server.py`, `fixtures/business.json`, `fixtures/base-case.json`: independent
  business source records and the local provider boundary. The fixture server's existing
  controlled-response support remains available; historical replay data is removed.

Both public apps expose assessments and service requests as well as Framework skill
execution endpoints. Java uses port 18081; Python uses 18082; Sidecar is on 18083.
The runtime guide lists infrastructure ports and isolated-workspace support.

Declared input/output bindings preserve source facts and authoritative results.
Eligible fully bound tasks dispatch directly; optional model input still leaves the
step model-driven. The current structure is a foundation to explore, not a prescribed
optimal decomposition for Phase 2.

## Business facts and interpretation

The fictional P240 revision-B sealer has recurrent E17 after warm-up, sensor replacement
and cleaning. A prior 20-minute test is shorter than the reported 35–50-minute onset.
Bulletin applicability supports investigation, not a confirmed defect. Qualified
personnel own diagnosis and return-to-service decisions.

Expedited attendance is the afternoon before production; standard attendance is after
the next morning's production start. Work can outlast normal site access. The compatible
loaner arrives in the evening and needs separately arranged access, approval and setup.
Offers expire before diagnosis, so continuity decisions cannot assume later availability.
The base case leaves restoration-risk preference unspecified.

Quoted service caps are $780 expedited and $480 standard, in integer USD cents on the
wire. The $300 expedited premium is included in its cap and payable on attendance even
if unresolved. Diagnosis/travel are included; actual authorized repair labor and installed
parts depend on findings, coverage and the approved scope/cap. Coverage remains pending
without qualifying findings. Elapsed work estimates do not enlarge approved repair hours.

Luis's recorded $1,000 ceiling accommodates either service cap after identity/permission
and explicit approval checks. The $2,400 loaner requires separate procurement approval.
An approved service request submitted before expiry preserves quoted scope/prices but
neither reserves resources nor books attendance. Changed scope/cap requires renewed
approval. Lost-result recovery and same-content idempotency use the persisted receipt.

The [source pack](equipment-service-source-pack.md) and current fixtures supply the
facts; these explanatory notes are not injected as a worked answer into model prompts.

## Current limits

The existing local runtime uses installed Framework 1.0.0-beta.8-SNAPSHOT and Sidecar
beta.2 source built against it. Both are local builds. Provider, mission and fixture-proxy
limits are 480, 2400 and 510 seconds. Normal model configuration remains Muse at medium
reasoning; retaining that default is not a model recommendation.

No Phase 2 experiment is complete yet. The historical evaluation machinery and semantic
reviewers are retired. The [shared runner](runner.md) now provides the four agreed modes
without an experiment-management layer. Its 19 provider-free tests cover orchestration,
failure/restoration paths and selected preservation checks; no live model run was made
to validate this implementation. The provider-free smoke check does not verify model judgment, full approval
recovery, every Framework feature or release readiness. Sidecar's pinned source tests
are not compatible with the installed Framework API; packaging currently skips those
tests, and the smoke check is no substitute for resolving full regression coverage.
