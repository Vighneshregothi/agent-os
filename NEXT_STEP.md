# Next Step (Chosen)

## Build the Action Gateway enforcement path end-to-end (single-action, deny-by-default)

Implement the minimal vertical slice first:

1. Add `gateway/action_gateway.py` as the **only** entrypoint for action execution.
2. Validate `ActionRequest` against `schemas/action.schema.json` and reject unknown `action_type`.
3. Evaluate policies via `gateway/policy_engine.py` using **first-match-wins** and deterministic `ALLOW`/`DENY`.
4. On `ALLOW`, execute exactly one browser action through `gateway/executor.py`.
5. Always append an audit event (including `policy_hash`); if audit write fails, fail the action.

### Done criteria

- Molt cannot execute Playwright directly.
- One request results in one action attempt.
- Denied actions never execute.
- Every attempt is auditable with decision + result/error.
