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
- OpenAP fuel estimate (fuel flow times duration, mass assumed from mtow to mlw over the flight). Spearman 0.93 with the fuel, but only because of duration and aircraft size, which the model already had: no gain (run #14, [OpenAP notebook](../notebooks/openap.ipynb)). Within a type the model already matches the real fuel rate better than OpenAP. A mass depending on route distance changed nothing either, all its inputs were already features.
- Time-based validation (`--split time`, last 20% of flights by takeoff in val). Tuning LightGBM on the random val made rank worse (run #15), because val flights have close flights in training. On the time split, val and rank order configs the same way (Spearman 0.94), so tuning is done there now: 127 leaves, at least 100 intervals per leaf, 75 trees at 0.05 (run #17, [tuning notebook](../notebooks/model_tuning.ipynb)).
- Mass from the climb ([climb mass notebook](../notebooks/climb_mass.ipynb)). About half the flights have a usable climb (first point under 3,000 ft, no gap over 5 min before 25,000 ft). The mass is the one that best matches the climb with OpenAP's climb thrust and drag. It comes out too light (often stuck at the empty weight) and very noisy: on the A359, flights of the same route get anything between ~140 and ~210 t, and within a route the estimated mass has no link with the fuel rate (Spearman -0.008). Most likely because we only have groundspeed, not airspeed, so the wind is mixed in, and because the thrust really used changes from flight to flight. Not added as a feature.
- Error on intervals without trajectory, measured on val_time with the reference model ([notebook](../notebooks/no_trajectory_error.ipynb)). Intervals under 0.5 points/s are a third of val and 69% of the squared error, but they are ~3 times bigger (long cruise legs) and relative to their fuel the error is the lowest (0.34 against 0.42 for dense ones). The 0.6% with no altitude and no speed at all are badly predicted but only 5% of the error, ~4 kg at best. Filling trajectories isn't worth it, not done.
- Other models, judged on the time split (runs #19 to #21, [tuning notebook](../notebooks/model_tuning.ipynb)). XGBoost with its defaults overfits and is worse everywhere (205.4 on val), not tuned. CatBoost tuned gets 179.6 on val, behind LightGBM, but is better on rank. The plain average of LightGBM and CatBoost beats both: 170.0 on val and 238.6 on rank, against 175.8 / 243.5 for LightGBM alone. It's the new reference (`--model blend`).

## Next, roughly in this order

1. Better cleaning: for now bad feature values are set to NaN and flights with a wrong target are dropped. Some could be replaced with real values instead, like the nearest valid altitude point instead of a bad one on the bound (directly in the SQL), groundspeed recomputed from positions, or mach estimated from groundspeed. To be checked with a run, an approximate value isn't always better than NaN. Few values are concerned (86 masked in run #10), so probably a small gain.
2. Retrain on all of train and score once on final. Not on rank: its fuel was hidden during the challenge (set to 0), so a model trained on it would have an unfair advantage and its final score couldn't be compared with the teams. Recent data does seem to matter though (training up to mid-July instead of August costs ~9 kg on rank), so a separate run with rank included could show how much, labelled as not comparable.

Every choice is judged on the time split, rank is only a check.

## Maybe later

- Wind for the climb mass. Public weather data (ERA5 for example) gives the wind by position, altitude and hour, so the airspeed could be rebuilt from the groundspeed and the mass computed again. It's a lot of work (big downloads, matching every climb point) and it may not be enough, since the reduced thrust would still be unknown. Not sure we'll do it. If we do, check first on the A359 whether flights of the same route get closer masses.
