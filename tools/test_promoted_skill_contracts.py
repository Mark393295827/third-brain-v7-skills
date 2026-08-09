from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AFFECTED_SKILLS = (
    "agentic-engineering",
    "harness-engineering",
    "agent-teams-command",
    "context-manager",
    "loop-engineering",
    "verify-before-claim",
    "knowledge-ops",
    "wiki-ingest",
    "startup-evaluation",
)


def skill_text(name):
    return (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")


def normalized(text):
    return " ".join(text.split())


class PromotedSkillContractTests(unittest.TestCase):
    def test_affected_skills_have_iteration_version_and_date(self):
        for name in AFFECTED_SKILLS:
            text = skill_text(name)
            self.assertRegex(text, r'version:\s*"7\.2\.1"', name)
            self.assertRegex(text, r'updated:\s*"2026-08-09"', name)

    def test_runtime_control_chain_is_explicit(self):
        harness = normalized(skill_text("harness-engineering"))
        for term in (
            "Intent Plan",
            "Compiled Contract",
            "tool_execution_owner",
            "termination_reason",
            "NO_OP",
            "runtime-envelope-example.json",
            "validate_runtime_envelope.py",
        ):
            self.assertIn(term, harness)

    def test_team_and_context_contracts_prevent_transcript_fan_in(self):
        teams = normalized(skill_text("agent-teams-command"))
        context = normalized(skill_text("context-manager"))
        self.assertIn("context_manifest", teams)
        self.assertIn("do not merge private branch transcripts", teams)
        self.assertIn("private context manifest", context)
        self.assertIn("not the builder's desired conclusion", context)

    def test_loop_and_verification_treat_no_op_as_a_checked_result(self):
        loop = normalized(skill_text("loop-engineering"))
        verify = normalized(skill_text("verify-before-claim"))
        self.assertIn("eligibility query", loop)
        self.assertIn("side-effect check", loop)
        self.assertIn("output-count check", verify)

    def test_ingest_contracts_require_concurrent_identity_reconciliation(self):
        ingest = normalized(skill_text("wiki-ingest"))
        knowledge = normalized(skill_text("knowledge-ops"))
        for text in (ingest, knowledge):
            self.assertIn("source identity", text.lower())
            self.assertIn("idempotency key", text.lower())
            self.assertIn("reconciliation", text.lower())

    def test_startup_evaluation_separates_ai_value_capture_layers(self):
        startup = normalized(skill_text("startup-evaluation"))
        for term in ("usage", "productivity", "customer ROI", "vendor profit"):
            self.assertIn(term, startup)
        self.assertIn("institutional", startup.lower())

    def test_promotion_audit_records_deferred_claims(self):
        audit = (
            ROOT / "docs" / "wiki-promotion-audit-2026-08-09.md"
        ).read_text(encoding="utf-8")
        self.assertIn("## Promoted", audit)
        self.assertIn("## Deferred", audit)
        normalized_audit = normalized(audit)
        self.assertRegex(
            normalized_audit,
            re.compile(r"Wisedocs.*single-source", re.IGNORECASE),
        )
        self.assertRegex(
            normalized_audit,
            re.compile(r"Otis.*single-source", re.IGNORECASE),
        )

    def test_ci_runs_the_strict_runtime_envelope(self):
        workflow = (
            ROOT / ".github" / "workflows" / "quality.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("validate_runtime_envelope.py", workflow)
        self.assertIn("runtime-envelope-example.json", workflow)
        self.assertIn("--strict", workflow)


if __name__ == "__main__":
    unittest.main()
