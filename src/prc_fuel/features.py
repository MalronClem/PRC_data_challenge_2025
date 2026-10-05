import pandas as pd

from prc_fuel.load import load


def build_features(df, features):
    columns = {}
    for feature in features:
        columns[feature] = FEATURES[feature](df)
    return pd.DataFrame(columns)


def duration_s(df):
    return (df.end - df.start).dt.total_seconds()


def aircraft_type(df):
    return df.aircraft_type.astype("category")


def since_takeoff_s(df):
    return (df.start - df.takeoff).dt.total_seconds()


def before_landing_s(df):
    return (df.landed - df.end).dt.total_seconds()


FEATURES = {
    "duration_s": duration_s,
    "aircraft_type": aircraft_type,
    "since_takeoff_s": since_takeoff_s,
    "before_landing_s": before_landing_s,
}


if __name__ == "__main__":
    df = load("train")
    X = build_features(
        df, ["duration_s", "since_takeoff_s", "before_landing_s", "aircraft_type"]
    )
    print(X.describe())
    print(X.dtypes)
