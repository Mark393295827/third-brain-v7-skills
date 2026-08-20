from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools import agentic_os_server, package_agentic_os, sync_vault_codex


ROOT = Path(__file__).resolve().parents[1]


class AgenticOSCommandCentreTest(unittest.TestCase):
    def test_static_surface_is_host_bound_and_has_no_invented_metrics(self):
        html = (ROOT / "tools" / "index.html").read_text(encoding="utf-8")
        self.assertIn("/api/snapshot", html)
        self.assertIn("HOST DISCONNECTED", html)
        self.assertIn("no counts are available", html)
        self.assertIn("x.state==='SUCCEEDED'&&v.result==='PASS'", html)
        self.assertNotIn("20 skills", html)
        self.assertNotIn("211", html)

    def test_host_requires_explicit_state_root(self):
        with self.assertRaises(SystemExit):
            agentic_os_server.build_parser().parse_args([])

    def test_package_allowlist_and_manifest_hashes(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "bundle.zip"
            result = package_agentic_os.package(ROOT, output)
            self.assertTrue(output.is_file())
            self.assertTrue(result["sha256"])
            verified = package_agentic_os.verify_package(output)
            self.assertTrue(verified["ok"], verified)
            with self.assertRaises(KeyError):
                # The manifest is part of the package, but credentials are not.
                import zipfile
                with zipfile.ZipFile(output) as archive:
                    archive.read(".env")

    def test_codex_vault_sync_plans_without_side_effects(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            vault = root / "vault"
            vault.mkdir()
            home = root / "home"
            state = root / "state"
            result = sync_vault_codex.sync(repo_root=ROOT, vault_root=vault, install_home=home, state_root=state)
            self.assertEqual(result["status"], "PLANNED")
            self.assertTrue(vault.is_dir())
            self.assertFalse((vault / "AGENTS.md").exists())
            self.assertFalse((home / ".agents").exists())
            self.assertFalse(state.exists())
            self.assertIn(".claude", result["forbidden"])

    def test_codex_vault_sync_approval_is_allowlisted_and_receipt_ready(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            vault_root = root / "vault"
            vault_root.mkdir()
            install_root = root / "install-home"
            state_root = root / "state"
            result = sync_vault_codex.sync(repo_root=ROOT, vault_root=vault_root, install_home=install_root, state_root=state_root, approve=True)
            self.assertEqual(result["status"], "COMMITTED")
            self.assertTrue((vault_root / "AGENTS.md").is_file())
            self.assertTrue((install_root / ".agents" / "skills" / ".third-brain-v8.1-manifest.json").is_file())
            self.assertFalse((vault_root / ".claude").exists())
            self.assertFalse((vault_root / "settings.local.json").exists())
            self.assertEqual(result["side_effect_count"], 1)


if __name__ == "__main__":
    unittest.main()
