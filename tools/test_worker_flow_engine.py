import shutil
import tempfile
import unittest
from pathlib import Path

from tools.legacy_compat import LegacyMutationDisabled
from tools.worker_flow_engine import WorkerFlowEngine


class TestWorkerFlowEngineCompatibility(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp())
        self.vault = self.temp_dir / "Vault"
        (self.vault / "Clippings").mkdir(parents=True)
        self.engine = WorkerFlowEngine(self.vault)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_governance_surface_is_read_only(self) -> None:
        before = sorted(path.relative_to(self.vault).as_posix() for path in self.vault.rglob("*"))
        result = self.engine.stage_4_governance_audit()
        after = sorted(path.relative_to(self.vault).as_posix() for path in self.vault.rglob("*"))
        self.assertEqual(result["status"], "DEPRECATED_READ_ONLY")
        self.assertEqual(result["side_effect_count"], 0)
        self.assertEqual(before, after)

    def test_all_mutation_surfaces_fail_closed(self) -> None:
        for operation in (
            self.engine.stage_1_ingest,
            self.engine.stage_2_cognitive_compile,
            self.engine.stage_3_graph_weave,
            self.engine.stage_5_deliver_output,
            self.engine.execute_full_pipeline,
        ):
            with self.subTest(operation=operation.__name__):
                with self.assertRaises(LegacyMutationDisabled):
                    operation()


if __name__ == "__main__":
    unittest.main()
