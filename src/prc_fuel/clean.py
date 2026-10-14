from prc_fuel.features import before_landing_s, duration_s, since_takeoff_s
from prc_fuel.load import load
from prc_fuel.split import split


def rate_outliers(df):
    df = df.assign(
        duration_s=duration_s(df),
    )

    flights = df.groupby("flight_id").agg(
        fuel_kg_sum=("fuel_kg", "sum"),
        duration_s_sum=("duration_s", "sum"),
        aircraft_type=("aircraft_type", "first"),
    )

    flights["fuel_rate_kg_per_s"] = flights["fuel_kg_sum"] / flights["duration_s_sum"]
    # Tukey far-out bounds per aircraft type and outlier flights
    grouped = flights.groupby("aircraft_type")["fuel_rate_kg_per_s"]
    flights["q1"] = grouped.transform(lambda s: s.quantile(0.25))
    flights["q3"] = grouped.transform(lambda s: s.quantile(0.75))
    flights["iqr"] = flights["q3"] - flights["q1"]
    flights["lower_bound"] = flights["q1"] - 3 * flights["iqr"]
    flights["upper_bound"] = flights["q3"] + 3 * flights["iqr"]

    outliers = flights[
        (flights["fuel_rate_kg_per_s"] < flights["lower_bound"])
        | (flights["fuel_rate_kg_per_s"] > flights["upper_bound"])
    ]
    return set(outliers.index)


def ground_outliers(df):

    df = df.assign(
        since_takeoff_s=since_takeoff_s(df),
        before_landing_s=before_landing_s(df),
    )

    ground_overflow = df[
        (df["since_takeoff_s"] < -1800) | (df["before_landing_s"] < -1800)
    ]
    ground_flights = ground_overflow["flight_id"].unique()
    return set(ground_flights)


def clean_training(df):
    bad_flights = ground_outliers(df)
    return df[~df["flight_id"].isin(bad_flights)]


def clean_all(df):
    bad_flights = rate_outliers(df) | ground_outliers(df)
    return df[~df["flight_id"].isin(bad_flights)]


if __name__ == "__main__":
    df = load("train")
    fit, val = split(df)
    cleaned = clean_training(fit)
    print("fit before cleaning:", len(fit), "intervals")
    print("fit after cleaning:", len(cleaned), "intervals")
