from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = (
    ROOT
    / "skills"
    / "graph-engineering"
    / "scripts"
    / "validate_graph_contract.py"
)
VALID_EXAMPLE = (
    ROOT
    / "skills"
    / "graph-engineering"
    / "references"
    / "diamond-graph-example.json"
)

SPEC = importlib.util.spec_from_file_location("validate_graph_contract", VALIDATOR_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load validator: {VALIDATOR_PATH}")
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


def valid_contract() -> dict:
    return {
        "schema_version": "1.0",
        "graph_id": "bounded-diamond",
        "objective": "Process two independent branches and verify one join.",
        "non_goals": ["No external mutation.", "No dynamic expansion."],
        "owner": "integration-owner",
        "artifact_path": ".agent-state/graph/artifacts",
        "state_path": ".agent-state/graph/state.json",
        "entry_nodes": ["source"],
        "terminal_nodes": ["reduce"],
        "budgets": {
            "max_nodes": 4,
            "max_concurrency": 2,
            "max_attempts_per_node": 2,
            "wall_time_seconds": 300,
            "tool_calls": 20,
            "review_changed_lines": 500,
        },
        "permission_boundary": {
            "allowed": ["Read repository files.", "Write declared artifacts."],
            "denied": ["Production deployment.", "External publication."],
            "approval_required": [],
            "rollback": "Restore the last verified graph checkpoint.",
        },
        "nodes": [
            {
                "id": "source",
                "kind": "deterministic",
                "owner": "integration-owner",
                "inputs": [],
                "outputs": ["work_item"],
                "reads": ["input.json"],
                "writes": [],
                "verifier": "Input schema validation passes.",
                "timeout_seconds": 30,
                "max_attempts": 1,
                "tool_calls": 2,
                "effect_class": "read-only",
                "idempotency": "Pure read and parse.",
                "compensation": "",
            },
            {
                "id": "worker-a",
                "kind": "agent",
                "owner": "worker-a-owner",
                "inputs": ["work_item"],
                "outputs": ["candidate"],
                "reads": ["input.json"],
                "writes": [".agent-state/graph/artifacts/worker-a.json"],
                "verifier": "Candidate A schema and targeted check pass.",
                "timeout_seconds": 90,
                "max_attempts": 2,
                "tool_calls": 6,
                "effect_class": "reversible",
                "idempotency": "Overwrite the same isolated artifact atomically.",
                "compensation": "Restore the prior isolated artifact.",
            },
            {
                "id": "worker-b",
                "kind": "agent",
                "owner": "worker-b-owner",
                "inputs": ["work_item"],
                "outputs": ["candidate"],
                "reads": ["input.json"],
                "writes": [".agent-state/graph/artifacts/worker-b.json"],
                "verifier": "Candidate B schema and targeted check pass.",
                "timeout_seconds": 90,
                "max_attempts": 2,
                "tool_calls": 6,
                "effect_class": "reversible",
                "idempotency": "Overwrite the same isolated artifact atomically.",
                "compensation": "Restore the prior isolated artifact.",
            },
            {
                "id": "reduce",
                "kind": "deterministic",
                "owner": "integration-owner",
                "inputs": ["candidate"],
                "outputs": ["verified_result"],
                "reads": [
                    ".agent-state/graph/artifacts/worker-a.json",
                    ".agent-state/graph/artifacts/worker-b.json",
                ],
                "writes": [".agent-state/graph/artifacts/result.json"],
                "verifier": "Join inputs are complete and final result check passes.",
                "timeout_seconds": 60,
                "max_attempts": 1,
                "tool_calls": 4,
                "effect_class": "reversible",
                "idempotency": "Deterministic reduce into one atomic artifact.",
                "compensation": "Restore the prior verified result.",
            },
        ],
        "edges": [
            {
                "from": "source",
                "to": "worker-a",
                "type": "data",
                "payload_schema": "work_item",
                "condition": "always",
                "failure_route": "",
            },
            {
                "from": "source",
                "to": "worker-b",
                "type": "data",
                "payload_schema": "work_item",
                "condition": "always",
                "failure_route": "",
            },
            {
                "from": "worker-a",
                "to": "reduce",
                "type": "data",
                "payload_schema": "candidate",
                "condition": "verified",
                "failure_route": "",
            },
            {
                "from": "worker-b",
                "to": "reduce",
                "type": "data",
                "payload_schema": "candidate",
                "condition": "verified",
                "failure_route": "",
            },
        ],
        "joins": [
            {
                "id": "candidate-reduce",
                "target": "reduce",
                "mode": "reduce",
                "inputs": ["worker-a", "worker-b"],
                "verifier": "Both candidate receipts are fresh and schema-valid.",
                "quorum": None,
            }
        ],
        "stop_conditions": [
            "The terminal verifier passes.",
            "Any graph or node budget is exhausted.",
            "The same failure signature repeats twice.",
        ],
        "recovery": {
            "checkpoint": ".agent-state/graph/checkpoint.json",
            "write_back": ".agent-state/graph/events.jsonl",
            "whole_graph_rerun": False,
        },
    }


def approved_external_contract() -> dict:
    contract = valid_contract()
    source = contract["nodes"][0]
    external = contract["nodes"][1]
    write_target = external["writes"][0]

    source["kind"] = "human-gate"
    source["outputs"].append("approval_receipt")
    source["verifier"] = "Fresh human approval receipt is valid for worker-a."
    external["inputs"] = ["approval_receipt"]
    external["effect_class"] = "external"
    external["outputs"].append("compensation_receipt")
    external["compensation"] = "Restore the prior isolated artifact."
    contract["edges"][0]["payload_schema"] = "approval_receipt"
    contract["edges"].append(
        {
            "from": "worker-a",
            "to": "reduce",
            "type": "compensation",
            "payload_schema": "compensation_receipt",
            "condition": "external effect requires compensation",
            "failure_route": "",
        }
    )
    contract["permission_boundary"]["allowed"].append(write_target)
    contract["permission_boundary"]["approval_required"] = ["worker-a"]
    return contract


class GraphContractValidatorTest(unittest.TestCase):
    def validate(self, contract: dict, *, strict: bool = True) -> list[str]:
        return validator.validate(contract, strict=strict)

    def write_contract(self, contract: dict, directory: str) -> Path:
        path = Path(directory) / "graph.json"
        path.write_text(json.dumps(contract), encoding="utf-8")
        return path

    def test_valid_example_passes_strict_cli(self) -> None:
        result = subprocess.run(
            [sys.executable, str(VALIDATOR_PATH), str(VALID_EXAMPLE), "--strict"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS graph contract", result.stdout)

    def test_dangling_edge_is_rejected(self) -> None:
        contract = valid_contract()
        contract["edges"][0]["to"] = "missing-node"
        self.assertIn(
            "edge references unknown node: source -> missing-node",
            self.validate(contract),
        )

    def test_incompatible_data_schema_is_rejected(self) -> None:
        contract = valid_contract()
        contract["edges"][0]["payload_schema"] = "unknown_schema"
        errors = self.validate(contract)
        self.assertIn(
            "data edge schema unknown_schema is not declared by source.outputs",
            errors,
        )
        self.assertIn(
            "data edge schema unknown_schema is not declared by worker-a.inputs",
            errors,
        )

    def test_cycle_and_feedback_edge_are_rejected(self) -> None:
        contract = valid_contract()
        contract["edges"].append(
            {
                "from": "reduce",
                "to": "source",
                "type": "feedback",
                "payload_schema": "verified_result",
                "condition": "retry",
                "failure_route": "",
            }
        )
        errors = self.validate(contract)
        self.assertIn("unsupported edge type: feedback", errors)
        self.assertIn("static graph must be acyclic", errors)

    def test_failure_route_participates_in_cycle_detection(self) -> None:
        contract = valid_contract()
        contract["edges"][2]["failure_route"] = "source"

        self.assertIn("static graph must be acyclic", self.validate(contract))

    def test_conflicting_writers_are_rejected(self) -> None:
        contract = valid_contract()
        contract["nodes"][2]["writes"] = copy.deepcopy(
            contract["nodes"][1]["writes"]
        )
        self.assertIn(
            "write target has multiple owners: "
            ".agent-state/graph/artifacts/worker-a.json",
            self.validate(contract),
        )

    def test_multi_input_target_requires_explicit_join(self) -> None:
        contract = valid_contract()
        contract["joins"] = []
        self.assertIn(
            "node reduce has multiple incoming dependencies but no join contract",
            self.validate(contract),
        )

    def test_unreachable_node_is_rejected(self) -> None:
        contract = valid_contract()
        contract["nodes"].append(
            {
                **copy.deepcopy(contract["nodes"][1]),
                "id": "orphan",
                "owner": "orphan-owner",
                "writes": [".agent-state/graph/artifacts/orphan.json"],
            }
        )
        contract["budgets"]["max_nodes"] = 5
        self.assertIn("unreachable node: orphan", self.validate(contract))

    def test_non_positive_and_oversized_budgets_are_rejected(self) -> None:
        for field, value in (
            ("max_nodes", 0),
            ("max_concurrency", -1),
            ("max_attempts_per_node", 0),
            ("wall_time_seconds", 0),
            ("tool_calls", -2),
            ("review_changed_lines", 1001),
        ):
            with self.subTest(field=field):
                contract = valid_contract()
                contract["budgets"][field] = value
                self.assertTrue(
                    any(field in error for error in self.validate(contract)),
                    field,
                )

    def test_required_control_lists_must_not_be_empty(self) -> None:
        for field in ("non_goals", "stop_conditions"):
            with self.subTest(field=field):
                contract = valid_contract()
                contract[field] = []
                self.assertTrue(
                    any(field in error for error in self.validate(contract)),
                    field,
                )

    def test_static_concurrency_cannot_exceed_declared_nodes(self) -> None:
        contract = valid_contract()
        contract["budgets"]["max_nodes"] = 8
        contract["budgets"]["max_concurrency"] = 5
        self.assertIn(
            "max_concurrency cannot exceed declared node count",
            self.validate(contract),
        )

    def test_external_effect_requires_approval_compensation_and_route(self) -> None:
        contract = valid_contract()
        node = contract["nodes"][1]
        node["effect_class"] = "external"
        node["compensation"] = ""
        errors = self.validate(contract)
        self.assertIn(
            "external node worker-a requires an approval boundary",
            errors,
        )
        self.assertIn(
            "external node worker-a requires compensation",
            errors,
        )
        self.assertIn(
            "external node worker-a requires a compensation edge",
            errors,
        )

    def test_external_effect_rejects_unbound_approval_text_and_missing_gate(self) -> None:
        contract = valid_contract()
        node = contract["nodes"][1]
        node["effect_class"] = "external"
        node["compensation"] = "Restore the prior isolated artifact."
        contract["permission_boundary"]["allowed"].append(node["writes"][0])
        contract["permission_boundary"]["approval_required"] = [
            "An operator approves release."
        ]
        contract["edges"].append(
            {
                "from": "worker-a",
                "to": "reduce",
                "type": "compensation",
                "payload_schema": "candidate",
                "condition": "compensate",
                "failure_route": "",
            }
        )

        errors = self.validate(contract)

        self.assertIn(
            "external node worker-a must be named in approval_required",
            errors,
        )
        self.assertIn(
            "external node worker-a requires a direct human-gate approval receipt",
            errors,
        )

    def test_external_effect_with_bound_gate_and_permission_scope_passes(self) -> None:
        self.assertEqual(self.validate(approved_external_contract()), [])

    def test_external_effect_cannot_write_an_explicitly_denied_scope(self) -> None:
        contract = approved_external_contract()
        write_target = contract["nodes"][1]["writes"][0]
        contract["permission_boundary"]["denied"].append(write_target)

        self.assertIn(
            "external node worker-a write target is denied: %s" % write_target,
            self.validate(contract),
        )

    def test_whole_graph_rerun_is_rejected_in_strict_mode(self) -> None:
        contract = valid_contract()
        contract["recovery"]["whole_graph_rerun"] = True
        self.assertIn(
            "strict static graphs must recover the smallest failed unit",
            self.validate(contract),
        )

    def test_invalid_quorum_join_is_rejected(self) -> None:
        contract = valid_contract()
        contract["joins"][0]["mode"] = "quorum"
        contract["joins"][0]["quorum"] = 3
        self.assertIn(
            "join candidate-reduce quorum must be between 1 and 2",
            self.validate(contract),
        )

    def test_duplicate_join_ids_and_empty_edge_conditions_are_rejected(self) -> None:
        contract = valid_contract()
        duplicate = copy.deepcopy(contract["joins"][0])
        duplicate["target"] = "worker-a"
        duplicate["inputs"] = ["source", "worker-b"]
        contract["joins"].append(duplicate)
        contract["edges"][0]["condition"] = ""
        errors = self.validate(contract)
        self.assertIn("duplicate join id: candidate-reduce", errors)
        self.assertIn("edge[0] condition must be non-empty", errors)


if __name__ == "__main__":
    unittest.main()
