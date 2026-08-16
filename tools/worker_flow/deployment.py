from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .utils import (
    atomic_write_bytes,
    canonical_json_sha256,
    normalize_relative_path,
    read_json,
    resolve_within,
    sha256_bytes,
    sha256_file,
)


@dataclass(frozen=True)
class SystemBundleEntry:
    source_relative_path: str
    target_relative_path: str
    source_sha256: str
    expected_preimage_sha256: str | None

    def to_dict(self) -> dict[str, str | None]:
        return asdict(self)


def load_system_bundle(repo_root: Path, contract_version: str) -> dict[str, Any]:
    bundle = read_json(repo_root / "contracts" / "system-bundle.json")
    if bundle.get("contract_version") != contract_version:
        raise ValueError("system bundle contract version mismatch")
    entries = bundle.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ValueError("system bundle has no entries")

    seen_sources: set[str] = set()
    seen_targets: set[str] = set()
    for raw in entries:
        if not isinstance(raw, dict):
            raise ValueError("system bundle entry must be an object")
        source = normalize_relative_path(str(raw.get("source") or ""))
        target = normalize_relative_path(str(raw.get("target") or ""))
        if not target.startswith("system/") or target.startswith("system/runs/"):
            raise ValueError(f"system bundle target is outside the deployable system surface: {target}")
        if source in seen_sources or target in seen_targets:
            raise ValueError(f"duplicate system bundle source or target: {source} -> {target}")
        source_path = resolve_within(repo_root, source)
        if not source_path.is_file():
            raise FileNotFoundError(f"system bundle source is missing: {source}")
        seen_sources.add(source)
        seen_targets.add(target)
    return bundle


def system_bundle_identity(repo_root: Path, contract_version: str) -> tuple[str, str]:
    bundle = load_system_bundle(repo_root, contract_version)
    files = []
    for raw in bundle["entries"]:
        source_relative = normalize_relative_path(raw["source"])
        target_relative = normalize_relative_path(raw["target"])
        files.append(
            {
                "source_relative_path": source_relative,
                "target_relative_path": target_relative,
                "source_sha256": sha256_file(resolve_within(repo_root, source_relative)),
            }
        )
    bundle_hash = canonical_json_sha256(
        {
            "bundle_id": bundle["bundle_id"],
            "contract_version": contract_version,
            "files": files,
        }
    )
    return bundle_hash, str(bundle["bundle_id"])


def plan_system_bundle(
    repo_root: Path,
    vault_root: Path,
    contract_version: str,
) -> tuple[list[SystemBundleEntry], str, str, bytes]:
    bundle = load_system_bundle(repo_root, contract_version)
    entries: list[SystemBundleEntry] = []
    for raw in bundle["entries"]:
        source_relative = normalize_relative_path(raw["source"])
        target_relative = normalize_relative_path(raw["target"])
        source_path = resolve_within(repo_root, source_relative)
        target_path = resolve_within(vault_root, target_relative)
        entries.append(
            SystemBundleEntry(
                source_relative,
                target_relative,
                sha256_file(source_path),
                sha256_file(target_path) if target_path.is_file() else None,
            )
        )

    bundle_hash, bundle_id = system_bundle_identity(repo_root, contract_version)
    deployment_manifest = {
        "schema_version": "1.0",
        "bundle_id": bundle_id,
        "contract_version": contract_version,
        "bundle_hash": bundle_hash,
        "files": [
            {
                "source_relative_path": entry.source_relative_path,
                "target_relative_path": entry.target_relative_path,
                "source_sha256": entry.source_sha256,
            }
            for entry in entries
        ],
    }
    deployment_bytes = (
        json.dumps(deployment_manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    deployment_target = "system/contracts/v8.1/deployment-manifest.json"
    target = resolve_within(vault_root, deployment_target)
    entries.append(
        SystemBundleEntry(
            "<generated>",
            deployment_target,
            sha256_bytes(deployment_bytes),
            sha256_file(target) if target.is_file() else None,
        )
    )
    return entries, bundle_hash, bundle_id, deployment_bytes


def stage_system_bundle(
    repo_root: Path,
    vault_root: Path,
    staging_root: Path,
    contract_version: str,
) -> tuple[list[SystemBundleEntry], str, str]:
    entries, bundle_hash, bundle_id, deployment_bytes = plan_system_bundle(
        repo_root, vault_root, contract_version
    )
    for entry in entries:
        if entry.source_relative_path == "<generated>":
            content = deployment_bytes
        else:
            content = resolve_within(repo_root, entry.source_relative_path).read_bytes()
        staged_path = resolve_within(staging_root, entry.target_relative_path)
        atomic_write_bytes(staged_path, content)
    return entries, bundle_hash, bundle_id


def verify_staged_system_bundle(
    repo_root: Path,
    vault_root: Path,
    staging_root: Path,
    entries: list[dict[str, Any]],
    contract_version: str,
    verify_target_preimages: bool = True,
) -> tuple[bool, list[dict[str, str]]]:
    evidence: list[dict[str, str]] = []
    expected_entries, _, _, _ = plan_system_bundle(repo_root, vault_root, contract_version)
    expected_payload = [entry.to_dict() for entry in expected_entries]
    if verify_target_preimages:
        manifest_exact = entries == expected_payload
    else:
        identity_fields = (
            "source_relative_path",
            "target_relative_path",
            "source_sha256",
        )
        manifest_exact = [
            {key: item.get(key) for key in identity_fields} for item in entries
        ] == [
            {key: item.get(key) for key in identity_fields} for item in expected_payload
        ]
    evidence.append(
        {
            "check": "contracted-entry-set"
            if verify_target_preimages
            else "contracted-entry-identity",
            "path": "contracts/system-bundle.json",
            "status": "PASS" if manifest_exact else "FAIL",
        }
    )
    if not manifest_exact:
        return False, evidence

    passed = manifest_exact
    for entry in expected_payload:
        target = normalize_relative_path(entry["target_relative_path"])
        if not target.startswith("system/") or target.startswith("system/runs/"):
            evidence.append({"check": "target-boundary", "path": target, "status": "FAIL"})
            return False, evidence
        staged = resolve_within(staging_root, target)
        expected = str(entry["source_sha256"])
        observed = sha256_file(staged) if staged.is_file() else "missing"
        status = "PASS" if observed == expected else "FAIL"
        evidence.append({"check": "staged-hash", "path": target, "status": status})
        passed = passed and status == "PASS"

        source = str(entry["source_relative_path"])
        if source != "<generated>":
            repository_source = resolve_within(repo_root, source)
            source_observed = sha256_file(repository_source) if repository_source.is_file() else "missing"
            source_status = "PASS" if source_observed == expected else "FAIL"
            evidence.append({"check": "repository-preimage", "path": source, "status": source_status})
            passed = passed and source_status == "PASS"
    return passed, evidence
