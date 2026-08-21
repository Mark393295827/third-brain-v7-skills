from __future__ import annotations

import shutil
import tempfile
import unittest
from datetime import date
from pathlib import Path

from tools.worker_flow.contracts import ContractBundle
from tools.worker_flow.frontmatter import parse_markdown
from tools.worker_flow.governance import validate_concept
from tools.worker_flow.schema import validate_schema
from tools.worker_flow.template_render import TOKEN_RE, render_host_template


class TemplateContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.bundle = ContractBundle.load()
        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _template(self, name: str) -> str:
        relative = self.bundle.vault_contract["templates"][name]["path"]
        return (self.bundle.repo_root / relative).read_text(encoding="utf-8")

    def _concept_values(self) -> dict[str, object]:
        return {
            "title": 'Quoted: "Concept" 中文',
            "chinese_title": "引用概念",
            "url": "https://example.com/source?a=1:b",
            "author": 'A "Researcher"',
            "source_date": "2026-08-20",
            "domain": "ai-engineering",
            "created": "2026-08-20",
            "updated": "2026-08-20",
            "evidence_level": "single-source",
            "freshness_tier": "stable",
            "valid_as_of": "2026-08-20",
            "last_verified": "2026-08-20",
            "next_review": "2027-08-20",
            "source_id": "src-template-test",
            "run_id": "run-template-test",
            "concept_slug": "quoted-concept",
            "source_note": "sources/2026-08/source",
            "thesis_anchor": "a1",
            "evidence_anchor": "a2",
            "mechanism_anchor_1": "a1",
            "mechanism_anchor_2": "a2",
            "mechanism_anchor_3": "a3",
            "metric_anchor_1": "a1",
            "metric_anchor_2": "a2",
            "moc_path": "maps/domain-mocs/AI Engineering",
        }

    def test_scaffold_frontmatter_is_schema_valid_and_only_semantics_remain(self) -> None:
        rendered = render_host_template(
            self._template("concept"),
            self._concept_values(),
            self.bundle.placeholder_registry["templates"]["concept"],
        )
        document = parse_markdown(rendered)
        self.assertEqual(document.frontmatter["title"], 'Quoted: "Concept" 中文')
        self.assertEqual(validate_schema(document.frontmatter, self.bundle.schema("concept")), [])
        unresolved = set(TOKEN_RE.findall(rendered))
        self.assertTrue(unresolved)
        self.assertTrue(all(token.startswith("semantic.") for token in unresolved))
        self.assertFalse(TOKEN_RE.search(document.raw_frontmatter))

    def test_fully_authored_template_candidate_passes_governance(self) -> None:
        vault = self.temp_dir / "Vault"
        source = vault / "sources/2026-08/source.md"
        source.parent.mkdir(parents=True)
        source.write_text("First evidence ^a1\nSecond evidence ^a2\nThird evidence ^a3\n", encoding="utf-8")
        targets = (
            "maps/domain-mocs/AI Engineering.md",
            "wiki/concepts/ai-engineering/Related One.md",
            "wiki/concepts/ai-engineering/Related Two.md",
            "wiki/entities/products/Example.md",
        )
        for relative in targets:
            target = vault / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("---\ntitle: target\n---\n", encoding="utf-8")

        rendered = render_host_template(
            self._template("concept"),
            self._concept_values(),
            self.bundle.placeholder_registry["templates"]["concept"],
        )
        replacements = {token: "authored evidence" for token in set(TOKEN_RE.findall(rendered))}
        replacements.update(
            {
                "semantic.related_concept_1": "wiki/concepts/ai-engineering/Related One",
                "semantic.related_concept_2": "wiki/concepts/ai-engineering/Related Two",
                "semantic.related_entity_1": "wiki/entities/products/Example",
            }
        )
        for token, value in replacements.items():
            rendered = rendered.replace("{{" + token + "}}", value)
        report = validate_concept(
            "wiki/concepts/ai-engineering/quoted-concept.md",
            rendered,
            source_text=source.read_text(encoding="utf-8"),
            source_relative_path="sources/2026-08/source.md",
            source_id="src-template-test",
            domain="ai-engineering",
            contract_version="8.1.0",
            freshness_policy=self.bundle.freshness_policy,
            today=date(2026, 8, 20),
            vault_root=vault,
            schema=self.bundle.schema("concept"),
        )
        self.assertTrue(report.passed, [finding.__dict__ for finding in report.findings])

    def test_output_host_render_has_schema_valid_frontmatter(self) -> None:
        values = {
            "deliverable_title": "Decision: Ship",
            "chinese_title": "交付决策",
            "output_type": "decision-memo",
            "valid_as_of": "2026-08-20",
            "domain": "ai-engineering",
            "created": "2026-08-20",
            "updated": "2026-08-20",
            "freshness_status": "current",
            "source_id": "src-template-test",
            "run_id": "run-output-test",
            "concept_1": "one",
            "concept_2": "two",
            "recipient_1": "operator",
            "source_note": "sources/2026-08/source",
        }
        rendered = render_host_template(
            self._template("output"),
            values,
            self.bundle.placeholder_registry["templates"]["output"],
        )
        document = parse_markdown(rendered)
        self.assertEqual(validate_schema(document.frontmatter, self.bundle.schema("output")), [])
        self.assertTrue(all(token.startswith("semantic.") for token in TOKEN_RE.findall(rendered)))

    def test_secondary_link_anchor_is_validated(self) -> None:
        vault = self.temp_dir / "Anchor Vault"
        primary = vault / "sources/2026-08/primary.md"
        secondary = vault / "sources/2026-08/secondary.md"
        primary.parent.mkdir(parents=True)
        primary.write_text("One ^a1\nTwo ^a2\nThree ^a3\n", encoding="utf-8")
        secondary.write_text("Punctuation。^missing\n", encoding="utf-8")
        rendered = render_host_template(
            self._template("concept"),
            self._concept_values(),
            self.bundle.placeholder_registry["templates"]["concept"],
        )
        for token in set(TOKEN_RE.findall(rendered)):
            rendered = rendered.replace("{{" + token + "}}", "authored")
        rendered += "\nSecondary: [[sources/2026-08/secondary#^missing]]\n"
        report = validate_concept(
            "wiki/concepts/ai-engineering/quoted-concept.md",
            rendered,
            source_text=primary.read_text(encoding="utf-8"),
            source_relative_path="sources/2026-08/source.md",
            source_id="src-template-test",
            domain="ai-engineering",
            contract_version="8.1.0",
            freshness_policy=self.bundle.freshness_policy,
            today=date(2026, 8, 20),
            vault_root=vault,
            schema=self.bundle.schema("concept"),
        )
        self.assertIn("concept.anchor.broken", {finding.code for finding in report.findings})


if __name__ == "__main__":
    unittest.main()
