# 06 — Python et uv

## Rôle

Gérer la version de Python, les dépendances et l'environnement virtuel du projet, de façon reproductible sur n'importe quelle machine (la sienne, la CI, celle d'un recruteur).

## Pourquoi ce choix

- **uv** (Astral, auteurs de Ruff) remplace à lui seul `venv`, `pip`, `pip-tools` et `pyenv`.
- 10 à 100 fois plus rapide que pip, sensible avec des bibliothèques lourdes (pandas, BigQuery).
- Fichier de verrouillage `uv.lock` : versions exactes de toutes les dépendances, y compris transitives.
- Standard `pyproject.toml` (PEP 621) : lisible par tous les outils Python, pas de format propriétaire.

Version installée : uv 0.12.17 (via snap, `/snap/bin/uv`). Python 3.12.3 (système).

## Fichiers

| Fichier | Contenu | Écrit par | Versionné |
|---|---|---|---|
| `pyproject.toml` | ce dont le projet a **besoin** (`pandas>=3.0.6`) | soi-même, via `uv add` | oui |
| `uv.lock` | ce qui est **réellement installé** (`pandas==3.0.6`, `numpy==2.5.3`…) | uv, jamais à la main | oui |
| `.venv/` | l'environnement virtuel : un Python et les bibliothèques du projet | uv | **non** (recréé depuis le lock) |

`pyproject.toml` reste souple, `uv.lock` rend l'installation reproductible. Monter de version se fait volontairement (`uv lock --upgrade`), puis on teste.

## Configuration

- **Nom** : `prc-fuel-burn-2025`, **Python** : `>=3.12`.
- **Dépendances** (nécessaires à l'exécution du code) :
  - `pandas`
  - `google-cloud-bigquery[pandas]` : l'extra `[pandas]` permet `.to_dataframe()` sur un résultat de requête
  - `google-cloud-storage`
  - `openap`
- **Groupe `dev`** (nécessaires pour développer, pas pour exécuter) : `ruff`, `pytest`, `ipykernel`, `pre-commit`.
  Tout est versionné, groupe dev compris. La différence : `uv sync --no-dev` installe seulement de quoi exécuter (ex. conteneur de déploiement).

## Package `src/prc_fuel/`

Le code réutilisable vit dans un package installé dans `.venv`, importable partout (`import prc_fuel`), y compris depuis les notebooks et les tests.

```toml
[build-system]
requires = ["uv_build>=0.12,<0.13"]
build-backend = "uv_build"

[tool.uv.build-backend]
module-name = "prc_fuel"   # sinon uv chercherait src/prc_fuel_burn_2025/
```

- `__init__.py` fait du dossier un package.
- Le dossier `src/` sépare le code du reste (tests, notebooks, docs) et évite d'importer un fichier local à la place du package installé.
- **Installation éditable** : uv ne copie pas le code, il dépose `.venv/lib/python3.12/site-packages/prc_fuel_burn_2025.pth`, qui contient le chemin vers `src/`. Une modification du code est prise en compte immédiatement ; `uv sync` n'est nécessaire que si les dépendances ou `pyproject.toml` changent.

## Commandes utiles

```bash
uv init --bare --name <nom> --python 3.12   # créer pyproject.toml seul
uv add <paquet>                  # ajouter une dépendance (pyproject + lock + .venv)
uv add --dev <paquet>            # ajouter un outil de développement
uv remove <paquet>               # retirer une dépendance
uv sync                          # (re)créer .venv selon uv.lock
uv sync --locked                 # idem, mais échoue si uv.lock n'est plus à jour (CI)
uv lock --upgrade                # monter les versions dans les limites du pyproject
uv run <commande>                # exécuter dans l'environnement sans l'activer
```

## Pièges connus

- Sur Ubuntu, la commande `python` n'existe pas hors environnement virtuel (seulement `python3`). Si `which python` ne renvoie rien, le `.venv` n'est pas activé.
- Modifier `pyproject.toml` à la main sans `uv lock` : la CI échoue à `uv sync --locked`.
- Mettre des guillemets autour des extras dans le shell : `uv add "google-cloud-bigquery[pandas]"`.
