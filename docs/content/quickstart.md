# Quickstart

Get oriented in a few minutes using the **main catalog**:

`https://github.com/mrjk/universal-templates.git`

Commands describe the **target** UX (`seed` / `snip`). See [Status](status.md) if binaries are not on PATH yet. Hosting your own catalog is optional and covered at the end.

## 1. Clone this repo

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

While you are in this directory, mise already sets the catalog to this project:

```bash
echo "$UT_CATALOG_REPO"
# https://github.com/mrjk/universal-templates.git
```

No extra config needed to consume **this** repo.

## 3. What’s in the main catalog

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

## 4. Seed a project (from this catalog)

```bash
mkdir -p ~/tmp/demo-app && cd ~/tmp/demo-app
seed
# pick projects/python-web → answer questions → done

seed sync          # later: pull template updates from the main catalog
```

Or without the menu:

```bash
seed new projects/python-web
```

You talk to **`seed`**, not to `copier` (the wrapper runs Copier against `$UT_CATALOG_REPO`).

## 5. Snip-sync an existing file (from this catalog)

Mark a shared region, then refresh it from the main catalog:

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

You talk to **`snip`**, not to `vendir` (the wrapper fetches/locks content from this catalog).

## 6. (Optional) Host your own catalog

When you want **your** snippets instead of (or in addition to) the main repo, point the same CLIs at another git URL or local path:

```bash
export UT_CATALOG_REPO="https://github.com/YOU/my-catalog.git"
# or: export UT_CATALOG_REPO="$HOME/prj/my-catalog"

seed
snip sync ./some_script.sh
```

Same commands, your content. Layout and authoring details: [Catalog & self-hosting](catalog.md).

## Next

- [Seed](seed.md) · [Snip](snip.md) · [Catalog](catalog.md) · [ADRs](../adr/README.md)
