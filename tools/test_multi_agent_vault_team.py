#!/usr/bin/env python3
"""
Unit tests for tools/multi_agent_vault_team.py
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

import tools.multi_agent_vault_team as team_engine

class TestMultiAgentVaultTeam(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.vault_dir = Path(self.temp_dir) / "Obsidian Vault"
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        
        self.commander = team_engine.MultiAgentVaultCommander(vault_dir=self.vault_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_log_ipc_event(self):
        self.commander.log_ipc_event("Worker-1", "Ingest", "DONE", "sources/", "Test evidence")
        self.assertEqual(len(self.commander.ipc_ledger), 1)
        self.assertEqual(self.commander.ipc_ledger[0]["worker_role"], "Worker-1")

    def test_execute_team_mission(self):
        res = self.commander.execute_team_mission()
        self.assertIn("mission_status", res)
        self.assertIn(res["mission_status"], ["SUCCESS", "PARTIAL_FAILURE"])

if __name__ == "__main__":
    unittest.main()
