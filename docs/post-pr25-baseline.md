# PR24/25 direct-dispatch and argument-guidance baseline

Current identity: `post-pr25-direct-dispatch-guidance-20261005`. [Exact manifest](post-pr25-baseline.json).
Both embedded Java and Sidecar package installed Framework `7d47269` (PR24/25 plus cleanup).
PR23 source contracts, business inputs, model defaults, evaluator and 480/2400/510-second limits are unchanged.

Framework now directly dispatches eligible fully bound assigned tasks. Remaining model dispatch
prompts distinguish required, optional and Framework-owned arguments. No per-skill switch was added here.
Output binding and planResolution forwarding behavior remain in place.

[Provider-free adoption verification](../evidence/pr25-adoption-20261005/summary.md) uses retained Luna
priority text in isolated diagnostic cases, with case identifiers normalized and the eight eliminated
dispatch responses excluded. Both hosts complete with eight Framework dispatches and seven fixture-backed
model interactions, 43 exact input bindings and 18 exact output bindings, exact final publication,
and no root synthesis. Three optional dispatch prompts per host explicitly allow empty arguments.
This verifies execution mechanics, not new model reasoning, cost savings or business acceptance.

The [PR22/23 baseline](post-pr23-baseline.md), its 141 source files and both prior host jars are preserved.
Historical PR20/21 captures and Sol reference remain unchanged. No fresh paid model baseline has been run
on PR24/25. The retained Luna reasoning still has its known technician-access gap; no replay approval,
fixture refresh or full mock acceptance follows from these diagnostics.

All five services are ready/provider-disabled. Sidecar production packaging retains the existing
skip of its obsolete source-export tests; deployed checks cover both running hosts. Future paid
comparison requires explicit model-run authorization and must record this distinct baseline.
