# Loomspan skill laboratory

Two equivalent equipment-service applications form the foundation for Phase 2:
Java embeds Loomspan Framework; Python/FastAPI uses Loomspan Sidecar. They share
the experimental skills and retain equivalent business behavior and source fixtures.

Phase 2 explores business-process skill composition and model assignment. The
skill tree must remain recognizable to business readers. First find the lowest
reasonable model tier that passes the full readable workflow. If that requires a
higher tier, preserve the working baseline and test lower-tier assignments for
selected business responsibilities. If a lower tier already succeeds, keep the
simple assignment. Skill-specific needs can also justify a mixed pack with higher
tiers only where stronger reasoning or specialist capabilities are required, and
lower tiers elsewhere. Model candidates will change over time. See the project
agreement before new experiments. Java remains first; paid Sidecar is deferred.

The current skills are a cleaned, business-readable baseline: responsibilities
and methods precede separate Framework instructions. The complete-offer redesign
preserves business responsibilities, public output shapes and model defaults while
revising input contracts and handoffs. Provider-free validation and four-case
Java Luna/medium and Sol/medium evaluations are complete. See the
[prepared baseline](docs/foundation.md#prepared-business-readable-baseline).

Two unchanged Java repeats of the six-Sol/two-Luna confirmation are complete.
Sol/medium handled technical assessment, all four feasibility skills and comparison;
Luna/medium retained resolveEquipment and planResolution. Across eight cases, all
216 structural checks passed, handoffs were exact, and 120 responses were valid
JSON with no corrections. Total reported cost was $1.408069770: 48 Sol calls and
72 Luna calls. Including the preceding confirmation, this version cost $2.111810165
across three batches; these are observed costs, not stable performance estimates.

The elapsed-time/repair-scope correction held throughout both repeats. One repeat
passed business review with minor caveats; the other did not: capacity-shortfall's
replacement finding questioned whether its supplied expiry applied, despite explicit
offer metadata. Comparison left that misleading deadline condition unresolved.
Seven of eight complete results were materially acceptable, but this is not a
statistical reliability estimate or complete workflow repeatability. See the
[repeat review](docs/foundation.md#two-unchanged-mixed-repeats--2026-10-07).

The current redesign supplies complete offer records and makes
comparison responsible for material accuracy across all published findings, including
deferred options. Both hosts preserve source details and attach exact service quotes
without changing the business tree or model defaults. All 44 provider-free tests and
both disabled-provider smoke checks passed. The first Java confirmation on this
revision passed all four business cases with minor caveats: 108/108 structural checks,
exact complete-offer handoffs, and 60 valid JSON responses without corrections.
The six-Sol/two-Luna medium assignment cost $0.729449095 (24 Sol calls, 36 Luna calls).
The earlier expiry and elapsed-time/scope defects did not recur. This is a single-batch
pass, not demonstrated consistency. See the
[offer and review redesign](docs/foundation.md#complete-offers-and-publication-review--2026-10-07).

That trial exposed unnecessary questions about the quote's `attendance` label versus
source `arrival`. The shared schemas now explicitly define attendance as the offered
technician arrival window, with exact-copy approval semantics. Both hosts' source-window
preservation is checked; genuine loaner setup uncertainty remains. This description-only
clarification passed provider-free checks and a fresh Java trial costing $0.711329490.
All four cases passed business review with one explicit correction and minor caveats:
108/108 structural checks, 60 valid JSON responses and no schema retries. Comparison
corrected a loaner timing error from 8–10 to 10–12 hours and clearly superseded the
original finding. That is one observed successful correction, not established reliability.

The intended clarification did not reach the affected models: request inspection
found the new description in coordinator calls, but in no service-assessor or
comparison call. Priority expedited still asked the unnecessary arrival/attendance
question. The definition is now included in the shared business instructions of both
service assessors and comparison. Provider-free probes verified its presence in all
six actual consumer request paths across Java and Sidecar; the local fixture rejected
every request before provider access, with no model responses or business-row changes.
All 44 tests and both regular smoke checks passed. The subsequent Java confirmation
cost $0.702841970: 108/108 checks passed, 60 responses were valid JSON with no schema
retries, and the definition reached all 12 intended consumer calls. The unnecessary
service-window question did not recur; genuine loaner setup uncertainty remained.

Full business acceptance is withheld: three cases passed, but later-start comparison
incorrectly superseded a supported part-price explanation with an uncertainty despite
receiving the manual's part identities and rate card. The primary decisions remained
defensible. Retain the targeted clarification; next review the quote/comparison boundary
provider-free, including whether authoritative quote itemization would help. No further
paid run is authorized. See the
[latest confirmation](docs/foundation.md#consumer-definition-java-confirmation--2026-10-07),
[consumer delivery check](docs/foundation.md#consumer-visible-service-window-definition--2026-10-07),
[attendance confirmation](docs/foundation.md#attendance-clarification-java-confirmation--2026-10-07)
and the preceding
[confirmation review](docs/foundation.md#complete-offer-java-confirmation--2026-10-07).

Provider access is disabled. Model defaults and `evidence/accepted` remain unchanged. Latest findings are in `evidence/latest/business-review.json`, with
consolidated observations in `evidence/validation-review.json`. No repeatability
claim or paid Sidecar evaluation is made.

The itemized-quote refinement passed its confirmation and **one unchanged Java
repeat**, all eight business cases with minor caveats. The repeat cost $0.718357850;
combined cost was $1.437386975. All 216 structural checks passed and 120 responses
were valid JSON without schema corrections. Supported prices and timing distinctions
held; owner precision and some ambiguous or redundant wording remain documented.
This is bounded repeated success on fixed cases, not general reliability. Retain
the six-Sol/two-Luna candidate and stop paid testing here; the user chose one repeat
to limit accumulating cost and emphasized diminishing returns from further tier tuning.
Provider access is disabled and accepted evidence remains unchanged. See the
[itemization review](docs/foundation.md#issued-quote-itemization-and-evidence-reconciliation--2026-10-07),
[confirmation](docs/foundation.md#itemized-quote-java-confirmation--2026-10-07) and
[single repeat](docs/foundation.md#one-unchanged-itemized-quote-repeat--2026-10-07).

## Start here

- [Project agreement](docs/project-agreement.md): scope and working boundaries.
- [From business processes to reliable skills](docs/mid-tier-skill-design.md): living
  best-practice guide for decomposing processes into skills for mid-tier models.
- [Foundation](docs/foundation.md): applications, skills, business rules and limitations.
- [Human business contract audit](docs/foundation.md#human-business-contract-audit):
  current boundaries and instructions to keep, simplify or reconsider.
- [Independent baseline review](docs/foundation.md#independent-review-of-the-prepared-baseline--2026-10-06):
  remaining tradeoffs, cleanup findings and the proposed four-case Java trial.
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
