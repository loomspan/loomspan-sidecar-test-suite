# Replay provenance gate

Current checkpoint (2026-10-02): `business-reviewed-v1.json` is approved for scoped
baseline/continuity-priority assessment replay on both applications. Its separate
approval record binds the exact fixture hash. All per-path live-source captures,
configuration identities, response provenance and semantic reviews remain required
local inputs; only case identifiers are normalized. The historical diagnostic
descriptions below keep their original rejected/unapproved dispositions.

`scripts/run_acceptance.py` runs all first-delivery offline scenario groups and
independent reviews with provider access disabled. Full-workflow recovery deliberately
appends an extra closing brace, then replays the original valid comparison only after
matching actual parser feedback. It labels both fault and correction provenance and
never modifies the approved fixture. This correction is reused captured content,
not a new model response to the injected failure. See the consolidated delivery audit
before making a complete-delivery claim.

`quote-contract-diagnostic-v1.json` reuses the paired comparison responses from
`evidence/live-20261001-205953`, retaining the original Sol model, request IDs,
provider envelopes, usage and source-file hashes. It is **not an approved replay
baseline**. Both samples lack authoritative asset/approval context and have unclear
monetary prose; Java also adds unissued quote objects. Sidecar is usable only as a
structurally valid two-quote sample.

`tests/test_contract_diagnostic.py` deliberately sequences Java's invalid output
and Sidecar's structurally valid output through each real Framework. This synthetic
cross-path sequence tests actual schema rejection/feedback, but is **not a captured
real-model correction response**. Only case IDs are normalized in runtime copies.
The input and responses remain historical; success does not establish corrected
model judgment, context propagation through the full workflow, or business acceptance.

To derive a new diagnostic copy without changing source evidence:

```powershell
.venv/Scripts/python scripts/derive_contract_diagnostic.py evidence/live-20261001-205953 --output evidence/new-quote-diagnostic.json
```

The exporter refuses overwrite and output within the source capture. It never
sets approval. Run the preserved diagnostic plus publication checks with:

```powershell
.venv/Scripts/python -m pytest tests/test_contract_diagnostic.py tests/test_quote_publication.py
```

No accepted baseline exists yet. Complete beta.6 live captures lose required upstream evidence and are **rejected**, even when the provider returned HTTP 200 or Framework accepted the JSON shape.

The fixture's replay engine supports execution-specific steps, evidence substrings, forbidden substrings, predecessor dependencies and single-use stage/attempt matching. It rejects missing/ambiguous matches and has no live fallback. A delivered scenario must cite a reviewed capture and the exact request/response event indexes, preserve the model/provider identity and usage, describe identifier normalization, and label any intentional fault mutation.

After the documented evidence-flow blocker is resolved, complete and review baseline and changed-priority workflows in both paths, capture real correction feedback/responses, and derive scripts. Do not add input-independent expected answers or treat development scripts as model provenance. Ordinary acceptance must fail/skip explicitly when a reviewed scenario is absent; it must never make a provider call to fill the gap.
The approved `full-correction-reviewed-v1.json` contains genuine Muse/medium
corrections captured within complete Java/Sidecar workflows with complete correction context. Original
comparison output has one explicitly labeled extra closing brace; corrective
envelopes are captured unchanged with case-ID normalization only. Both parent
envelopes echo actual corrected child content. The separate
`full-correction-reviewed-v1-approval.json` binds source/review hashes and paired
offline fidelity/JUnit verification. Consolidated acceptance requires it.
See [evidence](../../evidence/review-full-correction-live-20261002-171741/summary.md).
