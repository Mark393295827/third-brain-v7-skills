# Hooks

No executable hooks are shipped in this repository. This directory documents optional Claude Code integration ideas only.

| Design example | Possible trigger | Intended purpose |
|---|---|---|
| `session-stop` | Session end | Run `session-learn` after an explicit, tested integration is installed. |
| `before-tool` | Before a tool call | Add a bounded verification gate without claiming that a prompt-only hook can enforce policy. |

`session-stop` and `before-tool` are names for design examples, not files or enabled runtime behavior. Do not copy `hooks/*` into `.claude/hooks/`: there is nothing executable to install.

Before adding a real hook, define its trigger, permissions, timeout, failure behavior, observable receipt, and rollback path; then ship and test the executable separately.
