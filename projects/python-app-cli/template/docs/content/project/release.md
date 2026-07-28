# Release

1. On `main` / `master`, with a clean tree:

```bash
./scripts/release.sh patch   # or minor / major / 1.2.3
git push && git push --tags
```

2. Tag push `v*` triggers `.github/workflows/publish_pypi.yml` (configure the `pypi` environment / trusted publishing).

3. Docs deploy from `main` / `develop` via `.github/workflows/gh_page.yml`.
