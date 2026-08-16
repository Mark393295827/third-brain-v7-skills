from __future__ import annotations

import json
import os
import getpass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .contracts import ContractBundle
from .deployment import stage_system_bundle, system_bundle_identity, verify_staged_system_bundle
from .freshness import evaluate_freshness, scan_freshness
from .frontmatter import first_heading, parse_markdown
from .governance import ANCHOR_RE, WIKILINK_RE, Finding, GovernanceReport, validate_concept, validate_source
from .graph import GraphDelta, plan_graph_delta, render_graph_target
from .ingest import SourceCandidate, stage_source
from .inventory import build_inventory, inventory_debt_regressions, inventory_debt_signature
from .locking import integration_owned
from .schema import validate_schema
from .state import RunStore
from .transaction import PreimageConflict, TransactionManager, WriteOperation
from .utils import (
    atomic_write_json,
    atomic_write_bytes,
    atomic_write_text,
    canonical_json_sha256,
    iso_z,
    normalize_relative_path,
    read_json,
    resolve_within,
    sha256_bytes,
    sha256_file,
    slugify,
    unique_destination,
)
from .wikilinks import resolve_note_target


class WorkflowError(RuntimeError):
    pass


class WorkerFlowRuntime:
    """Host-owned staged runtime for the V8.1 Obsidian knowledge workflow."""

    def __init__(self, vault_root: Path | str, repo_root: Path | str | None = None):
        self.vault_root = Path(vault_root).resolve()
        if not self.vault_root.is_dir():
            raise FileNotFoundError(f"vault root does not exist: {self.vault_root}")
        self.contracts = ContractBundle.load(Path(repo_root).resolve() if repo_root else None)
        self.vault_fingerprint = self.contracts.vault_fingerprint(self.vault_root)

    @property
    def clipping_root(self) -> Path:
        return self.vault_root / self.contracts.paths["clippings"]

    @property
    def idempotency_root(self) -> Path:
        return self.vault_root / self.contracts.paths["runs"] / "idempotency"

    def _idempotency_key(self, clipping_hash: str) -> str:
        payload = f"ingest|{clipping_hash}|{self.contracts.version}"
        return sha256_bytes(payload.encode("utf-8"))

    def _idempotency_path(self, key: str) -> Path:
        return self.idempotency_root / f"{key}.json"

    def _archive_pending_index(self) -> dict[str, str]:
        pending: dict[str, str] = {}
        runs_root = self.vault_root / self.contracts.paths["runs"]
        if not runs_root.is_dir():
            return pending
        for manifest_path in sorted(runs_root.glob("*/run-*/manifest.json")):
            try:
                manifest = read_json(manifest_path)
            except (OSError, ValueError, json.JSONDecodeError):
                continue
            if manifest.get("mode") != "ingest" or manifest.get("status") != "ARCHIVE_PENDING":
                continue
            key = str(manifest.get("idempotency_key") or "")
            run_id = str(manifest.get("run_id") or "")
            if key and run_id:
                pending[key] = run_id
        return pending

    def _receipt_drift(self, receipt_path: Path) -> list[dict[str, str]]:
        receipt = read_json(receipt_path)
        drift: list[dict[str, str]] = []
        writes = receipt.get("writes") if isinstance(receipt.get("writes"), list) else []
        mode = str(receipt.get("mode") or "ingest")
        for write in writes:
            if not isinstance(write, dict) or not write.get("relative_path") or not write.get("postimage_sha256"):
                continue
            kind = str(write.get("kind") or "")
            if mode in {"ingest", "local-ingest"} and kind != "source":
                continue
            if mode == "retrofit":
                continue
            relative = normalize_relative_path(str(write["relative_path"]))
            target = resolve_within(self.vault_root, relative)
            observed = sha256_file(target) if target.is_file() else "missing"
            expected = str(write["postimage_sha256"])
            if observed != expected:
                drift.append({"path": relative, "expected": expected, "observed": observed})
        source_evidence = receipt.get("source_evidence")
        if mode in {"ingest", "local-ingest", "retrofit"} and isinstance(source_evidence, dict):
            if source_evidence.get("path") and source_evidence.get("sha256"):
                relative = normalize_relative_path(str(source_evidence["path"]))
                target = resolve_within(self.vault_root, relative)
                observed = sha256_file(target) if target.is_file() else "missing"
                expected = str(source_evidence["sha256"])
                if observed != expected and not any(item["path"] == relative for item in drift):
                    drift.append({"path": relative, "expected": expected, "observed": observed})
        return drift

    def _receipt_validity(
        self,
        receipt_path: Path,
        key: str,
        expected_mode: str | None = None,
        expected_input_sha256: str | None = None,
        expected_source_hash: str | None = None,
        expected_source_relative: str | None = None,
        expected_input_bytes: bytes | None = None,
    ) -> tuple[bool, str, list[dict[str, str]]]:
        try:
            receipt = read_json(receipt_path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            return False, f"unreadable idempotency receipt: {exc}", []
        if receipt.get("idempotency_key") != key:
            return False, "idempotency key mismatch", []
        if receipt.get("contract_version") != self.contracts.version:
            return False, "receipt contract version mismatch", []
        if receipt.get("vault_fingerprint") != self.vault_fingerprint:
            return False, "receipt vault fingerprint mismatch", []
        if not isinstance(receipt.get("run_id"), str) or not receipt.get("run_id"):
            return False, "receipt has no run identity", []
        if receipt.get("status") not in {"COMMITTED", "ARCHIVED"}:
            return False, "receipt is not terminal", []
        writes = receipt.get("writes")
        if not isinstance(writes, list) or not writes:
            return False, "terminal receipt has no canonical writes", []
        for index, write in enumerate(writes):
            if not isinstance(write, dict):
                return False, f"terminal receipt write {index} is not an object", []
            if not all(write.get(field) for field in ("relative_path", "postimage_sha256", "kind")):
                return False, f"terminal receipt write {index} is incomplete", []
            try:
                normalize_relative_path(str(write["relative_path"]))
            except ValueError as exc:
                return False, f"terminal receipt write {index} has unsafe path: {exc}", []
            digest = str(write["postimage_sha256"])
            if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest.lower()):
                return False, f"terminal receipt write {index} has invalid postimage hash", []
        mode_value = receipt.get("mode")
        if not isinstance(mode_value, str) or mode_value not in {
            "ingest",
            "local-ingest",
            "retrofit",
            "system-bundle",
        }:
            return False, "receipt mode is missing or unsupported", []
        mode = mode_value
        if expected_mode is not None and mode != expected_mode:
            return False, f"receipt mode mismatch: expected {expected_mode}, observed {mode}", []
        if expected_input_sha256 is not None and receipt.get("input_sha256") != expected_input_sha256:
            return False, "receipt input hash mismatch", []
        if mode == "ingest":
            if receipt.get("status") != "ARCHIVED" or receipt.get("archive_error"):
                return False, "ingest receipt is not archive-complete", []
            try:
                archive_relative = normalize_relative_path(str(receipt.get("archive") or ""))
                archive_path = resolve_within(self.vault_root, archive_relative)
            except ValueError as exc:
                return False, f"ingest archive path is invalid: {exc}", []
            if not archive_relative.startswith(
                normalize_relative_path(self.contracts.paths["clippings_archive"]) + "/"
            ):
                return False, "ingest receipt archive is outside the archive root", []
            if not archive_path.is_file() or sha256_file(archive_path) != receipt.get("input_sha256"):
                return False, "ingest archive evidence is missing or drifted", []
        kinds = [str(write["kind"]) for write in writes]
        if mode == "system-bundle":
            if any(kind != "system" for kind in kinds):
                return False, "system receipt contains a non-system write kind", []
            if any(
                not normalize_relative_path(str(write["relative_path"])).startswith("system/")
                for write in writes
            ):
                return False, "system receipt contains a write outside system/", []
        if mode in {"ingest", "local-ingest", "retrofit"}:
            if sorted(kinds) != ["concept", "map", "source"]:
                return False, "knowledge receipt must contain exactly one source, concept, and map write", []
            source_evidence = receipt.get("source_evidence")
            if not isinstance(source_evidence, dict) or not all(
                source_evidence.get(field)
                for field in ("path", "sha256", "source_hash", "source_id")
            ):
                return False, "terminal receipt has no bound source evidence", []
            source_relative = normalize_relative_path(str(source_evidence["path"]))
            if not source_relative.startswith("sources/") or not source_relative.endswith(".md"):
                return False, "terminal receipt source evidence is outside sources/", []
            if expected_source_relative is not None and source_relative != normalize_relative_path(
                expected_source_relative
            ):
                return False, "receipt source path does not match the run manifest", []
            source_write = next(write for write in writes if write["kind"] == "source")
            concept_write = next(write for write in writes if write["kind"] == "concept")
            map_write = next(write for write in writes if write["kind"] == "map")
            if (
                normalize_relative_path(str(source_write["relative_path"])) != source_relative
                or source_write["postimage_sha256"] != source_evidence["sha256"]
            ):
                return False, "source evidence does not match the source write", []
            if not normalize_relative_path(str(concept_write["relative_path"])).startswith(
                "wiki/concepts/"
            ):
                return False, "concept write is outside wiki/concepts/", []
            if not normalize_relative_path(str(map_write["relative_path"])).startswith("maps/"):
                return False, "map write is outside maps/", []
            if len({str(write["relative_path"]) for write in writes}) != len(writes):
                return False, "knowledge receipt contains duplicate write paths", []
            if expected_source_hash is not None and source_evidence["source_hash"] != expected_source_hash:
                return False, "receipt source content hash mismatch", []
            source_path = resolve_within(self.vault_root, source_relative)
            if not source_path.is_file():
                return False, "receipt source evidence is missing", []
            source_document = parse_markdown(
                source_path.read_text(encoding="utf-8", errors="replace")
            )
            declared_source_id = str(source_document.frontmatter.get("source_id") or "")
            if mode in {"ingest", "local-ingest"} and declared_source_id != source_evidence["source_id"]:
                return False, "receipt source_id does not match the canonical source", []
            if mode == "retrofit" and declared_source_id and declared_source_id != source_evidence["source_id"]:
                return False, "retrofit source_id conflicts with the canonical source", []
            if mode in {"ingest", "local-ingest"}:
                if source_evidence["source_hash"] != receipt.get("input_sha256"):
                    return False, "receipt source hash does not match its immutable input", []
                declared_hash = str(source_document.frontmatter.get("hash") or "")
                if declared_hash != f"sha256:{source_evidence['source_hash']}":
                    return False, "canonical source frontmatter hash does not match the receipt", []
                if expected_input_bytes is not None:
                    source_report = validate_source(
                        source_relative,
                        source_path.read_text(encoding="utf-8", errors="replace"),
                        expected_input_bytes,
                        self.contracts.version,
                        schema=self.contracts.schema("source"),
                    )
                    if not source_report.passed:
                        return False, "canonical source does not preserve the expected input", []
            elif source_evidence["source_hash"] != source_evidence["sha256"]:
                return False, "retrofit source hash does not match the preserved source bytes", []
        try:
            run_store = RunStore.find(self.vault_root, str(receipt["run_id"]))
            run_receipt_path = run_store.run_dir / "receipt.json"
            if not run_receipt_path.is_file() or read_json(run_receipt_path) != receipt:
                return False, "idempotency receipt does not match its canonical run receipt", []
            run_manifest = read_json(run_store.manifest_path)
            if (
                run_manifest.get("idempotency_key") != key
                or run_manifest.get("final_receipt")
                != run_receipt_path.relative_to(self.vault_root).as_posix()
                or run_manifest.get("canonical_checkpoint")
                != receipt.get("canonical_checkpoint")
                or run_manifest.get("canonical_checkpoint_sha256")
                != receipt.get("canonical_checkpoint_sha256")
            ):
                return False, "run manifest does not bind the terminal receipt", []
            checkpoint_relative = str(receipt.get("canonical_checkpoint") or "")
            checkpoint_path = resolve_within(self.vault_root, checkpoint_relative)
            checkpoint_path.relative_to(run_store.run_dir)
            if (
                not receipt.get("canonical_checkpoint_sha256")
                or sha256_file(checkpoint_path) != receipt.get("canonical_checkpoint_sha256")
            ):
                return False, "canonical checkpoint hash does not match the terminal receipt", []
            checkpoint = read_json(checkpoint_path)
            if (
                checkpoint.get("run_id") != receipt["run_id"]
                or checkpoint.get("state") != "CANONICAL_COMMITTED"
                or checkpoint.get("idempotency_key") != key
                or checkpoint.get("writes") != writes
                or checkpoint.get("commit_approval") != receipt.get("commit_approval")
                or checkpoint.get("commit_intent") != receipt.get("commit_intent")
            ):
                return False, "canonical checkpoint does not bind the terminal writes", []
            if mode == "ingest":
                repair_evidence = receipt.get("archive_repair_approval")
                if not isinstance(repair_evidence, dict) or not all(
                    repair_evidence.get(field) for field in ("path", "sha256")
                ):
                    return False, "ingest receipt has no archive-only approval evidence", []
                repair_path = resolve_within(self.vault_root, str(repair_evidence["path"]))
                repair_path.relative_to(run_store.run_dir)
                if not repair_path.is_file() or sha256_file(repair_path) != repair_evidence["sha256"]:
                    return False, "archive-only approval evidence is missing or changed", []
                repair_approval = read_json(repair_path)
                if (
                    repair_approval.get("run_id") != receipt["run_id"]
                    or not repair_approval.get("actor")
                    or not repair_approval.get("approved_at")
                    or repair_approval.get("action") != "archive-only"
                    or repair_approval.get("vault_fingerprint") != self.vault_fingerprint
                    or repair_approval.get("contract_version") != self.contracts.version
                    or repair_approval.get("idempotency_key") != key
                    or repair_approval.get("archive_target") != receipt.get("archive")
                    or repair_approval.get("canonical_checkpoint") != checkpoint_relative
                    or repair_approval.get("canonical_checkpoint_sha256")
                    != receipt.get("canonical_checkpoint_sha256")
                    or repair_approval.get("clipping") != run_manifest.get("clipping")
                    or run_manifest.get("archive_target") != receipt.get("archive")
                ):
                    return False, "archive-only approval does not bind the terminal archive", []
        except (FileNotFoundError, KeyError, OSError, TypeError, ValueError, json.JSONDecodeError):
            return False, "terminal receipt provenance chain is missing or invalid", []
        drift = self._receipt_drift(receipt_path)
        if drift:
            return False, "canonical outputs drifted", drift
        return True, "verified terminal receipt", []

    def _resolve_clipping(self, value: Path | str) -> Path:
        candidate = Path(value)
        if not candidate.is_absolute():
            candidate = self.clipping_root / candidate
        resolved = candidate.resolve()
        try:
            relative = resolved.relative_to(self.clipping_root.resolve())
        except ValueError as exc:
            raise ValueError("clipping must be inside the configured Clippings directory") from exc
        if relative.parts and relative.parts[0].casefold() == "archive":
            raise ValueError("archived clipping is not eligible input")
        if not resolved.is_file() or resolved.suffix.lower() != ".md":
            raise FileNotFoundError(f"clipping does not exist: {resolved}")
        return resolved

    @staticmethod
    def _manifest_receipt_expectations(
        manifest: dict[str, Any]
    ) -> tuple[str, str, str | None]:
        mode = str(manifest.get("mode") or "ingest")
        if mode == "ingest":
            return mode, str(manifest["clipping"]["sha256"]), str(manifest["source"]["source_hash"])
        if mode == "local-ingest":
            return mode, str(manifest["input"]["sha256"]), str(manifest["source"]["source_hash"])
        if mode == "retrofit":
            return (
                mode,
                str(manifest["original_concept"]["preimage_sha256"]),
                str(manifest["source"]["source_hash"]),
            )
        if mode == "system-bundle":
            return mode, str(manifest["bundle_hash"]), None
        raise WorkflowError(f"unsupported run mode: {mode}")

    def _existing_idempotency_gate(
        self, store: RunStore, manifest: dict[str, Any]
    ) -> dict[str, Any] | None:
        key = str(manifest.get("idempotency_key") or "")
        if not key:
            return {
                "status": "BLOCKED_DEPENDENCY",
                "run_id": store.run_id,
                "error": "run manifest has no idempotency key",
            }
        receipt_path = self._idempotency_path(key)
        if not receipt_path.is_file():
            return None
        mode, input_sha256, source_hash = self._manifest_receipt_expectations(manifest)
        valid, reason, drift = self._receipt_validity(
            receipt_path,
            key,
            expected_mode=mode,
            expected_input_sha256=input_sha256,
            expected_source_hash=source_hash,
            expected_source_relative=(
                str(manifest["source"]["canonical_relative_path"])
                if mode != "system-bundle"
                else None
            ),
        )
        if not valid:
            store.transition(
                "BLOCKED_DEPENDENCY",
                "repair_invalid_idempotency_receipt",
                last_error=reason,
            )
            return {
                "status": "BLOCKED_DEPENDENCY",
                "run_id": store.run_id,
                "error": reason,
                "drift": drift,
            }
        store.transition(
            "NO_OP",
            "stop",
            evidence=[receipt_path.relative_to(self.vault_root).as_posix()],
            last_error=None,
        )
        return {
            "status": "NO_OP",
            "run_id": store.run_id,
            "reason": "an equivalent verified transaction already owns the idempotency key",
            "idempotency_receipt": receipt_path.relative_to(self.vault_root).as_posix(),
            "side_effect_count": 0,
        }

    def _resolve_repo_input(self, value: Path | str) -> tuple[Path, str]:
        candidate = Path(value)
        if candidate.is_absolute():
            resolved = candidate.resolve()
            try:
                relative = resolved.relative_to(self.contracts.repo_root)
            except ValueError as exc:
                raise ValueError("local input must be inside the repository") from exc
        else:
            relative_value = normalize_relative_path(candidate)
            resolved = resolve_within(self.contracts.repo_root, relative_value)
            relative = resolved.relative_to(self.contracts.repo_root)
        if not resolved.is_file() or resolved.suffix.lower() != ".md":
            raise FileNotFoundError(f"local Markdown input does not exist: {resolved}")
        return resolved, relative.as_posix()

    def scan_queue(self) -> dict[str, Any]:
        eligible: list[dict[str, Any]] = []
        processed: list[dict[str, Any]] = []
        archive_pending = self._archive_pending_index()
        observed_pending_keys: set[str] = set()
        clipping_paths = (
            sorted(self.clipping_root.glob("*.md"), key=lambda item: item.name.casefold())
            if self.clipping_root.is_dir()
            else []
        )
        for path in clipping_paths:
            if path.name == "README.md" or path.name.startswith("[ERROR]_"):
                continue
            clipping_bytes = path.read_bytes()
            digest = sha256_bytes(clipping_bytes)
            item = {
                "path": path.relative_to(self.vault_root).as_posix(),
                "sha256": digest,
                "idempotency_key": self._idempotency_key(digest),
            }
            observed_pending_keys.add(item["idempotency_key"])
            receipt_path = self._idempotency_path(item["idempotency_key"])
            if receipt_path.is_file():
                valid, reason, drift = self._receipt_validity(
                    receipt_path,
                    item["idempotency_key"],
                    expected_mode="ingest",
                    expected_input_sha256=digest,
                    expected_source_hash=digest,
                    expected_input_bytes=clipping_bytes,
                )
                if valid:
                    repair_run_id = archive_pending.get(item["idempotency_key"])
                    if repair_run_id:
                        item["repair_run_id"] = repair_run_id
                        item["repair_action"] = "retry_archive_only"
                        item["receipt_issue"] = "terminal receipt exists but run finalization is pending"
                        eligible.append(item)
                    else:
                        processed.append(item)
                else:
                    item["receipt_issue"] = reason
                    if drift:
                        item["receipt_drift"] = json.dumps(drift, ensure_ascii=False, sort_keys=True)
                    repair_run_id = archive_pending.get(item["idempotency_key"])
                    if repair_run_id:
                        item["repair_run_id"] = repair_run_id
                        item["repair_action"] = "retry_archive_only"
                    eligible.append(item)
            else:
                repair_run_id = archive_pending.get(item["idempotency_key"])
                if repair_run_id:
                    item["repair_run_id"] = repair_run_id
                    item["repair_action"] = "retry_archive_only"
                eligible.append(item)
        for key, repair_run_id in sorted(archive_pending.items()):
            if key in observed_pending_keys:
                continue
            try:
                pending_store = RunStore.find(self.vault_root, repair_run_id)
                pending_manifest = read_json(pending_store.manifest_path)
                clipping = pending_manifest["clipping"]
                item = {
                    "path": normalize_relative_path(str(clipping["relative_path"])),
                    "sha256": str(clipping["sha256"]),
                    "idempotency_key": key,
                    "repair_run_id": repair_run_id,
                    "repair_action": "retry_archive_only",
                    "clipping_present": resolve_within(
                        self.vault_root, str(clipping["relative_path"])
                    ).is_file(),
                }
                archive_target = str(pending_manifest.get("archive_target") or "")
                if archive_target:
                    archive_relative = normalize_relative_path(archive_target)
                    item["archive_target"] = archive_relative
                    item["archive_present"] = resolve_within(
                        self.vault_root, archive_relative
                    ).is_file()
                eligible.append(item)
            except (FileNotFoundError, KeyError, OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
                eligible.append(
                    {
                        "path": "unknown",
                        "sha256": "unknown",
                        "idempotency_key": key,
                        "repair_run_id": repair_run_id,
                        "repair_action": "inspect_archive_pending_manifest",
                        "receipt_issue": str(exc),
                    }
                )
        return {
            "status": "ELIGIBLE" if eligible else "NO_OP",
            "eligible": eligible,
            "processed_duplicates": processed,
            "eligibility_checked_at": iso_z(),
            "side_effect_count": 0,
            "reason": (
                "eligible work found"
                if eligible
                else (
                    "fresh query found no unprocessed clipping"
                    if self.clipping_root.is_dir()
                    else "clippings directory does not exist"
                )
            ),
        }

    def _source_valid_as_of(self, source: SourceCandidate, today: date) -> date:
        try:
            observed = date.fromisoformat(source.source_date[:10])
        except (TypeError, ValueError):
            return today
        return observed if observed <= today else today

    def _concept_dates(
        self,
        tier: str,
        today: date,
        valid_as_of: date | None = None,
    ) -> tuple[str, str | None, str]:
        tiers = self.contracts.freshness_policy["tiers"]
        if tier not in tiers:
            raise ValueError(f"unknown freshness tier: {tier}")
        evidence_date = valid_as_of or today
        if tier == "snapshot":
            return evidence_date.isoformat(), None, "snapshot"
        next_review = min(today, evidence_date) + timedelta(days=int(tiers[tier]["review_days"]))
        freshness_status = "stale" if next_review < today else "due" if next_review == today else "current"
        return evidence_date.isoformat(), next_review.isoformat(), freshness_status

    def _source_manifest(self, source: SourceCandidate, store: RunStore) -> dict[str, Any]:
        staged_note = Path(source.staged_path) if source.staged_path else None
        existing_note = Path(source.existing_path) if source.existing_path else None
        governed_note = staged_note or existing_note
        return {
            "source_id": source.source_id,
            "source_identity": source.source_identity,
            "source_hash": source.source_hash,
            "source_title": source.source_title,
            "source_author": source.source_author,
            "source_date": source.source_date,
            "source_url": source.source_url,
            "canonical_relative_path": source.canonical_relative_path,
            "staged_relative_path": source.canonical_relative_path if source.staged_path else None,
            "staged_note_sha256": sha256_file(staged_note) if staged_note else None,
            "existing_relative_path": source.canonical_relative_path if source.existing_path else None,
            "canonical_preimage_sha256": sha256_file(existing_note) if existing_note else None,
            "governed_note_sha256": sha256_file(governed_note) if governed_note else None,
            "prior_snapshot_paths": list(source.prior_snapshot_paths),
            "anchors": list(source.anchors),
            "evidence_block_count": source.evidence_block_count,
            "metadata_unknowns": list(source.metadata_unknowns),
            "staging_root": store.run_dir.relative_to(self.vault_root).as_posix(),
        }

    def _source_note_path(self, store: RunStore, manifest: dict[str, Any]) -> Path:
        source = manifest["source"]
        if source["staged_relative_path"]:
            return resolve_within(store.run_dir / "staging", source["staged_relative_path"])
        return resolve_within(self.vault_root, source["existing_relative_path"])

    def _source_text(self, store: RunStore, manifest: dict[str, Any]) -> str:
        return self._source_note_path(store, manifest).read_text(encoding="utf-8", errors="replace")

    def _scaffold_concept(
        self,
        store: RunStore,
        source: SourceCandidate,
        concept_title: str,
        domain: str,
        concept_relative: str,
        moc_relative: str,
        freshness_tier: str,
        today: date,
    ) -> Path:
        if len(source.anchors) < 3:
            raise WorkflowError("source has fewer than 3 evidence blocks; concept promotion is unsupported")
        source_valid_as_of = self._source_valid_as_of(source, today)
        valid_as_of, next_review, freshness_status = self._concept_dates(
            freshness_tier, today, source_valid_as_of
        )
        template_path = self.contracts.repo_root / self.contracts.vault_contract["templates"]["concept"]["path"]
        content = template_path.read_text(encoding="utf-8")
        source_note = source.canonical_relative_path[:-3]
        moc_note = moc_relative[:-3]
        known = {
            "title": concept_title,
            "chinese_title": concept_title,
            "url": source.source_url,
            "author": source.source_author,
            "source_date": source.source_date,
            "domain": domain,
            "created": today.isoformat(),
            "updated": today.isoformat(),
            "evidence_level": "single-source",
            "freshness_tier": freshness_tier,
            "valid_as_of": valid_as_of,
            "last_verified": today.isoformat(),
            "next_review": next_review or "null",
            "source_id": source.source_id,
            "run_id": store.run_id,
            "source_note": source_note,
            "thesis_anchor": source.anchors[0],
            "evidence_anchor": source.anchors[1],
            "mechanism_anchor_1": source.anchors[0],
            "mechanism_anchor_2": source.anchors[1],
            "mechanism_anchor_3": source.anchors[2],
            "metric_anchor_1": source.anchors[0],
            "metric_anchor_2": source.anchors[1],
            "moc_path": moc_note,
        }
        for key, value in known.items():
            content = content.replace("{{" + key + "}}", value)
        content = content.replace("freshness_status: current", f"freshness_status: {freshness_status}")
        draft = resolve_within(store.run_dir / "staging", concept_relative)
        atomic_write_text(draft, content)
        return draft

    def prepare(
        self,
        clipping: Path | str,
        concept_title: str,
        domain: str,
        moc_relative_path: str,
        freshness_tier: str = "dynamic",
        approve_staging: bool = False,
    ) -> dict[str, Any]:
        if not approve_staging:
            raise PermissionError("staging writes require explicit host approval")
        if domain not in self.contracts.domains:
            raise ValueError(f"unsupported concept domain: {domain}")
        clipping_path = self._resolve_clipping(clipping)
        clipping_hash = sha256_file(clipping_path)
        key = self._idempotency_key(clipping_hash)
        prior_receipt = self._idempotency_path(key)
        if prior_receipt.is_file():
            valid, reason, drift = self._receipt_validity(
                prior_receipt,
                key,
                expected_mode="ingest",
                expected_input_sha256=clipping_hash,
                expected_source_hash=clipping_hash,
                expected_input_bytes=clipping_path.read_bytes(),
            )
            if not valid:
                return {
                    "status": "BLOCKED_DEPENDENCY",
                    "reason": f"an invalid clipping-ingest receipt occupies the idempotency key: {reason}",
                    "drift": drift,
                    "side_effect_count": 0,
                }
            return {
                "status": "NO_OP",
                "reason": "clipping content already has a verified receipt",
                "idempotency_receipt": prior_receipt.relative_to(self.vault_root).as_posix(),
                "side_effect_count": 0,
            }

        repair_run_id = self._archive_pending_index().get(key)
        if repair_run_id:
            return {
                "status": "BLOCKED_DEPENDENCY",
                "reason": "canonical knowledge writes are complete but clipping archival is still pending",
                "repair_run_id": repair_run_id,
                "repair_action": "retry_archive_only",
                "side_effect_count": 0,
            }

        moc_relative = normalize_relative_path(moc_relative_path)
        if not moc_relative.startswith("maps/") or not moc_relative.endswith(".md"):
            raise ValueError("moc_relative_path must be a Markdown file under maps/")
        store = RunStore.create(self.vault_root)
        store.transition("CLAIMED", "stage_source", vault_fingerprint=self.vault_fingerprint)
        source, source_text = stage_source(clipping_path, self.vault_root, store, self.contracts)
        source_report = validate_source(
            source.canonical_relative_path,
            source_text,
            clipping_path.read_bytes(),
            self.contracts.version,
            schema=self.contracts.schema("source"),
        )
        if not source_report.passed:
            receipt_path = store.run_dir / "receipts" / "source-governance.json"
            atomic_write_json(receipt_path, source_report.to_dict())
            state = store.transition(
                "INSUFFICIENT_EVIDENCE",
                "repair_or_review_source",
                evidence=[receipt_path.relative_to(self.vault_root).as_posix()],
                unknowns=list(source.metadata_unknowns),
                last_error="source governance failed",
            )
            return {"status": state["status"], "run_id": store.run_id, "governance": source_report.to_dict()}

        concept_relative = f"wiki/concepts/{domain}/{slugify(concept_title)}.md"
        concept_target = resolve_within(self.vault_root, concept_relative)
        if concept_target.exists():
            state = store.transition(
                "NEEDS_INPUT",
                "select_retrofit_or_merge_path",
                last_error=f"concept target already exists: {concept_relative}",
            )
            return {"status": state["status"], "run_id": store.run_id, "target": concept_relative}

        graph_delta = plan_graph_delta(self.vault_root, moc_relative, concept_relative, concept_title)
        today = datetime.now(timezone.utc).date()
        draft = self._scaffold_concept(
            store,
            source,
            concept_title,
            domain,
            concept_relative,
            moc_relative,
            freshness_tier,
            today,
        )
        source_manifest = self._source_manifest(source, store)
        manifest = {
            "schema_version": "1.0",
            "run_id": store.run_id,
            "mode": "ingest",
            "status": "STAGED",
            "contract_version": self.contracts.version,
            "vault_fingerprint": self.vault_fingerprint,
            "idempotency_key": key,
            "clipping": {
                "relative_path": clipping_path.relative_to(self.vault_root).as_posix(),
                "sha256": clipping_hash,
            },
            "source": source_manifest,
            "concept": {
                "title": concept_title,
                "domain": domain,
                "freshness_tier": freshness_tier,
                "target_relative_path": concept_relative,
                "staged_relative_path": concept_relative,
                "expected_preimage_sha256": None,
            },
            "graph": graph_delta.to_dict(),
            "permissions": {"staging": True, "canonical_commit": False},
        }
        atomic_write_json(store.manifest_path, manifest)
        context = {
            "run_id": store.run_id,
            "contract_version": self.contracts.version,
            "vault_fingerprint": self.vault_fingerprint,
            "source": source_manifest,
            "concept_target": concept_relative,
            "concept_draft": draft.relative_to(self.vault_root).as_posix(),
            "template": self.contracts.vault_contract["templates"]["concept"],
            "graph_target": moc_relative,
            "freshness_policy": {
                "tier": freshness_tier,
                "valid_as_of": self._source_valid_as_of(source, today).isoformat(),
                "next_review": self._concept_dates(
                    freshness_tier, today, self._source_valid_as_of(source, today)
                )[1],
            },
            "allowed_write_paths": [draft.relative_to(self.vault_root).as_posix()],
            "stop_rules": [
                "do not fabricate missing provenance or metrics",
                "leave no unresolved {{...}} token",
                "every factual claim needs a resolvable source block",
                "stop with INSUFFICIENT_EVIDENCE when the source cannot support the section",
            ],
        }
        context_path = store.run_dir / "context-manifest.json"
        atomic_write_json(context_path, context)
        task_path = store.run_dir / "semantic-task.md"
        atomic_write_text(
            task_path,
            "# Cognitive Worker Task\n\n"
            f"Edit only `{draft.relative_to(self.vault_root).as_posix()}`.\n\n"
            f"Use evidence from `{source.canonical_relative_path}` and anchors: {', '.join(source.anchors)}.\n\n"
            "Replace every remaining template token with source-supported content. Preserve locked frontmatter, temporal scope, source IDs, and exact locators. If evidence is insufficient, return a failure receipt instead of synthetic prose.\n",
        )
        store.transition(
            "STAGED",
            "semantic_author",
            evidence=[
                context_path.relative_to(self.vault_root).as_posix(),
                task_path.relative_to(self.vault_root).as_posix(),
            ],
            unknowns=list(source.metadata_unknowns),
        )
        return {
            "status": "STAGED",
            "run_id": store.run_id,
            "context_manifest": context_path.relative_to(self.vault_root).as_posix(),
            "semantic_task": task_path.relative_to(self.vault_root).as_posix(),
            "concept_draft": draft.relative_to(self.vault_root).as_posix(),
            "source": source_manifest,
        }

    def prepare_local(
        self,
        input_path: Path | str,
        concept_title: str,
        domain: str,
        moc_relative_path: str,
        freshness_tier: str = "stable",
        source_type: str = "local-synthesis",
        input_class: str = "internal-state",
        source_title: str | None = None,
        source_author: str = "",
        source_date: str = "unknown",
        approve_staging: bool = False,
    ) -> dict[str, Any]:
        """Stage a repository document as immutable evidence without clipping lifecycle effects."""

        if not approve_staging:
            raise PermissionError("local-source staging writes require explicit host approval")
        if domain not in self.contracts.domains:
            raise ValueError(f"unsupported concept domain: {domain}")
        local_input, repo_relative = self._resolve_repo_input(input_path)
        input_hash = sha256_file(local_input)
        concept_relative = f"wiki/concepts/{domain}/{slugify(concept_title)}.md"
        key = sha256_bytes(
            f"local-ingest|{repo_relative}|{input_hash}|{concept_relative}|{self.contracts.version}".encode("utf-8")
        )
        prior_receipt = self._idempotency_path(key)
        if prior_receipt.is_file():
            valid, reason, drift = self._receipt_validity(
                prior_receipt,
                key,
                expected_mode="local-ingest",
                expected_input_sha256=input_hash,
                expected_source_hash=input_hash,
                expected_input_bytes=local_input.read_bytes(),
            )
            if not valid:
                return {
                    "status": "BLOCKED_DEPENDENCY",
                    "reason": f"an invalid local-ingest receipt occupies the idempotency key: {reason}",
                    "drift": drift,
                    "side_effect_count": 0,
                }
            return {
                "status": "NO_OP",
                "reason": "this local document and concept target already have a verified receipt",
                "idempotency_receipt": prior_receipt.relative_to(self.vault_root).as_posix(),
                "side_effect_count": 0,
            }

        moc_relative = normalize_relative_path(moc_relative_path)
        if not moc_relative.startswith("maps/") or not moc_relative.endswith(".md"):
            raise ValueError("moc_relative_path must be a Markdown file under maps/")
        store = RunStore.create(self.vault_root)
        store.transition("CLAIMED", "stage_local_source", vault_fingerprint=self.vault_fingerprint)
        metadata_overrides = {
            "title": source_title or first_heading(local_input.read_text(encoding="utf-8", errors="replace")) or local_input.stem,
            "source_url": "",
            "author": source_author,
            "source_date": source_date,
        }
        source, source_text = stage_source(
            local_input,
            self.vault_root,
            store,
            self.contracts,
            source_type=source_type,
            input_class=input_class,
            evidence_level="single-source",
            trust_level="primary-source",
            metadata_overrides=metadata_overrides,
        )
        source_report = validate_source(
            source.canonical_relative_path,
            source_text,
            local_input.read_bytes(),
            self.contracts.version,
            schema=self.contracts.schema("source"),
        )
        if not source_report.passed or len(source.anchors) < 3:
            receipt_path = store.run_dir / "receipts" / "source-governance.json"
            atomic_write_json(receipt_path, source_report.to_dict())
            state = store.transition(
                "INSUFFICIENT_EVIDENCE",
                "repair_or_review_local_source",
                evidence=[receipt_path.relative_to(self.vault_root).as_posix()],
                unknowns=list(source.metadata_unknowns),
                last_error="local source governance failed or fewer than 3 evidence blocks",
            )
            return {"status": state["status"], "run_id": store.run_id, "governance": source_report.to_dict()}

        concept_target = resolve_within(self.vault_root, concept_relative)
        if concept_target.exists():
            state = store.transition(
                "NEEDS_INPUT",
                "select_retrofit_or_new_concept_target",
                last_error=f"concept target already exists: {concept_relative}",
            )
            return {"status": state["status"], "run_id": store.run_id, "target": concept_relative}

        graph_delta = plan_graph_delta(self.vault_root, moc_relative, concept_relative, concept_title)
        today = datetime.now(timezone.utc).date()
        draft = self._scaffold_concept(
            store,
            source,
            concept_title,
            domain,
            concept_relative,
            moc_relative,
            freshness_tier,
            today,
        )
        source_manifest = self._source_manifest(source, store)
        manifest = {
            "schema_version": "1.0",
            "run_id": store.run_id,
            "mode": "local-ingest",
            "status": "STAGED",
            "contract_version": self.contracts.version,
            "vault_fingerprint": self.vault_fingerprint,
            "idempotency_key": key,
            "input": {"repo_relative_path": repo_relative, "sha256": input_hash},
            "clipping": None,
            "source": source_manifest,
            "concept": {
                "title": concept_title,
                "domain": domain,
                "freshness_tier": freshness_tier,
                "target_relative_path": concept_relative,
                "staged_relative_path": concept_relative,
                "expected_preimage_sha256": None,
            },
            "graph": graph_delta.to_dict(),
            "permissions": {"staging": True, "canonical_commit": False},
        }
        atomic_write_json(store.manifest_path, manifest)
        context = {
            "run_id": store.run_id,
            "mode": "local-ingest",
            "contract_version": self.contracts.version,
            "vault_fingerprint": self.vault_fingerprint,
            "input": manifest["input"],
            "source": source_manifest,
            "concept_target": concept_relative,
            "concept_draft": draft.relative_to(self.vault_root).as_posix(),
            "template": self.contracts.vault_contract["templates"]["concept"],
            "graph_target": moc_relative,
            "allowed_write_paths": [draft.relative_to(self.vault_root).as_posix()],
            "stop_rules": [
                "treat the project document as evidence of the design, not proof of future reliability",
                "do not fabricate implementation results or production metrics",
                "leave no unresolved {{...}} token",
                "every design claim must resolve to a supplied source block",
            ],
        }
        context_path = store.run_dir / "context-manifest.json"
        atomic_write_json(context_path, context)
        task_path = store.run_dir / "semantic-task.md"
        atomic_write_text(
            task_path,
            "# Local Source Cognitive Task\n\n"
            f"Edit only `{draft.relative_to(self.vault_root).as_posix()}`.\n\n"
            f"Compile `{repo_relative}` through immutable source `{source.canonical_relative_path}` using anchors: "
            f"{', '.join(source.anchors)}. Preserve the distinction between planned architecture and verified runtime evidence.\n",
        )
        store.transition(
            "STAGED",
            "semantic_author",
            evidence=[context_path.relative_to(self.vault_root).as_posix(), task_path.relative_to(self.vault_root).as_posix()],
            unknowns=list(source.metadata_unknowns),
        )
        return {
            "status": "STAGED",
            "mode": "local-ingest",
            "run_id": store.run_id,
            "context_manifest": context_path.relative_to(self.vault_root).as_posix(),
            "semantic_task": task_path.relative_to(self.vault_root).as_posix(),
            "concept_draft": draft.relative_to(self.vault_root).as_posix(),
            "source": source_manifest,
        }

    def prepare_system_deployment(self, approve_staging: bool = False) -> dict[str, Any]:
        """Stage the deterministic V8.1 system control-plane bundle."""

        if not approve_staging:
            raise PermissionError("system deployment staging requires explicit host approval")
        self.contracts.verify_templates()
        baseline_inventory = build_inventory(
            self.vault_root,
            contract_version=self.contracts.version,
            vault_fingerprint=self.vault_fingerprint,
            limit=0,
        )
        baseline_debt = inventory_debt_signature(baseline_inventory)
        bundle_hash, bundle_id = system_bundle_identity(self.contracts.repo_root, self.contracts.version)
        key = sha256_bytes(f"system-deploy|{bundle_id}|{bundle_hash}|{self.contracts.version}".encode("utf-8"))
        prior_receipt = self._idempotency_path(key)
        if prior_receipt.is_file():
            valid, reason, drift = self._receipt_validity(
                prior_receipt, key, expected_mode="system-bundle", expected_input_sha256=bundle_hash
            )
            if not valid:
                return {
                    "status": "BLOCKED_DEPENDENCY",
                    "reason": f"an invalid system-bundle receipt occupies the idempotency key: {reason}",
                    "drift": drift,
                    "side_effect_count": 0,
                }
            return {
                "status": "NO_OP",
                "reason": "this exact V8.1 system bundle already has a verified receipt",
                "idempotency_receipt": prior_receipt.relative_to(self.vault_root).as_posix(),
                "side_effect_count": 0,
            }

        store = RunStore.create(self.vault_root)
        store.transition("CLAIMED", "stage_system_bundle", vault_fingerprint=self.vault_fingerprint)
        entries, staged_bundle_hash, staged_bundle_id = stage_system_bundle(
            self.contracts.repo_root,
            self.vault_root,
            store.run_dir / "staging",
            self.contracts.version,
        )
        if staged_bundle_hash != bundle_hash or staged_bundle_id != bundle_id:
            raise WorkflowError("system bundle identity changed during staging")
        manifest = {
            "schema_version": "1.0",
            "run_id": store.run_id,
            "mode": "system-bundle",
            "status": "STAGED",
            "contract_version": self.contracts.version,
            "vault_fingerprint": self.vault_fingerprint,
            "idempotency_key": key,
            "bundle_id": bundle_id,
            "bundle_hash": bundle_hash,
            "system_entries": [entry.to_dict() for entry in entries],
            "inventory_baseline": baseline_debt,
            "permissions": {"staging": True, "canonical_commit": False},
        }
        atomic_write_json(store.manifest_path, manifest)
        context = {
            "run_id": store.run_id,
            "mode": "system-bundle",
            "contract_version": self.contracts.version,
            "vault_fingerprint": self.vault_fingerprint,
            "bundle_id": bundle_id,
            "bundle_hash": bundle_hash,
            "inventory_baseline": baseline_debt,
            "allowed_write_paths": [
                (store.run_dir / "staging" / entry.target_relative_path).relative_to(self.vault_root).as_posix()
                for entry in entries
            ],
            "promotion_boundary": "single Integration Owner after deterministic hash verification",
        }
        context_path = store.run_dir / "context-manifest.json"
        atomic_write_json(context_path, context)
        store.transition(
            "STAGED",
            "governance",
            evidence=[context_path.relative_to(self.vault_root).as_posix()],
            unknowns=[],
        )
        return {
            "status": "STAGED",
            "mode": "system-bundle",
            "run_id": store.run_id,
            "bundle_id": bundle_id,
            "bundle_hash": bundle_hash,
            "file_count": len(entries),
            "context_manifest": context_path.relative_to(self.vault_root).as_posix(),
        }

    def prepare_system_bundle(self, approve_staging: bool = False) -> dict[str, Any]:
        """Compatibility name for the canonical V8.1 system deployment lane."""

        return self.prepare_system_deployment(approve_staging=approve_staging)

    def prepare_retrofit(
        self,
        concept_relative_path: str,
        moc_relative_path: str,
        freshness_tier: str = "stable",
        approve_staging: bool = False,
    ) -> dict[str, Any]:
        if not approve_staging:
            raise PermissionError("retrofit staging writes require explicit host approval")
        concept_relative = normalize_relative_path(concept_relative_path)
        parts = Path(concept_relative).parts
        if len(parts) < 4 or parts[0] != "wiki" or parts[1] != "concepts" or not concept_relative.endswith(".md"):
            raise ValueError("retrofit target must be under wiki/concepts/<domain>/")
        domain = parts[2]
        if domain not in self.contracts.domains:
            raise ValueError(f"unsupported concept domain: {domain}")
        concept_target = resolve_within(self.vault_root, concept_relative)
        if not concept_target.is_file():
            raise FileNotFoundError(f"retrofit target does not exist: {concept_relative}")
        moc_relative = normalize_relative_path(moc_relative_path)
        if not moc_relative.startswith("maps/") or not moc_relative.endswith(".md"):
            raise ValueError("moc_relative_path must be a Markdown file under maps/")

        original_text = concept_target.read_text(encoding="utf-8", errors="replace")
        preimage = sha256_file(concept_target)
        key = sha256_bytes(f"retrofit|{concept_relative}|{preimage}|{self.contracts.version}".encode("utf-8"))
        prior_receipt = self._idempotency_path(key)
        if prior_receipt.is_file():
            valid, reason, drift = self._receipt_validity(
                prior_receipt, key, expected_mode="retrofit", expected_input_sha256=preimage
            )
            if not valid:
                return {
                    "status": "BLOCKED_DEPENDENCY",
                    "reason": f"an invalid retrofit receipt occupies the idempotency key: {reason}",
                    "drift": drift,
                    "side_effect_count": 0,
                }
            return {
                "status": "NO_OP",
                "reason": "this exact concept preimage already has a verified retrofit receipt",
                "idempotency_receipt": prior_receipt.relative_to(self.vault_root).as_posix(),
                "side_effect_count": 0,
            }

        grouped: dict[Path, set[str]] = {}
        for target, anchor in WIKILINK_RE.findall(original_text):
            if not target.replace("\\", "/").startswith("sources/") or not anchor:
                continue
            resolved = resolve_note_target(self.vault_root, target)
            grouped.setdefault(resolved, set()).add(anchor)
        if not grouped:
            return {
                "status": "INSUFFICIENT_EVIDENCE",
                "reason": "concept has no resolvable anchored source reference",
                "side_effect_count": 0,
            }
        source_path, referenced_anchors = max(grouped.items(), key=lambda item: len(item[1]))
        source_text = source_path.read_text(encoding="utf-8", errors="replace")
        available_anchors = set(ANCHOR_RE.findall(source_text))
        verified_anchors = tuple(sorted(referenced_anchors & available_anchors))
        if len(verified_anchors) < 3:
            return {
                "status": "INSUFFICIENT_EVIDENCE",
                "reason": f"primary legacy source has only {len(verified_anchors)} resolvable referenced anchors",
                "side_effect_count": 0,
            }

        source_document = parse_markdown(source_text)
        source_relative = source_path.relative_to(self.vault_root).as_posix()
        source_hash = sha256_file(source_path)
        source_id = str(source_document.frontmatter.get("source_id") or f"legacy-src-{source_hash[:16]}")
        title = str(parse_markdown(original_text).frontmatter.get("title") or first_heading(original_text) or concept_target.stem)
        source = SourceCandidate(
            source_id=source_id,
            source_identity=str(
                source_document.frontmatter.get("source_identity")
                or source_document.frontmatter.get("source_url")
                or source_relative
            ),
            source_hash=source_hash,
            source_title=str(source_document.frontmatter.get("source_title") or source_document.frontmatter.get("title") or source_path.stem),
            source_author=str(source_document.frontmatter.get("source_author") or source_document.frontmatter.get("author") or ""),
            source_date=str(source_document.frontmatter.get("source_date") or source_document.frontmatter.get("date") or "unknown"),
            source_url=str(source_document.frontmatter.get("source_url") or source_document.frontmatter.get("url") or ""),
            canonical_relative_path=source_relative,
            staged_path=None,
            existing_path=str(source_path),
            prior_snapshot_paths=(),
            anchors=verified_anchors,
            evidence_block_count=len(verified_anchors),
            metadata_unknowns=(),
        )

        store = RunStore.create(self.vault_root)
        (store.run_dir / "inputs").mkdir()
        original_snapshot = store.run_dir / "inputs" / "original-concept.md"
        atomic_write_bytes(original_snapshot, concept_target.read_bytes())
        graph_delta = plan_graph_delta(self.vault_root, moc_relative, concept_relative, title)
        today = datetime.now(timezone.utc).date()
        draft = self._scaffold_concept(
            store,
            source,
            title,
            domain,
            concept_relative,
            moc_relative,
            freshness_tier,
            today,
        )
        source_manifest = self._source_manifest(source, store)
        manifest = {
            "schema_version": "1.0",
            "run_id": store.run_id,
            "mode": "retrofit",
            "status": "STAGED",
            "contract_version": self.contracts.version,
            "vault_fingerprint": self.vault_fingerprint,
            "idempotency_key": key,
            "clipping": None,
            "source": source_manifest,
            "source_preimage_sha256": source_hash,
            "original_concept": {
                "relative_path": concept_relative,
                "snapshot": original_snapshot.relative_to(self.vault_root).as_posix(),
                "preimage_sha256": preimage,
            },
            "concept": {
                "title": title,
                "domain": domain,
                "freshness_tier": freshness_tier,
                "target_relative_path": concept_relative,
                "staged_relative_path": concept_relative,
                "expected_preimage_sha256": preimage,
            },
            "graph": graph_delta.to_dict(),
            "permissions": {"staging": True, "canonical_commit": False},
        }
        atomic_write_json(store.manifest_path, manifest)
        context = {
            "run_id": store.run_id,
            "mode": "retrofit",
            "contract_version": self.contracts.version,
            "vault_fingerprint": self.vault_fingerprint,
            "original_concept": manifest["original_concept"],
            "source": source_manifest,
            "concept_target": concept_relative,
            "concept_draft": draft.relative_to(self.vault_root).as_posix(),
            "template": self.contracts.vault_contract["templates"]["concept"],
            "graph_target": moc_relative,
            "allowed_write_paths": [draft.relative_to(self.vault_root).as_posix()],
            "stop_rules": [
                "preserve every supported claim and append the prior timeline",
                "replace legacy source links with the resolved canonical monthly path",
                "do not invent a metric, source, date, author, or counterpoint",
                "leave no unresolved {{...}} token",
            ],
        }
        context_path = store.run_dir / "context-manifest.json"
        atomic_write_json(context_path, context)
        task_path = store.run_dir / "semantic-task.md"
        atomic_write_text(
            task_path,
            "# Gold-Standard Retrofit Task\n\n"
            f"Upgrade `{concept_relative}` by editing only `{draft.relative_to(self.vault_root).as_posix()}`.\n\n"
            f"Preserve the original snapshot at `{original_snapshot.relative_to(self.vault_root).as_posix()}`. "
            f"Use `{source_relative}` and these verified anchors: {', '.join(verified_anchors)}. "
            "Correct legacy source paths to the resolved monthly path. Do not fill unsupported template sections.\n",
        )
        store.transition(
            "STAGED",
            "semantic_author",
            evidence=[context_path.relative_to(self.vault_root).as_posix(), task_path.relative_to(self.vault_root).as_posix()],
            unknowns=[],
        )
        return {
            "status": "STAGED",
            "mode": "retrofit",
            "run_id": store.run_id,
            "context_manifest": context_path.relative_to(self.vault_root).as_posix(),
            "semantic_task": task_path.relative_to(self.vault_root).as_posix(),
            "concept_draft": draft.relative_to(self.vault_root).as_posix(),
            "source": source_manifest,
            "original_preimage_sha256": preimage,
        }

    def stage_candidate(
        self, run_id: str, candidate_path: Path | str, approve_staging: bool = False
    ) -> dict[str, Any]:
        if not approve_staging:
            raise PermissionError("candidate staging requires explicit host approval")
        candidate = Path(candidate_path).resolve()
        try:
            candidate.relative_to(self.contracts.repo_root)
        except ValueError as exc:
            raise ValueError("candidate must be inside the repository") from exc
        if not candidate.is_file() or candidate.suffix.lower() != ".md":
            raise FileNotFoundError(f"candidate Markdown does not exist: {candidate}")
        store = RunStore.find(self.vault_root, run_id)
        manifest = read_json(store.manifest_path)
        if manifest.get("mode") == "system-bundle":
            raise WorkflowError("system bundle runs do not accept semantic candidates")
        if manifest.get("status") not in {"STAGED", "AUTHORED", "VERIFY_FAILED"}:
            raise WorkflowError(f"candidate cannot be staged from state: {manifest.get('status')}")
        target = resolve_within(store.run_dir / "staging", manifest["concept"]["staged_relative_path"])
        atomic_write_bytes(target, candidate.read_bytes())
        store.transition(
            "AUTHORED",
            "governance",
            evidence=[{"candidate": str(candidate), "sha256": sha256_file(candidate)}],
        )
        return {
            "status": "AUTHORED",
            "run_id": run_id,
            "staged_candidate": target.relative_to(self.vault_root).as_posix(),
            "sha256": sha256_file(target),
        }

    def _worker_receipt_violations(
        self,
        receipt: dict[str, Any],
        run_id: str,
        expected_artifacts: list[dict[str, Any]] | None = None,
    ) -> list[str]:
        violations = validate_schema(receipt, self.contracts.schema("worker_receipt"))
        if receipt.get("run_id") != run_id:
            violations.append("$.run_id: does not match the active run")
        context = receipt.get("context_manifest")
        if not isinstance(context, dict):
            violations.append("$.context_manifest: must be an object")
        else:
            if context.get("run_id") != run_id:
                violations.append("$.context_manifest.run_id: does not match the active run")
            if context.get("contract_version") != self.contracts.version:
                violations.append("$.context_manifest.contract_version: contract drift")
            if context.get("vault_fingerprint") != self.vault_fingerprint:
                violations.append("$.context_manifest.vault_fingerprint: vault drift")
        artifacts = receipt.get("artifact")
        if isinstance(artifacts, list):
            if receipt.get("artifact_hash") != canonical_json_sha256(artifacts):
                violations.append("$.artifact_hash: does not bind the artifact array")
            if expected_artifacts is not None and artifacts != expected_artifacts:
                violations.append("$.artifact: does not match the verified promotion scope")
        decision = receipt.get("decision") if isinstance(receipt.get("decision"), dict) else {}
        if receipt.get("state") == "VERIFIED" and decision.get("promotion") != "ALLOW":
            violations.append("$.decision.promotion: VERIFIED receipt must ALLOW promotion")
        return violations

    def _assert_worker_receipt(
        self,
        receipt: dict[str, Any],
        run_id: str,
        expected_artifacts: list[dict[str, Any]] | None = None,
    ) -> None:
        violations = self._worker_receipt_violations(receipt, run_id, expected_artifacts)
        if violations:
            raise WorkflowError("worker receipt contract violation: " + "; ".join(violations))

    def _submit_system_deployment(self, store: RunStore, manifest: dict[str, Any]) -> dict[str, Any]:
        passed, evidence = verify_staged_system_bundle(
            self.contracts.repo_root,
            self.vault_root,
            store.run_dir / "staging",
            manifest["system_entries"],
            self.contracts.version,
        )
        try:
            current_hash, current_id = system_bundle_identity(self.contracts.repo_root, self.contracts.version)
            identity_ok = current_hash == manifest["bundle_hash"] and current_id == manifest["bundle_id"]
        except (FileNotFoundError, ValueError):
            identity_ok = False
        evidence.append(
            {
                "check": "bundle-identity",
                "path": "contracts/system-bundle.json",
                "status": "PASS" if identity_ok else "FAIL",
            }
        )
        passed = passed and identity_ok
        current_inventory = build_inventory(
            self.vault_root,
            contract_version=self.contracts.version,
            vault_fingerprint=self.vault_fingerprint,
            limit=0,
        )
        inventory_baseline_ok = manifest.get("inventory_baseline") == inventory_debt_signature(
            current_inventory
        )
        evidence.append(
            {
                "check": "inventory-baseline",
                "path": "maps|sources|system|wiki",
                "status": "PASS" if inventory_baseline_ok else "FAIL",
            }
        )
        passed = passed and inventory_baseline_ok
        artifacts = [
            {
                "path": str(entry["target_relative_path"]),
                "sha256": str(entry["source_sha256"]),
                "expected_preimage_sha256": entry.get("expected_preimage_sha256"),
            }
            for entry in manifest["system_entries"]
        ]
        state = "VERIFIED" if passed else "VERIFY_FAILED"
        receipt = {
            "task_id": f"{store.run_id}:system-governance",
            "run_id": store.run_id,
            "state": state,
            "context_manifest": read_json(store.run_dir / "context-manifest.json"),
            "artifact": artifacts,
            "artifact_hash": canonical_json_sha256(artifacts),
            "evidence": evidence,
            "decision": {"promotion": "ALLOW" if passed else "DENY"},
            "unknowns": [],
            "dependency": [f"{store.run_id}:system-stage"],
            "termination_reason": None if passed else "verify_failed",
            "next_action": "commit" if passed else "restage_system_bundle",
        }
        self._assert_worker_receipt(receipt, store.run_id, artifacts)
        receipt_path = store.run_dir / "receipts" / "governance.json"
        atomic_write_json(receipt_path, receipt)
        manifest["status"] = state
        manifest["governance_receipt"] = receipt_path.relative_to(self.vault_root).as_posix()
        atomic_write_json(store.manifest_path, manifest)
        store.transition(
            state,
            receipt["next_action"],
            evidence=[receipt_path.relative_to(self.vault_root).as_posix()],
            last_error=None if passed else "system bundle governance failed",
        )
        return {"status": state, "run_id": store.run_id, "evidence": evidence}

    def submit(self, run_id: str) -> dict[str, Any]:
        store = RunStore.find(self.vault_root, run_id)
        manifest = read_json(store.manifest_path)
        if manifest.get("contract_version") != self.contracts.version:
            raise WorkflowError("run contract is stale")
        if manifest.get("vault_fingerprint") != self.vault_fingerprint:
            raise WorkflowError("vault fingerprint changed")
        if manifest.get("mode") == "system-bundle":
            return self._submit_system_deployment(store, manifest)
        concept_path = resolve_within(store.run_dir / "staging", manifest["concept"]["staged_relative_path"])
        concept_text = concept_path.read_text(encoding="utf-8", errors="replace")
        source = manifest["source"]
        source_note_path = self._source_note_path(store, manifest)
        source_note_bytes = source_note_path.read_bytes()
        source_text = source_note_bytes.decode("utf-8", errors="replace")
        observed_source_note_hash = sha256_bytes(source_note_bytes)
        if observed_source_note_hash != source.get("governed_note_sha256"):
            report = GovernanceReport(
                False,
                (
                    Finding(
                        "source.preimage.changed",
                        "P0",
                        "source note changed after source governance",
                        source["canonical_relative_path"],
                    ),
                ),
                ("source-note-preimage",),
            )
        else:
            report = validate_concept(
                manifest["concept"]["target_relative_path"],
                concept_text,
                source["canonical_relative_path"],
                source_text,
                source["source_id"],
                manifest["concept"]["domain"],
                self.contracts.version,
                self.contracts.freshness_policy,
                vault_root=self.vault_root,
                schema=self.contracts.schema("concept"),
            )
        artifacts = [
            {
                "path": concept_path.relative_to(self.vault_root).as_posix(),
                "sha256": sha256_file(concept_path),
                "expected_preimage_sha256": manifest["concept"]["expected_preimage_sha256"],
            }
        ]
        receipt = {
            "task_id": f"{run_id}:governance",
            "run_id": run_id,
            "state": "VERIFIED" if report.passed else "VERIFY_FAILED",
            "context_manifest": read_json(store.run_dir / "context-manifest.json"),
            "artifact": artifacts,
            "artifact_hash": canonical_json_sha256(artifacts),
            "evidence": [{"check": name, "status": "PASS" if report.passed else "FAIL"} for name in report.checks],
            "decision": {"promotion": "ALLOW" if report.passed else "DENY", "report": report.to_dict()},
            "unknowns": [],
            "dependency": [f"{run_id}:source"],
            "termination_reason": None if report.passed else "verify_failed",
            "next_action": "commit" if report.passed else "repair_candidate",
        }
        self._assert_worker_receipt(receipt, run_id, artifacts)
        receipt_path = store.run_dir / "receipts" / "governance.json"
        atomic_write_json(receipt_path, receipt)
        manifest["status"] = receipt["state"]
        manifest["governance_receipt"] = receipt_path.relative_to(self.vault_root).as_posix()
        manifest["verified_artifact_sha256"] = sha256_file(concept_path) if report.passed else None
        atomic_write_json(store.manifest_path, manifest)
        store.transition(
            receipt["state"],
            receipt["next_action"],
            evidence=[receipt_path.relative_to(self.vault_root).as_posix()],
            last_error=None if report.passed else "concept governance failed",
        )
        return {"status": receipt["state"], "run_id": run_id, "governance": report.to_dict()}

    def _exclusive_idempotency_receipt(self, key: str, receipt: dict[str, Any]) -> Path:
        path = self._idempotency_path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = (json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
        flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
        try:
            descriptor = os.open(path, flags, 0o600)
        except FileExistsError:
            source_evidence = (
                receipt.get("source_evidence")
                if isinstance(receipt.get("source_evidence"), dict)
                else {}
            )
            valid, _, _ = self._receipt_validity(
                path,
                key,
                expected_mode=str(receipt.get("mode") or ""),
                expected_input_sha256=str(receipt.get("input_sha256") or ""),
                expected_source_hash=(
                    str(source_evidence.get("source_hash"))
                    if source_evidence.get("source_hash")
                    else None
                ),
            )
            if valid:
                return path
            raise WorkflowError(f"invalid existing idempotency receipt: {path}")
        try:
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
        except Exception:
            if path.exists():
                path.unlink()
            raise
        return path

    def _plan_archive_destination(self, clipping_relative: str, run_id: str) -> str:
        clipping = normalize_relative_path(clipping_relative)
        source = resolve_within(self.vault_root, clipping)
        archive_root = self.vault_root / self.contracts.paths["clippings_archive"]
        destination = unique_destination(archive_root / source.name, run_id[-8:])
        return destination.relative_to(self.vault_root).as_posix()

    def _archive(
        self,
        clipping_relative: str,
        run_id: str,
        destination_relative: str | None = None,
    ) -> str:
        source = resolve_within(self.vault_root, clipping_relative)
        if not source.is_file():
            raise FileNotFoundError(f"clipping disappeared before archive: {clipping_relative}")
        archive_root = self.vault_root / self.contracts.paths["clippings_archive"]
        archive_root.mkdir(parents=True, exist_ok=True)
        if destination_relative is None:
            destination = unique_destination(archive_root / source.name, run_id[-8:])
        else:
            destination_normalized = normalize_relative_path(destination_relative)
            destination = resolve_within(self.vault_root, destination_normalized)
            try:
                destination.relative_to(archive_root.resolve())
            except ValueError as exc:
                raise ValueError("archive destination is outside the configured archive root") from exc
            if destination.exists():
                raise FileExistsError(f"archive destination already exists: {destination_normalized}")
        os.replace(source, destination)
        return destination.relative_to(self.vault_root).as_posix()

    @staticmethod
    def _operation_scope(operations: list[WriteOperation]) -> list[dict[str, Any]]:
        return [
            {
                "relative_path": operation.relative_path,
                "kind": operation.kind,
                "expected_preimage_sha256": operation.expected_preimage_sha256,
                "postimage_sha256": sha256_bytes(operation.content),
            }
            for operation in operations
        ]

    def _validate_commit_authorization(
        self,
        store: RunStore,
        manifest: dict[str, Any],
        operations: list[WriteOperation],
    ) -> tuple[bool, str, str, str]:
        approval_file = store.run_dir / "receipts" / "commit-approval.json"
        intent_file = store.run_dir / "commit-intent.json"
        approval_relative = approval_file.relative_to(self.vault_root).as_posix()
        intent_relative = intent_file.relative_to(self.vault_root).as_posix()
        try:
            approval = read_json(approval_file)
            intent = read_json(intent_file)
            expected_scope = self._operation_scope(operations)
            expected_scope_hash = canonical_json_sha256(expected_scope)
            if intent.get("run_id") != store.run_id or intent.get("state") != "COMMITTING":
                raise ValueError("commit intent does not identify an active COMMITTING run")
            if intent.get("approval") != approval_relative:
                raise ValueError("commit intent points to a different approval receipt")
            if intent.get("approval_sha256") != sha256_file(approval_file):
                raise ValueError("commit approval bytes no longer match the intent")
            if intent.get("scope") != expected_scope:
                raise ValueError("commit intent scope does not match the current operations")
            if intent.get("scope_hash") != expected_scope_hash:
                raise ValueError("commit intent scope hash is invalid")
            expected_rollback = (store.run_dir / "rollback").relative_to(self.vault_root).as_posix()
            if intent.get("rollback_root") != expected_rollback:
                raise ValueError("commit intent rollback root is invalid")

            if approval.get("run_id") != store.run_id:
                raise ValueError("approval run_id mismatch")
            if approval.get("actor") != getpass.getuser():
                raise ValueError("approval actor does not match the current host actor")
            if approval.get("vault_fingerprint") != self.vault_fingerprint:
                raise ValueError("approval vault fingerprint mismatch")
            if approval.get("contract_version") != self.contracts.version:
                raise ValueError("approval contract version mismatch")
            if approval.get("manifest_sha256") != sha256_file(store.manifest_path):
                raise ValueError("approval manifest hash no longer matches the run")
            if approval.get("governance_receipt") != manifest.get("governance_receipt"):
                raise ValueError("approval governance receipt path mismatch")
            governance_path = resolve_within(self.vault_root, str(manifest["governance_receipt"]))
            if approval.get("governance_receipt_sha256") != sha256_file(governance_path):
                raise ValueError("approval governance receipt hash no longer matches")
            if approval.get("scope") != expected_scope:
                raise ValueError("approval scope does not match the current operations")
            if approval.get("scope_hash") != expected_scope_hash:
                raise ValueError("approval scope hash is invalid")

            def parse_utc(value: Any, field: str) -> datetime:
                if not isinstance(value, str):
                    raise ValueError(f"approval {field} is missing")
                parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
                if parsed.tzinfo is None:
                    raise ValueError(f"approval {field} is timezone-naive")
                return parsed.astimezone(timezone.utc)

            approved_at = parse_utc(approval.get("approved_at"), "approved_at")
            expires_at = parse_utc(approval.get("expires_at"), "expires_at")
            now = datetime.now(timezone.utc)
            if expires_at <= approved_at:
                raise ValueError("approval expiry does not follow approval time")
            if approved_at > now + timedelta(seconds=30):
                raise ValueError("approval time is in the future")
            if expires_at < now:
                raise ValueError("commit approval has expired")
        except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            return False, str(exc), approval_relative, intent_relative
        return True, "authorization receipt and intent are current", approval_relative, intent_relative

    def _authorize_commit(
        self,
        store: RunStore,
        manifest: dict[str, Any],
        operations: list[WriteOperation],
    ) -> tuple[str, str]:
        approved_at = datetime.now(timezone.utc).replace(microsecond=0)
        scope = self._operation_scope(operations)
        approval = {
            "schema_version": "1.0",
            "run_id": store.run_id,
            "actor": getpass.getuser(),
            "approved_at": approved_at.isoformat().replace("+00:00", "Z"),
            "expires_at": (approved_at + timedelta(minutes=5)).isoformat().replace("+00:00", "Z"),
            "vault_fingerprint": self.vault_fingerprint,
            "contract_version": self.contracts.version,
            "manifest_sha256": sha256_file(store.manifest_path),
            "governance_receipt": manifest["governance_receipt"],
            "governance_receipt_sha256": sha256_file(
                resolve_within(self.vault_root, manifest["governance_receipt"])
            ),
            "scope": scope,
            "scope_hash": canonical_json_sha256(scope),
            "approval_source": "explicit --approve-commit host invocation",
        }
        approval_path = store.run_dir / "receipts" / "commit-approval.json"
        atomic_write_json(approval_path, approval)
        intent = {
            "schema_version": "1.0",
            "run_id": store.run_id,
            "state": "COMMITTING",
            "approval": approval_path.relative_to(self.vault_root).as_posix(),
            "approval_sha256": sha256_file(approval_path),
            "scope": scope,
            "scope_hash": canonical_json_sha256(scope),
            "rollback_root": (store.run_dir / "rollback").relative_to(self.vault_root).as_posix(),
        }
        intent_path = store.run_dir / "commit-intent.json"
        atomic_write_json(intent_path, intent)
        store.transition(
            "COMMITTING",
            "apply_compare_and_set_transaction",
            evidence=[
                approval_path.relative_to(self.vault_root).as_posix(),
                intent_path.relative_to(self.vault_root).as_posix(),
            ],
            last_error=None,
        )
        return (
            approval_path.relative_to(self.vault_root).as_posix(),
            intent_path.relative_to(self.vault_root).as_posix(),
        )

    def _canonical_checkpoint(
        self,
        store: RunStore,
        manifest: dict[str, Any],
        applied: list[Any],
        approval_path: str,
        intent_path: str,
    ) -> str:
        checkpoint = {
            "schema_version": "1.0",
            "run_id": store.run_id,
            "state": "CANONICAL_COMMITTED",
            "mode": manifest.get("mode", "ingest"),
            "contract_version": self.contracts.version,
            "vault_fingerprint": self.vault_fingerprint,
            "idempotency_key": manifest["idempotency_key"],
            "writes": TransactionManager.receipts(applied),
            "commit_approval": approval_path,
            "commit_intent": intent_path,
            "verified_at": iso_z(),
        }
        checkpoint_path = store.run_dir / "receipts" / "canonical-commit.json"
        atomic_write_json(checkpoint_path, checkpoint)
        return checkpoint_path.relative_to(self.vault_root).as_posix()

    def _mark_archive_pending(
        self,
        store: RunStore,
        manifest: dict[str, Any],
        checkpoint_relative: str,
        error: str,
    ) -> dict[str, Any]:
        checkpoint_normalized = normalize_relative_path(checkpoint_relative)
        checkpoint_path = resolve_within(self.vault_root, checkpoint_normalized)
        try:
            checkpoint_path.relative_to(store.run_dir)
        except ValueError as exc:
            raise WorkflowError("canonical checkpoint is outside the active run") from exc
        if not checkpoint_path.is_file():
            raise WorkflowError("canonical checkpoint is missing before archival")
        observed_checkpoint_sha = sha256_file(checkpoint_path)
        existing_checkpoint = str(manifest.get("canonical_checkpoint") or "")
        existing_checkpoint_sha = str(manifest.get("canonical_checkpoint_sha256") or "")
        if existing_checkpoint and normalize_relative_path(existing_checkpoint) != checkpoint_normalized:
            raise WorkflowError("canonical checkpoint path changed while archival was pending")
        if existing_checkpoint_sha and existing_checkpoint_sha != observed_checkpoint_sha:
            raise WorkflowError("canonical checkpoint changed while archival was pending")
        archive_target = str(manifest.get("archive_target") or "")
        if not archive_target:
            archive_target = self._plan_archive_destination(
                str(manifest["clipping"]["relative_path"]), store.run_id
            )
        manifest["status"] = "ARCHIVE_PENDING"
        manifest["permissions"]["canonical_commit"] = True
        manifest["canonical_checkpoint"] = checkpoint_normalized
        manifest["canonical_checkpoint_sha256"] = observed_checkpoint_sha
        manifest["archive_target"] = normalize_relative_path(archive_target)
        manifest["archive_error"] = error
        atomic_write_json(store.manifest_path, manifest)
        store.transition(
            "BLOCKED_DEPENDENCY",
            "retry_archive_only",
            evidence=[checkpoint_normalized],
            last_error=error,
        )
        return {
            "status": "BLOCKED_DEPENDENCY",
            "run_id": store.run_id,
            "canonical_committed": True,
            "canonical_checkpoint": checkpoint_normalized,
            "archive_target": manifest["archive_target"],
            "archive_error": error,
            "next_action": "retry_archive_only",
        }

    def _validated_archive_checkpoint(
        self,
        store: RunStore,
        manifest: dict[str, Any],
    ) -> dict[str, Any]:
        checkpoint_relative = normalize_relative_path(str(manifest.get("canonical_checkpoint") or ""))
        checkpoint_path = resolve_within(self.vault_root, checkpoint_relative)
        try:
            checkpoint_path.relative_to(store.run_dir)
        except ValueError as exc:
            raise WorkflowError("archive checkpoint is outside the active run") from exc
        if not checkpoint_path.is_file():
            raise WorkflowError("archive checkpoint is missing")
        expected_checkpoint_sha = str(manifest.get("canonical_checkpoint_sha256") or "")
        if not expected_checkpoint_sha or sha256_file(checkpoint_path) != expected_checkpoint_sha:
            raise WorkflowError("archive checkpoint hash is missing or changed")
        checkpoint = read_json(checkpoint_path)
        if (
            checkpoint.get("run_id") != store.run_id
            or checkpoint.get("state") != "CANONICAL_COMMITTED"
            or checkpoint.get("mode") != "ingest"
            or checkpoint.get("contract_version") != self.contracts.version
            or checkpoint.get("vault_fingerprint") != self.vault_fingerprint
            or checkpoint.get("idempotency_key") != manifest.get("idempotency_key")
        ):
            raise WorkflowError("archive checkpoint identity is invalid")
        writes = checkpoint.get("writes")
        if not isinstance(writes, list) or len(writes) != 3 or any(
            not isinstance(write, dict) for write in writes
        ):
            raise WorkflowError("archive checkpoint must contain exactly three canonical writes")
        required_write_fields = {
            "relative_path",
            "kind",
            "preimage_sha256",
            "postimage_sha256",
            "changed",
            "preserve_on_rollback",
        }
        if any(not required_write_fields.issubset(write) for write in writes):
            raise WorkflowError("archive checkpoint contains an incomplete write receipt")
        if len({str(write["relative_path"]) for write in writes}) != len(writes):
            raise WorkflowError("archive checkpoint contains duplicate write paths")
        scope = [
            {
                "relative_path": write["relative_path"],
                "kind": write["kind"],
                "expected_preimage_sha256": write["preimage_sha256"],
                "postimage_sha256": write["postimage_sha256"],
            }
            for write in writes
        ]
        approval_relative = normalize_relative_path(str(checkpoint.get("commit_approval") or ""))
        intent_relative = normalize_relative_path(str(checkpoint.get("commit_intent") or ""))
        approval_path = resolve_within(self.vault_root, approval_relative)
        intent_path = resolve_within(self.vault_root, intent_relative)
        try:
            approval_path.relative_to(store.run_dir)
            intent_path.relative_to(store.run_dir)
        except ValueError as exc:
            raise WorkflowError("archive checkpoint authorization is outside the active run") from exc
        approval = read_json(approval_path)
        intent = read_json(intent_path)
        scope_hash = canonical_json_sha256(scope)
        governance_path = resolve_within(self.vault_root, str(manifest["governance_receipt"]))
        if (
            approval.get("run_id") != store.run_id
            or approval.get("vault_fingerprint") != self.vault_fingerprint
            or approval.get("contract_version") != self.contracts.version
            or approval.get("governance_receipt") != manifest.get("governance_receipt")
            or approval.get("governance_receipt_sha256") != sha256_file(governance_path)
            or approval.get("scope") != scope
            or approval.get("scope_hash") != scope_hash
        ):
            raise WorkflowError("archive checkpoint commit approval is invalid")
        expected_rollback_root = (store.run_dir / "rollback").relative_to(self.vault_root).as_posix()
        if (
            intent.get("run_id") != store.run_id
            or intent.get("state") != "COMMITTING"
            or intent.get("approval") != approval_relative
            or intent.get("approval_sha256") != sha256_file(approval_path)
            or intent.get("scope") != scope
            or intent.get("scope_hash") != scope_hash
            or intent.get("rollback_root") != expected_rollback_root
        ):
            raise WorkflowError("archive checkpoint commit intent is invalid")
        return checkpoint

    def _authorize_archive_repair(
        self,
        store: RunStore,
        manifest: dict[str, Any],
    ) -> dict[str, str]:
        approved_at = iso_z()
        approval = {
            "schema_version": "1.0",
            "run_id": store.run_id,
            "actor": getpass.getuser(),
            "approved_at": approved_at,
            "action": "archive-only",
            "approval_source": "explicit --approve-commit host invocation",
            "vault_fingerprint": self.vault_fingerprint,
            "contract_version": self.contracts.version,
            "idempotency_key": manifest["idempotency_key"],
            "clipping": {
                "relative_path": manifest["clipping"]["relative_path"],
                "sha256": manifest["clipping"]["sha256"],
            },
            "archive_target": manifest["archive_target"],
            "canonical_checkpoint": manifest["canonical_checkpoint"],
            "canonical_checkpoint_sha256": manifest["canonical_checkpoint_sha256"],
        }
        approval_path = store.run_dir / "receipts" / "archive-repair-approval.json"
        atomic_write_json(approval_path, approval)
        return {
            "path": approval_path.relative_to(self.vault_root).as_posix(),
            "sha256": sha256_file(approval_path),
        }

    def _repair_archive(self, store: RunStore, manifest: dict[str, Any]) -> dict[str, Any]:
        def blocked(error: str, drift: list[dict[str, str]] | None = None) -> dict[str, Any]:
            manifest["status"] = "ARCHIVE_PENDING"
            manifest["archive_error"] = error
            atomic_write_json(store.manifest_path, manifest)
            store.transition(
                "BLOCKED_DEPENDENCY",
                "retry_archive_only",
                evidence=[str(manifest.get("canonical_checkpoint") or "")],
                last_error=error,
            )
            result: dict[str, Any] = {
                "status": "BLOCKED_DEPENDENCY",
                "run_id": store.run_id,
                "canonical_committed": True,
                "archive_error": error,
                "next_action": "retry_archive_only",
            }
            if drift:
                result["drift"] = drift
            return result

        try:
            checkpoint = self._validated_archive_checkpoint(store, manifest)
            clipping_relative = normalize_relative_path(str(manifest["clipping"]["relative_path"]))
            archive_relative = normalize_relative_path(str(manifest.get("archive_target") or ""))
            archive_root_relative = normalize_relative_path(self.contracts.paths["clippings_archive"])
            if not archive_relative.startswith(archive_root_relative + "/"):
                raise WorkflowError("planned archive destination is outside the archive root")
            clipping_path = resolve_within(self.vault_root, clipping_relative)
            archive_path = resolve_within(self.vault_root, archive_relative)
            if clipping_path.is_file() and archive_path.exists():
                raise WorkflowError("both clipping and planned archive destination exist")
            if not clipping_path.is_file() and not archive_path.is_file():
                raise WorkflowError("neither clipping nor planned archive evidence exists")
            evidence_path = clipping_path if clipping_path.is_file() else archive_path
            input_bytes = evidence_path.read_bytes()
            input_sha256 = str(manifest["clipping"]["sha256"])
            if sha256_bytes(input_bytes) != input_sha256:
                raise WorkflowError("clipping or archive bytes changed before archive completion")

            writes = checkpoint["writes"]
            writes_by_kind = {str(write["kind"]): write for write in writes}
            if set(writes_by_kind) != {"source", "concept", "map"}:
                raise WorkflowError("archive checkpoint write kinds are invalid")
            source = manifest["source"]
            concept = manifest["concept"]
            expected_paths = {
                "source": normalize_relative_path(str(source["canonical_relative_path"])),
                "concept": normalize_relative_path(str(concept["target_relative_path"])),
                "map": normalize_relative_path(str(manifest["graph"]["target_relative_path"])),
            }
            expected_hashes = {
                "source": str(source["governed_note_sha256"]),
                "concept": str(manifest["verified_artifact_sha256"]),
            }
            for kind, expected_path in expected_paths.items():
                write = writes_by_kind[kind]
                if normalize_relative_path(str(write["relative_path"])) != expected_path:
                    raise WorkflowError(f"archive checkpoint {kind} path does not match the run manifest")
                target = resolve_within(self.vault_root, expected_path)
                if not target.is_file() or sha256_file(target) != write["postimage_sha256"]:
                    raise WorkflowError(f"canonical {kind} output drifted before archival")
                if kind in expected_hashes and write["postimage_sha256"] != expected_hashes[kind]:
                    raise WorkflowError(f"archive checkpoint {kind} hash does not match governance")

            source_path = resolve_within(self.vault_root, expected_paths["source"])
            source_text = source_path.read_text(encoding="utf-8", errors="replace")
            source_report = validate_source(
                expected_paths["source"],
                source_text,
                input_bytes,
                self.contracts.version,
                schema=self.contracts.schema("source"),
            )
            concept_path = resolve_within(self.vault_root, expected_paths["concept"])
            concept_report = validate_concept(
                expected_paths["concept"],
                concept_path.read_text(encoding="utf-8", errors="replace"),
                expected_paths["source"],
                source_text,
                source["source_id"],
                concept["domain"],
                self.contracts.version,
                self.contracts.freshness_policy,
                vault_root=self.vault_root,
                schema=self.contracts.schema("concept"),
            )
            graph_delta = GraphDelta(**manifest["graph"])
            expected_graph_hash = sha256_bytes(
                render_graph_target(self.vault_root, graph_delta, self.contracts.version)
            )
            if expected_graph_hash != writes_by_kind["map"]["postimage_sha256"]:
                raise WorkflowError("canonical map output no longer matches the governed graph delta")
            if not source_report.passed or not concept_report.passed:
                raise WorkflowError("canonical knowledge outputs no longer pass governance")
        except (KeyError, OSError, TypeError, ValueError, WorkflowError, json.JSONDecodeError) as exc:
            return blocked(str(exc))

        idempotency_path = self._idempotency_path(str(manifest["idempotency_key"]))
        if idempotency_path.is_file():
            valid, reason, drift = self._receipt_validity(
                idempotency_path,
                str(manifest["idempotency_key"]),
                expected_mode="ingest",
                expected_input_sha256=input_sha256,
                expected_source_hash=str(source["source_hash"]),
                expected_source_relative=expected_paths["source"],
                expected_input_bytes=input_bytes,
            )
            if not valid:
                return blocked(f"archive terminalization receipt is invalid: {reason}", drift)
            receipt = read_json(idempotency_path)
            if receipt.get("run_id") != store.run_id or receipt.get("archive") != archive_relative:
                return blocked("archive terminalization receipt belongs to a different run or destination")
            manifest["status"] = "ARCHIVED"
            manifest["archive_error"] = None
            manifest["permissions"]["canonical_commit"] = True
            manifest["final_receipt"] = (store.run_dir / "receipt.json").relative_to(
                self.vault_root
            ).as_posix()
            manifest["idempotency_receipt"] = idempotency_path.relative_to(
                self.vault_root
            ).as_posix()
            atomic_write_json(store.manifest_path, manifest)
            store.transition(
                "ARCHIVED",
                "stop",
                evidence=[manifest["final_receipt"], manifest["idempotency_receipt"]],
                last_error=None,
            )
            return {"status": "ARCHIVED", "run_id": store.run_id, "receipt": receipt}

        repair_approval = self._authorize_archive_repair(store, manifest)
        if clipping_path.is_file():
            try:
                observed_archive = self._archive(
                    clipping_relative,
                    store.run_id,
                    destination_relative=archive_relative,
                )
            except (OSError, ValueError) as exc:
                return blocked(str(exc))
            if observed_archive != archive_relative:
                return blocked("archive destination differs from the durable archive plan")
        if not archive_path.is_file() or sha256_file(archive_path) != input_sha256:
            return blocked("archive evidence is missing or changed after the move")

        receipt = {
            "run_id": store.run_id,
            "mode": "ingest",
            "status": "ARCHIVED",
            "contract_version": self.contracts.version,
            "vault_fingerprint": self.vault_fingerprint,
            "idempotency_key": manifest["idempotency_key"],
            "input_sha256": input_sha256,
            "writes": checkpoint["writes"],
            "archive": archive_relative,
            "archive_error": None,
            "verified_at": iso_z(),
            "governance_receipt": manifest["governance_receipt"],
            "source_evidence": {
                "path": source["canonical_relative_path"],
                "sha256": source["governed_note_sha256"],
                "source_hash": source["source_hash"],
                "source_id": source["source_id"],
            },
            "commit_approval": checkpoint["commit_approval"],
            "commit_intent": checkpoint["commit_intent"],
            "canonical_checkpoint": manifest["canonical_checkpoint"],
            "canonical_checkpoint_sha256": manifest["canonical_checkpoint_sha256"],
            "archive_repair_approval": repair_approval,
        }
        receipt_path = store.run_dir / "receipt.json"
        atomic_write_json(receipt_path, receipt)
        manifest["final_receipt"] = receipt_path.relative_to(self.vault_root).as_posix()
        manifest["idempotency_receipt"] = idempotency_path.relative_to(self.vault_root).as_posix()
        atomic_write_json(store.manifest_path, manifest)
        self._exclusive_idempotency_receipt(str(manifest["idempotency_key"]), receipt)
        valid, reason, drift = self._receipt_validity(
            idempotency_path,
            str(manifest["idempotency_key"]),
            expected_mode="ingest",
            expected_input_sha256=input_sha256,
            expected_source_hash=str(source["source_hash"]),
            expected_source_relative=expected_paths["source"],
            expected_input_bytes=input_bytes,
        )
        if not valid:
            if idempotency_path.is_file() and read_json(idempotency_path) == receipt:
                idempotency_path.unlink()
            return blocked(f"archive terminalization verification failed: {reason}", drift)
        manifest["status"] = "ARCHIVED"
        manifest["archive_error"] = None
        manifest["permissions"]["canonical_commit"] = True
        atomic_write_json(store.manifest_path, manifest)
        store.transition(
            "ARCHIVED",
            "stop",
            evidence=[manifest["final_receipt"], manifest["idempotency_receipt"]],
            last_error=None,
        )
        return {"status": "ARCHIVED", "run_id": store.run_id, "receipt": receipt}

    def _commit_system_deployment(self, store: RunStore, manifest: dict[str, Any]) -> dict[str, Any]:
        state_status = str(store.load_state().get("status") or "")
        recovering = state_status == "COMMITTING"
        current_hash, current_id = system_bundle_identity(self.contracts.repo_root, self.contracts.version)
        if current_hash != manifest["bundle_hash"] or current_id != manifest["bundle_id"]:
            store.transition(
                "BLOCKED_DEPENDENCY",
                "restage_system_bundle",
                last_error="repository system bundle changed after verification",
            )
            return {
                "status": "BLOCKED_DEPENDENCY",
                "run_id": store.run_id,
                "error": "repository system bundle changed after verification",
            }
        staged_ok, evidence = verify_staged_system_bundle(
            self.contracts.repo_root,
            self.vault_root,
            store.run_dir / "staging",
            manifest["system_entries"],
            self.contracts.version,
            verify_target_preimages=not recovering,
        )
        if not staged_ok:
            store.transition(
                "BLOCKED_DEPENDENCY",
                "restage_system_bundle_from_fresh_contract_and_preimages",
                last_error="system bundle manifest, staged bytes, or target preimages changed",
            )
            return {"status": "BLOCKED_DEPENDENCY", "run_id": store.run_id, "evidence": evidence}

        current_inventory = build_inventory(
            self.vault_root,
            contract_version=self.contracts.version,
            vault_fingerprint=self.vault_fingerprint,
            limit=0,
        )
        if manifest.get("inventory_baseline") != inventory_debt_signature(current_inventory):
            store.transition(
                "BLOCKED_DEPENDENCY",
                "restage_system_bundle_from_fresh_inventory",
                last_error="governed vault debt changed after system staging",
            )
            return {
                "status": "BLOCKED_DEPENDENCY",
                "run_id": store.run_id,
                "error": "governed vault debt changed after system staging",
            }

        expected_artifacts = [
            {
                "path": str(entry["target_relative_path"]),
                "sha256": str(entry["source_sha256"]),
                "expected_preimage_sha256": entry.get("expected_preimage_sha256"),
            }
            for entry in manifest["system_entries"]
        ]
        try:
            governance_receipt = read_json(
                resolve_within(self.vault_root, str(manifest["governance_receipt"]))
            )
            self._assert_worker_receipt(governance_receipt, store.run_id, expected_artifacts)
            if governance_receipt.get("state") != "VERIFIED":
                raise WorkflowError("system governance receipt is not VERIFIED")
        except (OSError, KeyError, TypeError, ValueError, WorkflowError) as exc:
            store.transition(
                "VERIFY_FAILED",
                "resubmit_system_bundle",
                last_error=f"system governance receipt is invalid: {exc}",
            )
            return {
                "status": "VERIFY_FAILED",
                "run_id": store.run_id,
                "error": f"system governance receipt is invalid: {exc}",
            }

        operations = []
        for entry in manifest["system_entries"]:
            target = str(entry["target_relative_path"])
            staged = resolve_within(store.run_dir / "staging", target)
            operations.append(
                WriteOperation(
                    target,
                    staged.read_bytes(),
                    "system",
                    expected_preimage_sha256=entry.get("expected_preimage_sha256"),
                )
            )
        transaction = TransactionManager(self.vault_root, store.run_dir / "rollback")
        if recovering:
            authorized, reason, approval_path, intent_path = self._validate_commit_authorization(
                store, manifest, operations
            )
            if not authorized:
                store.transition(
                    "BLOCKED_PERMISSION",
                    "obtain_fresh_commit_approval",
                    last_error=reason,
                )
                return {"status": "BLOCKED_PERMISSION", "run_id": store.run_id, "error": reason}
            recovered = transaction.reconcile_applied(operations)
            if recovered is None:
                store.transition(
                    "BLOCKED_DEPENDENCY",
                    "repair_or_rollback_incomplete_transaction",
                    last_error="COMMITTING system transaction is not an exact all-written checkpoint",
                )
                return {
                    "status": "BLOCKED_DEPENDENCY",
                    "run_id": store.run_id,
                    "error": "COMMITTING system transaction is not an exact all-written checkpoint",
                }
            applied = recovered
        else:
            approval_path, intent_path = self._authorize_commit(store, manifest, operations)
            authorized, reason, _, _ = self._validate_commit_authorization(
                store, manifest, operations
            )
            if not authorized:
                store.transition(
                    "BLOCKED_PERMISSION",
                    "obtain_fresh_commit_approval",
                    last_error=reason,
                )
                return {"status": "BLOCKED_PERMISSION", "run_id": store.run_id, "error": reason}
            try:
                applied = transaction.apply(operations)
            except PreimageConflict as exc:
                store.transition("BLOCKED_DEPENDENCY", "restage_from_fresh_system_preimages", last_error=str(exc))
                return {"status": "BLOCKED_DEPENDENCY", "run_id": store.run_id, "error": str(exc)}

        post_failures = []
        for entry in manifest["system_entries"]:
            target = resolve_within(self.vault_root, entry["target_relative_path"])
            if not target.is_file() or sha256_file(target) != entry["source_sha256"]:
                post_failures.append(str(entry["target_relative_path"]))
        if post_failures:
            rollback_conflicts = transaction.rollback(applied)
            post = {
                "failed_targets": post_failures,
                "rolled_back": not rollback_conflicts,
                "rollback_conflicts": rollback_conflicts,
            }
            atomic_write_json(store.run_dir / "receipts" / "post-commit-failure.json", post)
            store.transition("VERIFY_FAILED", "repair_system_post_commit_failure", last_error="system post-check failed")
            return {"status": "VERIFY_FAILED", "run_id": store.run_id, "post_commit": post}

        baseline_debt = manifest.get("inventory_baseline")
        if not isinstance(baseline_debt, dict):
            rollback_conflicts = transaction.rollback(applied)
            post = {
                "inventory_regressions": [{"metric": "inventory_baseline", "before": 1, "after": 0}],
                "rollback_conflicts": rollback_conflicts,
            }
            atomic_write_json(store.run_dir / "receipts" / "post-commit-failure.json", post)
            store.transition(
                "VERIFY_FAILED",
                "restage_system_bundle_with_inventory_baseline",
                last_error="system deployment has no governed-debt baseline",
            )
            return {"status": "VERIFY_FAILED", "run_id": store.run_id, "post_commit": post}
        observed_inventory = build_inventory(
            self.vault_root,
            contract_version=self.contracts.version,
            vault_fingerprint=self.vault_fingerprint,
            limit=0,
        )
        observed_debt = inventory_debt_signature(observed_inventory)
        inventory_regressions = inventory_debt_regressions(baseline_debt, observed_debt)
        if inventory_regressions:
            rollback_conflicts = transaction.rollback(applied)
            post = {
                "inventory_regressions": inventory_regressions,
                "inventory_baseline": baseline_debt,
                "inventory_observed": observed_debt,
                "rollback_conflicts": rollback_conflicts,
            }
            atomic_write_json(store.run_dir / "receipts" / "post-commit-failure.json", post)
            store.transition(
                "VERIFY_FAILED",
                "repair_system_inventory_regression",
                last_error="system deployment increased governed vault debt",
            )
            return {"status": "VERIFY_FAILED", "run_id": store.run_id, "post_commit": post}

        canonical_checkpoint = self._canonical_checkpoint(
            store, manifest, applied, approval_path, intent_path
        )

        receipt = {
            "run_id": store.run_id,
            "mode": "system-bundle",
            "status": "COMMITTED",
            "contract_version": self.contracts.version,
            "vault_fingerprint": self.vault_fingerprint,
            "idempotency_key": manifest["idempotency_key"],
            "input_sha256": manifest["bundle_hash"],
            "bundle_id": manifest["bundle_id"],
            "bundle_hash": manifest["bundle_hash"],
            "writes": transaction.receipts(applied),
            "inventory_baseline": baseline_debt,
            "inventory_observed": observed_debt,
            "archive": None,
            "archive_error": None,
            "verified_at": iso_z(),
            "governance_receipt": manifest["governance_receipt"],
            "commit_approval": approval_path,
            "commit_intent": intent_path,
            "canonical_checkpoint": canonical_checkpoint,
            "canonical_checkpoint_sha256": sha256_file(
                resolve_within(self.vault_root, canonical_checkpoint)
            ),
        }
        receipt_path = store.run_dir / "receipt.json"
        atomic_write_json(receipt_path, receipt)
        idempotency_path = self._exclusive_idempotency_receipt(manifest["idempotency_key"], receipt)
        manifest["status"] = "COMMITTED"
        manifest["permissions"]["canonical_commit"] = True
        manifest["canonical_checkpoint"] = canonical_checkpoint
        manifest["canonical_checkpoint_sha256"] = receipt["canonical_checkpoint_sha256"]
        manifest["final_receipt"] = receipt_path.relative_to(self.vault_root).as_posix()
        manifest["idempotency_receipt"] = idempotency_path.relative_to(self.vault_root).as_posix()
        atomic_write_json(store.manifest_path, manifest)
        store.transition(
            "COMMITTED",
            "stop",
            evidence=[
                receipt_path.relative_to(self.vault_root).as_posix(),
                idempotency_path.relative_to(self.vault_root).as_posix(),
            ],
            last_error=None,
        )
        return {"status": "COMMITTED", "run_id": store.run_id, "receipt": receipt}

    @integration_owned
    def commit(self, run_id: str, approve_commit: bool = False, archive: bool = True) -> dict[str, Any]:
        if not approve_commit:
            raise PermissionError("canonical commit requires explicit host approval")
        self.contracts.verify_templates()
        store = RunStore.find(self.vault_root, run_id)
        manifest = read_json(store.manifest_path)
        if manifest.get("contract_version") != self.contracts.version:
            raise WorkflowError("run contract is stale")
        if manifest.get("vault_fingerprint") != self.vault_fingerprint:
            raise WorkflowError("vault fingerprint changed after staging")
        mode = manifest.get("mode", "ingest")
        if mode == "ingest" and manifest.get("status") == "ARCHIVE_PENDING":
            if not archive:
                return self._mark_archive_pending(
                    store,
                    manifest,
                    str(manifest.get("canonical_checkpoint") or ""),
                    "archive deferred by explicit --no-archive invocation",
                )
            return self._repair_archive(store, manifest)
        prior_result = self._existing_idempotency_gate(store, manifest)
        if prior_result is not None:
            return prior_result
        if manifest.get("status") != "VERIFIED":
            raise WorkflowError(f"run is not verified: {manifest.get('status')}")
        if mode == "system-bundle":
            return self._commit_system_deployment(store, manifest)
        clipping: Path | None = None
        evidence_input: Path | None = None
        if mode == "ingest":
            clipping = resolve_within(self.vault_root, manifest["clipping"]["relative_path"])
            if sha256_file(clipping) != manifest["clipping"]["sha256"]:
                raise WorkflowError("clipping changed after staging")
            evidence_input = clipping
        elif mode == "local-ingest":
            evidence_input = resolve_within(self.contracts.repo_root, manifest["input"]["repo_relative_path"])
            if sha256_file(evidence_input) != manifest["input"]["sha256"]:
                raise WorkflowError("local repository input changed after staging")
        elif mode == "retrofit":
            legacy_source = resolve_within(self.vault_root, manifest["source"]["canonical_relative_path"])
            if sha256_file(legacy_source) != manifest["source_preimage_sha256"]:
                store.transition(
                    "BLOCKED_DEPENDENCY",
                    "rebuild_retrofit_context",
                    last_error="legacy source changed after staging",
                )
                return {
                    "status": "BLOCKED_DEPENDENCY",
                    "run_id": run_id,
                    "error": "legacy source changed after staging",
                }
        else:
            raise WorkflowError(f"unsupported run mode: {mode}")

        source = manifest["source"]
        concept = manifest["concept"]
        expected_source_note_sha256 = str(source["governed_note_sha256"])
        operations: list[WriteOperation] = []
        if source["staged_relative_path"]:
            staged_source = resolve_within(store.run_dir / "staging", source["staged_relative_path"])
            if sha256_file(staged_source) != source.get("staged_note_sha256"):
                store.transition(
                    "VERIFY_FAILED",
                    "restage_source_after_mutation",
                    last_error="staged source changed after source governance",
                )
                return {
                    "status": "VERIFY_FAILED",
                    "run_id": run_id,
                    "error": "staged source changed after source governance",
                }
            operations.append(
                WriteOperation(
                    source["canonical_relative_path"],
                    staged_source.read_bytes(),
                    "source",
                    expected_preimage_sha256=None,
                    preserve_on_rollback=False,
                )
            )
        else:
            existing_source = resolve_within(self.vault_root, source["existing_relative_path"])
            existing_source_bytes = existing_source.read_bytes()
            if sha256_bytes(existing_source_bytes) != expected_source_note_sha256:
                store.transition(
                    "BLOCKED_DEPENDENCY",
                    "rebuild_context_from_fresh_source_preimage",
                    last_error="reused source changed after governance",
                )
                return {
                    "status": "BLOCKED_DEPENDENCY",
                    "run_id": run_id,
                    "error": "reused source changed after governance",
                }
            operations.append(
                WriteOperation(
                    source["canonical_relative_path"],
                    existing_source_bytes,
                    "source",
                    expected_preimage_sha256=expected_source_note_sha256,
                    preserve_on_rollback=False,
                )
            )
        staged_concept = resolve_within(store.run_dir / "staging", concept["staged_relative_path"])
        governance_receipt = read_json(resolve_within(self.vault_root, manifest["governance_receipt"]))
        verified_artifacts = governance_receipt.get("artifact")
        expected_candidate_hash = manifest.get("verified_artifact_sha256")
        expected_artifacts = [
            {
                "path": staged_concept.relative_to(self.vault_root).as_posix(),
                "sha256": expected_candidate_hash,
                "expected_preimage_sha256": concept["expected_preimage_sha256"],
            }
        ]
        receipt_violations = self._worker_receipt_violations(
            governance_receipt, run_id, expected_artifacts
        )
        if (
            receipt_violations
            or
            governance_receipt.get("state") != "VERIFIED"
            or governance_receipt.get("run_id") != run_id
            or not isinstance(verified_artifacts, list)
            or len(verified_artifacts) != 1
            or verified_artifacts[0].get("sha256") != expected_candidate_hash
            or sha256_file(staged_concept) != expected_candidate_hash
        ):
            store.transition(
                "VERIFY_FAILED",
                "resubmit_candidate_after_mutation",
                last_error="staged concept no longer matches its governance receipt",
            )
            return {
                "status": "VERIFY_FAILED",
                "run_id": run_id,
                "error": "staged concept no longer matches its governance receipt"
                + (": " + "; ".join(receipt_violations) if receipt_violations else ""),
            }
        operations.append(
            WriteOperation(
                concept["target_relative_path"],
                staged_concept.read_bytes(),
                "concept",
                expected_preimage_sha256=concept["expected_preimage_sha256"],
            )
        )
        graph_delta = GraphDelta(**manifest["graph"])
        graph_content = render_graph_target(self.vault_root, graph_delta, self.contracts.version)
        operations.append(
            WriteOperation(
                graph_delta.target_relative_path,
                graph_content,
                "map",
                expected_preimage_sha256=graph_delta.expected_preimage_sha256,
            )
        )
        transaction = TransactionManager(self.vault_root, store.run_dir / "rollback")
        recovering = store.load_state().get("status") == "COMMITTING"
        if recovering:
            authorized, reason, approval_path, intent_path = self._validate_commit_authorization(
                store, manifest, operations
            )
            if not authorized:
                store.transition(
                    "BLOCKED_PERMISSION",
                    "obtain_fresh_commit_approval",
                    last_error=reason,
                )
                return {"status": "BLOCKED_PERMISSION", "run_id": run_id, "error": reason}
            recovered = transaction.reconcile_applied(operations)
            if recovered is None:
                store.transition(
                    "BLOCKED_DEPENDENCY",
                    "repair_or_rollback_incomplete_transaction",
                    last_error="COMMITTING transaction is not an exact all-written checkpoint",
                )
                return {
                    "status": "BLOCKED_DEPENDENCY",
                    "run_id": run_id,
                    "error": "COMMITTING transaction is not an exact all-written checkpoint",
                }
            applied = recovered
        else:
            approval_path, intent_path = self._authorize_commit(store, manifest, operations)
            authorized, reason, _, _ = self._validate_commit_authorization(
                store, manifest, operations
            )
            if not authorized:
                store.transition(
                    "BLOCKED_PERMISSION",
                    "obtain_fresh_commit_approval",
                    last_error=reason,
                )
                return {"status": "BLOCKED_PERMISSION", "run_id": run_id, "error": reason}
            try:
                applied = transaction.apply(operations)
            except PreimageConflict as exc:
                store.transition("BLOCKED_DEPENDENCY", "replan_from_fresh_preimages", last_error=str(exc))
                return {"status": "BLOCKED_DEPENDENCY", "run_id": run_id, "error": str(exc)}

        final_source = resolve_within(self.vault_root, source["canonical_relative_path"])
        final_concept = resolve_within(self.vault_root, concept["target_relative_path"])
        final_source_bytes = final_source.read_bytes()
        source_snapshot_hash = sha256_bytes(final_source_bytes)
        final_source_text = final_source_bytes.decode("utf-8", errors="replace")
        if source_snapshot_hash != expected_source_note_sha256:
            source_report = GovernanceReport(
                False,
                (
                    Finding(
                        "source.preimage.changed",
                        "P0",
                        "source bytes changed after governance",
                        source["canonical_relative_path"],
                    ),
                ),
                ("source-note-preimage",),
            )
        elif mode in {"ingest", "local-ingest"}:
            assert evidence_input is not None
            source_report = validate_source(
                source["canonical_relative_path"],
                final_source_text,
                evidence_input.read_bytes(),
                self.contracts.version,
                schema=self.contracts.schema("source"),
            )
        else:
            source_unchanged = source_snapshot_hash == manifest["source_preimage_sha256"]
            source_report = GovernanceReport(
                source_unchanged,
                ()
                if source_unchanged
                else (
                    Finding(
                        "source.preimage.changed",
                        "P0",
                        "legacy source changed during retrofit",
                        source["canonical_relative_path"],
                    ),
                ),
                ("legacy-source-preimage", "source-anchor-resolution"),
            )
        concept_report = validate_concept(
            concept["target_relative_path"],
            final_concept.read_text(encoding="utf-8", errors="replace"),
            source["canonical_relative_path"],
            final_source_text,
            source["source_id"],
            concept["domain"],
            self.contracts.version,
            self.contracts.freshness_policy,
            vault_root=self.vault_root,
            schema=self.contracts.schema("concept"),
        )
        graph_target = resolve_within(self.vault_root, graph_delta.target_relative_path)
        graph_ok = graph_target.is_file() and sha256_file(graph_target) == sha256_bytes(graph_content)
        source_still_bound = sha256_file(final_source) == expected_source_note_sha256
        if not source_still_bound and source_report.passed:
            source_report = GovernanceReport(
                False,
                (
                    Finding(
                        "source.preimage.changed",
                        "P0",
                        "source changed during post-commit validation",
                        source["canonical_relative_path"],
                    ),
                ),
                ("source-note-final-binding",),
            )
        if not source_report.passed or not concept_report.passed or not graph_ok:
            rollback_conflicts = transaction.rollback(applied)
            post = {
                "source": source_report.to_dict(),
                "concept": concept_report.to_dict(),
                "graph_ok": graph_ok,
                "rollback_conflicts": rollback_conflicts,
            }
            atomic_write_json(store.run_dir / "receipts" / "post-commit-failure.json", post)
            store.transition("VERIFY_FAILED", "repair_post_commit_failure", last_error="post-commit verification failed")
            return {"status": "VERIFY_FAILED", "run_id": run_id, "post_commit": post}

        canonical_checkpoint = self._canonical_checkpoint(
            store, manifest, applied, approval_path, intent_path
        )

        if mode == "ingest":
            pending = self._mark_archive_pending(
                store,
                manifest,
                canonical_checkpoint,
                (
                    "canonical commit complete; clipping archive pending"
                    if archive
                    else "archive deferred by explicit --no-archive invocation"
                ),
            )
            if not archive:
                return pending
            return self._repair_archive(store, manifest)

        final_status = "COMMITTED"
        if mode == "local-ingest":
            input_sha256 = manifest["input"]["sha256"]
        else:
            input_sha256 = manifest["original_concept"]["preimage_sha256"]
        receipt = {
            "run_id": run_id,
            "mode": mode,
            "status": final_status,
            "contract_version": self.contracts.version,
            "vault_fingerprint": self.vault_fingerprint,
            "idempotency_key": manifest["idempotency_key"],
            "input_sha256": input_sha256,
            "writes": transaction.receipts(applied),
            "archive": None,
            "archive_error": None,
            "verified_at": iso_z(),
            "governance_receipt": manifest["governance_receipt"],
            "source_evidence": {
                "path": source["canonical_relative_path"],
                "sha256": expected_source_note_sha256,
                "source_hash": source["source_hash"],
                "source_id": source["source_id"],
            },
            "commit_approval": approval_path,
            "commit_intent": intent_path,
            "canonical_checkpoint": canonical_checkpoint,
            "canonical_checkpoint_sha256": sha256_file(
                resolve_within(self.vault_root, canonical_checkpoint)
            ),
        }
        receipt_path = store.run_dir / "receipt.json"
        atomic_write_json(receipt_path, receipt)
        idempotency_path = self._exclusive_idempotency_receipt(manifest["idempotency_key"], receipt)
        manifest["status"] = final_status
        manifest["permissions"]["canonical_commit"] = True
        manifest["canonical_checkpoint"] = canonical_checkpoint
        manifest["canonical_checkpoint_sha256"] = receipt["canonical_checkpoint_sha256"]
        manifest["final_receipt"] = receipt_path.relative_to(self.vault_root).as_posix()
        manifest["idempotency_receipt"] = idempotency_path.relative_to(self.vault_root).as_posix()
        atomic_write_json(store.manifest_path, manifest)
        store.transition(
            final_status,
            "stop",
            evidence=[
                receipt_path.relative_to(self.vault_root).as_posix(),
                idempotency_path.relative_to(self.vault_root).as_posix(),
            ],
            last_error=None,
        )
        return {"status": final_status, "run_id": run_id, "receipt": receipt}

    def status(self, run_id: str) -> dict[str, Any]:
        return RunStore.find(self.vault_root, run_id).load_state()

    def freshness_scan(self, today: date | None = None, limit: int = 100) -> dict[str, Any]:
        if limit <= 0 or limit > 1000:
            raise ValueError("freshness limit must be between 1 and 1000")
        paths: list[Path] = []
        for relative in ("wiki/concepts", "wiki/entities", "wiki/outputs"):
            root = self.vault_root / relative
            if root.is_dir():
                paths.extend(root.rglob("*.md"))
        maps_root = self.vault_root / "maps"
        if maps_root.is_dir():
            paths.extend(maps_root.rglob("*.md"))
        system_root = self.vault_root / "system"
        if system_root.is_dir():
            paths.extend(system_root.glob("*.md"))
            for relative in ("dashboards", "reports", "indexes"):
                root = system_root / relative
                if root.is_dir():
                    paths.extend(root.rglob("*.md"))
        paths = sorted(set(paths))
        findings = scan_freshness(paths, self.contracts.freshness_policy, today=today, root=self.vault_root)
        return {
            "status": "DUE" if findings else "NO_OP",
            "checked_at": iso_z(),
            "scanned": len(paths),
            "due_or_unknown": len(findings),
            "findings": findings[:limit],
            "findings_truncated": len(findings) > limit,
            "side_effect_count": 0,
        }

    def inventory(self, limit: int = 100, domain: str | None = None) -> dict[str, Any]:
        if limit <= 0 or limit > 1000:
            raise ValueError("inventory limit must be between 1 and 1000")
        if domain is not None and domain not in self.contracts.domains:
            raise ValueError(f"unsupported concept domain: {domain}")
        return build_inventory(
            self.vault_root,
            contract_version=self.contracts.version,
            vault_fingerprint=self.vault_fingerprint,
            limit=limit,
            candidate_domain=domain,
        )
