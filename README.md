# Boilerplate Manager (`bp`)

Personal code boilerplate for Python, shell, and more — distributed via a portable bash CLI and plain git (sparse-checkout). No package registry, no server.

Two modes:

1. **New project scaffolding** — full templates via [Copier](https://copier.readthedocs.io/).
2. **Piecemeal parts** — small composable fragments (tests, Makefile, CI, `.gitignore`) injected into an *existing* project.

## Quickstart

### In this repo ([mise](https://mise.jdx.dev/))

With [mise](https://mise.jdx.dev/) activated in your shell (`eval "$(mise activate bash)"` or equivalent), clone and enter the repo:

```bash
mise trust          # once per machine, if prompted
mise install        # pinned jq, shellcheck, bats, python, copier
bp --help           # ./bin is on PATH via mise.toml [env]._.path
```

Dev tooling and `bin/bp` are then available automatically while you are in this directory.

### Install `bp` onto PATH (any project)

From a clone:

```bash
./install.sh
bp --help
```

Or from a remote git URL (no local clone required):

```bash
BP_INSTALL_REPO=https://github.com/YOU/universal-templates bash -c "$(curl -fsSL https://raw.githubusercontent.com/YOU/universal-templates/main/install.sh)"
```

This copies `bin/bp` to `~/.local/bin/bp` so you can run `bp` outside this repo.

Requirements for the core CLI: **git** (≥ 2.25) and **jq**. Copier is only needed for `bp new` (provided by mise in this repo).

Optional interactive menu:

```bash
pip install -r cli/requirements.txt
bp menu
```

## Commands

| Command | Behavior |
|---|---|
| `bp add <repo> <part-path> [@ref]` | Sparse-clone the part, copy `files/` into the **project root** (preserving paths), write `.bp/<name>.json`, run `post_add` if set |
| `bp update <name>` | Re-fetch, show diff, confirm, overwrite tracked files, refresh `sha` |
| `bp update --all` | Update every installed part |
| `bp remove <name>` | Run `post_remove` if set, delete tracked files, delete state |
| `bp list` | Print installed parts as a tree (name / ref / sha) |
| `bp browse <repo> [@ref]` | List `parts/`, `common/`, and `templates/` without installing |
| `bp new <repo> <template-path> [@ref]` | Shell out to Copier (`pipx install copier`) |
| `bp menu` | Python checkbox UI if deps present; otherwise a bash numbered menu |

Flags: `-y` / `--yes` for non-interactive confirm (CI-friendly).

Example:

```bash
mkdir /tmp/scratch && cd /tmp/scratch
bp add /path/to/universal-templates parts/python/pytest
# → pytest.ini, tests/test_example.py at project root
# → .bp/pytest.json
bp list
bp update pytest
bp remove pytest
```

## How parts install (project-root merge)

Each part is a directory with `part.yaml` + `files/`:

```
parts/python/pytest/
├── part.yaml
└── files/
    ├── pytest.ini
    └── tests/test_example.py
```

`bp add` copies `files/` into your project root, so you get `./pytest.ini` and `./tests/test_example.py` — not a nested `./pytest/` folder.

State lives in the **consuming** project:

```json
{
  "name": "pytest",
  "repo": "...",
  "path": "parts/python/pytest",
  "ref": "main",
  "sha": "a1b2c3d4...",
  "installed_at": "2026-07-28T12:00:00Z",
  "installed_files": ["pytest.ini", "tests/test_example.py"]
}
```

`bp update` / `bp remove` use `installed_files` so only those paths are touched.

### `part.yaml` schema

```yaml
name: pytest
description: "pytest + basic test scaffold"
language: python
files_dir: files
post_add: null      # optional shell command, run from project root
post_remove: null
```

Part directory names must be unique across `parts/` and `common/` (enforced in CI).

## Templates (Copier)

Full project skeletons live under `templates/`:

```bash
# via bp (requires copier on PATH)
bp new /path/to/universal-templates templates/python

# or directly
copier copy /path/to/universal-templates/templates/python ./my-app
```

Both `templates/python` and `templates/shell` prompt for `project_slug` and `description`. Later: `copier update` in the generated project.

## Adding a new part

1. Create `parts/<lang>/<name>/part.yaml` and `files/` (or `common/<name>/` for cross-language).
2. Put payload files under `files/` using the paths you want at the consumer project root.
3. Ensure `name` in `part.yaml` matches the directory name and is unique.
4. Commit. Consumers can `bp add <this-repo> parts/<lang>/<name>`.

## Adding a new template

1. Create `templates/<name>/copier.yml` with questions.
2. Put Jinja templates under `templates/<name>/template/` (this repo uses `_subdirectory: template`).
3. Consumers run `bp new <this-repo> templates/<name>` or `copier copy …`.

## Layout

```
bin/bp                 # core CLI (bash + git + jq)
cli/bp_menu.py         # optional interactive layer
install.sh             # optional: install bp to ~/.local/bin
mise.toml / mise.lock  # pinned tools + ./bin on PATH in this repo
Taskfile.yml           # lint / test / ci (go-task)
templates/             # Copier full-project scaffolds
parts/<lang>/<name>/   # composable parts
common/<name>/         # cross-language parts
tests/bp.bats
```

## Development

[mise](https://mise.jdx.dev/) manages tools and PATH in this repo; [Task](https://taskfile.dev/) runs project commands.

```bash
mise trust
mise install
task lint    # shellcheck bin/bp install.sh
task test    # bats tests/bp.bats
task ci      # lint + test
```

Without mise, use system `bats` / `shellcheck` / `jq` / `task` the same way CI does:

```bash
task ci
# or:
bats tests/bp.bats
shellcheck bin/bp install.sh
```
