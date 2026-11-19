# Direct OpenAI model reassessment

Authorized November 15, 2026; see project-agreement.md. This is business evaluation,
not completion of the deferred multi-provider framework acceptance matrix.

## Sequence and controls

1. Build beta.10 hosts; provider-free component, smoke, equipment/TypeSafe replay
   and affected SDK coverage. Preserve historical reference packs byte-for-byte.
2. Run the original Sol/Luna medium assignment on baseline, priority,
   capacity_shortfall and later_start, on Java and Sidecar.
3. Run all-Terra and all-Luna medium on the same Java scenarios. Review each batch
   before further sends. Confirm promising assignments on Sidecar.
4. Use mixed assignments only to address observed responsibility-specific failures.
   No business prompt redesign is presumed.

Use fresh output directories, direct OpenAI Responses and LOOMSPAN_OPENAI_API_KEY.
Keep physical request counts and input/output tokens; missing cost is unknown.
Automatic transport retries are disabled. Stop the batch on mechanical failure,
diagnose offline, and retain failure evidence. Semantic review can justify stopping
an otherwise mechanically successful configuration. Restore disabled forwarding.

## Predeclared semantic review

Review the complete published assessment and option findings against business.json,
not only the selected option. Mechanical checks and semantic acceptance are separate.

- Technical: recurrence after sensor replacement/cleaning; 20-minute prior testing
  versus 35–50-minute onset; bulletin eligibility is not a diagnosis; qualified
  inspection and clearance remain necessary.
- Timing: attendance is not restoration; use complete setup/work periods; honor
  stated date/access/deadline constraints without invented start triggers.
- Financial: exact 78000/48000-cent service caps; 30000-cent expedited premium
  included and payable on attendance; conditional labor/parts and pending warranty
  review; 240000-cent loaner procurement is separate.
- Authority: verified scoped service approval; directories confer no authority;
  loaner/replacement need separate procurement; no booking or service commitment.
- Decision: justify the pursued portfolio against the case's continuity priority,
  capacity and deadline. A 20/min loaner cannot satisfy the 25/min variant.
- Evidence fidelity: preserve original findings and explicitly identify justified
  corrections; do not invent facts or manufacture uncertainty about supplied data.

Classify material errors separately from non-blocking caveats and verbosity.
A single fixed-case pass does not establish reliability; repeat only when a concrete
uncertainty warrants the cost. Any improvement over Phase 2 is observational:
provider, framework and potentially model versions differ, preventing causal
attribution to framework fixes alone. Keep authoring/review effort in the comparison.

## Evidence status

The migration uses beta.10-SNAPSHOT and direct OpenAI Responses. Historical Chat
recordings are checksum-verified and imported to Responses envelopes in memory;
their business content and expected results are unchanged. Neither reference pack
was overwritten. Provider forwarding remains disabled outside explicit live runs.

Provider-free evidence (local ignored `evidence/` directories):

- Final component regression: 289 passed, 1 skipped; one dependency deprecation
  warning. Java application build tests also passed.
- `beta10-equipment-replay-01`: all four cases on both hosts, 240 checks and
  120 replay calls, exact accepted results.
- `beta10-typesafe-replay-01`, `beta10-typesafe-usage-missing-01`, and
  `beta10-typesafe-replay-remainder-01`: the union covers all 224 required
  scenario/host combinations successfully. The first batch stopped at a malformed
  HTTP header during trace retrieval for Java `usage_missing`; its execution result
  was correct and an unchanged targeted rerun passed. This is complete multi-batch
  coverage with an unresolved intermittent infrastructure caveat, not a clean full run.
- `sdk/beta10-local-01`: all 13 local Java SDK scenarios passed.
- `sdk/beta10-python-local-01`: Python SDK local lane and cleanup passed.
- Both hosts built/started successfully and provider-free smoke passed while
  preserving existing credentials and data.

The broader migration-roadmap gates, including its new media/acceptance matrix and
standard/hardened SDK recipes, are not established by these local checks.

Live results are recorded separately from mechanical checks. Each completed reviewed
batch has `equipment-service/business-review.json` bound to its report and bundle
checksums. No live result is promoted to a frozen reference by this review.

## Live model results

All assignments use medium reasoning. `Sol/Luna` is the authored six-Sol/two-Luna
assignment; Terra is `gpt-6.1-terra` and Luna is `gpt-6-luna`.

| Assignment | Host | Reviewed cases | Requests | Input tokens | Output tokens |
|---|---|---|---|---|---|
| Sol/Luna | Java | 4/4 accepted with caveats | 60 | 534,486 | 44,960 |
| Sol/Luna | Sidecar | 4/4 accepted with caveats | 60 | 534,620 | 45,606 |
| All-Terra | Java | 2/4 accepted; 2 semantic failures | 60 | 524,111 | 39,095 |
| All-Luna | Java | 4/4 accepted with caveats | 60 | 539,773 | 57,719 |
| All-Luna | Sidecar | 2/4 accepted; 2 semantic failures | 60 | 536,597 | 64,211 |
| Terra/Sol/Luna mix | Java | 4/4 accepted with caveats | 60 | 525,623 | 43,293 |
| Terra/Sol/Luna mix | Sidecar | 4/4 accepted with caveats | 61 | 540,977 | 44,220 |

Every case above passed all 27 mechanical checks. Each used 15 requests except the
mixed Sidecar baseline, which used 16. Luna generated a dependency on the nonexistent
task ID `check-serviceResources` rather than `check-service-resources`; Framework
rejected that plan and one built-in planning retry corrected it. This was not a
transport retry or schema correction, and no invalid plan was executed. There were
no failed model attempts or schema corrections across the batches. Output tokens
already include reasoning tokens; cached input is a subset of input, not additional
usage. Reported dollar cost is unavailable; consult the OpenAI console. The table
compares tokens, not prices. All-Luna used more output tokens than the other Java
assignments, so lower model tier does not establish fewer tokens or lower total cost.

Retained evidence: `beta10-openai-sol-luna-01`, including its checksum-linked
business review and original output bundle. The other four model experiment
directories were deleted by the user after evaluation: `beta10-openai-all-terra-01`,
`beta10-openai-all-luna-01`, `beta10-openai-all-luna-sidecar-01` and
`beta10-openai-mixed-01`. Their results below are retained summaries, not pointers
to available raw captures.

All-Terra's baseline and capacity-shortfall comparisons falsely superseded valid
conditional expedited timing estimates. Its technical and option assessments were
otherwise sound, and it more consistently recognized the missing owner for incomplete
warranty findings. All-Luna preserved those estimates, but its priority case left one
2-hour arithmetic error uncorrected in an already-disqualified standard option.
The capacity-shortfall loaner-first ranking is explicitly partial and debatable;
require business acceptance of the gap rather than treating it as full continuity.

All-Luna Sidecar priority misinterpreted `fullyCoveredScopeMaximum` as a warranty
benefit rather than the maximum customer exposure if fully covered, then endorsed
invented conflicts in the correct $300/$0 amounts. Its later-start comparison used
an incorrect four-hour maximum before production instead of the supplied 4-6-hour
arrival-to-start range. Here the error affects a potentially feasible option's
tradeoff, unlike the non-blocking Java priority arithmetic error for an option whose
arrival is already after the deadline. These are semantic failures despite all
mechanical checks passing. A different result across hosts is not evidence of a
host defect; single samples cannot separate sampling variation from host effects.

The focused mixed assignment passed semantic review on all four cases and both
hosts: five Terra technical/option assessments, Sol final comparison, and two Luna
coordinators. No business prompts were changed. It preserved valid timing and
financial interpretations, and Sol corrected several ownership overstatements.
Some minor ownership and procurement wording caveats remained. It used 8 Sol calls
across eight cases instead of the baseline's 48; model-price savings are not established
by that count alone. This was one preselected mixed batch, not sampling until pass.

**Recommendation:** retain the authored six-Sol/two-Luna default for now and treat the
five-Terra/one-Sol/two-Luna mix as the leading candidate for user review and a future
explicit promotion decision. Do not promote all-Terra or all-Luna from these results.
This round is complete; no additional paid batches are running. A targeted repeat of
the mixed candidate could measure repeatability after spend and semantic caveats are
reviewed, rather than automatically resuming broad tier tuning.

Across 28 live cases: **421 requests, 3,736,187 input tokens and 339,104 output tokens**.
The output includes 114,053 reasoning tokens; input includes 659,036 cached tokens.
Actual dollar cost remains unknown to the harness. Each batch restored the authored
runtime and disabled forwarding; a final direct check confirmed provider credentials
are absent from the fixture runtime. Both maintained reference manifests still verify.
Credentials and operational data were preserved; synthetic evaluation rows were added.
No commit, push, release, database reset, fixture promotion or default model change was
performed.

These observations do not prove that earlier Framework defects caused the historical
Sol requirement. Framework, provider and potentially model revisions changed together;
there is no controlled causal comparison. They do show that the migrated test harness
can run direct Responses evaluations, distinguish mechanical success from judgment
quality, and identify a promising narrower use of Sol.

## Reproducing the mixed candidate

Use a fresh output directory. The normal runtime remains provider-disabled; this
command temporarily enables direct OpenAI forwarding using LOOMSPAN_OPENAI_API_KEY
and restores it afterward. Further runs should follow the next agreed evaluation scope.

```powershell
.venv/Scripts/python.exe scripts/run_suite.py live --model gpt-6.1-terra --reasoning medium --skill-model resolveEquipment=gpt-6-luna --skill-model planResolution=gpt-6-luna --skill-model compareOptions=gpt-6-sol --scenario baseline --scenario priority --scenario capacity_shortfall --scenario later_start --output evidence/NEW_MIXED_RUN
```

Do not interpret `CHECKS_PASS_REVIEW_REQUIRED` as business acceptance. Review complete
outputs and preserve failures; the existing immutable reference remains the offline
regression asset.


## Subsequent user decision: promote Sol/Luna; defer tuning

The user reported $4 total console spend and chose the Sol/Luna baseline as the
active mock source while other suite changes take priority. `fixtures/reference-responses`
contains the four accepted Java cases with original content, semantic caveats and
provenance. Both hosts replay the same answers. This supersedes the earlier no-promotion
status for the Sol/Luna pack only; authored model assignments are unchanged.

Cleanup is complete for the four non-Sol/Luna live evidence directories: the user
deleted them on November 15, 2026 after the assistant's deletion commands were blocked,
and their absence was verified locally. No archive was created. Concise findings remain
in this document and the design guide. Sol/Luna source capture, the promoted mock pack,
provider-free regression evidence and operational data are retained. This confirmation
does not imply that scratch review files or operational logs were purged.


Promotion verification: all eight cases passed exact replay on Java and Sidecar
(240 checks, 120 local replay calls, zero paid calls), with 62 focused tests passing.
The new and both historical pack manifests verify; provider forwarding is disabled.
Evidence: `evidence/beta10-sol-luna-promotion-replay-01/equipment-service`.
