from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from .utils import atomic_write_bytes, atomic_write_json, read_json, resolve_within, sha256_bytes, sha256_file


@dataclass(frozen=True)
class WriteOperation:
    relative_path: str
    content: bytes
    kind: str
    expected_preimage_sha256: str | None = None
    preserve_on_rollback: bool = False


@dataclass(frozen=True)
class AppliedWrite:
    relative_path: str
    kind: str
    preimage_sha256: str | None
    postimage_sha256: str
    changed: bool
    preserve_on_rollback: bool


class PreimageConflict(RuntimeError):
    pass


class TransactionManager:
    def __init__(self, vault_root: Path, rollback_dir: Path):
        self.vault_root = vault_root.resolve()
        self.rollback_dir = rollback_dir.resolve()
        self.rollback_dir.mkdir(parents=True, exist_ok=True)

    def _preflight(self, operation: WriteOperation) -> tuple[Path, str | None]:
        target = resolve_within(self.vault_root, operation.relative_path)
        observed = sha256_file(target) if target.is_file() else None
        if operation.expected_preimage_sha256 is not None and observed != operation.expected_preimage_sha256:
            raise PreimageConflict(
                f"preimage conflict for {operation.relative_path}: expected "
                f"{operation.expected_preimage_sha256}, observed {observed}"
            )
        if operation.expected_preimage_sha256 is None and target.exists():
            raise PreimageConflict(f"unexpected existing target: {operation.relative_path}")
        return target, observed

    def apply(self, operations: Iterable[WriteOperation]) -> list[AppliedWrite]:
        prepared: list[tuple[WriteOperation, Path, str | None]] = []
        for operation in operations:
            target, observed = self._preflight(operation)
            prepared.append((operation, target, observed))

        rollback_manifest = []
        for operation, target, observed in prepared:
            backup_relative = None
            if target.is_file():
                backup_relative = operation.relative_path + ".bak"
                backup_path = resolve_within(self.rollback_dir, backup_relative)
                atomic_write_bytes(backup_path, target.read_bytes())
            rollback_manifest.append(
                {
                    "relative_path": operation.relative_path,
                    "backup_relative_path": backup_relative,
                    "preimage_sha256": observed,
                    "preserve_on_rollback": operation.preserve_on_rollback,
                }
            )
        atomic_write_json(self.rollback_dir / "manifest.json", {"writes": rollback_manifest})

        applied: list[AppliedWrite] = []
        try:
            for operation, target, observed in prepared:
                current = sha256_file(target) if target.is_file() else None
                if current != observed:
                    raise PreimageConflict(
                        f"preimage changed immediately before write for {operation.relative_path}: "
                        f"prepared {observed}, observed {current}"
                    )
                postimage = sha256_bytes(operation.content)
                changed = observed != postimage
                if changed:
                    atomic_write_bytes(target, operation.content)
                applied.append(
                    AppliedWrite(
                        operation.relative_path,
                        operation.kind,
                        observed,
                        postimage,
                        changed,
                        operation.preserve_on_rollback,
                    )
                )
        except Exception:
            self.rollback(applied)
            raise
        return applied

    def rollback(self, applied: Iterable[AppliedWrite]) -> list[str]:
        conflicts: list[str] = []
        for item in reversed(list(applied)):
            if item.preserve_on_rollback or not item.changed:
                continue
            target = resolve_within(self.vault_root, item.relative_path)
            current = sha256_file(target) if target.is_file() else None
            if current != item.postimage_sha256:
                conflicts.append(item.relative_path)
                continue
            backup = resolve_within(self.rollback_dir, item.relative_path + ".bak")
            if item.preimage_sha256 is None:
                if target.is_file():
                    target.unlink()
            elif backup.is_file() and sha256_file(backup) == item.preimage_sha256:
                atomic_write_bytes(target, backup.read_bytes())
            else:
                conflicts.append(item.relative_path)
        return conflicts

    def reconcile_applied(self, operations: Iterable[WriteOperation]) -> list[AppliedWrite] | None:
        """Recover an all-written transaction after a crash using its durable rollback manifest."""

        manifest_path = self.rollback_dir / "manifest.json"
        if not manifest_path.is_file():
            return None
        manifest = read_json(manifest_path)
        raw_writes = manifest.get("writes") if isinstance(manifest.get("writes"), list) else []
        operation_list = list(operations)
        if len(raw_writes) != len(operation_list) or any(not isinstance(item, dict) for item in raw_writes):
            return None
        preimages: dict[str, str | None] = {}
        rollback_flags: dict[str, bool] = {}
        backup_paths: dict[str, str | None] = {}
        for item in raw_writes:
            relative = str(item.get("relative_path") or "")
            if not relative or relative in preimages:
                return None
            preimages[relative] = item.get("preimage_sha256")
            rollback_flags[relative] = bool(item.get("preserve_on_rollback"))
            backup_paths[relative] = item.get("backup_relative_path")
        if set(preimages) != {operation.relative_path for operation in operation_list}:
            return None
        reconciled: list[AppliedWrite] = []
        for operation in operation_list:
            if preimages[operation.relative_path] != operation.expected_preimage_sha256:
                return None
            if rollback_flags[operation.relative_path] != operation.preserve_on_rollback:
                return None
            expected_backup = (
                operation.relative_path + ".bak"
                if operation.expected_preimage_sha256 is not None
                else None
            )
            if backup_paths[operation.relative_path] != expected_backup:
                return None
            if expected_backup is not None:
                backup = resolve_within(self.rollback_dir, expected_backup)
                if not backup.is_file() or sha256_file(backup) != operation.expected_preimage_sha256:
                    return None
            target = resolve_within(self.vault_root, operation.relative_path)
            postimage = sha256_bytes(operation.content)
            observed = sha256_file(target) if target.is_file() else None
            if observed != postimage:
                return None
            preimage = preimages[operation.relative_path]
            reconciled.append(
                AppliedWrite(
                    operation.relative_path,
                    operation.kind,
                    preimage,
                    postimage,
                    preimage != postimage,
                    operation.preserve_on_rollback,
                )
            )
        return reconciled

    @staticmethod
    def receipts(applied: Iterable[AppliedWrite]) -> list[dict[str, object]]:
        return [asdict(item) for item in applied]
