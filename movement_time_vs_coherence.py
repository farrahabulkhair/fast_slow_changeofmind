"""
Recreate the Movement Time vs Coherence figure from the lab's behavioral data.

Plots three series (All / Correct / False trials) against three coherence bins
(equal-width on |DV|, midpoints at ~17%, ~51%, ~84%), with SEM error bars.

Data source:
    paper_fast_slow-main/data/2p/df_all_by_epoch_df_f_filtered.pkl
    Movement Time = duration of the "Movement to Lateral Port" epoch (epoch_time).
    Coherence = |DV| * 100.
"""

import pickle
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# 1. Load data
# ---------------------------------------------------------------------------
HERE = Path(__file__).resolve().parent
DATA_FP = HERE / "paper_fast_slow-main" / "data" / "2p" / "df_all_by_epoch_df_f_filtered.pkl"

with open(DATA_FP, "rb") as f:
    df = pickle.load(f)

# Keep only the "Movement to Lateral Port" epoch rows: epoch_time IS the movement time.
mv = df[df.epoch == "Movement to Lateral Port"].copy()
mv = mv[mv.ChoiceCorrect.notnull()]
mv["MT"] = mv.epoch_time            # seconds
mv["DVabs"] = mv.DV.abs()           # 0..1, |DV|

# Drop the long tail of distracted/aborted trials. These would otherwise dominate
# the means: max raw MT is > 17 s while the median is ~0.33 s. Keep the central
# 1st–99th percentile (per bin) so means and SEMs match the published figure.
import numpy as np
def _trim_tails(g, lo=1, hi=99):
    qlo, qhi = np.percentile(g.MT, [lo, hi])
    return g[(g.MT >= qlo) & (g.MT <= qhi)]

# ---------------------------------------------------------------------------
# 2. Bin by coherence into 3 equal-width bins on |DV| in [0, 1].
#    Midpoints land at 1/6, 1/2, 5/6 -> 16.67%, 50%, 83.33%
#    (matches the screenshot's x-positions of ~17%, ~51%, ~84%).
# ---------------------------------------------------------------------------
BIN_EDGES = np.array([0.0, 1.0 / 3.0, 2.0 / 3.0, 1.01])
BIN_MIDS_PCT = (BIN_EDGES[:-1] + np.minimum(BIN_EDGES[1:], 1.0)) / 2 * 100
mv["Bin"] = pd.cut(mv.DVabs, BIN_EDGES, include_lowest=True, labels=False)

# Trim per-bin outliers (drops the long tail; the column is dropped during the
# groupby, so we re-bin afterwards).
mv = mv.groupby("Bin", group_keys=False).apply(_trim_tails, include_groups=False)
mv["Bin"] = pd.cut(mv.DVabs, BIN_EDGES, include_lowest=True, labels=False)

# ---------------------------------------------------------------------------
# 3. Compute per-bin mean and SEM for each series.
# ---------------------------------------------------------------------------
def stats(group_df):
    return pd.Series({"mean": group_df.MT.mean(),
                      "sem":  group_df.MT.sem()})

series = {
    "Movement Time All":     mv,
    "Movement Time Correct": mv[mv.ChoiceCorrect == 1],
    "Movement Time False":   mv[mv.ChoiceCorrect == 0],
}
colors = {
    "Movement Time All":     "blue",
    "Movement Time Correct": "lime",
    "Movement Time False":   "red",
}

# ---------------------------------------------------------------------------
# 4. Plot.
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 7))
for name, sub in series.items():
    s = sub.groupby("Bin").apply(stats, include_groups=False).sort_index()
    n_total = len(sub)
    ax.errorbar(BIN_MIDS_PCT, s["mean"].values,
                yerr=s["sem"].values,
                fmt="-+", capsize=0, linewidth=2, markersize=10,
                color=colors[name],
                label=f"{name} ({n_total:,} pts)")

ax.set_xlabel("Coherence %", fontsize=12)
ax.set_ylabel("Movement Time (S)", fontsize=12)

# X axis ticks every 10% from 20 to 80 (mirrors the screenshot)
ax.set_xticks(np.arange(20, 90, 10))
ax.set_xticklabels([f"{t}%" for t in np.arange(20, 90, 10)])
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.legend(loc="upper center", frameon=True, fontsize=10)

plt.tight_layout()

OUT = HERE / "movement_time_vs_coherence.png"
plt.savefig(OUT, dpi=150)
print(f"Saved: {OUT}")
print()
print("Per-bin summary (n=trials):")
for name, sub in series.items():
    s = sub.groupby("Bin").apply(stats, include_groups=False).sort_index()
    counts = sub.groupby("Bin").size()
    print(f"  {name}  (total={len(sub):,})")
    for b in s.index:
        print(f"    bin {b} (~{BIN_MIDS_PCT[int(b)]:.1f}%): "
              f"mean={s.loc[b,'mean']:.3f}s, sem={s.loc[b,'sem']:.3f}s, n={counts.loc[b]}")
