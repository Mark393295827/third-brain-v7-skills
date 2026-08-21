#!/usr/bin/env python3
"""Read-only migration planner replacing the retired blind entity mover."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from tools.legacy_compat import deprecation_envelope, explicit_directory
from tools.worker_flow.frontmatter import parse_markdown
from tools.worker_flow.utils import sha256_file


VALID_CATEGORIES = {"people", "companies", "funds-investors", "products", "orgs"}


def plan_entity_migrations(vault_dir: Path) -> dict[str, Any]:
    vault = explicit_directory(vault_dir, "vault")
    root = vault / "wiki" / "entities"
    proposals: list[dict[str, Any]] = []
    if root.is_dir():
        for note in sorted(root.glob("*.md")):
            document = parse_markdown(note.read_text(encoding="utf-8", errors="replace"))
            category = document.frontmatter.get("entity_category")
            target = f"wiki/entities/{category}/{note.name}" if category in VALID_CATEGORIES else None
            proposals.append(
                {
                    "source": note.relative_to(vault).as_posix(),
                    "source_sha256": sha256_file(note),
                    "proposed_target": target,
                    "decision": "move" if target else "requires_review",
                }
            )
    return deprecation_envelope(
        "tools/auto_heal_vault.py",
        vault,
        action="entity-migration-plan",
        facts={"proposals": proposals},
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", required=True, type=Path)
    args = parser.parse_args(argv)
    print(json.dumps(plan_entity_migrations(args.vault), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
