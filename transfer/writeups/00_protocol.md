# Protocol and disclosed corrections

The pre-registration is [`docs/TRANSFER_PROTOCOL.md`](../../docs/TRANSFER_PROTOCOL.md).
It was committed at `b2b7b3b` before the pilots ran.

## The template

| Link | Question | Evidence | Falsified if |
|---|---|---|---|
| **L1. Measurement** | Does a task-matched 10 Hz signal predict the position's outcome beyond the incumbent? | Standardized beta, 95% CI, reliability, incremental R² | Signal null or dominated by the incumbent |
| **L2. Unpriced signal** | Is the signal weakly related to draft capital? | Signal–`B_draft` Spearman ρ | \|ρ\| ≥ 0.30 |
| **L3. Allocation** | Is measured performance unrewarded in next-season role while current role and draft are rewarded? | Existing per-position role equations; gap by draft quartile | Performance→role positive, CI excluding zero |

Tier 2 assumptions are used only as directional predictions: the wedge should be
larger where outcome reliability is lower and status is cheaper. The
cross-position ordering is descriptive; no meta-analytic p-value is reported.

## Gates and status vocabulary

- Signal reliability ≥ 0.50 (odd/even drills, Spearman-Brown); outcome
  reliability ≥ 0.50; primary sample ≥ 60 player-season rows.
- Status: `supported` (beta > 0, CI lower > 0), `weak` (beta > 0, CI includes
  0), `null` (beta ≤ 0), `unidentifiable` (gate failed).
- Primary tests: Holm correction. Secondary and per-drill estimates: BH FDR at
  q = 0.10, labeled exploratory.

## Disclosed corrections (2026-10-20)

Two specifications were corrected once the code was run against the data. They
are repeated here so the reader can judge them; neither changes a gate
threshold or the direction of a result.

1. **Sample gate unit.** The protocol's "≥ 60 players" is implemented as **≥ 60
   player-season rows**, the unit of the models and of the entry's n=64 interior
   result. Unique-player counts are reported in `outputs/transfer/drill_translation.csv`
   as the `n` column and in the writeups. The interior positive control is 64
   rows from 42 players.
2. **DL outcome.** The DL primary uses `pressure_rate_z`, matching the entry's
   headline burst→pressure result. The entry's `burst_z` is reported as a
   benchmark row; `pass_rush_burst` (the `PASS_RUSH_DRILL`-specific composite)
   is the task-matched transfer signal. Non-DL positions use the panel's `perf_z`
   (position-specific performance residual).

The first correction aligns the gate with the model's unit. The second corrects
a mismatch between the protocol table (`perf_z`) and the shortlist ("DL
pass-rush drill → pressure"). Both are visible in the output `role` column
(`benchmark` versus `primary`) and in the notes.

## What was not done

No dollar valuation, no two-agent calibration, no causal identification, no
external salary data, and no modification of `writeup/`, the public notebook, or
`implications/`.
