# Development setup

## Tools

Pinned via [mise](https://mise.jdx.dev/) (`mise.toml`):

- Python
- [uv](https://docs.astral.sh/uv/)
- [Task](https://taskfile.dev/)
- shellcheck

```bash
mise trust && mise install
uv sync --all-groups
task               # root CI tasks only
```

## Gates

| Command | What it runs |
| --- | --- |
| `task test_core` | unit + coverage + lint (no docs) |
| `task test` | `test_core` + docs checks |
| `task fix_lint` | isort / black / pymarkdown auto-fix |
| `task docs` | serve docs locally (Zensical) |
| `cd ci && task` | full CORE task list |
| `cd docs && task` | full docs task list |
