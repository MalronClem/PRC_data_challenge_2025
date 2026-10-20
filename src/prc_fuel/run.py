import argparse

import pandas as pd

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

    parser.add_argument(
        "--target",
        choices=["fuel", "rate"],
        default="fuel",
    )

    parser.add_argument(
        "--final",
        action="store_true",
        help="Train on all of train and score on rank and final, only once",
    )

    args = parser.parse_args()
    features = [f for f in args.features if f not in args.drop]

    df = mask_bad_values(load("train"))
    rank = mask_bad_values(load("rank"))

    if args.final:
        # All of train, rank and final never used for training (see roadmap)
        model = train(clean_training(df), features, algo=args.model, target=args.target)
        final = mask_bad_values(load("final"))
        both = pd.concat([rank, final], ignore_index=True)

        print(f"RMSE on rank: {score(model, rank, features):.1f} kg")
        print(f"RMSE on final: {score(model, final, features):.1f} kg")
        print(f"RMSE on rank + final: {score(model, both, features):.1f} kg")
    else:
        splitter = {"random": split, "time": split_by_time}[args.split]
        fit, val = splitter(df)
        model = train(
            clean_training(fit), features, algo=args.model, target=args.target
        )

        print(f"RMSE on val: {score(model, val, features):.1f} kg")
        print(f"RMSE on clean_val: {score(model, clean_all(val), features):.1f} kg")
        print(f"RMSE on rank: {score(model, rank, features):.1f} kg")
