from catboost import CatBoostRegressor
from lightgbm import LGBMRegressor, early_stopping
from xgboost import XGBRegressor

from prc_fuel.features import build_features

# LightGBM, tuned on the time split (run #17)
DEFAULT_PARAMS = {
    "learning_rate": 0.05,
    "n_estimators": 75,
    "num_leaves": 127,
    "min_child_samples": 100,
}

# CatBoost, tuned on the time split (model_tuning notebook)
CATBOOST_PARAMS = {
    "learning_rate": 0.05,
    "iterations": 226,
    "depth": 10,
    "l2_leaf_reg": 3,
}


class Model:
    # Same fit and predict for every library, categories handled in one place

    def __init__(self, algo="lightgbm", params=None):
        self.algo = algo
        self.params = params or {}

    def fit(self, X, y, X_val=None, y_val=None):
        self.categories = {
            c: X[c].cat.categories for c in X.select_dtypes("category").columns
        }
        X = self.prepare(X)

        if self.algo == "lightgbm":
            self.model = LGBMRegressor(
                random_state=42, **{**DEFAULT_PARAMS, **self.params}
            )
        elif self.algo == "xgboost":
            self.model = XGBRegressor(
                random_state=42, enable_categorical=True, **self.params
            )
        elif self.algo == "catboost":
            self.model = CatBoostRegressor(
                random_seed=42,
                verbose=0,
                allow_writing_files=False,
                cat_features=list(self.categories),
                **{**CATBOOST_PARAMS, **self.params},
            )
        else:
            raise ValueError(f"unknown algo: {self.algo}")

        if X_val is None:
            self.model.fit(X, y)
        elif self.algo == "catboost":
            self.model.fit(
                X,
                y,
                eval_set=(self.prepare(X_val), y_val),
                early_stopping_rounds=50,
            )
        else:
            # Early stopping with LightGBM, not set up for xgboost
            self.model.fit(
                X,
                y,
                eval_set=[(self.prepare(X_val), y_val)],
                callbacks=[early_stopping(50, verbose=False)],
            )
        return self

    def predict(self, X):
        return self.model.predict(self.prepare(X))

    def prepare(self, X):
        X = X.copy()
        for c, categories in self.categories.items():
            # Airports never seen in fit become NaN, a new "unknown" category
            # made xgboost much worse (205 -> 303 kg on val)
            X[c] = X[c].cat.set_categories(categories)

            if self.algo == "catboost":
                # catboost refuses NaN in categories, it wants strings
                X[c] = X[c].astype(str).fillna("nan")

        return X


class Blend:
    # Plain average of LightGBM and CatBoost, 0.5 was the best weight on
    # val_time (model_tuning notebook)

    def __init__(self):
        self.models = [Model("lightgbm"), Model("catboost")]

    def fit(self, X, y):
        for model in self.models:
            model.fit(X, y)
        return self

    def predict(self, X):
        return sum(model.predict(X) for model in self.models) / len(self.models)


class RateModel:
    # Learns the fuel rate (kg/s) and multiplies back by the duration, so the
    # trees don't have to learn the product themselves

    def __init__(self, model):
        self.model = model

    def fit(self, X, y, X_val=None, y_val=None):
        if X_val is None:
            self.model.fit(X, y / X["duration_s"])
        else:
            self.model.fit(X, y / X["duration_s"], X_val, y_val / X_val["duration_s"])
        return self

    def predict(self, X):
        return self.model.predict(X) * X["duration_s"].values


def train(fit, features, params=None, val=None, algo="lightgbm", target="fuel"):
    X_fit = build_features(fit, features)
    model = Blend() if algo == "blend" else Model(algo, params)
    if target == "rate":
        model = RateModel(model)
    if val is None:
        return model.fit(X_fit, fit.fuel_kg)
    X_val = build_features(val, features)
    return model.fit(X_fit, fit.fuel_kg, X_val, val.fuel_kg)
