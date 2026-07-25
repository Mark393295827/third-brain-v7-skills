# Release Playbook

This playbook turns the repository's iteration strategy into a repeatable weekly loop.

## Weekly Feedback Loop

Run this once per week:

1. Review open Issues and PRs.
2. Label each item as `bug`, `skill-request`, `docs`, `good-first-issue`, `needs-info`, or `high-frequency-pain`.
3. Reply to every new issue, even if the answer is only a triage note.
4. Pick 1-2 user-visible fixes or improvements for the next small release.
5. Update `CHANGELOG.md` before tagging a release.

## Priority Order

1. Broken install or skill loading.
2. Data loss, misleading verification, or incorrect claim behavior.
3. High-frequency user confusion from README, GUIDE, or templates.
4. Small "wow" improvements that make the first successful run faster.
5. Larger new skills or architecture changes.

## Required Verification

Run these commands after the final material change. CI runs the same checks on Python 3.8 and 3.13, covering the declared minimum and current runtime:

```bash
python tools/lint-agent-skills.py
python -m unittest discover -s tools -p "test_*.py" -v
python -m unittest discover -s experiments/graph-engineering/tests -p "test_*.py" -v
git diff --check
python skills/loop-engineering/scripts/validate_loop_contract.py skills/loop-engineering/references/ci-repair-loop-example.md --strict
python skills/graph-engineering/scripts/validate_graph_contract.py skills/graph-engineering/references/diamond-graph-example.json --strict
```

Record the command, exit status, and key output in the PR. A partial or stale run does not support a release claim.

## Small Release Checklist

- [ ] Fix or improve 1-2 focused things.
- [ ] Add or update a usage example.
- [ ] Update `CHANGELOG.md`.
- [ ] Run the Agent Skills linter.
- [ ] Run full unittest discovery.
- [ ] Run the bounded Graph architecture experiment tests.
- [ ] Run `git diff --check`.
- [ ] Run the strict Loop contract example.
- [ ] Run the strict Graph contract example.
- [ ] Verify changed install targets still work.
- [ ] Create a GitHub Release with a short changelog.
- [ ] Reply to the issues or PRs that the release addresses.

## README Discovery Checklist

- [ ] First screen has a clear value proposition.
- [ ] Install commands are copyable.
- [ ] At least one quick prompt shows the expected workflow.
- [ ] Demo or screenshot links are easy to find.
- [ ] Troubleshooting covers the most common failure mode.
- [ ] The README has one honest star CTA tied to user value.
- [ ] The release has a short launch post ready for X / HN / Product Hunt.

## Launch Checklist

- [ ] Publish one X thread from `outreach/launch/x-thread.md`.
- [ ] Submit Show HN only when README and demo links are stable.
- [ ] Convert repeated launch feedback into docs or examples within 48 hours.

## Suggested GitHub Topics

Use concise topics so the repo is discoverable:

`agent-skills`, `codex-cli`, `claude-code`, `gemini-cli`, `llm-wiki`, `knowledge-management`, `personal-knowledge-base`, `ai-agents`, `obsidian`, `agentic-workflow`, `context-engineering`
