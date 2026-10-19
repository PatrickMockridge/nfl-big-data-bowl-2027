# Interior burst protocol — frozen before the final models

**Status:** exploratory re-analysis; protocol frozen 2026-10-19 before the final
model run. This is not a preregistered confirmatory test. The 2023–25 data were
already observed during the audit, so the out-of-sample tests below are
internal validation, not a pristine holdout.

## Question

Among interior defensive linemen, does a 10 Hz Combine burst (top speed plus
first-step acceleration) predict regular-season pressure and sacks, and does it
add information beyond the traditional 40-yard dash and 10-yard split?

## Sample

- 2023–2025 draft classes, Combine participants with a non-null
  `combine_movement` (510 players).
- Regular-season `player_play` rows only.
- `INTERIOR` = `nfl_position` in {DT, NT}; `EDGE` = {DE, OLB}.
- Player-season is the unit; cluster-robust standard errors by `nfl_id`.
- The timed subset (non-null `forty` and `ten_yd_split`) is used only for the
  drill-translation models.

## Metric

From `outputs/panel/combine_movement.parquet` (attempt-level z-scores within
drill × position group, averaged per player):

```
combine_speed = mean z(max_speed)
combine_accel = mean z(max_accel_first_05)
burst_raw     = (combine_speed + combine_accel) / 2
burst_z       = (burst_raw - mean) / sd   within position_subgroup,
                across the 510-player cohort (not the analytic sample)
```

The `burst_z` scale is fixed on the cohort so the analytic sample does not
determine its own scaling.

## Production outcomes

From `player_play.csv` and `games.csv`:

```
is_defense    = team_abbr != possession_team
def_snaps     = sum(is_defense)
rush_snaps    = sum(player_get_off.notna())          # pass-rush exposure
pressure      = sum(time_to_pressure.notna())
sacks         = sum(sack == True)
tfl           = sum(tackle_for_loss == True)
tackles       = sum(tackle == True)

pressure_rate = pressure / def_snaps
sack_rate     = sacks / rush_snaps
tfl_rate      = tfl / def_snaps
tackle_rate   = tackles / def_snaps
rush_share    = rush_snaps / def_snaps
```

Native rates are reported in percentage points. Standardized outcomes are
z-scored within `position_subgroup × season` and are labelled `*_z`. A
percentage-point coefficient is never labelled "z."

## Models

All OLS, `cov_type="cluster"`, groups `nfl_id`, unless stated.

1. **In-sample subgroup**
   `y ~ burst_z + B_draft + C(season_c)` for INTERIOR and EDGE separately;
   native-unit companion with `y` in percentage points.
2. **Interaction**
   `y ~ burst_z * INTERIOR + B_draft + C(season_c)`; report both simple slopes.
3. **Drill translation** (timed subset, n≈56)
   - M0: `y ~ B_draft + C(season_c)`
   - M_trad: `y ~ z(-forty) + z(-ten_yd_split) + B_draft + C(season_c)`
   - M_burst: `y ~ burst_z + B_draft + C(season_c)`
   - M_both: `y ~ burst_z + z(-forty) + z(-ten_yd_split) + B_draft + C(season_c)`
   - Report R², ΔR²(burst | traditional), ΔR²(traditional | burst), and the
     joint F for `forty = ten_yd_split = 0` in both M_trad and M_both. Label
     standalone vs conditional joint F explicitly.
4. **Out-of-sample**
   GroupKFold(5) by `nfl_id`, identical folds for M0/M_trad/M_burst/M_both and
   the generic composite benchmark; OOF R².
5. **Temporal**
   Train 2023–24, test 2025; no `C(season_c)` in the test model because 2025 is
   unseen. LOSO as a sensitivity.
6. **Team fixed effects**
   `y ~ burst_z + B_draft + C(season_c) + C(primary_team)` on INTERIOR; report
   both player-clustered and team-FE estimates.
7. **Role controls**
   Add `rush_share` and snaps/game; role is a mediator, so report both.
8. **Draft**
   `B_draft ~ burst_z + C(season_c)`; `log(draft_overall_pick) ~ burst_z +
   z(-forty) + z(-ten_yd_split) + C(season_c)` on drafted + timed. Report MDES.
9. **Cap**
   `log(cap_number) ~ perf_z + age_start + years_exp` on IDL, with and without
   `snap_share`. `perf_z` is nflverse public production, not NGS
   `player_play`. The direct NGS merge (n≈19) is descriptive only.
10. **Placebo and specification curve**
    EDGE is the placebo. Burst variants: speed-only, acceleration-only,
    equal-weight (primary), first principal component, rank average.
    Permutation: shuffle `burst_z` within `position_subgroup × season`, 1,000
    draws.

## Reliability

Split each player-season's plays by odd/even `play_id`; compute each half's
rate; Pearson r across player-seasons; Spearman–Brown `2r/(1+r)`. Report for
pressure and sacks. Do not disattenuate the headline.

## Multiplicity

Two primary outcomes: pressure and sacks. The primary contrast is the
incremental pressure R²/OOF. Holm correction across the two primary outcomes.
TFL, tackles, and all other subgroups are exploratory and labelled as such.

## Go/no-go

**GO only if:**

1. Phase 0 reproduction passes (n exact; coefficients ±0.05; CI endpoints
   ±0.10; R² ±0.02; OOF/temporal ±0.03).
2. INTERIOR pressure: `burst_z` > 0, p<0.05 player-clustered; ΔR²(burst |
   traditional) > 0; OOF burst > OOF traditional and > baseline; traditional
   OOF ≤ 0 for pressure.
3. Position specificity: EDGE pressure coefficient smaller and not significant
   at 0.05; interaction > 0, p<0.10. If the player-level interaction is null
   (it is currently p≈0.55), the claim must be narrowed to "DL burst" or the
   season-level test disclosed.
4. Sacks contrast: traditional joint p<0.05 in the standalone model; burst
   temporal R² > 0; both add.
5. Draft: the standardized coefficient is small and the CI excludes a large
   pricing effect; MDES reported.
6. No P0 in the pre-mortem; every writeup number traces to a CSV or notebook
   cell.

**Conditional go:** if pressure temporal R² ≤ 0 but in-sample + OOF +
stopwatch-negative-OOF hold, frame pressure as a cross-player scouting signal,
not a season forecast.

**Fallbacks, in order:** pressure-only cross-player claim; position-specific
burst story (7–8/10); position-specific Combine heterogeneity (6.5–7.5/10).
Never revive the pooled claim, cherry-pick a passing specification, drop the
EDGE placebo, or publish numbers that failed Phase 0.

## Phase 0 reproducible values (locked 2026-10-19)

The exploratory table that prompted this protocol used different outcome
z-scopes and denominators. The module now implements the definitions above;
these are the numbers the writeup may use. The exploratory values are
superseded, not reconciled by cherry-picking.

| Check | Pressure | Sacks |
|---|---|---|
| INTERIOR burst, in-sample (z per SD) | +0.354 (0.143, 0.565), p=0.001 | +0.317 (0.083, 0.550), p=0.008 |
| INTERIOR burst, native (pp per SD) | +0.644 (0.262, 1.026) | +0.270 (0.070, 0.469) |
| EDGE burst, in-sample (z per SD) | +0.157 (0.010, 0.305), p=0.036 | +0.035 (p=0.75) |
| Interaction (INTERIOR − EDGE) | +0.192 (−0.061, 0.445), p=0.137 | +0.277 (−0.034, 0.588), p=0.080 |
| Reliability (split-half r / SB), INTERIOR | 0.439 / 0.610 | 0.327 / 0.493 |
| Reliability (split-half r / SB), EDGE | 0.270 / 0.425 | 0.084 / 0.155 |
| R² traditional / burst / both | 0.245 / 0.295 / 0.295 | 0.279 / 0.183 / 0.287 |
| ΔR² burst over traditional / traditional over burst | +0.049 / +0.0001 | +0.007 / +0.104 |
| Conditional joint F for 40 + 10-yard split | p=0.998 | p=0.023 |
| OOF R² baseline / traditional / burst / both | 0.105 / −0.113 / 0.178 / −0.211 | −0.052 / 0.120 / 0.059 / 0.069 |
| Temporal 2023–24 → 2025 R² baseline / traditional / burst / both | −0.213 / −0.170 / −0.045 / −0.070 | 0.105 / 0.066 / 0.182 / 0.059 |
| LOSO R², burst | −0.065 | +0.064 |
| Team FE, burst | +0.298 (−0.045, 0.640), p=0.089 | +0.463 (0.040, 0.886), p=0.032 |
| Role controls, burst | +0.362 (0.172, 0.552), p<0.001 | +0.307 (0.072, 0.541), p=0.010 |
| Draft `B_draft` ~ burst | +0.034 (−0.044, 0.111), p=0.39 | — |
| Draft log(pick) ~ burst (timed) | −0.150 (−0.623, 0.323), p=0.53 | — |
| IDL cap ~ nflverse performance | +0.437 (0.290, 0.584), p<0.001; +0.252 (0.093, 0.410) with snap share | — |

Interpretation:

- The **drill-translation contrast survives**: the stopwatch predicts sacks
  (conditional joint p=0.023) but not pressure (p=0.998); the burst predicts
  pressure and adds +0.049 R² over the stopwatch; the stopwatch's pressure OOF
  is −0.113 while the burst's is +0.178.
- The **pressure temporal forecast is negative** for every model (−0.045 for
  the burst). The pressure claim is a cross-player scouting signal, not a
  season forecast.
- The **position-specific claim is weaker than the exploratory version**: EDGE
  pressure is +0.157 (p=0.036), the interaction is p=0.137. The correct wording
  is "concentrated in interior linemen (2.3× the edge coefficient)," not
  "absent in edge."
- The **sack signal is positive in-sample and temporally** (+0.317; temporal
  +0.182), but the stopwatch is the stronger sack model and the burst adds only
  +0.007 R² over traditional timing. Sacks are the robustness anchor, not a
  tracking-unique finding.
- The **specification curve**: speed-only pressure +0.267 (p=0.043), sacks
  +0.304 (p=0.019); acceleration-only pressure +0.284 (p=0.024), sacks +0.152
  (p=0.27); equal-weight pressure +0.354 (p=0.001), sacks +0.317 (p=0.008);
  rank-average pressure +1.79 (p=0.002), sacks +1.57 (p=0.012). The PC1 of
  speed/acceleration is a contrast, not a burst (speed and acceleration are
  negatively correlated within interior, r=−0.09); do not use it as a
  robustness check.

## Go/no-go decision after Phase 0

- **Pressure in-sample / incremental / OOF:** pass.
- **Position specificity:** fail at the pre-specified p<0.05 EDGE threshold
  (EDGE p=0.036; interaction p=0.137). The claim must be narrowed to
  "concentrated in interior," or the entry must be framed as a drill-translation
  result rather than an interior-only result.
- **Sacks contrast:** pass (traditional joint p=0.023; burst temporal +0.182),
  but the burst's incremental sack value is small (+0.007).
- **Draft:** pass as a null (CI excludes a large pricing effect; MDES to be
  reported).
- **Temporal pressure:** fails; conditional-go framing applies (cross-player
  scouting signal, not a season forecast).
- **Decision:** conditional go on the **drill-translation** entry. Realistic
  target 8–8.5, not 9+, unless the re-audit's Football/Writeup/Viz scores
  compensate for the DS caveats.

## Change log

- 2026-10-19: protocol created after the audit and exploratory re-analysis.
  Frozen before the final model run.
