# Evidence retention after reset — 2026-10-04

The user discarded the entire historical `evidence/` directory to make room for
fresh GLM and Muse baselines. Approximately 16.02 GB of allocated historical data
was inventoried before deletion; C: had about 23.09 GB free at fresh-run preflight.
The assistant's deletion commands were blocked; the user completed deletion.
[Reset inventory](evidence-reset-20261004.json) records the removed directory groups.

Current source/configuration, installed packages, `.runtime` databases and
credentials, fixture definitions and the Python environment were retained.
The [PR 20 identity manifest](post-pr20-baseline.json) still matches all 139 frozen
source/configuration/fixture/evaluator files. The former storage and integrity
reports were inside the discarded evidence tree and are no longer available.

Historical capture-dependent regression/audit and replay provenance checks cannot
be claimed to pass. Their criteria have not been changed. The 41 focused synthetic,
contract and runner tests remain available and passed at fresh-run preflight.
Full mock acceptance and replay migration remain separate future work.

Retain the fresh comparison's captures, reports and review while they are the
current baseline. New captures are not replay-approved merely because automated
checks pass. See [current results](implementation-status.md) and
[current evidence](../evidence/README.md).

Retain the user-designated Sol Java reference suite, its baseline/priority/service
captures, and `evidence/sol-reference-20261004/` review and integrity records.
The durable [reference record](model-reference.md) identifies the comparison role;
these files must remain available while that reference is current. No extra export
bundle or copy of historical evidence is needed to establish it.
