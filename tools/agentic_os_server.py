"""Small, localhost-only host for the Agentic OS command centre.

The browser is deliberately a presentation client.  Registry lookup, argv
resolution, execution and receipt creation stay in the T02 runtime.  This
module never accepts a command, path, shell fragment, or verifier from a
browser request.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import importlib
import inspect
import json
import mimetypes
import os
from pathlib import Path
import sys
import threading
import traceback
import uuid
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlsplit


SCHEMA_VERSION = "1.0"
RECEIPT_STATES = {"QUEUED", "RUNNING", "SUCCEEDED", "FAILED", "BLOCKED"}


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def _call_compatible(fn, **values):
    """Call a T02 function without guessing positional arguments."""
    try:
        params = inspect.signature(fn).parameters
    except (TypeError, ValueError):
        return fn()
    kwargs = {name: value for name, value in values.items() if name in params}
    return fn(**kwargs)


class RuntimeUnavailable(RuntimeError):
    pass


class T02Runtime:
    """Narrow adapter around the frozen T02 Python runtime interface."""

    def __init__(self, repo_root: Path, state_root: Path, vault_root: Path | None = None):
        self.repo_root = repo_root.resolve()
        self.state_root = state_root.resolve()
        self.vault_root = vault_root.resolve() if vault_root else None
        if str(self.repo_root) not in sys.path:
            sys.path.insert(0, str(self.repo_root))
        try:
            self.module = importlib.import_module("tools.agentic_os_runtime")
        except Exception as exc:  # pragma: no cover - exercised by host smoke tests
            raise RuntimeUnavailable(f"T02 runtime unavailable: {exc}") from exc

    def _function(self, names):
        for name in names:
            candidate = getattr(self.module, name, None)
            if callable(candidate):
                return candidate
        return None

    def snapshot(self):
        fn = self._function(("generate_snapshot", "build_snapshot", "get_snapshot", "snapshot"))
        if fn is None:
            raise RuntimeUnavailable("T02 runtime exposes no snapshot function")
        result = _call_compatible(fn, repo_root=str(self.repo_root), vault_root=str(self.vault_root) if self.vault_root else None, state_root=str(self.state_root))
        if not isinstance(result, dict):
            raise RuntimeUnavailable("T02 snapshot function did not return an object")
        return result

    def dispatch(self, action_id: str, approval: bool = False):
        fn = self._function(("dispatch_action", "execute_action", "run_action"))
        if fn is None:
            # Some T02 implementations expose the dispatcher through agentic_os.py.
            try:
                cli = importlib.import_module("tools.agentic_os")
            except Exception as exc:
                raise RuntimeUnavailable(f"T02 action runtime unavailable: {exc}") from exc
            fn = next((getattr(cli, name, None) for name in ("dispatch_action", "execute_action", "run_action") if callable(getattr(cli, name, None))), None)
        if fn is None:
            raise RuntimeUnavailable("T02 runtime exposes no action dispatcher")
        return _call_compatible(
            fn,
            action_id=action_id,
            approval=approval,
            approved=approval,
            repo_root=str(self.repo_root),
            vault_root=str(self.vault_root) if self.vault_root else None,
            state_root=str(self.state_root),
        )


def _error_snapshot(message: str) -> dict:
    """Error is intentionally sparse: no fake zero counts are emitted."""
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "status": "ERROR",
        "repository": {"contract_version": "8.1.0", "verification": {"error": message}},
        "vault": {"configured": False, "counts": None, "version_counts": None, "debt": None, "freshness": None, "latest_run": None},
        "actions": [],
        "evidence": [{"kind": "host", "status": "ERROR", "detail": message}],
        "side_effect_count": 0,
    }


def _normalise_receipt(action_id: str, result: object, *, execution_id: str) -> dict:
    if isinstance(result, dict):
        receipt = dict(result)
    else:
        receipt = {"state": "FAILED", "stderr_tail": str(result)}
    receipt.setdefault("schema_version", SCHEMA_VERSION)
    receipt.setdefault("action_id", action_id)
    receipt.setdefault("execution_id", execution_id)
    receipt.setdefault("state", "FAILED")
    if receipt["state"] not in RECEIPT_STATES:
        receipt["state"] = "FAILED"
    receipt.setdefault("started_at", utc_now())
    receipt.setdefault("completed_at", None if receipt["state"] in {"QUEUED", "RUNNING"} else utc_now())
    receipt.setdefault("resolved_argv", [])
    receipt.setdefault("exit_code", None)
    receipt.setdefault("stdout_tail", "")
    receipt.setdefault("stderr_tail", "")
    receipt.setdefault("verifier", {"argv": [], "exit_code": None, "result": "NOT_RUN"})
    receipt.setdefault("evidence", [])
    receipt.setdefault("side_effect_count", 0)
    # A terminal action is successful only with verifier evidence.
    if receipt["state"] == "SUCCEEDED" and receipt.get("verifier", {}).get("result") != "PASS":
        receipt["state"] = "FAILED"
        receipt["stderr_tail"] = (receipt.get("stderr_tail", "") + " verifier did not PASS").strip()
    return receipt


class CommandCentreHandler(BaseHTTPRequestHandler):
    server_version = "AgenticOSHost/1.0"

    @property
    def app(self):
        return self.server.app  # type: ignore[attr-defined]

    def log_message(self, fmt, *args):  # keep host output operator-readable
        sys.stderr.write("[agentic-os-host] " + (fmt % args) + "\n")

    def _send(self, status: int, payload: object, content_type: str = "application/json; charset=utf-8"):
        data = _json_bytes(payload) if content_type.startswith("application/json") else payload
        try:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)
        except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError):
            # Browsers may cancel an older snapshot request after navigation or
            # refresh.  A disconnected client is not a host/runtime failure.
            return None

    def _body(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length > 64 * 1024:
            raise ValueError("request body too large")
        raw = self.rfile.read(length) if length else b"{}"
        value = json.loads(raw.decode("utf-8"))
        if not isinstance(value, dict):
            raise ValueError("request body must be an object")
        return value

    def do_GET(self):  # noqa: N802
        path = unquote(urlsplit(self.path).path)
        if path == "/api/health":
            return self._send(200, {"status": "READY", "schema_version": SCHEMA_VERSION})
        if path == "/api/snapshot":
            try:
                return self._send(200, self.app.runtime.snapshot())
            except Exception as exc:
                return self._send(503, _error_snapshot(str(exc)))
        if path.startswith("/api/receipts/"):
            execution_id = path.rsplit("/", 1)[-1]
            if not execution_id or any(ch not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for ch in execution_id):
                return self._send(400, {"error": "invalid execution id"})
            receipt_path = self.app.state_root / "receipts" / f"{execution_id}.json"
            if not receipt_path.is_file():
                return self._send(404, {"error": "receipt not found"})
            try:
                return self._send(200, json.loads(receipt_path.read_text(encoding="utf-8")))
            except (OSError, json.JSONDecodeError) as exc:
                return self._send(500, {"error": str(exc)})
        return self._serve_static(path)

    def _serve_static(self, path: str):
        relative = path.lstrip("/") or "index.html"
        candidate = (self.app.static_root / relative).resolve()
        try:
            candidate.relative_to(self.app.static_root.resolve())
        except ValueError:
            return self._send(403, {"error": "path outside static root"})
        if not candidate.is_file():
            return self._send(404, {"error": "not found"})
        data = candidate.read_bytes()
        mime = mimetypes.guess_type(candidate.name)[0] or "application/octet-stream"
        return self._send(200, data, mime + "; charset=utf-8" if mime.startswith("text/") else mime)

    def do_POST(self):  # noqa: N802
        path = unquote(urlsplit(self.path).path)
        if not path.startswith("/api/actions/"):
            return self._send(404, {"error": "not found"})
        action_id = path.rsplit("/", 1)[-1]
        if not action_id or any(ch not in "abcdefghijklmnopqrstuvwxyz0123456789-_" for ch in action_id):
            return self._send(400, {"error": "invalid action id"})
        try:
            body = self._body()
            unknown = set(body) - {"approval"}
            if unknown:
                raise ValueError("only approval may be supplied; argv is registry-owned")
            approval = body.get("approval", False) is True
            execution_id = uuid.uuid4().hex
            result = self.app.runtime.dispatch(action_id, approval=approval)
            receipt = _normalise_receipt(action_id, result, execution_id=execution_id)
            receipt_path = self.app.state_root / "receipts" / f"{receipt['execution_id']}.json"
            receipt_path.parent.mkdir(parents=True, exist_ok=True)
            temporary = receipt_path.with_name(f".{receipt_path.name}.{uuid.uuid4().hex}.tmp")
            temporary.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            os.replace(temporary, receipt_path)
            return self._send(200, receipt)
        except (ValueError, RuntimeUnavailable) as exc:
            return self._send(400 if isinstance(exc, ValueError) else 503, {"error": str(exc)})
        except Exception as exc:  # never leak a traceback to the browser
            client_error = exc.__class__.__name__ in {"UnknownActionError", "ActionBlockedError"}
            return self._send(400 if client_error else 500, {"error": str(exc)})


class AgenticOSHost:
    def __init__(self, repo_root: Path, state_root: Path, vault_root: Path | None = None, static_root: Path | None = None):
        self.repo_root = repo_root.resolve()
        self.state_root = state_root.resolve()
        self.state_root.mkdir(parents=True, exist_ok=True)
        self.static_root = (static_root or self.repo_root / "tools").resolve()
        self.runtime = T02Runtime(self.repo_root, self.state_root, vault_root)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Serve the V8.1 Agentic OS command centre on localhost.")
    parser.add_argument("--state-root", required=True, help="Explicit operator state/receipt directory.")
    parser.add_argument("--repo-root", default=None, help="Repository root (defaults to this checkout).")
    parser.add_argument("--vault-root", default=None, help="Optional explicitly configured Vault root for read-only metrics.")
    parser.add_argument("--host", default="127.0.0.1", help="Bind address; localhost is the safe default.")
    parser.add_argument("--port", type=int, default=8765)
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if args.host not in {"127.0.0.1", "localhost", "::1"}:
        raise SystemExit("Refusing non-localhost bind; use an explicit host-owned reverse proxy instead.")
    repo_root = Path(args.repo_root).resolve() if args.repo_root else Path(__file__).resolve().parents[1]
    state_root = Path(args.state_root).resolve()
    try:
        app = AgenticOSHost(repo_root, state_root, Path(args.vault_root).resolve() if args.vault_root else None)
    except Exception as exc:
        raise SystemExit(f"Agentic OS host is not ready: {exc}") from exc
    server = ThreadingHTTPServer((args.host, args.port), CommandCentreHandler)
    server.app = app  # type: ignore[attr-defined]
    print(f"Agentic OS command centre: http://{args.host}:{args.port}/")
    print(f"State root: {state_root}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
