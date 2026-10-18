from lightgbm import LGBMRegressor, early_stopping

from prc_fuel.features import build_features

DEFAULT_PARAMS = {
    "learning_rate": 0.05,
    "n_estimators": 75,
    "num_leaves": 127,
    "min_child_samples": 100,
}


def train(fit, features, params=None, val=None):

    X_fit = build_features(fit, features)
    y_fit = fit.fuel_kg

    model = LGBMRegressor(random_state=42, **{**DEFAULT_PARAMS, **(params or {})})

    if val is None:
        model.fit(X_fit, y_fit)
    else:
        X_val = build_features(val, features)
        model.fit(
            X_fit,
            y_fit,
            eval_set=[(X_val, val.fuel_kg)],
            callbacks=[early_stopping(50, verbose=False)],
        )

    return model
