# universal-templates

A **git catalog** of project scaffolds and reusable snippets, plus two small CLIs:

| CLI | Job |
|-----|-----|
| **`seed`** | Create / update whole projects from `projects/` |
| **`snip`** | Add or refresh files and marked regions from `files/` |

No package registry. Point the tools at this repo, a fork, or a local path via `UT_CATALOG_REPO`.

## Learn it

Follow the guide (smooth path, real commands):

1. [Overview](docs/content/overview.md) — mental model  
2. [Tutorial](docs/content/tutorial.md) — hands-on `seed` + `snip`  
3. [Seed](docs/content/seed.md) · [Snip](docs/content/snip.md) · [Catalog](docs/content/catalog.md)

Index: [`docs/content/`](docs/content/index.md) · preview: `task docs:serve`

## Try in 60 seconds (this checkout)

```bash
git clone https://github.com/mrjk/universal-templates.git
cd universal-templates
mise trust && mise install          # once: python, copier, vendir, …
export UT_CATALOG_REPO="$PWD"

seed list
seed new projects/python-base /tmp/ut-demo-app -y

snip list
snip add files/src/_fixture/snippet.sh --dest /tmp/ut-demo-snip -y
```

With [mise](https://mise.jdx.dev/) activated here, `./bin` is on `PATH` so `seed` / `snip` just work.

## Install notes

- **In-repo:** mise supplies Python, Copier, vendir; shims live in `bin/`.  
- **No PyPI package** — run via the shims (or `PYTHONPATH=. python -m ut_cli.seed_cmd`).  
- Default catalog URL when `UT_CATALOG_REPO` is unset:  
  `https://github.com/mrjk/universal-templates.git`

## Layout

```text
projects/          # seed → Copier
  python-base/
files/             # snip → vendir + anchors
  src/
bin/seed  bin/snip
ut_cli/            # thin Python glue (stdlib-first)
docs/content/      # user guide (Zensical docs_dir)
docs/mkdocs.yml    # Zensical config
```

## Development

```bash
mise install
task lint    # shellcheck
task test    # python unittest
task ci
task docs:serve   # preview user guide (from docs/: task serve; once: task docs:install)

```

