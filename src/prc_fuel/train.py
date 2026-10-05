import argparse

from lightgbm import LGBMRegressor

from prc_fuel.clean import clean
from prc_fuel.evaluate import rmse
from prc_fuel.features import FEATURES, build_features
from prc_fuel.load import load
from prc_fuel.split import split


def train(features):
    df = load("train")
    fit, val = split(df)
    fit = clean(fit)

    X_fit = build_features(fit, features)
    y_fit = fit.fuel_kg
    X_val = build_features(val, features)
    y_val = val.fuel_kg

    model = LGBMRegressor(random_state=42)
    model.fit(X_fit, y_fit)
    y_pred = model.predict(X_val)

    return rmse(y_val, y_pred)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Train LightGBM and print the validation RMSE"
    )
    parser.add_argument(
        "--features",
        nargs="+",
        choices=list(FEATURES),
        default=list(FEATURES),
    )
    args = parser.parse_args()
    score = train(args.features)
    print(f"RMSE on val: {score:.1f} kg")
