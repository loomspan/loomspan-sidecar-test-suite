# Reviewed TypeSafe response pack

This maintained pack contains 34 real responses from `jev-1.13.0`, reviewed by the
assistant under the user's explicit delegation on 2026-10-11. It is separate from
the 49 authored protocol fixtures and the accepted equipment reference pack.

`review.json` records acceptance reasons, question-level scope, original rubric
misses, source capture hashes and the checksum of `cases.json`. The loader verifies
the checksum and acceptance membership. Captures remain diagnostic evidence; replay
needs only this pack and the normal runtime, with provider access disabled.

Run all protocol and reviewed cases with:

```powershell
.venv/Scripts/python.exe scripts/run_suite.py mock --suite typesafe-ai
```

Each recorded response is exercised through **both** current host implementations.
The `_java` or `_sidecar` suffix identifies where the original response was captured,
not which host may replay it. Request correlation IDs are replaced for each replay;
the captured response envelope, including historical usage, remains unchanged.
Historical usage is test data, not new billable usage. Paid replay calls are zero.

The first five original contacts were accepted on both source hosts. The original
sparse-contact example is excluded because its impact is unsupported. Twelve new
contacts demonstrate evidence sufficiency with `tsTriageEvidence`. For insufficient
evidence, only `impactEvidence` is semantically accepted: `impact` is preserved for
transport regression and must be ignored by a consumer. Its presence in this file
does not make it a known severity. At capture time there was no impact gate. The
subsequent [application policy](../../../docs/typesafe-ai.md#application-impact-policy)
provides a separate decision view; the frozen capture and review remain unchanged.

Four clear contacts missed the provisional evidence range of 0.80–1.00, returning
0.77–0.79. Their yes-leaning judgments were accepted with explicit caveats; the
original ranges and flags remain unchanged. A consumer using 0.80 would ask for
clarification unnecessarily on those cases. This is not a calibrated threshold.

Never overwrite this pack with runner output. A future replacement requires an
explicit semantic review linked to completed, checksummed captures. The native
`suites.typesafe_ai.reference.freeze` function verifies the supplied review and
captures and requires a new destination; live execution never calls it automatically.
Preserve prior accepted packs when preparing a replacement.
