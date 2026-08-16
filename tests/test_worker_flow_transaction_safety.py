from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from tools.worker_flow.transaction import PreimageConflict, TransactionManager, WriteOperation
from tools.worker_flow.utils import atomic_write_json, read_json, sha256_file


class TransactionSafetyTest(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp())
        self.vault = self.root / "Vault"
        self.vault.mkdir()
        self.rollback = self.root / "rollback"

    def tearDown(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)

    def test_preimage_is_rechecked_immediately_before_write(self) -> None:
        target = self.vault / "maps/index.md"
        target.parent.mkdir(parents=True)
        target.write_text("initial\n", encoding="utf-8")
        expected = sha256_file(target)
        transaction = TransactionManager(self.vault, self.rollback)
        original_preflight = transaction._preflight

        def racing_preflight(operation: WriteOperation):
            prepared = original_preflight(operation)
            target.write_text("concurrent edit\n", encoding="utf-8")
            return prepared

        transaction._preflight = racing_preflight  # type: ignore[method-assign]
        with self.assertRaises(PreimageConflict):
            transaction.apply(
                [WriteOperation("maps/index.md", b"replacement\n", "map", expected)]
            )
        self.assertEqual(target.read_text(encoding="utf-8"), "concurrent edit\n")

    def test_rollback_never_overwrites_a_post_write_concurrent_edit(self) -> None:
        target = self.vault / "wiki/concept.md"
        target.parent.mkdir(parents=True)
        target.write_text("initial\n", encoding="utf-8")
        expected = sha256_file(target)
        transaction = TransactionManager(self.vault, self.rollback)
        applied = transaction.apply(
            [WriteOperation("wiki/concept.md", b"transaction value\n", "concept", expected)]
        )
        target.write_text("human edit after transaction\n", encoding="utf-8")

        conflicts = transaction.rollback(applied)

        self.assertEqual(conflicts, ["wiki/concept.md"])
        self.assertEqual(target.read_text(encoding="utf-8"), "human edit after transaction\n")

    def test_new_target_rollback_ignores_forged_backup(self) -> None:
        transaction = TransactionManager(self.vault, self.rollback)
        applied = transaction.apply(
            [WriteOperation("sources/new.md", b"new source\n", "source")]
        )
        forged_backup = self.rollback / "sources/new.md.bak"
        forged_backup.parent.mkdir(parents=True, exist_ok=True)
        forged_backup.write_text("forged preimage\n", encoding="utf-8")

        conflicts = transaction.rollback(applied)

        self.assertEqual(conflicts, [])
        self.assertFalse((self.vault / "sources/new.md").exists())

    def test_recovery_rejects_tampered_rollback_manifest(self) -> None:
        target = self.vault / "maps/index.md"
        target.parent.mkdir(parents=True)
        target.write_text("initial\n", encoding="utf-8")
        expected = sha256_file(target)
        operation = WriteOperation("maps/index.md", b"replacement\n", "map", expected)
        transaction = TransactionManager(self.vault, self.rollback)
        transaction.apply([operation])
        manifest_path = self.rollback / "manifest.json"
        manifest = read_json(manifest_path)
        manifest["writes"][0]["preimage_sha256"] = "0" * 64
        atomic_write_json(manifest_path, manifest)

        reconciled = transaction.reconcile_applied([operation])

        self.assertIsNone(reconciled)


if __name__ == "__main__":
    unittest.main()
