# Loomspan Sidecar: customer-facing claims

These claims describe Loomspan Sidecar as a whole and the capabilities we want to demonstrate to customers. They are starting claims for this integration suite to prove, not statements that the suite has already verified. We will define the scenarios and operating limits together.

1. **Application integration:** Makes Loomspan execution available to applications through an authenticated asynchronous API.
2. **Concurrent callers:** Supports many simultaneous callers while keeping their executions isolated.
3. **Updates under load:** Lets users validate and publish configuration while the service is busy.
4. **Safe publication:** Prevents competing editors or failed publications from leaving a partially updated runtime.
5. **REST integration:** Executes REST integrations with the correct caller credentials and configuration.
6. **Restart persistence:** Preserves published configuration across restarts.
7. **Overload and slow dependencies:** Handles overload and slow dependencies predictably.
8. **Operator workflows:** Supports configuration transfer and recovery through operator workflows.

## Starting ideas for demonstrating these claims

- Run complex skill trees through the deployed Sidecar API with multiple simultaneous callers.
- Use dummy LLM and downstream services with deterministic results, controlled delays, and deliberate failures.
- Exercise validation, publication, and competing editors while executions are under load.
- Observe correctness through execution results, downstream behavior, the browser console, and diagnostics.

The emphasis is on the complete running system and interactions that isolated unit tests cannot establish convincingly. Framework capabilities are listed separately in [Loomspan Framework claims](loomspan-framework-claims.md).
