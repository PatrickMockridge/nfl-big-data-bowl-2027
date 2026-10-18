# Preregistration — NFL Big Data Bowl 2027 (Yellow Square)

Frozen: 2026-10-18. This file is written before any 2025 holdout analysis.
The 2025 draft class is the confirmatory test and will be run once.

## Focus

- Position group: **DL** (`combine_position == "DL"`), 115 players with snaps.
- Primary outcome: **`player_get_off`** (time from snap to crossing the line of scrimmage; lower is better). Verified performance = context-adjusted residual of `-player_get_off` (positive = faster get-off than expected).
- Secondary outcomes: pressure rate (`quick_pressure` / `time_to_pressure`, sparse), sack rate, `pass_rushers_encountered`; career snaps/start rate as a Blue-quadrant status outcome.
- Subgroups: EDGE (DE + OLB) and INTERIOR (DT + NT); pool with subgroup fixed effects and report separately.

## Framework variables

- **Bridge `B`**: percentile of `draft_overall_pick` within position subgroup and draft year; higher = more central. UDFAs handled with a censored/two-part sensitivity.
- **Alignment `A`**: out-of-fold similarity of the prospect's standardized Combine movement profile to the learned success archetype (top-tercile verified get-off) within position subgroup. `A ∈ [0,1]`.
- **Corruption `C`**: `1 − percentile(verified get-off residual given draft capital, subgroup, draft year)`; high = bust severity.
- **Flip rate `F`**: movement-state changes per transition in 10 Hz Combine attempts (accelerating/decelerating/left-turn/right-turn/straight), plus attempt-to-attempt sign flips.
- **Dwell `D`**: median run length in a movement state; consecutive attempts in the same state.
- **Möbius**: Yellow and `F` in the top quartile and `D` in the bottom quartile; continuous `m = z(F) − z(D)`.
- **Squares**: Green `B < median`; Red `B ≥ median, A < 0.30`; Yellow `B ≥ median, 0.30 ≤ A ≤ 0.70`; Blue `B ≥ median, A > 0.70`.
- **Fragility `Φ`**: cross-fitted `P(C > threshold | B, A, F, D, Z)`.
- **Resilience `R`**: `E[C | Φ] − C` (positive = better than predicted).
- **Compounding**: player-level interaction excess; team/cohort `Φ_team = 1 − ∏(1−Φ_i)` with permutation tests.

## Primary metric set (Combine)

First-step acceleration, time to first movement, path efficiency, change-of-direction time/angle, and entry/exit speed from `PASS_RUSH_DRILL`, `FRONT_START_WAVE_DRILL_AND_LATERAL_REACTION`, `FOUR_BAG_AGILITY_DRILL`, `RUN_AND_CLUB_DRILL`, `RUN_THE_HOOP_DRILL`, `BODY_CONTROL_DRILL`; official `ten_yd_split`, `forty`, `three_cone`, `short_shuttle`, `vertical`, `broad_jump`, `ngs_athleticism_score`. Secondary metrics are exploratory and FDR-corrected.

## Hypotheses

- **H1:** Yellow DL prospects have higher bust severity `C` than Red/Blue, controlling subgroup and draft year.
- **H2:** Within Yellow, Möbius prospects have worse `C` and more volatile weekly get-off than non-Möbius Yellow prospects.
- **H3:** Green prospects contain disproportionate verified-get-off bargains relative to draft capital.
- **H4:** `A`, `F`, `D`, square, and Möbius add out-of-time predictive value for `C` beyond draft capital + public Combine metrics.
- **H5:** Cohorts with more Yellow/Möbius exposure have worse cohort health and more busts (exploratory).
- **H6:** The movement traits driving `F`/`D` identify development priorities (e.g., braking/path consistency vs. first-step acceleration).
- **H7:** Player fragility compounds: joint failure exceeds additive/independent prediction.
- **H8:** Team/cohort failures cluster beyond independence (`Δ_team > 0`).
- **H9:** A subset of high-fragility players/teams is resilient; resilient and captured profiles differ on pre-specified movement/context features.

## Splits and validation

- Discovery: 2023; internal validation: 2024; confirmatory test: 2025 (run once).
- Train 2023–2024, test 2025; leave-one-draft-year-out as a secondary check.
- GroupKFold by `nfl_id`; no player overlap.
- Context residual model cross-fitted by player; archetype alignment learned out-of-fold only.
- No career outcomes, future seasons, or draft capital as predictors in the translation model.
- Player-cluster bootstrap (≥2,000 reps for primary effects); Benjamini–Hochberg FDR q < 0.10 for secondary tests.
- Threshold sensitivity: post thresholds vs. data-driven quartiles.

## Gate evidence

See `docs/gate_decision.md` and `outputs/audit/gate_scorecard.csv`. DL scored 6/6 on the pre-registered gate; WR was the backup.

## Change control

Any change to the primary outcome, focal trait, or hypothesis family must be logged here with a date and reason before the 2025 holdout is run. Exploratory analyses are labeled as such.
