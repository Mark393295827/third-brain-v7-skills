# Baseline Receipt

Captured before commander-authored integration changes on branch
`codex/v8.1-unification`.

## Protected worktree

- The branch was created from `main` without committing, stashing, resetting,
  cleaning, restoring, or otherwise changing the owner's existing worktree.
- Pre-existing modified, deleted, and untracked files remain in place.
- The only new files before this receipt were the approved command board and
  token ledger under this mission directory.

## Fresh checks

| Check | Result |
|---|---|
| Agent Skills linter | PASS, 20 skills |
| Transactional worker-flow tests | PASS, 39 tests |
| Graph architecture experiment tests | PASS, 22 tests |
| Repository diff whitespace | PASS, with existing LF/CRLF warnings |
| Tools test suite | STOPPED after hanging in legacy `test_execute_team_mission`; preceding tests passed |

The hanging process was positively identified as the Python process launched by
this baseline command and was terminated by exact PID. No unrelated process was
stopped.

## Baseline interpretation

The canonical transactional runtime is green before integration. The legacy
multi-agent wrapper is not suitable for the default CI path until it is made
bounded or replaced with a compatibility facade.
