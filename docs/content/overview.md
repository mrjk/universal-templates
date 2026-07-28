# Overview

**universal-templates** is a **public git catalog** of boilerplate you (and others) can reuse:

- **Projects** — full skeletons (Python web, shell+bats, …)
- **Files / snips** — shared fragments and standalone scripts you used to copy-paste

There is no package registry and no server. Distribution is **git**. Anyone can fork the repo (or keep a private mirror) and point the tools at it.

## Two jobs, one experience

You use **`seed`** and **`snip`**. Same catalog URL, same style of menu / sync / pins / diff-then-confirm. Under the hood the wrappers call **Copier** (projects) or **vendir** (files) via mise — you do not drive those tools day-to-day.

```text
        ┌──────────────────────────────────────┐
        │  seed / snip  (unified UX)           │
        │  menus · sync · pins · confirm       │
        └──────────────────┬───────────────────┘
               ┌───────────┴───────────┐
               ▼                       ▼
           Copier                    vendir
        projects/*                  files/*
```

| You want… | Use |
|-----------|-----|
| Bootstrap a Python app with CI, answer a few questions, done | `seed` |
| Fix an old shell script that still has copy-pasted helpers | `snip sync ./that_script.sh` |
| Publish *your* snippets for yourself or a team | Same tools + your own git URL |

## Mental model

1. **The catalog** is the source of truth (this repo, or yours).
2. **`seed`** grows or updates a **project directory** from `projects/…` (wraps Copier).
3. **`snip`** refreshes **files / regions** from `files/…` (wraps vendir for fetch/lock; thin glue for anchors and menus).
4. **Pins** (git tags/refs) show which version is deployed — same idea for both CLIs.

## Example: forgotten script

```bash
snip sync ~/bin/deploy.sh
```

Marked blocks → menu → diff → confirm → **catalog wins** for that region.

## Example: new project

```bash
seed
# → pick projects/python-web
# → answer name / options
# → tree appears; later: seed sync
```

## Design constraints (short)

- **Wrap Copier or vendir only** — unified UX; no third sync engine.
- Lean Python glue is fine; this is **not** a heavy Python app.
- Self-host by changing one setting: `UT_CATALOG_REPO`.

Next: [Quickstart](quickstart.md).
