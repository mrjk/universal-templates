# Catalog and self-hosting

The valuable artifact is the **git catalog**. `seed` and `snip` are thin clients: same UX, different backends (Copier vs vendir).

## Default catalog

```text
https://github.com/mrjk/universal-templates.git
```

Unset `UT_CATALOG_REPO` → that URL. In this repo, mise also sets the env var for you.

Local checkout (great while learning or authoring):

```bash
export UT_CATALOG_REPO="$HOME/prj/universal-templates"
# or simply: export UT_CATALOG_REPO="$PWD"
```

## Layout

```text
projects/                 # seed → Copier
files/                    # snip → vendir (+ anchors)
```

| Kind | Location | You run |
|------|----------|---------|
| Project | `projects/<name>/` | `seed new projects/<name>` |
| Fragment / file | `files/…` | `snip add` / `snip sync` |

What’s currently shipped: **[Inventory](inventory.md)** (live from disk).

## Host your own

```bash
mkdir -p my-catalog/{projects,files/bin,files/src,files/notes}
cd my-catalog && git init
# add projects/… (Copier templates) and files/… (snip units)
git remote add origin https://github.com/YOU/my-catalog.git
git push -u origin main

export UT_CATALOG_REPO="https://github.com/YOU/my-catalog.git"
seed list
snip list
```

Same commands, your content — no registry account.

## Pins / versioning

- Prefer **git tags** on the catalog (`v1.2.3`) for releases others consume.  
- `seed` records template linkage in `.copier-answers.yml`.  
- `snip` records pins in vendir lock and/or in-file anchors / headers.

```bash
# >>> snip:id=logging path=files/src/logging-setup ref=v1.2.3
```

```bash
# Template source: https://github.com/YOU/my-catalog.git
# curr_version: v1.2.3
```

## Adding content (authors)

**Project:** `projects/<name>/` with `copier.yml` + template files (include `.copier-answers.yml.jinja` so consumers can sync).  
**Snip:** drop files under `files/bin|src|notes/…`.

Authors may peek at Copier/vendir; **consumers** stay on `seed` / `snip`.

## Related

[Inventory](inventory.md) · [Tutorial](tutorial.md) · [ADR 0003](adr/0003-catalog-layout-and-self-hosting.md) · [ADR 0004](adr/0004-backend-tools-via-mise.md)
