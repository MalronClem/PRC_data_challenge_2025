# 02 — Cloud Storage

## Rôle

Stockage objet du projet. Source de vérité des données dans le cloud :

- zone `raw/` : les données du challenge telles que publiées, jamais modifiées ;
- zone `processed/` : les données produites par le projet (tableau de features, etc.).

## Pourquoi ce choix

- **Cloudflare R2 écarté** : offre gratuite plus généreuse (10 Go, sans frais de sortie), mais BigQuery ne sait pas lire R2 (seulement Cloud Storage, Amazon S3 et Azure Blob Storage). Il aurait fallu copier les données.
- **Cloud Storage retenu** : BigQuery lit nativement les fichiers Parquet d'un bucket via des tables externes. Stack homogène et courante en entreprise.

## Configuration du bucket

| Paramètre | Valeur | Raison |
|---|---|---|
| Nom | `gs://prc2025` | Unique au niveau mondial |
| Type d'emplacement | Region | Le free tier ne s'applique qu'en mono-région US |
| Région | `us-central1` | Free tier limité à us-central1, us-east1, us-west1 |
| Classe de stockage | Standard | Seule classe couverte par le free tier |
| Accès public | Bloqué (protection activée) | Aucune raison d'exposer les données |
| Contrôle d'accès | Uniforme | Droits gérés au niveau du bucket, plus simple |
| Espace de noms hiérarchique | Désactivé | Option irréversible, inutile ici |
| Rapid Cache | Désactivé | Service supplémentaire, inutile pour ce volume |
| Suppression réversible (soft delete) | Désactivée | Sinon, un fichier supprimé reste facturé 7 jours. Les données sont de toute façon sur Zenodo |

**Statut** : données envoyées le 2026-09-28. 15 771 fichiers, 4,6 Go. Le nombre de fichiers a été vérifié.

## Arborescence

```
gs://prc2025/
  raw/
    readme.txt
    airports.parquet
    train/
      flightlist.parquet
      fuel.parquet
      flights/          (11 037 fichiers, un par vol)
    rank/
      flightlist.parquet
      fuel.parquet
      fuel_submit.parquet
      flights/          (1 888 fichiers)
    final/
      flightlist.parquet
      fuel.parquet
      fuel_submit.parquet
      flights/          (2 836 fichiers)
  processed/
```

- Un dossier par phase : le même code fonctionne pour les trois, seul le nom de phase change.
- `rank/` et `final/` servent d'évaluation finale : **ne pas les utiliser pendant le développement**.
- Pas de zips dans le bucket : la source brute de référence reste Zenodo, immuable et re-téléchargeable.

## Source des données

- Dataset : Zenodo, https://doi.org/10.5281/zenodo.19184661 (licence CC BY 4.0)
- Taille totale : 4,9 Go (flights_train.zip 3,3 Go, flights_rank.zip 631,7 Mo, flights_final.zip 982,8 Mo, le reste < 4 Mo par fichier)
- Chaque fichier a une empreinte MD5 sur la page Zenodo : vérifiée le 2026-09-28 avec `md5sum -c`, les 13 fichiers sont bons.

## Commandes utiles

```bash
gcloud storage ls gs://prc2025/                 # lister le contenu
gcloud storage ls -r gs://prc2025/raw/train/    # lister récursivement
gcloud storage du -s gs://prc2025/              # taille totale
gcloud storage cp -r <dossier_local> gs://prc2025/raw/train/   # envoyer un dossier
gcloud storage rsync <dossier_local> gs://prc2025/raw --recursive   # synchroniser (reprend si interrompu)
```

## Coûts et limites (free tier)

- 5 Go-mois de stockage Standard, régions US uniquement
- 5 000 opérations de classe A (écritures, listings) par mois
- 50 000 opérations de classe B (lectures) par mois
- 100 Go de transfert sortant depuis l'Amérique du Nord par mois

Estimations pour ce projet :

- Déposer les 15 761 fichiers de trajectoires un par un : ~15 761 opérations de classe A, soit environ 0,05 $ au-delà du quota.
- Lire tout le train une fois : 11 037 opérations de classe B, soit ~4 lectures complètes gratuites par mois.
- Chaque lecture complète du dataset depuis la machine locale consomme ~4,9 Go du quota de transfert sortant.
