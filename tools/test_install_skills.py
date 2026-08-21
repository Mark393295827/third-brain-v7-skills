import shutil
import tempfile
import unittest
from pathlib import Path

from tools.install_skills import MANIFEST_NAME, sync_skills


class InstallSkillsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp())
        self.source = self.root / "source"
        self.destination = self.root / "destination"
        skill = self.source / "sample"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text("v1\n", encoding="utf-8")

    def tearDown(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)

    def test_sync_is_hash_verified_and_removes_only_managed_stale_files(self) -> None:
        first = sync_skills(self.source, self.destination)
        self.assertTrue(first["verified"])
        unmanaged = self.destination / "operator-owned.txt"
        unmanaged.write_text("keep\n", encoding="utf-8")
        managed = self.source / "sample" / "SKILL.md"
        managed.unlink()
        (self.source / "sample" / "README.md").write_text("replacement\n", encoding="utf-8")
        second = sync_skills(self.source, self.destination)
        self.assertEqual(second["removed_stale_managed_files"], 1)
        self.assertTrue(unmanaged.is_file())
        self.assertFalse((self.destination / "sample" / "SKILL.md").exists())
        self.assertTrue((self.destination / "sample" / "README.md").is_file())
        self.assertTrue((self.destination / MANIFEST_NAME).is_file())
        self.assertEqual(sync_skills(self.source, self.destination, check=True)["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
