#!/usr/bin/env python3
"""
Unit tests for tools/run_30min_clippings_pipeline.py
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

# Import the module under test
import tools.run_30min_clippings_pipeline as pipeline

class TestClippingsPipeline(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.vault_dir = Path(self.temp_dir) / "Obsidian Vault"
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        
        # Override VAULT_DIR in pipeline module
        pipeline.VAULT_DIR = self.vault_dir
        pipeline.CLIPPINGS_DIR = self.vault_dir / "Clippings"
        pipeline.ARCHIVE_DIR = pipeline.CLIPPINGS_DIR / "Archive"
        pipeline.SOURCES_DIR = self.vault_dir / "sources" / pipeline.CURRENT_MONTH
        pipeline.CONCEPTS_DIR = self.vault_dir / "wiki" / "concepts"
        pipeline.ENTITIES_DIR = self.vault_dir / "wiki" / "entities"
        pipeline.SYSTEM_DIR = self.vault_dir / "system"
        pipeline.LOG_FILE = pipeline.SYSTEM_DIR / "log.md"
        
        pipeline.ensure_dirs()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_scan_empty_inbox(self):
        files = pipeline.scan_inbox()
        self.assertEqual(len(files), 0)

    def test_classify_domain(self):
        ai_text = "Claude and DeepMind are building RAG and Harness for LLM Agents"
        self.assertEqual(pipeline.classify_domain(ai_text), "ai-engineering")
        
        geo_text = "Yen intervention by US and Japan near Strait of Hormuz and Iran"
        self.assertEqual(pipeline.classify_domain(geo_text), "geopolitics-energy")

    def test_process_clipping_file(self):
        clip_file = pipeline.CLIPPINGS_DIR / "Test_AI_Harness.md"
        clip_file.write_text("""---
title: Test AI Harness
source: "https://example.com/ai-harness"
---
Claude and DeepMind are building Harness for LLM Agents.
""", encoding="utf-8")

        inbox_files = pipeline.scan_inbox()
        self.assertEqual(len(inbox_files), 1)

        result = pipeline.process_file(inbox_files[0])
        self.assertTrue(result)

        # Verify archive
        archived_files = list(pipeline.ARCHIVE_DIR.glob("Test_AI_Harness.md"))
        self.assertEqual(len(archived_files), 1)

        # Verify generated concept note
        concept_file = pipeline.CONCEPTS_DIR / "ai-engineering" / "test-ai-harness.md"
        self.assertTrue(concept_file.exists())
        content = concept_file.read_text(encoding="utf-8")
        self.assertIn("Test_AI_Harness", content)
        self.assertIn("Core Thesis", content)

if __name__ == "__main__":
    unittest.main()
