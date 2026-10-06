# Loomspan reference applications and acceptance suite

Start here. This project demonstrates the same equipment-service process through
embedded Java Framework and Python/FastAPI with Sidecar.

**Current phase: skill-level optimization.** The user has declared Phase 1 Framework
exploration complete. Phase 2 explores skill composition and design to help less
capable models succeed; Phase 3 will establish long-term regression and release
confidence. See the [agreed phase direction](docs/project-agreement.md#three-phase-direction--agreed-2026-10-05).

1. Read the [PR24/25 dispatch and guidance baseline](docs/post-pr25-baseline.md) for the active configuration.
   The [PR22/23 output binding baseline](docs/post-pr23-baseline.md) remains frozen.
   The [PR 21 input binding baseline](docs/post-pr21-baseline.md) remains frozen.
   The [post-PR-20 baseline](docs/post-pr20-baseline.md) retains the prior exact artifacts,
   configuration/evaluator identities, fixed scenarios, limits and known gaps.
2. Read the [current results table](docs/implementation-status.md) for observed
   execution, evidence fidelity and business judgment, separately.
   The user-designated [Sol comparison reference](docs/model-reference.md) is Java-only.
3. Use [run modes](docs/run-modes.md) for operational details. The sole supported
   evaluation entry point is **scripts/run_suite.py**; other scripts are helpers,
   setup tools or historical diagnostics.

## Evaluation workflow

Run from this repository in the initialized workspace with Docker Compose services
ready. Initial setup: [operator runbook](docs/on-prem-runtime.md) or
[local development](docs/local-run.md). Run one mode at a time.

| Mode | Scope | Status / requirement |
| --- | --- | --- |
| `evaluate` | Baseline, priority and service follow-up on Java by default; `--path sidecar` selects Sidecar | Paid live calls; explicit model-run authorization and provider key required. |
| `live` | Same live workflow on both integrations | Paid live calls. |
| `capture` | Both integrations plus candidate replay review material | Paid live calls; capture is not replay approval. |
| `mock` | Historical deterministic acceptance on both integrations | Zero paid calls; **incompatible with current contracts**, migration pending. |

```powershell
# Read-only help; does not start evaluation.
.venv/Scripts/python.exe scripts/run_suite.py --help

# Future authorized comparison; Java is the default path.
.venv/Scripts/python.exe scripts/run_suite.py evaluate --model provider/model --reasoning medium
```

Live modes require `LOOMSPAN_OPENROUTER_API_KEY`. The default model is
`meta/muse-spark-1.3-contributor`, medium reasoning. `--reasoning none` omits the
reasoning parameter. Models and reasoning settings must be supported by the provider.
The runner preserves evidence and restores normal provider-disabled configuration.
Automated success requires separate semantic review; it is not replay approval or
proof of reliability. Original evidence must remain unchanged.

Replay migration and full mock acceptance are separate future work. Use the
[detailed migration and rollback procedure](docs/run-modes.md#replacing-business-fixtures)
only after suitable captures receive checksum-bound review. No existing PR 20
capture is approved for replay.

## Project references

- [Accepted scope and decisions](docs/project-agreement.md)
- [Continuation handoff](docs/implementation-handoff.md)
- [Input contract rationale](docs/input-contract-audit.md)
- [Retention/deletion record](docs/cleanup-retention.md)
- [Selected evidence](evidence/README.md)
- Customer-facing [Framework claims](docs/loomspan-framework-claims.md) and
  [Sidecar claims](docs/loomspan-sidecar-claims.md): validation targets, not blanket acceptance.
- [Business design](docs/equipment-service-design-draft.md) and
  [source pack](docs/equipment-service-source-pack.md): domain rationale; accepted decisions take precedence.

[Archived investigations](archive/2026-10-04-before-muse-baseline/README.md) preserve
history and are not required reading for a new comparison. The bounded cleanup
made no skill, scenario, evaluator, model or limit changes and ran no paid evaluation.
