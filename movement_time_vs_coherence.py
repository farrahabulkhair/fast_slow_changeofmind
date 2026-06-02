"""
Movement Time vs Coherence — layered.

Section A (original, commit fd8f19b): per-trial aggregation, SEM across trials.
                                      Recreates the published GP4 2P figure.
Section B (additions): supervisor revisions + trim-methods comparison.
  - Flag stalled trials (Sampling > 4.5 s)
  - Histogram of raw MT with chosen trim cutoffs
  - Comparison of 4 trimming methods (percentile, z-score, MAD, Tukey IQR)
  - Per-session aggregation (SEM across sessions, not trials)
  - Per-session sanity-check grid

Figures produced:
  movement_time_vs_coherence_orig.png   — Section A (per-trial, ORIGINAL)
  movement_time_histograms.png          — Section B Figure 1A
  trimming_methods_comparison.png       — Section B Figure 1B
  movement_time_vs_coherence.png        — Section B Figure 2B (per-session)
  movement_time_per_session.png         — Section B Figure 3

Data source:
    paper_fast_slow-main/data/2p/df_all_by_epoch_df_f_filtered.pkl
    Movement Time = duration of the "Movement to Lateral Port" epoch.
    Sampling Time = duration of the "Sampling" epoch.
    Coherence = |DV| * 100.
    Cohort = GP4 (6 mice, L2/3 calcium imaging). The "Rbp4_M2_1" slide is a
             DIFFERENT cohort whose per-trial MT is in a different data file.
"""

import pickle
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# ===========================================================================
# SECTION A — ORIGINAL (commit fd8f19b)
# ===========================================================================
# 1. Load data
# ---------------------------------------------------------------------------
HERE = Path(__file__).resolve().parent
DATA_FP = HERE / "paper_fast_slow-main" / "data" / "2p" / "df_all_by_epoch_df_f_filtered.pkl"

with open(DATA_FP, "rb") as f:
    df = pickle.load(f)

# Keep only the "Movement to Lateral Port" epoch rows: epoch_time IS the movement time.
mv_orig = df[df.epoch == "Movement to Lateral Port"].copy()
mv_orig = mv_orig[mv_orig.ChoiceCorrect.notnull()]
mv_orig["MT"] = mv_orig.epoch_time
mv_orig["DVabs"] = mv_orig.DV.abs()


# Drop the long tail of distracted/aborted trials.
def _trim_tails(g, lo=1, hi=99):
    qlo, qhi = np.percentile(g.MT, [lo, hi])
    return g[(g.MT >= qlo) & (g.MT <= qhi)]


# 2. Bin by coherence (3 equal-width bins on |DV|)
BIN_EDGES = np.array([0.0, 1.0 / 3.0, 2.0 / 3.0, 1.01])
BIN_MIDS_PCT = (BIN_EDGES[:-1] + np.minimum(BIN_EDGES[1:], 1.0)) / 2 * 100
BIN_LABELS = [f"{lo*100:.0f}–{min(hi,1.0)*100:.0f}%"
              for lo, hi in zip(BIN_EDGES[:-1], BIN_EDGES[1:])]
mv_orig["Bin"] = pd.cut(mv_orig.DVabs, BIN_EDGES, include_lowest=True, labels=False)

# Trim per-bin
mv_orig = mv_orig.groupby("Bin", group_keys=False).apply(_trim_tails, include_groups=False)
mv_orig["Bin"] = pd.cut(mv_orig.DVabs, BIN_EDGES, include_lowest=True, labels=False)


# 3. Compute per-bin mean and SEM for each series
def stats(group_df):
    return pd.Series({"mean": group_df.MT.mean(),
                      "sem":  group_df.MT.sem()})


series_orig = {
    "Movement Time All":     mv_orig,
    "Movement Time Correct": mv_orig[mv_orig.ChoiceCorrect == 1],
    "Movement Time False":   mv_orig[mv_orig.ChoiceCorrect == 0],
}
colors_orig = {
    "Movement Time All":     "blue",
    "Movement Time Correct": "lime",
    "Movement Time False":   "red",
}


# 4. Plot — ORIGINAL figure
fig_orig, ax_orig = plt.subplots(figsize=(10, 7))
for name, sub in series_orig.items():
    s = sub.groupby("Bin").apply(stats, include_groups=False).sort_index()
    n_total = len(sub)
    ax_orig.errorbar(BIN_MIDS_PCT, s["mean"].values, yerr=s["sem"].values,
                     fmt="-+", capsize=0, linewidth=2, markersize=10,
                     color=colors_orig[name],
                     label=f"{name} ({n_total:,} pts)")
ax_orig.set_xlabel("Coherence %", fontsize=12)
ax_orig.set_ylabel("Movement Time (S)", fontsize=12)
ax_orig.set_xticks(np.arange(20, 90, 10))
ax_orig.set_xticklabels([f"{t}%" for t in np.arange(20, 90, 10)])
ax_orig.spines["top"].set_visible(False)
ax_orig.spines["right"].set_visible(False)
ax_orig.legend(loc="upper center", frameon=True, fontsize=10)
ax_orig.set_title("ORIGINAL: Movement Time vs Coherence (per-trial aggregation)")
plt.tight_layout()
ORIG_OUT = HERE / "movement_time_vs_coherence_orig.png"
plt.savefig(ORIG_OUT, dpi=150)
print(f"Saved: {ORIG_OUT}")

print("\nORIGINAL per-bin summary (n=trials):")
for name, sub in series_orig.items():
    s = sub.groupby("Bin").apply(stats, include_groups=False).sort_index()
    counts = sub.groupby("Bin").size()
    print(f"  {name}  (total={len(sub):,})")
    for b in s.index:
        print(f"    bin {b} (~{BIN_MIDS_PCT[int(b)]:.1f}%): "
              f"mean={s.loc[b,'mean']:.3f}s, sem={s.loc[b,'sem']:.3f}s, n={counts.loc[b]}")


# ===========================================================================
# SECTION B — ADDITIONS (revision 1 + revision 2)
# ===========================================================================
# Reload + flag stalled. We keep the original mv_orig untouched above; here we
# build a fresh mv that also carries the SamplingTime so we can flag stalled trials.
# ---------------------------------------------------------------------------
TRIAL_KEY = ["Name", "Date", "SessionNum", "TrialNumber"]
samp = (df[df.epoch == "Sampling"][TRIAL_KEY + ["epoch_time"]]
        .rename(columns={"epoch_time": "SamplingTime"}))

mv = df[df.epoch == "Movement to Lateral Port"].copy()
mv = mv[mv.ChoiceCorrect.notnull()]
mv["MT"] = mv.epoch_time
mv["DVabs"] = mv.DV.abs()
mv = mv.merge(samp, on=TRIAL_KEY, how="left")
STALL_THRESH = 4.5
mv["stalled"] = mv.SamplingTime > STALL_THRESH
mv["Bin"] = pd.cut(mv.DVabs, BIN_EDGES, include_lowest=True, labels=False).astype(int)


# ---------------------------------------------------------------------------
# Cutoffs per bin under 4 trim methods, computed on non-stalled trials
# ---------------------------------------------------------------------------
_clean = mv[~mv.stalled]


def percentile_cutoffs(s, lo=1, hi=99):
    return np.percentile(s, lo), np.percentile(s, hi)


def zscore_cutoffs(s, k=3):
    m, sd = s.mean(), s.std(ddof=1)
    return m - k * sd, m + k * sd


def mad_cutoffs(s, k=3):
    med = np.median(s)
    mad = np.median(np.abs(s - med)) * 1.4826
    return med - k * mad, med + k * mad


def iqr_cutoffs(s, k=1.5):
    q1, q3 = np.percentile(s, [25, 75])
    iqr = q3 - q1
    return q1 - k * iqr, q3 + k * iqr


trim_methods = {
    "percentile (1st–99th)":           percentile_cutoffs,
    "z-score (mean ± 3·σ)":            zscore_cutoffs,
    "MAD (median ± 3·MAD)":            mad_cutoffs,
    "Tukey (Q1−1.5·IQR, Q3+1.5·IQR)":  iqr_cutoffs,
}
trim_colors = {
    "percentile (1st–99th)":           "black",
    "z-score (mean ± 3·σ)":            "tab:red",
    "MAD (median ± 3·MAD)":            "tab:green",
    "Tukey (Q1−1.5·IQR, Q3+1.5·IQR)":  "tab:purple",
}
cutoffs_all = {name: _clean.groupby("Bin")["MT"].apply(
                  lambda s, fn=fn: pd.Series(fn(s), index=["lo", "hi"]))
                  .unstack()
               for name, fn in trim_methods.items()}
cutoffs = cutoffs_all["percentile (1st–99th)"]
TRIM_LO, TRIM_HI = 1, 99


# ===========================================================================
# FIGURE 1A — Raw MT histograms with the chosen (percentile) cutoffs
# ===========================================================================
fig1, axes = plt.subplots(1, 3, figsize=(15, 4.8), sharey=True)
HIST_BINS = np.linspace(0, 5, 80)
for b, ax in enumerate(axes):
    sub = mv[mv.Bin == b]
    ok  = sub[~sub.stalled].MT.values
    bad = sub[ sub.stalled].MT.values
    ax.hist(ok, bins=HIST_BINS, color="steelblue", alpha=0.85,
            label=f"normal (n={len(ok):,})")
    if len(bad):
        ax.hist(bad, bins=HIST_BINS, color="crimson", alpha=0.95,
                label=f"sampling>{STALL_THRESH}s (n={len(bad):,})")
    ax.set_yscale("log")
    ax.set_ylim(0.7, None)
    lo, hi = cutoffs.loc[b, "lo"], cutoffs.loc[b, "hi"]
    for x, lbl in [(lo, f"{TRIM_LO}th pct"), (hi, f"{TRIM_HI}th pct")]:
        ax.axvline(x, color="black", linestyle="--", linewidth=1.3)
        ax.text(x, ax.get_ylim()[1] * 0.6, f" {lbl}: {x:.2f}s",
                rotation=90, va="top", ha="left", fontsize=8,
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.7))
    n_lo = (ok < lo).sum()
    n_hi = (ok > hi).sum()
    ax.set_title(f"Coherence {BIN_LABELS[b]}  (mid {BIN_MIDS_PCT[b]:.0f}%)\n"
                 f"trimmed: {n_lo} below, {n_hi} above", fontsize=10)
    ax.set_xlabel("Movement Time (s)")
    if b == 0:
        ax.set_ylabel("# trials (raw, pre-trim, log scale)")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(fontsize=8, loc="upper right")
fig1.suptitle("Raw MT distribution per coherence bin — chosen trim (1st/99th pct)",
              fontsize=12, y=1.02)
fig1.tight_layout()
HIST_OUT = HERE / "movement_time_histograms.png"
fig1.savefig(HIST_OUT, dpi=150, bbox_inches="tight")
print(f"Saved: {HIST_OUT}")


# ===========================================================================
# FIGURE 1B — Trimming methods comparison
# ===========================================================================
fig1b, axes1b = plt.subplots(1, 3, figsize=(16, 5), sharey=True)
for b, ax in enumerate(axes1b):
    sub = mv[mv.Bin == b]
    ok = sub[~sub.stalled].MT.values
    ax.hist(ok, bins=HIST_BINS, color="lightgray", alpha=0.95,
            label=f"raw MT (n={len(ok):,})")
    ax.set_yscale("log")
    ax.set_ylim(0.7, None)
    for mname in trim_methods.keys():
        lo, hi = cutoffs_all[mname].loc[b, ["lo", "hi"]]
        col = trim_colors[mname]
        ax.axvline(lo, color=col, linestyle="--", linewidth=1.4, alpha=0.9)
        ax.axvline(hi, color=col, linestyle="--", linewidth=1.4, alpha=0.9,
                   label=f"{mname}  [{lo:.2f}, {hi:.2f}]")
    ax.set_title(f"Coherence {BIN_LABELS[b]}  (mid {BIN_MIDS_PCT[b]:.0f}%)", fontsize=10)
    ax.set_xlabel("Movement Time (s)")
    if b == 0:
        ax.set_ylabel("# trials (raw, pre-trim, log scale)")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(fontsize=7, loc="upper right")
fig1b.suptitle("Trimming methods comparison — where each method would cut",
               fontsize=12, y=1.02)
fig1b.tight_layout()
TRIM_CMP_OUT = HERE / "trimming_methods_comparison.png"
fig1b.savefig(TRIM_CMP_OUT, dpi=150, bbox_inches="tight")
print(f"Saved: {TRIM_CMP_OUT}")


# ---------------------------------------------------------------------------
# Apply chosen trim + drop stalled
# ---------------------------------------------------------------------------
mv_clean = mv[~mv.stalled].copy()


def _within_cutoffs(g):
    lo, hi = cutoffs.loc[g.name, "lo"], cutoffs.loc[g.name, "hi"]
    return g[(g.MT >= lo) & (g.MT <= hi)]


mv_trim = mv_clean.groupby("Bin", group_keys=False).apply(_within_cutoffs)
print(f"\nADDITIONS — Trials dropped:")
print(f"  stalled (Sampling>{STALL_THRESH}s): {mv.stalled.sum()}")
print(f"  per-bin tail trim:                 {len(mv_clean) - len(mv_trim)}")
print(f"  remaining for aggregate figures:   {len(mv_trim):,}")


# ===========================================================================
# FIGURE 2B — Per-session aggregation, SEM across sessions
# ===========================================================================
SERIES = {
    "All":     mv_trim,
    "Correct": mv_trim[mv_trim.ChoiceCorrect == 1],
    "False":   mv_trim[mv_trim.ChoiceCorrect == 0],
}
COLORS = {"All": "blue", "Correct": "limegreen", "False": "red"}
SESSION_KEY = ["Name", "Date", "SessionNum"]


def session_means(sub):
    return (sub.groupby(SESSION_KEY + ["Bin"])["MT"].mean()
               .reset_index().rename(columns={"MT": "MT_session_mean"}))


fig2, ax = plt.subplots(figsize=(10, 7))
summary_rows = []
rng = np.random.default_rng(0)
for name, sub in SERIES.items():
    sm = session_means(sub)
    g  = sm.groupby("Bin")["MT_session_mean"].agg(
            mean="mean",
            sem=lambda s: s.std(ddof=1) / np.sqrt(len(s)),
            n_sessions="count")
    for b in g.index:
        ys = sm[sm.Bin == b]["MT_session_mean"].values
        xs = BIN_MIDS_PCT[b] + rng.uniform(-1.2, 1.2, size=len(ys))
        ax.scatter(xs, ys, s=18, color=COLORS[name], alpha=0.30, zorder=1)
    ax.errorbar(BIN_MIDS_PCT, g["mean"].values, yerr=g["sem"].values,
                fmt="-+", capsize=4, linewidth=2.2, markersize=12,
                color=COLORS[name],
                label=f"Movement Time {name} (n_sessions={int(g['n_sessions'].iloc[0])})",
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
ax.set_title("Movement Time vs Coherence — SUPERVISOR method (per-session)",
             fontsize=12)
fig2.tight_layout()
MAIN_OUT = HERE / "movement_time_vs_coherence.png"
fig2.savefig(MAIN_OUT, dpi=150)
print(f"Saved: {MAIN_OUT}")


# ===========================================================================
# FIGURE 3 — Per-session sanity-check grid
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
        if sname == "All":     sub = s_mv
        elif sname == "Correct": sub = s_mv[s_mv.ChoiceCorrect == 1]
        else:                   sub = s_mv[s_mv.ChoiceCorrect == 0]
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
for j in range(n_sess, nrows * ncols):
    axes3[j // ncols, j % ncols].axis("off")
for ax in axes3[-1, :]:
    ax.set_xlabel("Coherence %", fontsize=9)
for ax in axes3[:, 0]:
    ax.set_ylabel("MT (s)", fontsize=9)
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


print("\nSUPERVISOR per-session summary (mean of session means ± SEM across sessions):")
hdr = f"  {'series':<8} {'bin':>3} {'coh%':>5}  {'mean(s)':>8}  {'SEM(s)':>7}  {'n_sess':>6}"
print(hdr); print("  " + "-" * (len(hdr) - 2))
for name, b, mid, m, se, ns in summary_rows:
    print(f"  {name:<8} {b:>3} {mid:>4.1f}%  {m:>8.3f}  {se:>7.3f}  {ns:>6}")


# ===========================================================================
# SECTION C — MODIFICATIONS
# ===========================================================================

# ---------------------------------------------------------------------------
# Check for trial duplication in the samp merge
# ---------------------------------------------------------------------------
# The merge(samp, on=TRIAL_KEY, how="left") can produce duplicate rows if a
# trial has more than one "Sampling" epoch entry in df. Deduplicate samp so
# each TRIAL_KEY appears exactly once before merging.
# (Original samp construction left above untouched; we build a clean version.)

samp_dedup = (df[df.epoch == "Sampling"][TRIAL_KEY + ["epoch_time"]]
              .rename(columns={"epoch_time": "SamplingTime"})
              .groupby(TRIAL_KEY, as_index=False)["SamplingTime"].mean())

mv_check = df[df.epoch == "Movement to Lateral Port"].copy()
mv_check = mv_check[mv_check.ChoiceCorrect.notnull()]
mv_check["MT"] = mv_check.epoch_time
mv_check["DVabs"] = mv_check.DV.abs()
mv_check = mv_check.merge(samp_dedup, on=TRIAL_KEY, how="left")
mv_check["stalled"] = mv_check.SamplingTime > STALL_THRESH
mv_check["Bin"] = pd.cut(mv_check.DVabs, BIN_EDGES, include_lowest=True, labels=False).astype(int)

print(f"\nDuplication check — trials before dedup merge: {len(mv):,}, after: {len(mv_check):,}")
if len(mv_check) != len(mv):
    print("  WARNING: duplication found in original samp merge — using deduped version below.")
else:
    print("  OK: no duplication detected.")

# Use mv_check as the clean base for all modified figures
_clean_c = mv_check[~mv_check.stalled]
cutoffs_c = {name: _clean_c.groupby("Bin")["MT"].apply(
                 lambda s, fn=fn: pd.Series(fn(s), index=["lo", "hi"]))
                 .unstack()
              for name, fn in trim_methods.items()}
cutoffs_pct = cutoffs_c["percentile (1st–99th)"]


# ===========================================================================
# FIGURE 1A MODIFIED — Extended x-axis (0–10.1 s), consistent bin step 0.1 s
# Vertical bars show exact 1st & 99th percentile cut positions.
# ===========================================================================

# MODIFIED: extended range to reveal the full tail beyond the 5-s stimulus cap

HIST_BINS_EXT = np.arange(0, 10.1, 0.1)

fig1m, axes1m = plt.subplots(1, 3, figsize=(18, 4.8), sharey=True)
for b, ax in enumerate(axes1m):
    sub = mv_check[mv_check.Bin == b]
    ok  = sub[~sub.stalled].MT.values
    bad = sub[ sub.stalled].MT.values
    ax.hist(ok, bins=HIST_BINS_EXT, color="steelblue", alpha=0.85,
            label=f"normal (n={len(ok):,})")
    if len(bad):
        ax.hist(bad, bins=HIST_BINS_EXT, color="crimson", alpha=0.95,
                label=f"sampling>{STALL_THRESH}s (n={len(bad):,})")
    ax.set_yscale("log")
    ax.set_ylim(0.7, None)

    lo1, hi99 = cutoffs_pct.loc[b, "lo"], cutoffs_pct.loc[b, "hi"]
    n_lo = (ok < lo1).sum()
    n_hi = (ok > hi99).sum()

    ax.axvline(lo1, color="black", linestyle="--", linewidth=1.5,
               label=f"1st pct: {lo1:.2f}s (n={n_lo})")
    ax.axvline(hi99, color="darkorange", linestyle="--", linewidth=1.5,
               label=f"99th pct: {hi99:.2f}s (n={n_hi})")

    # shade the trimmed regions
    ax.axvspan(0, lo1, color="black", alpha=0.07)
    ax.axvspan(hi99, 10.1, color="darkorange", alpha=0.07)

    n_beyond5 = (ok > 5.0).sum()
    ax.set_title(f"Coherence {BIN_LABELS[b]}  (mid {BIN_MIDS_PCT[b]:.0f}%)\n"
                 f"trimmed: {n_lo} below 1st, {n_hi} above 99th | "
                 f"{n_beyond5} trials > 5 s", fontsize=9)
    ax.set_xlabel("Movement Time (s)")
    ax.set_xlim(0, 10.1)
    if b == 0:
        ax.set_ylabel("# trials (raw, pre-trim, log scale)")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(fontsize=7.5, loc="upper right")

fig1m.suptitle("Raw MT distribution — extended range 0–10.1 s, binwidth 0.1 s\n"
               "(vertical bars = exact 1st / 99th percentile cut positions)",
               fontsize=12, y=1.03)
fig1m.tight_layout()
HIST_EXT_OUT = HERE / "movement_time_histograms_extended.png"
fig1m.savefig(HIST_EXT_OUT, dpi=150, bbox_inches="tight")
print(f"Saved: {HIST_EXT_OUT}")


# ===========================================================================
# FIGURE 1A MODIFIED v2 — Normalized (density), full range 0–10.1 s,
# only 99th percentile shown (1st percentile NOT applied).
# ===========================================================================

# MODIFIED: normalized density view, no 1st-percentile cut, 99th pct only

fig1n, axes1n = plt.subplots(1, 3, figsize=(18, 4.8), sharey=True)
for b, ax in enumerate(axes1n):
    sub = mv_check[mv_check.Bin == b]
    ok  = sub[~sub.stalled].MT.values
    bad = sub[ sub.stalled].MT.values

    # normalized so the full distribution is visible regardless of bin size
    ax.hist(ok, bins=HIST_BINS_EXT, color="steelblue", alpha=0.85, density=True,
            label=f"normal (n={len(ok):,})")
    if len(bad):
        ax.hist(bad, bins=HIST_BINS_EXT, color="crimson", alpha=0.70, density=True,
                label=f"sampling>{STALL_THRESH}s (n={len(bad):,})")

    hi99 = cutoffs_pct.loc[b, "hi"]
    n_hi = (ok > hi99).sum()
    ax.axvline(hi99, color="darkorange", linestyle="--", linewidth=1.8,
               label=f"99th pct: {hi99:.2f}s (n={n_hi})")
    ax.axvspan(hi99, 10.1, color="darkorange", alpha=0.07)

    n_beyond5 = (ok > 5.0).sum()
    ax.set_title(f"Coherence {BIN_LABELS[b]}  (mid {BIN_MIDS_PCT[b]:.0f}%)\n"
                 f"{n_hi} above 99th pct | {n_beyond5} trials > 5 s", fontsize=9)
    ax.set_xlabel("Movement Time (s)")
    ax.set_xlim(0, 10.1)
    if b == 0:
        ax.set_ylabel("Probability density")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(fontsize=7.5, loc="upper right")

fig1n.suptitle("Raw MT distribution — normalized density, full range 0–10.1 s\n"
               "(1st percentile NOT removed; only 99th percentile cut shown)",
               fontsize=12, y=1.03)
fig1n.tight_layout()
HIST_NORM_OUT = HERE / "movement_time_histograms_normalized.png"
fig1n.savefig(HIST_NORM_OUT, dpi=150, bbox_inches="tight")
print(f"Saved: {HIST_NORM_OUT}")


# ===========================================================================
# FIGURE 2B MODIFIED — Per-session aggregation using deduped data
# (average of averages, SEM across sessions)
# ===========================================================================

# MODIFIED: uses deduped samp merge; trim applied with per-bin cutoffs

mv_clean_c = mv_check[~mv_check.stalled].copy()


def _within_cutoffs_c(g):
    lo_c, hi_c = cutoffs_pct.loc[g.name, "lo"], cutoffs_pct.loc[g.name, "hi"]
    return g[(g.MT >= lo_c) & (g.MT <= hi_c)]


mv_trim_c = mv_clean_c.groupby("Bin", group_keys=False).apply(_within_cutoffs_c)

SERIES_C = {
    "All":     mv_trim_c,
    "Correct": mv_trim_c[mv_trim_c.ChoiceCorrect == 1],
    "False":   mv_trim_c[mv_trim_c.ChoiceCorrect == 0],
}

fig2m, ax2m = plt.subplots(figsize=(10, 7))
summary_rows_c = []
rng_c = np.random.default_rng(0)
for name, sub in SERIES_C.items():
    sm = session_means(sub)
    g  = sm.groupby("Bin")["MT_session_mean"].agg(
            mean="mean",
            sem=lambda s: s.std(ddof=1) / np.sqrt(len(s)),
            n_sessions="count")
    for b in g.index:
        ys = sm[sm.Bin == b]["MT_session_mean"].values
        xs = BIN_MIDS_PCT[b] + rng_c.uniform(-1.2, 1.2, size=len(ys))
        ax2m.scatter(xs, ys, s=18, color=COLORS[name], alpha=0.30, zorder=1)
    ax2m.errorbar(BIN_MIDS_PCT, g["mean"].values, yerr=g["sem"].values,
                  fmt="-+", capsize=4, linewidth=2.2, markersize=12,
                  color=COLORS[name],
                  label=f"Movement Time {name} (n_sessions={int(g['n_sessions'].iloc[0])})",
                  zorder=3)
    for b in g.index:
        summary_rows_c.append((name, int(b), BIN_MIDS_PCT[b],
                               g.loc[b, "mean"], g.loc[b, "sem"],
                               int(g.loc[b, "n_sessions"])))
ax2m.set_xlabel("Coherence %", fontsize=12)
ax2m.set_ylabel("Movement Time (s)", fontsize=12)
ax2m.set_xticks(np.arange(20, 90, 10))
ax2m.set_xticklabels([f"{t}%" for t in np.arange(20, 90, 10)])
ax2m.spines["top"].set_visible(False)
ax2m.spines["right"].set_visible(False)
ax2m.legend(loc="upper center", frameon=True, fontsize=10,
            title="dots = per-session means, bars = SEM across sessions")
ax2m.set_title("Movement Time vs Coherence — per-session average of averages\n"
               "(dedup-checked merge)", fontsize=12)
fig2m.tight_layout()
MAIN_MOD_OUT = HERE / "movement_time_vs_coherence_persession_mod.png"
fig2m.savefig(MAIN_MOD_OUT, dpi=150)
print(f"Saved: {MAIN_MOD_OUT}")


# ===========================================================================
# FIGURE 4 — Sampling Time vs Movement Time scatter (per difficulty level)
# One panel per coherence bin (Easy / Medium / Hard)
# Color: correct = green, incorrect = red
# Linear fit per panel
# ===========================================================================

# MODIFIED: new behavioral correlation plot

DIFF_LABELS = ["Easy", "Medium", "Hard"]
# Easy = lowest coherence bin (0), Hard = highest (2)
# (BIN_LABELS[0] = 0–33%, BIN_LABELS[2] = 67–100%)

fig4, axes4 = plt.subplots(1, 3, figsize=(18, 5.5))

for b, ax in enumerate(axes4):
    sub = mv_trim_c[mv_trim_c.Bin == b].dropna(subset=["SamplingTime", "MT"])
    correct = sub[sub.ChoiceCorrect == 1]
    wrong   = sub[sub.ChoiceCorrect == 0]

    ax.scatter(correct.SamplingTime, correct.MT,
               c="green", s=10, alpha=0.35, linewidths=0,
               label=f"Correct (n={len(correct):,})")
    ax.scatter(wrong.SamplingTime, wrong.MT,
               c="red", s=10, alpha=0.35, linewidths=0,
               label=f"Incorrect (n={len(wrong):,})")

    # Linear fit on all trials in this bin
    x_all = sub.SamplingTime.values
    y_all = sub.MT.values
    if len(x_all) > 1:
        coeffs = np.polyfit(x_all, y_all, 1)
        x_fit  = np.array([x_all.min(), x_all.max()])
        y_fit  = np.polyval(coeffs, x_fit)
        # Pearson r for annotation
        r = np.corrcoef(x_all, y_all)[0, 1]
        ax.plot(x_fit, y_fit, color="black", linewidth=1.8,
                label=f"Linear fit  r={r:.3f}")

    ax.set_xlabel("Sampling Time (s)", fontsize=11)
    ax.set_ylabel("Movement Time (s)", fontsize=11)
    ax.set_title(f"{DIFF_LABELS[b]}  —  Coherence {BIN_LABELS[b]}\n"
                 f"(n={len(sub):,} trials)", fontsize=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(fontsize=8.5, loc="upper right", markerscale=2)

fig4.suptitle("Sampling Time vs Movement Time per difficulty level\n"
              "(correct = green, incorrect = red; black line = linear fit)",
              fontsize=12, y=1.02)
fig4.tight_layout()
SCATTER_OUT = HERE / "sampling_vs_movement_time.png"
fig4.savefig(SCATTER_OUT, dpi=150, bbox_inches="tight")
print(f"Saved: {SCATTER_OUT}")

print("\nSection C done.")
