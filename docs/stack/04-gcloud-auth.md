# 04 — Google Cloud SDK and authentication

## Role

Let the local machine drive Google Cloud from the command line (`gcloud`, `bq`) and let Python scripts access Cloud Storage and BigQuery, with no key file in the project.

## Installation (Ubuntu / Debian, official APT repository)

```bash
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates gnupg curl
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
sudo apt-get update && sudo apt-get install google-cloud-cli
```

Installed version: Google Cloud SDK 586.0.0 (includes `gcloud`, `bq`, `gsutil`).

Update: `sudo apt-get update && sudo apt-get install --only-upgrade google-cloud-cli`

## Authentication

Two separate logins:

1. **For the command line**: `gcloud init`
   Signs in to the Google account and selects the project `prc-data-challenge-2025`.
2. **For Python scripts**: `gcloud auth application-default login`
   Stores credentials in `~/.config/gcloud/application_default_credentials.json`, which every Google library finds automatically (Application Default Credentials).
   If a warning mentions a "quota project":
   `gcloud auth application-default set-quota-project prc-data-challenge-2025`

## Why not a service account key file

A JSON key file gives permanent access to the project. If it sits in the project folder, it easily ends up on GitHub. Application Default Credentials stay outside the repo, in the user's configuration. Google advises against service account keys for local development.

**Rule: no credentials, tokens or key files in the repo.**

## Checks

```bash
gcloud --version                                  # installed version
gcloud config list                                # active account and project
gcloud storage ls                                 # should show gs://prc2025/
gcloud auth application-default print-access-token   # a token = Python credentials OK
```
