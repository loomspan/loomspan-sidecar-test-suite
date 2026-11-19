# Accepted Responses replay pack

The user promoted the beta.10 direct-OpenAI Sol/Luna baseline on November 15, 2026.
This is the active equipment-service mock reference: six Sol skills and two Luna
coordinators, all at medium reasoning. All four Java cases were selected uniformly;
the same recorded answers run on Java and Sidecar to verify integration equivalence.
The original live batch passed review on both hosts with the recorded caveats.

`manifest.json` binds cases to source facts, skill contracts, model assignments and
the accepted capture hashes. `business-review.json` preserves the original semantic
review; `promotion.json` records the later explicit replay authorization. The original
review's replayApproved=false describes its pre-promotion state.

Only the transport envelope is minimized for deterministic replay, with zero synthetic
usage; accepted response text, request evidence and complete expected business outputs
are retained. Provider reasoning items are not replayed: this checks text-based
business execution, not all Responses protocol features or current model quality.

Run `scripts/run_suite.py mock` with the normal provider-disabled runtime. Requests
must match the recorded business inputs and evidence; every response is single-use.
Only fresh case identity is rebound. No paid fallback is allowed. New business or skill
contracts require an explicitly reviewed new pack, never silent fixture replacement.

The old `../reference` and `../reference-namespaced` packs remain untouched historical
provenance, not the active mock source. Raw Sol/Luna capture is retained locally in
`evidence/beta10-openai-sol-luna-01/equipment-service`; mock does not require it.
