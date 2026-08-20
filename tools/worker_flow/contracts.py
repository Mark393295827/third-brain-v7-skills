from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any

from .utils import normalized_text_sha256, read_json, sha256_bytes


@dataclass(frozen=True)
class ContractBundle:
    repo_root: Path
    vault_contract: dict[str, Any]
    freshness_policy: dict[str, Any]
    note_schemas: dict[str, dict[str, Any]]
    placeholder_registry: dict[str, Any]

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
        placeholder_registry = read_json(root / contract["placeholder_registry"])
        bundle = cls(root, contract, freshness, note_schemas, placeholder_registry)
        bundle.verify_templates()
        return bundle

    def schema(self, name: str) -> dict[str, Any]:
        try:
            return self.note_schemas[name]
        except KeyError as exc:
            raise ValueError(f"unknown contract schema: {name}") from exc

    def verify_templates(self) -> None:
        if self.placeholder_registry.get("contract_version") != self.version:
            raise ValueError("placeholder registry contract version mismatch")
        registry_templates = self.placeholder_registry.get("templates", {})
        if set(registry_templates) != set(self.vault_contract["templates"]):
            raise ValueError("placeholder registry template names do not match vault contract")

        for name, spec in self.vault_contract["templates"].items():
            path = self.repo_root / spec["path"]
            if not path.is_file():
                raise ValueError(f"missing {name} template: {path}")
            observed = normalized_text_sha256(path)
            if observed != spec["sha256"]:
                raise ValueError(
                    f"{name} template hash mismatch: expected {spec['sha256']}, observed {observed}"
                )
            for alias_relative in spec.get("aliases", []):
                alias = self.repo_root / alias_relative
                if not alias.is_file():
                    raise ValueError(f"missing {name} template alias: {alias}")
                alias_hash = normalized_text_sha256(alias)
                if alias_hash != observed:
                    raise ValueError(
                        f"{name} template alias mismatch: {alias_relative} has {alias_hash}, canonical has {observed}"
                    )
            text = path.read_text(encoding="utf-8-sig")
            observed_tokens = set(re.findall(r"\{\{([A-Za-z0-9_.]+)\}\}", text))
            token_spec = registry_templates[name]
            host_tokens = set(token_spec.get("host_tokens", []))
            semantic_tokens = set(token_spec.get("semantic_tokens", []))
            if host_tokens & semantic_tokens:
                raise ValueError(f"{name} placeholder roles overlap")
            if any(not token.startswith("semantic.") for token in semantic_tokens):
                raise ValueError(f"{name} semantic placeholders must use semantic. prefix")
            declared_tokens = host_tokens | semantic_tokens
            if observed_tokens != declared_tokens:
                missing = sorted(declared_tokens - observed_tokens)
                undeclared = sorted(observed_tokens - declared_tokens)
                raise ValueError(
                    f"{name} placeholder registry mismatch: missing={missing}, undeclared={undeclared}"
                )

        bundle = read_json(self.repo_root / "contracts" / "system-bundle.json")
        bundled_sources = {str(entry.get("source")) for entry in bundle.get("entries", [])}
        for name, spec in self.vault_contract["templates"].items():
            required = {str(spec["path"]), *(str(alias) for alias in spec.get("aliases", []))}
            missing = sorted(required - bundled_sources)
            if missing:
                raise ValueError(f"{name} template files are absent from system bundle: {missing}")
        required_contract_assets = {
            "contracts/vault-contract.json",
            "contracts/system-bundle.json",
            str(self.vault_contract["freshness_policy"]),
            str(self.vault_contract["placeholder_registry"]),
            *(str(path) for path in self.vault_contract["schemas"].values()),
        }
        missing_contract_assets = sorted(required_contract_assets - bundled_sources)
        if missing_contract_assets:
            raise ValueError(
                f"contract assets are absent from system bundle: {missing_contract_assets}"
            )

    def vault_fingerprint(self, vault_root: Path) -> str:
        resolved = vault_root.resolve()
        config = resolved / "system" / "config.md"
        config_hash = normalized_text_sha256(config) if config.is_file() else "missing-config"
        payload = f"{resolved.as_posix()}|{config_hash}|{self.version}".encode("utf-8")
        return sha256_bytes(payload)
