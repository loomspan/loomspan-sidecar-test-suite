# Project agreement

Current direction agreed 2026-10-06.

## Phases

1. **Framework exploration — complete.** Exercise realistic workflows, uncover
   bugs and identify useful Framework features and refinements.
2. **Skill-level optimization — current.** Vary how skills are composed and how
   reasoning is distributed to help models succeed without Sol-level capability.
3. **Regression and release confidence — future.** Stabilize a durable testing
   system covering Framework features and behavior. Coverage and acceptance criteria
   remain to be designed.

The user authorized a deep Phase 1 cleanup, retaining both apps with all current
skills/configuration as the Phase 2 foundation. Old tests, reports, copied baselines,
replay captures and investigation history are retired from the active project after
an external recoverable snapshot. The two Phase 1 summaries replace that history.
Sol's historical reference designation is retired; no previous model is the oracle
for future experiments.

## Foundation and business boundary

Java embeds real Framework and exposes deterministic SkillMethods. Python/FastAPI
uses real Sidecar and equivalent REST skills. Both demonstrate the same equipment
assessment and explicit approval-bound service-request process. Compare justified
business outcomes, not identical wording or model call counts.

Assessment produces a persisted, immutable recommendation. It creates no service
commitment. Request creation validates a selected assessment/quote, caller identity,
site scope, spending authority, explicit scope/cap approval and idempotency. It ends
at PENDING_DISPATCH, not booking, repair completion or technical clearance.

Keycloak supplies separate user identities through Authorization Code with PKCE.
Maya may assess; Luis may also request service. Contact records and model-authored
fields do not grant authority. Loaner procurement is outside the implemented service
request workflow. Preserve the independent business source facts and authorization
boundary when designing experiments.

## Working boundaries

Keep current apps, skills/configuration and fixtures as the initial Phase 2 starting
point. The cleanup itself makes no skill optimization or model-default change.
Experiment designs, success criteria, model choices and budgets remain to be agreed.
Explicit authorization is required for paid runs. Normal provider access stays disabled.
Do not embed the answer to a fixed example as a substitute for a general skill method.

Separate execution/transport fidelity from business judgment. New findings may still
identify Framework defects, but Phase 2's focus is skill design. The small smoke check
only verifies a runnable foundation; comprehensive regression work belongs to Phase 3.

No replay promotion, commit, push or release is authorized by the cleanup. Preserve
local credentials and business databases. New experiment results should have clear
identities and scope without reintroducing the retired Phase 1 dependencies.

## Simple four-mode runner — agreed 2026-10-06

Use one runner for `mock`, `live`, `evaluate` and `capture`, with shared execution,
collection and reporting. Edit the current skills directly. Compare a focused change
with the last accepted result; commit accepted improvements or revert the specific
unsuccessful edits while preserving other work. No variant registry, experiment trees
or comparison matrix are needed. Runner implementation is authorized; no paid run or
Git commit is authorized by that implementation request.

Record the model, scenarios, authored skill/configuration hashes, effective runtime
configuration and artifact identities. Keep a latest result and a manually maintained
accepted result instead of accumulating every attempt. The default latest report/bundle
is replaced; named outputs must be new directories. Capture never approves a fixture.
Mock remains explicitly unavailable until compatible approved fixtures and their replay
support are established. It must not load obsolete captures or fall back to paid calls.

The initial runner covers baseline and priority assessment scenarios. Scenario checks
are separate from orchestration; full service-request regression and broad release
coverage remain future work. Human business review remains distinct from execution
and exact-preservation checks. Repeated evidence of improvement is a working practice,
not an experiment-management subsystem.
