# ADR 0001 — Purpose and vision

- **Status:** Accepted
- **Date:** 2026-07-28
- **Updated:** 2026-07-28 — client tools moved to the snipseed project

## Context

This repository started as a handoff to build a “boilerplate manager” (`bp`) that mixed full-project scaffolding and piecemeal file injection in one CLI. That shape drifted from the real need: a **public git catalog** of reusable project skeletons and copy-pasted code fragments, with a simple way for the author and others to **bootstrap projects** and **refresh shared portions** in existing sources — including scripts scattered across machines — while keeping **version pins** visible.

Sibling folders under `misc_templates/` (e.g. full Python project templates) show the historical pattern: clone or copy a whole tree. The missing piece is ongoing sync of both whole projects and in-file regions, without standing up a package registry or a heavy application.

## Decision

**universal-templates** is a **git-hosted catalog** of personal (and shareable) boilerplate under `projects/` and `files/`. Thin client tools that consume this catalog (or any fork) live in a separate project: [**snipseed**](https://github.com/mrjk/snipseed) (`seed` / `snip`).

### Primary use cases

1. **Bootstrap a project** — pick a template under `projects/`, answer questions, get a directory tree; later update from the same template at a pinned ref.
2. **Sync portions in existing files** — refresh marked regions or whole files from `files/`, with visible pins and confirm-after-diff.

### Product principles

- **Catalog first** — this repo’s job is content + layout contract, not a packaging-centric Python product.
- **Distribution = git** — no package registry, no custom server; any git host or local path works; anyone can host their own catalog (see [ADR 0003](0003-catalog-layout-and-self-hosting.md)).
- **Two consumer CLIs** — project scaffolding vs file/portion sync (`seed` / `snip`); decisions and implementation: snipseed ADRs 0002, 0004–0006.
- **Pins for people** — consumers can see which catalog version was applied.

### Non-goals (v1)

- Package registries, SaaS, or tarball APIs
- Three-way merge as the default update strategy
- Silent overwrite of local changes without confirm (except explicit non-interactive `-y` for CI)
- Replacing Copier or vendir with a home-grown sync/scaffold engine
- Exposing Copier/vendir as the primary user-facing interface
- Turning **this** repository into a Poetry/packaging-centric Python product

### Relation to former `bp`

`bin/bp` was a transitional bash prototype. It has been **removed**. User-facing CLIs are `seed` / `snip` in snipseed.

## Consequences

- Catalog PRs are judged on content usefulness and layout compatibility.
- CLI / UX / implementation changes happen in snipseed; this repo keeps ADR 0001 + 0003.
- Empty stubs under `projects/` / `files/` are debt relative to this vision.
