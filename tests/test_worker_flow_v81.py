from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch

from tools.worker_flow.contracts import ContractBundle
from tools.worker_flow.cli import _exit_code
from tools.worker_flow.runtime import WorkerFlowRuntime
from tools.worker_flow.state import RunStore
from tools.worker_flow.utils import sha256_file


class WorkerFlowV81Test(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp())
        self.vault = self.temp_dir / "Test Vault"
        for relative in (
            "Clippings",
            "sources",
            "wiki/concepts/ai-engineering",
            "wiki/entities/products",
            "wiki/outputs",
            "maps/domain-mocs",
            "system",
        ):
            (self.vault / relative).mkdir(parents=True, exist_ok=True)
        (self.vault / "system" / "config.md").write_text(
            "---\ntitle: Test Vault Config\nversion: 8.1.0\n---\n", encoding="utf-8"
        )
        self.moc_relative = "maps/domain-mocs/AI Engineering.md"
        (self.vault / self.moc_relative).write_text(
            "---\n"
            'title: "AI Engineering"\n'
            "type: map\n"
            'contract_version: "8.1.0"\n'
            "map_tier: domain-moc\n"
            "status: active\n"
            f'updated: "{date.today().isoformat()}"\n'
            "---\n\n# AI Engineering\n\nManual content remains here.\n",
            encoding="utf-8",
        )
        (self.vault / "wiki/concepts/ai-engineering/Related Concept.md").write_text(
            "---\ntitle: Related Concept\ntype: concept\n---\n# Related Concept\n", encoding="utf-8"
        )
        (self.vault / "wiki/entities/products/Example Product.md").write_text(
            "---\ntitle: Example Product\ntype: entity\n---\n# Example Product\n", encoding="utf-8"
        )
        self.runtime = WorkerFlowRuntime(self.vault)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _write_clipping(self, name: str = "Temporal Agent.md", changed: bool = False) -> Path:
        suffix = " A later observation changes the measured behavior." if changed else ""
        content = (
            "---\n"
            'title: "Temporal Agent Architecture"\n'
            'url: "https://example.com/agent?utm_source=test"\n'
            'author: "Example Researcher"\n'
            f'date: "{date.today().isoformat()}"\n'
            "---\n\n"
            "# Temporal Agent Architecture\n\n"
            "A host-controlled runtime separates model proposals from tool execution.\n\n"
            "Immutable source snapshots preserve what was observed at a specific time.\n\n"
            "Independent governance checks evidence anchors before a serial commit."
            f"{suffix}\n"
        )
        path = self.vault / "Clippings" / name
        path.write_text(content, encoding="utf-8")
        return path

    def _prepare(self, name: str = "Temporal Agent.md", title: str = "Temporal Agent Control") -> dict:
        return self.runtime.prepare(
            name,
            concept_title=title,
            domain="ai-engineering",
            moc_relative_path=self.moc_relative,
            freshness_tier="dynamic",
            approve_staging=True,
        )

    def _write_valid_concept(self, prepared: dict, broken_anchor: bool = False) -> Path:
        source = prepared["source"]
        anchors = source["anchors"]
        anchor_1 = "ki-does-not-exist" if broken_anchor else anchors[0]
        today = date.today()
        next_review = today + timedelta(days=30)
        source_note = source["canonical_relative_path"][:-3]
        run_id = prepared["run_id"]
        content = f'''---
title: "Temporal Agent Control"
type: concept
contract_version: "8.1.0"
template_id: concept-gold-standard
template_version: "8.1.0"
url: "https://example.com/agent"
author: "Example Researcher"
date: "{today.isoformat()}"
tags: [domain/ai-engineering, type/concept]
aliases: ["Temporal Agent Control", "时序智能体控制"]
status: growing
created: "{today.isoformat()}"
updated: "{today.isoformat()}"
knowledge_stage: stored
evidence_level: single-source
freshness_tier: dynamic
valid_as_of: "{today.isoformat()}"
last_verified: "{today.isoformat()}"
next_review: "{next_review.isoformat()}"
freshness_status: current
source_ids: ["{source['source_id']}"]
run_id: "{run_id}"
---

# Temporal Agent Control (时序智能体控制)

> [!NOTE] Core Thesis
> Safe knowledge automation separates semantic proposals from host-owned, evidence-checked commits.
> (Source: [[{source_note}#^{anchor_1}]])

> [!INFO] Temporal Scope
> Valid as of **{today.isoformat()}** · freshness tier **dynamic** · next review **{next_review.isoformat()}**.

## 证据范围 (Evidence Scope)

- **Direct evidence:** The source describes host control, immutable snapshots, and independent checks. (Source: [[{source_note}#^{anchors[1]}]])
- **Interpretation:** Those controls form a bounded promotion path.
- **Evidence boundary:** One demonstration does not establish reliability across every vault or model.
- **Falsifier / counterpoint:** A replay that overwrites source evidence or commits a broken anchor would falsify the safety claim.
- **Exact locators:** [[{source_note}#^{anchor_1}]], [[{source_note}#^{anchors[1]}]]

## 核心机制 (Core Mechanisms)

### 1. Host-owned effects

- The host validates tool effects before execution. (Source: [[{source_note}#^{anchors[0]}]])

### 2. Temporal evidence

- Snapshots retain an explicit as-of boundary. (Source: [[{source_note}#^{anchors[1]}]])

### 3. Independent promotion

- Governance runs before the serial commit. (Source: [[{source_note}#^{anchors[2]}]])

## 概念机制图 (Concept Mechanism)

```mermaid
flowchart TD
    A["Clipping"] --> B["Immutable snapshot"]
    B --> C["Semantic candidate"]
    C --> D["Independent governance"]
    D --> E["Serial commit"]
```

## 范式对比矩阵 (Paradigm Matrix)

| Dimension | Prompt-only pipeline | Governed runtime |
|---|---|---|
| Authority | Model prose | Host contract |
| Evidence | Implicit | Block locators |
| Time | Timeless wording | Explicit as-of |
| Writes | Direct | Staged |
| Recovery | Replay all | Resume checkpoint |

## 关键数据与实证 (Key Data)

- **Evidence blocks:** 3 source blocks (as of {today.isoformat()}; Source: [[{source_note}#^{anchors[0]}]])
- **Commit owners:** 1 serial Integration Owner (as of {today.isoformat()}; Source: [[{source_note}#^{anchors[2]}]])

## 应用与工程含义 (Implications & SOP)

- **Actionable directive:** Stage semantic changes and validate exact locators before promotion.
- **Evaluation gate:** Reject unresolved placeholders, stale current claims, and changed graph preimages.
- **Governance constraint:** Preserve source bodies and append-only receipts.

## 关联 (Connections)

- **MOC:** [[maps/domain-mocs/AI Engineering]]
- **Related concepts:** [[wiki/concepts/ai-engineering/Related Concept]]
- **Entities:** [[wiki/entities/products/Example Product]]
- **Source:** [[{source_note}]]

## 演化时间线 (Evolution Timeline)

- **{today.isoformat()}:** Initial compiled understanding from [[{source_note}#^{anchor_1}]].
'''
        draft = self.vault / prepared["concept_draft"]
        draft.write_text(content, encoding="utf-8")
        return draft

    def _successful_run(self) -> tuple[dict, dict]:
        self._write_clipping()
        prepared = self._prepare()
        self.assertEqual(prepared["status"], "STAGED")
        self._write_valid_concept(prepared)
        submitted = self.runtime.submit(prepared["run_id"])
        self.assertEqual(submitted["status"], "VERIFIED", submitted)
        committed = self.runtime.commit(prepared["run_id"], approve_commit=True)
        self.assertEqual(committed["status"], "ARCHIVED", committed)
        return prepared, committed

    def _write_legacy_retrofit_fixture(self, with_anchors: bool = True) -> tuple[Path, Path]:
        source = self.vault / "sources/2026-08/legacy-provenance.md"
        source.parent.mkdir(parents=True, exist_ok=True)
        if with_anchors:
            source_body = (
                "A lineage edge preserves the relationship between evidence and a derived claim. ^legacy-lineage\n\n"
                "A merge must retain the source links of both parent entities. ^legacy-merge\n\n"
                "Deletion reevaluates whether any supporting source remains. ^legacy-delete\n"
            )
        else:
            source_body = "A source without block anchors.\n"
        source.write_text(
            "---\n"
            'title: "Legacy Provenance Source"\n'
            'source_id: "src-legacy-provenance"\n'
            f'source_date: "{date.today().isoformat()}"\n'
            'source_title: "Legacy Provenance Source"\n'
            'source_author: "Example"\n'
            'source_url: "https://example.com/provenance"\n'
            "---\n\n# Legacy Provenance Source\n\n" + source_body,
            encoding="utf-8",
        )
        concept = self.vault / "wiki/concepts/knowledge-systems/Legacy Provenance.md"
        links = (
            "[[sources/legacy-provenance#^legacy-lineage]]\n"
            "[[sources/legacy-provenance#^legacy-merge]]\n"
            "[[sources/legacy-provenance#^legacy-delete]]\n"
            if with_anchors
            else "[[sources/legacy-provenance]]\n"
        )
        concept.parent.mkdir(parents=True, exist_ok=True)
        concept.write_text(
            "---\ntags: [domain/knowledge, type/concept]\nstatus: seed\n---\n\n"
            "# Legacy Provenance\n\nLegacy page body.\n\n" + links,
            encoding="utf-8",
        )
        return source, concept

    def _write_valid_retrofit(self, prepared: dict) -> Path:
        source = prepared["source"]
        anchors = source["anchors"]
        today = date.today()
        next_review = today + timedelta(days=365)
        source_note = source["canonical_relative_path"][:-3]
        content = f'''---
title: "Legacy Provenance"
type: concept
contract_version: "8.1.0"
template_id: concept-gold-standard
template_version: "8.1.0"
url: "https://example.com/provenance"
author: "Example"
date: "{today.isoformat()}"
tags: [domain/knowledge-systems, type/concept]
aliases: ["Legacy Provenance", "旧版溯源"]
status: growing
created: "{today.isoformat()}"
updated: "{today.isoformat()}"
knowledge_stage: stored
evidence_level: single-source
freshness_tier: stable
valid_as_of: "{today.isoformat()}"
last_verified: "{today.isoformat()}"
next_review: "{next_review.isoformat()}"
freshness_status: current
source_ids: ["{source['source_id']}"]
run_id: "{prepared['run_id']}"
---

# Legacy Provenance (旧版溯源)

> [!NOTE] Core Thesis
> Provenance remains useful when it survives derivation, merging, and deletion.
> (Source: [[{source_note}#^{anchors[0]}]])

> [!INFO] Temporal Scope
> Valid as of **{today.isoformat()}** · freshness tier **stable** · next review **{next_review.isoformat()}**.

## 证据范围 (Evidence Scope)

- **Direct evidence:** The source describes lineage, merge, and deletion behavior. (Source: [[{source_note}#^{anchors[0]}]])
- **Interpretation:** A graph representation keeps those relationships traversable.
- **Evidence boundary:** This fixture demonstrates the contract, not every production knowledge graph.
- **Falsifier / counterpoint:** A complete static identifier that survives all three mutations would weaken the graph requirement.
- **Exact locators:** [[{source_note}#^{anchors[0]}]], [[{source_note}#^{anchors[1]}]], [[{source_note}#^{anchors[2]}]]

## 核心机制 (Core Mechanisms)

### 1. Lineage
- Evidence and claims remain connected. (Source: [[{source_note}#^{anchors[0]}]])

### 2. Merge preservation
- Parent source links survive a merge. (Source: [[{source_note}#^{anchors[1]}]])

### 3. Deletion reevaluation
- Remaining support is checked after deletion. (Source: [[{source_note}#^{anchors[2]}]])

## 概念机制图 (Concept Mechanism)

```mermaid
flowchart LR
    A["Source"] --> B["Derived claim"]
    B --> C["Merge or deletion"]
    C --> D["Lineage verification"]
```

## 范式对比矩阵 (Paradigm Matrix)

| Dimension | Static field | Lineage graph |
|---|---|---|
| Derivation | One label | Traversable edge |
| Merge | History may disappear | Parent links retained |
| Deletion | Blind removal | Remaining support checked |
| Trust | Reconstructed | Projected from source |
| Audit | Final value | Full path |

## 关键数据与实证 (Key Data)

- **Verified mechanisms:** 3 anchored mechanisms (as of {today.isoformat()}; Source: [[{source_note}#^{anchors[0]}]])
- **Integration owners:** 1 serial owner (as of {today.isoformat()}; Source: [[{source_note}#^{anchors[1]}]])

## 应用与工程含义 (Implications & SOP)

- **Actionable directive:** Retain provenance edges through graph mutations.
- **Evaluation gate:** Replay merge and deletion scenarios against exact locators.
- **Governance constraint:** Do not rewrite the legacy source during a concept retrofit.

## 关联 (Connections)

- **MOC:** [[maps/domain-mocs/AI Engineering]]
- **Related concepts:** [[wiki/concepts/ai-engineering/Related Concept]]
- **Entities:** [[wiki/entities/products/Example Product]]
- **Source:** [[{source_note}]]

## 演化时间线 (Evolution Timeline)

- **{today.isoformat()}:** Migrated from the legacy page with source bytes preserved.
'''
        draft = self.vault / prepared["concept_draft"]
        draft.write_text(content, encoding="utf-8")
        return draft

    def test_contract_bundle_and_template_hashes_validate(self) -> None:
        bundle = ContractBundle.load()
        self.assertEqual(bundle.version, "8.1.0")
        self.assertIn("knowledge-systems", bundle.domains)

    def test_cli_exit_codes_distinguish_success_from_stop_states(self) -> None:
        self.assertEqual(_exit_code({"status": "NO_OP"}), 0)
        self.assertEqual(_exit_code({"status": "COMMITTED"}), 0)
        self.assertEqual(
            _exit_code(
                {
                    "status": "COMMITTED",
                    "receipt": {"archive_error": "archive destination unavailable"},
                }
            ),
            3,
        )
        for status in (
            "BLOCKED_DEPENDENCY",
            "BLOCKED_PERMISSION",
            "BUDGET_STOP",
            "ERROR",
            "INSUFFICIENT_EVIDENCE",
            "NEEDS_INPUT",
            "NO_PROGRESS",
            "VERIFY_FAILED",
        ):
            with self.subTest(status=status):
                self.assertEqual(_exit_code({"status": status}), 3)

    def test_empty_scan_is_verified_read_only_no_op(self) -> None:
        before = sorted(path.relative_to(self.vault).as_posix() for path in self.vault.rglob("*"))
        result = self.runtime.scan_queue()
        after = sorted(path.relative_to(self.vault).as_posix() for path in self.vault.rglob("*"))
        self.assertEqual(result["status"], "NO_OP")
        self.assertEqual(result["side_effect_count"], 0)
        self.assertEqual(before, after)

    def test_forged_empty_terminal_receipt_cannot_suppress_clipping(self) -> None:
        clipping = self._write_clipping()
        key = self.runtime._idempotency_key(sha256_file(clipping))
        receipt_path = self.runtime._idempotency_path(key)
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        receipt_path.write_text(
            json.dumps(
                {
                    "idempotency_key": key,
                    "contract_version": "8.1.0",
                    "vault_fingerprint": self.runtime.vault_fingerprint,
                    "run_id": "run-forged-empty",
                    "status": "COMMITTED",
                    "mode": "ingest",
                    "input_sha256": sha256_file(clipping),
                    "writes": [],
                }
            ),
            encoding="utf-8",
        )

        scanned = self.runtime.scan_queue()

        self.assertEqual(scanned["status"], "ELIGIBLE")
        self.assertEqual(len(scanned["eligible"]), 1)
        self.assertIn("no canonical writes", scanned["eligible"][0]["receipt_issue"])
        prepared = self._prepare()
        self.assertEqual(prepared["status"], "BLOCKED_DEPENDENCY")
        self.assertNotEqual(prepared["status"], "NO_OP")

    def test_unrelated_source_receipt_cannot_suppress_clipping(self) -> None:
        clipping = self._write_clipping()
        clipping_hash = sha256_file(clipping)
        key = self.runtime._idempotency_key(clipping_hash)
        unrelated_hash = clipping_hash
        unrelated_source = self.vault / "sources/2026-08/unrelated.md"
        unrelated_source.parent.mkdir(parents=True, exist_ok=True)
        unrelated_source.write_text(
            "---\n"
            "source_id: src-unrelated\n"
            f'hash: "sha256:{unrelated_hash}"\n'
            "---\n\n# Unrelated\n",
            encoding="utf-8",
        )
        concept = self.vault / "wiki/concepts/ai-engineering/Related Concept.md"
        map_path = self.vault / self.moc_relative
        receipt = {
            "run_id": "run-forged-unrelated",
            "mode": "ingest",
            "status": "ARCHIVED",
            "contract_version": "8.1.0",
            "vault_fingerprint": self.runtime.vault_fingerprint,
            "idempotency_key": key,
            "input_sha256": clipping_hash,
            "writes": [
                {
                    "relative_path": unrelated_source.relative_to(self.vault).as_posix(),
                    "postimage_sha256": sha256_file(unrelated_source),
                    "kind": "source",
                },
                {
                    "relative_path": concept.relative_to(self.vault).as_posix(),
                    "postimage_sha256": sha256_file(concept),
                    "kind": "concept",
                },
                {
                    "relative_path": map_path.relative_to(self.vault).as_posix(),
                    "postimage_sha256": sha256_file(map_path),
                    "kind": "map",
                },
            ],
            "source_evidence": {
                "path": unrelated_source.relative_to(self.vault).as_posix(),
                "sha256": sha256_file(unrelated_source),
                "source_hash": unrelated_hash,
                "source_id": "src-unrelated",
            },
        }
        forged_archive = self.vault / "Clippings/Archive/Temporal Agent.md"
        forged_archive.parent.mkdir(parents=True, exist_ok=True)
        forged_archive.write_bytes(clipping.read_bytes())
        receipt["archive"] = forged_archive.relative_to(self.vault).as_posix()
        receipt["archive_error"] = None
        receipt_path = self.runtime._idempotency_path(key)
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")

        scanned = self.runtime.scan_queue()

        self.assertEqual(scanned["status"], "ELIGIBLE")
        self.assertIn("does not preserve the expected input", scanned["eligible"][0]["receipt_issue"])

    def test_arbitrary_write_kind_invalidates_terminal_receipt(self) -> None:
        prepared, committed = self._successful_run()
        key = self.runtime._idempotency_key(prepared["source"]["source_hash"])
        receipt_path = self.runtime._idempotency_path(key)
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        receipt["writes"][0]["kind"] = "arbitrary"
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")

        valid, reason, _ = self.runtime._receipt_validity(
            receipt_path,
            key,
            expected_mode="ingest",
            expected_input_sha256=committed["receipt"]["input_sha256"],
            expected_source_hash=prepared["source"]["source_hash"],
        )

        self.assertFalse(valid)
        self.assertIn("source, concept, and map", reason)

    def test_prepare_requires_explicit_staging_approval(self) -> None:
        self._write_clipping()
        with self.assertRaises(PermissionError):
            self.runtime.prepare(
                "Temporal Agent.md",
                concept_title="Temporal Agent Control",
                domain="ai-engineering",
                moc_relative_path=self.moc_relative,
            )
        self.assertFalse((self.vault / "system/runs").exists())

    def test_prepare_preserves_full_source_and_does_not_commit_or_archive(self) -> None:
        clipping = self._write_clipping()
        original_hash = sha256_file(clipping)
        prepared = self._prepare()
        self.assertEqual(prepared["status"], "STAGED")
        source = prepared["source"]
        staged_source = self.vault / source["staging_root"] / "staging" / source["staged_relative_path"]
        self.assertTrue(staged_source.is_file())
        self.assertIn(clipping.read_text(encoding="utf-8"), staged_source.read_text(encoding="utf-8"))
        self.assertEqual(source["source_hash"], original_hash)
        self.assertEqual(len(source["anchors"]), 3)
        self.assertFalse((self.vault / source["canonical_relative_path"]).exists())
        self.assertTrue(clipping.exists())

    def test_unresolved_semantic_template_is_denied(self) -> None:
        self._write_clipping()
        prepared = self._prepare()
        submitted = self.runtime.submit(prepared["run_id"])
        self.assertEqual(submitted["status"], "VERIFY_FAILED")
        codes = {item["code"] for item in submitted["governance"]["findings"]}
        self.assertIn("concept.placeholder", codes)
        self.assertTrue((self.vault / "Clippings/Temporal Agent.md").exists())
        self.assertFalse((self.vault / prepared["source"]["canonical_relative_path"]).exists())

    def test_broken_source_anchor_blocks_promotion(self) -> None:
        self._write_clipping()
        prepared = self._prepare()
        self._write_valid_concept(prepared, broken_anchor=True)
        submitted = self.runtime.submit(prepared["run_id"])
        self.assertEqual(submitted["status"], "VERIFY_FAILED")
        codes = {item["code"] for item in submitted["governance"]["findings"]}
        self.assertIn("concept.anchor.broken", codes)

    def test_end_to_end_commit_archives_and_updates_moc(self) -> None:
        prepared, committed = self._successful_run()
        source_path = self.vault / prepared["source"]["canonical_relative_path"]
        concept_path = self.vault / "wiki/concepts/ai-engineering/temporal-agent-control.md"
        self.assertTrue(source_path.is_file())
        self.assertTrue(concept_path.is_file())
        self.assertFalse((self.vault / "Clippings/Temporal Agent.md").exists())
        self.assertTrue((self.vault / committed["receipt"]["archive"]).is_file())
        moc = (self.vault / self.moc_relative).read_text(encoding="utf-8")
        self.assertIn("Manual content remains here.", moc)
        self.assertIn("third-brain:auto-links:start", moc)
        self.assertIn("wiki/concepts/ai-engineering/temporal-agent-control", moc)
        self.assertEqual(prepared["source"]["source_hash"], sha256_file(self.vault / committed["receipt"]["archive"]))

    def test_archive_failure_stays_repairable_without_replaying_canonical_writes(self) -> None:
        clipping = self._write_clipping()
        prepared = self._prepare()
        self._write_valid_concept(prepared)
        self.assertEqual(self.runtime.submit(prepared["run_id"])["status"], "VERIFIED")

        with patch.object(self.runtime, "_archive", side_effect=OSError("archive unavailable")):
            blocked = self.runtime.commit(prepared["run_id"], approve_commit=True)

        self.assertEqual(blocked["status"], "BLOCKED_DEPENDENCY", blocked)
        self.assertTrue(blocked["canonical_committed"])
        self.assertEqual(blocked["next_action"], "retry_archive_only")
        self.assertTrue(clipping.is_file())
        self.assertTrue((self.vault / prepared["source"]["canonical_relative_path"]).is_file())
        self.assertTrue(
            (self.vault / "wiki/concepts/ai-engineering/temporal-agent-control.md").is_file()
        )
        store = RunStore.find(self.vault, prepared["run_id"])
        manifest = json.loads(store.manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["status"], "ARCHIVE_PENDING")
        self.assertFalse((store.run_dir / "receipt.json").exists())
        self.assertFalse(self.runtime._idempotency_path(manifest["idempotency_key"]).exists())

        scanned = self.runtime.scan_queue()
        self.assertEqual(scanned["status"], "ELIGIBLE")
        self.assertEqual(scanned["eligible"][0]["repair_run_id"], prepared["run_id"])
        self.assertEqual(scanned["eligible"][0]["repair_action"], "retry_archive_only")
        duplicate_prepare = self._prepare(title="Must Not Replay")
        self.assertEqual(duplicate_prepare["status"], "BLOCKED_DEPENDENCY")
        self.assertEqual(duplicate_prepare["repair_run_id"], prepared["run_id"])

        repaired = self.runtime.commit(prepared["run_id"], approve_commit=True)
        self.assertEqual(repaired["status"], "ARCHIVED", repaired)
        self.assertFalse(clipping.exists())
        self.assertTrue((self.vault / repaired["receipt"]["archive"]).is_file())
        self.assertTrue((store.run_dir / "receipt.json").is_file())
        self.assertTrue(self.runtime._idempotency_path(manifest["idempotency_key"]).is_file())
        self.assertEqual(self.runtime.scan_queue()["status"], "NO_OP")

    def test_crash_after_archive_move_recovers_from_durable_destination(self) -> None:
        clipping = self._write_clipping()
        prepared = self._prepare()
        self._write_valid_concept(prepared)
        self.assertEqual(self.runtime.submit(prepared["run_id"])["status"], "VERIFIED")
        original_archive = self.runtime._archive

        def move_then_crash(*args: object, **kwargs: object) -> str:
            original_archive(*args, **kwargs)
            raise OSError("simulated crash after archive move")

        with patch.object(self.runtime, "_archive", side_effect=move_then_crash):
            blocked = self.runtime.commit(prepared["run_id"], approve_commit=True)

        store = RunStore.find(self.vault, prepared["run_id"])
        manifest = json.loads(store.manifest_path.read_text(encoding="utf-8"))
        archive_path = self.vault / manifest["archive_target"]
        self.assertEqual(blocked["status"], "BLOCKED_DEPENDENCY")
        self.assertFalse(clipping.exists())
        self.assertTrue(archive_path.is_file())
        self.assertFalse((store.run_dir / "receipt.json").exists())
        self.assertFalse(self.runtime._idempotency_path(manifest["idempotency_key"]).exists())
        scanned = self.runtime.scan_queue()
        self.assertEqual(scanned["status"], "ELIGIBLE")
        self.assertEqual(scanned["eligible"][0]["repair_run_id"], prepared["run_id"])
        self.assertFalse(scanned["eligible"][0]["clipping_present"])
        self.assertTrue(scanned["eligible"][0]["archive_present"])

        recovered = self.runtime.commit(prepared["run_id"], approve_commit=True)

        self.assertEqual(recovered["status"], "ARCHIVED", recovered)
        self.assertEqual(recovered["receipt"]["archive"], manifest["archive_target"])
        self.assertTrue(archive_path.is_file())

    def test_no_archive_is_nonterminal_and_retryable(self) -> None:
        clipping = self._write_clipping()
        prepared = self._prepare()
        self._write_valid_concept(prepared)
        self.assertEqual(self.runtime.submit(prepared["run_id"])["status"], "VERIFIED")

        deferred = self.runtime.commit(
            prepared["run_id"], approve_commit=True, archive=False
        )

        store = RunStore.find(self.vault, prepared["run_id"])
        manifest = json.loads(store.manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(deferred["status"], "BLOCKED_DEPENDENCY")
        self.assertEqual(manifest["status"], "ARCHIVE_PENDING")
        self.assertTrue(clipping.is_file())
        self.assertFalse((store.run_dir / "receipt.json").exists())
        self.assertFalse(self.runtime._idempotency_path(manifest["idempotency_key"]).exists())

        repaired = self.runtime.commit(prepared["run_id"], approve_commit=True)

        self.assertEqual(repaired["status"], "ARCHIVED", repaired)
        self.assertFalse(clipping.exists())

    def test_duplicate_clipping_is_no_op_and_does_not_duplicate_source(self) -> None:
        prepared, _ = self._successful_run()
        archived = next((self.vault / "Clippings/Archive").glob("Temporal Agent*.md"))
        duplicate = self.vault / "Clippings/Duplicate.md"
        duplicate.write_bytes(archived.read_bytes())
        result = self.runtime.prepare(
            "Duplicate.md",
            concept_title="Another Concept",
            domain="ai-engineering",
            moc_relative_path=self.moc_relative,
            approve_staging=True,
        )
        self.assertEqual(result["status"], "NO_OP")
        self.assertEqual(len(list((self.vault / "sources").rglob("*.md"))), 1)
        self.assertEqual(prepared["source"]["source_hash"], sha256_file(duplicate))

    def test_changed_content_at_same_url_creates_new_snapshot_thread(self) -> None:
        prepared, _ = self._successful_run()
        self._write_clipping(name="Changed.md", changed=True)
        second = self.runtime.prepare(
            "Changed.md",
            concept_title="Temporal Agent Revision",
            domain="ai-engineering",
            moc_relative_path=self.moc_relative,
            approve_staging=True,
        )
        self.assertEqual(second["status"], "STAGED")
        self.assertNotEqual(second["source"]["source_id"], prepared["source"]["source_id"])
        self.assertIn(prepared["source"]["canonical_relative_path"], second["source"]["prior_snapshot_paths"])

    def test_changed_moc_preimage_blocks_all_canonical_writes(self) -> None:
        self._write_clipping()
        prepared = self._prepare()
        self._write_valid_concept(prepared)
        self.assertEqual(self.runtime.submit(prepared["run_id"])["status"], "VERIFIED")
        with (self.vault / self.moc_relative).open("a", encoding="utf-8") as handle:
            handle.write("\nConcurrent manual edit.\n")
        result = self.runtime.commit(prepared["run_id"], approve_commit=True)
        self.assertEqual(result["status"], "BLOCKED_DEPENDENCY")
        self.assertFalse((self.vault / prepared["source"]["canonical_relative_path"]).exists())
        self.assertFalse((self.vault / "wiki/concepts/ai-engineering/temporal-agent-control.md").exists())
        self.assertTrue((self.vault / "Clippings/Temporal Agent.md").exists())

    def test_freshness_scan_surfaces_stale_and_unknown_notes(self) -> None:
        stale = self.vault / "wiki/concepts/ai-engineering/Stale.md"
        stale.write_text(
            "---\n"
            "title: Stale\n"
            "type: concept\n"
            "freshness_tier: volatile\n"
            "valid_as_of: 2020-01-01\n"
            "last_verified: 2020-01-01\n"
            "next_review: 2020-01-08\n"
            "freshness_status: stale\n"
            "---\n# Stale\n",
            encoding="utf-8",
        )
        result = self.runtime.freshness_scan(today=date(2026, 8, 16))
        self.assertEqual(result["status"], "DUE")
        matches = [item for item in result["findings"] if item["path"].endswith("Stale.md")]
        self.assertEqual(matches[0]["status"], "stale")
        self.assertEqual(result["side_effect_count"], 0)

    def test_future_snapshot_valid_as_of_is_unknown(self) -> None:
        future = self.vault / "wiki/concepts/ai-engineering/Future Snapshot.md"
        future.write_text(
            "---\n"
            "title: Future Snapshot\n"
            "type: concept\n"
            "freshness_tier: snapshot\n"
            "valid_as_of: 2099-01-01\n"
            "---\n# Future Snapshot\n",
            encoding="utf-8",
        )

        result = self.runtime.freshness_scan(today=date(2026, 8, 16))
        match = next(item for item in result["findings"] if item["path"].endswith("Future Snapshot.md"))

        self.assertEqual(match["status"], "unknown")
        self.assertIn("future", match["reason"])

    def test_inventory_is_read_only_and_classifies_retrofit_debt(self) -> None:
        before = sorted(path.relative_to(self.vault).as_posix() for path in self.vault.rglob("*"))
        result = self.runtime.inventory(limit=10)
        after = sorted(path.relative_to(self.vault).as_posix() for path in self.vault.rglob("*"))
        self.assertEqual(result["status"], "INVENTORIED")
        self.assertGreaterEqual(result["wiki"]["retrofit_counts"]["INSUFFICIENT_EVIDENCE"], 1)
        self.assertEqual(result["side_effect_count"], 0)
        self.assertEqual(before, after)

    def test_retrofit_updates_concept_and_map_without_mutating_source(self) -> None:
        source, concept = self._write_legacy_retrofit_fixture()
        source_hash = sha256_file(source)
        old_concept_hash = sha256_file(concept)
        prepared = self.runtime.prepare_retrofit(
            "wiki/concepts/knowledge-systems/Legacy Provenance.md",
            moc_relative_path=self.moc_relative,
            approve_staging=True,
        )
        self.assertEqual(prepared["status"], "STAGED")
        self._write_valid_retrofit(prepared)
        self.assertEqual(self.runtime.submit(prepared["run_id"])["status"], "VERIFIED")
        committed = self.runtime.commit(prepared["run_id"], approve_commit=True)
        self.assertEqual(committed["status"], "COMMITTED")
        self.assertEqual(sha256_file(source), source_hash)
        self.assertNotEqual(sha256_file(concept), old_concept_hash)
        self.assertIn('contract_version: "8.1.0"', concept.read_text(encoding="utf-8"))
        self.assertIsNone(committed["receipt"]["archive"])

    def test_retrofit_preimage_conflict_preserves_concurrent_edit(self) -> None:
        source, concept = self._write_legacy_retrofit_fixture()
        source_hash = sha256_file(source)
        prepared = self.runtime.prepare_retrofit(
            "wiki/concepts/knowledge-systems/Legacy Provenance.md",
            moc_relative_path=self.moc_relative,
            approve_staging=True,
        )
        self._write_valid_retrofit(prepared)
        self.assertEqual(self.runtime.submit(prepared["run_id"])["status"], "VERIFIED")
        with concept.open("a", encoding="utf-8") as handle:
            handle.write("\nConcurrent human note.\n")
        concurrent_hash = sha256_file(concept)
        result = self.runtime.commit(prepared["run_id"], approve_commit=True)
        self.assertEqual(result["status"], "BLOCKED_DEPENDENCY")
        self.assertEqual(sha256_file(concept), concurrent_hash)
        self.assertEqual(sha256_file(source), source_hash)

    def test_retrofit_without_three_resolvable_anchors_is_read_only_failure(self) -> None:
        _, concept = self._write_legacy_retrofit_fixture(with_anchors=False)
        before_hash = sha256_file(concept)
        result = self.runtime.prepare_retrofit(
            "wiki/concepts/knowledge-systems/Legacy Provenance.md",
            moc_relative_path=self.moc_relative,
            approve_staging=True,
        )
        self.assertEqual(result["status"], "INSUFFICIENT_EVIDENCE")
        self.assertEqual(result["side_effect_count"], 0)
        self.assertEqual(sha256_file(concept), before_hash)


if __name__ == "__main__":
    unittest.main()
