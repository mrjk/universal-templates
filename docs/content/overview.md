# Overview

**universal-templates** is a public (or private) **git catalog** of boilerplate:

- **Projects** — full skeletons under `projects/` (e.g. a Python package or Ansible base)
- **Files / snips** — fragments and scripts under `files/` you used to copy-paste

Distribution is **git**. There is no registry and no custom server — a URL or local path is enough.

## How you consume it

Install the [**snipseed**](https://github.com/mrjk/snipseed) CLIs (`seed` / `snip`), then point them at this catalog:

```bash
export UT_CATALOG_REPO="https://github.com/mrjk/universal-templates.git"
# or a local checkout / your fork

seed list
snip list
```

| Catalog tree | CLI | Job |
|--------------|-----|-----|
| `projects/` | `seed` | Create / update a whole project (Copier) |
| `files/` | `snip` | Drop in or refresh files and marked regions (vendir) |

CLI tutorials and reference live in **snipseed**, not here.

## This repo’s job

1. Keep **`projects/`** and **`files/`** useful and versioned (prefer git tags).
2. Document **layout and hosting** so forks stay compatible.
3. Publish an **[Inventory](inventory.md)** of what is exposed.

Authoring: [Catalog](catalog.md) · [Guides](guides/index.md) · [ADR 0003](adr/0003-catalog-layout-and-self-hosting.md).
