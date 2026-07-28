"""Resolve UT_CATALOG_REPO and list catalog hierarchies."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from ut_cli import proc
from ut_cli.config import catalog_repo


def catalog_root(repo: str | None = None) -> Path | None:
    """Return Path for a local catalog directory, else None for a remote URL."""
    root = repo if repo is not None else catalog_repo()
    path = Path(root).expanduser()
    if path.is_dir():
        return path.resolve()
    return None


def list_tree(root_name: str, *, repo: str | None = None, ref: str | None = None) -> list[str]:
    """List catalog entries under projects/ or files/."""
    local = catalog_root(repo)
    if local is not None:
        return _list_local(local, root_name)

    url = catalog_repo() if repo is None else repo
    tmp = Path(tempfile.mkdtemp(prefix="ut-catalog-list-"))
    try:
        dest = _sparse_clone(url, root_name, ref=ref, dest=tmp / "repo")
        return _list_local(dest, root_name)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _list_local(catalog: Path, root_name: str) -> list[str]:
    base = catalog / root_name
    if not base.is_dir():
        return []
    if root_name == "projects":
        return _list_projects(base)
    return _list_files(base)


def _list_projects(base: Path) -> list[str]:
    items: list[str] = []
    for path in sorted(base.rglob("copier.y*ml")):
        if path.name not in {"copier.yml", "copier.yaml"}:
            continue
        rel = path.parent.relative_to(base.parent)
        items.append(str(rel).replace("\\", "/"))
    return items


def _list_files(base: Path) -> list[str]:
    items: list[str] = []
    for path in sorted(base.rglob("*")):
        if not path.is_file() or path.name.startswith("."):
            continue
        rel = path.relative_to(base.parent)
        items.append(str(rel).replace("\\", "/"))
    return items


def _sparse_clone(url: str, sparse_path: str, *, ref: str | None, dest: Path) -> Path:
    proc.require_tool("git")
    clone = ["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse"]
    if ref:
        clone += ["--branch", ref]
    clone += [url, str(dest)]
    try:
        proc.run(clone)
    except proc.ProcError:
        if dest.exists():
            shutil.rmtree(dest, ignore_errors=True)
        proc.run(
            ["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse", url, str(dest)]
        )
        if ref:
            proc.run(["git", "-C", str(dest), "checkout", ref])
    proc.run(["git", "-C", str(dest), "sparse-checkout", "set", sparse_path], check=False)
    return dest


def resolve_local_path(rel_path: str, *, repo: str | None = None) -> Path:
    """Resolve a catalog-relative path on a local catalog."""
    local = catalog_root(repo)
    if local is None:
        raise FileNotFoundError("catalog is remote; use fetch helpers for paths")
    candidate = (local / rel_path.strip().strip("/")).resolve()
    if not candidate.exists():
        raise FileNotFoundError(f"not found in catalog: {rel_path}")
    return candidate


def fetch_catalog_path(rel_path: str, *, repo: str | None = None, ref: str | None = None) -> Path:
    """
    Ensure catalog path bytes are available locally.
    Returns a path under a temp sparse clone for remotes, or the local path.
    Caller owns cleanup only for remotes (returned path's parents may be temp).
    """
    rel_path = rel_path.strip().strip("/")
    local = catalog_root(repo)
    if local is not None:
        return resolve_local_path(rel_path, repo=repo)

    url = catalog_repo() if repo is None else repo
    tmp = Path(tempfile.mkdtemp(prefix="ut-catalog-fetch-"))
    dest = _sparse_clone(url, rel_path, ref=ref, dest=tmp / "repo")
    candidate = dest / rel_path
    if not candidate.exists():
        shutil.rmtree(tmp, ignore_errors=True)
        raise FileNotFoundError(f"not found in catalog: {rel_path}")
    return candidate


def numbered_menu(title: str, items: list[str]) -> str | None:
    """Stdlib numbered menu; returns selected item or None if cancelled."""
    if not items:
        print(f"{title}\n  (empty)")
        return None
    print(title)
    for i, item in enumerate(items, start=1):
        print(f"  {i}) {item}")
    print("  q) cancel")
    try:
        choice = input("Select: ").strip().lower()
    except EOFError:
        return None
    if choice in {"", "q", "quit"}:
        return None
    if not choice.isdigit():
        return None
    idx = int(choice)
    if idx < 1 or idx > len(items):
        return None
    return items[idx - 1]


def multi_select_menu(title: str, items: list[str], *, preselect_all: bool = False) -> list[str]:
    """
    Numbered multi-select. Enter comma-separated indexes, 'a' for all, empty for none.
    """
    if not items:
        print(f"{title}\n  (empty)")
        return []
    print(title)
    for i, item in enumerate(items, start=1):
        mark = "[x]" if preselect_all else "[ ]"
        print(f"  {i}) {mark} {item}")
    print("  a) all   <empty>) none   or comma-separated numbers")
    try:
        choice = input("Select: ").strip().lower()
    except EOFError:
        return []
    if choice in {"", "n", "none"}:
        return []
    if choice in {"a", "all"}:
        return list(items)
    selected: list[str] = []
    for part in choice.split(","):
        part = part.strip()
        if not part.isdigit():
            continue
        idx = int(part)
        if 1 <= idx <= len(items):
            selected.append(items[idx - 1])
    return selected
