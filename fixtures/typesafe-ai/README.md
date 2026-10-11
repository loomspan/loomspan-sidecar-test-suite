# Authored TypeSafe protocol fixtures

`cases.json` defines independent native requests, synthetic response envelopes and
expected results for the customer-support triage suite. These are not recorded real
provider judgments and must not be represented as an accepted model evaluation.

The runner substitutes only `__CASE__` with a unique correlation identity. It checks
the exact native request and consumes each specified response once. Lists of responses
represent explicit retry sequences; an empty list means no transport call is permitted.
Some intentionally malformed responses test passthrough or rejection, not correct
TypeSafe service behavior. Error cases must fail without a substitute result.

Run `scripts/run_suite.py mock --suite typesafe-ai` from the initialized workspace.
Future live recordings require explicit paid scope and review; the runner never
promotes outputs into this pack. Equipment's accepted `fixtures/reference` remains
separate and unchanged. See [coverage and limits](../../docs/typesafe-ai.md).
