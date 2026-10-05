# PRC_data_challenge_2025
The 2025 edition of the PRC Data Challenge builds on top of the 2024 edition and proposes to build Machine Learning (ML) models to predict the amount of fuel burnt at certain intervals of the flight. The training dataset will consist of flight intervals and corresponding fuel burnt/flown amounts.

## Setup

Requirements: [uv](https://docs.astral.sh/uv/), and Google Cloud access for the data (see `docs/stack/04-gcloud-auth.md`).

```bash
git clone git@github.com:MalronClem/PRC_data_challenge_2025.git
cd PRC_data_challenge_2025
uv sync                      # create .venv from uv.lock
uv run pre-commit install    # enable git hooks
uv run nbstripout --install  # strip notebook outputs from commits (local git config)
```

## Training

```bash
uv run python -m prc_fuel.train                                   # all features
uv run python -m prc_fuel.train --features duration_s aircraft_type
```

It loads the train set, splits it by flight (80/20), removes outlier flights from the training part, trains LightGBM and prints the RMSE on the validation part. The first run queries BigQuery and caches the result in `data/`; use `uv run python -m prc_fuel.load train --refresh` after changing the query.

The pipeline is split into small modules in `src/prc_fuel/`:

| Module | Does |
|---|---|
| `load.py` | queries fuel intervals with flight and airport info (`train`, `rank` or `final`) |
| `split.py` | random split by flight |
| `clean.py` | removes outlier flights (training data only) |
| `features.py` | one function per feature, and `build_features` to pick some |
| `evaluate.py` | RMSE |
| `train.py` | runs everything |

## Project layout

```
src/prc_fuel/          project package
notebooks/             data exploration and models
sql/                   BigQuery scripts (external tables on gs://prc2025/raw)
docs/exploration.md    data exploration findings
docs/experiments.md    experiment log: data, features, model, parameters, scores
docs/stack/            technical choices and setup of each tool
```

## Data and references

The data is not stored in this repository. It is published under CC BY 4.0:

- Sun, J., Spinielli, E., & Strohmeier, M. (2026). *Aircraft Fuel Burn Estimation: The EUROCONTROL PRC 2025 Data Challenge*. Journal of Open Aviation Science. https://doi.org/10.59490/joas.2026.8750
- Dataset: https://doi.org/10.5281/zenodo.19184661

## License

Code released under the MIT License (see `LICENSE`).
