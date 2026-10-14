import numpy as np
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


def flight_duration_s(df):
    return (df.landed - df.takeoff).dt.total_seconds()


def flight_progress(df):
    return since_takeoff_s(df) / flight_duration_s(df)


def origin_icao(df):
    return df.origin_icao.astype("category")


def destination_icao(df):
    return df.destination_icao.astype("category")


def origin_elevation(df):
    return df.origin_elevation


def dest_elevation(df):
    return df.dest_elevation


def day_of_week(df):
    return df.start.dt.dayofweek


def hour(df):
    return df.start.dt.hour


def route_distance(df):
    # Great circle distance between the two airports, haversine formula
    coordinates = np.radians(
        df[["origin_latitude", "origin_longitude", "dest_latitude", "dest_longitude"]]
    )

    a = (
        np.sin((coordinates.dest_latitude - coordinates.origin_latitude) / 2) ** 2
        + np.cos(coordinates.origin_latitude)
        * np.cos(coordinates.dest_latitude)
        * np.sin((coordinates.dest_longitude - coordinates.origin_longitude) / 2) ** 2
    )

    # 6371 km is the mean Earth radius
    return 2 * 6371 * np.arcsin(np.sqrt(a))


FEATURES = {
    "duration_s": duration_s,
    "aircraft_type": aircraft_type,
    "since_takeoff_s": since_takeoff_s,
    "before_landing_s": before_landing_s,
    "flight_duration_s": flight_duration_s,
    "flight_progress": flight_progress,
    "origin_icao": origin_icao,
    "destination_icao": destination_icao,
    "origin_elevation": origin_elevation,
    "dest_elevation": dest_elevation,
    "day_of_week": day_of_week,
    "hour": hour,
    "route_distance": route_distance,
}


if __name__ == "__main__":
    df = load("train")
    X = build_features(df, list(FEATURES))
    print(X.describe())
    print(X.dtypes)
