# 08 — Code quality: Ruff and pre-commit

## Role

- **Ruff**: enforce a consistent style and catch problems in Python code.
- **pre-commit**: run these checks automatically before each commit, and block the commit if they fail.

## Why this choice

- **Ruff** replaces Black, isort, Flake8 and pyupgrade in a single, very fast tool, configured in `pyproject.toml`.
- **pre-commit**: Ruff only helps if you remember to run it. Hooks make the check automatic and also block costly mistakes (data file, private key).

Versions: ruff 0.16.9, pre-commit 4.6.2 (`dev` group, see 06).

## Ruff: two commands, two roles

| Command | Handles | Example |
|---|---|---|
| `ruff format` | **form**: rewrites the code without changing what it does | spaces, indentation, line breaks (PEP 8) |
| `ruff check` | **problems**; `--fix` fixes some of them | unused import, undefined variable |

Configuration (`pyproject.toml`):

```toml
[tool.ruff]
line-length = 88

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP"]

[tool.ruff.lint.per-file-ignores]
"notebooks/*" = ["E501"]
```

| Code | Family | Catches |
|---|---|---|
| `E` | pycodestyle | PEP 8 style errors |
| `F` | Pyflakes | unused import, undefined variable |
| `I` | isort | unsorted imports |
| `B` | flake8-bugbear | classic pitfalls (list as default argument value…) |
| `UP` | pyupgrade | old syntax when a more modern one exists in 3.12 |

`per-file-ignores`: line length (`E501`) is not checked in `notebooks/`, whose cells contain long SQL queries inside strings (`ruff format` never splits strings). Every other rule still applies there, and `src/` keeps the full rule set.

A single configuration, applied everywhere: VS Code (format on save, see 07), terminal, pre-commit and CI (see 09).

## pre-commit

Configuration (`.pre-commit-config.yaml`, versioned):

| Hook | Role |
|---|---|
| `trailing-whitespace` | removes spaces at the end of lines |
| `end-of-file-fixer` | one newline at the end of each file |
| `check-yaml`, `check-toml` | valid YAML and TOML files |
| `check-added-large-files` | blocks files over 1 MB (data) |
| `detect-private-key` | blocks private keys |
| `ruff-check --fix`, `ruff-format` | Ruff (see above) |

`rev` pins the version of each tool, for the same reason as `uv.lock`. In YAML, indentation matters: spaces only.

### How it works

- Git runs `.git/hooks/pre-commit` before each commit; if a hook fails, **the commit is not created**.
- Only files **tracked by Git** are checked ("no files to check" otherwise), and only what is staged for the commit: pre-commit sets the rest aside ("Stashing unstaged files") then restores it. A config change (e.g. in `pyproject.toml`) that is not staged is therefore not seen by the hooks.
- A hook that **fixes** a file reports a failure: the fix is on disk, not in the commit. Review it, `git add` the file again, then re-run the same `git commit`.
- `.git/hooks/` is **never** carried over by a clone (otherwise cloning a repo could run code). Everyone must run `pre-commit install`; only `.pre-commit-config.yaml` (the recipe) is shared. Hence the CI, which cannot be forgotten.

### Notebooks

- `nbstripout` (git filter, installed with `uv run nbstripout --install`) removes notebook outputs when they are staged: only code and markdown are committed.
- Ruff also checks and formats notebook cells. `ruff format` rewrites the `.ipynb` files on disk: close and reopen them in VS Code before editing again (see 07).

## Useful commands

```bash
uv run ruff check .                    # problems
uv run ruff check --fix .              # fix what can be fixed
uv run ruff format .                   # format
uv run ruff format --check .           # check without modifying
uv run pre-commit install              # install the git hook (once per clone)
uv run pre-commit run                  # run hooks on staged files, before committing
uv run pre-commit run --all-files      # run on the whole repo
uv run pre-commit autoupdate           # update tool versions (rev)
```
