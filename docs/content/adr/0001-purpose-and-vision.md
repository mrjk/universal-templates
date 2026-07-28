# ADR 0001 — Purpose and vision

- **Status:** Accepted
- **Date:** 2026-07-28

## Context

This repository started as a handoff to build a “boilerplate manager” (`bp`) that mixed full-project scaffolding and piecemeal file injection in one CLI. That shape drifted from the real need: a **public git catalog** of reusable project skeletons and copy-pasted code fragments, with a simple way for the author and others to **bootstrap projects** and **refresh shared portions** in existing sources — including scripts scattered across machines — while keeping **version pins** visible.

Sibling folders under `misc_templates/` (e.g. full Python project templates) show the historical pattern: clone or copy a whole tree. The missing piece is ongoing sync of both whole projects and in-file regions, without standing up a package registry or a heavy application.

## Decision

**universal-templates** is a **git-hosted catalog** of personal (and shareable) boilerplate, plus **thin client tools** that consume that catalog (or any fork of it).

### Primary use cases

1. **Bootstrap a project** — e.g. a Python web app with good CI: pick a project template, answer questions, get a directory tree; later update from the same template at a pinned ref.
2. **Sync portions in existing files** — e.g. old shell scripts that share copy-pasted helpers: point a tool at a file, choose which marked portions to refresh from the catalog, confirm after a diff.

### Product principles

- **Two concerns, not one monolith** — project scaffolding vs file/portion sync (see [ADR 0002](0002-seed-and-snip-clis.md)).
- **Distribution = git** — no package registry, no custom server; any git host or local path works; anyone can host their own catalog (see [ADR 0003](0003-catalog-layout-and-self-hosting.md)).
- **Wrap Copier or vendir** — unified `seed`/`snip` UX; users do not drive upstream tools directly (see [ADR 0004](0004-backend-tools-via-mise.md)).
- **Pins for people** — consumers (including third parties) can see and keep track of which catalog version is deployed (see [ADR 0005](0005-snip-anchors-pins-and-update-ux.md)).
- **Stay a catalog repo** — clients may use lean Python glue; this must not become a heavy Python application (see [ADR 0006](0006-lean-implementation.md)).

### Non-goals (v1)

- Package registries, SaaS, or tarball APIs
- Three-way merge as the default update strategy
- Silent overwrite of local changes without confirm (except explicit non-interactive `-y` for CI)
- Replacing Copier or vendir with a home-grown sync/scaffold engine
- Exposing Copier/vendir as the primary user-facing interface
- Turning this repository into a Poetry/packaging-centric Python product

### Relation to current `bp`

`bin/bp` is a **transitional prototype**. Useful ideas (git fetch, install state, diff/confirm) may be reused. It is **not** the long-term user-facing product and should not gain features as if it were `seed`/`snip`.

## Consequences

- Product discussions and PRs are judged against these use cases and non-goals.
- High-level docs and CLI work follow ADRs 0002–0006.
- Catalog content (`projects/`, `files/`) matters more than CLI cleverness; empty stubs are debt relative to this vision.
