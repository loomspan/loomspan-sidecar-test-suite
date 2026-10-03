# Loomspan Framework: customer-facing claims

These claims describe Loomspan Framework as a whole and the capabilities we want to demonstrate to customers. They are starting claims for this integration suite to prove, not statements that the suite has already verified. We will define the scenarios and operating limits together.

1. **Complex planning:** Executes complex, nested skill plans while respecting dependencies and preserving the mission objective and required evidence through completion.
2. **Concurrent steps:** Executes independent plan steps concurrently.
3. **Structured output and recovery:** Enforces output contracts and supports correction of invalid model output while preserving required evidence and citations. Invalid output does not proceed as a successful result.
4. **Mixed capabilities:** Combines model reasoning with deterministic Java and REST operations.
5. **Authorization:** Enforces caller permissions throughout nested and parallel execution.
6. **Failure handling:** Handles provider errors, retries, and timeouts without corrupting execution state.
7. **Concurrent executions:** Runs many complex executions concurrently without mixing their inputs, identities, results, or diagnostics.
8. **Updates during execution:** Allows skill and configuration updates while existing executions continue consistently.
9. **Useful diagnostics:** Provides diagnostics that explain what happened across complex executions.
10. **Predictable shutdown:** Shuts down predictably while work is running.

## Starting ideas for demonstrating these claims

- Build complex skill trees with parallel branches, nested planners, dependencies, and deterministic Java and REST operations.
- Use dummy LLM services programmed to return deterministic responses, including malformed output, errors, and delayed responses.
- Explore 50 simultaneous executions of complex plans and verify isolation and correctness. Fifty is an initial validation target, not an established capacity promise.
- Validate and publish configuration while those executions are running.

The emphasis is on interactions and operating conditions that isolated unit tests cannot establish convincingly.

Individual observations establish only the scenarios and operating conditions
documented with their evidence. Successful controlled replay does not by itself
establish fresh model reasoning or a universal recovery guarantee.
