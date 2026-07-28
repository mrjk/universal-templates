"""Unified diff helpers (stdlib difflib)."""

from __future__ import annotations

import difflib
import os
import shutil
import subprocess
import sys
from pathlib import Path


def unified_text_diff(
    old: str,
    new: str,
    *,
    fromfile: str = "a",
    tofile: str = "b",
) -> str:
    old_lines = old.splitlines(keepends=True)
    new_lines = new.splitlines(keepends=True)
    if old and not old.endswith("\n"):
        old_lines = old.splitlines(keepends=True)
        if old_lines and not old_lines[-1].endswith("\n"):
            old_lines[-1] = old_lines[-1] + "\n"
    if new and not new.endswith("\n"):
        new_lines = new.splitlines(keepends=True)
        if new_lines and not new_lines[-1].endswith("\n"):
            new_lines[-1] = new_lines[-1] + "\n"
    return "".join(
        difflib.unified_diff(
            old.splitlines(keepends=True),
            new.splitlines(keepends=True),
            fromfile=fromfile,
            tofile=tofile,
        )
    )


def colorize_unified_diff(diff_text: str) -> str:
    """Color a unified diff via colordiff when available on a TTY."""
    if not diff_text or not sys.stdout.isatty():
        return diff_text
    if os.environ.get("NO_COLOR", ""):
        return diff_text
    colordiff = shutil.which("colordiff")
    if not colordiff:
        return diff_text
    try:
        # Force color: colordiff sees a pipe (capture_output) and would otherwise
        # skip ANSI; we already gate on our own stdout TTY / NO_COLOR above.
        result = subprocess.run(
            [colordiff, "--color=yes"],
            input=diff_text,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return diff_text
    # colordiff mirrors diff exit codes (0/1); either is fine for display
    if result.returncode in (0, 1) and result.stdout:
        return result.stdout
    return diff_text


def file_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8")


def diff_paths(old_path: Path, new_text: str, *, label: str | None = None) -> str:
    name = label or str(old_path)
    return unified_text_diff(file_text(old_path), new_text, fromfile=f"a/{name}", tofile=f"b/{name}")
