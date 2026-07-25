from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = (
    ROOT
    / "skills"
    / "loop-engineering"
    / "scripts"
    / "validate_loop_contract.py"
)
SKILL_PATH = ROOT / "skills" / "loop-engineering" / "SKILL.md"
VALID_EXAMPLE = (
    ROOT
    / "skills"
    / "loop-engineering"
    / "references"
    / "ci-repair-loop-example.md"
)

SPEC = importlib.util.spec_from_file_location("validate_loop_contract", VALIDATOR_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load validator: {VALIDATOR_PATH}")
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


def valid_fields() -> dict[str, str]:
    return {
        "objective": "Repair the bounded failing workflow.",
        "mode": "Goal.",
        "trigger": "Manual start from fresh failure evidence.",
        "scope": "One package and its tests.",
        "non-goals": "No dependency upgrades or external changes.",
        "owner": "Primary agent.",
        "inputs": "Failure log and current repository state.",
        "artifacts path": ".agent-state/artifacts/.",
        "state path": ".agent-state/loop-state.md.",
        "work clock": ".agent-state/work-clock.md.",
        "success metric": "Tests and lint both exit zero.",
        "evidence": "Fresh command output and diff.",
        "verifier": "Deterministic test and lint commands.",
        "topology": "single-agent.",
        "max iterations": "4.",
        "time limit": "35 minutes.",
        "budget": "18 tool calls.",
        "review budget": "800 changed lines and 8 files.",
        "stop condition": "Verifier passes or a finite cap fires.",
        "write-back": "Append the receipt to the state path.",
        "permission boundary": "Local-only writes; no production or external changes.",
        "recovery": "Restore the prior checkpoint after a regression.",
    }


class LoopContractValidatorTest(unittest.TestCase):
    def test_parses_compact_contract_template_from_skill(self) -> None:
        skill = SKILL_PATH.read_text(encoding="utf-8")
        match = re.search(
            r"Write this contract before acting:\s*```text\r?\n(.*?)\r?\n```",
            skill,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(match, "compact Loop Contract template not found")

        with tempfile.TemporaryDirectory() as temp_dir:
            contract = Path(temp_dir) / "compact-loop-contract.txt"
            contract.write_text(match.group(1), encoding="utf-8")
            fields = validator.parse_contract(contract)

        self.assertEqual(set(validator.REQUIRED) - set(fields), set())
        self.assertEqual(fields["objective"], "")
        self.assertEqual(fields["mode"], "Goal | Loop | Automation | AutoResearch")
        self.assertEqual(
            fields["topology"],
            "single-agent | maker-checker | manager-workers",
        )

    def test_rejects_non_positive_numeric_caps(self) -> None:
        invalid_caps = {
            "max iterations": "0",
            "time limit": "-1 minutes",
            "budget": "0 calls",
            "review budget": "-5 changed lines",
        }

        for field, value in invalid_caps.items():
            with self.subTest(field=field, value=value):
                fields = valid_fields()
                fields[field] = value
                errors = validator.validate(fields, strict=True)
                self.assertIn(
                    f"{field} must contain a positive finite numeric cap",
                    errors,
                )

    def test_rejects_unbounded_fallback_after_a_positive_cap(self) -> None:
        values = (
            "4 iterations; otherwise unlimited",
            "4 iterations; otherwise indefinitely",
            "4 iterations; no upper bound",
            "4 iterations; repeat as long as needed",
        )

        for value in values:
            with self.subTest(value=value):
                fields = valid_fields()
                fields["max iterations"] = value
                self.assertIn(
                    "max iterations must contain a finite numeric cap",
                    validator.validate(fields, strict=True),
                )

    def test_compound_budget_ignores_zero_for_an_unrelated_unit(self) -> None:
        fields = valid_fields()
        fields["budget"] = "0 retries, 20 tool calls"

        errors = validator.validate(fields, strict=True)

        self.assertFalse(any(error.startswith("budget must") for error in errors))

    def test_manager_workers_rejects_incidental_integration_word(self) -> None:
        fields = valid_fields()
        fields["topology"] = "manager-workers"
        fields["recovery"] = (
            "Retry failed worker output after integration test evidence is collected."
        )

        errors = validator.validate(fields, strict=True)

        self.assertIn(
            "manager-workers requires an explicit integration gate "
            "in recovery or permission boundary",
            errors,
        )

    def test_manager_workers_accepts_explicit_integration_gate(self) -> None:
        fields = valid_fields()
        fields["topology"] = "manager-workers"
        fields["recovery"] = (
            "Integration gate: the manager verifies the merged diff and tests "
            "before completion."
        )

        self.assertEqual(validator.validate(fields, strict=True), [])

    def test_existing_ci_repair_example_still_passes_cli(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(VALIDATOR_PATH),
                str(VALID_EXAMPLE),
                "--strict",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS loop contract", result.stdout)


if __name__ == "__main__":
    unittest.main()
