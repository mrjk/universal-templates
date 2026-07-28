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
# snip: path=files/bin/example.sh ref=1.2.3
# snip: source=https://github.com/mrjk/universal-templates.git
# snip: version=1.2.3
```

All snip-managed file metadata uses the `snip:` comment prefix. `path` / `ref` are required for **boilerplate** whole-file sync so the consumer file is self-describing without `.snip/` state. `version` mirrors `ref` and is bumped on sync.

### Two ownership modes (same CLI)

| Mode | Markers | Ownership |
|------|---------|-----------|
| **Inject** | `snip:id=` | User owns frame; catalog fills regions |
| **Boilerplate** | `snip:slot=` + header `path`/`ref` | Catalog owns frame; user fills slots |

- Stay in **`snip`** (no third CLI); vendir remains fetch/lock only; merge is glue.
- A file must not mix `snip:id=` and `snip:slot=` (v1).
- Boilerplate sync: fetch catalog template → merge consumer slot bodies by name → diff → confirm → write; bump header pin. Orphan local slots warn and drop.
- Tracked `snip sync` / re-`add` must merge when the destination already has slots (never blind overwrite of user holes).
- Region-level “envelope” blocks inside a user-owned file are out of scope for v1.

### `snip sync <file>` flow

1. Parse inject anchors, slots, and/or file header; reject mixed modes.
2. **Inject:** resolve each selected region against `UT_CATALOG_REPO` at the pinned ref; menu → diff → confirm → catalog wins inside regions.
3. **Boilerplate:** resolve header `path` @ `ref`; merge slots into fresh catalog bytes; diff → confirm → catalog wins frame, user wins slots.
4. Skip or remove paths when the user chooses erase/remove flows.

### Update UX (both `seed` and `snip`)

- Default: interactive **diff → confirm → apply**.
- Non-interactive: `-y` (CI-friendly).
- **No silent clobber** in interactive mode.
- **No three-way merge as v1 default.** Inject: catalog wins selected regions. Boilerplate: catalog wins frame; slots are user-preserved by name (not a textual 3-way merge).

### Project updates (`seed sync`)

- Rely on Copier’s update path and recorded answers/ref, exposed as `seed sync`.
- File/catalog bytes for snips rely on vendir lock/sync, exposed as `snip sync` / `snip add`.
- Same product policy: user-visible change review before accepting where the wrapper controls the flow.

## Consequences

- Forgotten scripts become first-class sync targets without turning them into mini-projects.
- Public consumers can read headers/anchors to see source URL and version.
- Anchor grammar details and state directory names (e.g. `.snip`, `.seed`, `.ut`) remain open follow-ups but must not contradict catalog-wins + pin visibility.
