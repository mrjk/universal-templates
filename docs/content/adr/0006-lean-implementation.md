# ADR 0006 — Lean implementation (Python allowed, not a Python project)

- **Status:** Accepted
- **Date:** 2026-07-28

## Context

Interactive menus, anchor parsing, and subprocess orchestration are easier in Python than in large bash. The repository’s identity is still a **git catalog of templates and snippets**, not a Python application or library product. Heavy dependency stacks would fight that identity and make self-hosting / casual contribution harder.

## Decision

### Language

- **Python is allowed** for unified UX glue (menus, anchor parse, subprocess to **Copier or vendir**, diff/confirm).
- **Bash remains fine** for tiny wrappers (`install.sh`, thin shims).
- Prefer **stdlib-first** Python.

### Not a Python project

- No Poetry-app / packaging-centric product layout for the CLIs.
- No framework stack for the glue.
- No fat dependency tree for `seed`/`snip` themselves.
- Heavy work stays in **mise-installed Copier and vendir**, invoked via `subprocess` — not reimplemented in Python.

### Dependencies

- Optional tiny deps only when clearly worth it (e.g. one small prompt/TUI helper).
- Out for glue: large CLI frameworks, rich UI stacks with many plugins, HTTP client stacks, or extra templating/vendoring engines (that is Copier/vendir’s job).

### How tools ship

- Simple scripts under `bin/` and/or `cli/` with shebangs; mise supplies Python and upstream CLIs in this repo.
- Consumers should not be required to `pip install` a published package merely to use the catalog; mise (for contributors) or a thin install script is enough.
- Catalog content remains plain files + Copier templates — the valuable artifact.

### Testing / quality

- Keep tests focused on glue behavior; do not import a large test framework ecosystem without need.
- Existing bats/shellcheck for shell bits remain appropriate where shell remains.

## Consequences

- Contributors treat Python as a **scripting aid**, not a reason to grow an application core.
- PRs that add heavy PyPI deps to the CLI glue need an explicit exception and ADR amendment.
- Aligns with [ADR 0004](0004-backend-tools-via-mise.md): wrap **Copier or vendir**, keep glue thin, unified UX.
