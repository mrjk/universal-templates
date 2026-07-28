# Quickstart

Get oriented in a few minutes. Commands describe the **target** UX (`seed` / `snip`). See [Status](status.md) if binaries are not on PATH yet.

## 1. Clone the catalog

```bash
git clone https://github.com/mrjk/universal-templates.git
cd universal-templates
```

## 2. Enable tools (mise)

With [mise](https://mise.jdx.dev/) activated:

```bash
mise trust    # once per machine, if prompted
mise install  # python, copier, … (+ vendir when snip lands)
```

Default catalog URL (override to self-host):

```bash
echo "$UT_CATALOG_REPO"
# https://github.com/mrjk/universal-templates.git

export UT_CATALOG_REPO="https://github.com/YOU/my-snippets.git"
# or a local path:
export UT_CATALOG_REPO="$HOME/prj/my-snippets"
```

## 3. Catalog layout

```text
projects/          # seed → Copier
  python-base/
  python-web/
  …
files/             # snip → vendir (+ anchors glue)
  bin/
  src/
  notes/
```

## 4. Seed a project

```bash
mkdir -p ~/tmp/demo-app && cd ~/tmp/demo-app
seed
# pick projects/python-web → answer questions → done

seed sync          # later: pull template updates (same confirm-oriented UX)
```

Direct path:

```bash
seed new projects/python-web
```

You talk to **`seed`**, not to `copier` (the wrapper runs Copier for you).

## 5. Snip-sync an existing file

```bash
#!/usr/bin/env bash
set -euo pipefail

# >>> snip:id=logging-setup path=files/src/logging-setup ref=main
log() { echo "[log] $*"; }
# <<< snip:id=logging-setup

main() { log "hello"; }
main "$@"
```

```bash
snip sync ./my_forgotten_old_script.sh
# menu → diff → confirm (catalog wins)
snip list ./my_forgotten_old_script.sh
```

You talk to **`snip`**, not to `vendir` (the wrapper uses vendir to fetch/lock catalog content).

## 6. Host your own snippets

```bash
export UT_CATALOG_REPO="https://github.com/YOU/my-catalog.git"
seed
snip sync ./some_script.sh
```

Same commands, your git repo. Details: [Catalog](catalog.md).

## Next

- [Seed](seed.md) · [Snip](snip.md) · [Catalog](catalog.md) · [ADRs](../adr/README.md)
