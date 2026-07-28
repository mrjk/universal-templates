# Catalog and self-hosting

The valuable artifact is the **git catalog**. Consumers use [snipseed](https://github.com/mrjk/snipseed) (`seed` / `snip`) against this repo or any compatible fork.

## Default catalog

```text
https://github.com/mrjk/universal-templates.git
```

Unset `UT_CATALOG_REPO` in snipseed → that URL.

Local checkout (great while authoring):

```bash
export UT_CATALOG_REPO="$HOME/prj/universal-templates"
# or simply: export UT_CATALOG_REPO="$PWD"
```

## Layout

```text
projects/                 # seed → Copier
files/                    # snip → vendir (+ anchors)
```

| Kind | Location | Consumer runs |
|------|----------|---------------|
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

Same commands, your content — no registry account. Consumer details: [snipseed — own catalog](https://github.com/mrjk/snipseed/blob/main/docs/content/guides/own-catalog.md).

## Pins / versioning

- Prefer **git tags** on the catalog (`v1.2.3`) for releases others consume.
- `seed` records template linkage in `.copier-answers.yml`.
- `snip` records pins in vendir lock and/or in-file anchors / headers.

```bash
# >>> snip:id=logging path=files/src/logging-setup ref=v1.2.3
```

```bash
# snip: source=https://github.com/YOU/my-catalog.git
# snip: version=v1.2.3
```

## Adding content (authors)

**Project:** `projects/<name>/` with `copier.yml` + template files (include `.copier-answers.yml.jinja` so consumers can sync).  
**Snip:** drop files under `files/bin|src|notes/…`.

For whole-script boilerplates consumers will customize:

- Prefix managed metadata with `snip:` (`path` / `ref` / `source` / `version`).
- Add empty `# >>> snip:slot=NAME` / `# <<< snip:slot=NAME` holes.
- Consumer guide: [Customize a boilerplate script](https://github.com/mrjk/snipseed/blob/main/docs/content/guides/boilerplate-script.md) (snipseed).

Authors may peek at Copier/vendir; **consumers** stay on `seed` / `snip`.

## Related

[Inventory](inventory.md) · [Guides](guides/index.md) · [ADR 0003](adr/0003-catalog-layout-and-self-hosting.md) · [snipseed](https://github.com/mrjk/snipseed)
