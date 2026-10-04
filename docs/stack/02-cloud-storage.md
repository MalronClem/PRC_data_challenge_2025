# 02 — Cloud Storage

## Role

Object storage for the project. Source of truth for the data in the cloud:

- `raw/` zone: the challenge data as published, never modified;
- `processed/` zone: data produced by the project (feature table, etc.).

## Why this choice

- **Cloudflare R2 ruled out**: more generous free offer (10 GB, no egress fees), but BigQuery cannot read R2 (only Cloud Storage, Amazon S3 and Azure Blob Storage). The data would have had to be copied.
- **Cloud Storage chosen**: BigQuery natively reads Parquet files in a bucket through external tables. A consistent stack, common in industry.

## Bucket configuration

| Setting | Value | Reason |
|---|---|---|
| Name | `gs://prc2025` | Globally unique |
| Location type | Region | The free tier only applies to single US regions |
| Region | `us-central1` | Free tier limited to us-central1, us-east1, us-west1 |
| Storage class | Standard | Only class covered by the free tier |
| Public access | Blocked (prevention enabled) | No reason to expose the data |
| Access control | Uniform | Permissions managed at bucket level, simpler |
| Hierarchical namespace | Disabled | Irreversible option, not needed here |
| Rapid Cache | Disabled | Extra service, not needed for this volume |
| Soft delete | Disabled | Otherwise a deleted file stays billed for 7 days. The data is on Zenodo anyway |

**Status**: data uploaded on 2026-09-28. 15,771 files, 4.6 GB. File count checked.

## Layout

```
gs://prc2025/
  raw/
    readme.txt
    airports.parquet
    train/
      flightlist.parquet
      fuel.parquet
      flights/          (11,037 files, one per flight)
    rank/
      flightlist.parquet
      fuel.parquet
      fuel_submit.parquet
      flights/          (1,888 files)
    final/
      flightlist.parquet
      fuel.parquet
      fuel_submit.parquet
      flights/          (2,836 files)
  processed/
```

- One folder per phase: the same code works for all three, only the phase name changes.
- `rank/` and `final/` are for final evaluation: **do not use them during development**.
- No zip files in the bucket: the reference raw source stays Zenodo, immutable and downloadable again.

## Data source

- Dataset: Zenodo, https://doi.org/10.5281/zenodo.19184661 (CC BY 4.0 licence)
- Total size: 4.9 GB (flights_train.zip 3.3 GB, flights_rank.zip 631.7 MB, flights_final.zip 982.8 MB, the rest < 4 MB per file)
- Each file has an MD5 checksum on the Zenodo page: checked on 2026-09-28 with `md5sum -c`, all 13 files are fine.

## Useful commands

```bash
gcloud storage ls gs://prc2025/                 # list content
gcloud storage ls -r gs://prc2025/raw/train/    # list recursively
gcloud storage du -s gs://prc2025/              # total size
gcloud storage cp -r <local_folder> gs://prc2025/raw/train/   # upload a folder
gcloud storage rsync <local_folder> gs://prc2025/raw --recursive   # sync (resumes if interrupted)
```

## Costs and limits (free tier)

- 5 GB-months of Standard storage, US regions only
- 5,000 class A operations (writes, listings) per month
- 50,000 class B operations (reads) per month
- 100 GB of egress from North America per month

Estimates for this project:

- Uploading the 15,761 trajectory files one by one: ~15,761 class A operations, about $0.05 beyond the quota.
- Reading the whole train set once: 11,037 class B operations, i.e. ~4 free full reads per month.
- Each full read of the dataset from the local machine uses ~4.9 GB of the egress quota.
