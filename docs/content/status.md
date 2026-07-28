# Status

What’s shipped vs still migrating. New users: start with the [Tutorial](tutorial.md) — you don’t need this page first.

## Shipped

| Piece | State |
|-------|--------|
| `bin/seed` / `bin/snip` | Primary UX (`ut_cli/`) |
| Catalog roots | `projects/` + `files/` (growing) |
| `UT_CATALOG_REPO` | Honored (URL or local path) |
| Copier / vendir | Pinned via mise; wrapped by the CLIs |
| Anchor `snip sync <file>` (inject) | Supported |
| Boilerplate `snip:slot=` whole-file sync | Supported |
| Docs learning path | Overview → Tutorial → Seed / Snip / Catalog / Inventory |
| Docs inventory page | Live `projects/` + `files/` via Zensical macros |

## Still transitional

| Piece | Notes |
|-------|--------|
| Catalog content | Growing; live list on [Inventory](inventory.md) (build-time macros, not committed) |

## Related

[Overview](overview.md) · [ADRs](adr/README.md)
