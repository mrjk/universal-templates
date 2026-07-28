# Snip — files and regions

`snip` updates **files and marked regions** from `files/`. It wraps [vendir](https://carvel.dev/vendir/) for fetch/lock, plus thin glue for anchors and confirm. You normally run **`snip`**, not `vendir`.

Same habits as [`seed`](seed.md): `$UT_CATALOG_REPO`, list/browse, sync, pins, diff/confirm.

## When to use `snip`

- Shared helpers copy-pasted into many scripts  
- Drop a catalog file into a project folder  
- Interactive refresh: pick blocks → diff → confirm  

Use [`seed`](seed.md) for a full new project tree.

## Commands

```bash
snip                          # numbered menu of files/ → add into cwd
snip list                     # catalog paths under files/
snip list <file>              # anchors / header pins in a local file
snip add <catalog-path> [--dest DIR] [--ref REF] [-y]
snip sync                     # re-sync paths previously added (tracked)
snip sync <file> [--ref REF] [-y]   # update anchors in that file
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

Whole-file units may advertise source + version:

```bash
#!/usr/bin/env bash
# snip: sync with: snip sync %FILE%
# Template source: https://github.com/mrjk/universal-templates.git
# curr_version: 1.2.3
```

## Policy

After you confirm, **catalog wins** for that file or region. No silent clobber in interactive mode. `-y` is for CI and scripts.

## Catalog areas

| Area | Typical content |
|------|-----------------|
| `files/bin/` | Standalone scripts |
| `files/src/` | Embeddable fragments |
| `files/notes/` | Doc snippets, checklists |

Today this repo ships a learning fixture under `files/src/_fixture/`. Real shared units grow here the same way.

## Before / after

**Before:** ten scripts, ten slightly different `log()` helpers.  
**After:** one unit in `files/src/…`; each script uses the same anchors; `snip sync` keeps them on a pin.

## Under the hood (optional)

vendir pulls/locks bytes from `$UT_CATALOG_REPO`; glue applies them to destinations or anchor bodies. See [ADR 0004](adr/0004-backend-tools-via-mise.md) · [ADR 0005](adr/0005-snip-anchors-pins-and-update-ux.md).

## Related

[Tutorial](tutorial.md) · [Seed](seed.md) · [Catalog](catalog.md)
