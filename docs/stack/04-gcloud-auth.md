# 04 — SDK Google Cloud et authentification

## Rôle

Permettre à la machine locale de piloter Google Cloud en ligne de commande (`gcloud`, `bq`) et aux scripts Python d'accéder à Cloud Storage et BigQuery, sans fichier de clé dans le projet.

## Installation (Ubuntu / Debian, dépôt APT officiel)

```bash
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates gnupg curl
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
sudo apt-get update && sudo apt-get install google-cloud-cli
```

Version installée : Google Cloud SDK 586.0.0 (inclut `gcloud`, `bq`, `gsutil`).

Mise à jour : `sudo apt-get update && sudo apt-get install --only-upgrade google-cloud-cli`

## Authentification

Deux connexions distinctes :

1. **Pour la ligne de commande** : `gcloud init`
   Connexion au compte Google et choix du projet `prc-data-challenge-2025`.
2. **Pour les scripts Python** : `gcloud auth application-default login`
   Enregistre des identifiants dans `~/.config/gcloud/application_default_credentials.json`, que toutes les bibliothèques Google retrouvent automatiquement (Application Default Credentials).
   Si un avertissement mentionne un « quota project » :
   `gcloud auth application-default set-quota-project prc-data-challenge-2025`

## Pourquoi pas un fichier de clé de compte de service

Un fichier de clé JSON donne un accès permanent au projet. S'il traîne dans le dossier du projet, il finit facilement sur GitHub. Les Application Default Credentials restent hors du repo, dans la configuration de l'utilisateur. Google déconseille les clés de compte de service pour le développement local.

**Règle : aucun identifiant, jeton ou fichier de clé dans le repo.**

## Vérifications

```bash
gcloud --version                                  # version installée
gcloud config list                                # compte et projet actifs
gcloud storage ls                                 # doit afficher gs://prc2025/
gcloud auth application-default print-access-token   # un jeton = identifiants Python OK
```
