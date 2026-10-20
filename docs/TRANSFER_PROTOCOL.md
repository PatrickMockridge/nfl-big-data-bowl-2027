# Transfer protocol — weaker patterns from the same fundamentals

**Status:** pre-registration for a GitHub-only extension. This is not part of the
judged Big Data Bowl entry and does not modify the artifacts frozen at
`c652424`. Date-stamped **2026-10-20**. The transfer pilots are
**Tier 1 descriptive only**: no dollar model, no two-agent model, no causal
claims.

## Question

The judged entry's chain is: a 10 Hz measurement carries a performance signal the
incumbent stopwatch misses; the signal is essentially unpriced by draft capital;
the depth chart rewards status and prior role rather than the measured
performance; the cap pays performance. The pattern is an allocation gap between
a **status-legible** opportunity technology and a **performance-legible** pricing
technology.

Can the same three-link pattern be found, more weakly, in other areas of the Big
Data Bowl dataset? The pilots below test the links separately and report where
they fail.

## Template

| Link | Question | Tier 1 evidence | Falsified if |
|---|---|---|---|
| **L1. Measurement** | Does a task-matched 10 Hz signal predict the position's outcome beyond the incumbent cheap signal? | Standardized beta and 95% CI; signal and outcome reliability; incremental R² over the stopwatch/generic composite | Signal null, or dominated by the incumbent |
| **L2. Unpriced signal** | Is the signal weakly related to draft capital? | Signal–`B_draft` Spearman ρ with CI, contrasted with the 40/10-yard split | \|ρ\| ≥ 0.30 |
| **L3. Allocation** | Is measured performance unrewarded in next-season role while current role and draft are rewarded? | Existing per-position role equations, plus the performance-minus-role gap by draft quartile | Performance→role positive with CI excluding zero |

Tier 2 assumptions are used only as directional predictions:

- Risk aversion → the performance→role coefficient is flatter where outcome
  reliability is lower (attenuation).
- Cheap public status → draft and prior role dominate wherever a performance
  measure exists.
- Noisy, slow-updating performance → concurrent performance is a stronger
  correlate than next-season role response.
- Inside BDB there is no pay ledger; career opportunity is the only reward
  proxy.

The cross-position ordering is descriptive. With five position groups, no
meta-analytic p-value is reported.

## Data and samples

- Competition data only for the pilots; no external salary data.
- 510 Combine cohort players, draft classes 2023–2025.
- Five testable position groups: DB 118, DL 118, OL 121, TE 42, WR 106.
  LB (n=3) and OTHER (n=3) are excluded; the Combine file has no RB or QB rows.
- Player-season outcomes come from the existing panel:
  `outputs/panel/panel_full.parquet` (543 performance rows), and the role panel
  `outputs/discovery/role_allocation_player_seasons_full.parquet` (233 rows with
  a next season; 192 reliable rows).
- `game_tracking` tracks only the cohort players on each play (mean 1.6, max 6),
  not all 22. Relative defender–receiver metrics are out of scope.

## Fixed drill families

Membership is resolved to these exact `drill_name` values from
`outputs/audit/drill_counts.csv`. Attempts are aggregated to player × drill
first; family composites average drills with equal weight. All attempt-level
metrics are standardized within `drill_name × position_group` before
aggregation.

| Position | Family | Exact drill names |
|---|---|---|
| WR | route | CIRCUS_ROUTE_LEFT, COMEBACK_ROUTE_RIGHT, CURL_ROUTE_RIGHT, DAGGER_ROUTE_LEFT, GO_ROUTE_RIGHT, POST_CORNER_ROUTE_LEFT, POST_CORNER_ROUTE_RIGHT, RED_ZONE_FADE_RIGHT, SLANT_ROUTE_LEFT, SLOT_SAIL_ROUTE_RIGHT, SLOT_STRIKE_ROUTE_LEFT, SPEED_OUT_LEFT, SPEED_OUT_ROUTE_LEFT |
| WR | other | GAUNTLET_DRILL, OVER_SHOULDER_ADJUST |
| TE | route | COMEBACK_ROUTE_RIGHT, CORNER_ROUTE, CURL_ROUTE_RIGHT, DAGGER_ROUTE_LEFT, END_ZONE_FADE_RIGHT, FLAT_ROUTE_LEFT, GO_ROUTE_RIGHT, HOOK_ROUTE_RIGHT, IN_ROUTE_LEFT, OVER_SHOULDER_ADJUST, OVER_THE_SHOULDER_ADJUST, POST_CORNER_ROUTE_LEFT, POST_CORNER_ROUTE_RIGHT, RED_ZONE_FADE_RIGHT, SLANT_ROUTE_LEFT, SLOT_SAIL_ROUTE_RIGHT, SLOT_STRIKE_ROUTE_LEFT, SPEED_OUT_ROUTE_LEFT, WHEEL_ROUTE_LEFT |
| TE | block | BLOCK_EXPLOSION |
| DB | backpedal | BACK_PEDAL_AND_90_DEGREE_BREAK_TO_BALL, BACK_PEDAL_AND_TRANSITION_45_DEGREE_REACTION |
| DB | agility | BOX_DRILL, GAUNTLET_DRILL, LINE, LINE_DRILL, TERYL_AUSTIN_DRILL_1, TERYL_AUSTIN_DRILL_2, W_DRILL |
| DB | cod | SHORT_SHUTTLE, THREE_CONE_DRILL |
| OL | pass_set | PASS_PRO-MIRROR_DRILL, PASS_PRO_MIRROR_DRILL, PASS_RUSH_DROP |
| OL | pull | OL_PULL_DRILL_DEEP_SHORT_PULL_LEFT, OL_PULL_DRILL_FOLD_BLOCK_RIGHT, OL_PULL_DRILL_LONG_PULL_RIGHT |
| OL | mirror | FIVE_YARD_WAVE_DRILL_SLIDE_AND_SHUFFLE, SCREEN_DRILL |
| DL | pass_rush | PASS_RUSH_DRILL |
| DL | first_step | FRONT_START_WAVE_DRILL_AND_LATERAL_REACTION |
| DL | agility | BODY_CONTROL_DRILL, FOUR_BAG_AGILITY_DRILL, FOUR_BAG_SHUFFLE_DRILL, RUN_AND_CLUB_DRILL, RUN_THE_HOOP_DRILL |
| DL | cod | SHORT_SHUTTLE, THREE_CONE_DRILL |

The 40-yard dash, three-cone, and short shuttle are treated as incumbent
measurements, not as part of the skill-drill signal.

## Fixed primary tests

One signal–outcome pair per position. Higher signal = better movement; all
panel outcomes are oriented higher = better.

| Position | Primary signal | Primary outcome | Signal reliability | Outcome reliability |
|---|---|---|---:|---:|
| WR | `route_burst` = mean of `z_max_accel_first_05` and `-z_time_to_1yd` across WR route drills | `perf_z` (separation residual) | gate | 0.675 |
| TE | `route_burst` = same across TE route drills | `perf_z` (separation residual) | gate | 0.449 |
| DB | `transition_quick` = mean of `-z_time_to_1yd` and `z_path_efficiency` across DB backpedal drills | `perf_z` (coverage residual) | gate | 0.121 |
| OL | `pass_set_quick` = mean of `-z_time_to_1yd` and `z_max_accel_first_05` across OL pass-set drills | `perf_z` (pressure-allowed residual) | gate | 0.553 |
| DL | `pass_rush_burst` = mean of `z_max_speed` and `z_max_accel_first_05` on PASS_RUSH_DRILL | `perf_z` (get-off residual) | gate | 0.953 |

DL is split into INTERIOR (DT/NT) and EDGE (DE/OLB). INTERIOR is the positive
control; EDGE is the weaker secondary/placebo.

## Gates and decision rules

- **Signal gate:** family-level split-half reliability ≥ 0.50, odd/even drills
  within the family, Spearman-Brown corrected. Per-drill ICC is reported as a
  diagnostic.
- **Outcome gate:** split-half reliability ≥ 0.50 from the existing audit.
- **Sample gate:** primary test requires ≥ 60 players; 40–59 is exploratory
  only; < 40 is not tested.
- **Status vocabulary:** `supported` (beta > 0, CI lower > 0), `weak` (beta > 0,
  CI includes 0), `null` (beta ≤ 0 or CI upper < 0), `unidentifiable` (gate
  failed). No other positive label.
- **L2 rule:** `unpriced` if |ρ| < 0.20; `partly priced` if 0.20–0.30; `priced`
  if ≥ 0.30.
- **L3 rule:** reuse the per-position role equations in
  `outputs/discovery/role_allocation_positions.csv`. A performance→role
  coefficient with a CI excluding zero in the positive direction falsifies the
  allocation-gap reading for that position.

## Multiplicity

- The primary family is the five position tests that clear the gates; Holm
  correction within that family.
- Every individual drill-level estimate and every secondary metric is
  exploratory, with Benjamini-Hochberg FDR at q = 0.10.
- No fishing across drill families after seeing results. Any addition is labeled
  post-hoc.

## Expected result

The honest expectation, fixed before estimation, is mostly weak or null:

| Area | Expected L1 | Expected L2 | Expected L3 |
|---|---|---|---|
| DL pass-rush drill | Supported (positive control) | Unpriced | Null (already observed) |
| WR route drills | Weak | Unpriced for skill drills; stopwatch priced | Null (already observed) |
| OL pass-set drills | Weak or null | Unpriced | Null (already observed) |
| TE routes/blocking | Unidentifiable (0.449, n=42) | Descriptive only | Null (already observed) |
| DB backpedal | Unidentifiable (0.121) | Descriptive only | Unidentifiable |
| Burst outcome breadth | Pressure-adjacent positive; box-score null | n/a | n/a |
| Career reward ladder | Draft dominates; performance adds little | n/a | Start rate rises with draft |

## What would change the transfer claim

- The signal predicts its outcome but is already priced by draft (|ρ| ≥ 0.30):
  the mispricing leg fails.
- Performance→role is positive with a CI excluding zero: the allocation leg
  fails.
- Outcome reliability is below 0.50: the area is unidentifiable, not null.
- The drill-family signal is dominated by the stopwatch or the generic
  composite: the measurement leg adds nothing.

## Non-goals

- No dollar valuation, no two-agent calibration, no causal identification.
- No external salary or contract data.
- No modification of `writeup/`, `notebooks/02_final_public.ipynb`, or
  `implications/`.
- No claims about coaching intent, scheme, injuries, or unobserved fit.

## Reproduce

```bash
python scripts/20_transfer_drills.py
python scripts/21_transfer_signals.py
python scripts/22_transfer_breadth.py
python scripts/23_transfer_career.py
python scripts/24_transfer_figures.py
```

Bootstrap seed: **20261020**. Outputs: `outputs/transfer/`. Writeups:
`transfer/writeups/`.
