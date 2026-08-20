"""Targeted checks for the V8.1 Agentic OS system navigation surface."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools.worker_flow.contracts import ContractBundle
from tools.worker_flow.deployment import load_system_bundle, plan_system_bundle


ROOT = Path(__file__).resolve().parents[1]


class AgenticOSNavigationTests(unittest.TestCase):
    def test_contract_bundle_load_and_system_plan_on_temp_vault(self) -> None:
        bundle = ContractBundle.load(ROOT)
        self.assertEqual(bundle.version, "8.1.0")
        with tempfile.TemporaryDirectory() as temp_dir:
            vault = Path(temp_dir)
            entries, bundle_hash, bundle_id, deployment = plan_system_bundle(
                ROOT, vault, bundle.version
            )
            self.assertTrue(bundle_hash)
            self.assertEqual(bundle_id, "third-brain-v8.1-system-bundle")
            manifest = json.loads(deployment)
            self.assertEqual(manifest["contract_version"], bundle.version)
            self.assertEqual(len(entries), len(manifest["files"]) + 1)
            self.assertTrue(all(item.target_relative_path.startswith("system/") for item in entries))
            self.assertTrue(all(not item.target_relative_path.startswith("system/runs/") for item in entries))

    def test_new_system_surfaces_are_in_deterministic_bundle(self) -> None:
        bundle = load_system_bundle(ROOT, "8.1.0")
        entries = {(item["source"], item["target"]) for item in bundle["entries"]}
        expected = {
            "contracts/agentic-os/action-registry.json",
            "contracts/agentic-os/registry.schema.json",
            "contracts/agentic-os/snapshot.schema.json",
            "contracts/agentic-os/action-receipt.schema.json",
            "system/vault-navigation.md",
            "system/workflow-registry.md",
            "system/run-history-index.md",
            "system/agentic-os-command-center.md",
            "system/codex.md",
            "system/claude.md",
            "system/templates/vault-agent-navigation-v8.1.md",
        }
        for path in expected:
            with self.subTest(path=path):
                expected_target = (
                    path.replace("contracts/agentic-os/", "system/contracts/v8.1/agentic-os/")
                    if path.startswith("contracts/agentic-os/")
                    else path
                )
                self.assertIn((path, expected_target), entries)

    def test_navigation_reaches_every_contracted_domain_category_tier_and_state_surface(self) -> None:
        contract = json.loads((ROOT / "contracts" / "vault-contract.json").read_text(encoding="utf-8"))
        navigation = (ROOT / "system" / "vault-navigation.md").read_text(encoding="utf-8")
        for domain in contract["taxonomy"]["concept_domains"]:
            self.assertIn(f"wiki/concepts/{domain}/", navigation)
        for category in contract["taxonomy"]["entity_categories"]:
            self.assertIn(f"wiki/entities/{category}/", navigation)
        for tier_path in contract["taxonomy"]["map_tier_paths"].values():
            self.assertIn(f"{tier_path}/", navigation)
        for required in (
            "maps/Home.md",
            "maps/中央索引.md",
            "system/runs/",
            "system/queues/",
            "system/run-history-index.md",
            "system/lint-report.md",
            "system/review-queue.md",
            "system/codex.md",
        ):
            self.assertIn(required, navigation)

    def test_agent_navigation_template_is_current_and_evidence_bounded(self) -> None:
        template = (ROOT / "system" / "templates" / "vault-agent-navigation-v8.1.md").read_text(
            encoding="utf-8"
        )
        self.assertNotRegex(template, r"(?i)V5\.1|16[- ]skill")
        self.assertIn("contract_version: \"8.1.0\"", template)
        self.assertIn("system/vault-navigation.md", template)
        self.assertIn("Codex is the primary host", template)
        self.assertIn("system/codex.md", template)
        self.assertIn("system/runs/", template)
        self.assertIn("generated run receipt", template)
        self.assertIn("source bodies are immutable", template)

    def test_codex_is_primary_and_claude_note_is_only_a_compatibility_redirect(self) -> None:
        codex = (ROOT / "system" / "codex.md").read_text(encoding="utf-8")
        claude = (ROOT / "system" / "claude.md").read_text(encoding="utf-8")
        self.assertIn("Codex is the primary host", codex)
        self.assertIn("~/.agents/skills/", codex)
        self.assertIn("status: deprecated", claude)
        self.assertIn("compatibility", claude.casefold())
        self.assertNotIn("status: active", claude)

    def test_all_bundle_targets_remain_inside_system_surface(self) -> None:
        raw = json.loads((ROOT / "contracts" / "system-bundle.json").read_text(encoding="utf-8"))
        for entry in raw["entries"]:
            target = entry["target"].replace("\\", "/")
            with self.subTest(target=target):
                self.assertTrue(target.startswith("system/"))
                self.assertFalse(target.startswith("system/runs/"))
                self.assertNotIn("maps/", target)
                self.assertNotIn(".claude/", target)


if __name__ == "__main__":
    unittest.main()
