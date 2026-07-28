# Docs

**User guide (site source):** [content/](content/index.md) — catalog layout, inventory, authoring.

**CLI docs** (`seed` / `snip`): [snipseed](https://github.com/mrjk/snipseed/tree/main/docs/content)

**Preview / build** (Zensical — config stays `mkdocs.yml`):

```bash
# from docs/
task install   # once: pip install -r requirements.txt
task serve     # http://localhost:8089
task build     # writes site/

# or from repo root
task docs:install
task docs:serve
task docs:build
```

Also:

- **[ADRs](content/adr/README.md)** — catalog decisions (0001, 0003)
- **[mkdocs.yml](mkdocs.yml)** — Zensical config (`docs_dir: content`)
- **[macros.py](macros.py)** — live `projects/` + `files/` inventory
- **[Taskfile.yml](Taskfile.yml)** — install / serve / build
