# Implementation plan — `seed` / `snip` (handoff)

Give this document to a coding agent as the build brief. Product intent is locked in [`docs/adr/`](adr/README.md) and [`docs/content/`](content/README.md). **Do not redesign** those decisions; implement them.

## Goal

Ship two thin Python CLIs with a **unified UX**:

| CLI | Backend (mise) | Catalog |
|-----|----------------|---------|
| `seed` | Copier | `projects/` |
| `snip` | vendir | `files/` |

Users talk to `seed` / `snip` only. Default catalog: `UT_CATALOG_REPO` → `https://github.com/mrjk/universal-templates.git`.

## Hard constraints

1. **Python** for CLIs and shared libs. Stdlib-first. Light deps only if clearly needed (e.g. one tiny prompt helper). **No** Poetry app, **no** heavy frameworks (Click mega-stack, Rich ecosystems, HTTP clients, extra templating).
2. **Wrap** Copier and vendir via `subprocess` — do not reimplement them.
3. **No third sync engine** (no fsrc/path-sync/custom package manager).
4. Keep modules **compact and small** — prefer many small files over large god-modules.
5. Shared code in a small common package; do not duplicate catalog/diff/confirm logic.
6. Do **not** extend `bin/bp` as the product. Leave it; new entrypoints are `seed` / `snip`.
7. Do **not** mass-migrate catalog trees in the first PR unless needed for a smoke test; can work against local paths and stub `projects/` / `files/` fixtures in tests.
8. Follow existing repo style: functions preferred, Taskfile for lint/test (not mise tasks).

## Suggested layout (keep small)

```text
bin/
  seed                 # shebang → python -m ut_cli.seed
  snip                 # shebang → python -m ut_cli.snip
cli/                   # optional: keep empty or delete old bp_menu later
ut_cli/                # package (name can be `ut_cli` — short)
  __init__.py
  __main__.py          # optional dispatcher
  catalog.py           # resolve UT_CATALOG_REPO, list hierarchy
  config.py            # defaults, -y, ref parsing
  confirm.py           # diff + y/N / --yes
  diffutil.py          # unified diff helpers (stdlib difflib)
  proc.py              # run copier/vendir/git, capture errors
  seed_cmd.py          # seed CLI argparse + commands
  snip_cmd.py          # snip CLI argparse + commands
  anchors.py           # parse/apply snip region markers
  vendir_wrap.py       # generate minimal vendir.yml, sync, read lock
  copier_wrap.py       # invoke copier copy/update
tests/
  test_anchors.py
  test_catalog.py
  test_seed_smoke.py   # mock subprocess where possible
  test_snip_smoke.py
```

Entry scripts in `bin/` must be on PATH via existing `mise.toml` `[env]._.path`.

Optional light dep (only if stdlib prompts feel too painful): **one** of `questionary` *or* plain numbered menus in stdlib — prefer stdlib numbered menus for v1 to avoid deps.

## Shared UX (both CLIs)

Implement once in common modules:

- Read `UT_CATALOG_REPO` (fallback URL above).
- Flags: `-y` / `--yes`, optional `@ref` / `--ref`.
- `list` / browse hierarchy under `projects/` or `files/`.
- Update flow: show diff → confirm → apply (**catalog wins**).
- Clear errors if `copier` / `vendir` missing from PATH.

## Phase 0 — Tooling

1. Add **vendir** to [`mise.toml`](../mise.toml) `[tools]` (pin a current stable); run `mise install`.
2. Ensure `python` + `copier` already present.
3. Add minimal `ut_cli` package; wire `bin/seed` and `bin/snip` shims.
4. Add `task` targets or pytest for unit tests (keep CI green; can extend Taskfile). Prefer **pytest** std with mise python — or unittest if you want zero pip deps. Prefer unittest/stdlib to stay dep-free unless pytest already wanted.

## Phase 1 — `seed` MVP

Commands:

```text
seed --help
seed new <project-path> [--ref REF] [-y]
seed sync [--ref REF] [-y]
seed list          # list projects/ in catalog (git ls-tree or local walk)
```

Behavior:

1. `seed new projects/python-web`  
   - Resolve catalog (local path or remote).  
   - If remote: shallow clone/sparse or let Copier fetch VCS URL (Copier supports git templates — prefer **Copier’s native git source** when `UT_CATALOG_REPO` is a URL: e.g. template `gh:…` / git URL + path subdirectory as Copier allows).  
   - `subprocess` → `copier copy <src> <dst>` with cwd/dst = user target.  
2. `seed sync`  
   - Detect `.copier-answers.yml` in cwd (or ask).  
   - `copier update` with confirm policy wrapped (`-y` → non-interactive flags Copier supports).  
3. Interactive menu (optional in same phase or Phase 1b): numbered list of `projects/*`.

Acceptance:

- From a temp dir, `seed new` against a **local** clone path works with an existing template under legacy `templates/python` **or** a tiny fixture `projects/_fixture/` you add for tests.
- `seed sync` calls Copier update on a generated project (smoke).
- No Copier logic reimplemented in Python.

## Phase 2 — `snip` MVP (whole file / path)

Commands:

```text
snip --help
snip add <files/...> [--dest DIR] [--ref REF] [-y]
snip sync [--ref REF] [-y]          # sync vendored paths already tracked
snip list
```

Behavior:

1. Wrapper writes/updates a **minimal** `vendir.yml` (and uses `vendir sync`) for the chosen catalog path → destination.  
2. Record pin from `vendir.lock.yml`.  
3. Diff against previous files before overwrite; confirm unless `-y`.

Acceptance:

- `snip add files/src/...` (fixture) materializes files via vendir.  
- Re-run sync updates when catalog ref changes.  
- User never hand-edits vendir config for the happy path.

## Phase 3 — `snip sync <file>` (anchors)

Per [ADR 0005](adr/0005-snip-anchors-pins-and-update-ux.md) and [snip guide](content/snip.md):

Anchor sketch (lock this grammar in code + one doc note if refined):

```bash
# >>> snip:id=NAME path=files/... ref=REF
...body...
# <<< snip:id=NAME
```

Plus optional file-level header (`Template source`, `curr_version`).

Flow:

1. Parse anchors in the target file.  
2. For each selected id: fetch catalog bytes for `path` @ `ref` **via vendir_wrap** (temp dir sync), not ad-hoc git clone sprawl.  
3. Menu: which portions to update.  
4. Diff region → confirm → replace body; bump `ref` in marker metadata.

Acceptance:

- Fixture script with two anchors; `snip sync fixture.sh` updates only selected region.  
- `-y` updates all without prompt.

## Phase 4 — Polish (same PR series or follow-up)

1. Shared interactive browse for `seed` / `snip`.  
2. Document install: shims on PATH; mention mise.  
3. Point root README at `docs/content/` (short); leave `bp` marked deprecated.  
4. Optional: migrate one real template `templates/python` → `projects/python-base` for a live demo.  
5. Tests in CI (`task test` / pytest).

## Out of scope (this implementation)

- Rewriting all catalog content  
- Public PyPI package  
- Three-way merge UI  
- Extending `bp`  
- Heavy TUI

## Implementation notes for the agent

- **Remote catalog:** prefer letting Copier/vendir speak git; wrapper only passes URL + path + ref.  
- **Local catalog:** if `UT_CATALOG_REPO` is an existing directory, use it directly (fast for dev).  
- **Diff/confirm:** `difflib.unified_diff` + stdin prompt; never silent overwrite without `-y`.  
- **Errors:** non-zero exit if upstream CLI missing or fails; print stderr.  
- **Commits:** small, reviewable PRs per phase (0+1, then 2, then 3). Ask before committing if user rules require it.  
- **Read first:** `docs/content/overview.md`, `quickstart.md`, ADR 0002/0004/0005/0006.

## Definition of done

- [x] `bin/seed` and `bin/snip` work with mise PATH  
- [x] `seed new` / `seed sync` wrap Copier  
- [x] `snip add` / path sync wrap vendir  
- [x] `snip sync <file>` anchors work with diff/confirm  
- [x] Shared catalog/confirm/diff helpers, small files  
- [x] Unit tests for anchors + smoke tests with mocks/fixtures  
- [x] vendir pinned in mise.toml  
- [x] No new heavy Python dependencies without explicit approval  

## Prompt blurb (copy-paste)

```text
Implement seed/snip per docs/IMPLEMENTATION.md in this repo.
Follow docs/adr and docs/content. Python only, stdlib-first, small modules
under ut_cli/. Wrap copier (seed) and vendir (snip) via subprocess.
Unified UX: UT_CATALOG_REPO, diff+confirm catalog-wins, -y for CI.
Do not extend bin/bp. Work phase by phase; keep PRs/reviewable chunks small.
Ask before committing.
```
