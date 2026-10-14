from lightgbm import LGBMRegressor

from prc_fuel.features import build_features


def train(fit, features):

    X_fit = build_features(fit, features)
    y_fit = fit.fuel_kg

    model = LGBMRegressor(random_state=42)
    model.fit(X_fit, y_fit)

    return model
