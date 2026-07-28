# universal-templates

Git-distributed catalog of project scaffolds and file snippets. Everyday UX is two thin CLIs:

| CLI | Job | Backend |
|-----|-----|---------|
| **`seed`** | Whole-project scaffolds from `projects/` | [Copier](https://copier.readthedocs.io/) |
| **`snip`** | Files / in-file regions from `files/` | [vendir](https://carvel.dev/vendir/) |

Docs: [`docs/content/`](docs/content/README.md) (start with [overview](docs/content/overview.md) and [quickstart](docs/content/quickstart.md)). Architecture: [`docs/adr/`](docs/adr/README.md).

Default catalog: `UT_CATALOG_REPO` → `https://github.com/mrjk/universal-templates.git` (override for forks / local paths).

## Quickstart (this repo + mise)

```bash
mise trust          # once per machine, if prompted
mise install        # python, copier, vendir, jq, shellcheck, bats
seed --help         # ./bin on PATH via mise.toml
snip --help
```

```bash
export UT_CATALOG_REPO="$PWD"   # use this checkout as catalog
seed new projects/python-base ./my-app -y
snip add files/src/_fixture/snippet.sh --dest /tmp/snip-demo -y
snip sync ./some_script_with_anchors.sh
```

## Install notes

- In-repo: activate [mise](https://mise.jdx.dev/); `bin/seed` and `bin/snip` are on `PATH`.
- No public PyPI package — glue lives in `ut_cli/` and is run via the shims.
- Upstream tools (`copier`, `vendir`) must be on `PATH` (mise pins them here).

## Catalog layout (target)

```text
projects/          # seed → Copier
  python-base/
  _fixture/        # test fixture
files/             # snip → vendir + anchors
  src/
  bin/
  notes/
```

Legacy `templates/`, `parts/`, and `common/` remain for the transitional `bp` CLI.

## Development

```bash
mise install
task lint      # shellcheck
task test      # bats + python unittest
task ci
```

## Deprecated: `bp`

`bin/bp` is a **deprecated** prototype (bash + sparse-checkout + jq). Prefer `seed` / `snip`. Do not expand `bp`'s public API; `./install.sh` still installs `bp` only for older workflows.
