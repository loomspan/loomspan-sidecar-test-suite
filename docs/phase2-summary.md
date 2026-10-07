# Phase 2: journey and destination

Phase 2 concluded on 2026-10-07. Its purpose was to turn a demanding equipment-service
process into a readable skill tree and find a practical model assignment that could
execute it with materially correct business outcomes.

## What we learned along the way

Early lower-tier runs often executed correctly while mishandling technical evidence,
timing, financial exposure or approval boundaries. Stronger-model runs improved core
judgment but also exposed business defects; there was no flawless all-Sol oracle.
Structural success and valid JSON could not substitute for business review.

The useful changes clarified coherent responsibilities and their evidence: per-option
feasibility, complete offer records, source-linked owners, explicit service conditions,
authoritative price itemization, and final review of all published material claims.
Runtime bindings preserved facts and findings instead of asking models to reconstruct
large handoffs. Business methods were separated from Framework instructions.

Consumer visibility mattered: a definition in an input schema did not necessarily reach
the model that needed it. Actual request checks established delivery before further
trials. Even with correct delivery, final review could introduce a false correction;
corrections themselves need source-based review.

The practical destination is mixed assignment. Further tier optimization can have
diminishing returns once authoring and review effort are counted. Preserve the human
business process and use capability where needed rather than keep reshaping work to
minimize stronger-model calls. This is a project lesson, not a universal cost threshold.

## Selected runtime

All eight reasoning skills use medium reasoning.

| Model | Responsibilities |
| --- | --- |
| Sol (`openai/gpt-6-sol`) | assessEquipment; assessExpeditedFeasibility; assessStandardFeasibility; assessLoanerFeasibility; assessReplacementFeasibility; compareOptions |
| Luna (`openai/gpt-6-luna`) | resolveEquipment; planResolution |

The final methods, contracts and source facts are retained. During cleanup, the same
validated assignment replaced the unused Muse default in both hosts and the generator.
No new business method or model evaluation is implied by making the assignment permanent.

## Validation at phase close

A four-case Java confirmation and one unchanged repeat covered baseline, continuity
priority, a loaner capacity shortfall, and a later production start. All eight results
passed business review with minor caveats; all 216 structural checks passed; all 120
responses were valid JSON with zero schema corrections. Exact handoffs, itemized quotes,
publication and selected routing were checked. Each batch used 24 Sol and 36 Luna calls.

| Batch | Reported cost |
| --- | ---: |
| Confirmation | $0.719029125 |
| One unchanged repeat | $0.718357850 |
| Combined | $1.437386975 |

These costs cover the final two batches, not total Phase 2 expenditure. They are observed
amounts, not guarantees. The run identities were d0cf8adf039d4def98f6edc7d1a1eafa and
f11193ccd3024844bb38cc69d53e0d2c. Raw evidence was retired during the authorized cleanup;
this summary retains the conclusions without making historical artifacts runtime inputs.

Remaining caveats include compressed attribution, redundant cross-process wording,
ambiguous access-window phrasing and the source gap for incomplete-but-undisputed
warranty-review ownership. The latter was explicitly corrected in one case but not
consistently called out. Correct primary decisions do not excuse material defects;
these remaining caveats were judged non-blocking in the complete published results.

Two fixed-case batches are bounded repeated evidence, not a statistical reliability
estimate or proof of transfer. Paid Sidecar testing, full service-request regression
and production release certification were not performed. Both integrations passed
provider-free smoke checks, and the design had 44 provider-free tests before cleanup.
Phase 3 remains separately scoped future work.


## Cleanup verification

The authorized cleanup retained business methods, schema shapes, deterministic
application code, fixtures, packaged hosts and local credentials. The selected
assignment is now authored in both hosts and survives regeneration. Current runner
overrides deliberately replace authored routing when a new trial is explicitly chosen.

After cleanup, all 45 provider-free tests passed, generation was stable, documentation
links resolved, and both deployed integrations passed smoke checks with zero model calls.
Mounted configuration checks verified all eight assignments and medium reasoning.
Historical synthetic assessments/requests were retired; only fresh smoke quotes remained
at cleanup close. Subsequent deterministic replays create their own synthetic records.
No paid evaluation, commit or push occurred during cleanup. This verifies runtime
preservation and routing, not a new business-reasoning result.

A verified private recovery snapshot and the retired originals are outside the repository;
`.runtime/cleanup-recovery.json` records their location and checksum locally. The snapshot
contains local credentials and is not a distributable runtime package. At cleanup close,
active evidence contained only retention guidance.

## Retained deterministic reference

The user subsequently requested continued deterministic testing. The final accepted
batch was recovered from the verified backup and reduced to the maintained
`fixtures/reference` pack: four case inputs, 60 recorded responses, request expectations,
expected published results, provenance and the existing business caveats. Other
historical captures remain retired. The backup is not needed to run the pack.

`run_suite.py mock` now exercises all four cases on both real integrations without
provider access. Validation passed eight replays and 240 checks with 120 local responses,
zero paid calls and zero cost; all 58 provider-free tests passed. Matching validates
business inputs and handoffs, and the complete output must equal the frozen result.
This establishes deterministic runtime regression coverage for these assessments,
not another live-model evaluation or full Phase 3 release coverage.
