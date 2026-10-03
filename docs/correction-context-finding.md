# Full-output correction context finding — 2026-10-02

**Resolved runtime limitation:** after the user completed and installed the correction-context implementation,
both real hosts send the exact complete rejected candidate in schema and
step-action correction requests, verified offline on commit
`900cc86bc2ba619d38647688008b138a07108af6`. See the
[Complete correction-context verification](../evidence/review-complete-correction-context-20261002/summary.md).
No paid calls or new model-fidelity claims. The finding below describes the
previous snapshot; its proposed context-preservation work is now verified.

Observed on embedded Java and Python/Sidecar with the same Framework snapshot
`4313a7fcdbad33ef358b6ee4d068ce610f3dee51`, installed package SHA256
`5a2657767b03ffdeb915dee30e7d8934e6d09a3ec72b8854bd65c5a0b9f38cbb`.

The approved comparison response is syntactically valid and complete. The harness
appends one `}` without changing any other byte of its model content. Framework
rejects it with INVALID_JSON, supplies actual parser feedback, and accepts the
genuine Muse/medium corrective response on attempt two. Both workflows complete,
with strict replay elsewhere and explicit parent envelopes copying the actual
corrected child. These envelopes do not establish new parent-model reasoning.

The invalid candidates are 14274 and 15409 code points for Java and Sidecar. The
actual corrective requests contain only 8192 code points in the assistant message,
and feedback explicitly states that the candidate was truncated. The baseline
canonical mission input remains complete (28045 and 21935 characters in the user
message); this is separate from the historical dependent-result truncation issue.

Exact snapshot source `src/main/java/ai/loomspan/internal/outputschema/OutputSchemaCallAdvisor.java`
sets `MAX_CANDIDATE_CODE_POINTS = 8_192` at line 35, inserts that candidate replay
and feedback at lines234–243, and truncates in `candidateReplay` at lines397–406.
No supported configuration for this internal limit was located in the inspected
configuration API. Source inspection is read-only; no Framework modification is
part of this repository's results.

The initial pair reconstructed and shortened the original child assessment.
An application prompt change now explicitly requires copying the complete child
from canonical input during parser retries, including when the candidate is
truncated. The revised pair preserves that child exactly. Nevertheless Java
shortens outer citations from 24 to 13, while Sidecar changes their order; both
rewrite recommendation text despite the syntax-only fault. Mechanical review
rejects both sources. A green parser outcome does not prove semantic fidelity.

Candidate truncation is an observed limitation, not proven to be the sole cause
of model rewriting. Preserving the complete candidate is the next supported
Framework capability to investigate and test; it is not a guaranteed model-quality
remedy. Keep citation and original-assessment fidelity checks unchanged.

Offline reproduction with the current provider-disabled stack:

```powershell
.venv/Scripts/python.exe scripts/capture_full_correction.py --rehearsal
.venv/Scripts/python.exe scripts/review_full_correction.py evidence/full-correction-rehearsal-RUN --output evidence/review-full-correction-rehearsal-RUN/review.json
.venv/Scripts/python.exe -m pytest -q tests/test_full_correction.py
```

The rehearsal uses original valid reviewed correction content and explicitly
makes no fresh model-correction claim. The test suite proves rejected sources
cannot be curated, stage dependencies reject premature/repeated calls without a
provider fallback, and parent envelopes copy actual child content. Any future
Framework change should add a deterministic test that a complete large invalid
candidate reaches the correction request and that configured bounds remain
explicit. Then verify both application paths offline before another separately
authorized live pair.

[Revised rejection and full artifact links](../evidence/review-full-correction-live-20261002-130627/summary.md),
[independent mechanical review](../evidence/review-full-correction-live-20261002-130627/review.json),
[original-source rehearsal](../evidence/review-full-correction-rehearsal-20261002-130309/review.json).
