"""Build and verify a shareable, credential-free Third Brain Agentic OS bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile
import zipfile


VERSION = "8.1.0"
MANIFEST_NAME = "agentic-os-manifest.json"

# This is intentionally an allowlist.  A package must not accidentally carry
# a user's Vault, credentials, plugins, host schedulers, or transient state.
PACKAGE_PATHS = (
    "tools/index.html",
    "tools/agentic_os_server.py",
    "tools/agentic_os_runtime.py",
    "tools/agentic_os.py",
    "tools/package_agentic_os.py",
    "tools/sync_vault_codex.py",
    "tools/install_skills.py",
    "tools/lint-agent-skills.py",
    "tools/worker_flow_engine.py",
    "dashboard.html",
    "assets/third-brain-v8.1-actual-system-architecture.png",
    "assets/third-brain-v8.1-actual-system-architecture.svg",
    "AGENTS.md",
    "README.md",
    "GUIDE.md",
    "install.ps1",
    "install.sh",
    "LICENSE",
)

PACKAGE_ROOTS = (
    "skills",
    "contracts",
    "system",
    "docs",
    "workflows",
    "examples",
    "commands",
    "adapters",
    "assets",
    "core",
    "hooks",
    "tools/worker_flow",
)

EXCLUDED_PARTS = {"__pycache__", ".git", ".pytest_cache"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def collect_files(root: Path) -> list[Path]:
    files: set[Path] = set()
    for relative in PACKAGE_PATHS:
        path = root / relative
        if path.is_file():
            files.add(path)
    for relative in PACKAGE_ROOTS:
        directory = root / relative
        if not directory.is_dir():
            continue
        for path in directory.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(root)
            if EXCLUDED_PARTS.intersection(rel.parts) or path.suffix.casefold() in EXCLUDED_SUFFIXES:
                continue
            files.add(path)
    return sorted(files, key=lambda p: p.relative_to(root).as_posix())


def build_manifest(root: Path, files: list[Path] | None = None) -> dict:
    files = files if files is not None else collect_files(root)
    entries = []
    missing = []
    for relative in PACKAGE_PATHS:
        path = root / relative
        if not path.is_file():
            missing.append(relative)
    for path in files:
        data = path.read_bytes()
        entries.append({"path": path.relative_to(root).as_posix(), "sha256": sha256_bytes(data), "size": len(data)})
    return {
        "schema_version": "1.0",
        "product": "third-brain-agentic-os",
        "version": VERSION,
        "host_primary": "Codex",
        "compatibility_adapters": ["Claude Code", "Gemini", "Cursor", "Windsurf"],
        "generated_by": "tools/package_agentic_os.py",
        "files": entries,
        "missing_required": missing,
        "excluded": ["credentials", "plugins", "host schedulers", "Vault contents", "sources", "wiki", "state/receipts"],
    }


def package(root: Path, output: Path) -> dict:
    files = collect_files(root)
    required = set(PACKAGE_PATHS)
    present = {p.relative_to(root).as_posix() for p in files}
    missing_required = sorted(required - present)
    if missing_required:
        raise RuntimeError("bundle is incomplete; missing: " + ", ".join(missing_required))
    manifest = build_manifest(root, files)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.relative_to(root).as_posix())
        archive.writestr(MANIFEST_NAME, json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    return {"output": str(output), "manifest": manifest, "sha256": sha256_bytes(output.read_bytes())}


def verify_package(bundle: Path) -> dict:
    if not bundle.is_file():
        return {"ok": False, "error": f"bundle not found: {bundle}"}
    try:
        with zipfile.ZipFile(bundle) as archive:
            manifest = json.loads(archive.read(MANIFEST_NAME).decode("utf-8"))
            checked = []
            for entry in manifest.get("files", []):
                data = archive.read(entry["path"])
                actual = sha256_bytes(data)
                if actual != entry["sha256"] or len(data) != entry["size"]:
                    return {"ok": False, "error": f"hash mismatch: {entry['path']}", "manifest": manifest}
                checked.append(entry["path"])
            names = set(archive.namelist())
            forbidden = [name for name in names if any(token in name.lower() for token in (".env", "credential", "plugin", "scheduler"))]
            if forbidden:
                return {"ok": False, "error": "forbidden package entries", "entries": forbidden}
            return {"ok": True, "checked": checked, "manifest": manifest, "sha256": sha256_bytes(bundle.read_bytes())}
    except (OSError, KeyError, ValueError, zipfile.BadZipFile) as exc:
        return {"ok": False, "error": str(exc)}


def readiness_probe(root: Path) -> dict:
    required = [
        "tools/index.html",
        "tools/agentic_os_server.py",
        "tools/agentic_os_runtime.py",
        "tools/sync_vault_codex.py",
        "contracts/agentic-os/action-registry.json",
        "contracts/agentic-os/action-receipt.schema.json",
        "system/codex.md",
        "system/templates/vault-agent-navigation-v8.1.md",
    ]
    missing = [path for path in required if not (root / path).is_file()]
    probe = {"ready": not missing, "python": os.sys.version.split()[0], "missing": missing, "checks": []}
    if not missing:
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("agentic_os_runtime_probe", root / "tools/agentic_os_runtime.py")
            if spec is None or spec.loader is None:
                raise RuntimeError("runtime spec unavailable")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            probe["checks"].append({"name": "t02-runtime-import", "ok": True})
        except Exception as exc:
            probe["ready"] = False
            probe["checks"].append({"name": "t02-runtime-import", "ok": False, "error": str(exc)})
    return probe


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Package or verify the credential-free Agentic OS bundle.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--output", default=None)
    parser.add_argument("--verify", default=None)
    parser.add_argument("--probe", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.root).resolve()
    if args.probe:
        result = readiness_probe(root)
    elif args.verify:
        result = verify_package(Path(args.verify).resolve())
    else:
        output = Path(args.output).resolve() if args.output else root / "dist" / "third-brain-agentic-os-v8.1.zip"
        result = package(root, output)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    if args.probe or args.verify:
        return 0 if result.get("ready", result.get("ok", False)) else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
