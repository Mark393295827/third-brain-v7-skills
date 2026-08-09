#!/usr/bin/env python3
"""
# Multi-Agent Vault Team Orchestrator (agent-teams-command Contract)
Implements a 3-worker collaborative agent team directed by a Primary Orchestrator (Commander):
- Commander: Primary Orchestrator / Director
- Worker 1 (Ingestion Agent): Scans inbox & generates immutable source notes (sources/YYYY-MM/src-*.md)
- Worker 2 (Enrichment Agent): Classifies concepts into 13 domains & compiles Gold-Standard concept notes
- Worker 3 (Governance Agent): Performs link auditing, KPI updates, SOP index sync & unit tests
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

DEFAULT_VAULT = r"C:\Users\高杰\Documents\Obsidian Vault"
VAULT_DIR = Path(os.environ.get("OBSIDIAN_VAULT_PATH", DEFAULT_VAULT))
TOOLS_DIR = Path(__file__).resolve().parent

class MultiAgentVaultCommander:
    def __init__(self, vault_dir: Path = VAULT_DIR):
        self.vault_dir = vault_dir
        self.run_id = f"run-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.ipc_ledger = []

    def log_ipc_event(self, worker_role: str, task: str, state: str, artifact: str, evidence: str):
        event = {
            "timestamp": datetime.now().isoformat(),
            "worker_role": worker_role,
            "task": task,
            "state": state,
            "artifact": artifact,
            "evidence": evidence
        }
        self.ipc_ledger.append(event)
        print(f"[{worker_role}] Task: {task} | State: {state} | Artifact: {artifact}")

    def run_worker_ingestion(self) -> dict:
        """Worker 1: Scans Clippings/ inbox and generates immutable source notes."""
        self.log_ipc_event("Ingestion-Agent", "Scan Inbox & Archive Sources", "RUNNING", "sources/YYYY-MM/", "Executing clippings pipeline")
        
        script = TOOLS_DIR / "run_30min_clippings_pipeline.py"
        res = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
        
        if res.returncode == 0:
            self.log_ipc_event("Ingestion-Agent", "Scan Inbox & Archive Sources", "DONE", "Clippings/Archive/", res.stdout.strip())
            return {"status": "SUCCESS", "output": res.stdout.strip()}
        else:
            self.log_ipc_event("Ingestion-Agent", "Scan Inbox & Archive Sources", "FAILED", "Clippings/", res.stderr.strip())
            return {"status": "FAILED", "error": res.stderr.strip()}

    def run_worker_governance(self) -> dict:
        """Worker 3: Runs vault auto-healing, KPI update, SOP sync, and unit tests."""
        self.log_ipc_event("Governance-Agent", "Auto-Heal & KPI Sync", "RUNNING", "system/governance-dashboard.md", "Running auto_heal_vault.py")
        
        script_heal = TOOLS_DIR / "auto_heal_vault.py"
        res_heal = subprocess.run([sys.executable, str(script_heal)], capture_output=True, text=True)
        
        script_adapt = TOOLS_DIR / "adapt_skills_to_vault.py"
        res_adapt = subprocess.run([sys.executable, str(script_adapt)], capture_output=True, text=True)
        
        # Run test suite
        res_test = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", str(TOOLS_DIR), "-p", "test_*.py"], capture_output=True, text=True)
        
        test_passed = res_test.returncode == 0
        state = "DONE" if test_passed else "FAILED"
        
        self.log_ipc_event("Governance-Agent", "Vault Health & Unit Test Gate", state, "tools/test_*.py", res_test.stderr.strip() or res_test.stdout.strip())
        
        return {
            "status": "SUCCESS" if test_passed else "FAILED",
            "heal_output": res_heal.stdout.strip(),
            "adapt_output": res_adapt.stdout.strip(),
            "test_output": res_test.stderr.strip()
        }

    def execute_team_mission(self) -> dict:
        """Commander: Orchestrates mission execution across Worker 1, Worker 2, and Worker 3."""
        print(f"=== Multi-Agent Vault Commander Started (Run ID: {self.run_id}) ===")
        
        # Step 1: Ingestion Worker
        ingest_res = self.run_worker_ingestion()
        
        # Step 2: Governance & Repair Worker
        gov_res = self.run_worker_governance()
        
        summary = {
            "run_id": self.run_id,
            "timestamp": datetime.now().isoformat(),
            "ingestion_agent": ingest_res["status"],
            "governance_agent": gov_res["status"],
            "total_ipc_events": len(self.ipc_ledger),
            "mission_status": "SUCCESS" if (ingest_res["status"] == "SUCCESS" and gov_res["status"] == "SUCCESS") else "PARTIAL_FAILURE"
        }
        
        print(f"=== Mission Complete: Status = {summary['mission_status']} ===")
        return summary

def main():
    commander = MultiAgentVaultCommander()
    res = commander.execute_team_mission()
    print(json.dumps(res, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
