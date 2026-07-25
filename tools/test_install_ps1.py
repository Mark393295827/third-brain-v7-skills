from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Optional


ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "install.ps1"


class PowerShellInstallScriptTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.fixture_root = Path(self.temp_dir.name) / "repository"
        self.home = Path(self.temp_dir.name) / "home"
        self.fixture_root.mkdir()
        self.home.mkdir()
        (self.home / ".claude").mkdir()

        shutil.copy2(INSTALLER, self.fixture_root / "install.ps1")
        skill = self.fixture_root / "skills" / "sample-skill"
        (skill / "scripts" / "__pycache__").mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            "---\n"
            "name: sample-skill\n"
            "description: Use when testing installer behavior.\n"
            "---\n",
            encoding="utf-8",
        )
        (skill / "scripts" / "keep.py").write_text(
            "print('keep')\n", encoding="utf-8"
        )
        (skill / "scripts" / "__pycache__" / "generated.pyc").write_bytes(b"cache")
        (skill / "generated.pyc").write_bytes(b"cache")
        (skill / "generated.pyo").write_bytes(b"optimized")

        cursor = self.fixture_root / "adapters" / "cursor"
        windsurf = self.fixture_root / "adapters" / "windsurf"
        cursor.mkdir(parents=True)
        windsurf.mkdir(parents=True)
        (cursor / "third-brain-skills.mdc").write_text("cursor\n", encoding="utf-8")
        (windsurf / "third-brain-skills.md").write_text(
            "windsurf\n", encoding="utf-8"
        )

    def run_installer(
        self, target: str, executable: Optional[str] = None
    ) -> subprocess.CompletedProcess[str]:
        powershell = executable or shutil.which("pwsh") or shutil.which("powershell")
        if not powershell:
            self.skipTest("PowerShell is unavailable")
        environment = os.environ.copy()
        environment["THIRD_BRAIN_HOME"] = str(self.home)
        environment.pop("CLAUDE_CODE", None)
        return subprocess.run(
            [
                powershell,
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(self.fixture_root / "install.ps1"),
                target,
            ],
            cwd=self.fixture_root,
            env=environment,
            text=True,
            capture_output=True,
            check=False,
        )

    def assert_filtered_skill(self, target: Path) -> None:
        skill = target / "sample-skill"
        self.assertTrue((skill / "SKILL.md").is_file())
        self.assertTrue((skill / "scripts" / "keep.py").is_file())
        self.assertFalse(any(skill.rglob("__pycache__")))
        self.assertEqual(list(skill.rglob("*.pyc")), [])
        self.assertEqual(list(skill.rglob("*.pyo")), [])

    def test_codex_install_filters_python_cache_artifacts(self) -> None:
        result = self.run_installer("codex")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assert_filtered_skill(self.home / ".agents" / "skills")

    def test_windows_powershell_51_installs_codex_target(self) -> None:
        if os.name != "nt":
            self.skipTest("Windows PowerShell 5.1 is Windows-only")
        powershell = shutil.which("powershell")
        if not powershell:
            self.skipTest("Windows PowerShell is unavailable")

        result = self.run_installer("codex", executable=powershell)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assert_filtered_skill(self.home / ".agents" / "skills")

    def test_auto_install_handles_unset_claude_code(self) -> None:
        result = self.run_installer("auto")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assert_filtered_skill(self.home / ".claude" / "skills")

    def test_all_preserves_targets_and_filters_python_cache_artifacts(self) -> None:
        result = self.run_installer("all")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for target in (
            self.home / ".claude" / "skills",
            self.home / ".agents" / "skills",
            self.home / ".gemini" / "skills",
            self.fixture_root / ".windsurf" / "skills",
        ):
            self.assert_filtered_skill(target)
        self.assertTrue(
            (
                self.fixture_root
                / ".cursor"
                / "rules"
                / "third-brain-skills.mdc"
            ).is_file()
        )
        self.assertTrue(
            (
                self.fixture_root
                / ".windsurf"
                / "rules"
                / "third-brain-skills.md"
            ).is_file()
        )


if __name__ == "__main__":
    unittest.main()
