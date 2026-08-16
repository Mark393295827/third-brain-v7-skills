import os
import sys
import shutil
import tempfile
import unittest
from pathlib import Path

# Add tools directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from worker_flow_engine import WorkerFlowEngine

class TestWorkerFlowEngine(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.vault_dir = Path(self.test_dir) / "TestVault"
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        
        # Create minimal vault structure
        for d in ["01_inbox", "Clippings", "sources", "wiki/concepts", "maps/domain-mocs", "wiki/outputs"]:
            (self.vault_dir / d).mkdir(parents=True, exist_ok=True)
            
        self.engine = WorkerFlowEngine(vault_dir=self.vault_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_stage_1_ingest(self):
        sample_file = self.vault_dir / "Clippings" / "Sample Test Clipping.md"
        sample_file.write_text("# Test Article\nKey point 1\nKey point 2", encoding="utf-8")
        
        res = self.engine.stage_1_ingest(sample_file, domain="ai-engineering")
        self.assertEqual(res["status"], "SUCCESS")
        self.assertTrue(res["canonical_path"].exists())
        
        # Check source content
        content = res["canonical_path"].read_text(encoding="utf-8")
        self.assertIn("source_id:", content)
        self.assertIn("^key-insight-1", content)

    def test_stage_2_cognitive_compile(self):
        dummy_source = self.vault_dir / "sources" / "2026-08" / "2026-08-15-dummy.md"
        dummy_source.parent.mkdir(parents=True, exist_ok=True)
        dummy_source.write_text("Dummy Source Content", encoding="utf-8")
        
        res = self.engine.stage_2_cognitive_compile(
            concept_title="测试自主智能体架构",
            domain="ai-engineering",
            source_path=dummy_source,
            thesis="智能体需要分层解耦与独立失败域以保证鲁棒性。"
        )
        self.assertEqual(res["status"], "SUCCESS")
        self.assertTrue(res["concept_path"].exists())
        
        content = res["concept_path"].read_text(encoding="utf-8")
        self.assertIn("mermaid", content)
        self.assertIn("范式对比矩阵", content)
        self.assertIn("核心论点 (Core Thesis)", content)

    def test_stage_4_governance_audit(self):
        res = self.engine.stage_4_governance_audit()
        self.assertEqual(res["status"], "SUCCESS")
        self.assertIn("total_sources", res)
        self.assertIn("total_concepts", res)

    def test_stage_5_deliver_output(self):
        res = self.engine.stage_5_deliver_output(
            title="测试战略交付备忘录",
            category="evaluations",
            summary="这是一份端到端交付评估总结。",
            concepts=["ai-engineering/测试自主智能体架构"]
        )
        self.assertEqual(res["status"], "SUCCESS")
        self.assertTrue(res["output_path"].exists())

    def test_full_pipeline_execution(self):
        sample_file = self.vault_dir / "Clippings" / "Autonomous Web Optimization.md"
        sample_file.write_text("Detailed research about web agents and computer use.", encoding="utf-8")
        
        res = self.engine.execute_full_pipeline(
            raw_file=sample_file,
            concept_title="自主网页优化引擎",
            domain="ai-engineering",
            thesis="自主智能体通过闭环感知与动作编译极大降低长尾自动化成本。"
        )
        self.assertEqual(res["status"], "SUCCESS")
        self.assertIn("source_created", res)
        self.assertIn("concept_created", res)
        self.assertIn("output_created", res)

if __name__ == "__main__":
    unittest.main()
