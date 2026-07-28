# Seed — project scaffolds

`seed` creates and updates **whole project trees** from `projects/`. It wraps [Copier](https://copier.readthedocs.io/) behind the **same UX language** as `snip` (catalog URL, menus, sync, pins, diff/confirm).

You normally run **`seed`**, not `copier`.

## When to use `seed`

- New Python / shell project from a maintained skeleton  
- Questions (name, options) + consistent layout (CI, tests, …)  
- Later **sync** of template updates without recreating by hand  

Use [`snip`](snip.md) for fragments inside an existing file.

## Commands (target)

```bash
seed                          # browse projects/, Q&A, generate
seed new <project-path>       # e.g. projects/python-web
seed sync                     # update current project from linked template
seed sync --ref v1.2.3        # illustrative pin move
```

Defaults to `$UT_CATALOG_REPO`.

## Example A — Python web app

```bash
mkdir my-service && cd my-service
seed new projects/python-web
# answer questions → tree + recorded answers/pin

seed sync
# review → confirm (managed template files follow catalog)
```

## Example B — Shell + bats

```bash
seed new projects/shell-bats
```

## Example C — Menu

```bash
seed
# Projects
#   python-base
#   python-web
#   shell-bats
# ▸ python-web
```

## Under the hood (footnote)

`seed` invokes Copier (`copy` / `update`) and keeps mise’s `copier` on PATH. Authors still write Copier templates under `projects/`; consumers should not need Copier’s CLI for everyday use. See [ADR 0004](../adr/0004-backend-tools-via-mise.md).

## Transitional notes

Prefer `seed` over calling Copier directly. Legacy Copier trees under `templates/` still work for `bp`; new work lives under `projects/` (e.g. `projects/python-base`).

## Related

- [ADR 0002](../adr/0002-seed-and-snip-clis.md) · [ADR 0004](../adr/0004-backend-tools-via-mise.md)
