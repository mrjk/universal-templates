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

## Today (transitional)

| Piece | Current state |
|-------|----------------|
| CLIs | `bin/bp` prototype — **not** the long-term UX |
| Catalog roots | Legacy `templates/`, `parts/`, `common/` → migrating |
| `UT_CATALOG_REPO` | Set in `mise.toml`; wire into `seed`/`snip` as they land |
| Copier | Available via mise; usable as a **dev escape hatch** |
| vendir | Not wired yet; required for `snip` implementation |
| Anchor `snip sync` | Specified in docs/ADRs; not the shipped interface yet |

Prefer implementing **`seed` / `snip`** wrappers over extending `bp`.

## How to read the docs

1. [Overview](overview.md) + [Quickstart](quickstart.md)  
2. [Seed](seed.md) / [Snip](snip.md) / [Catalog](catalog.md)  
3. [ADR 0004](../adr/0004-backend-tools-via-mise.md) — Copier or vendir, unified UX  
4. Root `README.md` may still describe `bp` until rewritten
