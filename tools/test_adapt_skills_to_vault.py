import shutil
import tempfile
import unittest
from pathlib import Path

from tools.adapt_skills_to_vault import build_adaptation_plan, parse_skill


class TestAdaptSkillsToVaultCompatibility(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp())
        self.repo = self.temp_dir / "Repository"
        self.vault = self.temp_dir / "Vault"
        skill = self.repo / "skills" / "wiki-ingest"
        skill.mkdir(parents=True)
        self.vault.mkdir()
        (skill / "SKILL.md").write_text("---\nversion: \"8.1.0\"\n---\n# Skill\n", encoding="utf-8")

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_parse_and_plan_without_writes(self) -> None:
        skill = parse_skill(self.repo / "skills" / "wiki-ingest")
        self.assertEqual(skill["name"], "wiki-ingest")
        result = build_adaptation_plan(self.repo, self.vault)
        self.assertEqual(result["side_effect_count"], 0)
        self.assertEqual(len(result["facts"]["proposals"]), 1)
        self.assertFalse((self.vault / "wiki").exists())


if __name__ == "__main__":
    unittest.main()
