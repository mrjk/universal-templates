# Tutorial — learn by doing

This walkthrough uses **this repo as the catalog**. You will:

1. Install tools with mise  
2. Seed a small Python project  
3. Add a snip file and sync anchors in a script  

Expect ~10 minutes.

## 0. Prerequisites

- [git](https://git-scm.com/)
- [mise](https://mise.jdx.dev/) (`curl https://mise.run | sh`, then activate in your shell)

## 1. Open the repo and install tools

```bash
git clone https://github.com/mrjk/universal-templates.git
cd universal-templates

mise trust          # once per machine, if prompted
mise install        # python, copier, vendir, …
```

With mise activated in this directory, `seed` and `snip` are on your `PATH` (`./bin`).

Point the tools at **this checkout** (fastest while learning):

```bash
export UT_CATALOG_REPO="$PWD"
seed --help
snip --help
```

> Outside this repo later, leave `UT_CATALOG_REPO` unset to use the default GitHub URL, or set it to your fork / local catalog.

## 2. See what’s in the catalog

```bash
seed list
# projects/_fixture
# projects/python-base

snip list
# files/src/_fixture/consumer.sh
# files/src/_fixture/snippet.sh
```

`_fixture` entries are tiny demos for tests and this tutorial. `python-base` is a real (minimal) Copier project.

## 3. Seed a project

```bash
mkdir -p /tmp/ut-learn && cd /tmp/ut-learn
seed new projects/python-base ./demo-app -y
cd demo-app
ls
# .copier-answers.yml  README.md  demo_app/  pyproject.toml  tests/  …
```

What happened:

- Copier copied `projects/python-base` into `./demo-app`
- Defaults filled the questions (`-y`)
- `.copier-answers.yml` remembers the template path so you can sync later

Interactive (no `-y`): answer prompts yourself.

```bash
seed new projects/python-base ./demo-app2
```

Or browse with a numbered menu:

```bash
seed
# pick a projects/… entry, then generate into the current directory
```

### Sync later

From the generated project:

```bash
cd /tmp/ut-learn/demo-app
seed sync -y
```

`seed sync` re-applies the linked template (catalog wins for managed files). Use without `-y` when you want an explicit confirm step first.

## 4. Snip — add a whole file

```bash
mkdir -p /tmp/ut-learn/snip-demo && cd /tmp/ut-learn/snip-demo
snip add files/src/_fixture/snippet.sh --dest . -y
cat snippet.sh
```

You’ll see the catalog fragment on disk. State for tracked adds lives under `.snip/` (vendir config + lock). You normally don’t edit that by hand.

## 5. Snip — refresh regions in a script

Copy the demo consumer (two anchors pointing at the same fixture snippet):

```bash
cp "$UT_CATALOG_REPO/files/src/_fixture/consumer.sh" ./myscript.sh
snip list ./myscript.sh
# fixture-a   path=files/src/_fixture/snippet.sh  ref=main
# fixture-b   …
```

Update all regions without prompts:

```bash
snip sync ./myscript.sh -y
```

Open `myscript.sh`: the bodies between `# >>> snip:…` / `# <<< snip:…` now match the catalog snippet, and `ref=` was refreshed.

Interactive flow (pick which ids to update, review each diff):

```bash
snip sync ./myscript.sh
```

### Anatomy of an anchor

```bash
# >>> snip:id=NAME path=files/src/… ref=REF
… body from the catalog …
# <<< snip:id=NAME
```

- `id` — stable name in *your* file  
- `path` — catalog path under `files/`  
- `ref` — pin (tag, branch, or sha)  

Comment prefix can be `#` or `//` (host-language style).

## 6. Flags you’ll reuse

| Flag | Meaning |
|------|---------|
| `-y` / `--yes` | No confirm prompts (CI / demos) |
| `--ref REF` | Catalog git ref when fetching |

Shared env:

| Variable | Meaning |
|----------|---------|
| `UT_CATALOG_REPO` | Git URL **or** local directory of the catalog |

## You’re done

You now know the loop:

1. **Discover** — `seed list` / `snip list`  
2. **Add** — `seed new` / `snip add`  
3. **Refresh** — `seed sync` / `snip sync`  

Next depth: [Seed](seed.md) · [Snip](snip.md) · [Catalog & self-hosting](catalog.md)
