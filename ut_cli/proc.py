"""Subprocess helpers for upstream CLIs."""

from __future__ import annotations

import shutil
import subprocess
import sys
from collections.abc import Sequence


class ToolMissingError(RuntimeError):
    pass


class ProcError(RuntimeError):
    def __init__(self, cmd: Sequence[str], returncode: int, stderr: str = ""):
        self.cmd = list(cmd)
        self.returncode = returncode
        self.stderr = stderr
        msg = f"command failed ({returncode}): {' '.join(self.cmd)}"
        if stderr:
            msg = f"{msg}\n{stderr}"
        super().__init__(msg)


def require_tool(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise ToolMissingError(
            f"{name!r} not found on PATH. Install via mise (mise install) or your package manager."
        )
    return path


def run(
    cmd: Sequence[str],
    *,
    cwd: str | None = None,
    check: bool = True,
    capture: bool = True,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        list(cmd),
        cwd=cwd,
        text=True,
        capture_output=capture,
        check=False,
    )
    if check and result.returncode != 0:
        err = (result.stderr or result.stdout or "").strip()
        raise ProcError(cmd, result.returncode, err)
    return result


def die(message: str, code: int = 1) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(code)
