"""
Movement Time vs Coherence — supervisor-revision version.

Three figures:
  (1) movement_time_histograms.png
      Raw MT distribution per coherence bin, with vertical lines at the 1st/99th
      percentile cutoffs (the "trim per bin" used downstream) and trials with
      Sampling > 4.5s flagged in red. Validates that the trimming is reasonable
      and shows what's being thrown away.

  (2) movement_time_vs_coherence.png
      Main figure. Each 2P session contributes one (mean MT) per coherence bin
      per series (All / Correct / False). Sessions are plotted as faint dots;
      the bold line is the mean of session means; error bars are SEM ACROSS
      SESSIONS (n=23), not across trials.
      SEM = std / sqrt(n). It tells you how precisely you've estimated the
      mean, given your sample size. SEM-across-sessions is the honest number
      because trials within a session aren't independent — pooling them and
      taking SEM-across-trials looks artificially tight.

  (3) movement_time_per_session.png
      One mini MT-vs-coherence panel per session (~5x5 grid). For visual
      sanity-checking each session and spotting bad ones.

Stalled trials (Sampling > 4.5s, ~1.4%) are flagged in figure (1) and EXCLUDED
before computing per-session means in figures (2) and (3).

Data source:
    paper_fast_slow-main/data/2p/df_all_by_epoch_df_f_filtered.pkl
    Movement Time = duration of the "Movement to Lateral Port" epoch (epoch_time).
    Sampling Time = duration of the "Sampling" epoch.
    Coherence = |DV| * 100.
    Session   = (Name, Date, SessionNum) tuple.
"""

import pickle
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# 1. Load data + merge sampling-time flag onto movement rows
# ---------------------------------------------------------------------------
HERE = Path(__file__).resolve().parent
DATA_FP = HERE / "paper_fast_slow-main" / "data" / "2p" / "df_all_by_epoch_df_f_filtered.pkl"

with open(DATA_FP, "rb") as f:
    df = pickle.load(f)

TRIAL_KEY = ["Name", "Date", "SessionNum", "TrialNumber"]

# Sampling-epoch duration per trial -> a dict-like lookup
samp = (df[df.epoch == "Sampling"][TRIAL_KEY + ["epoch_time"]]
        .rename(columns={"epoch_time": "SamplingTime"}))

# Movement-epoch rows (one per trial)
mv = df[df.epoch == "Movement to Lateral Port"].copy()
mv = mv[mv.ChoiceCorrect.notnull()]
mv["MT"]    = mv.epoch_time          # seconds
mv["DVabs"] = mv.DV.abs()            # 0..1, |DV|

# Attach the sampling time + the stalled flag
mv = mv.merge(samp, on=TRIAL_KEY, how="left")
STALL_THRESH = 4.5                    # supervisor's threshold
mv["stalled"] = mv.SamplingTime > STALL_THRESH

# ---------------------------------------------------------------------------
# 2. Coherence bins (3 equal-width bins on |DV| in [0, 1])
# ---------------------------------------------------------------------------
BIN_EDGES = np.array([0.0, 1.0 / 3.0, 2.0 / 3.0, 1.01])
BIN_MIDS_PCT = (BIN_EDGES[:-1] + np.minimum(BIN_EDGES[1:], 1.0)) / 2 * 100
BIN_LABELS = [f"{lo*100:.0f}–{min(hi,1.0)*100:.0f}%"
              for lo, hi in zip(BIN_EDGES[:-1], BIN_EDGES[1:])]

mv["Bin"] = pd.cut(mv.DVabs, BIN_EDGES, include_lowest=True, labels=False).astype(int)

# Per-bin trim cutoffs (1st / 99th percentile of MT, computed on RAW data
# excluding stalled trials so the cutoffs aren't pulled out by them).
_clean = mv[~mv.stalled]
TRIM_LO, TRIM_HI = 1, 99
cutoffs = (_clean.groupby("Bin")["MT"]
           .agg(lo=lambda s: np.percentile(s, TRIM_LO),
                hi=lambda s: np.percentile(s, TRIM_HI)))


# ===========================================================================
# FIGURE 1 — Raw-MT histograms with trim cutoffs + stalled-trial overlay
# ===========================================================================
fig1, axes = plt.subplots(1, 3, figsize=(15, 4.8), sharey=True)
HIST_BINS = np.linspace(0, 5, 80)     # show out to 5s; long tail clipped
for b, ax in enumerate(axes):
    sub = mv[mv.Bin == b]
    ok  = sub[~sub.stalled].MT.values
    bad = sub[ sub.stalled].MT.values

    # log y-scale so the tail (where the cutoffs live) is visible alongside the bulk
    ax.hist(ok,  bins=HIST_BINS, color="steelblue", alpha=0.85,
            label=f"normal (n={len(ok):,})")
    if len(bad):
        ax.hist(bad, bins=HIST_BINS, color="crimson", alpha=0.95,
                label=f"sampling>{STALL_THRESH}s (n={len(bad):,})")
    ax.set_yscale("log")
    ax.set_ylim(0.7, None)            # 1 trial = visible

    lo, hi = cutoffs.loc[b, "lo"], cutoffs.loc[b, "hi"]
    for x, lbl in [(lo, f"{TRIM_LO}th pct"), (hi, f"{TRIM_HI}th pct")]:
        ax.axvline(x, color="black", linestyle="--", linewidth=1.3)
        ax.text(x, ax.get_ylim()[1] * 0.6,
                f" {lbl}: {x:.2f}s",
                rotation=90, va="top", ha="left", fontsize=8, color="black",
                bbox=dict(boxstyle="round,pad=0.15", fc="white",
                          ec="none", alpha=0.7))

    n_clipped_lo = (ok < lo).sum()
    n_clipped_hi = (ok > hi).sum()
    ax.set_title(f"Coherence {BIN_LABELS[b]}  (mid {BIN_MIDS_PCT[b]:.0f}%)\n"
                 f"trimmed: {n_clipped_lo} below, {n_clipped_hi} above",
                 fontsize=10)
    ax.set_xlabel("Movement Time (s)")
    if b == 0:
        ax.set_ylabel("# trials (raw, pre-trim, log scale)")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(fontsize=8, loc="upper right")

fig1.suptitle("Raw MT distribution per coherence bin — trim cutoffs validation",
              fontsize=12, y=1.02)
fig1.tight_layout()
HIST_OUT = HERE / "movement_time_histograms.png"
fig1.savefig(HIST_OUT, dpi=150, bbox_inches="tight")
print(f"Saved: {HIST_OUT}")


# ---------------------------------------------------------------------------
# 3. Drop stalled trials, then per-bin trim, for the aggregate figures
# ---------------------------------------------------------------------------
mv_clean = mv[~mv.stalled].copy()

def _within_cutoffs(g):
    lo, hi = cutoffs.loc[g.name, "lo"], cutoffs.loc[g.name, "hi"]
    return g[(g.MT >= lo) & (g.MT <= hi)]

mv_trim = mv_clean.groupby("Bin", group_keys=False).apply(_within_cutoffs)

print(f"\nTrials dropped:")
print(f"  stalled (Sampling>{STALL_THRESH}s): {(mv.stalled).sum()}")
print(f"  per-bin tail trim:                 {len(mv_clean) - len(mv_trim)}")
print(f"  remaining for aggregate figures:   {len(mv_trim):,}")


# ===========================================================================
# FIGURE 2 — Main: session-level means, SEM across sessions
# ===========================================================================
SERIES = {
    "All":     mv_trim,
    "Correct": mv_trim[mv_trim.ChoiceCorrect == 1],
    "False":   mv_trim[mv_trim.ChoiceCorrect == 0],
}
COLORS = {"All": "blue", "Correct": "limegreen", "False": "red"}

SESSION_KEY = ["Name", "Date", "SessionNum"]

def session_means(sub):
    """For each (session, bin), the per-trial mean MT. Returns wide-ish df:
    rows = (Name, Date, SessionNum, Bin), col = MT mean.
    """
    return (sub.groupby(SESSION_KEY + ["Bin"])["MT"]
               .mean()
               .reset_index()
               .rename(columns={"MT": "MT_session_mean"}))

fig2, ax = plt.subplots(figsize=(10, 7))

summary_rows = []   # for the printed table at the end
for name, sub in SERIES.items():
    sm = session_means(sub)
    # grand mean of session means + SEM across sessions
    g  = sm.groupby("Bin")["MT_session_mean"].agg(
            mean="mean",
            sem=lambda s: s.std(ddof=1) / np.sqrt(len(s)),
            n_sessions="count")

    # individual session dots (jittered slightly on x for visibility)
    rng = np.random.default_rng(0)
    for b in g.index:
        ys = sm[sm.Bin == b]["MT_session_mean"].values
        xs = BIN_MIDS_PCT[b] + rng.uniform(-1.2, 1.2, size=len(ys))
        ax.scatter(xs, ys, s=18, color=COLORS[name], alpha=0.30, zorder=1)

    # bold line + SEM error bars
    ax.errorbar(BIN_MIDS_PCT, g["mean"].values, yerr=g["sem"].values,
                fmt="-+", capsize=4, linewidth=2.2, markersize=12,
                color=COLORS[name],
                label=f"Movement Time {name} "
                      f"(n_sessions={int(g['n_sessions'].iloc[0])})",
                zorder=3)

    for b in g.index:
        summary_rows.append((name, int(b), BIN_MIDS_PCT[b],
                             g.loc[b, "mean"], g.loc[b, "sem"],
                             int(g.loc[b, "n_sessions"])))

ax.set_xlabel("Coherence %", fontsize=12)
ax.set_ylabel("Movement Time (s)", fontsize=12)
ax.set_xticks(np.arange(20, 90, 10))
ax.set_xticklabels([f"{t}%" for t in np.arange(20, 90, 10)])
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.legend(loc="upper center", frameon=True, fontsize=10,
          title="dots = per-session means, bars = SEM across sessions")
ax.set_title("Movement Time vs Coherence — session-level aggregation", fontsize=12)
fig2.tight_layout()

MAIN_OUT = HERE / "movement_time_vs_coherence.png"
fig2.savefig(MAIN_OUT, dpi=150)
print(f"Saved: {MAIN_OUT}")


# ===========================================================================
# FIGURE 3 — Small multiples: one panel per 2P session
# ===========================================================================
sessions = (mv_trim[SESSION_KEY].drop_duplicates()
            .sort_values(SESSION_KEY).reset_index(drop=True))
n_sess = len(sessions)
ncols = 5
nrows = int(np.ceil(n_sess / ncols))
fig3, axes3 = plt.subplots(nrows, ncols, figsize=(ncols * 3.0, nrows * 2.4),
                           sharex=True, sharey=True)
axes3 = np.atleast_2d(axes3)

for i, (_, srow) in enumerate(sessions.iterrows()):
    ax = axes3[i // ncols, i % ncols]
    sess_mask = ((mv_trim.Name == srow.Name)
                 & (mv_trim.Date == srow.Date)
                 & (mv_trim.SessionNum == srow.SessionNum))
    s_mv = mv_trim[sess_mask]
    for sname, scolor in COLORS.items():
        if sname == "All":
            sub = s_mv
        elif sname == "Correct":
            sub = s_mv[s_mv.ChoiceCorrect == 1]
        else:
            sub = s_mv[s_mv.ChoiceCorrect == 0]
        m = sub.groupby("Bin")["MT"].mean()
        ax.plot(BIN_MIDS_PCT[m.index], m.values, "-o",
                color=scolor, markersize=4, linewidth=1.2)
    date_str = pd.to_datetime(srow.Date).strftime("%Y-%m-%d") \
               if not isinstance(srow.Date, str) else str(srow.Date)
    ax.set_title(f"{srow.Name} | {date_str} | s{srow.SessionNum} (n={len(s_mv)})",
                 fontsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(labelsize=8)

# blank out unused panels
for j in range(n_sess, nrows * ncols):
    axes3[j // ncols, j % ncols].axis("off")

# shared axis labels
for ax in axes3[-1, :]:
    ax.set_xlabel("Coherence %", fontsize=9)
for ax in axes3[:, 0]:
    ax.set_ylabel("MT (s)", fontsize=9)

# legend on the figure
handles = [plt.Line2D([0], [0], color=c, marker="o", markersize=5, label=n)
           for n, c in COLORS.items()]
fig3.legend(handles=handles, loc="lower right", ncol=3, frameon=False,
            bbox_to_anchor=(0.98, 0.005))
fig3.suptitle(f"MT vs Coherence — per-session sanity check ({n_sess} sessions)",
              fontsize=12, y=1.00)
fig3.tight_layout()
PER_SESS_OUT = HERE / "movement_time_per_session.png"
fig3.savefig(PER_SESS_OUT, dpi=150, bbox_inches="tight")
print(f"Saved: {PER_SESS_OUT}")


# ---------------------------------------------------------------------------
# Print summary table
# ---------------------------------------------------------------------------
print("\nSession-level summary (mean of session means ± SEM across sessions):")
hdr = f"  {'series':<8} {'bin':>3} {'coh%':>5}  {'mean(s)':>8}  {'SEM(s)':>7}  {'n_sess':>6}"
print(hdr)
print("  " + "-" * (len(hdr) - 2))
for name, b, mid, m, se, ns in summary_rows:
    print(f"  {name:<8} {b:>3} {mid:>4.1f}%  {m:>8.3f}  {se:>7.3f}  {ns:>6}")
