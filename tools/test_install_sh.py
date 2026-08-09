from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "install.sh"


class InstallScriptTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.fixture_root = Path(self.temp_dir.name) / "repository"
        self.home = Path(self.temp_dir.name) / "home"
        self.fixture_root.mkdir()
        self.home.mkdir()
        (self.home / ".claude").mkdir()

        shutil.copy2(INSTALLER, self.fixture_root / "install.sh")
        skill = self.fixture_root / "skills" / "sample-skill"
        (skill / "scripts" / "__pycache__").mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            "---\n"
            "name: sample-skill\n"
            "description: Use when testing installer behavior.\n"
            "---\n",
            encoding="utf-8",
        )
        (skill / "scripts" / "keep.py").write_text("print('keep')\n", encoding="utf-8")
        (skill / "scripts" / "__pycache__" / "generated.pyc").write_bytes(b"cache")
        (skill / "generated.pyc").write_bytes(b"cache")
        (skill / "generated.pyo").write_bytes(b"optimized")

        cursor = self.fixture_root / "adapters" / "cursor"
        windsurf = self.fixture_root / "adapters" / "windsurf"
        cursor.mkdir(parents=True)
        windsurf.mkdir(parents=True)
        (cursor / "third-brain-skills.mdc").write_text("cursor\n", encoding="utf-8")
        (windsurf / "third-brain-skills.md").write_text("windsurf\n", encoding="utf-8")

    @staticmethod
    def shell_path(path: Path) -> str:
        if os.name != "nt":
            return str(path)
        resolved = path.resolve()
        drive = resolved.drive.rstrip(":").lower()
        if not drive or resolved.anchor.startswith("\\\\"):
            raise unittest.SkipTest(f"Unsupported Windows path for WSL: {resolved}")
        relative = resolved.as_posix().split(":/", 1)[1]
        return f"/mnt/{drive}/{relative}"

    def run_installer(self, target: str) -> subprocess.CompletedProcess[str]:
        bash = shutil.which("bash")
        if not bash:
            self.skipTest("bash is unavailable")
        root = shlex.quote(self.shell_path(self.fixture_root))
        home = shlex.quote(self.shell_path(self.home))
        command = (
            f"cd {root} && unset CLAUDE_CODE && "
            f"HOME={home} bash ./install.sh {shlex.quote(target)}"
        )
        return subprocess.run(
            [bash, "-lc", command],
            text=True,
            capture_output=True,
            check=False,
            errors="replace",
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
        msg = (result.stdout or "") + (result.stderr or "")
        self.assertEqual(result.returncode, 0, msg)
        self.assert_filtered_skill(self.home / ".agents" / "skills")

    def test_auto_install_handles_unset_claude_code(self) -> None:
        result = self.run_installer("auto")
        msg = (result.stdout or "") + (result.stderr or "")
        self.assertEqual(result.returncode, 0, msg)
        self.assert_filtered_skill(self.home / ".claude" / "skills")

    def test_all_preserves_targets_and_filters_python_cache_artifacts(self) -> None:
        result = self.run_installer("all")
        msg = (result.stdout or "") + (result.stderr or "")
        self.assertEqual(result.returncode, 0, msg)
        for target in (
            self.home / ".claude" / "skills",
            self.home / ".agents" / "skills",
            self.home / ".gemini" / "skills",
            self.fixture_root / ".windsurf" / "skills",
        ):
            self.assert_filtered_skill(target)
        self.assertTrue(
            (self.fixture_root / ".cursor" / "rules" / "third-brain-skills.mdc").is_file()
        )
        self.assertTrue(
            (self.fixture_root / ".windsurf" / "rules" / "third-brain-skills.md").is_file()
        )


if __name__ == "__main__":
    unittest.main()
