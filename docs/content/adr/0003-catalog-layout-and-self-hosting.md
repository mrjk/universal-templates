# ADR 0003 — Catalog layout and self-hosting

- **Status:** Accepted
- **Date:** 2026-07-28

## Context

Boilerplate must be browsable with a clear hierarchy (language/kind and subdirs). Consumers and forks must be able to **host their own** catalog without forking the CLI design — only the git remote (and optional ref) should change.

Default public remote for this project:

`https://github.com/mrjk/universal-templates.git`

## Decision

### Target tree

```text
projects/                 # consumed by seed
  python-base/
  python-web/
  shell-bats/
  shell-home/
  …                       # further names / nested groups allowed
files/                    # consumed by snip
  bin/                    # autonomous / installable scripts
  src/                    # drop-in or embeddable fragments
  notes/                  # docs snippets, checklists, etc.
  …                       # further nesting allowed under each
```

- **`projects/<name>/`** — Copier scaffolds (consumed via `seed` UX).
- **`files/{bin,src,notes}/…`** — file units (consumed via `snip` UX → vendir + anchors). Subdirectories allowed; menus must show hierarchy.

### Unit kinds

| Kind | Lives under | Role |
|------|-------------|------|
| **Project** | `projects/` | Full scaffold; Copier behind `seed` |
| **Fragment** | `files/` | Region and/or drop-in paths; vendir behind `snip` |
| **Autonomous** | `files/` (often `bin/`) | Standalone script/file with embed header and version pin |

Exact on-disk metadata filenames for file units (e.g. `part.yaml` vs successors) are an implementation detail; the **layout roots above are normative**.

### Self-hosting

- One environment variable is the catalog identity knob:

  **`UT_CATALOG_REPO`**

  Default / documented value: `https://github.com/mrjk/universal-templates.git`

- Set in this repo’s [`mise.toml`](../../../mise.toml) `[env]` so local work picks it up easily; override to point at a fork, mirror, or local path.
- `seed` and `snip` must honor `UT_CATALOG_REPO` (with that URL as fallback when unset).
- **Hosting your own snippets** = publish a git repo with the same `projects/` + `files/` convention and point clients at it. No registry account required.

### Migration from former layout

| Former (removed) | Current |
|------------------|---------|
| `templates/` | `projects/` |
| `parts/`, `common/` | `files/` (under `bin/`, `src/`, `notes/` as appropriate) |

Legacy trees and the `bp` CLI are gone; catalog content lives only under `projects/` and `files/`.

## Consequences

- Browse/menu UX is hierarchy-first under `projects/` and `files/`.
- Forks and private catalogs stay first-class; documentation should show “set `UT_CATALOG_REPO=…`”.
- Default URL is easy to change in one place (`mise.toml` + ADR/docs), not hardcoded across many scripts without a single constant.
