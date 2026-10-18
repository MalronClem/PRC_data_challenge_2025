from lightgbm import LGBMRegressor, early_stopping

from prc_fuel.features import build_features

DEFAULT_PARAMS = {}


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
