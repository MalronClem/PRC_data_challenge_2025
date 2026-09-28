# 09 — Intégration continue (GitHub Actions)

## Rôle

À chaque push sur `main` et à chaque pull request, cloner le repo sur une machine neuve et relancer les vérifications du projet.

## Pourquoi ce choix

- **Personne ne peut y échapper** : un hook local se contourne (`git commit --no-verify`, `pre-commit install` oublié), la CI tourne quoi qu'il arrive.
- **Preuve que le projet s'installe de zéro** : un `uv.lock` incohérent ou une dépendance manquante casse ici, pas chez la personne qui clone.
- **GitHub Actions** : intégré au repo, gratuit pour ce volume, badge vert/rouge visible sur chaque commit.

## Configuration

`.github/workflows/ci.yml` :

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

| Élément | Rôle |
|---|---|
| `on` | déclencheurs : push sur `main`, toute pull request |
| `runs-on: ubuntu-latest` | machine Linux neuve et jetable |
| `actions/checkout` | récupère le code |
| `astral-sh/setup-uv` | installe uv |
| `uv sync --locked` | installe exactement `uv.lock` ; échoue si le lock ne correspond plus à `pyproject.toml` |
| `pre-commit run --all-files` | les **mêmes** vérifications qu'en local : une seule source de règles |

Structure d'un workflow : un workflow contient des **jobs**, un job contient des **steps** (commande `run` ou action toute faite `uses`).

**Statut** : en place, première exécution verte le 2026-09-27.

## À ajouter plus tard

- `uv run pytest` quand des tests existeront (pytest échoue s'il ne trouve aucun test).
- Protection de la branche `main` sur GitHub : interdire de fusionner si la CI est rouge.

## Où le retrouver

Repo GitHub → onglet **Actions** : historique des exécutions et journaux de chaque étape.
