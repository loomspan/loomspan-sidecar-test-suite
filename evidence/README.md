# Current evaluation evidence

Latest: [PR22/23 output bindings and Luna](pr23-adoption-20261005/summary.md): exact input/output transfer in both scenarios; corrected review 66/67 baseline, 67/67 priority. Original evaluator/report retained alongside the offline parser correction. No replay approval.

The latest [two DeepSeek PR21 evaluations](pr21-deepseek-20261005/summary.md) complete
all four scenarios with exact bindings. Flash misses W-2 citations; Pro priority
breaks exact preservation through minor root edits. Business gaps remain; no replay
approval. Both runtimes were restored and source/evidence integrity verified.

The preceding [GLM Flash PR21 evaluation](pr21-glm-flash-20261005/summary.md) records
exact bindings in both scenarios, baseline 61/67 with real final rewriting and a
separate fenced-plan review limitation, and priority comparison timeout. No replay
approval; original criteria and evidence remain unchanged.

The preceding [MiMo PR21 evaluation](pr21-mimo-20261005/summary.md) records baseline
failure on optional reasoning JSON, priority 67/67 with exact bindings and final
preservation, and skipped service follow-up. Remaining business wording issues
prevent replay approval; all original evidence is preserved.

The preceding [Luna PR21 evaluation](pr21-luna-20261005/summary.md) records exact bound
evidence, baseline 67/67, priority 65/67 due to minor final rewording, and 33/33 service
checks. The calendar error did not recur; priority technician-access reasoning remains
incomplete. Original reports and captures are unchanged; no replay approval.

Historical captures and export bundles were deleted by the user on 2026-10-04.
Old evidence links and historical replay dependencies are intentionally unavailable.
Fresh GLM and Muse Java evaluations use the unchanged
[post-PR-20 baseline](../docs/post-pr20-baseline.md).
The user-designated [Sol Java reference](../docs/model-reference.md) uses the same
baseline. Its [review and validation](sol-reference-20261004/summary.md) identify the
retained source captures and comparison boundaries.
The subsequent [non-Flash GLM-5.3 comparison](glm-5.3-comparison-20261004/summary.md)
retains its successful baseline, failed priority, service checks and semantic review.
The [Luna comparison](luna-comparison-20261004/summary.md) records both completed
scenarios, the baseline source-fidelity failure and priority calendar/access errors.
The [DeepSeek comparison](deepseek-comparison-20261004/summary.md) records completed
scenarios with assessment-source fidelity failures and continuity/access concerns.
The [Pro alias attempt](deepseek-pro-comparison-20261004/summary.md) records an
invalid OpenRouter model ID, not an additional model-quality result.
The [exact tilde-alias Pro run](deepseek-pro-tilde-comparison-20261004/summary.md)
corrects that identifier mistake and records the completed baseline and provider-failed priority.

The final selected [MiMo comparison](mimo-comparison-20261004/summary.md) records
a baseline timeout and a priority malformed tool call after correction, with no
final recommendation. The selected comparison set is complete; Sol stays the reference.

See [current results](../docs/implementation-status.md). Read the [fresh comparison](fresh-comparison-20261004/summary.md) for results,
failure evidence, semantic review and final runtime validation. Captures are not automatically approved
for replay; full mock acceptance and replay migration remain separate work.


PR 21 adoption and the first GLM comparison are recorded in
[the new review](pr21-adoption-20261005/summary.md). Earlier captures remain original;
this is a separate baseline and no capture is approved for replay.
