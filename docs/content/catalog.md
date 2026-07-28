# Catalog and self-hosting

The valuable artifact is the **git catalog**. `seed` and `snip` are thin clients with a **unified UX**; they wrap **Copier** or **vendir** so you do not operate those tools directly for everyday use.

## Default catalog

```text
https://github.com/mrjk/universal-templates.git
```

```toml
# mise.toml
[env]
UT_CATALOG_REPO = "https://github.com/mrjk/universal-templates.git"
```

## Target layout

```text
projects/                 # seed → Copier
  python-base/
  python-web/
  shell-bats/
  shell-home/
files/                    # snip → vendir (+ region glue)
  bin/
  src/
  notes/
```

| Kind | Location | Engine (behind UX) |
|------|----------|--------------------|
| Project | `projects/<name>/` | Copier |
| Fragment / autonomous | `files/…` | vendir (+ anchors when in-file) |

Legacy `templates/`, `parts/`, `common/` migrate here over time ([Status](status.md)).

## Host your own snippets

```bash
mkdir -p my-catalog/{projects,files/bin,files/src,files/notes}
cd my-catalog && git init
# add projects/… (Copier templates) and files/… (snip units)
git remote add origin https://github.com/YOU/my-catalog.git
git push -u origin main

export UT_CATALOG_REPO="https://github.com/YOU/my-catalog.git"
seed
snip sync ./some_script.sh
```

Local path:

```bash
export UT_CATALOG_REPO="$HOME/prj/my-catalog"
```

Same commands, your content — no registry.

## Versioning for other people

- Prefer **git tags** on the catalog (`v1.2.3`).  
- `seed` records template ref (via Copier answers / wrapper state).  
- `snip` records pins in vendir lock and/or in-file headers/anchors.

```bash
# Template source: https://github.com/YOU/my-catalog.git
# curr_version: v1.2.3
```

## Adding content (authors)

**Project:** add `projects/<name>/` as a Copier template → consumers `seed new projects/<name>`.  
**Snip:** add under `files/bin|src|notes/…` → consumers embed anchors/header → `snip sync`.

Authors may touch Copier/vendir layouts; **consumers** stay on `seed`/`snip`.

## Related

- [ADR 0003](../adr/0003-catalog-layout-and-self-hosting.md) · [ADR 0004](../adr/0004-backend-tools-via-mise.md)
