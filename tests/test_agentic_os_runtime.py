from __future__ import annotations

import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from tools.agentic_os_runtime import (
    UnknownActionError,
    audit_workflow,
    build_action_registry,
    build_snapshot,
    execute_action,
    generate_skill_registry,
    verify_receipt,
)
from tools.agentic_os import main as agentic_os_main


ROOT = Path(__file__).resolve().parents[1]


class AgenticOSRuntimeTest(unittest.TestCase):
    def test_skill_registry_is_dynamic_and_matches_repository(self) -> None:
        registry = generate_skill_registry(ROOT)
        expected = len([path for path in (ROOT / "skills").iterdir() if path.is_dir()])
        self.assertEqual(expected, registry["skill_count"])
        self.assertEqual(21, registry["skill_count"])
        self.assertIn("workflow-audit", {item["name"] for item in registry["skills"]})
        self.assertEqual(64, len(registry["skill_registry_sha256"]))

    def test_registry_live_actions_are_read_only_and_vault_state_is_host_bound(self) -> None:
        without_vault = build_action_registry(ROOT)
        live = {item["id"] for item in without_vault["actions"] if item["state"] == "LIVE"}
        self.assertEqual({"skill-lint", "runtime-envelope-verify"}, live)
        with tempfile.TemporaryDirectory() as temp_dir:
            with_vault = build_action_registry(ROOT, temp_dir)
            live = {item["id"] for item in with_vault["actions"] if item["state"] == "LIVE"}
            self.assertEqual({"skill-lint", "runtime-envelope-verify", "vault-inventory", "vault-freshness"}, live)
        for item in without_vault["actions"]:
            if item["state"] == "LIVE":
                self.assertEqual("READ_ONLY", item["effect"])

    def test_unknown_action_is_rejected_before_state_write(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            state = Path(temp_dir) / "state"
            with self.assertRaises(UnknownActionError):
                execute_action("not-in-registry", state, ROOT)
            self.assertFalse(state.exists())

    def test_dispatcher_uses_literal_argv_without_shell(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            state = Path(temp_dir) / "state"
            observed: list[dict[str, object]] = []

            def fake_run(argv, **kwargs):
                observed.append({"argv": argv, **kwargs})
                return type("Result", (), {"returncode": 0, "stdout": b"PASS", "stderr": b""})()

            with patch("tools.agentic_os_runtime.subprocess.run", side_effect=fake_run):
                receipt = execute_action("skill-lint", state, ROOT)
            self.assertEqual("SUCCEEDED", receipt["state"])
            self.assertTrue(observed)
            self.assertTrue(all(call["shell"] is False for call in observed))
            self.assertTrue(all(isinstance(token, str) for call in observed for token in call["argv"]))
            self.assertNotIn("--injected", receipt["resolved_argv"])

    def test_missing_vault_is_partial_without_fabricated_zero_metrics(self) -> None:
        snapshot = build_snapshot(ROOT)
        self.assertEqual("PARTIAL", snapshot["status"])
        self.assertIsNone(snapshot["vault"]["counts"])
        self.assertIsNone(snapshot["vault"]["version_counts"])
        self.assertEqual(0, snapshot["side_effect_count"])

    def test_snapshot_with_configured_empty_vault_is_ready_and_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            snapshot = build_snapshot(ROOT, temp_dir)
        self.assertIn(snapshot["status"], {"READY", "PARTIAL"})
        self.assertTrue(snapshot["vault"]["configured"])
        self.assertIsInstance(snapshot["vault"]["counts"], dict)
        self.assertEqual(0, snapshot["side_effect_count"])

    def test_audit_supports_modes_and_bounded_decisions(self) -> None:
        result = audit_workflow(
            {"tasks": ["Every Friday export the report, then retry until complete.", "One-off meeting"]},
            mode="interview",
            max_candidates=1,
        )
        self.assertEqual("AUDITED", result["status"])
        self.assertEqual("interview", result["mode"])
        self.assertEqual(1, len(result["candidates"]))
        self.assertEqual("AUTOMATION_CANDIDATE", result["candidates"][0]["automation_decision"])
        self.assertEqual("LOOP_CANDIDATE", result["candidates"][0]["loop_decision"])
        self.assertEqual("OPERATOR_REVIEW_REQUIRED", result["candidates"][0]["owner"])
        self.assertEqual("DEFINE_BEFORE_PROMOTION", result["candidates"][0]["verifier"])
        self.assertEqual("NO_AUTOMATIC_PROMOTION", result["candidates"][0]["stop_condition"])
        self.assertEqual(0, result["side_effect_count"])

    def test_audit_cli_rejects_a_missing_input_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            missing = Path(temp_dir) / "missing.md"
            output = StringIO()
            with redirect_stdout(output):
                exit_code = agentic_os_main(["audit", "--input", str(missing)])
        self.assertEqual(2, exit_code)
        self.assertIn("workflow audit input does not exist", output.getvalue())

    def test_markdown_audit_ignores_frontmatter_and_prioritises_workflow_evidence(self) -> None:
        result = audit_workflow(
            "---\ntitle: Demo\ndescription: Buy this course\n---\n"
            "**4:26** · Step one is a workflow audit before skill creation and automation.\n"
            "**13:29** · Memory and state management record previous runs for future decisions.\n"
            "One-off sponsor message.",
            mode="manual",
            max_candidates=2,
        )
        evidence = [item["evidence"] for item in result["candidates"]]
        self.assertEqual(2, len(evidence))
        self.assertTrue(all("title:" not in item and "description:" not in item for item in evidence))
        self.assertTrue(any("workflow audit" in item for item in evidence))
        self.assertTrue(any("Memory and state" in item for item in evidence))

    def test_snapshot_finds_latest_run_under_system_runs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            vault = Path(temp_dir)
            manifest = vault / "system" / "runs" / "2026-08" / "run-demo" / "manifest.json"
            manifest.parent.mkdir(parents=True)
            manifest.write_text(
                json.dumps({"run_id": "run-demo", "status": "COMMITTED"}),
                encoding="utf-8",
            )
            snapshot = build_snapshot(ROOT, vault)
        self.assertEqual("run-demo", snapshot["vault"]["latest_run"]["run_id"])
        self.assertEqual("COMMITTED", snapshot["vault"]["latest_run"]["status"])

    def test_receipt_and_verifier_require_zero_side_effects(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            receipt = execute_action("skill-lint", Path(temp_dir) / "state", ROOT)
        valid, errors = verify_receipt(receipt)
        self.assertTrue(valid, errors)
        receipt["side_effect_count"] = 1
        valid, errors = verify_receipt(receipt)
        self.assertFalse(valid)
        self.assertIn("side_effect_count must be zero", errors)


if __name__ == "__main__":
    unittest.main()
