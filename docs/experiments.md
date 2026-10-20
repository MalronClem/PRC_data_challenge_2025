# Experiments

Log of the models I tried, one row per run. Scores are RMSE in kg, and two scores can only be compared if they come from the same evaluation set.

## Evaluation sets

- `val`: 20% of the train flights, drawn at random with `random_state=42`. Outlier flights are kept in it, since the test sets are noisy too. It covers the same months as training, so it says nothing about how the model holds up on later months.
- From run #16 on, some runs use a time split instead (`--split time`): the last 20% of flights to take off go to `val` (from ~11 July), the rest to training, like rank comes after train. It has far fewer outlier flights than the random `val`, so its scores are much lower and can't be compared with the random split rows. Rows say which split they use.
- `clean val`: `val` without its outlier flights, both kinds (`clean_all`). It stays the same whatever the training cleaning is. It isn't used to pick models, since the test sets aren't clean. It only says whether a gain comes from normal flights or from outliers.
- `rank`: the phase 1 test set (September 2025, 1,888 flights). Its true `fuel_kg` was published after the challenge.
- `final`: the phase 2 test set (October 2025, 2,836 flights). The official ranking was computed on rank and final together. I'll only score on it once, at the very end.

For reference, the winning team got 200.83 kg on the final ranking (then 211.99 and 219.85).

## Cleaning

Up to row 7, the 385 flights in `bad_flights` are removed from the training data (not from `val`). They are the 205 flights whose average fuel rate is a far-out value for their aircraft type, plus 189 flights with an interval starting or ending more than 30 min away from the flight. Details in the [baseline notebook](../notebooks/baseline.ipynb).

From row 8 on, only the flights with an interval far from the flight are removed (`clean_training`). The fuel rate outliers make most of the val error but taking them out of training made the model predict too low, see the [outliers notebook](../notebooks/outliers_error.ipynb).

## Results

| # | Date | Training data | Features | Model | Parameters | val | clean val | rank | final | Commit | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 2026-10-05 | `fit`, cleaned | `aircraft_type`, `duration_s` | median fuel rate of the type × duration | global median rate for unknown types | 330 |  | | | 90442f3 | First reference. Same score without cleaning (329.9), the median doesn't care about extremes |
| 2 | 2026-10-05 | `fit`, cleaned | `aircraft_type`, `duration_s`, `since_takeoff_s`, `before_landing_s` | LightGBM | defaults, `random_state=42` | 299 |  | | | d5572cf | 9% better than #1 |
| 3 | 2026-10-05 | `fit`, not cleaned | same as #2 | LightGBM | same as #2 | 305 |  | | | d5572cf | Worse than #2, so the cleaning stays |
| 4 | 2026-10-05 | `fit`, cleaned | same as #2 | LightGBM | same as #2 | 299.7 |  | | | 6394943 | Same as #2 but through the pipeline (`train.py`). Cleaning is now computed on `fit` only, hence 102,065 intervals instead of 102,001 |
| 5 | 2026-10-05 | `fit`, cleaned | `duration_s`, `aircraft_type` | LightGBM | same as #2 | 327.9 |  | | | 6394943 | Without the two flight phase features we're back to the baseline level: they bring the whole gain of #4 |
| 6 | 2026-10-14 | `fit`, cleaned | #4 + `flight_duration_s`, `flight_progress`, `origin_icao`, `destination_icao`, `origin_elevation`, `dest_elevation`, `day_of_week`, `hour` | LightGBM | same as #2 | 297.6 |  | | | b8d6f68 | Only 2 kg better than #4. Flight duration is the sum of `since_takeoff_s`, `duration_s` and `before_landing_s`, so it's mostly redundant, and the airport and time features add little on their own |
| 7 | 2026-10-14 | `fit`, cleaned | same as #6 | LightGBM | same as #2 | 297.6 | 145.9 | 255.1 | | 9cc5d5c | Same model as #6, first time scored on clean val and rank. Removing the outliers from `val` halves the error, so about half of the val score comes from a few flights. Rank sits in between, it probably has fewer outliers than `val` |
| 8 | 2026-10-14 | `fit`, off-flight intervals removed only | same as #6 | LightGBM | same as #2 | 293.8 | 167.0 | 250.7 | | d327755 | Fuel rate outliers kept in training. Better on val and rank, worse on clean val: the model predicts a bit higher for everyone, so it loses on normal flights but gains more on the big outliers. Keeping nothing out at all gave 297.0 / 248.0 in the notebook |
| 9 | 2026-10-14 | same as #8 | #6 + `route_distance` | LightGBM | same as #2 | 294.0 | 165.7 | 248.6 | | a956a0d | Great circle distance between the airports. Small gain on clean val and rank, nothing on val. Probably close to `flight_duration_s`, which the model already had |
| 10 | 2026-10-16 | same as #8, impossible trajectory values set to NaN on every set | #9 + `n_points`, `avg_altitude`, `alt_start`, `alt_end`, `avg_groundspeed`, `avg_vertical_rate`, `avg_mach` | LightGBM | same as #2 | 292.3 | 164.4 | 242.7 | | 4105cd2 | Per interval trajectory summary from BigQuery. Thresholds come from gaps in the data ([trajectory notebook](../notebooks/trajectory_features.ipynb)), only 86 values masked. Biggest gain on rank (-5.9). Modest overall, probably because ~40% of intervals have almost no trajectory and the flight phase features already gave climb / cruise / descent |
| 11 | 2026-10-16 | same as #10 | #10 + `implied_vr` | LightGBM | same as #2 | 294.2 | 166.0 | 242.6 | | 4c38c14 | Rate implied by the altitude change, `(alt_end - alt_start) / duration`. Nothing gained, the 1-2 kg differences are noise. The model could already get climb and descent from `alt_start`, `alt_end` and `duration_s` |
| 12 | 2026-10-16 | same as #10 | #11 without `avg_vertical_rate` | LightGBM | same as #2 | 293.2 | 163.9 | 243.9 | | 4c38c14 | Same level as #10 and #11, so `avg_vertical_rate` brings nothing either. Kept as the reference: same score, and `implied_vr` follows the cleaned altitudes while `avg_vertical_rate` is wrong on some flights. Replayed with `--drop` from the next commit on |
| 13 | 2026-10-16 | same as #10, boundary positions set to NaN when they imply more than 800 kt | #12 + `interval_distance` | LightGBM | same as #2 | 295.0 | 163.8 | 241.2 | | d370cfe | Great circle distance between the first and last position of the interval. Mostly useful on the ~32% of intervals without groundspeed, which only have the two acars boundary points. Those positions are a few minutes off in time, so 654 intervals of a few seconds were masked ([trajectory notebook](../notebooks/trajectory_features.ipynb)). Best rank so far, val a bit worse. Kept, rank being the more honest test |
| 14 | 2026-10-18 | same as #13 | #13 + `openap_fuel` | LightGBM | same as #2 | 298.0 | 169.5 | 242.6 | | baaa20b | OpenAP fuel flow times duration, with a mass going linearly from mtow to mlw over the flight and the airspeed from mach, else groundspeed, else the distance between the bounds ([OpenAP notebook](../notebooks/openap.ipynb)). Spearman 0.93 with `fuel_kg`, but that comes from duration and aircraft size, which the model already had: within a type the fuel rates only match at 0.35-0.6. Worse everywhere, not kept |
| 15 | 2026-10-18 | same as #13 | same as #13 | LightGBM | `learning_rate=0.05`, `n_estimators=160`, `num_leaves=127` | 288.1 | 157.0 | 247.3 | | 33e6ce1 | Parameters tuned on val with early stopping ([tuning notebook](../notebooks/model_tuning.ipynb)): more leaves was better on val and clean val, a smaller learning rate wasn't. But rank gets 6 kg worse. val flights are drawn at random from the same months as fit and have very close flights in it, bigger trees learn those details, which don't carry over to September. Not kept, tuning needs a time-based validation |
| 16 | 2026-10-18 | time split, rest same as #13 | same as #13 | LightGBM | same as #13 | 188.0 | 159.5 | 250.4 | | 774182d | #13 with the time split. Rank is ~9 kg worse than #13 without the mid-July to August flights, recent data matters. Reference for the time split |
| 17 | 2026-10-18 | time split | same as #13 | LightGBM | `learning_rate=0.05`, `n_estimators=75`, `num_leaves=127`, `min_child_samples=100` | 175.8 | 146.6 | 243.5 | | 774182d | Parameters tuned on the time split ([tuning notebook](../notebooks/model_tuning.ipynb)). Over 12 configs, val and rank rank them almost the same way (Spearman 0.94), unlike the random val. The difference with #15 is mostly `min_child_samples` 100 instead of 20. -12 kg on val and -7 on rank against #16. Kept as the new defaults |
| 18 | 2026-10-18 | same as #8 (random split) | same as #13 | LightGBM | same as #17 | 298.0 | 156.8 | 241.9 | | 774182d | #17's parameters with the random split, to compare with #13. Rank doesn't move, clean val is 7 kg better and val 3 kg worse: leaves of at least 100 intervals smooth out the outlier flights. No clear reason why the rank gain of #17 disappears here |
| 19 | 2026-10-20 | time split | same as #13 | XGBoost | `enable_categorical=True`, rest default | 205.4 | 179.4 | 264.4 | | ab4ebd1 | Worse than LightGBM with its defaults (#16) everywhere. Its defaults are more aggressive (learning rate 0.3, no minimum leaf size) and in a test its error on fit was ~110 kg against 205 on val, so it overfits. Airports never seen in fit are set to NaN before predicting: putting them in a new "unknown" category instead gave 303 on val |
| 20 | 2026-10-20 | time split | same as #13 | CatBoost | defaults (1,000 trees) | 187.1 | 159.6 | 238.1 | | ab4ebd1 | Same val as LightGBM with defaults (#16) but best rank so far, 5 kg better than tuned LightGBM (#17) without any tuning. On val tuned LightGBM is still 11 kg better though, so val and rank disagree here. Needs tuning on the time split before comparing |
| 21 | 2026-10-20 | time split | same as #13 | LightGBM + CatBoost, plain average | LightGBM as #17, CatBoost `depth=10`, `l2_leaf_reg=3`, `learning_rate=0.05`, 226 trees | 170.0 | 141.4 | 238.6 | | 491bb87 | CatBoost tuned on the time split ([tuning notebook](../notebooks/model_tuning.ipynb)): best 179.6 on val, still behind LightGBM, but better on rank (241.3), and val and rank only agree at 0.59 over its grid. The average of the two beats both on val and rank, U shape over the weight, 0.5 best on val. -5.8 kg on val and -4.9 on rank against #17. New reference |
| 22 | 2026-10-20 | time split | #13 + `airspeed_kt` | LightGBM + CatBoost, plain average | same as #21 | 169.9 | 141.1 | 239.2 | | 8fa0e87 | One speed column filled for ~96% of intervals: true airspeed from mach, else groundspeed, else distance between the bounds over duration. `avg_groundspeed` alone is missing on 35%. Noise level everywhere (-0.1 on val, +0.6 on rank), the model already got the speed from `interval_distance` and `duration_s`. Not kept, dropped with `--drop` |
| 23 | 2026-10-20 | time split | same as #13 | LightGBM + CatBoost, plain average, fuel rate target | same as #21 | 167.7 | 141.2 | 234.1 | | d9cf264 | Learns `fuel_kg / duration_s` and multiplies back by the duration (`--target rate`). Better than #21 on val and rank, but worse than CatBoost alone (#25), LightGBM pulls it down |
| 24 | 2026-10-20 | time split | same as #13 | LightGBM, fuel rate target | same as #17 | 184.9 | 161.1 | 249.0 | | d9cf264 | 9 kg worse than predicting the fuel (#17). Not the number of trees, early stopping stops at 72 and gives 184.5. Probably because every interval weighs the same when learning the rate, while the RMSE in kg weighs long intervals much more |
| 25 | 2026-10-20 | time split | same as #13 | CatBoost, fuel rate target | same as #21 | 162.6 | 134.4 | 232.9 | | d9cf264 | Best so far everywhere: -7.4 on val, -7.0 on clean val and -5.7 on rank against the blend (#21). Trees don't have to learn the product rate × duration any more. Tested off-pipeline: weighting intervals by their duration or duration² (so the loss matches the RMSE in kg) is worse for both models (CatBoost 164.7 / 240.2 and 174.0 / 247.8 on val / rank), and averaging with LightGBM on the fuel target gains only ~1.4 kg on val (161.2 with weight 0.25), noise level |
| 26 | 2026-10-20 | all of train, cleaned (`--final`) | same as #13 | CatBoost, fuel rate target | same as #25 | | | 233.2 | 213.7 | 4a8fd33 | Final run, model fixed in the roadmap before looking. Rank + final together (how the official ranking was computed): 221.6. Training on all of train instead of the time fit doesn't change rank (232.9 in #25) |

The very first baseline run gave 213, but outliers had also been removed from `val`, so that number isn't comparable and isn't in the table.

Runs from #4 on can be replayed with `run.py` (it was `train.py` before 9cc5d5c), but only from the commit of the row since the cleaning changed in #8:

```bash
uv run python -m prc_fuel.run --features duration_s aircraft_type since_takeoff_s before_landing_s   # 4
uv run python -m prc_fuel.run --features duration_s aircraft_type                                    # 5
uv run python -m prc_fuel.run                                                                        # 11
uv run python -m prc_fuel.run --drop avg_vertical_rate openap_fuel                                 # 13
uv run python -m prc_fuel.run --drop avg_vertical_rate                                             # 14
uv run python -m prc_fuel.run --drop avg_vertical_rate openap_fuel --split time                    # 17
uv run python -m prc_fuel.run --drop avg_vertical_rate openap_fuel                                 # 18
uv run python -m prc_fuel.run --drop avg_vertical_rate openap_fuel --model xgboost                 # 19
uv run python -m prc_fuel.run --drop avg_vertical_rate openap_fuel --model catboost                # 20
uv run python -m prc_fuel.run --drop avg_vertical_rate openap_fuel --model blend                   # 21
uv run python -m prc_fuel.run --drop avg_vertical_rate openap_fuel --model blend                   # 22
uv run python -m prc_fuel.run --drop avg_vertical_rate openap_fuel airspeed_kt --model blend --target rate      # 23
uv run python -m prc_fuel.run --drop avg_vertical_rate openap_fuel airspeed_kt --model lightgbm --target rate   # 24
uv run python -m prc_fuel.run --drop avg_vertical_rate openap_fuel airspeed_kt --model catboost --target rate   # 25
uv run python -m prc_fuel.run --drop avg_vertical_rate openap_fuel airspeed_kt --model catboost --target rate --final   # 26
```

From the commit after #18 on, `--split time` is the default, so the random split has to be asked for with `--split random`.

From #21 on, `--model catboost` uses the tuned parameters (`CATBOOST_PARAMS` in `train.py`), so #20 with CatBoost's own defaults only replays from its commit.

From #22 on `airspeed_kt` is in the registry, so the reference (#21) is replayed with `--drop avg_vertical_rate openap_fuel airspeed_kt --model blend`.

## Adding a row

- Commit first, so the row can point to the exact code.
- Change only one thing compared to an earlier row and say which one in the notes.
- Only list parameters that differ from the library defaults.
- Keep `random_state=42` everywhere.
