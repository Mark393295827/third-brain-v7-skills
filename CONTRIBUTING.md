# Contributing to Third Brain V7 Skills

Thanks for considering contributing! This project aims to make personal knowledge compounding accessible to everyone.

## How to Contribute

### 1. Report Issues

Use the bug report template and include:
- What you tried
- What happened
- What you expected
- Your agent harness and version

Maintainers should triage new issues weekly, reply quickly, and label high-frequency pain points before planning the next small release.

### 2. Suggest Skills

Have a recurring workflow that should be a skill? Use the skill request template with:
- **When to use** — when should this skill activate?
- **What it should do** — step-by-step workflow
- **How to verify** — how do we know it works?

### 3. Submit Pull Requests

PRs are welcome! Please:

1. **Read the PR template** at `.github/PULL_REQUEST_TEMPLATE.md` (if exists) or follow:
2. **One skill per PR** — makes review faster
3. **Follow the V7 Skill format**:
   ```yaml
   ---
   name: your-skill
   description: One-line owned transformation. Use when the trigger applies.
   metadata:
     version: "7.0.0"
     updated: "YYYY-MM-DD"
     profile: "one-shot"
     assumes: "Required operating condition."
     conflicts_with: "Boundary that must not be overridden."
   ---
   ```
4. **Use the canonical template** — include Workflow, Failure Protocol, Output Contract, Edge Cases, Success Metrics, and Quality Gates
5. **Run the linter** — `python tools/lint-agent-skills.py`

### 4. Release Small, Useful Updates

The preferred release rhythm is one small release every 1-2 weeks when there is a meaningful user-visible improvement.

Each release should:
- Fix 1-2 focused issues or add one small "wow" improvement
- Update `CHANGELOG.md`
- Include a clear GitHub Release note
- Reply to the Issues or PRs addressed by the release

See [docs/release-playbook.md](docs/release-playbook.md) for the weekly triage and release checklist.

### Skill Standards

Every skill in this repo must have:

| Element | Required | Example |
|---------|----------|---------|
| YAML frontmatter | ✅ | discovery fields plus nested V7 metadata |
| Trigger | ✅ | complete `Use when` clause in `description` |
| Structured Workflow | ✅ | intake, unknowns, execute, evaluate |
| Failure + Output | ✅ | standard code and inspectable receipt |
| Edge Cases | ✅ | at least two expensive failure examples |
| Quality Gates | ✅ | objective completion checklist |

### Code of Conduct

Be respectful, constructive, and patient. This is a learning project as much as a utility.
