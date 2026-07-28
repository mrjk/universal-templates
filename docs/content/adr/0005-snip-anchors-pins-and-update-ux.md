# ADR 0005 — Snip anchors, pins, and update UX

- **Status:** Accepted
- **Date:** 2026-07-28

## Context

Shared code is often copy-pasted into scripts that live outside any single project tree. Updates must target **marked regions** (or whole autonomous files), show what will change, and leave a **visible pin** so third parties know which catalog version is deployed. Silent clobber and mandatory three-way merges are the wrong defaults for this audience.

## Decision

### Pins

- **Pin = git ref** — prefer **tags** for releases; branch or sha allowed.
- Recorded in:
  - `seed` / Copier state (answers + template ref/sha) for projects
  - `snip` / vendir lock + **in-file metadata** for file units
- Catalog identity: `UT_CATALOG_REPO` ([ADR 0003](0003-catalog-layout-and-self-hosting.md)).
- Pins and sync verbs should feel the same whether the backend is Copier or vendir ([ADR 0004](0004-backend-tools-via-mise.md)).

### In-file region anchors (normative mechanism)

Portions in consumer files are delimited by **begin/end comment anchors** plus metadata (id, catalog path, ref/version). Exact grammar may be refined in a follow-up; the **mechanism** is accepted:

```bash
# >>> snip:id=logging-setup path=files/src/logging-setup ref=1.2.3
... shared logging code ...
# <<< snip:id=logging-setup
```

Comment style follows the host language (`#`, `//`, etc.); tools must tolerate common variants.

### Autonomous file header

Whole-file units may carry a header instead of (or in addition to) region anchors:

```bash
#!/usr/bin/env bash
# snip: sync with: snip sync %FILE%
# Template source: https://github.com/mrjk/universal-templates.git
# curr_version: 1.2.3
```

### `snip sync <file>` flow

1. Parse anchors and/or file header.
2. Resolve each portion against `UT_CATALOG_REPO` at the pinned ref (offer newer when appropriate).
3. Interactive menu: which portions to update.
4. Show **diff** → **confirm** → **catalog wins** for selected regions (or whole file).
5. Skip or remove paths when the user chooses erase/remove flows.

### Update UX (both `seed` and `snip`)

- Default: interactive **diff → confirm → catalog overwrites**.
- Non-interactive: `-y` (CI-friendly).
- **No silent clobber** in interactive mode.
- **No three-way merge as v1 default** for snip regions. Upstream tools may still surface their own conflict behavior; wrappers present a single confirm-oriented flow where we control it.

### Project updates (`seed sync`)

- Rely on Copier’s update path and recorded answers/ref, exposed as `seed sync`.
- File/catalog bytes for snips rely on vendir lock/sync, exposed as `snip sync` / `snip add`.
- Same product policy: user-visible change review before accepting where the wrapper controls the flow.

## Consequences

- Forgotten scripts become first-class sync targets without turning them into mini-projects.
- Public consumers can read headers/anchors to see source URL and version.
- Anchor grammar details and state directory names (e.g. `.snip`, `.seed`, `.ut`) remain open follow-ups but must not contradict catalog-wins + pin visibility.
