# Dependency Review Intent Plan

## Objective

Review dependency updates and produce either one verified pull request or a
verified no-op receipt.

## Constraints

- Read only the repository and declared dependency sources.
- Stage all file writes in the isolated run workspace.
- Never expose credentials to model context.
- Open at most one pull request and only after approval.
- Emit no external output when no eligible update passes policy and tests.

## Acceptance

- Targeted tests and `git diff --check` pass.
- The external output count does not exceed one.
- The event log, state checkpoint, and final receipt are durable.
