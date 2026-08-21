import shutil
import tempfile
import unittest
from pathlib import Path

from tools.legacy_compat import LegacyMutationDisabled
from tools.run_30min_clippings_pipeline import process_file, scan_inbox
from tools.worker_flow.utils import sha256_file


class TestClippingsPipelineCompatibility(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp())
        self.vault = self.temp_dir / "Vault"
        (self.vault / "Clippings").mkdir(parents=True)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_scan_is_read_only(self) -> None:
        clipping = self.vault / "Clippings" / "sample.md"
        clipping.write_text("evidence\n", encoding="utf-8")
        before = sha256_file(clipping)
        result = scan_inbox(self.vault)
        self.assertEqual(result["status"], "DEPRECATED_READ_ONLY")
        self.assertEqual(len(result["facts"]["scan"]["eligible"]), 1)
        self.assertEqual(sha256_file(clipping), before)
        self.assertFalse((self.vault / "Clippings" / "Archive").exists())

    def test_mutation_api_fails_closed(self) -> None:
        with self.assertRaises(LegacyMutationDisabled):
            process_file(self.vault / "Clippings" / "sample.md")


if __name__ == "__main__":
    unittest.main()
