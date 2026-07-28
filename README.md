# universal-templates

A **git catalog** of project scaffolds (`projects/`) and reusable snippets (`files/`).

Consume it with [**snipseed**](https://github.com/mrjk/snipseed) (`seed` / `snip`). Point tools here via `UT_CATALOG_REPO`.

## Learn it

1. [Overview](docs/content/overview.md) — catalog mental model  
2. [Catalog](docs/content/catalog.md) — layout, pins, self-hosting  
3. [Inventory](docs/content/inventory.md) — what’s shipped  

CLI tutorial / reference: [snipseed docs](https://github.com/mrjk/snipseed/tree/main/docs/content)

Preview catalog docs: `task docs:serve`

## Layout

```text
projects/          # seed → Copier scaffolds
files/             # snip → file / region units
docs/content/      # catalog docs (Zensical)
```

## Development (this catalog)

```bash
mise trust && mise install
task docs:serve    # preview site
task ci            # build docs
```

Library / template generation stays here. CLI source lives in snipseed.
