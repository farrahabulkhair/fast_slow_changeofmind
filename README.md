# Fast & Slow — Movement Time vs Coherence

Reproduction and extension of the behavioral movement-time analyses from
**Nashaat et al., *Neuron*** — a random-dot-kinematogram (RDK) coherence
discrimination task in mice. This repo focuses on the *"fast and slow"*
change-of-mind signature: how movement time (MT) depends on stimulus
coherence and trial history.

Rotation project, Larkum Lab.

## The question

In the RDK task, mice sample a noisy motion stimulus and move to a lateral
port to report their choice. A key observation is that **error trials slow
down at high coherence** — when the evidence is strong but the animal chooses
wrong, movement is slower, consistent with a within-trial change of mind.
This repo recreates that plot and stress-tests it against different
trial-trimming and aggregation choices.

## Data

Analyses read from the upstream paper repository, cloned separately (it is
~4 GB and **not** tracked here — see `.gitignore`):

```
paper_fast_slow-main/data/2p/df_all_by_epoch_df_f_filtered.pkl
```

Each row is one trial × epoch. Key columns:

| Column          | Meaning                                                        |
|-----------------|----------------------------------------------------------------|
| `epoch`         | trial phase: `Sampling`, `Movement to Lateral Port`, `Reward`… |
| `epoch_time`    | duration of that epoch (s). On movement rows, this **is** MT   |
| `DV`            | signed coherence ∈ [-1, 1]; sign = side, \|DV\| = difficulty    |
| `ChoiceCorrect` | 1 = correct, 0 = error, null = no choice                       |

Movement Time = `epoch_time` on `epoch == "Movement to Lateral Port"` rows.
Coherence % = `|DV| * 100`. Cohort: GP4 (6 mice, L2/3 calcium imaging).

## Running

```bash
python -m venv .venv && source .venv/bin/activate
pip install numpy pandas matplotlib
python movement_time_vs_coherence.py
```

The script is layered:

- **Section A** — original per-trial aggregation (SEM across trials).
  Recreates the published GP4 figure.
- **Section B** — supervisor revisions: flag stalled trials (Sampling > 4.5 s),
  compare four trim methods (percentile, z-score, MAD, Tukey IQR), and
  re-aggregate per session (SEM across sessions rather than trials).

`movement_time_vs_coherence.ipynb` is the interactive version with the same
analysis plus the trial-history breakdowns.

## Figures

| File                                    | What it shows                                  |
|-----------------------------------------|------------------------------------------------|
| `movement_time_vs_coherence_orig.png`   | Section A — per-trial MT vs coherence (original)|
| `movement_time_vs_coherence.png`        | Section B — per-session MT vs coherence         |
| `movement_time_histograms*.png`         | Raw MT distributions and trim cutoffs           |
| `trimming_methods_comparison.png`       | Four trimming methods side by side              |
| `movement_time_per_session.png`         | Per-session sanity-check grid                   |
| `mt_by_prev_outcome.png`                | MT split by previous-trial outcome              |
| `mt_prev_difficulty_outcome.png`        | MT by previous difficulty × outcome             |
| `mt_streak.png`, `mt_win_stay_lose_shift.png` | Trial-history / win-stay–lose-shift effects |
| `mt_vs_reward_rate.png`, `accuracy_vs_*` | MT / accuracy vs reward rate                    |
| `sampling_vs_movement_time.png`         | Sampling time vs movement time                  |

## Reproduction notes

The qualitative pattern matches the paper — errors slow at high coherence.
Trial counts came out slightly higher than published (5,320 / 4,144 / 1,176 vs
5,119 / 3,881 / 1,238), likely due to a session-level inclusion criterion
(min-trials-per-session or per-animal performance) not yet in this pipeline.

## Repo layout

```
movement_time_vs_coherence.py     analysis script (Sections A + B)
movement_time_vs_coherence.ipynb  interactive notebook
*.png                             generated figures
paper_fast_slow-main/             upstream data + paper PDFs (gitignored, ~4 GB)
Fast_and_Slow_talk.pptx           rotation talk
talk_outline_and_script.md        talk notes
```
