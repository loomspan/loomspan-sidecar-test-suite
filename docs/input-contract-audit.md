# Skill contract audit and fixed evaluation baseline

This review follows producer/consumer behavior, not any model's preferred wording.
The current contracts are authored in `scripts/workflow_contracts.json` and generated
by `scripts/author_workflow.py`. Java method signatures and Python request models
describe the same deterministic inputs. Changes to these sources require regeneration
and compatibility review before another comparison baseline is declared.

| Skill boundary | Contract and reason |
| --- | --- |
| resolveEquipment | Case/asset identifiers plus incident and operating requirements; context remains extensible. These are caller facts needed to judge options. |
| assessEquipment | Incident, asset, history and reference data with source metadata; no commercial input requirement. Output gives chronology, hypotheses, questions, uncertainty and citations. |
| planResolution | Original assessment, technical evidence, terms and operating requirements. It coordinates the downstream checks without rewriting the assessment. |
| compareOptions | Technical and commercial source data, original assessment, operating needs, issued quotes and a separate entitlementDetermination. The latter is copied from the tool envelope, not merged into raw findings. |
| assetContext, serviceHistory, referenceEvidence, serviceTerms, serviceResources, continuityOptions | Only caseId and assetId. Their implementations read records and do not consume model context. |
| entitlements | Only caseId and assetId. It reads authoritative terms, findings and clock itself; model-supplied hypotheses do not establish eligibility. |
| quoteOptions | Only caseId and assetId. It rereads authoritative inputs and computes/persists quotes; copied model amounts cannot become authoritative. |
| createServiceRequest | Required typed approval and repair scope, closed objects. Existing business checks still enforce approved=true, matching quote/scope/cap, verified authority, expiry and idempotency. A structurally valid approval grants nothing. |
| compatibility | Closed caseId input; intentionally minimal provider-protocol diagnostic. |
| authorizationParent, authorizationNested | Closed caseId/approval envelope using the same approval shape as creation. They remain controlled authorization tests, not ordinary workflow guidance. |
| stepCorrectionDiagnostic | Closed caseId/assetId/context envelope. Context is deliberately open diagnostic evidence; the entitlement child accepts identifiers only. |

Source contracts describe the current reference application's data version. Optional
contact fields remain optional: requiring a name because one model omitted a known
name would misrepresent valid unnamed contacts. Open finding records accommodate
incomplete observations; model reasoning belongs outside source records. Named stable
records are closed. Context and operating needs allow extensions. Descriptions state
provenance and meaning; they do not provide runtime equality checks or automatic
result binding. Collection membership, source equality and citation provenance remain
independent evaluation responsibilities.

The former decision prompts included worked calculations, contact names, fixed
times and exact clause IDs from the demonstration case. These were removed. The
prompts now ask for the same business analysis using supplied sources: cost/coverage,
arrival versus completion, access, expiry, approval, uncertainty and alternatives.
No model-name branches, fixture-answer enums, synthetic repair of live outputs or
new Framework behavior were added. Model-dependent failures must be recorded without
editing this baseline between models.

Provider timeout is 480 seconds on both hosts; mission timeout is 2,400 seconds.
The recording proxy's upstream read timeout is 510 seconds, so it does not enforce
the former 240-second cutoff first. These are test limits, not latency guarantees.
Capture polling follows the recorded mission timeout. REST business-tool timeouts
remain separate: the deterministic tools do not invoke a provider.

## Compatibility and evaluation

These are deliberate input-contract changes. Existing replay captures with large
lookup contexts or incomplete receiving inputs are not compatible merely because
they previously passed. Preserve their original bytes, provenance and approval;
do not rewrite them to manufacture current acceptance. A new approved replay baseline
requires a suitable live capture, semantic review and the normal refresh procedure.
Historical fault/authorization payloads also need explicit compatibility review.

Run the normal `scripts/run_suite.py evaluate --model <model> --reasoning <supported-level>`
against this configuration. Keep prompts, schemas, timeouts, quotas, scenarios and
business checks fixed across models. Record any reasoning-profile difference.
The older experimental wrapper is [archived](../archive/2026-10-04-before-muse-baseline/README.md)
and should not be used for this revised baseline. Report completion, fidelity, business quality,
latency, corrections and provider failures separately. No single run establishes
causation or broad model accuracy.

## PR 20 completion-policy update

The user-authorized PR 20 migration changes only `planResolution` completion to
`output_from: {skill: compareOptions}`. Its authored output schema/retry setting
and final-copy instruction are removed; compareOptions retains the producing
contract. Input contracts and business prompts otherwise remain unchanged. This is
an explicit new evaluation baseline; see [verification](../evidence/pr20-output-from-20261004/summary.md).
