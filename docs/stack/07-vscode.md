# 07 — VS Code

## Rôle

Éditeur du projet : écriture du code, notebooks d'exploration, débogage, terminal intégré.

## Pourquoi ce choix

- **PyCharm écarté** : excellent en refactoring, mais le support Jupyter nécessite la version Pro et l'outil est plus lourd.
- **VS Code retenu** : notebooks Jupyter intégrés gratuitement, léger, extensions Remote SSH / Dev Containers si l'entraînement passe sur une machine distante.

Installation : paquet `.deb` officiel (`code`). Profil réinitialisé le 2026-09-27 (suppression de `~/.vscode` et `~/.config/Code`) pour repartir d'une base propre.

## Extensions installées

| Extension | Éditeur | Rôle |
|---|---|---|
| Python | Microsoft | support Python ; installe aussi **Pylance** (autocomplétion, analyse) et **Python Debugger** |
| Jupyter | Microsoft | notebooks `.ipynb` |
| Ruff | Astral Software | formatage et linting (voir 08) |

Toujours vérifier l'éditeur : des copies publiées par d'autres existent.

## Réglages : utilisateur et projet

- **Utilisateur** (`~/.config/Code/User/settings.json`) : préférences personnelles (thème, police), tous projets confondus.
- **Projet** (`.vscode/settings.json`, versionné) : règles propres au projet, identiques pour quiconque l'ouvre.

```jsonc
{
  // Python du projet
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",

  // Formater les fichiers Python avec Ruff à chaque enregistrement
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true
  }
}
```

- `${workspaceFolder}` : dossier du projet, le chemin fonctionne quel que soit l'emplacement du clone.
- `"[python]"` : réglages appliqués aux seuls fichiers Python.
- Format JSONC : JSON avec commentaires `//`, accepté par VS Code.

## Vérifications

1. Barre d'état en bas à droite : l'interpréteur affiché doit être `.venv`. Sinon `Ctrl+Shift+P` → `Python: Select Interpreter`.
2. Nouveau terminal (`` Ctrl+Shift+` ``) : `which python` doit renvoyer `…/PRC_data_challenge_2025/.venv/bin/python`. L'activation place `.venv/bin` en tête du `PATH` (`echo $PATH`).

## Pièges connus

- Un fichier de configuration mal nommé ne produit **aucune erreur**, il est simplement ignoré (vécu : `setting.json` au lieu de `settings.json`). Quand une config « ne fait rien », vérifier d'abord le nom exact et l'emplacement.
- Un onglet ouvert avec `Ctrl+N` (« Untitled-1 ») n'est pas un fichier Python : créer les fichiers depuis l'explorateur, avec leur extension.
- Un terminal ouvert **avant** le choix de l'interpréteur n'active pas `.venv` : en ouvrir un nouveau.
- Au premier lancement, répondre « Yes, I trust the authors » : en mode restreint, les extensions Python sont désactivées.
