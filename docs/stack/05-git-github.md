# 05 — Git et GitHub

## Rôle

Versionner le code et la documentation, et publier le projet comme portfolio.

## Repo

- **Nom prévu** : `prc-fuel-burn-2025`. Nom actuel sur GitHub : `PRC_data_challenge_2025` (renommage à faire dans Settings → General, puis `git remote set-url origin <nouvelle-url>` en local).
- **Visibilité** : privé pour commencer, à passer en public quand le projet est présentable et vérifié (aucune information sensible).
- **Initialisé avec** : `README.md`, `.gitignore` (modèle Python, exclut notamment `.venv/`), licence MIT.

## Licence

- **MIT** : réutilisation libre du code, y compris commerciale, à condition de conserver la mention de l'auteur et de la licence. Aucune garantie.
- La licence ne couvre que le **code**. Les données sont sous CC BY 4.0 et ne sont **pas** dans le repo. Le README doit citer :
  - le papier : Sun, J., Spinielli, E., & Strohmeier, M. (2026). *Aircraft Fuel Burn Estimation: The EUROCONTROL PRC 2025 Data Challenge*. Journal of Open Aviation Science. https://doi.org/10.59490/joas.2026.8750
  - le dataset : https://doi.org/10.5281/zenodo.19184661

## Configuration Git

```bash
git --version
git config --global user.name
git config --global user.email
```

L'e-mail configuré apparaît publiquement dans l'historique des commits. Utiliser l'adresse anonyme fournie par GitHub (`...@users.noreply.github.com`) pour ne pas exposer son adresse personnelle.

Configuration en place :

- `user.name` : `MalronClem` (identique au pseudo GitHub)
- `user.email` : adresse noreply GitHub (Settings → Emails)
- Côté GitHub : « Keep my email addresses private » et « Block command line pushes that expose my email » activés

```bash
git config --global user.email "<id>+<pseudo>@users.noreply.github.com"
git commit --amend --reset-author --no-edit   # corriger l'auteur du dernier commit (seulement s'il n'est pas encore poussé)
git log --format='%h %an <%ae> %s'            # vérifier l'auteur de chaque commit
```

## Conventions de commit

- **Messages en anglais**, à l'impératif, majuscule initiale, sans point final, moins de 50 caractères : `Add CI workflow`, `Set up Ruff and pre-commit`. Le message complète la phrase « If applied, this commit will… ».
- **Un commit = un changement logique.** Deux sujets différents font deux commits.
- **Lister les fichiers** dans `git add` plutôt que `git add .`, pour ne rien committer par accident.
- **Vérifier après chaque commit** (`git status`, `git log --oneline -1`) : un hook pre-commit peut l'avoir bloqué (voir 08).
- **Jamais de `--amend` sur un commit déjà poussé** : le hash change, les historiques local et distant divergent.

## Commandes utiles

```bash
git status                      # état : modifié, préparé, non suivi, avance sur origin
git log --oneline               # historique compact
git check-ignore -v <chemin>    # quelle règle du .gitignore exclut ce fichier
git remote -v                   # adresse du repo distant (origin)
```

## Authentification SSH

```bash
ssh-keygen -t ed25519 -C "student-laptop"   # clé protégée par une passphrase
cat ~/.ssh/id_ed25519.pub                   # clé publique à coller dans GitHub
ssh -T git@github.com                       # test de connexion
```

- Clé publique ajoutée dans GitHub : Settings → SSH and GPG keys → New SSH key (type Authentication Key).
- La clé **privée** (`~/.ssh/id_ed25519`) ne quitte jamais la machine.
- À la première connexion, vérifier que l'empreinte affichée est celle publiée par GitHub (ED25519 : `SHA256:+DiY3wvvV6TuJJhbpZisF/zLDA0zPMSvHdkr4UvCOqU`).

## Clonage

```bash
mkdir -p ~/Projects
cd ~/Projects
git clone git@github.com:<pseudo>/prc-fuel-burn-2025.git
cd prc-fuel-burn-2025
uv sync                       # recrée .venv à l'identique (voir 06)
uv run pre-commit install     # les hooks git ne sont pas transmis par le clone (voir 08)
```

## Dépannage : `git push` très lent

Constaté le 2026-09-27 : chaque push prenait environ 45 s. La cause n'était ni Git ni le réseau, mais la machine. L'Embedded Controller du portable ne répondait plus (centaines de processus `kworker/…+kec_query` bloqués, charge moyenne ≈ 240), ce qui bloquait systemd. Au démarrage, SSH interroge systemd pour identifier l'utilisateur et attendait l'expiration du délai.

- Diagnostic : `uptime` (charge anormalement élevée), `ssh -v -T git@github.com` (le délai se situe avant « Reading configuration data »).
- Solution : redémarrer. Si le problème revient (souvent après une mise en veille ou un branchement du chargeur) : mettre à jour le système et le BIOS.

## Ce qui ne va jamais dans le repo

- les données (vivent dans Cloud Storage)
- identifiants, jetons, fichiers de clé
- adresse e-mail personnelle, identifiant du compte de facturation
- l'environnement virtuel `.venv/`
