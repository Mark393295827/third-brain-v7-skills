from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .utils import normalized_text_sha256, read_json, sha256_bytes


@dataclass(frozen=True)
class ContractBundle:
    repo_root: Path
    vault_contract: dict[str, Any]
    freshness_policy: dict[str, Any]
    note_schemas: dict[str, dict[str, Any]]

    @property
    def version(self) -> str:
        return str(self.vault_contract["contract_version"])

    @property
    def domains(self) -> tuple[str, ...]:
        return tuple(self.vault_contract["taxonomy"]["concept_domains"])

    @property
    def paths(self) -> dict[str, str]:
        return dict(self.vault_contract["path_contract"])

    @classmethod
    def load(cls, repo_root: Path | None = None) -> "ContractBundle":
        root = (repo_root or Path(__file__).resolve().parents[2]).resolve()
        contract = read_json(root / "contracts" / "vault-contract.json")
        freshness = read_json(root / contract["freshness_policy"])
        note_schemas = {
            name: read_json(root / relative)
            for name, relative in contract["schemas"].items()
        }
        bundle = cls(root, contract, freshness, note_schemas)
        bundle.verify_templates()
        return bundle

    def schema(self, name: str) -> dict[str, Any]:
        try:
            return self.note_schemas[name]
        except KeyError as exc:
            raise ValueError(f"unknown contract schema: {name}") from exc

    def verify_templates(self) -> None:
        for name, spec in self.vault_contract["templates"].items():
            path = self.repo_root / spec["path"]
            if not path.is_file():
                raise ValueError(f"missing {name} template: {path}")
            observed = normalized_text_sha256(path)
            if observed != spec["sha256"]:
                raise ValueError(
                    f"{name} template hash mismatch: expected {spec['sha256']}, observed {observed}"
                )

    def vault_fingerprint(self, vault_root: Path) -> str:
        resolved = vault_root.resolve()
        config = resolved / "system" / "config.md"
        config_hash = normalized_text_sha256(config) if config.is_file() else "missing-config"
        payload = f"{resolved.as_posix()}|{config_hash}|{self.version}".encode("utf-8")
        return sha256_bytes(payload)
