# Experiments

Log of the models I tried, one row per run. Scores are RMSE in kg, and two scores can only be compared if they come from the same evaluation set.

## Evaluation sets

- `val`: 20% of the train flights, drawn at random with `random_state=42`. Outlier flights are kept in it, since the test sets are noisy too. It covers the same months as training, so it says nothing about how the model holds up on later months.
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

The very first baseline run gave 213, but outliers had also been removed from `val`, so that number isn't comparable and isn't in the table.

Runs from #4 on can be replayed with `run.py` (it was `train.py` before 9cc5d5c), but only from the commit of the row since the cleaning changed in #8:

```bash
uv run python -m prc_fuel.run --features duration_s aircraft_type since_takeoff_s before_landing_s   # 4
uv run python -m prc_fuel.run --features duration_s aircraft_type                                    # 5
uv run python -m prc_fuel.run                                                                        # 8
```

## Adding a row

- Commit first, so the row can point to the exact code.
- Change only one thing compared to an earlier row and say which one in the notes.
- Only list parameters that differ from the library defaults.
- Keep `random_state=42` everywhere.
