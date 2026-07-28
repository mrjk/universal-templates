# Status

Product intent vs what the tree does today.

## Target

| Piece | Intent |
|-------|--------|
| Catalog | `projects/` + `files/{bin,src,notes}/` |
| UX | Unified **`seed`** + **`snip`** (menus, sync, pins, diff/confirm) |
| Backends | **`seed` → Copier**, **`snip` → vendir** (via mise only; no third engine) |
| Config | `UT_CATALOG_REPO` |

Docs in [`docs/content/`](README.md) describe that target.

## Today

| Piece | Current state |
|-------|----------------|
| CLIs | **`bin/seed`** / **`bin/snip`** (`ut_cli/`) — primary UX |
| Catalog roots | `projects/` (incl. `python-base`, `_fixture`) + `files/src/_fixture/`; legacy `templates/`, `parts/`, `common/` still present |
| `UT_CATALOG_REPO` | Set in `mise.toml`; honored by seed/snip |
| Copier | Pinned via mise; wrapped by `seed` |
| vendir | Pinned via mise; wrapped by `snip` |
| Anchor `snip sync <file>` | Implemented (`ut_cli/anchors.py`) |
| `bp` | Deprecated prototype — still works; do not extend |

## How to read the docs

1. [Overview](overview.md) + [Quickstart](quickstart.md)  
2. [Seed](seed.md) / [Snip](snip.md) / [Catalog](catalog.md)  
3. [ADR 0004](../adr/0004-backend-tools-via-mise.md) — Copier or vendir, unified UX  
4. Root [`README.md`](../../README.md) for install + mise
