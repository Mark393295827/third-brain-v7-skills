#!/usr/bin/env python3
"""Read-only audit for skill contract versions; never performs global rewrites."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from tools.legacy_compat import explicit_directory


VERSION_RE = re.compile(r'(?m)^version:\s*["\']?([^"\'\s]+)')


def audit_skill_versions(repo_dir: Path) -> dict[str, Any]:
    repo = explicit_directory(repo_dir, "repository")
    rows: list[dict[str, str | None]] = []
    for skill_file in sorted((repo / "skills").glob("*/SKILL.md")):
        text = skill_file.read_text(encoding="utf-8", errors="replace")
        match = VERSION_RE.search(text)
        rows.append(
            {
                "skill": skill_file.parent.name,
                "declared_version": match.group(1) if match else None,
                "status": "current" if match and match.group(1) == "8.1.0" else "requires_review",
            }
        )
    return {
        "status": "DEPRECATED_READ_ONLY",
        "entrypoint": "tools/upgrade_skills_v81.py",
        "deprecated_in": "8.1",
        "removal_release": "9.0",
        "repository": str(repo),
        "replacement_command": "edit reviewed files explicitly and run python tools/lint-agent-skills.py",
        "side_effect_count": 0,
        "skills": rows,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=Path)
    args = parser.parse_args(argv)
    print(json.dumps(audit_skill_versions(args.repo), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
