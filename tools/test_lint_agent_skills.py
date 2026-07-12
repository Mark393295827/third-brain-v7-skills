from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LINTER = ROOT / "tools" / "lint-agent-skills.py"
TEMPLATE = ROOT / "docs" / "skill-template.md"
ADAPTERS = [
    ROOT / "adapters" / "cursor" / "third-brain-skills.mdc",
    ROOT / "adapters" / "windsurf" / "third-brain-skills.md",
]


def skill_text(
    *,
    name: str = "sample-skill",
    profile: str = "one-shot",
    body_extra: str = "",
    metadata: bool = True,
) -> str:
    if metadata:
        frontmatter = f"""---
name: {name}
description: Use when a bounded sample operation needs verification.
metadata:
  version: "7.0.0"
  updated: "2026-07-11"
  profile: "{profile}"
  assumes: "The input is available."
  conflicts_with: "Fabricating unavailable evidence."
---"""
    else:
        frontmatter = f"""---
name: {name}
description: Use when a bounded sample operation needs verification.
version: "7.0.0"
updated: "2026-07-11"
profile: "one-shot"
assumes: "The input is available."
conflicts_with: "Fabricating unavailable evidence."
---"""

    body = f"""# Sample Skill

<skill_contract>

## Usage Template

Provide the objective and evidence.

## Workflow

<intake>
Validate the request.
</intake>

<unknowns_gate>
Return `NEEDS_INPUT` when a required fact is missing.
</unknowns_gate>

<execute>
Produce the smallest useful result.
</execute>

<evaluate>
Check the result against the request using fresh evidence.
</evaluate>

{body_extra}

## Failure Protocol

Use `NEEDS_INPUT`, `VERIFY_FAILED`, or `BUDGET_STOP`; preserve prior valid state.

## Output Contract

Return status, result, evidence, unknowns, and next_action.

## Edge Cases

- Missing evidence: return `NEEDS_INPUT` with one minimal probe.
- Failed verification: return `VERIFY_FAILED` and do not claim completion.

## Success Metrics

- The requested result is present and verified.

## Quality Gates

- [ ] Required evidence is cited.
- [ ] Completion is supported by a fresh check.

</skill_contract>"""
    return f"{frontmatter}\n\n{body}\n"


class AgentSkillsLinterTest(unittest.TestCase):
    def run_lint(self, skill: str, *, extra_files: dict[str, str] | None = None):
        with tempfile.TemporaryDirectory() as temp_dir:
            skills_dir = Path(temp_dir) / "skills"
            skill_dir = skills_dir / "sample-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(skill, encoding="utf-8")
            for relative_path, contents in (extra_files or {}).items():
                target = skill_dir / relative_path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(contents, encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(LINTER), "--skills-dir", str(skills_dir)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

    def assert_lint_error(self, skill: str, expected: str) -> None:
        result = self.run_lint(skill)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(expected, result.stdout + result.stderr)

    def test_valid_v7_skill_passes(self) -> None:
        result = self.run_lint(skill_text())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_canonical_template_passes_its_linter(self) -> None:
        document = TEMPLATE.read_text(encoding="utf-8")
        template = document.split("````markdown\n", 1)[1].split("\n````", 1)[0]
        template = template.replace("name: skill-name", "name: sample-skill", 1)
        template = template.replace("YYYY-MM-DD", "2026-07-11")
        result = self.run_lint(template)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_repository_skills_pass(self) -> None:
        result = subprocess.run(
            [sys.executable, str(LINTER)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_adapters_route_every_skill(self) -> None:
        skill_names = {path.name for path in (ROOT / "skills").iterdir() if path.is_dir()}
        for adapter in ADAPTERS:
            content = adapter.read_text(encoding="utf-8")
            missing = sorted(name for name in skill_names if name not in content)
            self.assertEqual(missing, [], f"{adapter} is missing routes: {missing}")

    def test_governance_must_be_nested_under_metadata(self) -> None:
        self.assert_lint_error(
            skill_text(metadata=False),
            "frontmatter missing metadata.assumes",
        )

    def test_stateful_profile_requires_state_contract(self) -> None:
        self.assert_lint_error(
            skill_text(profile="stateful"),
            "stateful profile requires <state_contract>",
        )

    def test_loop_profile_requires_retry_policy(self) -> None:
        body = """<state_contract>Persist state atomically.</state_contract>"""
        self.assert_lint_error(
            skill_text(profile="loop", body_extra=body),
            "loop profile requires <retry_policy>",
        )

    def test_model_brand_routing_is_rejected(self) -> None:
        self.assert_lint_error(
            skill_text(body_extra="Route hard work to Opus."),
            "model routing must use capabilities",
        )

    def test_missing_local_resource_is_rejected(self) -> None:
        self.assert_lint_error(
            skill_text(body_extra="Run `scripts/missing.py`."),
            "references missing local resource: scripts/missing.py",
        )

    def test_plain_slash_words_are_not_resource_references(self) -> None:
        result = self.run_lint(
            skill_text(body_extra="Capabilities may include skills/scripts/evals."),
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_duplicate_when_to_use_section_is_rejected(self) -> None:
        self.assert_lint_error(
            skill_text(body_extra="## When to Use\n\nUse this sample."),
            "duplicate trigger section",
        )

    def test_skill_at_line_limit_is_rejected(self) -> None:
        skill = skill_text() + ("padding\n" * 500)
        self.assert_lint_error(skill, "SKILL.md has")


if __name__ == "__main__":
    unittest.main()
