# Named integration suites

A suite is a coherent example and integration-test boundary. A scenario is a set of
inputs within that suite; an integration is Java or Sidecar; a mode is mock, evaluate,
live or capture. The suites are `equipment-service` and `typesafe-ai`. There is still one Java host,
one Python host and one Sidecar instance, sharing authentication and fixture transport.

## Ownership

| Concern | Equipment-service location |
|---|---|
| Shared authored skills | `config/skills/equipment-service/` |
| Sidecar deterministic skill declarations | `config/rest-skills/equipment-service/` |
| Sidecar callback routes | `config/routes/equipment-service.yaml` |
| Java API, workflow completion, SkillMethods and business operations | `apps/java/src/main/java/example/suites/equipmentservice/` |
| Python API, workflow completion, callbacks, contracts and business operations | `apps/python/suites/equipment_service/` |
| Scenario inputs, checks, authoring tool and contracts | `scripts/suites/equipment_service/` |
| Runner registration and fixture ownership | `scripts/suites/registry.py` |
| Independent business records and base input | `fixtures/business.json`, `fixtures/base-case.json` |
| Frozen accepted replay | `fixtures/reference/` |

The last two rows intentionally keep their original paths. Accepted provenance and
source hashes remain valid; directory organization does not require rewriting a frozen
asset. Source generation (`scripts/seed_sources.py`) and reference validation/freezing
remain equipment-service helpers at their existing CLI paths. New suites should place
their own fixtures under `fixtures/<suite>/` and never reuse equipment records implicitly.

Java infrastructure owns execution state and authenticated invocation. Suite completion
handlers implement `CompletionHandler`; equipment assessment persistence lives there.
`EquipmentSkills` exposes the original annotated signatures and delegates to `Business`,
which retains business authorization and transaction rules. Java startup and security
configuration live in the common root `example.Application`.

Python infrastructure owns JWT authentication and Sidecar transport. The host mounts
suite routers and registers completion handlers; equipment workflow code validates and
persists its own completed result. Existing equipment endpoints remain available, with
aliases under `/suites/equipment-service`. Both hosts preserve their existing generic
`/v1` execution endpoints. Callbacks also have a prefixed Python alias; current Sidecar
routes retain their original paths for compatibility.

## Configuration and identity

Both hosts load `config/skills/*/*.yaml`; only Sidecar loads
`config/rest-skills/*/*.yaml`. Directories are ownership boundaries, not runtime
namespaces. Existing equipment skill identities remain unchanged. New suites must use
distinct runtime names, including deterministic Java method names, and distinct route
target names. Prefer a recognizable business prefix for new suite skills.
Spring bean identities must also be distinct: a second class named `Business` needs
an explicit suite-specific bean name, even when its Java package differs.

The documented Compose helper validates YAML skill-name collisions and assembles all
`config/routes/*.yaml` fragments into `.runtime/suite-routes.yaml`, Sidecar's single
mounted route catalog. Duplicate route/target names and unresolved targets fail before
startup. Do not hand-edit the generated file. Java callback names must match the
equivalent REST declarations; the YAML collision check is not a Java source analyzer.

Trial model aliases are separate from normal aliases. Overrides rewrite only the
selected suite's temporary skill copies, preserving other suites' skill contents and
model definitions. Normal runtime remains provider-disabled.

## Adding another suite

1. Define its business purpose, Loomspan capabilities exercised, scenarios and evidence
   limits. Keep both implementations equivalent; do not copy the entire applications.
2. Add skill directories and, when callbacks are needed, REST directories and a route fragment with distinct identities. Add Java
   suite packages, Python modules and host registrations. Use prefixed HTTP routes.
3. Add suite-owned inputs and checks. Register a `Suite` in `scripts/suites/registry.py`
   with supported modes, entry skill, endpoint, database/table ownership, source files
   and optional reference loader. Its scenario adapter supplies inputs, result decoding,
   trace payload extraction, review areas, business checks and preservation checks.
4. Keep persistence separate by database or table ownership. The shared runner currently
   supports SQLite row snapshots and the existing asynchronous execution/trace protocol.
   TypeSafe uses the optional `mock_runner` adapter to exercise native transport without
   equipment persistence. The catalog does not claim arbitrary workflow support.
5. Add deterministic tests and, where appropriate, independently reviewed frozen responses.
   A suite without mock support must reject that mode; `--suite all` must not omit it.

The fixture server's current `/records` source endpoint serves equipment-service records.
A second domain must add its own fixture routing explicitly. Shared authentication
currently uses the equipment audience and identities; new permission tests must define
their intended grants rather than assuming directory contacts confer authority.

Run `scripts/run_suite.py mock --suite equipment-service` or `--suite all`. Results go
under `evidence/latest/<suite>/`; the root summary identifies the current selection.
An unselected suite directory may contain an older run. Scenarios passed with `all`
must exist in every selected suite. Per-skill model overrides require one selected suite.
See [runner](runner.md) for modes, paid authorization and retention.

## Evidence limits

This extraction preserves the original eight-skill model assignment, business handoffs
and frozen reference. It introduces no new reasoning method or cost-optimization claim.
Synthetic adapter tests check grouping and isolation. TypeSafe adds a second coherent
example with deterministic protocol coverage; real model judgment in that example
remains unverified. Phase 3 release-confidence scope remains future work.

The 2026-10-11 extraction passed the Java package build, 65 provider-free tests,
both-integration smoke and all eight frozen replay cases (240 checks). All 18 regenerated
skill/route configurations matched the authored configuration. The 17 relocated skill
declarations and frozen reference contents remained unchanged. Replay reported zero
paid calls and zero cost; provider access stayed disabled. This is preservation evidence,
not fresh model evaluation or full service-request regression.

## TypeSafe boundary

The [customer-support triage suite](typesafe-ai.md) owns `config/skills/typesafe-ai`,
`fixtures/typesafe-ai`, `scripts/suites/typesafe_ai`, Java package
`example.suites.typesafeai` and Python module `suites.typesafe_ai`. It uses no business
tables or callbacks and therefore has no REST-skill directory. Its runtime names use
the `tsTriage` prefix. Parent coordination still uses the shared local chat fixture
transport; native leaves use a separate strict System One endpoint in `fixtures/typesafe.py`.

`typesafe-ai` mock reports `PROTOCOL_PASS`; equipment mock reports `REPLAY_PASS`.
`mock --suite all` runs both with separate evidence. TypeSafe's separate live runner
supports predeclared direct-native live cases and pins the model; paid native runs
must select a single suite, with at most 12 sends per batch. Captures require semantic
review; the user delegated TypeSafe acceptance to the assistant. The fixture packs
have different origins and must not be promoted, replaced or described interchangeably.
