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
                cat_features=list(self.categories),
                **self.params,
            )
        else:
            raise ValueError(f"unknown algo: {self.algo}")

        if X_val is None:
            self.model.fit(X, y)
        else:
            # Early stopping, only used with LightGBM
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


def train(fit, features, params=None, val=None, algo="lightgbm"):
    X_fit = build_features(fit, features)
    if val is None:
        return Model(algo, params).fit(X_fit, fit.fuel_kg)
    X_val = build_features(val, features)
    return Model(algo, params).fit(X_fit, fit.fuel_kg, X_val, val.fuel_kg)
