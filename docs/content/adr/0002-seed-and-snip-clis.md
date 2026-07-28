# ADR 0002 — Two CLIs: `seed` and `snip`

- **Status:** Accepted
- **Date:** 2026-07-28

## Context

Project scaffolding (many files, questions, long-lived update) and file/portion sync (anchors in an existing script, interactive region update) are different jobs. One CLI (`bp`) blurred them and produced confusing UX (e.g. asking for a catalog URL when the user expected “update my script”).

Names must be short, easy to type, and match everyday language.

## Decision

Ship **two commands** with separate concerns and catalog roots:

| CLI | Concern | Catalog root | Orientation |
|-----|---------|--------------|-------------|
| **`seed`** | Whole-project boilerplate | `projects/` | Directory / many files |
| **`snip`** | Portions and file units in existing sources | `files/` | File / region (and whole-file units) |

### `seed` (project-oriented)

Typical flow:

```bash
seed                          # menu: pick under projects/, answer questions, generate
seed new projects/python-web  # direct path when known
seed sync                     # update an already-seeded project from its pinned template
```

Backend: **Copier** via mise, behind a unified UX (see [ADR 0004](0004-backend-tools-via-mise.md)).

### `snip` (file-oriented)

Typical flow:

```bash
snip sync ./my_forgotten_old_script.sh   # scan anchors → menu → diff → apply
snip list ./my_forgotten_old_script.sh   # show detected portions / pins
snip add files/src/logging-setup         # inject / attach a unit (details in later design)
```

Backend: **vendir** via mise for catalog fetch/lock of `files/*`, plus thin glue for anchors/menus (see [ADR 0004](0004-backend-tools-via-mise.md), [ADR 0005](0005-snip-anchors-pins-and-update-ux.md)).

### Unified UX + coupling

- Hierarchies and CLIs stay **separate**; **experience** stays aligned (same catalog URL, sync/list/menu language, diff/confirm, pins).
- Users should not need to learn Copier or vendir to do everyday work.
- `seed` **may invoke** `snip` when a project template declares optional file units.
- Shared config: catalog URL / defaults (see [ADR 0003](0003-catalog-layout-and-self-hosting.md)).

### Naming rationale

- Avoid long `ut-*` prefixes and the overloaded `bp` name.
- `seed` / `snip` are four letters, metaphor-clear (“seed a project”, “snip that shared bit”).

### Transition

- `bp` is **removed**; `seed` / `snip` replaced it.
- Do not reintroduce a kitchen-sink CLI under the `bp` name.

## Consequences

- Install / PATH story exposes two binaries (or two entry points), not one kitchen-sink CLI.
- Menus and docs are split by concern; users are not forced through the wrong mental model.
- Implementation and tests can evolve independently per CLI.
