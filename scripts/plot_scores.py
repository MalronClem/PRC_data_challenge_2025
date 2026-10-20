from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "figures" / "scores.png"

# Runs that became the reference, the others were tried and dropped
KEPT = [7, 8, 9, 10, 12, 13, 16, 17, 21, 25, 26]
# Text and offset in points for the annotated runs
LABELS = {
    10: ("trajectory features", (0, -16)),
    16: ("time split", (0, 10)),
    21: ("LightGBM + CatBoost", (0, -16)),
    25: ("fuel rate target", (-10, -16)),
    26: ("final model", (0, 10)),
}
BASELINE_RANK = 266.6


def read_runs(path):
    rows = []
    for line in path.read_text().splitlines():
        cells = [c.strip() for c in line.split("|")[1:-1]]
        if cells and cells[0].isdigit():
            rank = pd.to_numeric(cells[8], errors="coerce")
            rows.append({"run": int(cells[0]), "rank": rank})
    return pd.DataFrame(rows).dropna()


runs = read_runs(ROOT / "docs" / "experiments.md")
kept = runs[runs["run"].isin(KEPT)]
dropped = runs[~runs["run"].isin(KEPT)]

blue, grey, ink, muted = "#2a78d6", "#a3a29c", "#0b0b0b", "#52514e"
fig, ax = plt.subplots(figsize=(9, 4.5))

ax.axhline(BASELINE_RANK, color=grey, linewidth=1, linestyle="--")
ax.text(
    runs["run"].max(),
    BASELINE_RANK - 0.8,
    "baseline 266.6",
    color=muted,
    fontsize=8,
    ha="right",
    va="top",
)
ax.axvline(15.5, color=grey, linewidth=1, linestyle=":")
ax.text(
    15.7,
    264,
    "time split from here,\ntrained on older flights",
    color=muted,
    fontsize=8,
    va="top",
)

ax.scatter(
    dropped["run"], dropped["rank"], s=30, color=grey, label="tried, not kept", zorder=2
)
# The line is cut where the validation changed, the two parts aren't trained
# on the same data
for part, label in [
    (kept[kept["run"] < 16], "kept as reference"),
    (kept[kept["run"] >= 16], None),
]:
    ax.plot(
        part["run"],
        part["rank"],
        color=blue,
        linewidth=2,
        marker="o",
        markersize=6,
        label=label,
        zorder=3,
    )

for run, (text, offset) in LABELS.items():
    y = runs.loc[runs["run"] == run, "rank"].iloc[0]
    ax.annotate(
        f"{text} ({y:.1f})",
        (run, y),
        xytext=offset,
        textcoords="offset points",
        ha="center",
        va="center",
        fontsize=8,
        color=ink,
    )

ax.set_xlabel("run (docs/experiments.md)", color=muted)
ax.set_ylabel("RMSE on rank (kg)", color=muted)
ax.set_title(
    "RMSE on the September test set (rank) over the runs",
    loc="left",
    color=ink,
    fontsize=11,
)
ax.set_xticks(runs["run"])
ax.tick_params(colors=muted, labelsize=8)
for side in ["top", "right"]:
    ax.spines[side].set_visible(False)
ax.grid(axis="y", color="#e6e5e0", linewidth=0.8)
ax.set_axisbelow(True)
ax.set_ylim(228, 270)
ax.legend(frameon=False, fontsize=8, loc="lower left")

fig.tight_layout()
OUT.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT, dpi=150)
