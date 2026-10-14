from prc_fuel.features import build_features


def rmse(y_true, y_pred):
    return (((y_true - y_pred) ** 2).mean()) ** 0.5


def score(model, df, features):
    X = build_features(df, features)
    y_predict = model.predict(X)
    return rmse(df.fuel_kg, y_predict)
