import shutil
import tempfile
import unittest
from pathlib import Path

from tools.multi_agent_vault_team import MultiAgentVaultCommander


class TestMultiAgentVaultTeam(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp())
        self.vault = self.temp_dir / "Vault"
        (self.vault / "Clippings").mkdir(parents=True)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_execute_is_read_only_and_does_not_recurse(self) -> None:
        before = sorted(path.relative_to(self.vault).as_posix() for path in self.vault.rglob("*"))
        result = MultiAgentVaultCommander(self.vault).execute_team_mission()
        after = sorted(path.relative_to(self.vault).as_posix() for path in self.vault.rglob("*"))
        self.assertEqual(result["mission_status"], "READ_ONLY")
        self.assertEqual(result["side_effect_count"], 0)
        self.assertEqual(before, after)

    def test_vault_root_is_mandatory(self) -> None:
        with self.assertRaises(TypeError):
            MultiAgentVaultCommander()  # type: ignore[call-arg]


if __name__ == "__main__":
    unittest.main()
