# Quickstart

Cheat sheet after you’ve done the [Tutorial](tutorial.md) once.

## Install (this repo)

```bash
git clone https://github.com/mrjk/universal-templates.git
cd universal-templates
mise trust && mise install
export UT_CATALOG_REPO="$PWD"   # learn against local checkout
```

`seed` and `snip` come from `./bin` via mise `PATH`.

## Everyday commands

```bash
seed list
seed new projects/python-base ./my-app
seed new projects/python-base ./my-app -y    # defaults, no prompts
seed sync                                   # in a generated project
seed                                        # numbered browse → new

snip list
snip list ./script.sh                       # anchors in a file
snip add files/src/_fixture/snippet.sh --dest .
snip sync ./script.sh                       # regions → menu → diff → apply
snip sync ./script.sh -y
snip                                        # numbered browse → add
```

## Catalog knob

```bash
# default when unset:
# https://github.com/mrjk/universal-templates.git

export UT_CATALOG_REPO="https://github.com/YOU/my-catalog.git"
export UT_CATALOG_REPO="$HOME/prj/my-catalog"   # local path also works
```

## Policy

Updates show a **diff**, ask for confirm, then **catalog overwrites** the selected content. Use `-y` only when you mean it (CI, scripts).

## Next

[Seed](seed.md) · [Snip](snip.md) · [Catalog](catalog.md)
