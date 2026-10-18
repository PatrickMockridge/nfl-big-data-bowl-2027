# Preregistration v2 — Transition Premium Across Scales

Frozen: 2026-10-18, before the broadened panel analysis.
Supersedes the DL-only preregistration for the broadened tests.

## Data corrections (applied)

- **Regular season is primary.** `player_play` includes 51,759 preseason and 13,169 postseason rows. The earlier DL analysis pooled them. Primary panel: `season_type == "REG"`.
- **Team abbreviation normalization:** `LA` → `LAR`. Without it, 10 Rams players create spurious team changes.
- **Corrected panel:** 722 regular-season player-seasons, 401 players. DL: 177 player-seasons, 98 players. (All-season: 922/497; DL 212/115.)
- **Corrected transitions (regular season):** 27 between-season team changes (27 players); 13 mid-season multi-team player-seasons (12 players); 49 primary-role-label changes (43 players). DL: 10 team changes, 5 mid-season multi-team, 1 role-label change.
- **No Yellow DL team changers.** A Yellow × team-change interaction is not estimable; report the zero and use continuous pond variables instead.
- **Freeze:** one build; re-run `scripts/03`–`05` on regular season. No stale artifacts.

## Scope and identifiability

| Scale | Operationalization | n (regular) | Status |
|---|---|---|---|
| DL rookie Yellow | `C_abs` vs Red/Blue | 16 Yellow, 14 Red/Blue | Replication (fragile) |
| Rookie pond step-up | `pond_mismatch` → `C_abs` | 98–115 DL | **Primary broadened test** |
| NFL room competition | `team_dl_competition` → `C_abs` | 98–115 DL | Primary/secondary |
| Veteran team change | `pond_upgrade` → `ΔC` | 10 DL / 27 all | Descriptive case series |
| Mid-season move | multi-team season | 5 DL / 13 all | Descriptive case series |
| Role change | role-share change | 53 DL | Mediator/outcome, not predictor |
| WR replication | separation over expected | 106 players (effective ~72) | Replication |
| OL replication | pressure allowed | 121 players (effective ~67) | Replication |
| DB measurement check | allowed completion | 118 players (effective ~14) | Not a replication test |

## Primary hypotheses (DL, regular season)

- **P1 (Yellow replication):** Yellow rookies have higher `C_abs` than Red/Blue. Report the regular-season estimate with bootstrap CI; the original all-season estimate is descriptive.
- **P2 (Rookie pond step-up):** `pond_mismatch` (college dominance minus conference strength) predicts higher `C_abs` beyond the strong baseline. Continuous predictor primary; big-fish-small-pond binary descriptive only.
- **P3 (Incremental gate):** The RJF/pond state (T4) improves leave-one-player-out prediction of `C_abs`/bust beyond the strong baseline (T3). **Primary gate.** If ΔR²/AUC CI includes zero, interactions are descriptive only.
- **P4 (Veteran pond upgrade):** `pond_upgrade` predicts higher `ΔC` for team changers. Underpowered; report as a case series and MDES, not a significance test.

## Secondary/exploratory

- S1: `Mob_t` within Yellow predicts `C_abs` (n=16; MDES |ρ|≈0.65).
- S2: `R_{t−1}` predicts future `C_t`.
- S3: Team/cohort clustering of bust residuals (permutation).
- S4: Weekly volatility increases after a setup change (case series).
- S5: Cross-position `pond_mismatch` sign consistency (WR/OL).
- S6: College pond does not predict veteran `C` given prior `C` (negative control).

## Definitions

- `B_draft` = draft-capital percentile within position subgroup and draft year; UDFA = 0.
- `B_t` = `0.7 B_draft + 0.3 B_status,t`, where `B_status,t` uses prior-season role share and prior `C_abs`; rookies use `B_draft`.
- `A_t` = Combine archetype alignment learned from **strictly prior draft classes**; 2023 is excluded from confirmatory dynamic tests (no prior class). Role-fit alignment may be added only from prior-season data.
- `F_t/D_t` = weekly residual sign flips and dwell (temporal Möbius); standardized within position/season.
- `C_abs` = `1 − percentile(shrunk get-off residual | B_draft, subgroup, season)`.
- `C_dyn` = `1 − percentile(shrunk residual | B_draft, prior residual, prior role share, subgroup, season)`; rookies = `C_abs`.
- `Yellow_t` = `B_t ≥ median` and `0.30 ≤ A_t ≤ 0.70`.
- `Phi_t` = cross-fitted `P(bust | prior information only)`; no same-season role or performance.
- `R_t` = calibrated `C_t` minus observed `C_abs,t`; positive = resilient.
- `pond_mismatch` = `z(college_dominance) − z(conference_strength)`; residualize on `B_draft` for the incremental test.
- `team_dl_competition` = mean z(room size, teammate draft strength, teammate prior performance); leave-one-out.
- `pond_upgrade` = `team_dl_competition_t − team_dl_competition_{t−1}`.

## Validation

- **Primary:** leave-one-player-out (GroupKFold by `nfl_id`). Every season of a player in one fold.
- **Secondary:** leave-one-season-out; 2025 temporal check. The 2025 data was already observed in the earlier analysis, so it is **not** a pristine holdout.
- Nested tuning within training folds; no test-fold peeking.
- Baseline tiers: T0 null; T1 scouts (draft/college/age); T2 + Combine/NGS/tracking; T3 + prior role/competition/scheme/prior performance; **T4 + RJF/pond state**. Headline = T4 − T3.
- Metrics: out-of-sample ΔR², ΔAUC, ΔBrier, calibration slope/intercept, Spearman; 95% player-cluster bootstrap CIs; MDES.

## Leakage rules

- `A_t` and `Phi_t` use only prior-season information; no same-season role, snap share, or performance.
- `C_t` and `R_t` are outcomes, never predictors of themselves.
- Transition variables use only past/current information; realized role-share change is a mediator/outcome.
- `2023` is excluded from confirmatory dynamic tests because no strictly prior archetype exists.
- Test: recompute `A_t`/`Phi_t` with all data after `t` masked; assert identical values.

## Power / MDES (planning)

- Yellow vs Red/Blue, DL regular: n=16 vs 14; MDES ≈ 0.30 C units (~1.0 SD).
- `pond_mismatch` incremental R², DL n≈98, 10 predictors: MDES ≈ 0.09 ΔR².
- Team changes, DL regular: n=10; paired MDES ≈ 0.31 C units (~0.9 SD); report case series.
- DB reliability 0.121 (effective n≈14): measurement check only.

## Negative controls

Outcome permutation within position-season; placebo transitions matched on B/role; future pond upgrade predicting current C; college pond predicting veteran C given prior C; DB canary; preseason-only performance; LA/LAR audit.

## Change log

- 2026-10-18: v2 created after confirming preseason/postseason contamination, LA/LAR artifact, and corrected transition counts. Primary broadened test moved from veteran team changes to the rookie college-to-NFL pond step-up. DL regular season is the confirmatory panel.
- 2026-10-18 (amendment): the role-allocation, within-player, and Combine-movement analyses were added after the preregistered tests. They are labeled exploratory in the writeup and are not confirmatory. The DL Yellow result is reported for 2024–25 only, where the archetype uses strictly prior classes.
- 2026-10-18 (amendment 2): the salary extension was added after the preregistered tests. It is exploratory and observational. The primary star measure is OTC positional spending; the 2025 archived OTC cap ledger is used for the rent proxy. The rent residual is a cap-allocation residual, not a causal rent. The soccer table is illustrative and uses public club accounts with different accounting scopes and season windows.
- 2026-10-18 (amendment 3): the week-to-week role check was added after the main results to answer the competition's Football-score question. It is exploratory: player-week snap share, weekly performance residuals, and a lead-lag model with role, performance, draft capital, position, season, and week controls. It is reported as a 4–6 week review aid, not a single-week trigger.
