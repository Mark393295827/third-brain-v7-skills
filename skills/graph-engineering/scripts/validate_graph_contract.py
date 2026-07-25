#!/usr/bin/env python3
"""Validate a bounded static Graph Engineering contract."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set, Tuple


REQUIRED_TOP_LEVEL = {
    "schema_version",
    "graph_id",
    "objective",
    "non_goals",
    "owner",
    "artifact_path",
    "state_path",
    "entry_nodes",
    "terminal_nodes",
    "budgets",
    "permission_boundary",
    "nodes",
    "edges",
    "joins",
    "stop_conditions",
    "recovery",
}
REQUIRED_BUDGETS = {
    "max_nodes",
    "max_concurrency",
    "max_attempts_per_node",
    "wall_time_seconds",
    "tool_calls",
    "review_changed_lines",
}
REQUIRED_NODE_FIELDS = {
    "id",
    "kind",
    "owner",
    "inputs",
    "outputs",
    "reads",
    "writes",
    "verifier",
    "timeout_seconds",
    "max_attempts",
    "tool_calls",
    "effect_class",
    "idempotency",
    "compensation",
}
REQUIRED_EDGE_FIELDS = {
    "from",
    "to",
    "type",
    "payload_schema",
    "condition",
    "failure_route",
}
REQUIRED_JOIN_FIELDS = {
    "id",
    "target",
    "mode",
    "inputs",
    "verifier",
    "quorum",
}
VALID_NODE_KINDS = {
    "deterministic",
    "loop",
    "agent",
    "agent-team",
    "human-gate",
    "subgraph",
}
VALID_EDGE_TYPES = {
    "data",
    "control",
    "verification",
    "failure",
    "compensation",
}
SCHEMA_EDGE_TYPES = {"data", "verification"}
DEPENDENCY_EDGE_TYPES = {"data", "control", "verification"}
VALID_JOIN_MODES = {
    "all",
    "reduce",
    "first-success",
    "quorum",
    "barrier-verifier",
    "human-gate",
}
VALID_EFFECT_CLASSES = {"read-only", "reversible", "external"}
NODE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_positive_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _string_list(value: Any) -> bool:
    return (
        isinstance(value, list)
        and all(_is_non_empty_string(item) for item in value)
        and len(value) == len(set(value))
    )


def _missing_fields(value: Dict[str, Any], required: Iterable[str]) -> List[str]:
    return sorted(field for field in required if field not in value)


def _detect_cycle(
    node_ids: Set[str],
    adjacency: Dict[str, Set[str]],
) -> bool:
    indegree = {node_id: 0 for node_id in node_ids}
    for source in node_ids:
        for target in adjacency.get(source, set()):
            if target in indegree:
                indegree[target] += 1

    ready = [node_id for node_id, degree in indegree.items() if degree == 0]
    visited = 0
    while ready:
        source = ready.pop()
        visited += 1
        for target in adjacency.get(source, set()):
            if target not in indegree:
                continue
            indegree[target] -= 1
            if indegree[target] == 0:
                ready.append(target)
    return visited != len(node_ids)


def _reachable(
    entries: List[str],
    adjacency: Dict[str, Set[str]],
) -> Set[str]:
    seen: Set[str] = set()
    stack = list(entries)
    while stack:
        node_id = stack.pop()
        if node_id in seen:
            continue
        seen.add(node_id)
        stack.extend(adjacency.get(node_id, set()) - seen)
    return seen


def validate(contract: Dict[str, Any], strict: bool = False) -> List[str]:
    errors: List[str] = []
    if not isinstance(contract, dict):
        return ["contract must be a JSON object"]

    for field in _missing_fields(contract, REQUIRED_TOP_LEVEL):
        errors.append("missing top-level field: %s" % field)
    if errors:
        return errors

    if contract["schema_version"] != "1.0":
        errors.append("schema_version must be 1.0")
    for field in ("graph_id", "objective", "owner", "artifact_path", "state_path"):
        if not _is_non_empty_string(contract.get(field)):
            errors.append("%s must be a non-empty string" % field)
    if not _string_list(contract.get("non_goals")) or not contract.get("non_goals"):
        errors.append("non_goals must be a non-empty unique string list")
    if not _string_list(contract.get("stop_conditions")) or not contract.get(
        "stop_conditions"
    ):
        errors.append("stop_conditions must be a non-empty unique string list")

    budgets = contract.get("budgets")
    if not isinstance(budgets, dict):
        errors.append("budgets must be an object")
        budgets = {}
    for field in _missing_fields(budgets, REQUIRED_BUDGETS):
        errors.append("missing budget: %s" % field)
    for field in REQUIRED_BUDGETS:
        if field in budgets and not _is_positive_int(budgets[field]):
            errors.append("%s must be a positive integer" % field)

    if strict:
        if _is_positive_int(budgets.get("max_nodes")) and budgets["max_nodes"] > 64:
            errors.append("max_nodes must be 64 or less in strict mode")
        if (
            _is_positive_int(budgets.get("max_concurrency"))
            and budgets["max_concurrency"] > 16
        ):
            errors.append("max_concurrency must be 16 or less in strict mode")
        if (
            _is_positive_int(budgets.get("max_attempts_per_node"))
            and budgets["max_attempts_per_node"] > 5
        ):
            errors.append("max_attempts_per_node must be 5 or less in strict mode")
        if (
            _is_positive_int(budgets.get("review_changed_lines"))
            and budgets["review_changed_lines"] > 1000
        ):
            errors.append("review_changed_lines must be 1000 or less in strict mode")

    permission = contract.get("permission_boundary")
    if not isinstance(permission, dict):
        errors.append("permission_boundary must be an object")
        permission = {}
    for field in ("allowed", "denied", "approval_required"):
        value = permission.get(field)
        if not isinstance(value, list) or not all(
            _is_non_empty_string(item) for item in value
        ):
            errors.append("permission_boundary.%s must be a string list" % field)
    if not _is_non_empty_string(permission.get("rollback")):
        errors.append("permission_boundary.rollback must be non-empty")

    recovery = contract.get("recovery")
    if not isinstance(recovery, dict):
        errors.append("recovery must be an object")
        recovery = {}
    for field in ("checkpoint", "write_back"):
        if not _is_non_empty_string(recovery.get(field)):
            errors.append("recovery.%s must be non-empty" % field)
    if not isinstance(recovery.get("whole_graph_rerun"), bool):
        errors.append("recovery.whole_graph_rerun must be boolean")
    elif strict and recovery["whole_graph_rerun"]:
        errors.append("strict static graphs must recover the smallest failed unit")

    nodes = contract.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        errors.append("nodes must be a non-empty list")
        nodes = []

    node_map: Dict[str, Dict[str, Any]] = {}
    writers: Dict[str, List[str]] = {}
    external_nodes: Set[str] = set()
    total_node_tool_calls = 0

    for index, node in enumerate(nodes):
        label = "node[%d]" % index
        if not isinstance(node, dict):
            errors.append("%s must be an object" % label)
            continue
        for field in _missing_fields(node, REQUIRED_NODE_FIELDS):
            errors.append("%s missing field: %s" % (label, field))
        node_id = node.get("id")
        if not _is_non_empty_string(node_id) or not NODE_ID_RE.fullmatch(node_id):
            errors.append("%s id must match %s" % (label, NODE_ID_RE.pattern))
            continue
        if node_id in node_map:
            errors.append("duplicate node id: %s" % node_id)
            continue
        node_map[node_id] = node

        if node.get("kind") not in VALID_NODE_KINDS:
            errors.append("node %s has unsupported kind: %s" % (node_id, node.get("kind")))
        if not _is_non_empty_string(node.get("owner")):
            errors.append("node %s owner must be non-empty" % node_id)
        for field in ("inputs", "outputs", "reads", "writes"):
            if not _string_list(node.get(field)) and node.get(field) != []:
                errors.append("node %s %s must be a unique string list" % (node_id, field))
        if not _is_non_empty_string(node.get("verifier")):
            errors.append("node %s verifier must be non-empty" % node_id)
        for field in ("timeout_seconds", "max_attempts", "tool_calls"):
            if not _is_positive_int(node.get(field)):
                errors.append("node %s %s must be a positive integer" % (node_id, field))

        if (
            _is_positive_int(node.get("timeout_seconds"))
            and _is_positive_int(budgets.get("wall_time_seconds"))
            and node["timeout_seconds"] > budgets["wall_time_seconds"]
        ):
            errors.append("node %s timeout exceeds graph wall_time_seconds" % node_id)
        if (
            _is_positive_int(node.get("max_attempts"))
            and _is_positive_int(budgets.get("max_attempts_per_node"))
            and node["max_attempts"] > budgets["max_attempts_per_node"]
        ):
            errors.append("node %s max_attempts exceeds graph cap" % node_id)
        if _is_positive_int(node.get("tool_calls")):
            total_node_tool_calls += node["tool_calls"]

        effect_class = node.get("effect_class")
        if effect_class not in VALID_EFFECT_CLASSES:
            errors.append(
                "node %s has unsupported effect_class: %s"
                % (node_id, effect_class)
            )
        if not _is_non_empty_string(node.get("idempotency")):
            errors.append("node %s idempotency must be non-empty" % node_id)
        if effect_class == "read-only" and node.get("writes"):
            errors.append("read-only node %s cannot declare writes" % node_id)
        if effect_class == "external":
            external_nodes.add(node_id)
            if not _is_non_empty_string(node.get("compensation")):
                errors.append("external node %s requires compensation" % node_id)

        for target in node.get("writes", []) if isinstance(node.get("writes"), list) else []:
            if _is_non_empty_string(target):
                writers.setdefault(target, []).append(node_id)

    node_ids = set(node_map)
    if _is_positive_int(budgets.get("max_nodes")) and len(nodes) > budgets["max_nodes"]:
        errors.append("declared nodes exceed max_nodes")
    if (
        _is_positive_int(budgets.get("max_concurrency"))
        and _is_positive_int(budgets.get("max_nodes"))
        and budgets["max_concurrency"] > budgets["max_nodes"]
    ):
        errors.append("max_concurrency cannot exceed max_nodes")
    if (
        _is_positive_int(budgets.get("max_concurrency"))
        and nodes
        and budgets["max_concurrency"] > len(nodes)
    ):
        errors.append("max_concurrency cannot exceed declared node count")
    if (
        _is_positive_int(budgets.get("tool_calls"))
        and total_node_tool_calls > budgets["tool_calls"]
    ):
        errors.append("sum of node tool_calls exceeds graph tool_calls budget")
    for target, owners in sorted(writers.items()):
        if len(owners) > 1:
            errors.append("write target has multiple owners: %s" % target)

    edges = contract.get("edges")
    if not isinstance(edges, list):
        errors.append("edges must be a list")
        edges = []
    adjacency = {node_id: set() for node_id in node_ids}  # type: Dict[str, Set[str]]
    outgoing = {node_id: set() for node_id in node_ids}  # type: Dict[str, Set[str]]
    incoming = {node_id: set() for node_id in node_ids}  # type: Dict[str, Set[str]]
    compensation_sources: Set[str] = set()
    edge_keys: Set[Tuple[str, str, str, str]] = set()

    for index, edge in enumerate(edges):
        label = "edge[%d]" % index
        if not isinstance(edge, dict):
            errors.append("%s must be an object" % label)
            continue
        for field in _missing_fields(edge, REQUIRED_EDGE_FIELDS):
            errors.append("%s missing field: %s" % (label, field))
        source = edge.get("from")
        target = edge.get("to")
        edge_type = edge.get("type")
        payload = edge.get("payload_schema")
        if source not in node_ids or target not in node_ids:
            errors.append("edge references unknown node: %s -> %s" % (source, target))
            continue
        if source == target:
            errors.append("self edge is not allowed: %s" % source)
        if edge_type not in VALID_EDGE_TYPES:
            errors.append("unsupported edge type: %s" % edge_type)
        if not _is_non_empty_string(edge.get("condition")):
            errors.append("%s condition must be non-empty" % label)
        key = (source, target, str(edge_type), str(payload))
        if key in edge_keys:
            errors.append("duplicate edge: %s -> %s (%s)" % (source, target, edge_type))
        edge_keys.add(key)
        adjacency[source].add(target)
        outgoing[source].add(target)
        incoming[target].add(source)

        if edge_type in SCHEMA_EDGE_TYPES:
            if not _is_non_empty_string(payload):
                errors.append("%s payload_schema must be non-empty" % label)
            else:
                if payload not in node_map[source].get("outputs", []):
                    errors.append(
                        "%s edge schema %s is not declared by %s.outputs"
                        % (edge_type, payload, source)
                    )
                if payload not in node_map[target].get("inputs", []):
                    errors.append(
                        "%s edge schema %s is not declared by %s.inputs"
                        % (edge_type, payload, target)
                    )
        failure_route = edge.get("failure_route")
        if _is_non_empty_string(failure_route) and failure_route not in node_ids:
            errors.append("%s failure_route references unknown node: %s" % (label, failure_route))
        elif _is_non_empty_string(failure_route):
            # A failure route is an implicit control arc from the source node.
            # It must participate in the same reachability and cycle checks as
            # an explicit edge so recovery cannot hide a feedback loop.
            adjacency[source].add(failure_route)
            outgoing[source].add(failure_route)
            incoming[failure_route].add(source)
        if edge_type == "compensation":
            compensation_sources.add(source)

    entries = contract.get("entry_nodes")
    terminals = contract.get("terminal_nodes")
    if not _string_list(entries) or not entries:
        errors.append("entry_nodes must be a non-empty unique string list")
        entries = []
    if not _string_list(terminals) or not terminals:
        errors.append("terminal_nodes must be a non-empty unique string list")
        terminals = []
    for node_id in entries:
        if node_id not in node_ids:
            errors.append("unknown entry node: %s" % node_id)
        elif strict and incoming[node_id]:
            errors.append("entry node has incoming edge: %s" % node_id)
    for node_id in terminals:
        if node_id not in node_ids:
            errors.append("unknown terminal node: %s" % node_id)
        elif strict and outgoing[node_id]:
            errors.append("terminal node has outgoing edge: %s" % node_id)

    known_entries = [node_id for node_id in entries if node_id in node_ids]
    for node_id in sorted(node_ids - _reachable(known_entries, adjacency)):
        errors.append("unreachable node: %s" % node_id)
    if _detect_cycle(node_ids, adjacency):
        errors.append("static graph must be acyclic")

    joins = contract.get("joins")
    if not isinstance(joins, list):
        errors.append("joins must be a list")
        joins = []
    join_targets: Set[str] = set()
    join_ids: Set[str] = set()
    for index, join in enumerate(joins):
        label = "join[%d]" % index
        if not isinstance(join, dict):
            errors.append("%s must be an object" % label)
            continue
        for field in _missing_fields(join, REQUIRED_JOIN_FIELDS):
            errors.append("%s missing field: %s" % (label, field))
        join_id = join.get("id")
        target = join.get("target")
        inputs = join.get("inputs")
        mode = join.get("mode")
        if not _is_non_empty_string(join_id):
            errors.append("%s id must be non-empty" % label)
            join_id = label
        elif join_id in join_ids:
            errors.append("duplicate join id: %s" % join_id)
        join_ids.add(join_id)
        if target not in node_ids:
            errors.append("join %s references unknown target: %s" % (join_id, target))
            continue
        if target in join_targets:
            errors.append("multiple join contracts target node: %s" % target)
        join_targets.add(target)
        if mode not in VALID_JOIN_MODES:
            errors.append("join %s has unsupported mode: %s" % (join_id, mode))
        if not _string_list(inputs) or len(inputs) < 2:
            errors.append("join %s inputs must contain at least two unique nodes" % join_id)
            inputs = []
        for source in inputs:
            if source not in node_ids:
                errors.append("join %s references unknown input: %s" % (join_id, source))
            elif target not in adjacency.get(source, set()):
                errors.append(
                    "join %s input %s has no edge to %s"
                    % (join_id, source, target)
                )
        dependency_inputs = {
            edge.get("from")
            for edge in edges
            if isinstance(edge, dict)
            and edge.get("to") == target
            and edge.get("type") in DEPENDENCY_EDGE_TYPES
            and edge.get("from") in node_ids
        }
        if inputs and set(inputs) != dependency_inputs:
            errors.append("join %s inputs must match incoming dependencies" % join_id)
        if not _is_non_empty_string(join.get("verifier")):
            errors.append("join %s verifier must be non-empty" % join_id)
        quorum = join.get("quorum")
        if mode == "quorum":
            if not _is_positive_int(quorum) or quorum > len(inputs):
                errors.append(
                    "join %s quorum must be between 1 and %d"
                    % (join_id, len(inputs))
                )
        elif quorum is not None:
            errors.append("join %s quorum must be null unless mode is quorum" % join_id)
        if mode == "human-gate" and node_map[target].get("kind") != "human-gate":
            errors.append("join %s human-gate target must use kind human-gate" % join_id)

    for node_id in sorted(node_ids):
        dependency_sources = {
            edge.get("from")
            for edge in edges
            if isinstance(edge, dict)
            and edge.get("to") == node_id
            and edge.get("type") in DEPENDENCY_EDGE_TYPES
            and edge.get("from") in node_ids
        }
        if len(dependency_sources) > 1 and node_id not in join_targets:
            errors.append(
                "node %s has multiple incoming dependencies but no join contract"
                % node_id
            )

    approval_required = permission.get("approval_required")
    has_approval = isinstance(approval_required, list) and bool(approval_required)
    approval_scopes = (
        set(approval_required) if isinstance(approval_required, list) else set()
    )
    allowed_scopes = (
        set(permission.get("allowed", []))
        if isinstance(permission.get("allowed"), list)
        else set()
    )
    denied_scopes = (
        set(permission.get("denied", []))
        if isinstance(permission.get("denied"), list)
        else set()
    )
    for node_id in sorted(external_nodes):
        if not has_approval:
            errors.append("external node %s requires an approval boundary" % node_id)
        if node_id not in approval_scopes:
            errors.append(
                "external node %s must be named in approval_required" % node_id
            )
        approval_edges = [
            edge
            for edge in edges
            if isinstance(edge, dict)
            and edge.get("to") == node_id
            and edge.get("type") in SCHEMA_EDGE_TYPES
            and edge.get("from") in node_map
            and node_map[edge["from"]].get("kind") == "human-gate"
            and _is_non_empty_string(edge.get("payload_schema"))
            and "approval" in edge["payload_schema"].lower()
            and "receipt" in edge["payload_schema"].lower()
        ]
        if not approval_edges:
            errors.append(
                "external node %s requires a direct human-gate approval receipt"
                % node_id
            )
        node_writes = node_map[node_id].get("writes", [])
        if not isinstance(node_writes, list) or not node_writes:
            errors.append(
                "external node %s must declare at least one write target" % node_id
            )
        else:
            for target in node_writes:
                if target not in allowed_scopes:
                    errors.append(
                        "external node %s write target is not explicitly allowed: %s"
                        % (node_id, target)
                    )
                if target in denied_scopes:
                    errors.append(
                        "external node %s write target is denied: %s"
                        % (node_id, target)
                    )
        if node_id not in compensation_sources:
            errors.append("external node %s requires a compensation edge" % node_id)

    return errors


def load_contract(path: Path) -> Dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError("invalid JSON at line %d: %s" % (error.lineno, error.msg))
    if not isinstance(value, dict):
        raise ValueError("contract must be a JSON object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", type=Path)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if not args.contract.is_file():
        parser.error("contract does not exist: %s" % args.contract)
    try:
        contract = load_contract(args.contract)
    except ValueError as error:
        print("FAIL graph contract")
        print("- %s" % error)
        return 1

    errors = validate(contract, strict=args.strict)
    result = {
        "contract": str(args.contract),
        "valid": not errors,
        "errors": errors,
        "graph_id": contract.get("graph_id"),
        "nodes": len(contract.get("nodes", []))
        if isinstance(contract.get("nodes"), list)
        else 0,
        "edges": len(contract.get("edges", []))
        if isinstance(contract.get("edges"), list)
        else 0,
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif errors:
        print("FAIL graph contract")
        for error in errors:
            print("- %s" % error)
    else:
        print("PASS graph contract")
        print("- graph_id: %s" % result["graph_id"])
        print("- nodes: %d" % result["nodes"])
        print("- edges: %d" % result["edges"])
        print("- entries: %s" % ", ".join(contract["entry_nodes"]))
        print("- terminals: %s" % ", ".join(contract["terminal_nodes"]))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
