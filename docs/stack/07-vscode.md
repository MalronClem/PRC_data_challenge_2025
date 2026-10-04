# 07 — VS Code

## Role

Project editor: writing code, exploration notebooks, debugging, integrated terminal.

## Why this choice

- **PyCharm ruled out**: excellent at refactoring, but Jupyter support requires the Pro edition and the tool is heavier.
- **VS Code chosen**: free built-in Jupyter notebooks, lightweight, Remote SSH / Dev Containers extensions if training moves to a remote machine.

Installation: official `.deb` package (`code`). Profile reset on 2026-09-27 (removed `~/.vscode` and `~/.config/Code`) to start from a clean base.

## Installed extensions

| Extension | Publisher | Role |
|---|---|---|
| Python | Microsoft | Python support; also installs **Pylance** (autocompletion, analysis) and **Python Debugger** |
| Jupyter | Microsoft | `.ipynb` notebooks |
| Ruff | Astral Software | formatting and linting (see 08) |

Always check the publisher: copies published by others exist.

## Settings: user and project

- **User** (`~/.config/Code/User/settings.json`): personal preferences (theme, font), for all projects.
- **Project** (`.vscode/settings.json`, versioned): project-specific rules, the same for anyone who opens it.

```jsonc
{
  // Project Python
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",

  // Format Python files with Ruff on every save
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true
  }
}
```

- `${workspaceFolder}`: the project folder, so the path works wherever the clone lives.
- `"[python]"`: settings applied to Python files only.
- JSONC format: JSON with `//` comments, accepted by VS Code.

## Checks

1. Status bar, bottom right: the interpreter shown must be `.venv`. Otherwise `Ctrl+Shift+P` → `Python: Select Interpreter`.
2. New terminal (`` Ctrl+Shift+` ``): `which python` must return `…/PRC_data_challenge_2025/.venv/bin/python`. Activation puts `.venv/bin` first in `PATH` (`echo $PATH`).

## Known pitfalls

- A misnamed configuration file produces **no error**, it is simply ignored (happened: `setting.json` instead of `settings.json`). When a config "does nothing", first check the exact name and location.
- A tab opened with `Ctrl+N` ("Untitled-1") is not a Python file: create files from the explorer, with their extension.
- A terminal opened **before** choosing the interpreter does not activate `.venv`: open a new one.
- On first launch, answer "Yes, I trust the authors": in restricted mode, Python extensions are disabled.
- When a notebook file is changed on disk (a pre-commit hook, a script), close and reopen it before editing: saving the old open version overwrites the change.
