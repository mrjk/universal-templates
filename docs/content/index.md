# Learn universal-templates

A **git catalog** of reusable project scaffolds and file snippets:

| Tree | Contents |
|------|----------|
| **`projects/`** | Full project templates (Copier) — consumed with `seed` |
| **`files/`** | Scripts and fragments — consumed with `snip` |

No package registry. Anyone can fork or host their own catalog with the same layout.

## Tools live elsewhere

The **`seed`** / **`snip`** CLIs are the [**snipseed**](https://github.com/mrjk/snipseed) project. Install and use them from there; point `UT_CATALOG_REPO` at this repo (or your fork).

## Suggested path

| Step | Doc | What you do |
|------|-----|-------------|
| 1 | [Overview](overview.md) | Catalog mental model |
| 2 | [Catalog](catalog.md) | Layout, pins, self-hosting |
| 3 | [Inventory](inventory.md) | What’s in this catalog today |
| 4 | [Author a catalog](guides/index.md) | Add projects / files |

CLI usage (tutorial, guides, `seed` / `snip` reference): **[snipseed docs](https://github.com/mrjk/snipseed/tree/main/docs/content)**.

Architecture (catalog): [ADRs](adr/README.md)
