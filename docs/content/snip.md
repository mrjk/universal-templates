# Snip — files and regions

`snip` updates **files and marked regions** from `files/`. It wraps [vendir](https://carvel.dev/vendir/) for fetch/lock, plus thin glue for anchors and confirm. You normally run **`snip`**, not `vendir`.

Same habits as [`seed`](seed.md): `$UT_CATALOG_REPO`, list/browse, sync, pins, diff/confirm.

## When to use `snip`

- Shared helpers copy-pasted into many scripts (**inject**)
- Whole scripts shipped as customizable templates (**boilerplate**)
- Drop a catalog file into a project folder
- Interactive refresh: pick blocks → diff → confirm

Use [`seed`](seed.md) for a full new project tree.

### Two ownership modes

| Mode | Who owns the frame | Who owns the holes | Markers |
|------|--------------------|--------------------|---------|
| **Inject** | You | Catalog (`snip:id=`) | Regions filled from `files/` |
| **Boilerplate** | Catalog | You (`snip:slot=`) | Slots preserved on sync |

Do not mix `snip:id=` and `snip:slot=` in the same file.

## Commands

```bash
snip                          # numbered menu of files/ → add into cwd
snip list                     # catalog paths under files/
snip list <file>              # anchors / slots / header pins in a local file
snip add <catalog-path> [--dest DIR] [--ref REF] [-y]
snip sync                     # re-sync paths previously added (tracked)
snip sync <file> [--ref REF] [-y]   # update inject anchors or boilerplate slots
```

## Path 1 — add a whole file

```bash
snip add files/src/_fixture/snippet.sh --dest ./vendor -y
# → ./vendor/snippet.sh
```

Tracked units live under `.snip/` (`vendir.yml`, lock, `units.txt`). Happy path: you never edit those by hand.

```bash
snip sync -y                  # refresh tracked units after catalog changes
```

## Path 2 — anchors inside a script

Mark a region with begin/end comments:

```bash
#!/usr/bin/env bash
set -euo pipefail

# >>> snip:id=logging path=files/src/_fixture/snippet.sh ref=main
# (old body — will be replaced from catalog)
log() { echo old; }
# <<< snip:id=logging

main() { log "hi"; }
main "$@"
```

```bash
snip list ./myscript.sh
snip sync ./myscript.sh       # menu → diff → confirm per region
snip sync ./myscript.sh -y    # update all regions
```

### Anchor rules

```text
# >>> snip:id=NAME path=files/... ref=REF
...body...
# <<< snip:id=NAME
```

| Field | Meaning |
|-------|---------|
| `id` | Name of this region in your file (begin/end must match) |
| `path` | Catalog path under `files/` |
| `ref` | Pin (tag, branch, or sha); bumped on successful sync |

Comment style follows the host language (`#`, `//`, …). Grammar lives in `ut_cli/anchors.py`.

### Optional file header

Whole-file units carry **snip-managed** metadata comments (always prefixed with `snip:`). These are not part of the script logic; sync rewrites `ref=` / `version=` to the pin just applied.

```bash
#!/usr/bin/env bash
# snip: sync with: snip sync %FILE%
# snip: path=files/bin/example.sh ref=1.2.3
# snip: source=https://github.com/mrjk/universal-templates.git
# snip: version=1.2.3
```

| Line | Meaning |
|------|---------|
| `snip: sync with:` | Hint for humans / agents |
| `snip: path=` / `ref=` | Catalog unit + pin (required for boilerplate `snip sync <file>`) |
| `snip: source=` | Catalog git URL |
| `snip: version=` | Same pin as `ref=` (bumped on sync) |

Lines **without** a `snip:` prefix (e.g. `TEMPLATE_VERSION=…`, `APP_VERSION=…`) are yours — snip does not manage them.

Legacy `Template source:` / `curr_version:` headers are still read, but new templates should use the `snip:` form.

## Path 3 — boilerplate (catalog owns the frame)

Ship a full script from the catalog with named **slots** for user customizations. On sync, the frame is replaced from catalog; slot bodies are preserved.

Catalog template (`files/src/_fixture/boilerplate.sh` shape):

```bash
#!/usr/bin/env bash
# snip: sync with: snip sync %FILE%
# snip: path=files/src/_fixture/boilerplate.sh ref=main
# snip: source=https://github.com/mrjk/universal-templates.git
# snip: version=main
FRAME_MARKER=v1
# >>> snip:slot=main
# <<< snip:slot=main
echo done
```

Consumer after edit:

```bash
# … same header …
FRAME_MARKER=v1
# >>> snip:slot=main
echo custom-user
# <<< snip:slot=main
echo done
```

```bash
snip add files/src/_fixture/boilerplate.sh --dest . -y
# edit slot bodies
snip sync ./boilerplate.sh -y    # frame updates; slots kept
snip list ./boilerplate.sh       # shows slot:main
```

| Field | Meaning |
|-------|---------|
| `snip: path=` / `ref=` | Catalog unit + pin (required for `snip sync <file>`) |
| `snip: source=` / `version=` | Catalog URL + pin display (bumped on sync) |
| `snip:slot=NAME` | User-owned hole; begin/end must match |

Orphan slots (present locally but removed from catalog) are dropped with a warning.

## Policy

After you confirm:

- **Inject:** catalog wins inside `snip:id=` regions.
- **Boilerplate:** catalog wins the frame; **user wins** inside `snip:slot=` regions.

No silent clobber in interactive mode. `-y` is for CI and scripts.

## Catalog areas

| Area | Typical content |
|------|-----------------|
| `files/bin/` | Standalone scripts |
| `files/src/` | Embeddable fragments |
| `files/notes/` | Doc snippets, checklists |

What’s currently under `files/`: **[Inventory](inventory.md)**.

## Before / after

**Before:** ten scripts, ten slightly different `log()` helpers.  
**After:** one unit in `files/src/…`; each script uses the same anchors; `snip sync` keeps them on a pin.

## Under the hood (optional)

vendir pulls/locks bytes from `$UT_CATALOG_REPO`; glue applies them to destinations or anchor bodies. See [ADR 0004](adr/0004-backend-tools-via-mise.md) · [ADR 0005](adr/0005-snip-anchors-pins-and-update-ux.md).

## Related

[Tutorial](tutorial.md) · [Seed](seed.md) · [Catalog](catalog.md) · [Inventory](inventory.md)
