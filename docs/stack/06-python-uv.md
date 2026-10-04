# 06 — Python and uv

## Role

Manage the Python version, dependencies and virtual environment of the project, reproducibly on any machine (your own, the CI, a recruiter's).

## Why this choice

- **uv** (Astral, the makers of Ruff) replaces `venv`, `pip`, `pip-tools` and `pyenv` on its own.
- 10 to 100 times faster than pip, noticeable with heavy libraries (pandas, BigQuery).
- `uv.lock` lock file: exact versions of every dependency, transitive ones included.
- Standard `pyproject.toml` (PEP 621): readable by every Python tool, no proprietary format.

Installed version: uv 0.12.17 (via snap, `/snap/bin/uv`). Python 3.12.3 (system).

## Files

| File | Content | Written by | Versioned |
|---|---|---|---|
| `pyproject.toml` | what the project **needs** (`pandas>=3.0.6`) | yourself, via `uv add` | yes |
| `uv.lock` | what is **actually installed** (`pandas==3.0.6`, `numpy==2.5.3`…) | uv, never by hand | yes |
| `.venv/` | the virtual environment: a Python and the project's libraries | uv | **no** (recreated from the lock) |

`pyproject.toml` stays flexible, `uv.lock` makes installation reproducible. Upgrading is done on purpose (`uv lock --upgrade`), then tested.

## Configuration

- **Name**: `prc-fuel-burn-2025`, **Python**: `>=3.12`.
- **Dependencies** (needed to run the code):
  - `pandas`
  - `google-cloud-bigquery[pandas]`: the `[pandas]` extra enables `.to_dataframe()` on a query result
  - `google-cloud-storage`
  - `openap`
- **`dev` group** (needed to develop, not to run): `ruff`, `pytest`, `ipykernel`, `pre-commit`, `nbstripout`, `matplotlib`.
  Everything is versioned, dev group included. The difference: `uv sync --no-dev` installs only what is needed to run (e.g. a deployment container).

## `src/prc_fuel/` package

Reusable code lives in a package installed in `.venv`, importable everywhere (`import prc_fuel`), including from notebooks and tests.

```toml
[build-system]
requires = ["uv_build>=0.12,<0.13"]
build-backend = "uv_build"

[tool.uv.build-backend]
module-name = "prc_fuel"   # otherwise uv would look for src/prc_fuel_burn_2025/
```

- `__init__.py` makes the folder a package.
- The `src/` folder separates the code from the rest (tests, notebooks, docs) and avoids importing a local file instead of the installed package.
- **Editable install**: uv does not copy the code, it drops `.venv/lib/python3.12/site-packages/prc_fuel_burn_2025.pth`, which contains the path to `src/`. A code change is picked up immediately; `uv sync` is only needed when dependencies or `pyproject.toml` change.

## Useful commands

```bash
uv init --bare --name <name> --python 3.12   # create pyproject.toml only
uv add <package>                 # add a dependency (pyproject + lock + .venv)
uv add --dev <package>           # add a development tool
uv remove <package>              # remove a dependency
uv sync                          # (re)create .venv from uv.lock
uv sync --locked                 # same, but fails if uv.lock is out of date (CI)
uv lock --upgrade                # upgrade versions within pyproject limits
uv run <command>                 # run inside the environment without activating it
```

## Known pitfalls

- On Ubuntu, the `python` command does not exist outside a virtual environment (only `python3`). If `which python` returns nothing, `.venv` is not activated.
- Editing `pyproject.toml` by hand without `uv lock`: the CI fails at `uv sync --locked`.
- Quote extras in the shell: `uv add "google-cloud-bigquery[pandas]"`.
- A running notebook kernel does not see packages installed after it started: restart the kernel after `uv add`.
