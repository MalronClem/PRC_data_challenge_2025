import argparse
from pathlib import Path

import pandas as pd
from google.cloud import bigquery

CACHE_DIR = Path(__file__).resolve().parents[2] / "data"


def q(sql):
    client = bigquery.Client(project="prc-data-challenge-2025")
    return client.query(sql).to_dataframe()


def load(dataset, refresh=False):
    # BigQuery is only queried when the local copy is missing or refresh is asked.
    # Delete data/<dataset>.parquet (or use refresh) after changing the query.
    cache = CACHE_DIR / f"{dataset}.parquet"
    if cache.exists() and not refresh:
        return pd.read_parquet(cache)

    query = f"""
    SELECT
        TIMESTAMP_MICROS(DIV(f.start,1000)) as start,
        TIMESTAMP_MICROS(DIV(f.`end`,1000)) as `end`,
        f.idx,
        f.flight_id,
        f.fuel_kg,
        fl.aircraft_type,
        fl.takeoff,
        fl.landed,
        fl.origin_icao,
        fl.destination_icao,
        ao.longitude AS origin_longitude,
        ao.latitude AS origin_latitude,
        ao.elevation AS origin_elevation,
        ad.longitude AS dest_longitude,
        ad.latitude AS dest_latitude,
        ad.elevation AS dest_elevation
    FROM `prc-data-challenge-2025.prc2025.fuel_{dataset}` as f
    JOIN `prc-data-challenge-2025.prc2025.flightlist_{dataset}` as fl
        ON fl.flight_id = f.flight_id
    LEFT JOIN `prc-data-challenge-2025.prc2025.airports` as ao
    ON ao.icao = fl.origin_icao
    LEFT JOIN `prc-data-challenge-2025.prc2025.airports` as ad
    ON ad.icao = fl.destination_icao
    """
    df = q(query)
    CACHE_DIR.mkdir(exist_ok=True)
    df.to_parquet(cache)
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Load fuel intervals with flight info from BigQuery"
    )
    parser.add_argument("dataset", choices=["train", "rank", "final"])
    parser.add_argument(
        "--refresh", action="store_true", help="query BigQuery even if cached"
    )
    args = parser.parse_args()
    df = load(args.dataset, refresh=args.refresh)
    print("\n\n")
    print(df.shape, "\n")
    print(df.head())

    print("\n")
