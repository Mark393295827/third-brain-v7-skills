#!/usr/bin/env python3
"""Validate Third Brain skills against the V7 execution contract."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SKILLS_DIR = ROOT / "skills"
MAX_SKILL_LINES = 350
ALLOWED_TOP_LEVEL = {"SKILL.md", "scripts", "references", "assets", "agents"}
REQUIRED_METADATA = ["version", "updated", "profile", "assumes", "conflicts_with"]
REQUIRED_SECTIONS = [
    "## Usage Template",
    "## Workflow",
    "## Failure Protocol",
    "## Output Contract",
    "## Edge Cases",
    "## Success Metrics",
    "## Quality Gates",
]
REQUIRED_TAGS = ["skill_contract", "intake", "unknowns_gate", "execute", "evaluate"]
REQUIRED_CONTRACT_FIELDS = ["input", "output", "done", "non_goals"]
PROFILES = {"one-shot", "stateful", "loop", "high-risk"}
STATEFUL_PROFILES = {"stateful", "loop", "high-risk"}
ERROR_CODES = {
    "NEEDS_INPUT",
    "INSUFFICIENT_EVIDENCE",
    "BLOCKED_PERMISSION",
    "BLOCKED_DEPENDENCY",
    "VERIFY_FAILED",
    "NO_PROGRESS",
    "BUDGET_STOP",
}
MODEL_BRANDS = re.compile(r"\b(?:Opus|Sonnet|Haiku)\b", flags=re.IGNORECASE)
LOCAL_RESOURCE_PATTERNS = (
    re.compile(r"`((?:scripts|references|assets)/[^`\s#]+)`", flags=re.IGNORECASE),
    re.compile(r"\]\(((?:scripts|references|assets)/[^)\s#]+)(?:#[^)]*)?\)", flags=re.IGNORECASE),
)


@dataclass(frozen=True)
class Issue:
    path: Path
    message: str


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Parse the flat and one-level nested keys used by Agent Skills."""
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text

    raw = text[4:end]
    body = text[end + 5 :]
    data: dict[str, str] = {}
    parent = ""
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if line[0].isspace() and parent:
            data[f"{parent}.{key}"] = value
        else:
            parent = key if not value else ""
            data[key] = value
    return data, body


def section_text(body: str, heading: str) -> str:
    match = re.search(
        rf"^{re.escape(heading)}\s*$\n(?P<section>.*?)(?=^##\s|\Z)",
        body,
        flags=re.MULTILINE | re.DOTALL,
    )
    return match.group("section") if match else ""


def tag_block(body: str, tag: str) -> str | None:
    opening = f"<{tag}>"
    closing = f"</{tag}>"
    if body.count(opening) != 1 or body.count(closing) != 1:
        return None

    start = body.index(opening) + len(opening)
    end = body.index(closing)
    return body[start:end] if start <= end else None


def check_balanced_tag(body: str, tag: str) -> bool:
    return tag_block(body, tag) is not None


def check_skill(skill_dir: Path) -> list[Issue]:
    issues: list[Issue] = []
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.exists():
        return [Issue(skill_dir, "missing SKILL.md")]

    text = skill_file.read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter(text)
    line_count = len(text.splitlines())

    if line_count >= MAX_SKILL_LINES:
        issues.append(
            Issue(
                skill_file,
                f"SKILL.md has {line_count} lines; keep it below {MAX_SKILL_LINES} and move detail to references/",
            )
        )

    for key in ("name", "description"):
        if not frontmatter.get(key):
            issues.append(Issue(skill_file, f"frontmatter missing {key}"))
    for key in REQUIRED_METADATA:
        if not frontmatter.get(f"metadata.{key}"):
            issues.append(Issue(skill_file, f"frontmatter missing metadata.{key}"))

    name = frontmatter.get("name")
    if name and name != skill_dir.name:
        issues.append(Issue(skill_file, f"name '{name}' does not match folder '{skill_dir.name}'"))

    description = frontmatter.get("description", "")
    if description and "Use when" not in description:
        issues.append(Issue(skill_file, "description must include an explicit 'Use when' trigger"))

    profile = frontmatter.get("metadata.profile", "")
    if profile and profile not in PROFILES:
        issues.append(Issue(skill_file, f"unknown profile '{profile}'"))

    if not re.search(r"^#\s+\S+", body, flags=re.MULTILINE):
        issues.append(Issue(skill_file, "missing top-level title"))

    for section in REQUIRED_SECTIONS:
        if section not in body:
            issues.append(Issue(skill_file, f"missing required section: {section}"))

    if re.search(r"^##\s+When to Use\s*$", body, flags=re.MULTILINE | re.IGNORECASE):
        issues.append(Issue(skill_file, "duplicate trigger section; keep routing in description"))

    for tag in REQUIRED_TAGS:
        if not check_balanced_tag(body, tag):
            issues.append(Issue(skill_file, f"requires one balanced <{tag}> block"))

    skill_contract = tag_block(body, "skill_contract")
    for field in REQUIRED_CONTRACT_FIELDS:
        field_block = tag_block(skill_contract, field) if skill_contract is not None else None
        if not check_balanced_tag(body, field) or field_block is None:
            issues.append(Issue(skill_file, f"requires one balanced <{field}> block"))
        elif not field_block.strip():
            issues.append(Issue(skill_file, f"<{field}> block must not be empty"))

    if profile in STATEFUL_PROFILES and not check_balanced_tag(body, "state_contract"):
        issues.append(Issue(skill_file, f"{profile} profile requires <state_contract>"))

    if profile in {"loop", "high-risk"}:
        if not check_balanced_tag(body, "retry_policy"):
            issues.append(Issue(skill_file, f"{profile} profile requires <retry_policy>"))
        retry = section_text(body, "## Failure Protocol") + body
        if "max_attempts" not in retry or "NO_PROGRESS" not in retry:
            issues.append(
                Issue(skill_file, f"{profile} profile requires max_attempts and NO_PROGRESS controls")
            )

    if profile == "high-risk":
        for control in ("independent", "approval", "rollback"):
            if not re.search(rf"\b{control}\b", body, flags=re.IGNORECASE):
                issues.append(Issue(skill_file, f"high-risk profile missing {control} control"))

    failure = section_text(body, "## Failure Protocol")
    if failure and not any(code in failure for code in ERROR_CODES):
        issues.append(Issue(skill_file, "Failure Protocol must use a standard error code"))

    output = section_text(body, "## Output Contract").lower()
    for field in ("status", "result", "evidence", "unknowns", "next_action"):
        if output and field not in output:
            issues.append(Issue(skill_file, f"Output Contract missing {field}"))

    edge_cases = section_text(body, "## Edge Cases")
    if edge_cases and len(re.findall(r"^\s*[-*]\s+", edge_cases, flags=re.MULTILINE)) < 2:
        issues.append(Issue(skill_file, "Edge Cases requires at least two precise examples"))

    if MODEL_BRANDS.search(body):
        issues.append(Issue(skill_file, "model routing must use capabilities, not model brand names"))

    resources = {
        match.group(1)
        for pattern in LOCAL_RESOURCE_PATTERNS
        for match in pattern.finditer(body)
    }
    for resource in sorted(resources):
        resource_path = Path(*resource.split("/"))
        if not (skill_dir / resource_path).exists():
            issues.append(Issue(skill_file, f"references missing local resource: {resource}"))

    for child in skill_dir.iterdir():
        if child.name not in ALLOWED_TOP_LEVEL:
            issues.append(Issue(child, "unexpected file or folder inside skill directory"))

    return issues


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skills-dir",
        type=Path,
        default=DEFAULT_SKILLS_DIR,
        help="Directory containing skill folders (default: repository skills/).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    skills_dir = args.skills_dir.resolve()
    if not skills_dir.exists():
        print(f"Missing skills directory: {skills_dir}", file=sys.stderr)
        return 2

    skill_dirs = sorted(path for path in skills_dir.iterdir() if path.is_dir())
    issues = [issue for skill_dir in skill_dirs for issue in check_skill(skill_dir)]
    if issues:
        print("Agent Skills lint failed:")
        for issue in issues:
            print(f"- {display_path(issue.path)}: {issue.message}")
        return 1

    print(f"Agent Skills lint passed for {len(skill_dirs)} skills.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
