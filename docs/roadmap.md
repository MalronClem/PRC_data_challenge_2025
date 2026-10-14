# Roadmap

Where the project stands and what comes next. Scores for each step are in [`experiments.md`](experiments.md).

## Done

- Setup: tooling, data on GCS, BigQuery external tables.
- Exploration of every table, summed up in [`exploration.md`](exploration.md).
- Baseline without trajectory (median fuel rate of the type × duration), 330 kg on val.
- Pipeline in `src/prc_fuel/` (load, split, clean, features, train, evaluate, run), so train, rank and final go through the same code.
- Scores on rank and on val without outliers. Most of the val error comes from a few flights with a wrong fuel rate, and keeping them in training actually helps (run #8, [outliers notebook](../notebooks/outliers_error.ipynb)).

## Next, roughly in this order

1. Trajectory features: altitude, groundspeed, vertical rate and number of points per interval, computed in BigQuery.
2. OpenAP: a physics-based fuel estimate used as a feature. Mass is unknown, so we'll have to assume it.
3. Intervals without trajectory (~40%): try to fill them from other flights on the same route, or at least guess the flight phase.
4. Model: tune LightGBM (still on defaults), try CatBoost or XGBoost, maybe average a few models.
5. Check that the choices hold on later months (rank already does part of this).
6. Retrain on all of train, maybe rank too, and score once on final.

Features first because that's where new information comes in, the model choice should matter less.
