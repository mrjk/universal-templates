# Docs

**User guide (site source):** [content/](content/index.md) — catalog layout, inventory, authoring.

**CLI docs** (`seed` / `snip`): [snipseed](https://github.com/mrjk/snipseed/tree/main/docs/content)

**Preview / build** (Zensical — config stays `mkdocs.yml`):

```bash
# from repo root (preferred)
task install       # uv sync: snipseed + docs group
task docs:serve    # http://localhost:8089
task docs:build

# or from docs/
task install
task serve
task build
```

Also:

- **[ADRs](content/adr/README.md)** — catalog decisions (0001, 0003)
- **[mkdocs.yml](mkdocs.yml)** — Zensical config (`docs_dir: content`)
- **[macros.py](macros.py)** — live `projects/` + `files/` inventory
- **[Taskfile.yml](Taskfile.yml)** — install / serve / build
