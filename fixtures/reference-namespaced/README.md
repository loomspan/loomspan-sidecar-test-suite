# Deterministic assessment contract

The four accepted assessment cases use canonical `default-` Framework identities.
The original accepted business inputs, evidence, model judgments and complete
expected results are preserved. This tests runtime fidelity, not new reasoning or
current provider behavior. No service commitment is created by assessment replay.

Run `scripts/run_suite.py mock` after starting the provider-disabled runtime. It
executes all four cases on Java and Python/Sidecar with strict semantic request
matching and one-time response consumption. Changed business values, assignments,
reasoning, mission input, task prose or evidence fail closed. JSON object order
and parallel evidence collection order have their existing documented semantics.

`namespace-review.json` enumerates each qualified identity position, its before/
after values, source hashes and current hashes. Positions are request skill,
completed-evidence skill, the explicit assigned-task capability line, and plan/
tool reply capability identifiers. All other reply bytes and business values stay
unchanged. The immutable original accepted pack remains at `../reference` as the
review source; runtime loads this directory directly without a legacy fallback.
The source manifest's `sourceManifestLfSha256` pins its repository LF representation,
so a preserved Windows worktree and a fresh checkout use the same review identity.
This normalization applies only to that metadata digest; case files, model replies
and the ledger retain exact byte checksums. The original manifest is never rewritten.
`manifest.json` retains the source acceptance, caveats, assignments and source/
skill-contract checksums and verifies current file integrity. Updates require
explicit review; run outputs always go to a new evidence directory.
