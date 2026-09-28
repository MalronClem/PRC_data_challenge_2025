# 08 — Qualité du code : Ruff et pre-commit

## Rôle

- **Ruff** : garantir un style uniforme et repérer les problèmes du code Python.
- **pre-commit** : lancer ces vérifications automatiquement avant chaque commit, et bloquer le commit en cas d'échec.

## Pourquoi ce choix

- **Ruff** remplace Black, isort, Flake8 et pyupgrade en un seul outil, très rapide, configuré dans `pyproject.toml`.
- **pre-commit** : Ruff ne protège que si on pense à le lancer. Les hooks rendent la vérification automatique et bloquent aussi les erreurs coûteuses (fichier de données, clé privée).

Versions : ruff 0.16.9, pre-commit 4.6.2 (groupe `dev`, voir 06).

## Ruff : deux commandes, deux rôles

| Commande | S'occupe de | Exemple |
|---|---|---|
| `ruff format` | la **forme** : réécrit le code sans changer ce qu'il fait | espaces, indentation, sauts de ligne (PEP 8) |
| `ruff check` | les **problèmes** ; `--fix` en corrige une partie | import inutilisé, variable non définie |

Configuration (`pyproject.toml`) :

```toml
[tool.ruff]
line-length = 88

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP"]
```

| Code | Famille | Repère |
|---|---|---|
| `E` | pycodestyle | erreurs de style PEP 8 |
| `F` | Pyflakes | import inutilisé, variable non définie |
| `I` | isort | imports mal triés |
| `B` | flake8-bugbear | pièges classiques (liste comme valeur par défaut d'argument…) |
| `UP` | pyupgrade | syntaxe ancienne alors qu'une plus moderne existe en 3.12 |

Une seule configuration, appliquée partout : VS Code (formatage à l'enregistrement, voir 07), terminal, pre-commit et CI (voir 09).

## pre-commit

Configuration (`.pre-commit-config.yaml`, versionné) :

| Hook | Rôle |
|---|---|
| `trailing-whitespace` | supprime les espaces en fin de ligne |
| `end-of-file-fixer` | un saut de ligne à la fin de chaque fichier |
| `check-yaml`, `check-toml` | fichiers YAML et TOML valides |
| `check-added-large-files` | bloque les fichiers de plus de 1 Mo (données) |
| `detect-private-key` | bloque les clés privées |
| `ruff-check --fix`, `ruff-format` | Ruff (voir ci-dessus) |

`rev` fixe la version de chaque outil, pour la même raison que `uv.lock`. En YAML, l'indentation compte : espaces uniquement.

### Fonctionnement

- Git lance `.git/hooks/pre-commit` avant chaque commit ; si un hook échoue, **le commit n'est pas créé**.
- Seuls les fichiers **suivis par Git** sont vérifiés (« no files to check » sinon), et seulement ce qui est préparé pour le commit : pre-commit met de côté le reste (« Stashing unstaged files ») puis le restaure.
- Un hook qui **corrige** un fichier signale un échec : la correction est sur le disque, pas dans le commit. Il faut relire, refaire `git add` sur le fichier, puis relancer le même `git commit`.
- `.git/hooks/` n'est **jamais** transmis par un clone (sinon cloner un repo pourrait exécuter du code). Chacun doit lancer `pre-commit install` ; seul `.pre-commit-config.yaml` (la recette) est partagé. D'où la CI, qui ne peut pas être oubliée.

## Commandes utiles

```bash
uv run ruff check .                    # problèmes
uv run ruff check --fix .              # corriger ce qui peut l'être
uv run ruff format .                   # formater
uv run ruff format --check .           # vérifier sans modifier
uv run pre-commit install              # installer le hook git (une fois par clone)
uv run pre-commit run                  # lancer les hooks sur les fichiers préparés, avant de committer
uv run pre-commit run --all-files      # lancer sur tout le repo
uv run pre-commit autoupdate           # mettre à jour les versions (rev)
```
