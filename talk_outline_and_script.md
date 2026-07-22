# Fast & Slow — 30-min lab talk (Larkum lab)
## Outline + presenter monologue

**Audience:** lab meeting with Prof. Larkum in the room. ~30 min + questions.
**Format on every slide:** big figure, minimal text, one verdict line. The *monologue* below is what you SAY — it is deliberately not printed on the slide.
**Color code (say it once on slide 8, reuse everywhere):** green = correct, red = error/false, blue = all trials.
**Memes:** 3 total — Slide 1 (hook), Slide 15 (transition into next steps), Slide 18 (close).

---

# PART 1 — INTRO (~10 min)

## Slide 1 — Title + hook meme
**On slide:** Title "Neural correlates of certainty during movement time." Your name / date. The adapted *woman-yelling-at-cat* meme: woman = "You can't ask a mouse how confident it is!"; cat = "Movement time go brrr."

**Monologue:**
"Everyone here has had the experience of getting an answer right and *knowing* you got it right — versus getting it right but feeling like you basically flipped a coin. That feeling of certainty is metacognition, and in humans we just ask: 'how sure were you?' The problem is our animals can't answer that question. So the whole talk today is about a backdoor. The claim is that the mouse tells us how sure it is whether it wants to or not — through how it moves. Let me build up to why that's a reasonable thing to believe."

## Slide 2 — The Nashaat / Mostafa question (Fig 1)
**On slide:** Task-design figure (paper Fig 1). One line: "How long should you look before you decide?"

**Monologue:**
"This project sits on top of Mostafa's paper. The task is a random-dot motion task: a cloud of dots drifts left or right, coherence sets the difficulty, and the mouse reports the direction. The key manipulation is that the animal controls its own sampling time — it looks for as long as it wants before committing. Mostafa's question was about the *front end* of the decision: what sampling strategy do the mice use, and is it near-optimal? And the answer was yes — they spend longer on hard trials and less on easy ones, roughly the way an ideal observer should. Hold onto that idea that the animal is titrating time against difficulty, because we're about to do the same thing at the other end of the trial."

## Slide 3 — The pivot
**On slide:** Your trial-timeline image (sampling → decision → movement → reward). Bracket over "sampling" = *their question*; bracket over "movement" = *our question*.

**Monologue:**
"Here's the pivot. Mostafa studied everything up to the moment of commitment — the evidence-gathering. Once the mouse commits and starts moving to the port, that part was basically treated as 'the trial is over, it's just motor execution.' Our bet is that it is *not* just motor execution. We think the decision leaves a fingerprint on the movement itself. So we're taking the exact same logic — time as a readout of an internal state — and applying it to the movement instead of the sampling."

## Slide 4 — Our question: metacognition → metamotor
**On slide:** "Can movement time be a proxy for confidence?" Two labelled terms: *metacognition* (knowing how sure you are) and *metamotor* (that knowledge leaking into how you move).

**Monologue:**
"So the question in one sentence: can we use movement time as a proxy for the animal's confidence? Two words to define. Metacognition is your read-out of your own decision — a sense of 'I nailed that' or 'I'm guessing.' Metamotor is the idea that this internal sense doesn't stay in your head; it changes how you act it out. Think of a game-show buzzer — when you know the answer you slam it, when you're guessing you kind of half-reach and hesitate. That hesitation is metamotor. We're asking whether the mouse's run to the port carries that same hesitation."

## Slide 5 — How humans did it: trajectories
**On slide:** Human reaching screenshot — non-CoM (clean arc) vs CoM (curves back).

**Monologue:**
"This has been shown in humans, and it's worth seeing because it makes the idea concrete. In these experiments people report the decision by reaching to a target. On the left is a normal trial — a clean, committed arc straight to the answer. On the right is a 'change of mind' trial: the hand starts heading toward one option, then curves back and lands on the other. Nobody asked these people if they changed their mind — the *hand* said it. The movement is leaking the decision process in real time."

## Slide 6 — How humans did it: the signatures
**On slide:** The 4-panel human figure — p(correct) lower for CoM; p(CoM) peaks at low coherence; p(CoM) grows with RT tertile.

**Monologue:**
"And when you quantify those change-of-mind trials, three things fall out, and these are the 'signatures' I want you to remember. One: change-of-mind trials are less accurate — they happen when the person was unsure. Two: they peak at low coherence, i.e. on hard trials. Three: they grow with response time — the slower, more deliberative trials have more of them. So difficulty, accuracy, and time all line up with this movement signature. Our whole analysis section is basically: do we see these same signatures in the mouse's movement time? So keep this slide in the back of your mind — it's the answer key."

## Slide 7 — The logic, as a picture (the rubric)
**On slide:** Simple schematic: confidence ↑ with easy + correct, ↓ with hard + error. Claim card: "If MT is a proxy → fast when confident, slow when unsure."

**Monologue:**
"Let me make the prediction explicit before I show any data, so you can hold me to it. Confidence should be high when the trial is easy and you got it right, and low when it's hard or you got it wrong. So if movement time really is a confidence proxy, it has to inherit that pattern: fast movements on easy and correct trials, slow movements on hard and error trials. Every plot in the next section is me checking one box on this card. If a box doesn't get checked, I'll tell you."

---

# PART 2 — ANALYSIS (~14 min)

## Slide 8 — Defining and cleaning movement time
**On slide:** `movement_time_histograms.png` + `trimming_methods_comparison.png`. Note: MT = "Movement to Lateral Port" epoch. Trim = 1st/99th percentile per coherence bin.

**Monologue:**
"First, plumbing — because this is the thing you'd all ask me anyway. Movement time is the duration of the 'movement to lateral port' epoch: from when the animal leaves the center to when it reaches the choice port. The raw distributions have long tails — a handful of trials where the animal wandered off or disengaged, some of them 6, 8, 10 seconds. Those aren't 'slow decisions,' they're 'the animal stopped doing the task.' So I trim at the 1st and 99th percentile within each difficulty bin, and on the right I show that the result doesn't depend on which trimming rule I use. Just so you know the effects I'm about to show aren't an artifact of a couple of outliers. Everything from here is on this cleaned set, and the color code is green for correct, red for error, blue for all trials."

## Slide 9 — Robustness: per-session and per-trial
**On slide:** `movement_time_per_session.png` + `movement_time_vs_coherence_orig.png`. One line: "Not driven by one session or one aggregation choice."

**Monologue:**
"One more rigor slide, then the payoff. On the left is the same core effect broken out for all 23 sessions individually — I don't want you to think this is one lucky animal. In most sessions you can already see the error trials, the red line, peeling upward at high coherence. Two sessions are flagged: one with very few trials and high variance, and one animal, GP4-85, that's just globally faster with a flatter gradient. On the right is the same result aggregated per-trial instead of per-session, as a reference — the story is identical either way. So the effect is there whether I average within sessions first or pool trials, and it's present across the population, not one outlier."

## Slide 10 — Signature 1: MT vs coherence, split by outcome
**On slide:** `movement_time_vs_coherence.png`. Verdict: "Errors slow down at high coherence — the change-of-mind signature."

**Monologue:**
"Here's the first real signature. X-axis is coherence — difficulty, easy on the right. Y-axis is movement time. Green correct trials and blue all-trials are basically flat, even dipping a little as it gets easier — makes sense, easy trials, confident, quick movement. Now look at the red line, the errors. On easy trials — high coherence — the errors are dramatically *slower*. Think about what an error on an easy trial is: the evidence was screaming 'left' and the animal went right. That's exactly the trial where you'd expect a wobble, a change of mind, a hesitation — and the movement time shows it. This is the mouse version of the human change-of-mind signature from two slides ago. Box one, checked."

## Slide 11 — Signature 2: accuracy vs movement time
**On slide:** `accuracy_vs_mt.png`. Verdict: "Faster movements are more accurate — at every difficulty."

**Monologue:**
"This is the one I'd frame if I had to pick a single slide. Here I've flipped it around: bin trials by movement time and ask how accurate they are. Three lines for three difficulty levels. Within every single difficulty level, the faster movements are the more accurate ones — the lines slope down as movement time grows. So it's not just that easy trials are both fast and accurate; even holding difficulty fixed, when the animal moves fast it's more likely to be right. That is exactly what 'movement time reads out confidence' predicts: fast means sure means correct. Box two, checked."

## Slide 12 — Is movement time just sampling time again?
**On slide:** `sampling_vs_movement_time.png` + `mt_vs_sampling_time_binned.png`. Verdict: "Weak, difficulty-specific link → MT carries independent information."

**Monologue:**
"Now the obvious objection, and I want to hit it head-on. Mostafa already showed sampling time tracks difficulty. So am I just re-measuring sampling time with extra steps? No. On the left, the trial-by-trial correlation between sampling time and movement time is weak — significant on hard trials, r around minus 0.13, and negligible on easy trials. On the right, binned: yes, there's a mild tendency for longer sampling to go with slightly faster movement, and notice the error trials, in red, sit *above* the correct ones — slower — across the board. But the headline is these are two loosely coupled variables. Movement time is not a copy of sampling time; it's carrying its own information about the trial. That's what makes it worth studying separately."

## Slide 13 — Signature 3: confidence carries across trials (history)
**On slide:** `mt_by_prev_outcome.png` + `mt_prev_difficulty_outcome.png`. Verdict: "A surprising error slows the *next* movement."

**Monologue:**
"If movement time indexes an internal confidence state, that state shouldn't reset perfectly every trial — it should carry over. On the left: movement time, z-scored, split by whether the previous trial was correct or an error. Almost everything sits near zero except one condition that jumps way up — an error following an error, on easy trials. Two errors in a row on trials that should have been easy is the animal's worst 'wait, what am I doing' moment, and the movement time balloons. On the right I break it down by the difficulty of the *previous* trial, and it's the previous *easy* errors that slow you down the most — because an error on an easy trial is the most surprising, the most information that something's off. This is confidence-scaled updating: the more surprising the mistake, the bigger the hesitation on the next move. Box three, checked."

## Slide 14 — History continued: streaks and win-stay/lose-shift
**On slide:** `mt_streak.png` + `mt_win_stay_lose_shift.png`. Verdict: "Losing streaks slow the animal; win/lose-shift strategy: no reliable MT effect (honest null)."

**Monologue:**
"Two more history views, including one negative result, because I'd rather show you the whole picture. On the left, movement time as a function of streak length — positive numbers are consecutive correct, negative are consecutive errors. When the animal is on a losing streak, minus 3, 4, 5 in a row, the movements slow right down; winning streaks are flat or slightly faster. So it's a graded thing, not just the single previous trial. On the right I tested whether movement time differs by win-stay versus lose-shift strategy — and here it doesn't, the Kruskal–Wallis is not significant. There's a hint of a lose-stay effect on hard trials but I wouldn't hang anything on it. So the outcome history matters, but the specific strategic labels don't cleanly map onto movement time. That's a real boundary on the story."

## Slide 15 — Engagement: local reward rate
**On slide:** `mt_vs_reward_rate.png` + `accuracy_vs_reward_rate.png`. Verdict: "When the animal is doing badly locally, it's slow AND inaccurate — engagement confound to control for."
**MEME #2 goes on the transition out of this slide** (e.g. Drake: reject "ask the mouse how sure it is" / approve "time how fast it moves").

**Monologue:**
"Last analysis slide, and it's partly a caveat. I computed a local reward rate — how well the animal did in the last five trials — as a proxy for engagement. On the left, when reward rate is low, movement times shoot up, especially on medium and easy trials. On the right, low reward rate also goes with lower accuracy. So there's a global engagement axis: sometimes the animal is just checked out, and on those stretches it's both slow and wrong. I flag this because it's a confound I'll need to regress out before I claim a movement-time effect is 'confidence' rather than 'the animal was sleepy.' It doesn't erase the earlier effects — those hold within engaged blocks — but it's the honest asterisk."

## Slide 16 — Analysis summary: the rubric, checked
**On slide:** Re-show Slide 7's card, boxes now ticked: MT vs coherence ✓, accuracy ✓, history ✓; caveats noted (WSLS null, engagement confound).

**Monologue:**
"So, back to the card I gave you at the start. Movement time is fast on easy and correct trials, slow on hard and error trials. It shows the change-of-mind signature — errors slow at high coherence. It predicts accuracy even within a difficulty level. And it carries a confidence state across trials that scales with how surprising the last outcome was. The caveats are honest: the win-shift strategy labels don't map on, and I have to control for engagement. But the core claim survives: movement time behaves like a confidence readout. Which means we now have a confidence signal we can go looking for in the brain."

---

# PART 3 — NEXT STEPS (~5 min)

## Slide 17 — From behavior to neurons
**On slide:** Schematic: 2P traces aligned to movement onset; medial vs lateral frontal cortex; "which neurons predict MT / correct-vs-error trial by trial?" (No dendritic/layer detail.)

**Monologue:**
"So where does this go. We have two-photon calcium imaging from frontal cortex — medial and lateral fields — while the animals do this task. The plan is to align the neural activity to movement onset and ask a simple decoding question: is there a population of neurons whose activity around the movement predicts the movement time, and predicts whether the trial was correct or an error, trial by trial? If movement time is a confidence readout at the behavioral level, there should be a neural signal that carries it. That's the bridge from 'behavioral proxy' to 'neural correlate of certainty.'"

## Slide 18 — The modeling handle + close
**On slide:** Reference Mostafa's Fig 2 (DDM + RL / Q-learning predicts behavior). Arrow: "extend the model to predict MT as the readout." **MEME #3 / closing quote:** "All models are wrong, but some are useful."

**Monologue:**
"And the reason I'm optimistic this is tractable: Mostafa's paper already built a model — a drift-diffusion decision process wrapped in reinforcement learning — that predicts these animals' choices and sampling times really well. That's a ready-made scaffold. The next modeling step is to add movement time as an output of that same model — to predict, trial by trial, not just what the animal chose but how fast it moved to say so, and tie that to the confidence term in the model. Get that working and we can line the model's confidence up against the neural signal from the previous slide. That's the roadmap for the rest of the rotation. All models are wrong, but this one's going to be useful. Thanks — happy to take questions."

---

# BACKUP SLIDES (after Slide 18, for Q&A)
- `movement_time_histograms_extended.png` / `movement_time_histograms_normalized.png` — alternative MT distributions.
- `movement_time_vs_coherence_persession_mod.png` — per-session variant.
- `sampling_vs_movement_time_mod.png` — alternative sampling-vs-MT view.
- Trial counts vs published (5,320/4,144/1,176 vs 5,119/3,881/1,238) — for the "did you reproduce it exactly?" question.

# NOTES / OPEN DECISIONS
- Slides 8–9 are rigor. If you're tight on time, collapse to one slide and move per-session to backup.
- Consider stating the single sentence "movement time = a stopwatch on the animal's confidence" as your repeated tagline (Slides 1, 7, 16).
- Meme count kept to 3 so it stays a science talk with jokes, not a joke with science.
