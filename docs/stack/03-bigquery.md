# 03 — BigQuery

## Rôle

Étape intermédiaire entre le stockage et la manipulation fine en Python (pandas, numpy).

BigQuery fait le travail lourd sur les millions de points de trajectoire (filtrer, joindre, agréger) directement là où sont les données. Python ne récupère qu'un tableau compact : environ une ligne par intervalle de carburant (131 530 lignes pour le train, de l'ordre de 30 Mo).

## Pourquoi ce choix

- Lit nativement les fichiers Parquet de Cloud Storage via des tables externes.
- Free tier permanent suffisant pour ce projet.
- Compétence SQL / data warehouse très demandée en data engineering.

## Configuration

**Statut** : créé le 2026-09-28, 12 tables externes, toutes lisibles.

- **Dataset** : `prc-data-challenge-2025.prc2025`, région `us-central1` (même région que le bucket, condition pour lire ses fichiers via des tables externes). L'emplacement d'un dataset ne peut plus être modifié après création.
- **Tables externes** (pas de tables natives) pointant vers les Parquet de `gs://prc2025/raw/`. Nommage `<contenu>_<phase>` :

| Table | Source | Lignes |
|---|---|---|
| `airports` | `airports.parquet` | |
| `flights_train` / `_rank` / `_final` | `<phase>/flights/*.parquet` (un fichier par vol) | 123 587 596 / 24 227 539 / 37 877 494 |
| `fuel_train` / `_rank` / `_final` | `<phase>/fuel.parquet` | 131 530 (train) |
| `flightlist_train` / `_rank` / `_final` | `<phase>/flightlist.parquet` | |
| `fuel_submit_rank` / `_final` | `<phase>/fuel_submit.parquet` | |

- **Script de création** : [`sql/create_external_tables.sql`](../../sql/create_external_tables.sql), idempotent (`CREATE OR REPLACE`) : le relancer ne remplace que les définitions de tables, jamais les données du bucket.
- **Vérification** : un `COUNT(*)` sur chaque table `flights_*` oblige BigQuery à ouvrir tous les fichiers. Aucune erreur, donc les schémas des fichiers de vol sont compatibles entre eux.

## Schémas observés

- `fuel_*` : `idx` (INTEGER), `flight_id` (STRING), `start`, `end` (INTEGER), `fuel_kg` (FLOAT, la cible).
- `flights_*` : `timestamp` (INTEGER), `flight_id`, `typecode`, `latitude`, `longitude`, `altitude`, `groundspeed`, `track`, `vertical_rate`, `mach`, `TAS`, `CAS` (FLOAT), `source` (STRING).
- **Point ouvert** : `start`, `end` et `timestamp` sont des entiers et non des dates. Leur unité (secondes, microsecondes, nanosecondes ?) est à vérifier avant de joindre les trajectoires aux intervalles.

## Répartition du travail SQL / Python (à affiner)

- Côté BigQuery : jointures (type d'avion depuis la flightlist, points de trajectoire compris entre `start` et `end` de chaque intervalle).
- Côté Python : estimation OpenAP, modélisation.
- Points ouverts : agrégations, durée des intervalles, interpolation des valeurs manquantes.

## Coûts et limites (free tier)

- 1 Tio de requêtes par mois
- 10 Gio de stockage par mois
- Chargement de données depuis Cloud Storage ou un fichier local : gratuit
- Au-delà : facturation par octet **scanné** par les requêtes

Pièges connus :

- Par défaut, le stockage BigQuery est facturé sur la taille **non compressée** des données (facturation « logique »). Les 4,9 Go de Parquet compressé pourraient dépasser 10 Gio une fois chargés en tables natives. D'où le choix des tables externes.
- BigQuery ne lit pas les archives zip.
- BigQuery ne lit pas Cloudflare R2.
