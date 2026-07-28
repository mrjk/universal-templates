"""Zensical macros: live inventory of projects/ and files/ from this repo."""

from __future__ import annotations

from pathlib import Path

import yaml

_DOCS_ROOT = Path(__file__).resolve().parent
_REPO_ROOT = _DOCS_ROOT.parent
_CATALOG = str(_REPO_ROOT)


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


def list_tree(root_name: str) -> list[str]:
    """List catalog entries under projects/ or files/ in this checkout."""
    base = _REPO_ROOT / root_name
    if not base.is_dir():
        return []
    if root_name == "projects":
        return _list_projects(base)
    return _list_files(base)


def _project_blurb(rel_path: str) -> str:
    """Best-effort short description from a project's copier.yml."""
    base = _REPO_ROOT / rel_path
    for name in ("copier.yml", "copier.yaml"):
        cfg = base / name
        if not cfg.is_file():
            continue
        data = yaml.safe_load(cfg.read_text(encoding="utf-8")) or {}
        desc = data.get("description")
        if isinstance(desc, dict):
            return str(desc.get("default") or desc.get("help") or "").strip()
        if isinstance(desc, str):
            return desc.strip()
    return ""


def _esc_cell(text: str) -> str:
    return text.replace("|", r"\|")


def _md_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        cells = []
        for i, cell in enumerate(row):
            text = _esc_cell(cell)
            cells.append(f"`{text}`" if i == 0 else text)
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def define_env(env):
    projects = list_tree("projects")
    files = list_tree("files")

    env.variables["catalog_root"] = _CATALOG
    env.variables["catalog_projects"] = projects
    env.variables["catalog_files"] = files

    @env.macro
    def catalog_projects_table() -> str:
        """Markdown table of projects/ entries (path + description)."""
        if not projects:
            return "_No projects exposed yet._"
        rows = [[p, _project_blurb(p) or "—"] for p in projects]
        return _md_table(["Path", "Description"], rows)

    @env.macro
    def catalog_files_table() -> str:
        """Markdown table of files/ entries."""
        if not files:
            return "_No snip files exposed yet._"
        rows = [[f] for f in files]
        return _md_table(["Path"], rows)

    @env.macro
    def catalog_projects_list() -> str:
        """Bullet list of project paths (for menus / quick scans)."""
        if not projects:
            return "- _(empty)_"
        return "\n".join(f"- `{p}`" for p in projects)

    @env.macro
    def catalog_files_list() -> str:
        """Bullet list of file paths."""
        if not files:
            return "- _(empty)_"
        return "\n".join(f"- `{f}`" for f in files)
