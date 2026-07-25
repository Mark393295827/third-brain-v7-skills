#!/usr/bin/env python3
"""Bounded local verification of two static Loop-vs-Graph fixtures."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import platform
import statistics
import threading
import time
from concurrent.futures import ThreadPoolExecutor, wait
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


EXPERIMENT_ROOT = Path(__file__).resolve().parent
DEFAULT_FIXTURE = EXPERIMENT_ROOT / "fixtures" / "architecture_tasks.json"
DEFAULT_RECEIPT = EXPERIMENT_ROOT / "receipts" / "loop-vs-graph-receipt.json"
SUPPORTED_BRANCH_OPERATIONS = {"sum", "unique_sorted", "checksum"}
SUPPORTED_SEQUENCE_OPERATIONS = {"add", "multiply", "subtract", "square"}


class BudgetExceeded(RuntimeError):
    """Raised when a declared finite time budget is exhausted."""


class TransientNodeFailure(RuntimeError):
    """Injected retryable failure used by the static-diamond fixture."""


class IntermediateVerificationError(RuntimeError):
    """Raised when a dependency-chain step differs from its expected output."""


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _semantic_fixture_hash(fixture: Dict[str, Any]) -> str:
    payload = {
        key: value for key, value in fixture.items() if not key.startswith("_fixture_")
    }
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _positive_number(value: Any, field: str, allow_zero: bool = False) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("%s must be a finite number" % field)
    if not math.isfinite(value):
        raise ValueError("%s must be finite" % field)
    if allow_zero and value < 0:
        raise ValueError("%s must be greater than or equal to zero" % field)
    if not allow_zero and value <= 0:
        raise ValueError("%s must be greater than zero" % field)


def _require_integer(value: Any, field: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("%s must be an integer" % field)


def validate_fixture(fixture: Dict[str, Any]) -> None:
    """Validate finite budgets and the exact two-fixture experiment contract."""
    budgets = fixture.get("budgets")
    if not isinstance(budgets, dict):
        raise ValueError("budgets must be an object")

    for field in (
        "max_total_wall_time_seconds",
        "max_task_wall_time_seconds",
        "max_concurrency",
        "max_nodes",
        "max_review_load_units",
        "trials",
    ):
        _positive_number(budgets.get(field), field)
    for field in ("max_retries_per_node", "external_side_effect_limit"):
        _positive_number(budgets.get(field), field, allow_zero=True)
    for field in (
        "max_retries_per_node",
        "max_concurrency",
        "max_nodes",
        "max_review_load_units",
        "external_side_effect_limit",
        "trials",
    ):
        _require_integer(budgets[field], field)
    if budgets["external_side_effect_limit"] != 0:
        raise ValueError("external_side_effect_limit must be zero")

    policy = fixture.get("admission_policy")
    if not isinstance(policy, dict):
        raise ValueError("admission_policy must be an object")
    _positive_number(
        policy.get("minimum_independent_width"),
        "minimum_independent_width",
    )
    _positive_number(
        policy.get("minimum_critical_path_payback_seconds"),
        "minimum_critical_path_payback_seconds",
    )
    _positive_number(
        policy.get("max_additional_review_load_units"),
        "max_additional_review_load_units",
        allow_zero=True,
    )
    _require_integer(
        policy["minimum_independent_width"],
        "minimum_independent_width",
    )
    _require_integer(
        policy["max_additional_review_load_units"],
        "max_additional_review_load_units",
    )

    task_a = fixture.get("task_a")
    if not isinstance(task_a, dict) or not isinstance(task_a.get("branches"), list):
        raise ValueError("task_a.branches must be a list")
    branches = task_a["branches"]
    if not branches:
        raise ValueError("task_a.branches must not be empty")
    if len(branches) + 2 > budgets["max_nodes"]:
        raise ValueError("task_a static diamond exceeds max_nodes")
    if budgets["max_concurrency"] < len(branches):
        raise ValueError(
            "task_a requires max_concurrency for every static diamond branch"
        )

    branch_ids = [branch.get("id") for branch in branches]
    if any(not isinstance(node_id, str) or not node_id for node_id in branch_ids):
        raise ValueError("every task_a branch needs a non-empty id")
    if len(branch_ids) != len(set(branch_ids)):
        raise ValueError("task_a branch ids must be unique")
    if set(task_a.get("expected", {})) != set(branch_ids):
        raise ValueError("task_a.expected keys must match branch ids")

    for branch in branches:
        node_id = branch["id"]
        if branch.get("operation") not in SUPPORTED_BRANCH_OPERATIONS:
            raise ValueError("unsupported task_a operation: %s" % branch.get("operation"))
        _positive_number(branch.get("work_seconds"), "%s.work_seconds" % node_id)
        fail_attempts = branch.get("fail_attempts")
        _require_integer(fail_attempts, "%s.fail_attempts" % node_id)
        if fail_attempts < 0:
            raise ValueError("%s.fail_attempts must not be negative" % node_id)
        if fail_attempts > budgets["max_retries_per_node"]:
            raise ValueError(
                "%s.fail_attempts exceeds max_retries_per_node" % node_id
            )

    failing_branches = [
        branch for branch in branches if branch["fail_attempts"] > 0
    ]
    if len(failing_branches) != 1:
        raise ValueError("task_a requires exactly one injected failing branch")
    failing_node = failing_branches[0]["id"]
    if task_a.get("transient_failure_node") != failing_node:
        raise ValueError(
            "task_a.transient_failure_node must match the exactly one failing branch"
        )

    task_b = fixture.get("task_b")
    if not isinstance(task_b, dict) or not isinstance(task_b.get("steps"), list):
        raise ValueError("task_b.steps must be a list")
    steps = task_b["steps"]
    if not steps:
        raise ValueError("task_b.steps must not be empty")
    step_ids = [step.get("id") for step in steps]
    if len(step_ids) != len(set(step_ids)):
        raise ValueError("task_b step ids must be unique")

    seen = set()  # type: Set[str]
    for index, step in enumerate(steps):
        node_id = step.get("id")
        if not isinstance(node_id, str) or not node_id:
            raise ValueError("every task_b step needs a non-empty id")
        if step.get("operation") not in SUPPORTED_SEQUENCE_OPERATIONS:
            raise ValueError("unsupported task_b operation: %s" % step.get("operation"))
        _positive_number(step.get("work_seconds"), "%s.work_seconds" % node_id)
        if "expected_output" not in step:
            raise ValueError("%s.expected_output is required" % node_id)
        dependencies = step.get("depends_on")
        if not isinstance(dependencies, list):
            raise ValueError("%s.depends_on must be a list" % node_id)
        if any(dependency not in seen for dependency in dependencies):
            raise ValueError("%s has a dangling or forward dependency" % node_id)
        if index > 0 and step_ids[index - 1] not in dependencies:
            raise ValueError("task_b must remain dependency-heavy and sequential")
        seen.add(node_id)
    if steps[-1]["expected_output"] != task_b.get("expected"):
        raise ValueError("task_b final expected output must match the last step")

    branch_work = [
        branch["work_seconds"] * (branch["fail_attempts"] + 1)
        for branch in branches
    ]
    loop_worst_case = sum(branch_work)
    graph_worst_case = max(branch_work)
    sequence_worst_case = sum(step["work_seconds"] for step in steps)
    if max(loop_worst_case, graph_worst_case, sequence_worst_case) >= budgets[
        "max_task_wall_time_seconds"
    ]:
        raise ValueError("declared worst-case workload must fit the task time budget")
    total_worst_case = budgets["trials"] * (
        loop_worst_case + graph_worst_case
    ) + sequence_worst_case
    if total_worst_case >= budgets["max_total_wall_time_seconds"]:
        raise ValueError(
            "declared worst-case benchmark must fit the total time budget"
        )


def load_fixture(path: Path) -> Dict[str, Any]:
    fixture = json.loads(path.read_text(encoding="utf-8"))
    validate_fixture(fixture)
    fixture["_fixture_source"] = {
        "absolute_path": str(path.resolve()),
        "sha256": _sha256_file(path),
        "semantic_sha256": _semantic_fixture_hash(fixture),
    }
    return fixture


def _fixture_provenance(fixture: Dict[str, Any]) -> Dict[str, str]:
    source = fixture.get("_fixture_source")
    if not isinstance(source, dict):
        raise ValueError("fixture provenance is absent; load it with load_fixture")
    source_path = Path(source["absolute_path"])
    current_file_hash = _sha256_file(source_path)
    if current_file_hash != source["sha256"]:
        raise ValueError("fixture file changed after load")
    if _semantic_fixture_hash(fixture) != source["semantic_sha256"]:
        raise ValueError("in-memory fixture differs from its loaded source")
    try:
        relative_path = source_path.resolve().relative_to(EXPERIMENT_ROOT.resolve())
        display_path = str(relative_path).replace("\\", "/")
    except ValueError:
        display_path = source_path.name
    return {
        "algorithm": "sha256",
        "path": display_path,
        "sha256": current_file_hash,
    }


def _canonical_checksum(values: List[int]) -> str:
    payload = json.dumps(values, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _run_branch_operation(operation: str, values: List[int]) -> Any:
    if operation == "sum":
        return sum(values)
    if operation == "unique_sorted":
        return sorted(set(values))
    if operation == "checksum":
        return _canonical_checksum(values)
    raise ValueError("unsupported branch operation: %s" % operation)


def _check_deadline(deadline: float, scope: str, budget_name: str) -> None:
    if time.perf_counter() >= deadline:
        raise BudgetExceeded("%s exceeded %s" % (scope, budget_name))


def _check_total_deadline(
    deadline: float,
    boundary: str,
    checked_boundaries: List[str],
) -> None:
    checked_boundaries.append(boundary)
    _check_deadline(deadline, boundary, "max_total_wall_time_seconds")


def _run_branch_with_retry(
    branch: Dict[str, Any],
    values: List[int],
    max_retries: int,
    deadline: float,
    attempts: Dict[str, int],
    retry_events: List[Dict[str, Any]],
    shared_lock: threading.Lock,
    activity: Dict[str, int],
    start_barrier: Optional[threading.Barrier] = None,
) -> Tuple[str, Any]:
    node_id = branch["id"]
    allowed_attempts = max_retries + 1

    while True:
        _check_deadline(deadline, node_id, "max_task_wall_time_seconds")
        with shared_lock:
            attempts[node_id] = attempts.get(node_id, 0) + 1
            attempt = attempts[node_id]
            activity["active"] += 1
            activity["peak"] = max(activity["peak"], activity["active"])

        try:
            if attempt == 1 and start_barrier is not None:
                remaining = max(0.0, deadline - time.perf_counter())
                try:
                    start_barrier.wait(timeout=remaining)
                except threading.BrokenBarrierError:
                    raise BudgetExceeded(
                        "%s could not enter the bounded concurrency barrier"
                        % node_id
                    )
            time.sleep(branch["work_seconds"])
            result = _run_branch_operation(branch["operation"], values)
            if attempt <= branch["fail_attempts"]:
                raise TransientNodeFailure(
                    "injected transient failure at %s attempt %s"
                    % (node_id, attempt)
                )
            _check_deadline(deadline, node_id, "max_task_wall_time_seconds")
            return node_id, result
        except TransientNodeFailure as error:
            with shared_lock:
                retry_events.append(
                    {
                        "node": node_id,
                        "failed_attempt": attempt,
                        "signature": "INJECTED_TRANSIENT_FAILURE",
                        "diagnosis": str(error),
                        "next_action": "RETRY_NODE_LOCALLY",
                    }
                )
            if attempt >= allowed_attempts:
                raise
        finally:
            with shared_lock:
                activity["active"] -= 1


def _correctness_receipt(
    observed: Dict[str, Any],
    expected: Dict[str, Any],
) -> Dict[str, Any]:
    mismatches = {
        key: {"expected": expected.get(key), "observed": observed.get(key)}
        for key in sorted(set(expected) | set(observed))
        if expected.get(key) != observed.get(key)
    }
    return {
        "passed": not mismatches,
        "verifier": "exact deterministic equality at the static-diamond join",
        "expected": expected,
        "observed": observed,
        "mismatches": mismatches,
    }


def _task_a_review_proxy(task: Dict[str, Any]) -> Dict[str, Any]:
    branch_count = len(task["branches"])
    retry_count = sum(branch["fail_attempts"] for branch in task["branches"])
    loop_units = branch_count + retry_count + 1 + 1
    graph_units = branch_count + retry_count + 1 + branch_count + 1
    return {
        "is_proxy": True,
        "not_measured_human_review": True,
        "unit_definition": (
            "one proxy unit per branch artifact, retry diagnosis, join check, "
            "and architecture-control check"
        ),
        "loop_units": loop_units,
        "graph_units": graph_units,
        "additional_units": graph_units - loop_units,
    }


def _task_b_review_proxy(task: Dict[str, Any]) -> Dict[str, Any]:
    step_count = len(task["steps"])
    edge_count = sum(len(step["depends_on"]) for step in task["steps"])
    loop_units = step_count + 1 + 1
    graph_units = loop_units + edge_count
    return {
        "is_proxy": True,
        "not_measured_human_review": True,
        "unit_definition": (
            "one proxy unit per step check, final check, admission check, "
            "and graph edge contract"
        ),
        "loop_units": loop_units,
        "graph_units": graph_units,
        "additional_units": graph_units - loop_units,
    }


def _sequence_topology_metrics(
    task: Dict[str, Any],
) -> Tuple[int, float, float]:
    levels = {}  # type: Dict[str, int]
    longest_paths = {}  # type: Dict[str, float]
    widths = {}  # type: Dict[int, int]
    serial_seconds = 0.0

    for step in task["steps"]:
        dependencies = step["depends_on"]
        duration = step["work_seconds"]
        serial_seconds += duration
        level = (
            0
            if not dependencies
            else 1 + max(levels[dependency] for dependency in dependencies)
        )
        levels[step["id"]] = level
        widths[level] = widths.get(level, 0) + 1
        longest_paths[step["id"]] = duration + (
            0.0
            if not dependencies
            else max(longest_paths[dependency] for dependency in dependencies)
        )

    return max(widths.values()), serial_seconds, max(longest_paths.values())


def decide_architecture(
    task: Dict[str, Any],
    budgets: Dict[str, Any],
    policy: Dict[str, Any],
    topology: str,
) -> Dict[str, Any]:
    """Apply one bounded admission gate to either static fixture topology."""
    started = time.perf_counter()
    if topology == "static_diamond":
        durations = [
            branch["work_seconds"] * (branch["fail_attempts"] + 1)
            for branch in task["branches"]
        ]
        independent_width = min(len(durations), budgets["max_concurrency"])
        sequential_seconds = sum(durations)
        graph_critical_path_seconds = max(durations)
        review_proxy = _task_a_review_proxy(task)
    elif topology == "sequence":
        (
            independent_width,
            sequential_seconds,
            graph_critical_path_seconds,
        ) = _sequence_topology_metrics(task)
        review_proxy = _task_b_review_proxy(task)
    else:
        raise ValueError("unsupported topology: %s" % topology)

    payback_seconds = max(0.0, sequential_seconds - graph_critical_path_seconds)
    reason_codes = []  # type: List[str]
    if independent_width < policy["minimum_independent_width"]:
        reason_codes.append("INSUFFICIENT_INDEPENDENT_WIDTH")
    if payback_seconds < policy["minimum_critical_path_payback_seconds"]:
        reason_codes.append("INSUFFICIENT_CRITICAL_PATH_PAYBACK")
    if (
        review_proxy["additional_units"]
        > policy["max_additional_review_load_units"]
    ):
        reason_codes.append("ADDITIONAL_REVIEW_PROXY_EXCEEDS_BOUND")

    return {
        "selected": "LOOP" if reason_codes else "GRAPH",
        "topology": topology,
        "reason_codes": reason_codes or ["STATIC_FIXTURE_GATE_PASSED"],
        "metrics": {
            "independent_width": independent_width,
            "estimated_sequential_seconds": round(sequential_seconds, 6),
            "estimated_graph_critical_path_seconds": round(
                graph_critical_path_seconds,
                6,
            ),
            "estimated_critical_path_payback_seconds": round(
                payback_seconds,
                6,
            ),
            "review_load_proxy": review_proxy,
        },
        "thresholds": policy,
        "claim_scope": "only the declared static fixture",
        "gate_wall_time_seconds": round(time.perf_counter() - started, 6),
    }


def evaluate_retry_contract(
    task: Dict[str, Any],
    recovery: Dict[str, Any],
) -> Dict[str, Any]:
    """Verify that only the declared transient node was replayed."""
    failing = [
        branch for branch in task["branches"] if branch["fail_attempts"] > 0
    ]
    if len(failing) != 1:
        return {
            "passed": False,
            "node_local_only": False,
            "failing_node_attempts_match": False,
            "all_unaffected_nodes_single_attempt": False,
            "retry_count_matches": False,
            "reason": "task does not declare exactly one failing branch",
        }

    failing_branch = failing[0]
    failing_node = failing_branch["id"]
    expected_attempts = {
        branch["id"]: 1 + branch["fail_attempts"] for branch in task["branches"]
    }
    actual_attempts = recovery.get("attempts", {})
    replayed_nodes = sorted(recovery.get("replayed_nodes", []))
    events = recovery.get("events", [])

    node_local_only = (
        replayed_nodes == [failing_node]
        and len(events) == failing_branch["fail_attempts"]
        and all(event.get("node") == failing_node for event in events)
    )
    failing_node_attempts_match = (
        actual_attempts.get(failing_node) == expected_attempts[failing_node]
    )
    all_unaffected_nodes_single_attempt = all(
        actual_attempts.get(branch["id"]) == 1
        for branch in task["branches"]
        if branch["id"] != failing_node
    )
    retry_count_matches = (
        recovery.get("retry_count") == failing_branch["fail_attempts"]
    )
    passed = all(
        (
            node_local_only,
            failing_node_attempts_match,
            all_unaffected_nodes_single_attempt,
            retry_count_matches,
        )
    )
    return {
        "passed": passed,
        "node_local_only": node_local_only,
        "failing_node_attempts_match": failing_node_attempts_match,
        "all_unaffected_nodes_single_attempt": all_unaffected_nodes_single_attempt,
        "retry_count_matches": retry_count_matches,
        "failing_node": failing_node,
        "expected_attempts": expected_attempts,
        "actual_attempts": actual_attempts,
    }


def run_task_a_architecture(
    task: Dict[str, Any],
    budgets: Dict[str, Any],
    architecture: str,
) -> Dict[str, Any]:
    """Run one serial Loop baseline or one concurrent static-Graph trial."""
    architecture = architecture.lower()
    if architecture not in {"loop", "graph"}:
        raise ValueError("architecture must be 'loop' or 'graph'")

    started = time.perf_counter()
    deadline = started + budgets["max_task_wall_time_seconds"]
    attempts = {}  # type: Dict[str, int]
    retry_events = []  # type: List[Dict[str, Any]]
    results = {}  # type: Dict[str, Any]
    shared_lock = threading.Lock()
    activity = {"active": 0, "peak": 0}
    overhead = {
        "scheduler_setup_seconds": 0.0,
        "dispatch_seconds": 0.0,
        "result_collection_seconds": 0.0,
        "scheduler_cleanup_seconds": 0.0,
    }

    if architecture == "loop":
        for branch in task["branches"]:
            check_started = time.perf_counter()
            _check_deadline(
                deadline,
                task["id"],
                "max_task_wall_time_seconds",
            )
            overhead["dispatch_seconds"] += time.perf_counter() - check_started
            node_id, value = _run_branch_with_retry(
                branch,
                task["input"],
                budgets["max_retries_per_node"],
                deadline,
                attempts,
                retry_events,
                shared_lock,
                activity,
                None,
            )
            collect_started = time.perf_counter()
            results[node_id] = value
            overhead["result_collection_seconds"] += (
                time.perf_counter() - collect_started
            )
    else:
        setup_started = time.perf_counter()
        executor = ThreadPoolExecutor(
            max_workers=min(budgets["max_concurrency"], len(task["branches"])),
            thread_name_prefix="graph-node",
        )
        overhead["scheduler_setup_seconds"] = time.perf_counter() - setup_started
        futures = {}
        start_barrier = threading.Barrier(len(task["branches"]))
        try:
            dispatch_started = time.perf_counter()
            for branch in task["branches"]:
                future = executor.submit(
                    _run_branch_with_retry,
                    branch,
                    task["input"],
                    budgets["max_retries_per_node"],
                    deadline,
                    attempts,
                    retry_events,
                    shared_lock,
                    activity,
                    start_barrier,
                )
                futures[future] = branch["id"]
            overhead["dispatch_seconds"] = time.perf_counter() - dispatch_started

            remaining = max(0.0, deadline - time.perf_counter())
            done, not_done = wait(futures, timeout=remaining)
            if not_done:
                for future in not_done:
                    future.cancel()
                raise BudgetExceeded(
                    "%s exceeded max_task_wall_time_seconds" % task["id"]
                )

            collect_started = time.perf_counter()
            completed = {future: future.result() for future in done}
            future_by_node = {
                node_id: future for future, node_id in futures.items()
            }
            for branch in task["branches"]:
                node_id, value = completed[future_by_node[branch["id"]]]
                results[node_id] = value
            overhead["result_collection_seconds"] = (
                time.perf_counter() - collect_started
            )
        finally:
            cleanup_started = time.perf_counter()
            executor.shutdown(wait=True)
            overhead["scheduler_cleanup_seconds"] = (
                time.perf_counter() - cleanup_started
            )

    wall_time = time.perf_counter() - started
    if wall_time > budgets["max_task_wall_time_seconds"]:
        raise BudgetExceeded(
            "%s exceeded max_task_wall_time_seconds" % task["id"]
        )

    retry_events.sort(key=lambda event: (event["node"], event["failed_attempt"]))
    replayed_nodes = sorted({event["node"] for event in retry_events})
    correctness = _correctness_receipt(results, task["expected"])
    recovery = {
        "injected_failure_node": task["transient_failure_node"],
        "retry_count": len(retry_events),
        "attempts": {key: attempts[key] for key in sorted(attempts)},
        "replayed_nodes": replayed_nodes,
        "events": retry_events,
    }
    recovery["contract"] = evaluate_retry_contract(task, recovery)
    recovery["recovered"] = (
        correctness["passed"] and recovery["contract"]["passed"]
    )

    review_proxy = _task_a_review_proxy(task)
    review_proxy = dict(review_proxy)
    review_proxy["units"] = review_proxy[
        "loop_units" if architecture == "loop" else "graph_units"
    ]
    measured_overhead = sum(overhead.values())
    return {
        "architecture": architecture.upper(),
        "correctness": correctness,
        "wall_time_seconds": round(wall_time, 6),
        "retry_recovery": recovery,
        "review_load_proxy": review_proxy,
        "orchestration_overhead": {
            **{key: round(value, 6) for key, value in overhead.items()},
            "measured_seconds": round(measured_overhead, 6),
            "operation_proxy": 1
            if architecture == "loop"
            else len(task["branches"]) + 1,
            "definition": (
                "scheduler setup, dispatch, result collection, and cleanup; "
                "worker wait time is excluded"
            ),
        },
        "observed_peak_concurrency": activity["peak"],
        "budget_status": {
            "within_task_time_limit": True,
            "within_retry_limit": max(attempts.values()) - 1
            <= budgets["max_retries_per_node"],
            "within_concurrency_limit": activity["peak"]
            <= budgets["max_concurrency"],
            "within_review_proxy_limit": review_proxy["units"]
            <= budgets["max_review_load_units"],
        },
    }


def _run_sequence_operation(step: Dict[str, Any], value: int) -> int:
    operation = step["operation"]
    if operation == "add":
        return value + step["operand"]
    if operation == "multiply":
        return value * step["operand"]
    if operation == "subtract":
        return value - step["operand"]
    if operation == "square":
        return value * value
    raise ValueError("unsupported sequence operation: %s" % operation)


def run_task_b(
    task: Dict[str, Any],
    budgets: Dict[str, Any],
    policy: Dict[str, Any],
) -> Dict[str, Any]:
    """Reject the static dependency chain to Loop and verify every step."""
    started = time.perf_counter()
    deadline = started + budgets["max_task_wall_time_seconds"]
    decision = decide_architecture(
        task,
        budgets,
        policy,
        topology="sequence",
    )
    if decision["selected"] != "LOOP":
        raise RuntimeError("task_b fixture must be rejected to Loop")

    value = task["initial_value"]
    step_receipts = []  # type: List[Dict[str, Any]]
    for step in task["steps"]:
        _check_deadline(
            deadline,
            task["id"],
            "max_task_wall_time_seconds",
        )
        before = value
        time.sleep(step["work_seconds"])
        value = _run_sequence_operation(step, value)
        expected_output = step["expected_output"]
        verified = value == expected_output
        mismatch = (
            None
            if verified
            else {"expected": expected_output, "observed": value}
        )
        step_receipt = {
            "node": step["id"],
            "input": before,
            "output": value,
            "expected_output": expected_output,
            "verified": verified,
            "mismatch": mismatch,
        }
        step_receipts.append(step_receipt)
        if not verified:
            raise IntermediateVerificationError(
                "intermediate verification failed at %s: expected %s, observed %s"
                % (step["id"], expected_output, value)
            )
        _check_deadline(
            deadline,
            task["id"],
            "max_task_wall_time_seconds",
        )

    wall_time = time.perf_counter() - started
    if wall_time > budgets["max_task_wall_time_seconds"]:
        raise BudgetExceeded(
            "%s exceeded max_task_wall_time_seconds" % task["id"]
        )

    correctness = (
        all(receipt["verified"] for receipt in step_receipts)
        and value == task["expected"]
    )
    review_proxy = dict(decision["metrics"]["review_load_proxy"])
    review_proxy["units"] = review_proxy["loop_units"]
    return {
        "admission_decision": decision,
        "correctness": {
            "passed": correctness,
            "verifier": "exact equality at every declared intermediate and final output",
            "expected": task["expected"],
            "observed": value,
            "step_receipts": step_receipts,
        },
        "measured_wall_time_seconds": round(wall_time, 6),
        "retry_recovery": {
            "retry_count": 0,
            "recovered": False,
            "reason": "no failure is injected into Task B",
        },
        "review_load_proxy": review_proxy,
        "orchestration_overhead": {
            "admission_gate_seconds": decision["gate_wall_time_seconds"],
            "graph_scheduler_invocations": 0,
            "graph_execution_skipped": True,
            "avoided_graph_operation_proxy": len(task["steps"]) + 1,
        },
        "budget_status": {
            "within_task_time_limit": True,
            "within_review_proxy_limit": review_proxy["units"]
            <= budgets["max_review_load_units"],
        },
    }


def _median(values: List[float]) -> float:
    return round(statistics.median(values), 6)


def _source_capability_audit(path: Path) -> Dict[str, Any]:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    imported_roots = set()  # type: Set[str]
    dynamic_execution_calls = []  # type: List[str]
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in {"eval", "exec", "__import__"}:
                dynamic_execution_calls.append(node.func.id)

    forbidden_roots = {
        "boto3",
        "ftplib",
        "http",
        "paramiko",
        "requests",
        "smtplib",
        "socket",
        "subprocess",
        "urllib",
    }
    forbidden_found = sorted(imported_roots & forbidden_roots)
    passed = not forbidden_found and not dynamic_execution_calls
    return {
        "method": "DESIGN_AND_SOURCE_AUDIT",
        "runtime_instrumented": False,
        "source_audit_passed": passed,
        "result": (
            "NO_EXTERNAL_EFFECT_CAPABILITY_FOUND_IN_AUDITED_SOURCE"
            if passed
            else "EXTERNAL_EFFECT_CAPABILITY_FOUND"
        ),
        "imported_module_roots": sorted(imported_roots),
        "forbidden_import_roots_found": forbidden_found,
        "dynamic_execution_calls_found": sorted(dynamic_execution_calls),
        "declared_boundary": (
            "no network, subprocess, credential, or external-system API paths; "
            "the selected receipt is the only durable write"
        ),
        "limitation": (
            "This is a design and source audit, not runtime syscall, filesystem, "
            "or network instrumentation."
        ),
    }


def run_experiment(
    fixture: Dict[str, Any],
    trials: Optional[int] = None,
) -> Dict[str, Any]:
    """Run both fixtures and return evidence for an independent reviewer."""
    validate_fixture(fixture)
    fixture_provenance = _fixture_provenance(fixture)
    budgets = fixture["budgets"]
    policy = fixture["admission_policy"]
    trial_count = budgets["trials"] if trials is None else trials
    if isinstance(trial_count, bool) or not isinstance(trial_count, int):
        raise ValueError("trials must be an integer")
    if trial_count <= 0 or trial_count > budgets["trials"]:
        raise ValueError("trials must be positive and no greater than the fixture cap")

    experiment_started = time.perf_counter()
    total_deadline = (
        experiment_started + budgets["max_total_wall_time_seconds"]
    )
    deadline_boundaries = []  # type: List[str]
    loop_trials = []  # type: List[Dict[str, Any]]
    graph_trials = []  # type: List[Dict[str, Any]]

    task_a_admission = decide_architecture(
        fixture["task_a"],
        budgets,
        policy,
        topology="static_diamond",
    )
    if task_a_admission["selected"] != "GRAPH":
        raise RuntimeError("task_a fixture must be positively admitted to Graph")

    for index in range(trial_count):
        trial_number = index + 1
        _check_total_deadline(
            total_deadline,
            "before_trial_%s" % trial_number,
            deadline_boundaries,
        )
        order = ("loop", "graph") if index % 2 == 0 else ("graph", "loop")
        for architecture in order:
            _check_total_deadline(
                total_deadline,
                "before_task_a_%s_trial_%s" % (architecture, trial_number),
                deadline_boundaries,
            )
            result = run_task_a_architecture(
                fixture["task_a"],
                budgets,
                architecture=architecture,
            )
            if architecture == "loop":
                loop_trials.append(result)
            else:
                graph_trials.append(result)
            _check_total_deadline(
                total_deadline,
                "after_task_a_%s_trial_%s" % (architecture, trial_number),
                deadline_boundaries,
            )
        _check_total_deadline(
            total_deadline,
            "after_trial_%s" % trial_number,
            deadline_boundaries,
        )

    _check_total_deadline(
        total_deadline,
        "before_task_b",
        deadline_boundaries,
    )
    task_b = run_task_b(fixture["task_b"], budgets, policy=policy)
    _check_total_deadline(
        total_deadline,
        "after_task_b",
        deadline_boundaries,
    )

    loop_times = [trial["wall_time_seconds"] for trial in loop_trials]
    graph_times = [trial["wall_time_seconds"] for trial in graph_trials]
    loop_median = _median(loop_times)
    graph_median = _median(graph_times)
    speedup_ratio = round(loop_median / graph_median, 3)
    retry_contracts = [
        evaluate_retry_contract(
            fixture["task_a"],
            trial["retry_recovery"],
        )
        for trial in graph_trials
    ]

    task_a_correct = all(
        trial["correctness"]["passed"] for trial in loop_trials + graph_trials
    )
    graph_recovered = all(
        trial["retry_recovery"]["recovered"] for trial in graph_trials
    )
    node_local_only = all(
        contract["node_local_only"] for contract in retry_contracts
    )
    failing_attempts_match = all(
        contract["failing_node_attempts_match"] for contract in retry_contracts
    )
    unaffected_single_attempt = all(
        contract["all_unaffected_nodes_single_attempt"]
        for contract in retry_contracts
    )
    retry_count_matches = all(
        contract["retry_count_matches"] for contract in retry_contracts
    )

    max_task_time = max(
        loop_times + graph_times + [task_b["measured_wall_time_seconds"]]
    )
    max_retry_count = max(
        trial["retry_recovery"]["retry_count"]
        for trial in loop_trials + graph_trials
    )
    max_concurrency = max(
        trial["observed_peak_concurrency"]
        for trial in loop_trials + graph_trials
    )
    max_review_proxy = max(
        [
            trial["review_load_proxy"]["units"]
            for trial in loop_trials + graph_trials
        ]
        + [task_b["review_load_proxy"]["units"]]
    )

    source_audit = _source_capability_audit(Path(__file__).resolve())
    _check_total_deadline(
        total_deadline,
        "before_receipt",
        deadline_boundaries,
    )
    total_wall_time = time.perf_counter() - experiment_started
    within_limits = all(
        (
            total_wall_time <= budgets["max_total_wall_time_seconds"],
            max_task_time <= budgets["max_task_wall_time_seconds"],
            max_retry_count <= budgets["max_retries_per_node"],
            max_concurrency <= budgets["max_concurrency"],
            max_review_proxy <= budgets["max_review_load_units"],
        )
    )

    task_a_review = _task_a_review_proxy(fixture["task_a"])
    task_a_receipt = {
        "id": fixture["task_a"]["id"],
        "admission_decision": task_a_admission,
        "selected_architecture_executed": (
            task_a_admission["selected"] == "GRAPH"
            and len(graph_trials) == trial_count
        ),
        "graph_scheduler_invocations": len(graph_trials),
        "loop_execution_role": "serial comparison baseline only",
        "correctness": {
            "passed": task_a_correct,
            "loop_all_trials_passed": all(
                trial["correctness"]["passed"] for trial in loop_trials
            ),
            "graph_all_trials_passed": all(
                trial["correctness"]["passed"] for trial in graph_trials
            ),
            "verifier": "exact deterministic equality at every static join",
        },
        "measured_wall_time_seconds": {
            "loop": {"trials": loop_times, "median": loop_median},
            "graph": {"trials": graph_times, "median": graph_median},
            "graph_speedup_ratio_for_these_fixtures_only": speedup_ratio,
        },
        "retry_recovery": {
            "injected_node": fixture["task_a"]["transient_failure_node"],
            "graph_all_trials_recovered": graph_recovered,
            "node_local_only": node_local_only,
            "failing_node_attempts_match": failing_attempts_match,
            "all_unaffected_nodes_single_attempt": unaffected_single_attempt,
            "retry_count_matches": retry_count_matches,
            "graph_contracts": retry_contracts,
            "graph_attempts": [
                trial["retry_recovery"]["attempts"] for trial in graph_trials
            ],
            "graph_replayed_nodes": [
                trial["retry_recovery"]["replayed_nodes"] for trial in graph_trials
            ],
        },
        "review_load_proxy": task_a_review,
        "orchestration_overhead": {
            "loop_measured_seconds_median": _median(
                [
                    trial["orchestration_overhead"]["measured_seconds"]
                    for trial in loop_trials
                ]
            ),
            "graph_measured_seconds_median": _median(
                [
                    trial["orchestration_overhead"]["measured_seconds"]
                    for trial in graph_trials
                ]
            ),
            "definition": graph_trials[-1]["orchestration_overhead"]["definition"],
        },
        "observed_peak_concurrency": {
            "loop": max(
                trial["observed_peak_concurrency"] for trial in loop_trials
            ),
            "graph": max(
                trial["observed_peak_concurrency"] for trial in graph_trials
            ),
        },
    }

    evidence_criteria = {
        "task_a_positively_admitted_to_graph": task_a_admission["selected"]
        == "GRAPH",
        "task_a_selected_graph_executed": task_a_receipt[
            "selected_architecture_executed"
        ],
        "task_a_correct": task_a_correct,
        "task_a_graph_node_local_only": node_local_only,
        "task_a_failing_node_attempts_match": failing_attempts_match,
        "task_a_unaffected_nodes_single_attempt": unaffected_single_attempt,
        "task_a_retry_count_matches": retry_count_matches,
        "task_b_rejected_to_loop": task_b["admission_decision"]["selected"]
        == "LOOP",
        "task_b_graph_scheduler_skipped": task_b["orchestration_overhead"][
            "graph_scheduler_invocations"
        ]
        == 0,
        "task_b_all_intermediate_outputs_verified": all(
            receipt["verified"]
            for receipt in task_b["correctness"]["step_receipts"]
        ),
        "all_runtime_budgets_respected": within_limits,
        "source_audit_boundary_passed": source_audit["source_audit_passed"],
    }
    evidence_gate_passed = all(evidence_criteria.values())
    implementation_path = Path(__file__).resolve()

    return {
        "schema_version": "1.1",
        "experiment": {
            "id": fixture["experiment_id"],
            "verification_class": "LOCAL_ARCHITECTURAL_VERIFICATION",
            "claim_scope": fixture["claim_scope"],
            "universal_performance_claim": False,
            "production_claim": False,
            "workloads": "deterministic local sleeps and pure transformations",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "runtime": {
                "python": platform.python_version(),
                "platform": platform.system(),
                "minimum_supported_python": "3.8",
            },
        },
        "provenance": {
            "fixture": fixture_provenance,
            "implementation": {
                "algorithm": "sha256",
                "path": "benchmark.py",
                "sha256": _sha256_file(implementation_path),
            },
        },
        "budgets": {
            "configured": budgets,
            "observed": {
                "total_wall_time_seconds": round(total_wall_time, 6),
                "max_single_task_wall_time_seconds": round(max_task_time, 6),
                "max_retries_per_node": max_retry_count,
                "max_concurrency": max_concurrency,
                "max_nodes": len(fixture["task_a"]["branches"]) + 2,
                "max_review_load_proxy_units": max_review_proxy,
            },
            "within_limits": within_limits,
            "total_deadline_boundaries_checked": deadline_boundaries,
        },
        "task_a": task_a_receipt,
        "task_b": task_b,
        "external_side_effect_boundary": source_audit,
        "independent_review_handoff": {
            "decision": "DEFERRED_TO_INDEPENDENT_REVIEW",
            "agent_recommendation": "NONE",
            "artifact_status": (
                "EVIDENCE_COMPLETE"
                if evidence_gate_passed
                else "EVIDENCE_INCOMPLETE"
            ),
            "evidence_gate_passed": evidence_gate_passed,
            "criteria": evidence_criteria,
            "review_scope": "only the two declared static fixtures",
            "promotion_authority": "independent reviewer",
            "excluded_claims": [
                "universal Graph performance superiority",
                "dynamic or cyclic graph safety",
                "production scalability",
                "model-token or cost improvement",
                "runtime proof of external-side-effect absence",
                "measured human review effort",
            ],
        },
        "local_artifacts": {
            "durable_write": (
                "the caller-selected receipt path, constrained to this "
                "experiment directory"
            )
        },
    }


def _path_is_within(target: Path, root: Path) -> bool:
    try:
        target.relative_to(root)
        return True
    except ValueError:
        return False


def write_receipt(
    receipt: Dict[str, Any],
    output: Path,
    experiment_root: Path = EXPERIMENT_ROOT,
) -> None:
    root = experiment_root.resolve()
    receipts_root = (root / "receipts").resolve()
    target = output.resolve()
    if not _path_is_within(target, receipts_root):
        raise ValueError(
            "receipt path must stay inside experiment receipts directory"
        )
    if target.suffix.lower() != ".json":
        raise ValueError("receipt output must be a JSON file")

    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(target.suffix + ".tmp")
    try:
        temporary.write_text(
            json.dumps(receipt, indent=2, sort_keys=True, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        temporary.replace(target)
    finally:
        if temporary.exists():
            temporary.unlink()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run bounded local evidence for two static Loop-vs-Graph fixtures. "
            "The artifact defers all promotion decisions to independent review."
        )
    )
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument(
        "--trials",
        type=int,
        default=None,
        help="Override trial count without exceeding the fixture cap.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    fixture = load_fixture(args.fixture)
    receipt = run_experiment(fixture, trials=args.trials)
    write_receipt(receipt, args.receipt)
    print(json.dumps(receipt, indent=2, sort_keys=True, allow_nan=False))
    return (
        0
        if receipt["independent_review_handoff"]["artifact_status"]
        == "EVIDENCE_COMPLETE"
        else 2
    )


if __name__ == "__main__":
    raise SystemExit(main())
