import ast
import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = EXPERIMENT_ROOT / "fixtures" / "architecture_tasks.json"
BENCHMARK_PATH = EXPERIMENT_ROOT / "benchmark.py"
ADMISSION_POLICY = {
    "minimum_independent_width": 2,
    "minimum_critical_path_payback_seconds": 0.05,
    "max_additional_review_load_units": 3,
}
sys.path.insert(0, str(EXPERIMENT_ROOT))

import benchmark  # noqa: E402


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ArchitectureExperimentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = benchmark.load_fixture(FIXTURE_PATH)

    def test_fixture_binds_declared_failure_to_the_only_failing_branch(self):
        invalid = copy.deepcopy(self.fixture)
        invalid["task_a"]["transient_failure_node"] = "sum"

        with self.assertRaisesRegex(ValueError, "transient_failure_node"):
            benchmark.validate_fixture(invalid)

    def test_fixture_requires_exactly_one_injected_failing_branch(self):
        for fail_attempts in (0, 1):
            invalid = copy.deepcopy(self.fixture)
            invalid["task_a"]["branches"][0]["fail_attempts"] = fail_attempts
            invalid["task_a"]["branches"][2]["fail_attempts"] = fail_attempts
            with self.subTest(fail_attempts=fail_attempts):
                with self.assertRaisesRegex(ValueError, "exactly one"):
                    benchmark.validate_fixture(invalid)

    def test_task_a_graph_is_concurrent_correct_and_recovers_node_locally(self):
        graph = benchmark.run_task_a_architecture(
            self.fixture["task_a"],
            self.fixture["budgets"],
            architecture="graph",
        )
        contract = graph["retry_recovery"]["contract"]

        self.assertTrue(graph["correctness"]["passed"])
        self.assertGreaterEqual(graph["observed_peak_concurrency"], 2)
        self.assertTrue(contract["passed"])
        self.assertTrue(contract["node_local_only"])
        self.assertTrue(contract["failing_node_attempts_match"])
        self.assertTrue(contract["all_unaffected_nodes_single_attempt"])
        self.assertEqual(graph["retry_recovery"]["attempts"]["checksum"], 2)
        self.assertEqual(graph["retry_recovery"]["replayed_nodes"], ["checksum"])

    def test_retry_exhaustion_stops_after_the_finite_attempt_cap(self):
        task = copy.deepcopy(self.fixture["task_a"])
        task["branches"][2]["fail_attempts"] = 2

        with self.assertRaises(benchmark.TransientNodeFailure):
            benchmark.run_task_a_architecture(
                task,
                self.fixture["budgets"],
                architecture="graph",
            )

    def test_retry_contract_rejects_incorrect_replay_of_unaffected_node(self):
        forged = {
            "attempts": {"checksum": 2, "sum": 2, "unique_sorted": 1},
            "retry_count": 2,
            "replayed_nodes": ["checksum", "sum"],
            "events": [
                {"node": "checksum", "failed_attempt": 1},
                {"node": "sum", "failed_attempt": 1},
            ],
        }

        contract = benchmark.evaluate_retry_contract(
            self.fixture["task_a"],
            forged,
        )

        self.assertFalse(contract["passed"])
        self.assertFalse(contract["node_local_only"])
        self.assertFalse(contract["all_unaffected_nodes_single_attempt"])

    def test_one_admission_function_selects_graph_for_task_a(self):
        decision = benchmark.decide_architecture(
            self.fixture["task_a"],
            self.fixture["budgets"],
            ADMISSION_POLICY,
            topology="static_diamond",
        )

        self.assertEqual(decision["selected"], "GRAPH")
        self.assertEqual(decision["metrics"]["independent_width"], 3)
        self.assertGreaterEqual(
            decision["metrics"]["estimated_critical_path_payback_seconds"],
            ADMISSION_POLICY["minimum_critical_path_payback_seconds"],
        )
        review = decision["metrics"]["review_load_proxy"]
        self.assertTrue(review["is_proxy"])
        self.assertLessEqual(
            review["additional_units"],
            ADMISSION_POLICY["max_additional_review_load_units"],
        )

    def test_task_a_positive_admission_executes_the_static_graph(self):
        receipt = benchmark.run_experiment(self.fixture, trials=1)

        self.assertEqual(receipt["task_a"]["admission_decision"]["selected"], "GRAPH")
        self.assertTrue(receipt["task_a"]["selected_architecture_executed"])
        self.assertEqual(receipt["task_a"]["graph_scheduler_invocations"], 1)

    def test_task_a_static_graph_has_lower_wall_time_than_serial_loop(self):
        loop = benchmark.run_task_a_architecture(
            self.fixture["task_a"],
            self.fixture["budgets"],
            architecture="loop",
        )
        graph = benchmark.run_task_a_architecture(
            self.fixture["task_a"],
            self.fixture["budgets"],
            architecture="graph",
        )

        self.assertTrue(loop["correctness"]["passed"])
        self.assertTrue(graph["correctness"]["passed"])
        self.assertLess(graph["wall_time_seconds"], loop["wall_time_seconds"])

    def test_same_admission_function_selects_loop_for_task_b(self):
        decision = benchmark.decide_architecture(
            self.fixture["task_b"],
            self.fixture["budgets"],
            ADMISSION_POLICY,
            topology="sequence",
        )

        self.assertEqual(decision["selected"], "LOOP")
        self.assertEqual(decision["metrics"]["independent_width"], 1)
        self.assertEqual(
            decision["metrics"]["estimated_critical_path_payback_seconds"],
            0.0,
        )
        self.assertIn("INSUFFICIENT_INDEPENDENT_WIDTH", decision["reason_codes"])
        self.assertIn("INSUFFICIENT_CRITICAL_PATH_PAYBACK", decision["reason_codes"])

    def test_task_b_rejection_skips_graph_scheduler(self):
        result = benchmark.run_task_b(
            self.fixture["task_b"],
            self.fixture["budgets"],
            policy=ADMISSION_POLICY,
        )

        self.assertEqual(result["admission_decision"]["selected"], "LOOP")
        self.assertTrue(result["correctness"]["passed"])
        self.assertTrue(result["orchestration_overhead"]["graph_execution_skipped"])
        self.assertEqual(
            result["orchestration_overhead"]["graph_scheduler_invocations"],
            0,
        )

    def test_task_b_verifies_every_expected_intermediate_output(self):
        result = benchmark.run_task_b(
            self.fixture["task_b"],
            self.fixture["budgets"],
            policy=ADMISSION_POLICY,
        )

        receipts = result["correctness"]["step_receipts"]
        self.assertEqual([item["expected_output"] for item in receipts], [12, 36, 32, 1024])
        self.assertTrue(all(item["verified"] for item in receipts))
        self.assertTrue(all(item["mismatch"] is None for item in receipts))

    def test_task_b_fails_on_an_intermediate_mismatch(self):
        task = copy.deepcopy(self.fixture["task_b"])
        task["steps"][1]["expected_output"] = 999

        with self.assertRaisesRegex(
            benchmark.IntermediateVerificationError,
            "multiply",
        ):
            benchmark.run_task_b(
                task,
                self.fixture["budgets"],
                policy=ADMISSION_POLICY,
            )

    def test_receipt_defers_promotion_to_independent_review(self):
        receipt = benchmark.run_experiment(self.fixture, trials=1)
        handoff = receipt["independent_review_handoff"]

        self.assertNotIn("promotion_decision", receipt)
        self.assertEqual(
            handoff["decision"],
            "DEFERRED_TO_INDEPENDENT_REVIEW",
        )
        self.assertEqual(handoff["agent_recommendation"], "NONE")
        self.assertTrue(handoff["evidence_gate_passed"])
        self.assertTrue(
            handoff["criteria"]["task_a_graph_node_local_only"],
        )
        self.assertTrue(
            handoff["criteria"]["task_a_failing_node_attempts_match"],
        )
        self.assertTrue(
            handoff["criteria"]["task_a_unaffected_nodes_single_attempt"],
        )

    def test_receipt_contains_fixture_and_implementation_sha256_provenance(self):
        receipt = benchmark.run_experiment(self.fixture, trials=1)

        self.assertEqual(
            receipt["provenance"]["fixture"]["sha256"],
            sha256(FIXTURE_PATH),
        )
        self.assertEqual(
            receipt["provenance"]["implementation"]["sha256"],
            sha256(BENCHMARK_PATH),
        )
        self.assertEqual(receipt["provenance"]["fixture"]["algorithm"], "sha256")
        self.assertEqual(
            receipt["provenance"]["implementation"]["algorithm"],
            "sha256",
        )

    def test_receipt_labels_review_load_and_side_effect_evidence_limits(self):
        receipt = benchmark.run_experiment(self.fixture, trials=1)

        self.assertTrue(receipt["task_a"]["review_load_proxy"]["is_proxy"])
        self.assertTrue(receipt["task_b"]["review_load_proxy"]["is_proxy"])
        boundary = receipt["external_side_effect_boundary"]
        self.assertFalse(boundary["runtime_instrumented"])
        self.assertEqual(boundary["method"], "DESIGN_AND_SOURCE_AUDIT")
        self.assertNotIn(
            "external_side_effects",
            receipt["budgets"]["observed"],
        )

    def test_total_deadline_is_checked_at_every_trial_and_task_boundary(self):
        receipt = benchmark.run_experiment(self.fixture, trials=1)

        self.assertEqual(
            receipt["budgets"]["total_deadline_boundaries_checked"],
            [
                "before_trial_1",
                "before_task_a_loop_trial_1",
                "after_task_a_loop_trial_1",
                "before_task_a_graph_trial_1",
                "after_task_a_graph_trial_1",
                "after_trial_1",
                "before_task_b",
                "after_task_b",
                "before_receipt",
            ],
        )

    def test_non_positive_or_unbounded_limits_are_rejected(self):
        invalid = copy.deepcopy(self.fixture)
        invalid["budgets"]["max_retries_per_node"] = -1

        with self.assertRaisesRegex(ValueError, "max_retries_per_node"):
            benchmark.validate_fixture(invalid)

    def test_declared_worst_case_work_must_fit_wall_time_budgets(self):
        invalid = copy.deepcopy(self.fixture)
        invalid["task_a"]["branches"][0]["work_seconds"] = 3.0

        with self.assertRaisesRegex(ValueError, "worst-case"):
            benchmark.validate_fixture(invalid)

    def test_benchmark_source_is_python_38_compatible(self):
        source = BENCHMARK_PATH.read_text(encoding="utf-8")

        ast.parse(source, filename=str(BENCHMARK_PATH), feature_version=(3, 8))
        self.assertNotIn(".is_relative_to(", source)
        self.assertNotIn("cancel_futures=", source)

    def test_receipt_writer_rejects_paths_outside_receipts_directory(self):
        receipt = benchmark.run_experiment(self.fixture, trials=1)
        outside = EXPERIMENT_ROOT.parent / "outside-receipt.json"

        with self.assertRaisesRegex(
            ValueError,
            "inside experiment receipts directory",
        ):
            benchmark.write_receipt(
                receipt,
                outside,
                experiment_root=EXPERIMENT_ROOT,
            )
        self.assertFalse(outside.exists())

        with self.assertRaisesRegex(
            ValueError,
            "inside experiment receipts directory",
        ):
            benchmark.write_receipt(
                receipt,
                EXPERIMENT_ROOT / "fixture-overwrite.json",
                experiment_root=EXPERIMENT_ROOT,
            )

    def test_receipt_writer_rejects_non_json_output(self):
        receipt = benchmark.run_experiment(self.fixture, trials=1)

        with self.assertRaisesRegex(ValueError, "JSON file"):
            benchmark.write_receipt(
                receipt,
                EXPERIMENT_ROOT / "receipts" / "receipt.txt",
                experiment_root=EXPERIMENT_ROOT,
            )

    def test_receipt_writer_emits_valid_json_inside_receipts_directory(self):
        receipt = benchmark.run_experiment(self.fixture, trials=1)

        with tempfile.TemporaryDirectory(
            dir=EXPERIMENT_ROOT / "receipts"
        ) as inside:
            output = Path(inside) / "receipt.json"
            benchmark.write_receipt(
                receipt,
                output,
                experiment_root=EXPERIMENT_ROOT,
            )
            observed = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(observed["experiment"]["id"], self.fixture["experiment_id"])
        self.assertEqual(
            observed["independent_review_handoff"],
            receipt["independent_review_handoff"],
        )


if __name__ == "__main__":
    unittest.main()
