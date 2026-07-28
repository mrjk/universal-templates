# Seed — project scaffolds

`seed` creates and updates **whole project trees** from `projects/`. It wraps [Copier](https://copier.readthedocs.io/); you normally run **`seed`**, not `copier`.

Same habits as [`snip`](snip.md): `$UT_CATALOG_REPO`, list/browse, sync, pins, diff/confirm.

## When to use `seed`

- Start a new project from a maintained skeleton  
- Answer a few questions (name, options) and get a consistent layout  
- Later pull template updates with `seed sync`  

Use [`snip`](snip.md) for fragments *inside* an existing file.

## Commands

```bash
seed                          # numbered menu of projects/ → generate into cwd
seed list                     # print projects/ paths
seed new <project-path> [dest] [--ref REF] [-y]
seed sync [dest] [--ref REF] [-y]
```

| Argument | Meaning |
|----------|---------|
| `project-path` | Catalog path, e.g. `projects/python-base` (bare name `python-base` is accepted) |
| `dest` | Output directory (default `.`) |
| `--ref` | Catalog git ref when the catalog is remote |
| `-y` | Non-interactive defaults / confirms |

## Walkthrough — Python base

```bash
export UT_CATALOG_REPO=/path/to/universal-templates   # or leave default URL

mkdir my-service && cd my-service
seed new projects/python-base . 
# answer project_slug / description → files appear

ls
# .copier-answers.yml  README.md  <slug>/  pyproject.toml  tests/ …
```

Non-interactive:

```bash
seed new projects/python-base ./my-service -y
```

### Update from the catalog

```bash
cd my-service
seed sync          # confirm intent, then Copier re-applies the template
seed sync -y       # CI / “just do it”
seed sync --ref v1.2.3
```

`seed` looks for `.copier-answers.yml` in the project directory. That file records `_src_path` (and more) so sync knows which template to use.

> **Note:** Copier’s smart `update` needs a git-tracked project and a prior template commit. For local-path templates (typical while developing the catalog), `seed sync` falls back to **recopy** (catalog wins for managed files).

## What’s in this catalog today

See **[Inventory](inventory.md)** for the live list of `projects/`. More scaffolds land there over time.

## Menu browse

```bash
seed
# Projects
#   1) projects/_fixture
#   2) projects/python-base
#   q) cancel
```

## Under the hood (optional)

`seed` shells out to `copier copy` / `copier update` (or `recopy`). Authors write Copier templates under `projects/`; consumers stay on `seed`. See [ADR 0004](adr/0004-backend-tools-via-mise.md).

## Related

[Tutorial](tutorial.md) · [Snip](snip.md) · [Catalog](catalog.md) · [Inventory](inventory.md) · [ADR 0002](adr/0002-seed-and-snip-clis.md)
