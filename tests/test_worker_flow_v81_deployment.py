from __future__ import annotations

import shutil
import tempfile
import unittest
import json
from unittest.mock import patch
from datetime import date, timedelta
from pathlib import Path

from tools.worker_flow.runtime import WorkerFlowRuntime, WorkflowError
import tools.worker_flow.runtime as runtime_module
from tools.worker_flow.governance import Finding, GovernanceReport
from tools.worker_flow.schema import validate_schema
from tools.worker_flow.state import RunStore
from tools.worker_flow.utils import atomic_write_json, canonical_json_sha256, read_json, sha256_file


class WorkerFlowV81DeploymentTest(unittest.TestCase):
    """Acceptance tests for the two non-clipping V8.1 deployment lanes."""

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp())
        self.project_root = Path(__file__).resolve().parents[1]
        self.repo = self.temp_dir / "Repository"
        self._copy_runtime_bundle_inputs()
        self.vault = self._create_vault("Test Vault")
        self.runtime = WorkerFlowRuntime(self.vault, repo_root=self.repo)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _copy_runtime_bundle_inputs(self) -> None:
        shutil.copytree(self.project_root / "contracts", self.repo / "contracts")
        bundle = json.loads((self.project_root / "contracts/system-bundle.json").read_text(encoding="utf-8"))
        for relative in {str(entry["source"]) for entry in bundle["entries"]}:
            source = self.project_root / relative
            target = self.repo / relative
            if target.is_file():
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)

    def _create_vault(self, name: str) -> Path:
        vault = self.temp_dir / name
        for relative in (
            "Clippings",
            "sources",
            "wiki/concepts/knowledge-systems",
            "wiki/entities/products",
            "maps/domain-mocs",
            "system",
        ):
            (vault / relative).mkdir(parents=True, exist_ok=True)
        (vault / "system/config.md").write_text(
            "---\ntitle: Test Vault Config\nversion: 8.1.0\n---\n",
            encoding="utf-8",
        )
        (vault / "maps/domain-mocs/Knowledge Systems.md").write_text(
            "---\n"
            'title: "Knowledge Systems"\n'
            "type: map\n"
            'contract_version: "8.1.0"\n'
            "map_tier: domain-moc\n"
            "status: active\n"
            f'updated: "{date.today().isoformat()}"\n'
            "---\n\n# Knowledge Systems\n\nManual map content.\n",
            encoding="utf-8",
        )
        (vault / "wiki/concepts/knowledge-systems/Related Concept.md").write_text(
            "---\ntitle: Related Concept\ntype: concept\n---\n# Related Concept\n",
            encoding="utf-8",
        )
        (vault / "wiki/entities/products/Obsidian.md").write_text(
            "---\ntitle: Obsidian\ntype: entity\n---\n# Obsidian\n",
            encoding="utf-8",
        )
        return vault

    def _write_local_markdown(self) -> Path:
        local_input = self.repo / "docs/local-knowledge-automation.md"
        local_input.write_text(
            "---\n"
            'title: "Repository Local Knowledge Automation"\n'
            'author: "Third Brain Team"\n'
            f'date: "{date.today().isoformat()}"\n'
            "---\n\n"
            "# Repository Local Knowledge Automation\n\n"
            "A repository document can be captured as an immutable evidence snapshot before any semantic promotion.\n\n"
            "The semantic concept remains staged until an independent governance pass validates exact source anchors.\n\n"
            "A serial compare-and-set commit updates the source, concept, and map as one governed unit.\n",
            encoding="utf-8",
        )
        return local_input

    def _write_local_concept_candidate(self, prepared: dict) -> Path:
        source = prepared["source"]
        anchors = source["anchors"]
        self.assertGreaterEqual(len(anchors), 3)
        source_note = source["canonical_relative_path"].removesuffix(".md")
        today = date.today()
        next_review = today + timedelta(days=365)
        candidate = self.repo / "candidates/repository-local-knowledge.md"
        candidate.parent.mkdir(parents=True, exist_ok=True)
        candidate.write_text(
            f'''---
title: "Repository Local Knowledge"
type: concept
contract_version: "8.1.0"
template_id: concept-gold-standard
template_version: "8.1.0"
author: "Third Brain Team"
date: "{today.isoformat()}"
tags: [domain/knowledge-systems, type/concept]
aliases: ["Repository Local Knowledge", "仓库本地知识"]
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

# Repository Local Knowledge (仓库本地知识)

> [!NOTE] Core Thesis
> Repository Markdown should cross an immutable evidence boundary before it becomes a governed concept.
> (Source: [[{source_note}#^{anchors[0]}]])

> [!INFO] Temporal Scope
> Valid as of **{today.isoformat()}** · freshness tier **stable** · next review **{next_review.isoformat()}**.

## 证据范围 (Evidence Scope)

- **Direct evidence:** The local document describes snapshot, validation, and serial-commit boundaries. (Source: [[{source_note}#^{anchors[1]}]])
- **Interpretation:** Those boundaries form a non-clipping ingestion lane.
- **Evidence boundary:** One repository example does not establish reliability for every source format.
- **Falsifier / counterpoint:** A commit that succeeds before candidate validation would falsify the governance claim.
- **Exact locators:** [[{source_note}#^{anchors[0]}]], [[{source_note}#^{anchors[1]}]]

## 核心机制 (Core Mechanisms)

### 1. Immutable local capture

- Preserve the repository input before semantic transformation. (Source: [[{source_note}#^{anchors[0]}]])

### 2. Candidate validation

- Validate evidence anchors while the concept is still staged. (Source: [[{source_note}#^{anchors[1]}]])

### 3. Serial promotion

- Commit the source, concept, and map through one compare-and-set boundary. (Source: [[{source_note}#^{anchors[2]}]])

## 概念机制图 (Concept Mechanism)

```mermaid
flowchart TD
    A["Repository Markdown"] --> B["Immutable source"]
    B --> C["Semantic candidate"]
    C --> D["Governance validation"]
    D --> E["Transactional promotion"]
```

## 范式对比矩阵 (Paradigm Matrix)

| Dimension | Direct copy | Governed local ingest |
|---|---|---|
| Evidence | Mutable file | Immutable snapshot |
| Semantics | Unchecked | Validated candidate |
| Graph | Manual drift | Transactional map delta |
| Replay | Duplicate-prone | Idempotent receipt |

## 关键数据与实证 (Key Data)

- **Evidence anchors:** At least 3 source blocks are required. (Source: [[{source_note}#^{anchors[0]}]])
- **Commit boundary:** One serial transaction applies the promotion. (Source: [[{source_note}#^{anchors[2]}]])

## 应用与工程含义 (Implications & SOP)

- **Actionable directive:** Capture local Markdown, author a candidate, validate it, then commit.
- **Evaluation gate:** Deny promotion before a passing governance receipt.
- **Governance constraint:** Never route repository-local input through the clipping archive lifecycle.

## 关联 (Connections)

- **MOC:** [[maps/domain-mocs/Knowledge Systems]]
- **Related concept:** [[wiki/concepts/knowledge-systems/Related Concept]]
- **Entity:** [[wiki/entities/products/Obsidian]]
- **Source:** [[{source_note}]]

## 演化时间线 (Evolution Timeline)

- **{today.isoformat()}:** Defined the repository-local governed ingestion lane from [[{source_note}#^{anchors[0]}]].
''',
            encoding="utf-8",
        )
        return candidate

    def _expected_system_bundle(self) -> dict[str, Path]:
        bundle = json.loads((self.repo / "contracts/system-bundle.json").read_text(encoding="utf-8"))
        return {
            str(entry["target"]): self.repo / str(entry["source"])
            for entry in bundle["entries"]
        }

    def _prepare_verified_local(self, local_input: Path, concept_title: str) -> dict:
        prepared = self.runtime.prepare_local(
            local_input,
            concept_title=concept_title,
            domain="knowledge-systems",
            moc_relative_path="maps/domain-mocs/Knowledge Systems.md",
            approve_staging=True,
        )
        candidate = self._write_local_concept_candidate(prepared)
        if concept_title != "Repository Local Knowledge":
            candidate.write_text(
                candidate.read_text(encoding="utf-8").replace(
                    "Repository Local Knowledge", concept_title
                ),
                encoding="utf-8",
            )
        self.runtime.stage_candidate(prepared["run_id"], candidate, approve_staging=True)
        submitted = self.runtime.submit(prepared["run_id"])
        self.assertEqual(submitted["status"], "VERIFIED", submitted)
        return prepared

    def _crash_verified_local_after_canonical_writes(self) -> tuple[dict, RunStore]:
        local_input = self._write_local_markdown()
        prepared = self._prepare_verified_local(local_input, "Repository Local Knowledge")
        original_atomic_write_json = runtime_module.atomic_write_json
        crashed = False

        def crash_before_terminal_receipt(path: Path, value: object) -> None:
            nonlocal crashed
            if Path(path).name == "receipt.json" and not crashed:
                crashed = True
                raise OSError("simulated process crash before terminal receipt")
            original_atomic_write_json(path, value)

        with patch(
            "tools.worker_flow.runtime.atomic_write_json",
            side_effect=crash_before_terminal_receipt,
        ):
            with self.assertRaises(OSError):
                self.runtime.commit(prepared["run_id"], approve_commit=True)
        store = RunStore.find(self.vault, prepared["run_id"])
        self.assertEqual(store.load_state()["status"], "COMMITTING")
        return prepared, store

    def test_repository_local_ingest_requires_validation_commits_without_archive_and_is_idempotent(self) -> None:
        local_input = self._write_local_markdown()
        prepared = self.runtime.prepare_local(
            local_input,
            concept_title="Repository Local Knowledge",
            domain="knowledge-systems",
            moc_relative_path="maps/domain-mocs/Knowledge Systems.md",
            source_type="local-synthesis",
            input_class="internal-state",
            freshness_tier="stable",
            approve_staging=True,
        )

        self.assertEqual(prepared["status"], "STAGED")
        self.assertEqual(prepared["mode"], "local-ingest")
        store = RunStore.find(self.vault, prepared["run_id"])
        manifest = read_json(store.manifest_path)
        self.assertEqual(manifest["mode"], "local-ingest")
        self.assertIsNone(manifest.get("clipping"))
        staged_source = store.run_dir / "staging" / prepared["source"]["staged_relative_path"]
        self.assertTrue(staged_source.is_file())
        self.assertIn(local_input.read_text(encoding="utf-8"), staged_source.read_text(encoding="utf-8"))
        source_target = self.vault / prepared["source"]["canonical_relative_path"]
        concept_target = self.vault / manifest["concept"]["target_relative_path"]
        self.assertFalse(source_target.exists())
        self.assertFalse(concept_target.exists())
        with self.assertRaises(WorkflowError):
            self.runtime.commit(prepared["run_id"], approve_commit=True)

        candidate = self._write_local_concept_candidate(prepared)
        authored = self.runtime.stage_candidate(
            prepared["run_id"], candidate, approve_staging=True
        )
        self.assertEqual(authored["status"], "AUTHORED")
        submitted = self.runtime.submit(prepared["run_id"])
        self.assertEqual(submitted["status"], "VERIFIED", submitted)
        committed = self.runtime.commit(prepared["run_id"], approve_commit=True)
        self.assertEqual(committed["status"], "COMMITTED", committed)
        self.assertIsNone(committed["receipt"]["archive"])
        self.assertTrue(source_target.is_file())
        self.assertTrue(concept_target.is_file())
        self.assertIn(
            "wiki/concepts/knowledge-systems/repository-local-knowledge",
            (self.vault / "maps/domain-mocs/Knowledge Systems.md").read_text(encoding="utf-8"),
        )
        self.assertEqual(
            prepared["source"]["source_hash"],
            sha256_file(local_input),
        )
        archive = self.vault / "Clippings/Archive"
        self.assertFalse(archive.exists() and any(archive.iterdir()))

        source_count = len(list((self.vault / "sources").rglob("*.md")))
        run_count = len(list((self.vault / "system/runs").rglob("manifest.json")))
        repeated = self.runtime.prepare_local(
            local_input,
            concept_title="Repository Local Knowledge",
            domain="knowledge-systems",
            moc_relative_path="maps/domain-mocs/Knowledge Systems.md",
            source_type="local-synthesis",
            input_class="internal-state",
            freshness_tier="stable",
            approve_staging=True,
        )
        self.assertEqual(repeated["status"], "NO_OP")
        self.assertEqual(len(list((self.vault / "sources").rglob("*.md"))), source_count)
        self.assertEqual(
            len(list((self.vault / "system/runs").rglob("manifest.json"))), run_count
        )
        self.assertFalse(archive.exists() and any(archive.iterdir()))

    def test_reused_canonical_source_mutation_after_governance_blocks_commit(self) -> None:
        local_input = self._write_local_markdown()
        first = self._prepare_verified_local(local_input, "Repository Local Knowledge")
        first_commit = self.runtime.commit(first["run_id"], approve_commit=True)
        self.assertEqual(first_commit["status"], "COMMITTED", first_commit)

        duplicate_input = self.repo / "docs/local-knowledge-automation-copy.md"
        duplicate_input.write_bytes(local_input.read_bytes())
        second = self._prepare_verified_local(duplicate_input, "Repository Source Reuse")
        self.assertIsNone(second["source"]["staged_relative_path"])
        source_path = self.vault / second["source"]["canonical_relative_path"]
        map_path = self.vault / "maps/domain-mocs/Knowledge Systems.md"
        map_preimage = sha256_file(map_path)
        with source_path.open("a", encoding="utf-8") as handle:
            handle.write("\nConcurrent source mutation after Governance.\n")
        mutated_source_hash = sha256_file(source_path)

        committed = self.runtime.commit(second["run_id"], approve_commit=True)

        self.assertEqual(committed["status"], "BLOCKED_DEPENDENCY")
        self.assertEqual(sha256_file(source_path), mutated_source_hash)
        self.assertEqual(sha256_file(map_path), map_preimage)
        self.assertFalse(
            (self.vault / "wiki/concepts/knowledge-systems/repository-source-reuse.md").exists()
        )

    def test_reused_source_race_during_post_validation_rolls_back_derived_writes(self) -> None:
        local_input = self._write_local_markdown()
        first = self._prepare_verified_local(local_input, "Repository Local Knowledge")
        self.assertEqual(
            self.runtime.commit(first["run_id"], approve_commit=True)["status"],
            "COMMITTED",
        )
        duplicate_input = self.repo / "docs/local-knowledge-race-copy.md"
        duplicate_input.write_bytes(local_input.read_bytes())
        second = self._prepare_verified_local(duplicate_input, "Repository Source Race")
        source_path = self.vault / second["source"]["canonical_relative_path"]
        map_path = self.vault / "maps/domain-mocs/Knowledge Systems.md"
        map_preimage = sha256_file(map_path)
        original_validate_concept = runtime_module.validate_concept
        raced = False

        def mutate_source_after_concept_validation(*args, **kwargs):
            nonlocal raced
            report = original_validate_concept(*args, **kwargs)
            if not raced:
                raced = True
                with source_path.open("a", encoding="utf-8") as handle:
                    handle.write("\nConcurrent mutation inside the post-check window.\n")
            return report

        with patch(
            "tools.worker_flow.runtime.validate_concept",
            side_effect=mutate_source_after_concept_validation,
        ):
            committed = self.runtime.commit(second["run_id"], approve_commit=True)

        self.assertEqual(committed["status"], "VERIFY_FAILED", committed)
        self.assertTrue(raced)
        self.assertIn("Concurrent mutation", source_path.read_text(encoding="utf-8"))
        self.assertEqual(sha256_file(map_path), map_preimage)
        self.assertFalse(
            (self.vault / "wiki/concepts/knowledge-systems/repository-source-race.md").exists()
        )

    def test_system_bundle_deploy_is_deterministic_transactional_and_idempotent(self) -> None:
        expected = self._expected_system_bundle()
        inventory_before = self.runtime.inventory(limit=10)
        prepared = self.runtime.prepare_system_bundle(approve_staging=True)
        self.assertEqual(prepared["status"], "STAGED")
        self.assertEqual(prepared["mode"], "system-bundle")
        store = RunStore.find(self.vault, prepared["run_id"])
        manifest = read_json(store.manifest_path)
        self.assertEqual(manifest["mode"], "system-bundle")
        for target_relative, repository_source in expected.items():
            staged = store.run_dir / "staging" / target_relative
            self.assertTrue(staged.is_file(), target_relative)
            self.assertEqual(staged.read_bytes(), repository_source.read_bytes(), target_relative)
            self.assertFalse((self.vault / target_relative).exists(), target_relative)

        submitted = self.runtime.submit(prepared["run_id"])
        self.assertEqual(submitted["status"], "VERIFIED", submitted)
        committed = self.runtime.commit(prepared["run_id"], approve_commit=True)
        self.assertEqual(committed["status"], "COMMITTED", committed)
        self.assertIsNone(committed["receipt"]["archive"])
        for target_relative, repository_source in expected.items():
            target = self.vault / target_relative
            self.assertTrue(target.is_file(), target_relative)
            self.assertEqual(target.read_bytes(), repository_source.read_bytes(), target_relative)
        inventory_after = self.runtime.inventory(limit=10)
        for section in ("missing_frontmatter", "unresolved_template_tokens"):
            self.assertLessEqual(
                inventory_after[section]["system"]["count"],
                inventory_before[section]["system"]["count"],
                section,
            )
        self.assertLessEqual(
            inventory_after["version_counts"]["system"].get("unversioned", 0),
            inventory_before["version_counts"]["system"].get("unversioned", 0),
        )
        self.assertLessEqual(
            inventory_after["system"]["debt_count"],
            inventory_before["system"]["debt_count"],
        )
        self.assertGreater(inventory_after["system"]["excluded_artifacts"]["count"], 0)
        self.assertEqual(
            committed["receipt"]["inventory_observed"],
            committed["receipt"]["inventory_baseline"],
        )

        canonical_hashes = {
            target: sha256_file(self.vault / target) for target in expected
        }
        run_count = len(list((self.vault / "system/runs").rglob("manifest.json")))
        repeated = self.runtime.prepare_system_bundle(approve_staging=True)
        self.assertEqual(repeated["status"], "NO_OP")
        self.assertEqual(
            len(list((self.vault / "system/runs").rglob("manifest.json"))), run_count
        )
        self.assertEqual(
            {target: sha256_file(self.vault / target) for target in expected},
            canonical_hashes,
        )

        conflict_vault = self._create_vault("Conflict Vault")
        conflict_runtime = WorkerFlowRuntime(conflict_vault, repo_root=self.repo)
        conflict_target_relative = "system/templates/template-source-v8.1.md"
        conflict_target = conflict_vault / conflict_target_relative
        conflict_target.parent.mkdir(parents=True, exist_ok=True)
        conflict_target.write_text("legacy operator-owned template\n", encoding="utf-8")
        conflict_prepared = conflict_runtime.prepare_system_bundle(approve_staging=True)
        self.assertEqual(conflict_prepared["status"], "STAGED")
        self.assertEqual(
            conflict_runtime.submit(conflict_prepared["run_id"])["status"], "VERIFIED"
        )
        conflict_target.write_text("concurrent operator edit\n", encoding="utf-8")
        blocked = conflict_runtime.commit(
            conflict_prepared["run_id"], approve_commit=True
        )
        self.assertEqual(blocked["status"], "BLOCKED_DEPENDENCY")
        self.assertEqual(
            conflict_target.read_text(encoding="utf-8"), "concurrent operator edit\n"
        )
        for target_relative in expected:
            if target_relative != conflict_target_relative:
                self.assertFalse(
                    (conflict_vault / target_relative).exists(),
                    f"partial canonical write escaped preflight: {target_relative}",
                )

    def test_system_manifest_tampering_cannot_escape_system_boundary(self) -> None:
        prepared = self.runtime.prepare_system_bundle(approve_staging=True)
        store = RunStore.find(self.vault, prepared["run_id"])
        manifest = read_json(store.manifest_path)
        manifest["system_entries"][0]["target_relative_path"] = "wiki/escaped-contract.json"
        atomic_write_json(store.manifest_path, manifest)

        submitted = self.runtime.submit(prepared["run_id"])
        self.assertEqual(submitted["status"], "VERIFY_FAILED")
        self.assertFalse((self.vault / "wiki/escaped-contract.json").exists())
        with self.assertRaises(WorkflowError):
            self.runtime.commit(prepared["run_id"], approve_commit=True)

    def test_worker_receipt_schema_is_enforced_at_submit_and_commit(self) -> None:
        local_input = self._write_local_markdown()
        prepared = self._prepare_verified_local(local_input, "Repository Local Knowledge")
        store = RunStore.find(self.vault, prepared["run_id"])
        manifest = read_json(store.manifest_path)
        receipt_path = self.vault / manifest["governance_receipt"]
        receipt = read_json(receipt_path)
        self.assertEqual(
            validate_schema(receipt, self.runtime.contracts.schema("worker_receipt")),
            [],
        )
        receipt["forged_extra_field"] = True
        self.assertTrue(
            any(
                "additional property" in violation
                for violation in validate_schema(
                    receipt, self.runtime.contracts.schema("worker_receipt")
                )
            )
        )
        atomic_write_json(receipt_path, receipt)

        committed = self.runtime.commit(prepared["run_id"], approve_commit=True)

        self.assertEqual(committed["status"], "VERIFY_FAILED")
        self.assertIn("additional property", committed["error"])
        self.assertFalse((self.vault / prepared["source"]["canonical_relative_path"]).exists())
        self.assertFalse(
            (self.vault / manifest["concept"]["target_relative_path"]).exists()
        )

    def test_verified_candidate_mutation_is_rejected_before_any_canonical_write(self) -> None:
        local_input = self._write_local_markdown()
        prepared = self.runtime.prepare_local(
            local_input,
            concept_title="Repository Local Knowledge",
            domain="knowledge-systems",
            moc_relative_path="maps/domain-mocs/Knowledge Systems.md",
            approve_staging=True,
        )
        candidate = self._write_local_concept_candidate(prepared)
        self.runtime.stage_candidate(prepared["run_id"], candidate, approve_staging=True)
        self.assertEqual(self.runtime.submit(prepared["run_id"])["status"], "VERIFIED")
        with self.assertRaises(WorkflowError):
            self.runtime.stage_candidate(prepared["run_id"], candidate, approve_staging=True)

        store = RunStore.find(self.vault, prepared["run_id"])
        manifest = read_json(store.manifest_path)
        staged_concept = store.run_dir / "staging" / manifest["concept"]["staged_relative_path"]
        with staged_concept.open("a", encoding="utf-8") as handle:
            handle.write("\nPost-verification mutation.\n")
        committed = self.runtime.commit(prepared["run_id"], approve_commit=True)
        self.assertEqual(committed["status"], "VERIFY_FAILED")
        self.assertFalse((self.vault / prepared["source"]["canonical_relative_path"]).exists())
        self.assertFalse((self.vault / manifest["concept"]["target_relative_path"]).exists())

    def test_post_commit_source_failure_rolls_back_new_source_and_derived_writes(self) -> None:
        local_input = self._write_local_markdown()
        prepared = self.runtime.prepare_local(
            local_input,
            concept_title="Repository Local Knowledge",
            domain="knowledge-systems",
            moc_relative_path="maps/domain-mocs/Knowledge Systems.md",
            approve_staging=True,
        )
        candidate = self._write_local_concept_candidate(prepared)
        self.runtime.stage_candidate(prepared["run_id"], candidate, approve_staging=True)
        self.assertEqual(self.runtime.submit(prepared["run_id"])["status"], "VERIFIED")
        store = RunStore.find(self.vault, prepared["run_id"])
        manifest = read_json(store.manifest_path)
        map_path = self.vault / "maps/domain-mocs/Knowledge Systems.md"
        map_preimage = sha256_file(map_path)
        denied = GovernanceReport(
            False,
            (Finding("source.synthetic-post-failure", "P0", "forced post-check failure", prepared["source"]["canonical_relative_path"]),),
            ("forced-post-check",),
        )
        with patch("tools.worker_flow.runtime.validate_source", return_value=denied):
            committed = self.runtime.commit(prepared["run_id"], approve_commit=True)
        self.assertEqual(committed["status"], "VERIFY_FAILED")
        self.assertFalse((self.vault / prepared["source"]["canonical_relative_path"]).exists())
        self.assertFalse((self.vault / manifest["concept"]["target_relative_path"]).exists())
        self.assertEqual(sha256_file(map_path), map_preimage)

    def test_crash_after_canonical_writes_resumes_from_durable_intent(self) -> None:
        local_input = self._write_local_markdown()
        prepared = self.runtime.prepare_local(
            local_input,
            concept_title="Repository Local Knowledge",
            domain="knowledge-systems",
            moc_relative_path="maps/domain-mocs/Knowledge Systems.md",
            approve_staging=True,
        )
        candidate = self._write_local_concept_candidate(prepared)
        self.runtime.stage_candidate(prepared["run_id"], candidate, approve_staging=True)
        self.assertEqual(self.runtime.submit(prepared["run_id"])["status"], "VERIFIED")
        original_atomic_write_json = runtime_module.atomic_write_json
        crashed = False

        def crash_before_terminal_receipt(path: Path, value: object) -> None:
            nonlocal crashed
            if Path(path).name == "receipt.json" and not crashed:
                crashed = True
                raise OSError("simulated process crash before terminal receipt")
            original_atomic_write_json(path, value)

        with patch(
            "tools.worker_flow.runtime.atomic_write_json",
            side_effect=crash_before_terminal_receipt,
        ):
            with self.assertRaises(OSError):
                self.runtime.commit(prepared["run_id"], approve_commit=True)

        store = RunStore.find(self.vault, prepared["run_id"])
        self.assertEqual(store.load_state()["status"], "COMMITTING")
        self.assertTrue((store.run_dir / "commit-intent.json").is_file())
        self.assertTrue((store.run_dir / "receipts/canonical-commit.json").is_file())

        resumed = self.runtime.commit(prepared["run_id"], approve_commit=True)
        self.assertEqual(resumed["status"], "COMMITTED", resumed)
        self.assertTrue((self.vault / prepared["source"]["canonical_relative_path"]).is_file())
        self.assertTrue((store.run_dir / "receipt.json").is_file())

    def test_recovery_rejects_expired_approval_without_terminal_receipt(self) -> None:
        _, store = self._crash_verified_local_after_canonical_writes()
        approval_path = store.run_dir / "receipts/commit-approval.json"
        approval = read_json(approval_path)
        approval["approved_at"] = "1999-01-01T00:00:00Z"
        approval["expires_at"] = "2000-01-01T00:00:00Z"
        atomic_write_json(approval_path, approval)
        intent_path = store.run_dir / "commit-intent.json"
        intent = read_json(intent_path)
        intent["approval_sha256"] = sha256_file(approval_path)
        atomic_write_json(intent_path, intent)

        resumed = self.runtime.commit(store.run_id, approve_commit=True)

        self.assertEqual(resumed["status"], "BLOCKED_PERMISSION")
        self.assertIn("expired", resumed["error"])
        self.assertFalse((store.run_dir / "receipt.json").exists())
        manifest = read_json(store.manifest_path)
        self.assertFalse(self.runtime._idempotency_path(manifest["idempotency_key"]).exists())

    def test_recovery_rejects_tampered_scope_without_terminal_receipt(self) -> None:
        _, store = self._crash_verified_local_after_canonical_writes()
        approval_path = store.run_dir / "receipts/commit-approval.json"
        approval = read_json(approval_path)
        forged_scope = list(approval["scope"])
        forged_scope.append(
            {
                "relative_path": "wiki/escaped.md",
                "kind": "concept",
                "expected_preimage_sha256": None,
                "postimage_sha256": "0" * 64,
            }
        )
        approval["scope"] = forged_scope
        approval["scope_hash"] = canonical_json_sha256(forged_scope)
        atomic_write_json(approval_path, approval)
        intent_path = store.run_dir / "commit-intent.json"
        intent = read_json(intent_path)
        intent["scope"] = forged_scope
        intent["scope_hash"] = canonical_json_sha256(forged_scope)
        intent["approval_sha256"] = sha256_file(approval_path)
        atomic_write_json(intent_path, intent)

        resumed = self.runtime.commit(store.run_id, approve_commit=True)

        self.assertEqual(resumed["status"], "BLOCKED_PERMISSION")
        self.assertIn("scope", resumed["error"])
        self.assertFalse((store.run_dir / "receipt.json").exists())
        self.assertFalse((self.vault / "wiki/escaped.md").exists())
        manifest = read_json(store.manifest_path)
        self.assertFalse(self.runtime._idempotency_path(manifest["idempotency_key"]).exists())

    def test_recovery_rejects_tampered_backup_path_without_terminal_receipt(self) -> None:
        _, store = self._crash_verified_local_after_canonical_writes()
        rollback_manifest_path = store.run_dir / "rollback/manifest.json"
        rollback_manifest = read_json(rollback_manifest_path)
        rollback_manifest["writes"][0]["backup_relative_path"] = "forged/elsewhere.bak"
        atomic_write_json(rollback_manifest_path, rollback_manifest)

        resumed = self.runtime.commit(store.run_id, approve_commit=True)

        self.assertEqual(resumed["status"], "BLOCKED_DEPENDENCY")
        self.assertIn("all-written checkpoint", resumed["error"])
        self.assertFalse((store.run_dir / "receipt.json").exists())
        manifest = read_json(store.manifest_path)
        self.assertFalse(self.runtime._idempotency_path(manifest["idempotency_key"]).exists())


if __name__ == "__main__":
    unittest.main()
