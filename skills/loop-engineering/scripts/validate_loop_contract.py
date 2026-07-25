#!/usr/bin/env python3
"""Validate the minimum control fields required before an agent loop starts."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


REQUIRED = {
    "objective",
    "mode",
    "trigger",
    "scope",
    "non-goals",
    "owner",
    "inputs",
    "artifacts path",
    "state path",
    "work clock",
    "success metric",
    "evidence",
    "verifier",
    "topology",
    "max iterations",
    "time limit",
    "budget",
    "review budget",
    "stop condition",
    "write-back",
    "permission boundary",
    "recovery",
}
VALID_MODES = {"goal", "loop", "automation", "autoresearch"}
VALID_TOPOLOGIES = {"single-agent", "maker-checker", "manager-workers"}
EMPTY_MARKERS = {"", "-", "n/a", "na", "none", "tbd", "todo", "unknown"}
FIELD_RE = re.compile(r"^\s*(?:[-*+]\s+)?(?:\*\*)?([^:*]+?)(?:\*\*)?\s*:\s*(.+?)\s*$")
FIELD_ALIASES = {
    "global work clock": "work clock",
    "change budget": "review budget",
    "review bandwidth": "review budget",
}
KNOWN_FIELD_RE = re.compile(
    r"(?:^\s*(?:[-*+]\s+)?|[ \t]{2,})(?:\*\*)?"
    rf"(?P<field>{'|'.join(re.escape(field) for field in sorted(REQUIRED | FIELD_ALIASES.keys(), key=len, reverse=True))})"
    r"(?:\*\*)?\s*:",
    re.IGNORECASE,
)
NUMERIC_CAP_RE = re.compile(r"(?<![\w.])[+-]?(?:\d+(?:\.\d*)?|\.\d+)")
UNBOUNDED_CAP_RE = re.compile(
    r"\b(?:unlimited|unbounded|uncapped|infinite|indefinitely|forever|open[- ]ended)\b"
    r"|\b(?:no|without)\s+(?:an?\s+)?"
    r"(?:(?:upper|hard|fixed)\s+)?(?:limit|maximum|cap|bound|end)\b"
    r"|\b(?:repeat|continue|retry|run|loop)\b.{0,32}"
    r"\b(?:as long as|while)\s+(?:needed|required|necessary)\b",
    re.IGNORECASE,
)
NUMERIC_TOKEN = r"(?<![\w.])(?P<cap>[+-]?(?:\d+(?:\.\d*)?|\.\d+))"
CAP_UNIT_PATTERNS = {
    "max iterations": re.compile(
        NUMERIC_TOKEN + r"\s*(?:iterations?|runs?|cycles?|attempts?)\b",
        re.IGNORECASE,
    ),
    "time limit": re.compile(
        NUMERIC_TOKEN
        + r"\s*(?:milliseconds?|ms|seconds?|minutes?|hours?|days?)\b",
        re.IGNORECASE,
    ),
    "budget": re.compile(
        NUMERIC_TOKEN
        + r"\s*(?:(?:tool|api|model)\s+)?"
        + r"(?:calls?|tokens?|credits?|usd|dollars?)\b",
        re.IGNORECASE,
    ),
    "review budget": re.compile(
        NUMERIC_TOKEN
        + r"\s*(?:changed\s+lines?|lines?|files?|diffs?|reviews?)\b",
        re.IGNORECASE,
    ),
}
MODE_ALIASES = {
    "goal-oriented agent": "goal",
    "interval loop": "loop",
    "scheduled loop": "automation",
}


def normalize(field: str) -> str:
    return re.sub(r"\s+", " ", field.strip().lower())


def parse_contract(path: Path) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        matches = list(KNOWN_FIELD_RE.finditer(line))
        if matches:
            for index, match in enumerate(matches):
                key = normalize(match.group("field"))
                key = FIELD_ALIASES.get(key, key)
                value_end = matches[index + 1].start() if index + 1 < len(matches) else len(line)
                value = line[match.end() : value_end].strip()
                if key not in fields or not fields[key]:
                    fields[key] = value
                elif value:
                    fields[key] = f"{fields[key]}; {value}"
            continue

        match = FIELD_RE.match(line)
        if match:
            key = normalize(match.group(1))
            key = FIELD_ALIASES.get(key, key)
            value = match.group(2).strip()
            fields[key] = f"{fields[key]}; {value}" if key in fields else value
    return fields


def numeric_caps(field: str, value: str) -> list[float]:
    pattern = CAP_UNIT_PATTERNS[field]
    scoped = [float(match.group("cap")) for match in pattern.finditer(value)]
    if scoped:
        return scoped
    return [float(match.group()) for match in NUMERIC_CAP_RE.finditer(value)]


def validate(fields: dict[str, str], strict: bool) -> list[str]:
    errors: list[str] = []
    for field in sorted(REQUIRED):
        value = fields.get(field, "")
        if normalize(value) in EMPTY_MARKERS:
            errors.append(f"missing or empty field: {field}")

    mode = normalize(fields.get("mode", "")).rstrip(".")
    mode = MODE_ALIASES.get(mode, mode)
    if mode and mode not in VALID_MODES:
        errors.append("mode must be Goal, Loop, Automation, or AutoResearch")

    topology = normalize(fields.get("topology", "")).rstrip(".")
    if topology and topology not in VALID_TOPOLOGIES:
        errors.append("topology must be single-agent, maker-checker, or manager-workers")

    for field in ("max iterations", "time limit", "budget", "review budget"):
        value = normalize(fields.get(field, ""))
        if value and UNBOUNDED_CAP_RE.search(value):
            errors.append(f"{field} must contain a finite numeric cap")
            continue
        caps = numeric_caps(field, value)
        if value and not caps:
            errors.append(f"{field} must contain a finite numeric cap")
        elif any(cap <= 0 for cap in caps):
            errors.append(f"{field} must contain a positive finite numeric cap")

    review_budget = normalize(fields.get("review budget", ""))
    if strict:
        numbers = [int(match) for match in re.findall(r"\d+", review_budget)]
        mentions_lines = "line" in review_budget or "changed" in review_budget or "diff" in review_budget
        if mentions_lines and numbers and max(numbers) > 1000:
            errors.append("review budget should cap changed lines at 1000 or less")

    stop = normalize(fields.get("stop condition", ""))
    if any(phrase in stop for phrase in ("until satisfied", "keep improving", "run forever", "infinite")):
        errors.append("stop condition must be an evidence-based result or finite cap")

    verifier = normalize(fields.get("verifier", ""))
    if "self" in verifier or "same builder" in verifier:
        errors.append("verifier cannot be the builder alone")

    boundary = normalize(fields.get("permission boundary", ""))
    high_risk_boundary = re.search(r"\b(production|deploy|publish|external|shared)\b", boundary)
    explicitly_denied = re.search(
        r"\b(no|not|without|deny|denied)\b.{0,32}\b(production|deploy|publish|external|shared)\b",
        boundary,
    )
    if high_risk_boundary and not explicitly_denied:
        if "approval" not in boundary or "rollback" not in boundary:
            errors.append("external or production boundary requires approval and rollback")

    if strict and topology == "manager-workers":
        integration_controls = f"{normalize(fields.get('recovery', ''))} {boundary}"
        if "integration gate" not in integration_controls:
            errors.append(
                "manager-workers requires an explicit integration gate "
                "in recovery or permission boundary"
            )

    if strict and mode == "automation":
        trigger = normalize(fields.get("trigger", ""))
        if not re.search(r"\b(cron|schedule|scheduled|webhook|event|queue|timer|ci|pr)\b", trigger):
            errors.append("automation mode requires a schedule, webhook, event, queue, CI, PR, or timer trigger")

    return errors


def canonical_mode(value: str) -> str:
    mode = normalize(value).rstrip(".")
    return MODE_ALIASES.get(mode, mode)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", type=Path)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if not args.contract.is_file():
        parser.error(f"contract does not exist: {args.contract}")

    fields = parse_contract(args.contract)
    errors = validate(fields, args.strict)
    result = {"contract": str(args.contract), "valid": not errors, "errors": errors}

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif errors:
        print("FAIL loop contract")
        for error in errors:
            print(f"- {error}")
    else:
        print("PASS loop contract")
        print(f"- fields: {len(fields)}")
        print(f"- mode: {canonical_mode(fields['mode'])}")
        print(f"- topology: {normalize(fields['topology']).rstrip('.')}")
        print(f"- stop condition: {fields['stop condition']}")

    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
