# Position-group gate decision

Date: 2026-10-18. Frozen before any 2025 holdout analysis.

## Scorecard

| Group | Players | Best outcome reliability (Spearman–Brown) | Best abs. screen ρ | Sample | Reliability | Signal | Total |
|---|---:|---:|---:|---:|---:|---:|---:|
| **DL** | **118** | **0.953** | **0.638** | 2 | 2 | 2 | **6** |
| WR | 106 | 0.675 | 0.122 | 2 | 2 | 0 | 4 |
| TE | 42 | 0.449 | 0.232 | 1 | 1 | 1 | 3 |
| OL | 121 | 0.553 | 0.106 | 2 | 1 | 0 | 3 |
| DB | 118 | 0.121 | 0.195 | 2 | 0 | 1 | 3 |

Source: `outputs/audit/gate_scorecard.csv`, `outcome_reliability.csv`, `translation_screen.csv`.

## Decision

**Frozen focus: defensive line (`combine_position == "DL"`).**

- 115 players have game snaps; 118 are in the DL Combine cohort.
- Primary outcome: `player_get_off` — time from snap until the rusher crosses the line of scrimmage. Lower is better. 43,312 non-null observations; split-half ρ = 0.910, Spearman–Brown = 0.953.
- Position subgroups: EDGE (DE + OLB) = 63 players; INTERIOR (DT + NT) = 52. Pool with subgroup fixed effects; report subgroup results separately.
- All DL drills are well covered: `PASS_RUSH_DRILL` (85), `FOUR_BAG_AGILITY_DRILL` (85), `BODY_CONTROL_DRILL` (84), `FRONT_START_WAVE_DRILL_AND_LATERAL_REACTION` (83), `RUN_AND_CLUB_DRILL` (83), `RUN_THE_HOOP_DRILL` (80), plus 40/3-cone/shuttle.

## Why DL

- Highest outcome reliability of any group by a wide margin (0.953 vs. 0.675 for WR, 0.553 for OL, 0.121 for DB).
- Large, stable sample (115 players; median 247 get-off observations per player).
- Strong preliminary translation signal: path efficiency ρ = 0.638, max speed ρ = −0.579, max acceleration ρ = −0.428, mean direction change ρ = 0.458.
- Clean tracking: 0 of 6,310 attempts flagged; median speed-error 0.13 yd/s; no duplicate timestamps or gaps over 0.3 s in the audit.
- The competition explicitly lists trench play (first-step quickness, lateral agility, burst vs. pass-rush performance) as a target.

## Data quirks to respect

- `player_get_off` is non-null only on pass-rush rows (`blitzing=True` in 22,688 of 22,696 non-null rows). Treat it as a pass-rush get-off measure, not an all-snap measure.
- `time_to_pressure` / `quick_pressure` are sparse (4.6% of DL rows); use as secondary outcomes only.
- `PASS_RUSH_DRILL` has no rip/swim mapping; left/right in drill names may be alignment side, not break direction. Do not infer move type.
- `LEFT`/`RIGHT` in some skill-drill names may be alignment side; audit before using as a break-direction label.
- Community-flagged 2024 data trap: compare missingness/distributions by draft year before using 2024 in primary training.
- Data page says 316,338 `player_play` records; the shipped file parses to 314,197 records (327,019 physical lines, some quoted multi-line fields). SHA-256 `68926a…` matches the version cited in the organizer discussion. Record the actual count; do not force the data-page number.

## Novelty check

Public notebooks already cover DL bend, burst, and pass-rush kinematics. This entry does not re-derive a univariate drill-to-game correlation. Its contribution is the **Yellow transition-zone / Möbius early-warning framework**: bridge score (draft capital) × archetype alignment, movement-state flip rate and dwell time, fragility compounding, and counter-wise resilience. The DL outcome reliability makes that framework testable.

## Backup

WR (reliability 0.675, 106 players) is the backup if DL fails the preregistered out-of-time signal test. Do not switch after seeing the 2025 holdout.
