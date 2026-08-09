#!/usr/bin/env python3
"""
Unit tests for tools/adapt_skills_to_vault.py
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

import tools.adapt_skills_to_vault as adapt_engine

class TestAdaptSkillsToVault(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.skills_dir = Path(self.temp_dir) / "skills"
        self.vault_dir = Path(self.temp_dir) / "Obsidian Vault"
        
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        self.vault_dir.mkdir(parents=True, exist_ok=True)

        # Create dummy skill
        dummy_skill = self.skills_dir / "wiki-ingest"
        dummy_skill.mkdir()
        (dummy_skill / "SKILL.md").write_text("# Wiki Ingest\nSTOW Contract implementation", encoding="utf-8")

        # Override module targets
        adapt_engine.SKILLS_DIR = self.skills_dir
        adapt_engine.VAULT_DIR = self.vault_dir
        adapt_engine.CONCEPTS_AI_ENG = self.vault_dir / "wiki" / "concepts" / "ai-engineering"
        adapt_engine.CONCEPTS_KNOWLEDGE = self.vault_dir / "wiki" / "concepts" / "knowledge-systems"
        adapt_engine.SOPS_DIR = self.vault_dir / "wiki" / "sops"
        adapt_engine.MAPS_DOMAIN = self.vault_dir / "maps" / "domain-mocs"
        adapt_engine.MAPS_SYSTEM = self.vault_dir / "maps" / "system-indexes"
        adapt_engine.SYSTEM_DIR = self.vault_dir / "system"
        adapt_engine.LOG_FILE = adapt_engine.SYSTEM_DIR / "log.md"
        adapt_engine.LINT_FILE = adapt_engine.SYSTEM_DIR / "lint-report.md"

        adapt_engine.ensure_dirs()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_parse_and_adapt_skill(self):
        dummy_skill = self.skills_dir / "wiki-ingest"
        skill_info = adapt_engine.parse_skill(dummy_skill)
        
        self.assertEqual(skill_info["name"], "wiki-ingest")
        self.assertIn("STOW", skill_info["zh_title"])

        sop_path = adapt_engine.adapt_skill_to_sop(skill_info)
        self.assertTrue(sop_path.exists())
        content = sop_path.read_text(encoding="utf-8")
        self.assertIn("STOW", content)

    def test_generate_skill_index(self):
        dummy_skill = self.skills_dir / "wiki-ingest"
        skill_info = adapt_engine.parse_skill(dummy_skill)
        
        index_path = adapt_engine.generate_skill_index([skill_info])
        self.assertTrue(index_path.exists())
        content = index_path.read_text(encoding="utf-8")
        self.assertIn("wiki-ingest", content)
        self.assertIn("SOP - Wiki 知识提取与入库 (STOW 管道)", content)

    def test_run_vault_lint(self):
        total, broken, links = adapt_engine.run_vault_lint()
        self.assertGreaterEqual(total, 0)
        self.assertTrue(adapt_engine.LINT_FILE.exists())

if __name__ == "__main__":
    unittest.main()
