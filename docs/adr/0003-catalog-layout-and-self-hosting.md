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

- **`projects/<name>/`** — Copier-oriented multi-file scaffolds (directory-oriented).
- **`files/{bin,src,notes}/…`** — file-oriented units (fragments and autonomous scripts). Subdirectories are allowed; menus must show hierarchy.

### Unit kinds

| Kind | Lives under | Role |
|------|-------------|------|
| **Project** | `projects/` | Full scaffold; Copier answers + update |
| **Fragment** | `files/` | Region and/or drop-in paths merged into consumer sources |
| **Autonomous** | `files/` (often `bin/`) | Standalone script/file with embed header and version pin |

Exact on-disk metadata filenames for file units (e.g. `part.yaml` vs successors) are an implementation detail; the **layout roots above are normative**.

### Self-hosting

- One environment variable is the catalog identity knob:

  **`UT_CATALOG_REPO`**

  Default / documented value: `https://github.com/mrjk/universal-templates.git`

- Set in this repo’s [`mise.toml`](../../mise.toml) `[env]` so local work picks it up easily; override to point at a fork, mirror, or local path.
- `seed` and `snip` must honor `UT_CATALOG_REPO` (with that URL as fallback when unset).
- **Hosting your own snippets** = publish a git repo with the same `projects/` + `files/` convention and point clients at it. No registry account required.

### Migration from current layout

| Current (legacy) | Target |
|------------------|--------|
| `templates/` | `projects/` |
| `parts/`, `common/` | `files/` (reorganized under `bin/`, `src/`, `notes/` as appropriate) |

Migration can be incremental; ADRs define the target, not the rename commit schedule.

## Consequences

- Browse/menu UX is hierarchy-first under `projects/` and `files/`.
- Forks and private catalogs stay first-class; documentation should show “set `UT_CATALOG_REPO=…`”.
- Default URL is easy to change in one place (`mise.toml` + ADR/docs), not hardcoded across many scripts without a single constant.
