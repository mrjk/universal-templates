"""Invoke Copier via subprocess."""

from __future__ import annotations

import re
from pathlib import Path

from ut_cli import proc
from ut_cli.catalog import catalog_root, fetch_catalog_path
from ut_cli.config import catalog_repo


def copier_bin() -> str:
    return proc.require_tool("copier")


def template_source(project_path: str, *, ref: str | None = None) -> str:
    """Resolve Copier src for a projects/... path (local path or fetched remote)."""
    project_path = project_path.strip().strip("/")
    local = catalog_root()
    if local is not None:
        src = local / project_path
        if not src.is_dir():
            raise FileNotFoundError(f"project not found: {src}")
        return str(src)
    # Remote: sparse-fetch subdirectory for reliable subdirectory templates
    return str(fetch_catalog_path(project_path, ref=ref))


def copy_project(
    project_path: str,
    dest: str | Path,
    *,
    ref: str | None = None,
    yes: bool = False,
) -> None:
    src = template_source(project_path, ref=ref)
    dest_path = Path(dest)
    dest_path.mkdir(parents=True, exist_ok=True)
    cmd = [copier_bin(), "copy"]
    if yes:
        cmd += ["--defaults", "--overwrite"]
    if ref and catalog_root() is None:
        # ref already applied via fetch; still pass vcs-ref when src is git URL
        pass
    cmd += [src, str(dest_path)]
    proc.run(cmd, capture=False)


def update_project(
    dest: str | Path = ".",
    *,
    ref: str | None = None,
    yes: bool = False,
) -> None:
    dest_path = Path(dest).resolve()
    answers = dest_path / ".copier-answers.yml"
    if not answers.is_file():
        answers = dest_path / ".copier-answers.yaml"
    if not answers.is_file():
        raise FileNotFoundError(
            f"no .copier-answers.yml in {dest_path}; run seed new first"
        )

    answers_text = answers.read_text(encoding="utf-8")
    has_commit = bool(re.search(r"(?m)^_commit:", answers_text))
    in_git = (
        proc.run(
            ["git", "-C", str(dest_path), "rev-parse", "--is-inside-work-tree"],
            check=False,
        ).returncode
        == 0
    )

    # Copier update needs a git-tracked project + prior template commit.
    # Local-path templates / non-git dests use recopy (catalog wins).
    if in_git and has_commit:
        cmd = [copier_bin(), "update"]
        if yes:
            cmd += ["--defaults", "--skip-answered"]
    else:
        cmd = [copier_bin(), "recopy"]
        if yes:
            cmd += ["--defaults", "--overwrite", "--skip-answered"]
        else:
            cmd += ["--overwrite"]
    if ref:
        cmd += ["--vcs-ref", ref]
    cmd.append(str(dest_path))
    proc.run(cmd, cwd=str(dest_path), capture=False)


def catalog_identity() -> str:
    return catalog_repo()
