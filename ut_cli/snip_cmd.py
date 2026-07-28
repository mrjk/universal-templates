#!/usr/bin/env python3
"""snip — file/region sync via vendir + anchors."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from ut_cli import anchors, catalog, confirm, diffutil, proc, vendir_wrap
from ut_cli.config import add_common_flags, catalog_repo, common_from_args


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="snip",
        description="Sync files and in-file regions from files/ (wraps vendir).",
    )
    add_common_flags(p)
    sub = p.add_subparsers(dest="command")

    add_p = sub.add_parser("add", help="Vendor a catalog path into the project")
    add_p.add_argument("catalog_path", help="e.g. files/src/logging-setup")
    add_p.add_argument(
        "--dest",
        default=".",
        help="Destination directory (default: cwd)",
    )
    add_common_flags(add_p)

    sync_p = sub.add_parser("sync", help="Sync tracked paths or anchors/slots in a file")
    sync_p.add_argument(
        "target",
        nargs="?",
        default=None,
        help="Optional file with snip anchors/slots; omit to sync tracked vendir units",
    )
    add_common_flags(sync_p)

    list_p = sub.add_parser("list", help="List files/ in catalog, or anchors/slots in a file")
    list_p.add_argument(
        "target",
        nargs="?",
        default=None,
        help="Optional local file to list anchors/slots in",
    )
    add_common_flags(list_p)

    return p


def cmd_list_catalog(opts) -> int:
    items = catalog.list_tree("files", ref=opts.ref)
    if not items:
        print("(no files found)")
        return 0
    for item in items:
        print(item)
    return 0


def cmd_list_file(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    found = anchors.parse_anchors(text)
    slots = anchors.parse_slots(text)
    header = anchors.parse_file_header(text)
    if header.template_source or header.curr_version or header.path:
        print(
            f"header: source={header.template_source} version={header.curr_version}"
            f" path={header.path} ref={header.ref}"
        )
    if found and slots:
        print("error: file mixes snip:id= (inject) and snip:slot= (boilerplate)", file=sys.stderr)
        return 1
    if slots:
        for s in slots:
            print(f"slot:{s.id}")
        return 0
    if not found:
        print("(no snip anchors or slots)")
        return 0
    for a in found:
        print(f"{a.id}\tpath={a.path}\tref={a.ref}")
    return 0


def cmd_add(args, opts) -> int:
    catalog_path = args.catalog_path.strip().strip("/")
    if not catalog_path.startswith("files/"):
        catalog_path = f"files/{catalog_path}"
    dest = Path(args.dest)
    try:
        # Preview: fetch and diff if dest file exists
        new_bytes = vendir_wrap.fetch_bytes(catalog_path, ref=opts.ref)
        leaf = Path(catalog_path).name
        target = dest / leaf
        old = diffutil.file_text(target) if target.is_file() else ""
        new_text = new_bytes.decode("utf-8")
        # If dest already has slots, merge instead of clobbering on re-add
        if old and anchors.parse_slots(old):
            new_text = anchors.merge_boilerplate(new_text, anchors.get_slot_bodies(old))
        diff = diffutil.unified_text_diff(
            old, new_text, fromfile=f"a/{leaf}", tofile=f"b/{leaf}"
        )
        if old and not confirm.show_diff_and_confirm(diff, yes=opts.yes):
            return 1
        if not old and not opts.yes:
            print(f"snip add {catalog_path} → {dest}")
            print(f"catalog: {catalog_repo()}")
            if not confirm.confirm("Add from catalog?", yes=False):
                return 1
        if old and anchors.parse_slots(old):
            pin = opts.ref or "HEAD"
            target.write_text(
                anchors.bump_file_header_ref(new_text, pin),
                encoding="utf-8",
            )
            print(f"merged boilerplate {target}")
            return 0
        out = vendir_wrap.add_unit(catalog_path, dest=dest, ref=opts.ref, base=dest)
        print(f"added {out}")
    except (FileNotFoundError, IsADirectoryError, proc.ToolMissingError, proc.ProcError) as exc:
        proc.die(str(exc))
    return 0


def _resolve_tracked_target(leaf: str) -> Path:
    target = Path(leaf)
    if target.is_file():
        return target
    candidates = list(Path(".").glob(f"**/{leaf}"))
    return candidates[0] if candidates else Path(leaf)


def _sync_boilerplate_text(old: str, catalog_text: str, *, pin: str) -> str:
    bodies = anchors.get_slot_bodies(old)
    merged = anchors.merge_boilerplate(catalog_text, bodies)
    return anchors.bump_file_header_ref(merged, pin)


def cmd_sync_tracked(opts) -> int:
    units = vendir_wrap.load_units()
    if not units:
        proc.die("no tracked snip units; use snip add first")
    try:
        work = vendir_wrap.state_dir()
        vendir_wrap.write_vendir_config(units, dest_dir=work)
        for unit in units:
            catalog_path = unit["path"]
            ref = opts.ref or unit.get("ref")
            new_bytes = vendir_wrap.fetch_bytes(catalog_path, ref=ref)
            leaf = Path(catalog_path).name
            target = _resolve_tracked_target(leaf)
            old = diffutil.file_text(target) if target.is_file() else ""
            catalog_text = new_bytes.decode("utf-8")
            pin = ref or "HEAD"
            if old and anchors.parse_slots(old):
                new_text = _sync_boilerplate_text(old, catalog_text, pin=pin)
            else:
                new_text = catalog_text
            diff = diffutil.unified_text_diff(
                old, new_text, fromfile=f"a/{leaf}", tofile=f"b/{leaf}"
            )
            if not confirm.show_diff_and_confirm(
                diff or "--- (new file)\n", yes=opts.yes, prompt=f"Apply {catalog_path}?"
            ):
                continue
            if old and anchors.parse_slots(old):
                target.write_text(new_text, encoding="utf-8")
            else:
                vendir_wrap.add_unit(catalog_path, dest=target.parent, ref=ref)
            print(f"synced {catalog_path}")
    except (FileNotFoundError, proc.ToolMissingError, proc.ProcError) as exc:
        proc.die(str(exc))
    return 0


def cmd_sync_inject(path: Path, text: str, found: list, opts) -> int:
    labels = [f"{a.id}  path={a.path}  ref={a.ref}" for a in found]
    if opts.yes:
        selected_labels = labels
    else:
        selected_labels = catalog.multi_select_menu("Portions to update", labels)
    if not selected_labels:
        print("nothing selected")
        return 0

    selected_ids = {lab.split()[0] for lab in selected_labels}
    current = text
    to_apply = [a for a in found if a.id in selected_ids]
    to_apply.sort(key=lambda a: a.start_line, reverse=True)

    try:
        for anchor in to_apply:
            if not anchor.path:
                print(f"skip {anchor.id}: missing path=", file=sys.stderr)
                continue
            ref = opts.ref or anchor.ref
            new_bytes = vendir_wrap.fetch_bytes(anchor.path, ref=ref)
            new_body = new_bytes.decode("utf-8")
            refreshed = {a.id: a for a in anchors.parse_anchors(current)}
            anchor = refreshed[anchor.id]
            old_body = anchors.get_body(current, anchor)
            diff = diffutil.unified_text_diff(
                old_body,
                new_body if new_body.endswith("\n") else new_body + "\n",
                fromfile=f"a/{anchor.id}",
                tofile=f"b/{anchor.id}",
            )
            if not confirm.show_diff_and_confirm(
                diff, yes=opts.yes, prompt=f"Apply {anchor.id}?"
            ):
                continue
            pin = ref or "HEAD"
            current = anchors.replace_body(current, anchor, new_body, new_ref=pin)
            print(f"updated {anchor.id} → ref={pin}")
        path.write_text(current, encoding="utf-8")
    except (FileNotFoundError, IsADirectoryError, proc.ToolMissingError, proc.ProcError) as exc:
        proc.die(str(exc))
    return 0


def cmd_sync_boilerplate(path: Path, text: str, opts) -> int:
    header = anchors.parse_file_header(text)
    catalog_path = header.path
    if not catalog_path:
        proc.die(f"boilerplate file missing header 'snip: path=...': {path}")
    ref = opts.ref or header.ref
    try:
        new_bytes = vendir_wrap.fetch_bytes(catalog_path, ref=ref)
        catalog_text = new_bytes.decode("utf-8")
        pin = ref or "HEAD"
        merged = _sync_boilerplate_text(text, catalog_text, pin=pin)
        diff = diffutil.unified_text_diff(
            text, merged, fromfile=f"a/{path.name}", tofile=f"b/{path.name}"
        )
        if not confirm.show_diff_and_confirm(
            diff, yes=opts.yes, prompt=f"Apply boilerplate {catalog_path}?"
        ):
            return 1
        path.write_text(merged, encoding="utf-8")
        print(f"updated boilerplate {path} → ref={pin}")
    except (FileNotFoundError, IsADirectoryError, proc.ToolMissingError, proc.ProcError) as exc:
        proc.die(str(exc))
    return 0


def cmd_sync_file(path: Path, opts) -> int:
    text = path.read_text(encoding="utf-8")
    found = anchors.parse_anchors(text)
    slots = anchors.parse_slots(text)
    if found and slots:
        proc.die(
            f"{path}: mixes snip:id= (inject) and snip:slot= (boilerplate); use one mode"
        )
    if slots:
        return cmd_sync_boilerplate(path, text, opts)
    if not found:
        proc.die(f"no snip anchors or slots in {path}")
    return cmd_sync_inject(path, text, found, opts)


def cmd_browse(opts) -> int:
    items = catalog.list_tree("files", ref=opts.ref)
    choice = catalog.numbered_menu("Files", items)
    if not choice:
        return 1

    class Args:
        catalog_path = choice
        dest = "."

    return cmd_add(Args(), opts)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    opts = common_from_args(args)
    if hasattr(args, "yes"):
        opts.yes = opts.yes or bool(args.yes)
    if getattr(args, "ref", None):
        opts.ref = args.ref

    if args.command is None:
        return cmd_browse(opts)
    if args.command == "list":
        if args.target:
            return cmd_list_file(Path(args.target))
        return cmd_list_catalog(opts)
    if args.command == "add":
        return cmd_add(args, opts)
    if args.command == "sync":
        if args.target:
            return cmd_sync_file(Path(args.target), opts)
        return cmd_sync_tracked(opts)
    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
