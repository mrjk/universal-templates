"""Diff display + y/N confirm (catalog wins after accept)."""

from __future__ import annotations

import sys


def confirm(prompt: str = "Apply changes?", *, yes: bool = False) -> bool:
    if yes:
        return True
    try:
        answer = input(f"{prompt} [y/N] ").strip().lower()
    except EOFError:
        return False
    return answer in {"y", "yes"}


def show_diff_and_confirm(diff_text: str, *, yes: bool = False, prompt: str = "Apply catalog changes?") -> bool:
    if not diff_text.strip():
        print("No changes.", file=sys.stderr)
        return False
    sys.stdout.write(diff_text)
    if not diff_text.endswith("\n"):
        sys.stdout.write("\n")
    return confirm(prompt, yes=yes)
