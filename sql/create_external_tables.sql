-- External tables on the raw challenge data (gs://prc2025/raw/).
-- Dataset: prc-data-challenge-2025.prc2025 (location: us-central1).
-- Idempotent: safe to re-run, only table definitions are replaced, never the data.

-- Common
CREATE OR REPLACE EXTERNAL TABLE `prc-data-challenge-2025.prc2025.airports`
OPTIONS (format = 'PARQUET', uris = ['gs://prc2025/raw/airports.parquet']);

-- Train
CREATE OR REPLACE EXTERNAL TABLE `prc-data-challenge-2025.prc2025.flights_train`
OPTIONS (format = 'PARQUET', uris = ['gs://prc2025/raw/train/flights/*.parquet']);
CREATE OR REPLACE EXTERNAL TABLE `prc-data-challenge-2025.prc2025.fuel_train`
OPTIONS (format = 'PARQUET', uris = ['gs://prc2025/raw/train/fuel.parquet']);
CREATE OR REPLACE EXTERNAL TABLE `prc-data-challenge-2025.prc2025.flightlist_train`
OPTIONS (format = 'PARQUET', uris = ['gs://prc2025/raw/train/flightlist.parquet']);

-- Rank
CREATE OR REPLACE EXTERNAL TABLE `prc-data-challenge-2025.prc2025.flights_rank`
OPTIONS (format = 'PARQUET', uris = ['gs://prc2025/raw/rank/flights/*.parquet']);
CREATE OR REPLACE EXTERNAL TABLE `prc-data-challenge-2025.prc2025.fuel_rank`
OPTIONS (format = 'PARQUET', uris = ['gs://prc2025/raw/rank/fuel.parquet']);
CREATE OR REPLACE EXTERNAL TABLE `prc-data-challenge-2025.prc2025.flightlist_rank`
OPTIONS (format = 'PARQUET', uris = ['gs://prc2025/raw/rank/flightlist.parquet']);
CREATE OR REPLACE EXTERNAL TABLE `prc-data-challenge-2025.prc2025.fuel_submit_rank`
OPTIONS (format = 'PARQUET', uris = ['gs://prc2025/raw/rank/fuel_submit.parquet']);

-- Final
CREATE OR REPLACE EXTERNAL TABLE `prc-data-challenge-2025.prc2025.flights_final`
OPTIONS (format = 'PARQUET', uris = ['gs://prc2025/raw/final/flights/*.parquet']);
CREATE OR REPLACE EXTERNAL TABLE `prc-data-challenge-2025.prc2025.fuel_final`
OPTIONS (format = 'PARQUET', uris = ['gs://prc2025/raw/final/fuel.parquet']);
CREATE OR REPLACE EXTERNAL TABLE `prc-data-challenge-2025.prc2025.flightlist_final`
OPTIONS (format = 'PARQUET', uris = ['gs://prc2025/raw/final/flightlist.parquet']);
CREATE OR REPLACE EXTERNAL TABLE `prc-data-challenge-2025.prc2025.fuel_submit_final`
OPTIONS (format = 'PARQUET', uris = ['gs://prc2025/raw/final/fuel_submit.parquet']);
