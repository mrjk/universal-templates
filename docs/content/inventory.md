---
render_macros: true
---

# Inventory

Live listing of what this catalog exposes — generated at docs build time from the trees on disk (same sources as `seed list` / `snip list`).

## Projects (`seed`)

{{ catalog_projects_table() }}

```bash
seed list
seed new <path> .
```

## Files (`snip`)

{{ catalog_files_table() }}

```bash
snip list
snip add <path>
```

## Notes

- Paths starting with `_` (e.g. `_fixture`) are fixtures for tests and learning.
- Layout, pins, and self-hosting: [Catalog](catalog.md).
- Adding content: drop a Copier project under `projects/` or a unit under `files/`, then rebuild docs.
