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

## Next, roughly in this order

1. Mass from the trajectory. Both masses we assumed (from flight progress, then from route distance) were built from columns the model already had, so they couldn't add anything. The mass changes the fuel rate a lot and none of our features really says it. Where the data could show it is the climb: at the same thrust a heavier plane climbs slower, so comparing the real vertical rate with what OpenAP's thrust and drag allow should give the mass back. That needs the trajectory points of the climb, not the interval averages.
2. Intervals without trajectory: the ~40% from the exploration still have their two acars boundary points, so only ~2% have neither altitude nor speed now (and ~2% only one of them, [trajectory notebook](../notebooks/trajectory_features.ipynb)). Worth doing only if the error on those turns out big: fill them from other flights on the same route, or guess the flight phase.
3. Better cleaning: for now bad feature values are set to NaN and flights with a wrong target are dropped. Some could be replaced with real values instead, like the nearest valid altitude point instead of a bad one on the bound (directly in the SQL), groundspeed recomputed from positions, or mach estimated from groundspeed. To be checked with a run, an approximate value isn't always better than NaN.
4. Try other models (CatBoost, XGBoost) or average a few, judged on the time split.
5. Retrain on all of train and score once on final. Not on rank: its fuel was hidden during the challenge (set to 0), so a model trained on it would have an unfair advantage and its final score couldn't be compared with the teams. Recent data does seem to matter though (training up to mid-July instead of August costs ~9 kg on rank), so a separate run with rank included could show how much, labelled as not comparable.

Mass first, since the runs so far show that features built from what the model already knows don't help, only new information does. Every choice is now judged on the time split, rank is only a check.
