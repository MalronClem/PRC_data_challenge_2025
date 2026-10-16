# Roadmap

Where the project stands and what comes next. Scores for each step are in [`experiments.md`](experiments.md).

## Done

- Setup: tooling, data on GCS, BigQuery external tables.
- Exploration of every table, summed up in [`exploration.md`](exploration.md).
- Baseline without trajectory (median fuel rate of the type × duration), 330 kg on val.
- Pipeline in `src/prc_fuel/` (load, split, clean, features, train, evaluate, run), so train, rank and final go through the same code.
- Scores on rank and on val without outliers. Most of the val error comes from a few flights with a wrong fuel rate, and keeping them in training actually helps (run #8, [outliers notebook](../notebooks/outliers_error.ipynb)).
- Route distance (great circle between the two airports, haversine). Available for every flight, even without trajectory.
- Trajectory features per interval, computed in BigQuery: number of points, altitudes, groundspeed, mach, and the distance between the first and last position. Impossible values are set to NaN, with thresholds taken from gaps in the data ([trajectory notebook](../notebooks/trajectory_features.ipynb)). The averaged `vertical_rate` didn't match the altitude change (correlation 0.42) and was dropped, the rate implied by the altitudes brought nothing either. Rank went from 248.6 to 241.2 (runs #10 to #13).

## Next, roughly in this order

1. OpenAP: a physics-based fuel estimate used as a feature. Mass is unknown, so we'll have to assume it.
2. Intervals without trajectory (~40%): try to fill them from other flights on the same route, or at least guess the flight phase.
3. Better cleaning: for now bad feature values are set to NaN and flights with a wrong target are dropped. Some could be replaced with real values instead, like the nearest valid altitude point instead of a bad one on the bound (directly in the SQL), groundspeed recomputed from positions, or mach estimated from groundspeed. To be checked with a run, an approximate value isn't always better than NaN.
4. Model: tune LightGBM (still on defaults), try CatBoost or XGBoost, maybe average a few models.
5. Check that the choices hold on later months (rank already does part of this).
6. Retrain on all of train, maybe rank too, and score once on final.

Features first because that's where new information comes in, the model choice should matter less.
