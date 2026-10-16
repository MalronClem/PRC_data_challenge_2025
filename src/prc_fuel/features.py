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
    return haversine(
        df.origin_latitude, df.origin_longitude, df.dest_latitude, df.dest_longitude
    )


def n_points(df):
    return df.n_points


def avg_altitude(df):
    return df.avg_altitude


def alt_start(df):
    return df.alt_start


def alt_end(df):
    return df.alt_end


def avg_groundspeed(df):
    return df.avg_groundspeed


def avg_vertical_rate(df):
    return df.avg_vertical_rate


def avg_mach(df):
    return df.avg_mach


def implied_vr(df):
    return (df.alt_end - df.alt_start) / (duration_s(df) / 60)


def interval_distance(df):
    return haversine(df.lat_start, df.long_start, df.lat_end, df.long_end)


def haversine(lat1, lon1, lat2, lon2):
    # Great circle distance between the two airports, haversine formula
    lat1, lon1, lat2, lon2 = (
        np.radians(lat1),
        np.radians(lon1),
        np.radians(lat2),
        np.radians(lon2),
    )
    a = (
        np.sin((lat2 - lat1) / 2) ** 2
        + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    )
    # 6371 km is the mean earth radius
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
    "n_points": n_points,
    "avg_altitude": avg_altitude,
    "alt_start": alt_start,
    "alt_end": alt_end,
    "avg_groundspeed": avg_groundspeed,
    "avg_vertical_rate": avg_vertical_rate,
    "avg_mach": avg_mach,
    "implied_vr": implied_vr,
    "interval_distance": interval_distance,
}


if __name__ == "__main__":
    df = load("train")
    X = build_features(df, list(FEATURES))
    print(X.describe())
    print(X.dtypes)
