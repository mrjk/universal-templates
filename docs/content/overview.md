# Overview

**universal-templates** is a public (or private) **git catalog** of boilerplate:

- **Projects** — full skeletons under `projects/` (e.g. a small Python package)
- **Files / snips** — fragments and scripts under `files/` you used to copy-paste

You consume it with two commands that share the same habits: catalog URL, list/browse, sync, pins, and **diff → confirm** before overwrite.

## Two jobs, one experience

```text
        ┌──────────────────────────────────────┐
        │  seed / snip  (what you type)        │
        │  menus · sync · pins · confirm       │
        └──────────────────┬───────────────────┘
               ┌───────────┴───────────┐
               ▼                       ▼
           Copier                    vendir
        projects/*                  files/*
```

| You want… | Use |
|-----------|-----|
| New app from a maintained skeleton | `seed new …` then later `seed sync` |
| Refresh shared helpers inside an old script | `snip sync ./that_script.sh` |
| Drop a catalog file into a folder | `snip add files/…` |
| Use *your* snippets instead of the public ones | Set `UT_CATALOG_REPO` |

You talk to **`seed` / `snip`**, not to Copier or vendir day-to-day.

## Mental model

1. **The catalog** is the source of truth (this repo, a fork, or a local path).
2. **`seed`** grows or updates a **project directory**.
3. **`snip`** refreshes **whole files**, **inject regions** (`snip:id=`), or **boilerplate slots** (`snip:slot=`).
4. **Pins** (git refs / tags) record which version you applied.
5. Updates are never silent: you see a **diff**, confirm, then **catalog wins** (or pass `-y` for CI).

## Tiny taste

```bash
seed list                          # what’s available under projects/
seed new projects/python-base ./my-app

snip list                          # what’s available under files/
snip sync ./myscript.sh            # update marked regions
```

Next: hands-on [Tutorial](tutorial.md).
