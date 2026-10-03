# Muse JSON failure: model output and Framework prompting

Subsequent controlled diagnostic 2026-10-02: both actual paths reject the injected
original trailing-brace action and Muse/medium answers their invalid step-action feedback with
valid entitlement calls. Each lookup executes once after correction, with no prior
tool call or business-record change. The model drops optional context to `{}`;
this proves isolated recovery with authoritative re-reads, not full-payload copying
or original full-workflow recovery. See
[forced-failure evidence](../evidence/review-controlled-step-live-20261002-004937/summary.md).

Follow-up 2026-10-02: installed Framework source `4313a7f` includes invalid step-action recovery
feedback and mission-objective prompt changes. Both original failures still reject offline;
new bounded feedback retains the parser diagnostic and long-response tail. One new
Muse/medium workflow per path completes, but neither emits malformed JSON or
exercises step-action correction. Java instead demonstrates ordinary schema recovery.
This verifies the feedback improvement without proving Muse recovery from these
trailing-brace failures. Both new captures remain semantically unapproved; see
[follow-up review](../evidence/review-live-20261002-000544/summary.md).

The investigation below preserves the earlier source and capture observations.

Reviewed 2026-10-01, using the preserved `live-20261001-220102` capture and Framework
source commit `b7dbefee8ffca873e84efb455e5609234c59e119`. No provider calls or
production code/configuration changes were made for this investigation.

The immediate defect is malformed provider output. The Framework correctly rejects
it. However, its step-action correction prompt has a concrete weakness, and the
reference application's broad context-passing contract creates unnecessary copying
work. This run does not establish that Muse is unsuitable, or that improved prompts
would necessarily succeed. It warrants fixing and testing the recovery design.

## What the captured bytes prove

The failed operation is Java `planResolution#step-1`, task `t-entitlements-01`.
Both requests explicitly instruct the model to return only valid JSON, name the
exact task and tool, and show the action shape.

| Attempt | Provider request ID | Output size | Independent JSON finding |
| --- | --- | ---: | --- |
| Initial | `1837c3a9035c4ba7aa2203927dba436d` | 15,865 characters | Complete action followed by one extra `}` |
| Correction | `d8fae2f5e70b40968e9a1f3afdc2f8f6` | 15,539 characters | Complete root object followed by three extra `}` characters; six context fields also moved outside `toolArguments` |

Both provider envelopes report HTTP 200 and `finish_reason: stop`; the outgoing
requests set model and medium reasoning but contain no `response_format`, native
`tools`, or explicit output-token limit. The action is generated as ordinary message
text under prompt instructions, not a requested provider-native structured-output mode.
This does not establish which constrained-output modes the provider supports.

The original provider `message.content` exactly matches the Framework trace's
reassembled response content at sequences 270 and 316. Rejections occur at 277 and
323, followed by failure at 325. There is no evidence of an intermediary modifying
the text or of response truncation causing these terminal failures.

An isolated offline reproduction used the exact packaged Framework codec and
StepAction type, with JAR identity checked against the run manifest. Both originals
fail with `Unexpected close marker '}': no open Object to close`.
`FAIL_ON_TRAILING_TOKENS` is enabled. Removing only the trailing characters from
diagnostic copies allows parsing, confirming the syntax defect. Those copies are
**diagnostic mutations, not repaired captures or approved responses**. The retry's
misplaced fields remain a separate shape problem; the StepAction type ignores unknown
root properties, so parse success alone is not evidence of faithful argument transfer.

## The step-action retry is weak

The correction request contains exactly the same user input and original system
prompt, with this suffix:

```text
YOUR PREVIOUS ACTION WAS INVALID: Failed to parse model response as StepAction
Please correct and try again.
```

It contains only system and user messages. The failed assistant answer is absent.
The actual parser reason, error location and offending fragment are absent. The
Framework catches the parsing exception, returns null and exposes the generic message
to the next call. The model is being asked to regenerate approximately 15 KB of nested
JSON without being shown what it must repair. There is one retry, a separate limit
from `output_schema_max_retries`.

Source anchors in the inspected Framework revision:

- `StepLoopMissionExecutionEngine.java:815–841`: generic appended feedback and retry.
- `StepLoopMissionExecutionEngine.java:1041–1065`: parser error is logged at debug level and discarded from model feedback.
- `StepLoopMissionExecutionEngine.java:88`: one invalid-action retry.
- `StepPromptBuilder.java:100–114`: valid-JSON instruction and illustrative action shape.

The Framework already has stronger ordinary output-schema recovery:
`OutputSchemaCallAdvisor.java:233–244` replays the candidate and adds a correction
message; its diagnostics include parser reason, location and nearby fragment.
Sidecar used that path in this same run for malformed equipment-assessment JSON,
and its next response was valid. This is a useful comparison of recovery mechanisms,
not a controlled A/B proof that the Java step would recover.

## Application prompt and contract contributors

The shared authored prompt tells every child call to carry full relevant evidence
in context. The deterministic Java entitlement method accepts an open optional
context object, but does not use it: it re-reads authoritative findings, terms and
clock records using the case ID and verifies asset scope. For this leaf, copying
the assessment, service terms, contacts and operating needs into a large nested
action is unnecessary. The retry even changed field placement while recopying it.

The Framework combines the entire parent skill prompt with the assigned-step prompt.
That puts final recommendation/quote-preservation instructions alongside a simple
lookup assignment. The examples contain placeholders such as
`<arguments for this tool>` and `<any JSON value>`, so they are schematic rather than
parseable JSON examples. These are plausible additional contributors, not proven
causes of the extra braces.

## Recommended order of work

1. Improve Framework step-action recovery to carry bounded prior-candidate evidence
   and precise parser diagnostics, including the failing tail for long responses.
   Distinguish syntax errors from action-contract errors. Test against these captured
   responses before any paid run. Keep rejection of malformed actions.
2. Narrow deterministic lookup contracts and authored context guidance so these
   leaves receive the IDs they use. Preserve complete evidence for the substantive
   model responsibilities through supported mechanisms.
3. Use valid JSON examples with placeholder explanations outside the JSON, and make
   assigned-step instructions unambiguous about their immediate task.
4. If needed after offline verification, compare the old and revised prompts on the
   same isolated failed step with Muse/medium. Do not use a full workflow merely to
   test correction feedback. A controlled comparison is needed to establish whether
   the changes improve model success rates.

Evidence: [machine-readable findings](../evidence/json-forensics-20261001-220102/findings.json),
[exact-parser reproduction](../evidence/json-forensics-20261001-220102/parser-reproduction.txt),
[initial request](../evidence/json-forensics-20261001-220102/initial-request.json), and
[retry request](../evidence/json-forensics-20261001-220102/retry-request.json).
All original capture checksums remain unchanged; the full capture remains unapproved.
