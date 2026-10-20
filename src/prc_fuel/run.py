import argparse

from prc_fuel.clean import clean_all, clean_training, mask_bad_values
from prc_fuel.evaluate import score
from prc_fuel.features import FEATURES
from prc_fuel.load import load
from prc_fuel.split import split, split_by_time
from prc_fuel.train import train

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Train LightGBM and print the val, clean_val and rank RMSE"
    )
    parser.add_argument(
        "--features",
        nargs="+",
        choices=list(FEATURES),
        default=list(FEATURES),
    )

    parser.add_argument(
        "--drop",
        nargs="+",
        choices=list(FEATURES),
        default=[],
    )

    parser.add_argument(
        "--split",
        choices=["random", "time"],
        default="time",
    )

    parser.add_argument(
        "--model",
        choices=["lightgbm", "xgboost", "catboost", "blend"],
        default="lightgbm",
    )

    args = parser.parse_args()
    features = [f for f in args.features if f not in args.drop]

    df = load("train")
    df = mask_bad_values(df)
    splitter = {"random": split, "time": split_by_time}[args.split]
    fit, val = splitter(df)
    fit = clean_training(fit)
    model = train(fit, features, algo=args.model)

    rank = load("rank")
    rank = mask_bad_values(rank)
    val_rmse = score(model, val, features)
    clean_val_rmse = score(model, clean_all(val), features)
    rank_rmse = score(model, rank, features)

    print(f"RMSE on val: {val_rmse:.1f} kg")
    print(f"RMSE on clean_val: {clean_val_rmse:.1f} kg")
    print(f"RMSE on rank: {rank_rmse:.1f} kg")
