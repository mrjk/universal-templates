# Snip — files and regions

`snip` updates **portions of existing source** (or whole autonomous files) from `files/`. It wraps [vendir](https://carvel.dev/vendir/) for **fetch/lock of catalog content**, and adds thin glue for anchors, menus, and confirm — same product language as [`seed`](seed.md).

You normally run **`snip`**, not `vendir`.

## When to use `snip`

- Shared helpers copy-pasted into many scripts  
- Standalone gist-like scripts with source + version headers  
- Interactive refresh: pick blocks → diff → confirm  

Use [`seed`](seed.md) for a full new project tree.

## Commands (target)

```bash
snip sync <file>              # anchors → menu → diff → apply
snip list <file>              # portions / pins
snip add <catalog-path> …     # attach / inject a unit
```

## Anchors (regions)

```bash
#!/usr/bin/env bash
set -euo pipefail

# >>> snip:id=logging-setup path=files/src/logging-setup ref=1.2.3
log() {
  echo "[$(date -Iseconds)] $*"
}
die() { log "error: $*"; exit 1; }
# <<< snip:id=logging-setup

# >>> snip:id=argparse-style path=files/src/argparse-style ref=main
# … shared argv parsing …
# <<< snip:id=argparse-style

main() { :; }
main "$@"
```

```bash
snip sync ./deploy.sh
```

Illustrative session:

```text
Portions in deploy.sh
  [x] logging-setup   files/src/logging-setup   ref=1.2.3  (newer: 1.3.0)
  [ ] argparse-style  files/src/argparse-style  ref=main
Apply selected? → show diff → confirm
updated logging-setup → ref=1.3.0
```

**Policy:** after confirm, **catalog wins** for that region (`-y` only for non-interactive/CI).

## Autonomous file header

```bash
#!/usr/bin/env bash
# snip: sync with: snip sync %FILE%
# Template source: https://github.com/mrjk/universal-templates.git
# curr_version: 1.2.3
```

```bash
snip sync ./something.sh
```

## Catalog paths

| Area | Typical content |
|------|-----------------|
| `files/bin/` | Standalone scripts |
| `files/src/` | Embeddable fragments |
| `files/notes/` | Doc snippets, checklists |

## Under the hood (footnote)

- **vendir** pulls and locks bytes from `$UT_CATALOG_REPO` under `files/…`  
- Glue applies those bytes into whole files or **anchor regions**, and owns the interactive UX  
- No second package manager; no fsrc/path-sync as product backends ([ADR 0004](../adr/0004-backend-tools-via-mise.md))

## Before / after

**Before:** ten scripts, ten slightly different `log()` helpers.  
**After:** canonical unit in `files/src/logging-setup`; each script uses the same anchors; `snip sync` keeps them on a pin.

## Related

- [ADR 0004](../adr/0004-backend-tools-via-mise.md) · [ADR 0005](../adr/0005-snip-anchors-pins-and-update-ux.md)
