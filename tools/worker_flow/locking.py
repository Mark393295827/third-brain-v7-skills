from __future__ import annotations

import functools
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Iterator, TypeVar


class IntegrationLeaseBusy(RuntimeError):
    pass


@contextmanager
def integration_lock(path: Path) -> Iterator[None]:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+b") as handle:
        handle.seek(0, os.SEEK_END)
        if handle.tell() == 0:
            handle.write(b"0")
            handle.flush()
            os.fsync(handle.fileno())
        handle.seek(0)
        if os.name == "nt":
            import msvcrt

            try:
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError as exc:
                raise IntegrationLeaseBusy("another Integration Owner holds the commit lease") from exc
            try:
                yield
            finally:
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            try:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as exc:
                raise IntegrationLeaseBusy("another Integration Owner holds the commit lease") from exc
            try:
                yield
            finally:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


F = TypeVar("F", bound=Callable[..., Any])


def integration_owned(method: F) -> F:
    @functools.wraps(method)
    def wrapper(self: Any, run_id: str, approve_commit: bool = False, archive: bool = True) -> Any:
        if not approve_commit:
            return method(self, run_id, approve_commit=approve_commit, archive=archive)
        lock_path = self.vault_root / self.contracts.paths["runs"] / ".integration.lock"
        with integration_lock(lock_path):
            return method(self, run_id, approve_commit=approve_commit, archive=archive)

    return wrapper  # type: ignore[return-value]

