# Compatibility

Third Brain V8.1 includes 21 skills using the open Agent Skills-style `SKILL.md` format. Codex OS is the primary host; compatibility has two levels:

1. Native skills: the tool can discover `SKILL.md` files directly.
2. Rules/context adapter: the tool can read these skills through project rules, `AGENTS.md`, or manual prompt context.

## Support Matrix

| Tool | Support Level | Recommended Setup |
|------|---------------|-------------------|
| Codex CLI | Native | Run `bash install.sh codex` or `.\install.ps1 codex`. |
| Claude Code | Explicit compatibility adapter | Run `bash install.sh claude` or `.\install.ps1 claude`. |
| Gemini CLI | Native-compatible | Run `bash install.sh gemini` or `.\install.ps1 gemini`. |
| Windsurf / Cascade | Native + rules | Run `bash install.sh windsurf` or `.\install.ps1 windsurf`. |
| Cursor | Rules/context adapter | Run `bash install.sh cursor` or `.\install.ps1 cursor`. |
| Other AI IDEs | Prompt/context adapter | Keep `AGENTS.md`, `skills/`, and `examples/`; ask the agent to read the relevant `SKILL.md`. |

## V8.1 Engineering Routing

Loop Engineering = temporal depth. Graph Engineering = dependency width. Agent Teams Command = process ownership, IPC, and integration. Harness Engineering = runtime scheduler, permissions, and observability.

- Route repeated execution through time to `loop-engineering`.
- Route explicit dependencies, independently executable branches, typed joins, or node-local recovery to `graph-engineering`.
- Route worker process ownership, IPC, and integration to `agent-teams-command`.
- Route runtime scheduling, permissions, and observability to `harness-engineering`.

Add `graph-engineering` after `loop-engineering` only when its admission value exceeds orchestration and review cost. V8.1 supports bounded static DAGs; dynamic expansion and cyclic graphs are not supported.

## Cursor Setup

Cursor supports project rules under `.cursor/rules/` and can also use `AGENTS.md` as a simple project instruction file. Use the adapter template in [adapters/cursor/third-brain-skills.mdc](../adapters/cursor/third-brain-skills.mdc).

```bash
bash install.sh cursor
```

Recommended prompt:

```text
Use the Third Brain V8.1 skill router. Select the relevant `skills/*/SKILL.md`, inspect `metadata.profile` plus `assumes`/`conflicts_with`, then follow the Usage Template, Workflow, Failure Protocol, Output Contract, Success Metrics, Quality Gates, and the V8.1 promotion gate. Route explicit dependency DAGs to `graph-engineering` only after its admission value exceeds orchestration and review cost.
```

## Windsurf Setup

Windsurf Cascade supports workspace skills in `.windsurf/skills/<skill-name>/SKILL.md`, global skills in `~/.codeium/windsurf/skills/<skill-name>/SKILL.md`, and workspace rules in `.windsurf/rules/*.md`.

Workspace skills:

```bash
bash install.sh windsurf
```

Recommended prompt:

```text
Use @wiki-ingest on this source, resolve paths from system/config.md, then verify the created files and list the single-source claims.
```

## Other Tools

For tools without native skill discovery:

1. Keep `AGENTS.md` at the repo root.
2. Keep `skills/` and `examples/` in the repo.
3. Start with one explicit prompt:

```text
Read AGENTS.md and the relevant skills/*/SKILL.md before acting. Check metadata.profile plus assumes/conflicts_with; follow Usage Template, Workflow, Failure Protocol, Output Contract, Success Metrics, Quality Gates, and the V8.1 promotion gate; resolve wiki paths from the canonical vault contract.
```

## Notes

- Prefer native skills when the tool supports `SKILL.md`.
- Prefer rules for lightweight routing instructions.
- Prefer examples when the user wants a copyable workflow rather than an always-on behavior rule.
- Prefer `system/config.md` over hard-coded vault paths in tools that write wiki files.

## References

- Cursor Rules documentation: https://docs.cursor.com/en/context/rules
- Windsurf Memories & Rules: https://docs.windsurf.com/windsurf/cascade/memories
- Windsurf Cascade Skills: https://docs.windsurf.com/windsurf/cascade/skills
