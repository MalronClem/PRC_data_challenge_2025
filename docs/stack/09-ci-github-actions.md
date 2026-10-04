# 09 — Continuous integration (GitHub Actions)

## Role

On every push to `main` and every pull request, clone the repo on a fresh machine and re-run the project's checks.

## Why this choice

- **Nobody can skip it**: a local hook can be bypassed (`git commit --no-verify`, forgotten `pre-commit install`), the CI runs no matter what.
- **Proof that the project installs from scratch**: an inconsistent `uv.lock` or a missing dependency breaks here, not for the person who clones.
- **GitHub Actions**: built into the repo, free for this volume, green/red badge visible on each commit.

## Configuration

`.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v6
      - run: uv sync --locked
      - run: uv run pre-commit run --all-files
```

| Element | Role |
|---|---|
| `on` | triggers: push to `main`, any pull request |
| `runs-on: ubuntu-latest` | fresh, disposable Linux machine |
| `actions/checkout` | fetches the code |
| `astral-sh/setup-uv` | installs uv |
| `uv sync --locked` | installs exactly `uv.lock`; fails if the lock no longer matches `pyproject.toml` |
| `pre-commit run --all-files` | the **same** checks as locally: a single source of rules |

Workflow structure: a workflow contains **jobs**, a job contains **steps** (a `run` command or a ready-made `uses` action).

**Status**: in place, first green run on 2026-09-27.

## To add later

- `uv run pytest` once tests exist (pytest fails if it finds no test).
- Branch protection on `main` on GitHub: forbid merging when the CI is red.

## Where to find it

GitHub repo → **Actions** tab: run history and logs for each step.
