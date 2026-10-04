# 03 — BigQuery

## Role

Intermediate step between storage and fine-grained work in Python (pandas, numpy).

BigQuery does the heavy work on the millions of trajectory points (filter, join, aggregate) right where the data lives. Python only fetches a compact table: about one row per fuel interval (131,530 rows for train, around 30 MB).

## Why this choice

- Natively reads Parquet files from Cloud Storage through external tables.
- Permanent free tier, enough for this project.
- SQL / data warehouse skills are in high demand in data engineering.

## Configuration

**Status**: created on 2026-09-28. All 12 tables work.

- **Dataset**: `prc2025`, in region `us-central1`, the same as the bucket. This is required for BigQuery to read the bucket's files. The region cannot be changed afterwards.
- **External tables**: the data stays in the bucket and BigQuery reads it directly. Nothing is copied.
- **Table names**: `<content>_<phase>`, e.g. `fuel_train`.
  - `airports`: the airports
  - `flights_train`, `flights_rank`, `flights_final`: trajectories, one file per flight
  - `fuel_train`, `fuel_rank`, `fuel_final`: fuel burnt per interval
  - `flightlist_train`, `flightlist_rank`, `flightlist_final`: one row per flight
  - `fuel_submit_rank`, `fuel_submit_final`: the files to fill in for the ranking
- **To recreate the tables**: run [`sql/create_external_tables.sql`](../../sql/create_external_tables.sql) in BigQuery. It is safe to re-run, it never touches the data.

## Checks done

- `fuel_train`: 131,530 rows, as announced.
- Trajectories: 123,587,596 points (train), 24,227,539 (rank), 37,877,494 (final). No error, so every file is readable.

## Table content

- `fuel_*`: flight id (`flight_id`), interval start and end (`start`, `end`) and fuel burnt in kg (`fuel_kg`). `fuel_kg` is the target.
- `flights_*`: for each point of the flight, the time (`timestamp`), position, altitude, speeds and aircraft type.
- `start`, `end` and `timestamp` are integers in **nanoseconds** since 1970 (UTC). See [`docs/exploration.md`](../exploration.md).

## SQL / Python split (to refine)

- BigQuery side: joins (aircraft type from the flightlist, trajectory points between each interval's `start` and `end`).
- Python side: OpenAP estimate, modelling.
- Open points: aggregations, interval duration, interpolation of missing values.

## Costs and limits (free tier)

- 1 TiB of queries per month
- 10 GiB of storage per month
- Loading data from Cloud Storage or a local file: free
- Beyond that: billed per byte **scanned** by queries

Known pitfalls:

- By default, BigQuery storage is billed on the **uncompressed** size of the data ("logical" billing). The 4.9 GB of compressed Parquet could exceed 10 GiB once loaded into native tables. Hence the choice of external tables.
- On external Parquet tables, `LIMIT` and `WHERE` do not reduce the bytes read: only the selected columns do (columnar format). Avoid `SELECT *` on `flights_*`.
- BigQuery does not read zip archives.
- BigQuery does not read Cloudflare R2.
