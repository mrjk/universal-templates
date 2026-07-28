# ADR 0004 — Backend tools via mise (wrap, don’t reinvent)

- **Status:** Accepted
- **Date:** 2026-07-28

## Context

Reimplementing project templating or file vendoring would duplicate mature tools and bloat this repo. Dev tooling is already managed with **mise**. Clients should be **thin UX + catalog glue** that shell out to upstream CLIs where possible.

## Decision

### Principle

**Wrap existing tools installed via mise.** Custom code only where no suitable tool covers the use case.

### `seed` → Copier

- **[Copier](https://copier.readthedocs.io/)** is the project engine: questions, Jinja, `.copier-answers.yml`, `copier update`, git template refs.
- Greenfield choice: **Copier only** (not Cookiecutter + cruft).
- `seed` responsibilities: default catalog URL/paths under `projects/`, hierarchy discovery/menu, invoke `copier copy` / `copier update`, surface pins/refs.
- Keep `copier` pinned in [`mise.toml`](../../mise.toml) `[tools]`.

### `snip` → wrap where possible; small custom core for regions

| Tool | Role | Fit |
|------|------|-----|
| [vendir](https://carvel.dev/vendir/) | Declarative sync of git paths into directories + lockfile | Prefer for **whole-file/dir** drops from `files/` when a vendored path + lock is enough |
| [fsrc](https://github.com/urmzd/fsrc) | Comment markers embed local file content into a host file | Candidate **region replace** engine after catalog fetch (spike later) |
| [path-sync](https://github.com/EspenAlbert/path-sync) | SRC→DEST sync with section markers and headers | Closest conceptual model for marked sections; oriented to multi-repo YAML workflows — evaluate in a spike |
| Docs embedders (embedoc, code-embedder, …) | Keep documentation in sync with code | **Out of scope** for `snip` |

Decisions:

1. **Whole-file/dir** sync → prefer **vendir** (or equivalent) via mise rather than reinventing sparse-checkout package logic.
2. **In-file region sync** (`snip sync <file>`) → no mature end-to-end CLI for interactive catalog + menu + pins. **Custom glue is justified** for parse, menu, diff/confirm, pin metadata, and fetch. Optional follow-up: drive region apply through fsrc/path-sync after fetch.
3. **Do not** use Copier for `snip` (wrong granularity).

```text
seed  -->  copier (mise)  -->  UT_CATALOG_REPO / projects/*
snip  -->  vendir (optional, mise)  -->  whole paths under files/*
snip  -->  region engine (custom and/or fsrc|path-sync)  -->  anchors in consumer files
```

### What stays custom (intentionally small)

- Catalog browse menus
- `UT_CATALOG_REPO` defaults
- Interactive “which portions?” for `snip sync`
- Diff/confirm policy wiring
- Pin/header helpers aligned with [ADR 0005](0005-snip-anchors-pins-and-update-ux.md)

### Relation to `bp`

Treat `bp` as a prototype for fetch/state ideas only. Long-term backends are Copier + (vendir and/or small snip core), not an expanded `bp`.

## Consequences

- mise.toml grows with tools we actually wrap (copier now; vendir/etc. when adopted).
- Spikes for fsrc/path-sync are expected before locking a region backend.
- Less Python/bash reimplementation of templating and vendoring; more subprocess orchestration.
