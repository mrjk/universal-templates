# Docs

**User guide (site source):** [content/](content/index.md) — Overview → Tutorial → Seed / Snip / Catalog.

**Preview / build** (Zensical — Material for MkDocs successor; config stays `mkdocs.yml`):

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

- **[ADRs](content/adr/README.md)** — architecture decisions  
- **[Implementation plan](IMPLEMENTATION.md)** — build brief (already implemented)
- **[mkdocs.yml](mkdocs.yml)** — Zensical config (`docs_dir: content`)
- **[Taskfile.yml](Taskfile.yml)** — install / serve / build
