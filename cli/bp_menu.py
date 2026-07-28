#!/usr/bin/env python3
"""Interactive menu for bp — optional layer over the bash CLI."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from collections import defaultdict
from pathlib import Path


def _fail(msg: str, code: int = 1) -> None:
    print(f"error: {msg}", file=sys.stderr)
    raise SystemExit(code)


def _ensure_deps() -> None:
    missing = []
    try:
        import questionary  # noqa: F401
    except ImportError:
        missing.append("questionary")
    try:
        import rich  # noqa: F401
    except ImportError:
        missing.append("rich")
    if missing:
        _fail(
            "missing Python packages: "
            + ", ".join(missing)
            + "\ninstall: pip install -r cli/requirements.txt"
        )


def _find_bp() -> str:
    env = os.environ.get("BP_BIN")
    if env and Path(env).is_file():
        return env
    which = shutil.which("bp")
    if which:
        return which
    here = Path(__file__).resolve().parent.parent / "bin" / "bp"
    if here.is_file():
        return str(here)
    _fail("bp executable not found (install via ./install.sh or set BP_BIN)")


def _run(bp: str, args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [bp, *args],
        check=check,
        text=True,
        capture_output=True,
    )


def _browse(bp: str, repo: str, ref: str | None) -> list[str]:
    args = ["browse", repo]
    if ref:
        args.append(ref if ref.startswith("@") else f"@{ref}")
    try:
        proc = _run(bp, args)
    except subprocess.CalledProcessError as exc:
        err = (exc.stderr or exc.stdout or str(exc)).strip()
        _fail(f"bp browse failed: {err}")
    paths: list[str] = []
    section = ""
    for line in proc.stdout.splitlines():
        if line.startswith("parts:"):
            section = "parts"
            continue
        if line.startswith("common:"):
            section = "common"
            continue
        if line.startswith("templates:"):
            section = ""
            continue
        if section and line.startswith("  ") and "(none)" not in line:
            paths.append(line.strip())
    return paths


def _group_paths(paths: list[str]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = defaultdict(list)
    for p in paths:
        parts = p.split("/")
        # parts/python/pytest -> python; common/gitignore -> common
        if parts[0] == "parts" and len(parts) >= 3:
            groups[parts[1]].append(p)
        elif parts[0] == "common":
            groups["common"].append(p)
        else:
            groups["other"].append(p)
    return dict(groups)


def main() -> None:
    try:
        _ensure_deps()
        import questionary
        from rich.console import Console
        from rich.panel import Panel

        console = Console()
        bp = _find_bp()

        repo = os.environ.get("BP_DEFAULT_REPO", "").strip()
        if not repo:
            repo = questionary.text("Boilerplate repo URL or local path:").ask()
            if not repo:
                _fail("repo is required")

        ref = questionary.text("Git ref (empty for main):", default="").ask()
        if ref is None:
            raise SystemExit(0)

        paths = _browse(bp, repo, ref or None)
        if not paths:
            console.print("[yellow]No parts found in that repo.[/yellow]")
            raise SystemExit(0)

        groups = _group_paths(paths)
        choices = []
        for group in sorted(groups.keys()):
            for p in sorted(groups[group]):
                choices.append(questionary.Choice(title=f"[{group}] {p}", value=p))

        selected = questionary.checkbox(
            "Select parts (space to toggle, enter to confirm):",
            choices=choices,
        ).ask()
        if selected is None:
            raise SystemExit(0)
        if not selected:
            console.print("Nothing selected.")
            raise SystemExit(0)

        action = questionary.select(
            "Action:",
            choices=[
                questionary.Choice("Add selected parts", "add"),
                questionary.Choice("Update by part name (installed)", "update"),
                questionary.Choice("Remove by part name (installed)", "remove"),
            ],
        ).ask()
        if action is None:
            raise SystemExit(0)

        console.print(Panel.fit(f"repo={repo}\naction={action}\nparts={len(selected)}"))

        for path in selected:
            name = Path(path).name
            try:
                if action == "add":
                    args = ["add", repo, path, "-y"]
                    if ref:
                        args.insert(3, ref if ref.startswith("@") else f"@{ref}")
                    proc = _run(bp, args, check=False)
                elif action == "update":
                    proc = _run(bp, ["update", name, "-y"], check=False)
                else:
                    proc = _run(bp, ["remove", name, "-y"], check=False)
            except OSError as exc:
                _fail(str(exc))

            out = (proc.stdout or "").strip()
            err = (proc.stderr or "").strip()
            if proc.returncode == 0:
                console.print(f"[green]ok[/green] {name}: {out or '(done)'}")
            else:
                console.print(f"[red]fail[/red] {name}: {err or out or 'unknown error'}")

    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 — never dump a raw traceback to users
        _fail(str(exc))


if __name__ == "__main__":
    main()
