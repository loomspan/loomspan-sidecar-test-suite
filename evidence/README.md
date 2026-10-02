# Evidence

Run directories are generated and ignored by Git. They include actual Framework NDJSON artifacts and separate independent observations. Read `docs/implementation-status.md` before interpreting results: compatibility success is not completed first-delivery acceptance.

## Current evidence map — 2026-10-02

| Evidence | Use and disposition |
| --- | --- |
| [Reviewed baseline replay](review-business-reviewed-baseline-20261002-112945/summary.md) | Both offline paths complete; 34 checks/eight assertions pass. Approved deterministic assessment scope only; zero paid calls. |
| [Reviewed priority replay](review-business-reviewed-priority-20261002-113035/summary.md) | Both offline paths complete; 34 checks/eight assertions pass. Approved deterministic assessment scope only; original sources retained. |
| [review-live-20261002-102148](review-live-20261002-102148/summary.md) | Java priority completes; all31 mechanical checks and four assertions pass, business wording and exact assessment fidelity suitable for curation. No shared approval. |
| [review-live-20261002-095046](review-live-20261002-095046/summary.md) | Sidecar priority completes with full fidelity and suitable business wording; Java fails an HTTP200 provider error completion. No shared approval. |
| [review-live-20261002-100123](review-live-20261002-100123/summary.md) | Java priority retry completes with correct commercial wording but root adds one assessment citation; rejected for exact-copy contract violation. |
| [review-live-20261002-093632](review-live-20261002-093632/summary.md) | Java-only baseline follow-up completes with verified quota400000 and full fidelity; suitable for curation, no shared replay approval. |
| [review-live-20261002-093706](review-live-20261002-093706/summary.md) | Java-only priority completes with verified quota400000; ambiguous risk wording keeps it rejected. |
| [review-live-20261002-092503](review-live-20261002-092503/summary.md) | Both complete. Sidecar suitable for replay curation; Java rejected for renewed-quote contradiction and date error. |
| [review-live-20261002-092554](review-live-20261002-092554/summary.md) | Sidecar priority rejected for shortened assessment; Java recovers actual malformed output then fails 200000 usage quota. Incomplete Java capture unapproved. |
| [review-live-20261002-090948](review-live-20261002-090948/summary.md) | Revised full baseline: both complete, prior findings improve, exact equipment fidelity verified; shared replay unapproved for separate loaner access handoff gap. |
| [review-live-20261002-091031](review-live-20261002-091031/summary.md) | Revised full priority pair: both complete; shared replay unapproved for loaner access/expiry handoff ambiguity. |
| [review-comparison-correction-live-20261002-090917](review-comparison-correction-live-20261002-090917/summary.md) | Both direct comparison schema corrections succeed: 28 checks, one real Muse answer per path. Source business defects retained; no semantic/replay approval. |
| [review-comparison-correction-offline-20261002-090841](review-comparison-correction-offline-20261002-090841/summary.md) | Synthetic missing-field correction rehearsal: 28 checks pass, no paid calls. |
| [review-live-20261002-085034](review-live-20261002-085034/summary.md) | Full baseline after first wording fixes: both complete, rejected for known applicability/price/work-cap defects; actual-child metadata check strengthened. |
| [review-live-20261002-085100](review-live-20261002-085100/summary.md) | Full changed-priority pair: both complete and escalate continuity, rejected for deadline/reapproval/reviewer/standard-access wording. |
| [review-business-workflow-offline-20261002-075008](review-business-workflow-offline-20261002-075008/summary.md) | Earlier deployed offline verification: both full diagnostic paths complete, 32 checks pass; real schema recovery with synthetic correction and authored business outputs. No new model judgment or business replay approval. |
| [review-business-workflow-offline-20261002-074647](review-business-workflow-offline-20261002-074647/summary.md) | First offline attempt exposed a replay ordering defect on Java; failure retained. Superseded by dependency-graph matching, without changing deployed hosts. |
| [business-output-offline-20261002](business-output-offline-20261002/summary.md) | Earlier offline fixes/checks. Hand-edited examples, no new model or Framework execution, no business replay approval. Revised deployed behavior remains unverified. |
| [review-live-20261002-000544](review-live-20261002-000544/summary.md) | Historical full Muse run before the business-output fixes. Both workflows completed; semantic findings keep the captures REJECTED_FOR_REPLAY. Retained as source provenance and regression evidence. |
| [review-controlled-step-live-20261002-004937](review-controlled-step-live-20261002-004937/summary.md) | Historical isolated real step-action recovery on both paths, with synthetic surrounding stages and optional-context omission. Supports only that diagnostic; no full business approval. |
| Earlier capture and review directories | Historical evidence for their recorded revisions/configuration. Consult status and each manifest; do not substitute them for current acceptance. |

## Retention and cleanup

Retain unique source captures, provider/downstream journals, actual Framework
traces, business records, artifact/configuration identities and checksums, review
dispositions and reports used by regression or provenance checks. Fixing a bug does
not remove the value of its reproducer. Keep historical labels and original paths
so references remain reliable; never promote old or edited outputs to approved replay.

Delete reproducible scratch output when finished: temporary test databases, compiled
checker classes, Python/pytest caches and verified redundant files with no provenance
or recovery role. Keep uncommitted source work and running-service state. Review
large build archives for references and recovery value before deletion; do not use
age alone as a deletion rule. Record what was removed.

Cleanup verified on 2026-10-02: disposable Java checker classes, two temporary test
databases, workspace Python caches and `.pytest_cache` are absent. Broad automated
deletion was initially blocked; explicit file deletions succeeded and the user
completed directory cleanup. [Cleanup verification](business-output-offline-20261002/cleanup.json)
confirms all eight paths are absent and all 134 preserved source-evidence hashes
still match. Captures, journals, actual traces and source work remain intact.

Latest cleanup: 33 disposable files and seven empty cache directories removed;
original134 hashes and finalized live capture checksums match. See
[report](review-live-20261002-102148/cleanup.json).
