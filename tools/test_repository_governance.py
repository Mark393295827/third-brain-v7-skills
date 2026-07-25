from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_RELEASE_COMMANDS = (
    "python tools/lint-agent-skills.py",
    'python -m unittest discover -s tools -p "test_*.py" -v',
    'python -m unittest discover -s experiments/graph-engineering/tests '
    '-p "test_*.py" -v',
    "git diff --check",
    "python skills/loop-engineering/scripts/validate_loop_contract.py "
    "skills/loop-engineering/references/ci-repair-loop-example.md --strict",
    "python skills/graph-engineering/scripts/validate_graph_contract.py "
    "skills/graph-engineering/references/diamond-graph-example.json --strict",
)


def normalized(text: str) -> str:
    return " ".join(text.split())


def numbered_checks(text: str) -> list[str]:
    return [
        match.rstrip(";.").strip()
        for match in re.findall(r"^\d+\.\s+(.+)$", text, flags=re.MULTILINE)
    ]


class RepositoryGovernanceTest(unittest.TestCase):
    def test_wiki_lint_command_matches_all_twelve_skill_checks(self) -> None:
        skill = (ROOT / "skills" / "wiki-lint" / "SKILL.md").read_text(encoding="utf-8")
        command = (ROOT / "commands" / "wiki-lint.md").read_text(encoding="utf-8")

        skill_checks = numbered_checks(skill)
        command_checks = numbered_checks(command)

        self.assertEqual(len(skill_checks), 12)
        self.assertEqual(command_checks, skill_checks)

    def test_hooks_are_documentation_only(self) -> None:
        hooks_dir = ROOT / "hooks"
        shipped = sorted(path.name for path in hooks_dir.iterdir() if path.name != "README.md")
        readme = (hooks_dir / "README.md").read_text(encoding="utf-8")

        self.assertEqual(shipped, [])
        self.assertIn("No executable hooks are shipped", readme)
        self.assertIn("design examples, not files", readme)

    def test_repository_lint_report_is_an_explicit_non_evidence_placeholder(self) -> None:
        report = (ROOT / "system" / "lint-report.md").read_text(encoding="utf-8")

        self.assertIn('status: template', report)
        self.assertIn("NO_SCAN_EVIDENCE", report)
        self.assertIn("not a health receipt", report)

    def test_changelog_declares_the_v71_twenty_skill_baseline(self) -> None:
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        current_header = "\n".join(changelog.splitlines()[:12])

        self.assertIn("Third Brain V7 Skills", current_header)
        self.assertIn("Current V7.1 baseline: 20 Agent Skills.", current_header)

    def test_release_surfaces_include_the_required_commands(self) -> None:
        surfaces = (
            ROOT / "docs" / "release-playbook.md",
            ROOT / ".github" / "PULL_REQUEST_TEMPLATE.md",
            ROOT / ".github" / "workflows" / "quality.yml",
        )

        for surface in surfaces:
            content = normalized(surface.read_text(encoding="utf-8"))
            with self.subTest(surface=surface):
                for command in REQUIRED_RELEASE_COMMANDS:
                    self.assertIn(normalized(command), content)

    def test_ci_covers_declared_minimum_and_current_python(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "quality.yml").read_text(
            encoding="utf-8"
        )

        self.assertIn('actions/checkout@v6', workflow)
        self.assertIn('actions/setup-python@v6', workflow)
        self.assertIn('- "3.8"', workflow)
        self.assertIn('- "3.13"', workflow)

    def test_current_guides_use_v71_main_and_the_hardened_installer(self) -> None:
        guide = (ROOT / "docs" / "v7-max-potential-guide-zh.md").read_text(
            encoding="utf-8"
        )
        discovery = (ROOT / "docs" / "community-discovery.md").read_text(
            encoding="utf-8"
        )

        self.assertNotIn("codex/v7-skill-contract-refactor", guide)
        self.assertNotIn("Copy-Item -Recurse", guide)
        self.assertIn(r".\install.ps1 codex", guide)
        self.assertIn("git switch main", guide)
        self.assertIn("PowerShell 5.1+", (ROOT / "GUIDE.md").read_text(encoding="utf-8"))
        self.assertTrue((ROOT / "install.ps1").is_file())
        self.assertIn("Third Brain V7.1", discovery)
        self.assertIn("20 profile-aware Agent Skills", discovery)


if __name__ == "__main__":
    unittest.main()
