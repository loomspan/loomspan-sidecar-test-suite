# Current implementation status

Updated 2026-10-04 after PR 20 forwarding verification. This is observed status;
[the agreement](project-agreement.md) records accepted scope. Earlier checkpoint
narratives are preserved in the [archive](../archive/2026-10-04-before-muse-baseline/README.md).

## Current: PR 20 designated-child forwarding

`planResolution` now declares `output_from: {skill: compareOptions}` through the
normal authoring generator. Its duplicate output schema/retry policy and final-copy
instruction were removed. Other skill contracts and prompts, model and limits are
unchanged; `resolveEquipment` retains ordinary synthesis.

Both hosts embed installed Framework `cb37a28e0acf892744c2bbafd6c7cb657be757b1`, starter
SHA-256 `501464a9e33256fc0690bdec5bb2d852f5de51215e0184d33681597f379a2e9d`.
A fresh Muse/medium priority run completed on both integrations: **67/67 mechanical
checks per path**, exact child/parent text, all accepted work complete before
`RESULT_FORWARDED`, no resolution-parent synthesis call and no duplicate output
validation. Each workflow used 16 model requests versus 17 previously. The unchanged
outer parent also preserved the comparison in these runs. Forty-one focused tests
passed, and the old synthesis baseline still passes its 128 checks under read-only review.

The known service-work access reasoning gap remains in the child's answers; these
captures are not approved for replay. This verifies forwarding of a model child
through both hosts, not the entire forwarding feature matrix. No full mock suite
or service-request scenario was run. Services are ready/provider-disabled; prior
records are intact, with one new assessment and two quotes per path, no new requests.

Sidecar's pinned beta.2 test source uses the old public `SkillDescriptor` constructor
and fails test compilation against PR 20. Production code compiled, and runtime
packaging used `-Dmaven.test.skip=true`; Sidecar tests were not run. The deployed
Sidecar check above passed. Keep this downstream compatibility gap explicit.

[Full verification and artifacts](../evidence/pr20-output-from-20261004/summary.md).
The historical observations below belong to the previous configuration.

## Previous PR 19.1 evaluation baseline

Both integrations use the Maven-installed PR 19.1 Framework beta.8-SNAPSHOT,
commit `5c46862d04c85ba0d37c40b52feb35094a280b67`, starter SHA-256
`9590217b845e97e862a3b8db906bd77a6cccdbe67391684e02f9bedf87f6ea75`.
Sidecar is beta.2 source rebuilt against that snapshot, not a published Sidecar binary.
The [audited contracts](input-contract-audit.md) are normal configuration. Provider,
mission and proxy read limits are 480/2400/510 seconds, shared across models.

All 27 frozen application/configuration/limit files remain unchanged from the latest
GLM evaluation. No Muse-specific skill tuning or Framework production change was made.
The fresh run used `meta/muse-spark-1.3-contributor`, medium reasoning, on both paths.

| Model / path | Baseline | Priority | Observation |
| --- | --- | --- | --- |
| Muse / Java | 66/66 | 64/66 | Priority parent adds four valid citations, violating exact copy. |
| Muse / Sidecar | 66/66 | 66/66 | All mechanical checks pass. |
| GLM-5.3-Flash / Java | 64/66 | 64/66 | Retained runs re-reviewed using the same corrected evaluator. |

Counts include four shared capture checks per path. They are diagnostic assertions,
not percentages of model accuracy. Original reports remain unchanged; the Muse
runner originally also failed one overly strict sequencing check per path/scenario.
The evaluator now accepts Framework-guaranteed unit ordering for identifier-only
reads, while still requiring actual evidence dependencies. It also accepts exact
persisted quote IDs as citations. Both fixes are model-independent; 21 focused tests pass.

All four Muse workflows completed with 17 requests each, zero observed corrections,
malformed JSON, truncation, provider failures or timeouts. Longest response was 145.2s.
Reported total provider cost was $0.091806364. All source collections, operating
values and entitlement determination reached comparison unchanged; equipment assessments
were preserved. Java priority added MAN-3.4, MAN-4.2, MAN-4.3 and MAN-4.4 to the
comparison citations in its parent result; no other decoded fields changed.

## Business judgment and replay decision

These captures are **not approved for replay**. In all four results, expedited
arrival at 14:00-16:00 is treated as inside site access without resolving 2-4 hours
of elapsed work that could continue until 20:00, beyond the 18:00 cutoff. Java
explicitly says no after-hours arrangement is needed. Sidecar baseline also groups
the evening loaner with the ten-day replacement as unable to restore the morning
shift, while later recommending arranging loaner access as a contingency.

Sidecar changes its primary recommendation to loaner under the stronger continuity
priority. Java keeps expedited primary with urgent loaner escalation; the stronger
priority response is limited/inconclusive. These are reasoning findings, separate
from schema validity, exact-copy requirements and evaluator corrections.

The deterministic approval/recovery follow-up passed **61/61 checks** across both
paths, with no additional model calls. The original runner skipped it because of
the sequencing assertion; the separate follow-up used the mechanically valid live
baseline after the evaluator correction. Denial, approved creation, lost-result
recovery, idempotency, conflicts and expiry were checked through real integrations.

[Full review, outputs, comparisons and provenance](../evidence/muse-baseline-20261004/summary.md)
are the current reference point. This is a useful fixed evaluation baseline, not
a clean semantic or full-delivery pass. No new replay version was activated and
full mock acceptance was not run: suitable reviewed answers are a prerequisite.

## Remaining boundaries

Historical replay remains incompatible with the new inputs: the audit rejected
42 of 43 distinct old calls. Business and correction fixtures, retained-live audits
and their historical dependencies need explicit migration before current full mock
acceptance can pass. Preserve old provenance and do not silently edit captured answers.

The earlier contract audit passed 52 actual installed-Framework validator cases,
36 focused offline tests, nine final contract/regeneration checks and ten deployed
boundary checks across both hosts. These validate structure and runtime boundaries;
they do not guarantee complete copying or correct reasoning.

The next comparison can use these unchanged skills, scenarios, limits and corrected
evaluator for another model. Keep access reasoning and parent-result fidelity as
separate known findings. Any proposed schema/prompt/framework change should become
an explicit new comparison baseline rather than an adjustment for one model.

Normal services are ready and provider-disabled. All prior business rows are
unchanged. Java now has 102 assessments, 240 quotes and 18 requests; Python has
84 assessments, 196 quotes and 17 requests. Each path added two assessments, four
quotes and one authorized test request. Original captures/fixtures remain intact.

Storage cleanup on 2026-10-04 reduced project file storage from 22.38 GB to
16.88 GB using lossless NTFS compression of retained evidence. All 13,850 original
evidence files retain their SHA-256 hashes and paths. Docker separately reclaimed
5.47 GB of unused build cache older than a week; images, containers and volumes
were retained. C: had 5.33 GB free at the final measurement. See the
[cleanup and integrity report](../evidence/storage-cleanup-20261004/summary.md).
