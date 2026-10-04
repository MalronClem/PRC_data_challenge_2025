# 05 — Git and GitHub

## Role

Version the code and documentation, and publish the project as a portfolio piece.

## Repo

- **Planned name**: `prc-fuel-burn-2025`. Current name on GitHub: `PRC_data_challenge_2025` (rename in Settings → General, then `git remote set-url origin <new-url>` locally).
- **Visibility**: private to start with, to be made public once the project is presentable and checked (no sensitive information).
- **Initialised with**: `README.md`, `.gitignore` (Python template, excludes `.venv/` among others), MIT licence.

## Licence

- **MIT**: free reuse of the code, including commercial, as long as the author and licence notice are kept. No warranty.
- The licence only covers the **code**. The data is under CC BY 4.0 and is **not** in the repo. The README must cite:
  - the paper: Sun, J., Spinielli, E., & Strohmeier, M. (2026). *Aircraft Fuel Burn Estimation: The EUROCONTROL PRC 2025 Data Challenge*. Journal of Open Aviation Science. https://doi.org/10.59490/joas.2026.8750
  - the dataset: https://doi.org/10.5281/zenodo.19184661

## Git configuration

```bash
git --version
git config --global user.name
git config --global user.email
```

The configured email appears publicly in the commit history. Use the anonymous address provided by GitHub (`...@users.noreply.github.com`) so as not to expose a personal address.

Current configuration:

- `user.name`: `MalronClem` (same as the GitHub username)
- `user.email`: GitHub noreply address (Settings → Emails)
- On GitHub: "Keep my email addresses private" and "Block command line pushes that expose my email" enabled

```bash
git config --global user.email "<id>+<username>@users.noreply.github.com"
git commit --amend --reset-author --no-edit   # fix the author of the last commit (only if not pushed yet)
git log --format='%h %an <%ae> %s'            # check the author of each commit
```

## Commit conventions

- **Messages in English**, imperative mood, capitalised, no final period, under 50 characters: `Add CI workflow`, `Set up Ruff and pre-commit`. The message completes the sentence "If applied, this commit will…".
- **One commit = one logical change.** Two different topics make two commits.
- **List the files** in `git add` rather than `git add .`, so nothing gets committed by accident.
- **Check after each commit** (`git status`, `git log --oneline -1`): a pre-commit hook may have blocked it (see 08).
- **Never `--amend` a commit that was already pushed**: the hash changes and local and remote histories diverge.

## Useful commands

```bash
git status                      # state: modified, staged, untracked, ahead of origin
git log --oneline               # compact history
git check-ignore -v <path>      # which .gitignore rule excludes this file
git remote -v                   # remote repo address (origin)
```

## SSH authentication

```bash
ssh-keygen -t ed25519 -C "student-laptop"   # key protected by a passphrase
cat ~/.ssh/id_ed25519.pub                   # public key to paste into GitHub
ssh -T git@github.com                       # connection test
```

- Public key added on GitHub: Settings → SSH and GPG keys → New SSH key (type Authentication Key).
- The **private** key (`~/.ssh/id_ed25519`) never leaves the machine.
- On first connection, check that the displayed fingerprint is the one published by GitHub (ED25519: `SHA256:+DiY3wvvV6TuJJhbpZisF/zLDA0zPMSvHdkr4UvCOqU`).

## Cloning

```bash
mkdir -p ~/Projects
cd ~/Projects
git clone git@github.com:<username>/prc-fuel-burn-2025.git
cd prc-fuel-burn-2025
uv sync                       # recreates .venv identically (see 06)
uv run pre-commit install     # git hooks are not carried over by a clone (see 08)
uv run nbstripout --install   # strip notebook outputs on commit (local git config)
```

## Troubleshooting: very slow `git push`

Seen on 2026-09-27: each push took about 45 s. The cause was neither Git nor the network, but the machine. The laptop's Embedded Controller had stopped responding (hundreds of blocked `kworker/…+kec_query` processes, load average ≈ 240), which blocked systemd. On startup, SSH queries systemd to identify the user and was waiting for the timeout.

- Diagnosis: `uptime` (abnormally high load), `ssh -v -T git@github.com` (the delay happens before "Reading configuration data").
- Fix: reboot. If it comes back (often after sleep or plugging in the charger): update the system and BIOS.

## What never goes into the repo

- the data (lives in Cloud Storage)
- credentials, tokens, key files
- personal email address, billing account ID
- the `.venv/` virtual environment
- notebook outputs (stripped by nbstripout)
