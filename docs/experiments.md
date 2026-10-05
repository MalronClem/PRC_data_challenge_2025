# Experiments

Log of the models I tried, one row per run. Scores are RMSE in kg, and two scores can only be compared if they come from the same evaluation set.

## Evaluation sets

- `val`: 20% of the train flights, drawn at random with `random_state=42`. Outlier flights are kept in it, since the test sets are noisy too. It covers the same months as training, so it says nothing about how the model holds up on later months.
- `rank`: the phase 1 test set (September 2025, 1,888 flights). Its true `fuel_kg` was published after the challenge.
- `final`: the phase 2 test set (October 2025, 2,836 flights). The official ranking was computed on rank and final together. I'll only score on it once, at the very end.

For reference, the winning team got 200.83 kg on the final ranking (then 211.99 and 219.85).

## Cleaning

Unless a row says otherwise, the 385 flights in `bad_flights` are removed from the training data (not from `val`). They are the 205 flights whose average fuel rate is a far-out value for their aircraft type, plus 189 flights with an interval starting or ending more than 30 min away from the flight. Details in the [baseline notebook](../notebooks/baseline.ipynb).

## Results

| # | Date | Training data | Features | Model | Parameters | val | rank | final | Commit | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 2026-10-05 | `fit`, cleaned | `aircraft_type`, `duration_s` | median fuel rate of the type × duration | global median rate for unknown types | 330 | | | 90442f3 | First reference. Same score without cleaning (329.9), the median doesn't care about extremes |
| 2 | 2026-10-05 | `fit`, cleaned | `aircraft_type`, `duration_s`, `since_takeoff_s`, `before_landing_s` | LightGBM | defaults, `random_state=42` | 299 | | | d5572cf | 9% better than #1 |
| 3 | 2026-10-05 | `fit`, not cleaned | same as #2 | LightGBM | same as #2 | 305 | | | d5572cf | Worse than #2, so the cleaning stays |

The very first baseline run gave 213, but outliers had also been removed from `val`, so that number isn't comparable and isn't in the table.

## Adding a row

- Commit first, so the row can point to the exact code.
- Change only one thing compared to an earlier row and say which one in the notes.
- Only list parameters that differ from the library defaults.
- Keep `random_state=42` everywhere.
