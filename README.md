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

### Install tools (public)

```bash
mise trust && mise install
task install       # snipseed from GitHub main + docs deps → .venv
seed list          # uses this checkout (UT_CATALOG_REPO)
snip list
task docs:serve
task ci            # public install + build docs
```

Runtime backends: **copier** / **vendir** (mise).

### Develop snipseed against this catalog

```bash
task snipseed:dev
# edit snipseed → seed / snip pick up changes immediately
task install       # restore public git pin when done
```

Local path (first match wins):

1. `task snipseed:dev SNIPSEED_SRC=/path/to/snipseed`
2. env `SNIPSEED_SRC`
3. `mise.local.toml` → `[env] SNIPSEED_SRC = "…"`
4. default `../../misc_python/snipseed`
