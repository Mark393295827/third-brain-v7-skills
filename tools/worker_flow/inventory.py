from __future__ import annotations

import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .frontmatter import parse_markdown
from .governance import CONCEPT_REQUIRED, CONCEPT_SECTIONS, SOURCE_REQUIRED
from .utils import iso_z, normalized_text_sha256, sha256_file


SOURCE_LINK_RE = re.compile(r"\[\[(sources/[^\]|#]+)(?:#\^([^\]|]+))?")
VALID_HASH_RE = re.compile(r"^(?:sha256:)?[a-f0-9]{64}$", re.IGNORECASE)
SYSTEM_ARTIFACT_PREFIXES = (
    "system/contracts/",
    "system/docs/",
    "system/runs/",
    "system/scripts/",
    "system/templates/",
)


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _is_system_artifact(relative: str) -> bool:
    return relative.startswith(SYSTEM_ARTIFACT_PREFIXES)


def inventory_debt_signature(inventory: dict[str, Any]) -> dict[str, int]:
    """Return only governed debt counters suitable for no-regression comparison."""

    signature: dict[str, int] = {}
    for section in ("missing_frontmatter", "unresolved_template_tokens"):
        values = inventory.get(section) if isinstance(inventory.get(section), dict) else {}
        for layer in ("maps", "sources", "system", "wiki"):
            item = values.get(layer) if isinstance(values.get(layer), dict) else {}
            signature[f"{section}.{layer}"] = int(item.get("count") or 0)
    sources = inventory.get("sources") if isinstance(inventory.get("sources"), dict) else {}
    for key in (
        "provenance_debt_count",
        "duplicate_hash_group_count",
        "invalid_hash_count",
        "identity_thread_count",
    ):
        signature[f"sources.{key}"] = int(sources.get(key) or 0)
    for layer in ("maps", "system"):
        values = inventory.get(layer) if isinstance(inventory.get(layer), dict) else {}
        signature[f"{layer}.debt_count"] = int(values.get("debt_count") or 0)
    return signature


def inventory_debt_regressions(
    baseline: dict[str, int], observed: dict[str, int]
) -> list[dict[str, int | str]]:
    regressions: list[dict[str, int | str]] = []
    for metric in sorted(set(baseline) | set(observed)):
        before = int(baseline.get(metric, 0))
        after = int(observed.get(metric, 0))
        if after > before:
            regressions.append({"metric": metric, "before": before, "after": after})
    return regressions


def build_inventory(
    vault_root: Path,
    contract_version: str,
    vault_fingerprint: str,
    limit: int = 100,
    candidate_domain: str | None = None,
) -> dict[str, Any]:
    layer_roots = {
        "maps": vault_root / "maps",
        "sources": vault_root / "sources",
        "system": vault_root / "system",
        "wiki": vault_root / "wiki",
    }
    files_by_layer: dict[str, list[Path]] = {
        name: sorted(path.rglob("*.md")) if path.is_dir() else [] for name, path in layer_roots.items()
    }
    version_counts: dict[str, Counter[str]] = {name: Counter() for name in layer_roots}
    missing_frontmatter: dict[str, list[str]] = {name: [] for name in layer_roots}
    unresolved_tokens: dict[str, list[str]] = {name: [] for name in layer_roots}
    source_debt: list[dict[str, Any]] = []
    source_hashes: dict[str, list[str]] = defaultdict(list)
    source_identities: dict[str, list[str]] = defaultdict(list)
    invalid_hashes: list[dict[str, str]] = []
    retrofit_candidates: dict[str, list[dict[str, Any]]] = {
        "STRUCTURE_ONLY": [],
        "EVIDENCE_RESTORABLE": [],
        "INSUFFICIENT_EVIDENCE": [],
    }
    map_debt: list[dict[str, Any]] = []
    system_debt: list[dict[str, Any]] = []
    excluded_system_artifacts: list[str] = []

    for layer, files in files_by_layer.items():
        for path in files:
            relative = _relative(path, vault_root)
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError as exc:
                system_debt.append({"path": relative, "issue": "read-error", "detail": str(exc)})
                continue
            if layer == "system" and _is_system_artifact(relative):
                excluded_system_artifacts.append(relative)
                continue
            document = parse_markdown(text)
            if not document.frontmatter:
                missing_frontmatter[layer].append(relative)
            version_counts[layer][str(document.frontmatter.get("contract_version") or document.frontmatter.get("version") or "unversioned")] += 1
            expected_template = relative.startswith("system/templates/")
            if "{{" in text and "}}" in text and not expected_template:
                unresolved_tokens[layer].append(relative)

            if layer == "sources":
                missing = sorted(field for field in SOURCE_REQUIRED if field not in document.frontmatter)
                if missing:
                    source_debt.append({"path": relative, "missing_fields": missing})
                source_hash = str(document.frontmatter.get("hash") or "")
                identity = str(document.frontmatter.get("source_identity") or document.frontmatter.get("source_url") or "")
                if source_hash and VALID_HASH_RE.fullmatch(source_hash):
                    source_hashes[source_hash].append(relative)
                elif source_hash:
                    invalid_hashes.append({"path": relative, "hash": source_hash})
                if identity and identity.casefold() != "unknown":
                    source_identities[identity].append(relative)

            if layer == "wiki" and relative.startswith("wiki/concepts/"):
                missing_fields = sorted(field for field in CONCEPT_REQUIRED if field not in document.frontmatter)
                missing_sections = [section for section in CONCEPT_SECTIONS if section not in text]
                source_links = SOURCE_LINK_RE.findall(text)
                anchored = [f"{target}#^{anchor}" for target, anchor in source_links if anchor]
                if anchored and not missing_sections:
                    classification = "STRUCTURE_ONLY"
                elif anchored:
                    classification = "EVIDENCE_RESTORABLE"
                else:
                    classification = "INSUFFICIENT_EVIDENCE"
                if candidate_domain is None or relative.startswith(f"wiki/concepts/{candidate_domain}/"):
                    retrofit_candidates[classification].append(
                        {
                            "path": relative,
                            "missing_fields": missing_fields,
                            "missing_sections": missing_sections,
                            "anchored_source_refs": anchored,
                            "preimage_sha256": sha256_file(path),
                        }
                    )

            if layer == "maps":
                issues = []
                if not document.frontmatter:
                    issues.append("missing-frontmatter")
                if document.frontmatter.get("contract_version") != contract_version:
                    issues.append("contract-version-drift")
                if issues:
                    map_debt.append({"path": relative, "issues": issues})

            if layer == "system":
                duplicate_daily = text.count("## Daily Knowledge Loop Snapshot")
                if duplicate_daily > 1:
                    system_debt.append(
                        {"path": relative, "issue": "duplicate-machine-section", "count": duplicate_daily}
                    )

    duplicate_hashes = {key: value for key, value in source_hashes.items() if len(value) > 1}
    identity_threads = {key: value for key, value in source_identities.items() if len(value) > 1}
    live_template = vault_root / "system" / "templates" / "template-concept-gold-standard.md"
    template_state = {
        "path": _relative(live_template, vault_root) if live_template.is_file() else "system/templates/template-concept-gold-standard.md",
        "exists": live_template.is_file(),
        "sha256_normalized": normalized_text_sha256(live_template) if live_template.is_file() else None,
    }

    return {
        "status": "INVENTORIED",
        "generated_at": iso_z(),
        "vault_fingerprint": vault_fingerprint,
        "contract_version": contract_version,
        "scope": ["maps/**/*.md", "sources/**/*.md", "system/**/*.md", "wiki/**/*.md"],
        "candidate_domain": candidate_domain,
        "counts": {layer: len(files) for layer, files in files_by_layer.items()},
        "version_counts": {layer: dict(counts) for layer, counts in version_counts.items()},
        "missing_frontmatter": {
            layer: {"count": len(paths), "sample": paths[:limit]} for layer, paths in missing_frontmatter.items()
        },
        "unresolved_template_tokens": {
            layer: {"count": len(paths), "sample": paths[:limit]} for layer, paths in unresolved_tokens.items()
        },
        "sources": {
            "provenance_debt_count": len(source_debt),
            "provenance_debt_sample": source_debt[:limit],
            "duplicate_hash_group_count": len(duplicate_hashes),
            "duplicate_hash_sample": dict(list(duplicate_hashes.items())[:limit]),
            "invalid_hash_count": len(invalid_hashes),
            "invalid_hash_sample": invalid_hashes[:limit],
            "identity_thread_count": len(identity_threads),
            "identity_thread_sample": dict(list(identity_threads.items())[:limit]),
        },
        "wiki": {
            "retrofit_counts": {key: len(value) for key, value in retrofit_candidates.items()},
            "retrofit_candidates": {key: value[:limit] for key, value in retrofit_candidates.items()},
        },
        "maps": {"debt_count": len(map_debt), "debt_sample": map_debt[:limit]},
        "system": {
            "debt_count": len(system_debt),
            "debt_sample": system_debt[:limit],
            "active_concept_template": template_state,
            "excluded_artifacts": {
                "count": len(excluded_system_artifacts),
                "sample": excluded_system_artifacts[:limit],
                "policy": list(SYSTEM_ARTIFACT_PREFIXES),
                "reason": "runtime, contract, template, script, and operator-doc artifacts are not governed knowledge notes",
            },
        },
        "side_effect_count": 0,
    }
