#!/usr/bin/env python3
"""Hash-aware, read-only plan for adapting repository skills into a Vault."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from tools.legacy_compat import deprecation_envelope, explicit_directory
from tools.worker_flow.utils import sha256_file


def parse_skill(skill_folder: Path) -> dict[str, str]:
    skill_file = skill_folder / "SKILL.md"
    if not skill_file.is_file():
        return {}
    return {
        "name": skill_folder.name,
        "source": str(skill_file.resolve()),
        "source_sha256": sha256_file(skill_file),
    }


def build_adaptation_plan(repo_dir: Path, vault_dir: Path) -> dict[str, Any]:
    repo = explicit_directory(repo_dir, "repository")
    vault = explicit_directory(vault_dir, "vault")
    proposals: list[dict[str, Any]] = []
    for folder in sorted((repo / "skills").iterdir() if (repo / "skills").is_dir() else []):
        skill = parse_skill(folder)
        if not skill:
            continue
        target = vault / "wiki" / "sops" / f"sop-{skill['name']}.md"
        proposals.append(
            {
                **skill,
                "target": target.relative_to(vault).as_posix(),
                "target_sha256": sha256_file(target) if target.is_file() else None,
                "decision": "requires_review",
            }
        )
    return deprecation_envelope(
        "tools/adapt_skills_to_vault.py",
        vault,
        action="skill-adaptation-plan",
        facts={"repository": str(repo), "proposals": proposals},
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--vault", required=True, type=Path)
    args = parser.parse_args(argv)
    print(json.dumps(build_adaptation_plan(args.repo, args.vault), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
