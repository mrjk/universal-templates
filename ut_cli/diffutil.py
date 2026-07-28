"""Unified diff helpers (stdlib difflib)."""

from __future__ import annotations

import difflib
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


def file_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8")


def diff_paths(old_path: Path, new_text: str, *, label: str | None = None) -> str:
    name = label or str(old_path)
    return unified_text_diff(file_text(old_path), new_text, fromfile=f"a/{name}", tofile=f"b/{name}")
