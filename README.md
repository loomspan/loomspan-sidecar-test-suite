# Loomspan reference applications and acceptance suite

**Latest full Muse baseline (2026-10-01):** `meta/muse-spark-1.3-contributor`, medium reasoning, ran once on each path after offline fixes and successful access checks. Java failed on malformed step-action JSON after correction; Sidecar published its assessment with unchanged quotes and correct monetary units but has semantic wording findings. Focused assertions: 6 passed / 2 failed. Both Framework traces are retained. The capture remains unapproved for replay. See `evidence/review-live-20261001-220102/summary.md` and implementation status.

**Implementation authorized on 2026-10-01; first delivery remains incomplete.** Both paths build and run with the user-authorized Framework beta.8-SNAPSHOT timeout fix. The latest full Muse run completed on Sidecar and failed on Java model JSON; semantic review keeps the bundle unapproved. See [implementation status](docs/implementation-status.md), [run review](evidence/review-live-20261001-220102/summary.md), and [local build/run instructions](docs/local-run.md). Historical planning and compatibility text below is not acceptance evidence.

This project will demonstrate and verify customer-facing Loomspan capabilities through two REST-only reference microservices implementing the same business workflow:

- An embedded Java application using Loomspan as a Maven dependency and deterministic operations exposed as `@SkillMethod` skills.
- A Python/FastAPI application integrating with Loomspan Sidecar and exposing equivalent operations as REST skills.

Shared scenarios will exercise complex skill trees, concurrent executions, failure handling, and configuration changes under load using deterministic dummy LLM and downstream services.

The shared acceptance runner is Python/pytest, initially running on Windows and exercising both applications through HTTP with independently authored expectations. Docker Compose runs the Java application, Python application, pinned Sidecar, Keycloak and Python/FastAPI fixture services. Fixtures run separately from the applications and runner, supplying scripted external responses, gates and independent request journals.

The dummy model serves non-streaming OpenAI Chat Completions at `/v1/chat/completions` through the real Framework provider client in both paths. Scripts are execution-specific, match stages/attempts and required evidence, and use separate harness controls for registration, gates and journals.

Each run will retain an evidence directory containing its manifest, independent fixture journals and business records, logs, Framework-generated trace files from both integration paths, and linked Markdown/machine-readable results. Supported Framework NDJSON collection is implemented and has produced actual trace files on both paths.

First delivery includes optional real-model execution for both applications. During the build, all prompts/model responsibilities will be exercised in complete real-model workflows; reviewed captures will seed versioned replay scripts with provenance and explicitly labeled fault mutations. Ordinary acceptance runs use those scripts without live-provider calls. The initial real-model baseline is OpenRouter `openai/gpt-6.1-sol` with `medium` reasoning for both versions. No project-level spending budget is required for this small test. The provider key is supplied through `LOOMSPAN_OPENROUTER_API_KEY`. Live compatibility and partial workflow captures exist; none is approved as a complete replay baseline.

Both applications will trust a local Keycloak instance for normal demonstrations and acceptance tests. Java will use Spring Security, and Python will use FastAPI security dependencies with PyJWT. Explicit role and token-audience contracts will govern authorization across application and skill boundaries; controlled token fixtures will support specialized negative tests.

Maya and Luis obtain access tokens using Authorization Code with PKCE through Keycloak's login page: a browser login helper supports manual demonstrations, and Playwright automates seeded-user login for acceptance tests against both versions.

Both versions use the accepted `ASSESS_EQUIPMENT` and `REQUEST_SERVICE` permissions in a top-level Keycloak `roles` array and shared logical resource audience `equipment-service`. Java and Sidecar map roles with the `ROLE_` authority prefix; Python checks unprefixed names. Site assignments and spending limits remain authoritative application records. Java propagates the verified caller in its security context; Python/Sidecar passes through the caller's access token. Keycloak 26.3.5 provisioning and PKCE login are implemented; broader authorization acceptance remains outstanding.

**Current stage: implementation and compatibility verification, first delivery incomplete.** The [implementation handoff](docs/implementation-handoff.md) still defines the delivery boundary. Reviewed full-workflow replay and acceptance must not be claimed from the passing compatibility checks.

Independent fixture/capture-review checks and controlled nested-denial diagnostics pass; both denial paths retain actual Framework traces. These handcrafted, incomplete-approval diagnostics do not replace valid-approval authorization acceptance or reviewed real-model replay. The subsequent local snapshot test is explicitly authorized; it does not require a new published release. See [status](docs/implementation-status.md) and [opt-in diagnostic instructions](docs/local-run.md).

**Active local test baseline:** Framework `1.0.0-beta.8-SNAPSHOT`, source reference `b7dbefee8ffca873e84efb455e5609234c59e119`, with identical installed Framework bytes packaged in both hosts. Sidecar uses beta.2 source (`da3bb8f8ae6087955f9b3a6bd02b9706d3b582e7`) with that dependency override. This is not the published Sidecar binary. Earlier released beta.7/beta.2 build checks and evidence remain preserved.

## Start here

Read [Project agreement and conversation handoff](docs/project-agreement.md) before continuing design or implementation. It records the agreed direction, recommendations that remain open, and the next decisions.

For the next coding context, read the [implementation handoff](docs/implementation-handoff.md), which consolidates the baseline, recommended build sequence, completion criteria and starter prompt. Implementation is already authorized; resume from its current-state section rather than rebuilding the foundations.

Read [Equipment service resolution](docs/equipment-service-resolution.md) for the selected business problem, illustrative request, and model versus deterministic responsibilities.

For the accepted domain details and retained design history, read the [working design](docs/equipment-service-design-draft.md) and [fictional source pack](docs/equipment-service-source-pack.md). These describe the people, manual, warranty/service terms, repair history, skill tree, scenario portfolio, and business contracts. Apply the agreement’s accepted decisions; historical open/proposed wording does not reopen settled choices.

The initial customer-facing claims are maintained in:

- [Loomspan Framework claims](docs/loomspan-framework-claims.md)
- [Loomspan Sidecar claims](docs/loomspan-sidecar-claims.md)

These are claims to demonstrate, not completed verification results.

## Related projects

- [Loomspan Framework](https://github.com/loomspan/loomspan-framework), normally checked out beside this repository as `../loomspan-framework`.
- [Loomspan Sidecar](https://github.com/loomspan/loomspan-sidecar), normally checked out beside this repository as `../loomspan-sidecar`.

The current development environment is Windows with PowerShell and Docker. Local execution comes first; GitHub Actions follows later.
