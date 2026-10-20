# PRC Data Challenge 2025: fuel burn estimation

Predicting how much fuel an airliner burns over a given window of its flight, from its ADS-B trajectory, the flight list and the airports. This is the 2025 edition of the EUROCONTROL Performance Review Commission data challenge. I worked on it after the challenge closed, as a learning project, so the scores below are an after-the-fact evaluation and not an official entry.

## Results

Scores are RMSE in kg on the official test sets: September (`rank`), October (`final`), and both together, which is how the official ranking was computed.

| Model | rank | final | rank + final |
|---|---|---|---|
| Baseline: median fuel rate of the aircraft type × duration | 266.6 | 249.3 | 256.3 |
| CatBoost on the fuel rate (final model) | 233.2 | 213.7 | **221.6** |

The final model was fixed before looking at `final` and trained on all of `train` only. With 221.6 kg it would have been 6th of the 19 teams in the [official final ranking](https://ansperformance.eu/study/data-challenge/dc2025/outcome.html), which only keeps the teams that shared their code: between the 5th (221.25) and the 6th (227.14), the winner being at 200.83. Counting all 33 teams of the final phase, repository or not, it would have been 7th. The baseline alone (256.26) would have been 10th of the 19, 0.01 kg ahead of the team in 10th place (256.27). Two things make this comparison generous: the teams didn't know the fuel of `rank` or `final`, while I used `rank` as a check during the project (never for training), and I could read how the teams worked before trying some ideas (the mass from the climb comes from there).

![RMSE on rank over the runs](docs/figures/scores.png)

Each point is a run from the experiment log, blue when it became the reference, grey when it was tried and dropped. The jump at run #16 is the switch to the time split, which trains on the same number of flights but older ones (up to mid-July instead of all of April to August). The figure is made by `scripts/plot_scores.py` from `docs/experiments.md`.

A good part of the error comes from a few flights whose measured fuel rate is far off for their aircraft type. They are spotted from their fuel, which isn't known at prediction time, so the model can't single them out. Without them (and without the few flights with windows far outside the flight time) the error on the validation set drops from 162.6 to 134.4 kg.

## Approach

The full story with every run is in [`docs/experiments.md`](docs/experiments.md), and the order in which things were tried in [`docs/roadmap.md`](docs/roadmap.md). The main steps:

1. Exploration of every table ([`docs/exploration.md`](docs/exploration.md)). The target is fuel per time window, about 40% of the windows have almost no trajectory points, and ~2% of the flights have a fuel rate far out of the range of their aircraft type.
2. Baseline, then LightGBM on duration, aircraft type and position of the window in the flight.
3. Features per window computed in BigQuery: altitudes, speeds, mach, distance flown. Impossible values set to NaN, with thresholds taken from gaps in the data.
4. A time-based validation: the last 20% of flights by takeoff, like the test sets come after train. Tuning on a random split made the test score worse, probably because random validation flights have very close flights (same aircraft, route, week) in training. On the time split, validation and `rank` order the configurations the same way (Spearman 0.94 for LightGBM).
5. CatBoost, and above all learning the fuel rate (kg/s) instead of the fuel, then multiplying back by the duration. Trees can't multiply two columns, so this leaves the model only what changes the rate. With CatBoost it took 7.4 kg off on validation (170.0 to 162.6 against the LightGBM + CatBoost average) and 5.7 on `rank` (238.6 to 232.9).

What didn't work, each one measured before being dropped:

- OpenAP fuel flow as a feature: highly correlated with the fuel, but only through duration and aircraft size, which the model already had.
- Aircraft mass estimated from the climb (energy balance with OpenAP thrust and drag): about half the flights have a usable climb, but the mass comes out as noise: on the A359, flights of the same route get anything between ~140 and ~210 t, with no link to their fuel rate. Probably because groundspeed mixes in the wind and the thrust really used is unknown.
- Filling windows without trajectory: they are long windows (about 3 times more fuel than the others) and already the best predicted relative to their fuel.
- Wind from ERA5, tested on one week: almost no link with the error. Airliners usually cruise at a fixed mach, so the wind changes the distance flown more than the fuel burnt per hour, and the target is fuel per time window.
- XGBoost, sample weights by duration, a single filled-in speed column, and re-tuning CatBoost on the rate.

## Running it

Requirements: [uv](https://docs.astral.sh/uv/), and Google Cloud access for the data (see [`docs/stack/04-gcloud-auth.md`](docs/stack/04-gcloud-auth.md)).

```bash
git clone git@github.com:MalronClem/PRC_data_challenge_2025.git
cd PRC_data_challenge_2025
uv sync                      # create .venv from uv.lock
uv run pre-commit install    # enable git hooks
uv run nbstripout --install  # strip notebook outputs from commits (local git config)
```

Final model, trained on all of train and scored on `rank` and `final`:

```bash
uv run python -m prc_fuel.run --drop avg_vertical_rate openap_fuel airspeed_kt --model catboost --target rate --final
```

Without `--final`, the same command trains on the time split and prints the RMSE on validation, validation without outlier flights, and `rank`. Other options: `--model lightgbm|xgboost|catboost|blend`, `--target fuel|rate`, `--split time|random`, `--features` / `--drop` to pick features. The first run queries BigQuery and caches the data in `data/`.

The pipeline is split into small modules in `src/prc_fuel/`:

| Module | Does |
|---|---|
| `load.py` | queries fuel windows with flight, airport and trajectory info (`train`, `rank` or `final`), cached as parquet |
| `split.py` | random or time-based split by flight |
| `clean.py` | masks impossible feature values, removes flights with windows far outside the flight time from training (flights with an odd fuel rate are kept, it scores better) |
| `features.py` | one function per feature, and `build_features` to pick some |
| `train.py` | LightGBM, XGBoost and CatBoost behind one `Model` class, the blend, and the fuel rate target |
| `evaluate.py` | RMSE |
| `run.py` | command line entry, puts everything together |

## Project layout

```
src/prc_fuel/          project package
notebooks/             exploration and every experiment behind the docs
scripts/               figure of the scores over the runs
sql/                   BigQuery scripts (external tables on gs://prc2025/raw)
docs/exploration.md    data exploration findings
docs/experiments.md    experiment log: data, features, model, parameters, scores
docs/roadmap.md        what was done, in which order, and why
docs/stack/            technical choices and setup of each tool
```

## Data and references

The data is not stored in this repository. It is published under CC BY 4.0:

- Sun, J., Spinielli, E., & Strohmeier, M. (2026). *Aircraft Fuel Burn Estimation: The EUROCONTROL PRC 2025 Data Challenge*. Journal of Open Aviation Science. https://doi.org/10.59490/joas.2026.8750
- Dataset: https://doi.org/10.5281/zenodo.19184661

## License

Code released under the MIT License (see `LICENSE`).
