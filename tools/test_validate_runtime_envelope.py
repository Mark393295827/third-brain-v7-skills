from __future__ import annotations

import ast
import copy
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = (
    ROOT
    / "skills"
    / "harness-engineering"
    / "scripts"
    / "validate_runtime_envelope.py"
)
EXAMPLE_PATH = (
    ROOT
    / "skills"
    / "harness-engineering"
    / "references"
    / "runtime-envelope-example.json"
)

SPEC = importlib.util.spec_from_file_location(
    "validate_runtime_envelope", VALIDATOR_PATH
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Unable to load validator: %s" % VALIDATOR_PATH)
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


def valid_envelope():
    return json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))


class RuntimeEnvelopeValidatorTest(unittest.TestCase):
    def test_validator_source_is_python_38_compatible(self):
        source = VALIDATOR_PATH.read_text(encoding="utf-8")
        ast.parse(source, filename=str(VALIDATOR_PATH), feature_version=(3, 8))

    def test_example_passes_strict_validation(self):
        self.assertEqual(
            [],
            validator.validate_envelope(
                valid_envelope(), strict=True, base_dir=EXAMPLE_PATH.parent
            ),
        )

    def test_plan_hash_mismatch_is_rejected(self):
        contract = valid_envelope()
        contract["plan"]["source_sha256"] = "b" * 64
        errors = validator.validate_envelope(
            contract, strict=True, base_dir=EXAMPLE_PATH.parent
        )
        self.assertIn("plan.source_sha256 does not match source plan", errors)

    def test_plan_path_cannot_escape_base_directory(self):
        contract = valid_envelope()
        contract["plan"]["source_path"] = "../outside.md"
        errors = validator.validate_envelope(
            contract, strict=True, base_dir=EXAMPLE_PATH.parent
        )
        self.assertIn("strict plan.source_path escapes base-dir", errors)

    def test_example_passes_strict_cli(self):
        result = subprocess.run(
            [sys.executable, str(VALIDATOR_PATH), str(EXAMPLE_PATH), "--strict"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("PASS runtime envelope", result.stdout)

    def test_model_owned_tool_execution_is_rejected(self):
        contract = valid_envelope()
        contract["runtime"]["tool_execution_owner"] = "model"
        errors = validator.validate_envelope(contract, strict=True)
        self.assertIn("strict runtime.tool_execution_owner must be host", errors)

    def test_secret_visibility_is_rejected(self):
        contract = valid_envelope()
        contract["runtime"]["secrets"]["visible_to_model"] = True
        errors = validator.validate_envelope(contract, strict=True)
        self.assertIn(
            "strict runtime envelope must not expose secrets to the model", errors
        )

    def test_raw_secret_field_is_rejected(self):
        contract = valid_envelope()
        contract["runtime"]["secrets"]["token_value"] = "not-a-real-token"
        errors = validator.validate_envelope(contract, strict=True)
        self.assertIn(
            "strict runtime.secrets field is not allowed: token_value", errors
        )

    def test_wildcard_network_target_is_rejected(self):
        contract = valid_envelope()
        contract["runtime"]["network_allowlist"] = ["*.example.com"]
        errors = validator.validate_envelope(contract, strict=True)
        self.assertTrue(any("exact host" in error for error in errors))

    def test_broad_write_target_is_rejected(self):
        contract = valid_envelope()
        contract["runtime"]["filesystem"]["write"] = ["."]
        errors = validator.validate_envelope(contract, strict=True)
        self.assertIn("strict write target is too broad: .", errors)

    def test_absolute_traversal_and_wildcard_write_targets_are_rejected(self):
        for target in ("C:/repo", "../outside", ".agent-state/*"):
            contract = valid_envelope()
            contract["runtime"]["filesystem"]["write"] = [target]
            errors = validator.validate_envelope(contract, strict=True)
            self.assertIn("strict write target is too broad: %s" % target, errors)

    def test_no_op_requires_a_condition(self):
        contract = valid_envelope()
        contract["runtime"]["output_policy"]["no_op_condition"] = ""
        errors = validator.validate_envelope(contract, strict=True)
        self.assertIn(
            "no_op output requires runtime.output_policy.no_op_condition", errors
        )

    def test_termination_reasons_must_be_disjoint(self):
        contract = valid_envelope()
        contract["termination_policy"]["complete"] = ["same"]
        contract["termination_policy"]["tool_request"] = ["same"]
        errors = validator.validate_envelope(contract, strict=True)
        self.assertIn("termination reason appears in multiple classes: same", errors)

    def test_unknown_termination_must_escalate(self):
        contract = valid_envelope()
        contract["termination_policy"]["escalate"] = ["error"]
        errors = validator.validate_envelope(contract, strict=True)
        self.assertIn(
            "strict termination_policy.escalate must include unknown", errors
        )

    def test_malformed_termination_list_returns_errors_without_crashing(self):
        contract = valid_envelope()
        contract["termination_policy"]["escalate"] = None
        errors = validator.validate_envelope(contract, strict=True)
        self.assertIn("termination_policy.escalate must be a list", errors)
        self.assertIn(
            "strict termination_policy.escalate must include unknown", errors
        )

    def test_external_outputs_require_approval_and_budget(self):
        contract = valid_envelope()
        contract["effects"]["approval_required_for"] = ["published"]
        contract["budgets"]["external_outputs"] = 0
        errors = validator.validate_envelope(contract, strict=True)
        self.assertIn("strict external outputs require external approval", errors)
        self.assertIn("output policy exceeds budgets.external_outputs", errors)

    def test_declared_writes_must_be_staged(self):
        contract = valid_envelope()
        contract["effects"]["stage_writes"] = False
        errors = validator.validate_envelope(contract, strict=True)
        self.assertIn("strict envelopes must stage declared writes", errors)


if __name__ == "__main__":
    unittest.main()
