# ADR 0004 — Wrap Copier or vendir; unified UX

- **Status:** Accepted
- **Date:** 2026-07-28
- **Supersedes:** earlier draft that left snip’s backend optional and listed fsrc/path-sync as candidates

## Context

Project scaffolding and file sync need different engines, but users should not learn two upstream products. Reimplementing either engine would bloat this repo. **mise** already pins tooling.

## Decision

### Backends (only these two)

| Concern | CLI | Upstream (via mise) | Catalog |
|---------|-----|---------------------|---------|
| Whole-project scaffold / update | `seed` | **[Copier](https://copier.readthedocs.io/)** | `projects/` |
| File / fragment sync | `snip` | **[vendir](https://carvel.dev/vendir/)** | `files/` |

- Do **not** invent a third sync engine or adopt fsrc/path-sync as product backends.
- Do **not** use Copier for `files/` or vendir for full project Q&A scaffolds.
- Greenfield projects: **Copier only** (not Cookiecutter + cruft).

### Unified user experience

`seed` and `snip` present **one product language**. Users talk to our CLIs, not to Copier or vendir day-to-day.

Shared UX across both:

- Same catalog knob: `UT_CATALOG_REPO`
- Hierarchy browse / menus over the catalog
- Verbs in the same family: discover → add/new → **sync** → list pins
- Update policy: **diff → confirm → catalog wins** (plus `-y` for CI)
- Visible **pins** (git tag/ref) for what is deployed

Wrappers own:

- Mapping catalog paths → Copier template vs vendir content
- Generating/maintaining whatever config the upstream tool needs (e.g. answers file, `vendir.yml` / lock) so users are not hand-editing upstream config for common flows
- Interactive confirm and messaging in our terms (`seed sync`, `snip sync`)

```text
        ┌─────────────────────────────────────┐
        │  Unified UX (seed / snip)           │
        │  menus · pins · diff/confirm · URL  │
        └──────────────┬──────────────────────┘
               ┌───────┴───────┐
               ▼               ▼
           Copier           vendir
          (mise)            (mise)
               │               │
               ▼               ▼
          projects/*        files/*
```

### What glue may still do (thin)

- Menus, `UT_CATALOG_REPO` defaults, pin/header helpers
- For **in-file regions** ([ADR 0005](0005-snip-anchors-pins-and-update-ux.md)): parse anchors, let the user pick portions, show diff/confirm, then apply content that was **fetched via the vendir-backed catalog path** (or an equivalent fetch already owned by the snip→vendir integration). Region apply is glue; **fetch/lock of catalog bytes is vendir’s job**, not a parallel package manager.

### Relation to `bp`

`bp` is a prototype. Long-term = unified `seed`/`snip` wrapping **Copier or vendir** only.

## Consequences

- Pin `copier` and `vendir` in mise when implementing snip.
- Docs teach `seed`/`snip` first; Copier/vendir are implementation footnotes.
- PRs that add another sync backend need an ADR change.
- Custom code stays UX + orchestration, not a second Copier or vendir.
