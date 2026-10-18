import pandas as pd

from prc_fuel.load import load


def split(df, val_frac=0.2):
    list_flights = sorted(df.flight_id.unique())
    val_flights = pd.Series(list_flights).sample(frac=val_frac, random_state=42)
    val = df[df["flight_id"].isin(val_flights)]
    fit = df[~df["flight_id"].isin(val_flights)]
    return fit, val


def split_by_time(df, val_frac=0.2):
    # The last flights to take off go to val, like rank comes after train
    takeoffs = df.groupby("flight_id").takeoff.first().sort_values()
    n_val = int(len(takeoffs) * val_frac)
    val_flights = takeoffs.index[-n_val:]
    val = df[df.flight_id.isin(val_flights)]
    fit = df[~df.flight_id.isin(val_flights)]
    return fit, val


if __name__ == "__main__":
    df = load("train")
    fit, val = split(df)
    print("fit:", fit["flight_id"].nunique(), "flights,", len(fit), "intervals")
    print("val:", val["flight_id"].nunique(), "flights,", len(val), "intervals")
