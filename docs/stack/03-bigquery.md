# 03 — BigQuery

## Rôle

Étape intermédiaire entre le stockage et la manipulation fine en Python (pandas, numpy).

BigQuery fait le travail lourd sur les millions de points de trajectoire (filtrer, joindre, agréger) directement là où sont les données. Python ne récupère qu'un tableau compact : environ une ligne par intervalle de carburant (131 530 lignes pour le train, de l'ordre de 30 Mo).

## Pourquoi ce choix

- Lit nativement les fichiers Parquet de Cloud Storage via des tables externes.
- Free tier permanent suffisant pour ce projet.
- Compétence SQL / data warehouse très demandée en data engineering.

## Configuration

**Statut** : créé le 2026-09-28. Les 12 tables fonctionnent.

- **Dataset** : `prc2025`, dans la région `us-central1`, la même que le bucket. C'est obligatoire pour que BigQuery puisse lire les fichiers du bucket. La région ne peut plus être changée ensuite.
- **Tables externes** : les données restent dans le bucket, BigQuery les lit directement. Rien n'est copié.
- **Noms des tables** : `<contenu>_<phase>`, par exemple `fuel_train`.
  - `airports` : les aéroports
  - `flights_train`, `flights_rank`, `flights_final` : les trajectoires, un fichier par vol
  - `fuel_train`, `fuel_rank`, `fuel_final` : le carburant brûlé par intervalle
  - `flightlist_train`, `flightlist_rank`, `flightlist_final` : une ligne par vol
  - `fuel_submit_rank`, `fuel_submit_final` : les fichiers à remplir pour le classement
- **Pour recréer les tables** : lancer [`sql/create_external_tables.sql`](../../sql/create_external_tables.sql) dans BigQuery. On peut le relancer sans risque, il ne touche pas aux données.

## Contrôles faits

- `fuel_train` : 131 530 lignes, comme annoncé.
- Trajectoires : 123 587 596 points (train), 24 227 539 (rank), 37 877 494 (final). Aucune erreur, donc tous les fichiers sont lisibles.

## Contenu des tables

- `fuel_*` : l'identifiant du vol (`flight_id`), le début et la fin de l'intervalle (`start`, `end`) et le carburant brûlé en kg (`fuel_kg`). C'est `fuel_kg` qu'il faut prédire.
- `flights_*` : pour chaque point du vol, l'heure (`timestamp`), la position, l'altitude, les vitesses et le type d'avion.
- `start`, `end` et `timestamp` sont des entiers en **nanosecondes** depuis 1970 (UTC). Voir [`docs/exploration.md`](../exploration.md) (en anglais).

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
