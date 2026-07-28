#!/usr/bin/env python3
"""seed — project scaffolds via Copier."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running as script from bin/ without install
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from ut_cli import catalog, confirm, copier_wrap, proc
from ut_cli.config import add_common_flags, catalog_repo, common_from_args


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="seed",
        description="Create and update whole projects from projects/ (wraps Copier).",
    )
    add_common_flags(p)
    sub = p.add_subparsers(dest="command")

    new_p = sub.add_parser("new", help="Generate a project from a catalog path")
    new_p.add_argument("project_path", help="e.g. projects/python-base")
    new_p.add_argument(
        "dest",
        nargs="?",
        default=".",
        help="Destination directory (default: cwd)",
    )
    add_common_flags(new_p)

    sync_p = sub.add_parser("sync", help="Update current project from linked template")
    sync_p.add_argument(
        "dest",
        nargs="?",
        default=".",
        help="Project directory with .copier-answers.yml",
    )
    add_common_flags(sync_p)

    list_p = sub.add_parser("list", help="List projects/ in the catalog")
    add_common_flags(list_p)

    return p


def cmd_list(opts) -> int:
    items = catalog.list_tree("projects", ref=opts.ref)
    if not items:
        print("(no projects found)")
        return 0
    for item in items:
        print(item)
    return 0


def cmd_new(args, opts) -> int:
    project_path = args.project_path.strip().strip("/")
    if not project_path.startswith("projects/"):
        # allow bare name → projects/<name>
        if "/" not in project_path:
            project_path = f"projects/{project_path}"
    dest = Path(args.dest)
    try:
        if not opts.yes and dest.exists() and any(dest.iterdir()):
            # Show what we will do; Copier handles file prompts unless -y
            print(f"seed new {project_path} → {dest}")
            print(f"catalog: {catalog_repo()}")
            if not confirm.confirm("Continue?", yes=False):
                return 1
        copier_wrap.copy_project(project_path, dest, ref=opts.ref, yes=opts.yes)
    except (FileNotFoundError, proc.ToolMissingError, proc.ProcError) as exc:
        proc.die(str(exc))
    return 0


def cmd_sync(args, opts) -> int:
    dest = Path(args.dest)
    try:
        if not opts.yes:
            print(f"seed sync in {dest.resolve()}")
            print(f"catalog: {catalog_repo()}")
            # Copier update shows its own diffs; we still confirm intent
            if not confirm.confirm("Run template update (catalog wins)?", yes=False):
                return 1
        copier_wrap.update_project(dest, ref=opts.ref, yes=opts.yes)
    except (FileNotFoundError, proc.ToolMissingError, proc.ProcError) as exc:
        proc.die(str(exc))
    return 0


def cmd_browse(opts) -> int:
    items = catalog.list_tree("projects", ref=opts.ref)
    choice = catalog.numbered_menu("Projects", items)
    if not choice:
        return 1
    # Reuse new into cwd
    class Args:
        project_path = choice
        dest = "."

    return cmd_new(Args(), opts)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    opts = common_from_args(args)

    # Subparsers may not inherit top-level -y/--ref; merge from namespace
    if hasattr(args, "yes"):
        opts.yes = opts.yes or bool(args.yes)
    if getattr(args, "ref", None):
        opts.ref = args.ref

    if args.command is None:
        return cmd_browse(opts)
    if args.command == "list":
        return cmd_list(opts)
    if args.command == "new":
        return cmd_new(args, opts)
    if args.command == "sync":
        return cmd_sync(args, opts)
    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
