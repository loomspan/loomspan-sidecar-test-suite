# Input-contract evaluation

Historical candidate: the current model-comparison baseline is now the normal
configuration described in [the contract audit](../../docs/input-contract-audit.md).
Use the normal suite runner for new comparisons. This wrapper intentionally loads
the earlier candidate and is not compatible with the revised deterministic inputs.


`closed-sources/skills` is an opt-in authored candidate for the equipment skill
tree. It keeps the normal skills and approved replay fixtures available while
testing stronger contracts against the same business checks.

The candidate requires full technical evidence, source metadata, operating needs
and commercial inputs at the receiving boundaries. Named source records are
closed; the surrounding `context` remains open for interpretation. Deliberately
shape-free findings remain open. Forwarding prompts preserve absent optional
source fields rather than filling them with blank defaults. Existing output
schemas, planning requirements and business criteria are unchanged.

Run from the repository root with the existing runtime and provider configuration:

```powershell
.venv/Scripts/python.exe experiments/input-contracts/run_evaluation.py --evidence-dir evidence/input-contract-run-UNIQUE --model z-ai/glm-5.3-flash --reasoning medium
```

Use a fresh evidence directory for each run. The wrapper uses the standard suite
runner, lock, captures, checks and provider-disabled restoration. It substitutes
candidate files only in the private runtime overlay, and saves their exact bytes
with the run. Model and reasoning options are passed to the normal evaluator.
The Framework version is unchanged; field-description rendering is separately
requested in Framework ticket PR 19.1 and is not part of this experiment.

## What to measure

| Question | Evidence |
| --- | --- |
| Does the contract reject missing or invalid structure? | Installed Framework validator: missing nested fields, incorrect types/envelopes, unknown source fields |
| Is legitimate flexibility retained? | Valid optional branches and additional reasoning fields beside source objects |
| What can still pass while changing meaning or provenance? | Shortened/empty collections, duplicate records, rewritten values and invented optional blanks |
| What does the model actually see? | Captured ordinary and corrective prompts, including field paths and descriptions when supported |
| Does the workflow improve? | Same-model live runs, original business checks, source diffs, corrections and completed outputs |

Requiredness and closure do not bind data to a previous result or enforce original
record membership. Prompts can ask for fidelity but do not turn it into deterministic
validation. Closing a record also rejects legitimate new source fields; update
contracts deliberately when producers evolve rather than silently discarding data.

This candidate changes both schemas and a short forwarding instruction. A quality
difference cannot be attributed to either change alone. Report failed parsing or
incomplete execution separately from completed business failures. Keep historical
automated results even when semantic review accepts a wording difference.

## Compatibility and promotion

The approved replay contains older handoff representations. Offline validation
against this candidate accepts 1 of 12 retained handoffs and rejects 11; the
evidence is in `evidence/closed-schema-experiment-20261004/replay-compatibility`.
Those are compatibility observations, not live workflow results. Do not activate
the candidate as the normal skill set without addressing its producers/replay and
the existing review requirements. No fixtures were rewritten for this experiment.

Initial stronger-schema evidence is retained under
`evidence/strong-schema-experiment-20261004`; the closed-source follow-up is under
`evidence/closed-schema-experiment-20261004`. See
[implementation status](../../docs/implementation-status.md) for observed outcomes.

## Observed outcome and remaining boundary

The PR 19 follow-up preserved source evidence at the reached handoffs, but both
live scenarios stopped on malformed JSON before completion. This is not evidence
of overall accuracy improvement. See the linked implementation status for routes,
correction results and retained captures. The run also changes forwarding prompts,
so it is not a schema-only comparison.

The Java entitlements tool supplies a legitimate `determination` alongside its
`data` envelope. The candidate describes the raw data object only. Before promotion,
define where that derived output belongs (for example, a separately declared field
or a full result envelope) and align producers/consumers. An earlier model moved
this provided value into the data object; calling it invented was incorrect.
