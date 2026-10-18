# Repository appendix — broader lens scan (exploratory)

This appendix records the exploratory lenses that are summarized in the writeup but not reproduced in the compact public notebook. They are **not confirmatory** and are reported as wide nulls or descriptive results. The robust core is the Combine movement → performance linkage and the role persistence/performance-null result.

## Data corrections

- Regular season only: PRE 51,759 and POST 13,169 rows excluded.
- `LA` → `LAR` normalization: between-season team changes 37 → 27; mid-season moves 13.
- Panel: 722 player-seasons / 401 players; DL 177 / 98.
- DB performance residual: reliability 0.12, zero variance; unidentifiable. Excluded from pooled performance models; role persistence reported descriptively.

## Yellow / RJF lens

- Full static DL H1 (all draft years; includes 2023 whose archetype uses a later class): Yellow − Red/Blue C = **+0.176** (95% CI −0.020 to 0.357, p = 0.077, n = 30).
- 2024–25 only (strictly prior archetype): **+0.144** (95% CI −0.070 to 0.351, p = 0.18, n = 23).
- Dynamic squared state (strict prior-class archetype; 2023 unassigned): 177 DL rows; Yellow 17, Blue 11, Red 8, Green 31, Unassigned 110. The Yellow/Blue contrast is flat.
- Möbius movement-state and weekly flip/dwell: null; 2 strict flags.
- Interpretation: wide nulls, not evidence of absorption. The RJF transition-zone archetype does not add detectable incremental signal in this cohort.

## Pond / price-vs-prediction lens

- Price-vs-prediction summary classifications: 6 irrelevant, 6 no detectable increment, 1 residual opportunity (`role_share_room → career status`, ΔR² +0.073). The latter is a role/allocation variable, not a pre-draft signal.
- Pond mismatch and pond-upgrade features: no detectable incremental signal.
- The preregistered pond step-up and T4−T3 incremental gate were underpowered/wide; the role analysis was added after them and is labeled exploratory in the writeup.

## Cross-position replication

| Group | Players | Yellow | Red/Blue | Diff in C (95% CI) | p |
|---|---:|---:|---:|---:|---:|
| WR | 76 | 14 | 10 | −0.045 (−0.285, 0.218) | 0.79 |
| OL | 80 | 13 | 18 | +0.121 (−0.059, 0.289) | 0.21 |
| DB | 83 | 11 | 27 | +0.139 (−0.076, 0.332) | 0.29 (measurement check) |
| TE | 27 | 4 | 7 | too few | — |

## Salary extension (exploratory, 2023–2025)

- Team panel: 96 team-seasons; OTC positional spending is the primary star measure; 2025 archived OTC cap pages supply the player-level cap ledger.
- Star share → wins per $100M: −0.70 (95% CI −10.23 to +8.83, p = 0.89); the null holds for point differential and offensive EPA per dollar.
- Rookie snap share → wins: −28.39 (−47.96 to −8.82, p = 0.004), or −2.84 wins per 10 percentage points.
- Homegrown snap share → wins: +9.21 (+3.81 to +14.62, p = 0.001), or +0.92 wins per 10 points. Point differential and offensive EPA per play agree.
- QB quadratic: linear +42.37, quadratic −149.17 (p ≈ 0.07), inflection at a QB share of 14.2% of offense+defense spending. The 2025 top quartile of QB cap share wins 8.31 versus 8.56 for the rest; point differential −5.5 versus +1.8.
- Rent proxy (2025): pay model R² 0.438. Q4−Q1 total rent −$20.5M (bootstrap CI −$40.9M to −$2.0M); underperformer rent −$6.3M (−$14.5M to −$0.2M); youth surplus +$1.9M (+$0.1M to +$4.0M); star rent −$14.2M (CI −$29.3M to +$0.7M). Cash-pay sensitivity: star −0.31, underperformer −0.29, youth +0.32 correlations with wins per $100M.
- Soccer table: five clubs, illustrative; full source notes in `docs/SOCCER_DATA.md`.

## Week-to-week check (exploratory)

- 3,885 player-weeks across 249 players (DL/WR/TE/OL; DB and LB weekly samples are too thin/unidentifiable).
- Model: `next_week_role_z ~ role_week_z + perf_week_z + B_draft + C(group) + C(season) + C(week)`, cluster-robust by player.
- Current-week role: **+0.753** (95% CI 0.717 to 0.788). Current-week performance: **−0.006** (−0.027 to 0.015, p = 0.586). Draft capital: +0.116 (0.008 to 0.225).
- Early/late split (282 player-seasons, 180 players): early role +0.741 (0.639 to 0.842); early performance +0.008 (−0.072 to 0.087, p = 0.846); draft +0.093 (ns).
- Interpretation: role is sticky week to week; performance does not move next-week role. The operational conclusion is a **4–6 week rolling review**, not a single-week trigger.

## What moved out of the writeup

The role-measure sensitivity figure and the role-gap tail figure remain in the
repository but are no longer in the writeup. The soccer comparison table now
lives in `docs/SOCCER_DATA.md`; only a one-line pointer remains in the writeup.
The Football scorecard table replaced the soccer table in the body. The
role-gap tails remain descriptive: high-role/low-performance 9 player-seasons
across 7 players; low-role/high-performance 13 across 11; next-role difference
1.04 (player-clustered 95% CI 0.53 to 1.49).

## What was cut after adversarial review

The earlier “predictability premium,” “rent,” and “suppression” interpretations were not robust:

- The volatility → role-gap coefficient collapses when current role is controlled (+0.02, p = 0.82) and is partly a play-count artifact.
- Career status is cumulative snaps; role predicts career snaps mechanically. The old career-snap “rent” label is dropped. The salary extension's rent proxy is a separate, cap-based pay-performance residual and is labeled descriptive, not causal.
- “Absorption” and “suppression” implied more than a wide null; the final writeup uses “no detectable increment” and treats the role allocation result as descriptive/exploratory.

## Code

- `scripts/03_build_features.py`, `04_build_squares.py`, `05_test_hypotheses.py` — Yellow/Möbius/pond lens.
- `scripts/07_build_dynamic.py`, `08_replicate_positions.py`, `12_price_prediction.py` — dynamic, replication, price-vs-prediction lenses.
- `src/discovery/role_allocation.py`, `src/discovery/combine_linkage.py`, `src/discovery/weekly_role.py`, `src/features/combine_movement.py` — final core and week-to-week check.
- `src/salary/{otc.py, otc_cap.py, contracts.py, roster.py, performance.py, team_panel.py, analysis.py, rents.py, soccer.py}` — salary extension.
- `src/viz/figures.py` — core figures; `src/viz/salary_figures.py` — combined core and salary figures.
- `docs/EXTERNAL_DATA.md`, `docs/SOCCER_DATA.md` — external sources and scope notes.
- `notebooks/02_final_public.ipynb` — compact public reproduction of the core and salary panel.

## Caveats

- 2023 is excluded from the final Yellow coefficient because its archetype would use a later class.
- DB performance is unidentifiable; DB role persistence is descriptive.
- Transition/pond samples are small (27 team changes, 13 mid-season moves); no strong claims.
- The salary panel is 96 team-seasons; OTC positional spending is not a full cap ledger; the rent sample covers 69% of 2025 active-cap dollars because OL and specialists are excluded.
- All role/rent/predictability/salary/weekly analyses are observational and exploratory; no causal claims.
- The weekly check is player-week snap share, not depth-chart rank; opponent, injury, scheme, and coaching controls are unavailable. It is a 4–6 week review aid, not a weekly verdict.
- The soccer table uses different accounting scopes and season windows; it is illustrative.
