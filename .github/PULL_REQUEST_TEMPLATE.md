## Summary

- 

## Type

- [ ] Bug fix
- [ ] Skill update
- [ ] New skill
- [ ] Documentation
- [ ] Tooling

## Verification

- [ ] `python tools/lint-agent-skills.py`
- [ ] `python -m unittest discover -s tools -p "test_*.py" -v`
- [ ] `python -m unittest discover -s tests -p "test_*.py" -v`
- [ ] `python -m unittest discover -s experiments/graph-engineering/tests -p "test_*.py" -v`
- [ ] `git diff --check`
- [ ] `python skills/loop-engineering/scripts/validate_loop_contract.py skills/loop-engineering/references/ci-repair-loop-example.md --strict`
- [ ] `python skills/graph-engineering/scripts/validate_graph_contract.py skills/graph-engineering/references/diamond-graph-example.json --strict`
- [ ] `python skills/harness-engineering/scripts/validate_runtime_envelope.py skills/harness-engineering/references/runtime-envelope-example.json --strict`
- [ ] I tested the changed install or usage path.
- [ ] I checked affected links and file paths.
- [ ] I checked `system/config.md` compatibility for wiki-writing changes.
- [ ] I added or updated `assumes`, `conflicts_with`, and `## Success Metrics` for changed skills.
- [ ] I updated examples or troubleshooting notes when behavior changed.
- [ ] I updated `CHANGELOG.md` for user-visible changes.

## Notes

Link related issues and mention anything reviewers should test first.
