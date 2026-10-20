# The Combine burst predicts pressure; the allocation gap has a price

## Part 1 — What the data show, and what they imply

The 10 Hz Combine burst predicts regular-season pressure for interior defensive linemen; the stopwatch does not. The allocation pattern that follows is measurable, and the contract market prices it. The argument is tiered: each tier says what it can support. Samples: 543 player-seasons, 233 with a next season, 909 in the 2025 cap ledger, and 306 2026 free-agent contracts.

### Tier 0 — What the data alone show

**The pressure signal.** For interior defensive linemen, average the Combine z-scores for max speed and first-step acceleration. The top tercile generates 3.83% pressure per defensive snap, the bottom 2.47% (+1.4 points); sacks run 0.97% versus 0.35% per pass rush (2.7×). The middle is flat (2.25%), so the signal is a top-versus-bottom contrast, not a gradient. The burst predicts pressure at +0.354 SD per SD (95% CI 0.143 to 0.565, n=64) and sacks at +0.317 (0.083 to 0.550, n=63), controlling draft and season. Edge rushers show a smaller pressure signal (+0.157) and no sack signal (+0.035).

**The stopwatch does not carry the pressure signal.** In the timed interior sample, the 40-yard dash and 10-yard split jointly explain pressure with p=0.998; the burst adds +0.049 R². Out of sample, by player, the stopwatch scores −0.113 for pressure and the burst +0.178. For sacks the stopwatch is positive (+0.120) and the burst adds only +0.007 R². The 10 Hz burst is not a better sack model; its value is pressure.

**Concentrated in interior linemen.** The movement composite predicts defensive-line performance (+0.734 raw; +0.42 SD per SD, 0.26 to 0.58, n=175), but not offensive line (+0.058) or tight end (+0.093); receiver is marginal (+0.366, p=0.084). The Combine-movement interaction is p=0.0004; the burst-pressure interaction is p=0.137 and is not significant. The claim is concentrated in interior linemen, not universal.

![Figure 1. A: the burst predicts pressure where the stopwatch does not. B: the Combine signal is concentrated in interior linemen.](https://raw.githubusercontent.com/PatrickMockridge/nfl-big-data-bowl-2027/main/writeup/figures/measurement_panel.png)

**Cap charge is associated with performance.** On the full 909-player 2025 ledger, a standard deviation of measured performance is associated with +0.328 log points of cap charge (95% CI 0.264 to 0.392), controlling age, experience, and position. Adding playing time gives +0.143 (0.078 to 0.208). The salary measure is nflverse production, partly role-loaded (r≈0.5 with snaps), not the NGS residual.

**The depth chart does not detectably reward performance.** Current playing time (+0.606) and draft capital (+0.785) predict next-season playing time; the performance coefficient is −0.011 (95% CI −0.119 to 0.097, n=233). The concurrent estimate is −0.132 (p=0.031), marginal; a shuffle gives −0.10; the within-player estimate is −0.095 (p=0.11, n=235). This is absence of evidence, not proof of zero.

![Figure 2. A: cap charge is associated with measured performance. B: next-season role follows current role and draft, not performance.](https://raw.githubusercontent.com/PatrickMockridge/nfl-big-data-bowl-2027/main/writeup/figures/pricing_allocation_panel.png)

### Tier 1 — What the pattern implies

The performance-role gap by draft is +0.59 SD for late picks and undrafted players and −0.92 for early picks (n=233; +0.28 and −0.93 in the reliable 192). The group means show why: the role spread is 1.462 SD versus a performance spread of 0.046, so the gap is mostly role. A two-agent model calibrated to the same equations reproduces the pattern: the coach's performance weight is −0.13 (shuffle −0.10, p=0.10), the GM's +0.14; the cross-construct difference is +0.28. Aligning the coach to the GM raises the top group's role by 0.32 SD in the model. Model-reproduced, not identified. The strict tail is 13 player-seasons (12 players), a review list, not a population.

![Figure 3. A: the allocation gap by draft. B: the coach/GM cross-construct difference.](https://raw.githubusercontent.com/PatrickMockridge/nfl-big-data-bowl-2027/main/writeup/figures/gap_agent_panel.png)

### Tier 2 — What the market pays

Using public, free contract data — the competition host confirmed this is appropriate — the 2026 free-agent class gives an APY role premium of **+0.179 log points** (95% CI 0.022 to 0.336, n=306); the 2025 cap ledger gives **+0.185** (0.094 to 0.276, n=909); the draft-matched 2026 gap is **+0.151** (0.016 to 0.286). A median team's class carries **$7.05M a year of uncut modeled role premium**. At the base **0.40** capture assumption, the annual capture is **$2.82M gross / $1.82M net** after a **$1M** implementation cost. The conservative EDGE/S/CB subset is **$1.38M uncut but −$0.45M capture**: it does not cover the cost. The premium is concentrated: the top 10% of contracts carry **51%** of it. It is also fragile: adding contract length and guarantee share as commitment controls reduces the gap to **+0.049** (−0.093 to 0.191, n=253). The 2025 APY cross-check is +0.105 (CI crosses zero); 2024 is +0.029. These are associations, not causal estimates; the dollar is a scenario, not a forecast.

![Figure 4. Median team: $7.05M uncut; capture $2.82M gross / $1.82M net at 0.40.](https://raw.githubusercontent.com/PatrickMockridge/nfl-big-data-bowl-2027/main/implications/free_agency/writeups/figures/fa_headline.png)

![Figure 5. The role premium across cuts: +0.179 unconditional; +0.076 with years; +0.150 with guarantees; +0.049 with both.](https://raw.githubusercontent.com/PatrickMockridge/nfl-big-data-bowl-2027/main/implications/free_agency/writeups/figures/fa_role_premium.png)

**Table 1. The dollar is a scenario.**

| Scenario | Positions | Uncut annual | Capture gross | Capture net |
|---|---|---:|---:|---:|
| Base, 0.40 | all | $7.05M | $2.82M | $1.82M |
| Conservative, 0.40 | EDGE/S/CB | $1.38M | $0.55M | −$0.45M |
| Low, 0.15 | EDGE/S/CB | $1.38M | $0.21M | −$0.29M |

n=306 APY contracts; 2025 cap n=909; $1M implementation cost.

### Tier 3 — What to do

**Coach:** review the largest role gaps on a 4–6 week cadence; the strict tail is 13 player-seasons. **GM:** the cap is not the problem; use the interior-DL Combine on the board. **League:** the gap is consistent with a role pipeline, not a proven structural cause. **Youth:** late picks performing above role are the development target. The RJF/transition-zone test is a wide null; treat it as fallback evidence. None of these is a tested intervention.

**Table 2. Football scorecard.**

| Criterion | Evidence | Use | Caveat |
|---|---|---|---|
| Week-to-week usability | Snaps persist; performance adds no detectable next-week or next-season signal. | Review the largest role gaps; no tested cadence. | Absence of evidence; snaps are not depth-chart rank. |
| Complexity | Interior-DL Combine; 543 performance rows; 233 role rows; 909 cap rows; 306 contracts. | One analyst can maintain it; output is a short review list. | Measures differ by position; DB excluded. |
| Uniqueness | Cap charge is associated with performance; the depth chart does not detectably reward it. | Ask whether the depth chart uses the signal the testing shows. | A pattern, not a causal claim. |

## Part 2 — Method and evidence

### Data

The 2023–2025 Combine cohorts: 510 players; 401 with 722 regular-season player-seasons; 10 Hz tracking; NGS `player_play`; nflverse snaps and production; OTC positional spending (96 team-seasons), archived 2025 OTC active-cap pages (32 teams), and a public contract snapshot. The contract-market section uses the 2026 free-agent class (1,086 contract rows; 306 with a usable APY and prior-season performance) and the 2025 cap ledger (909 players). Salary data are publicly available and free; the competition host confirmed this is appropriate (discussion 751037).

### Measures

**Combine movement.** Attempt-level z-scores within drill and position for max speed, first-step acceleration, time to 1 yard (reversed), and path efficiency; the interior burst is the average of the standardized speed and acceleration components; the stopwatch is the 40 and 10-yard split, faster is better.

**Performance and role.** Position-specific play outcome residualized against context (down, distance, pressure, coverage, field position, motion, blitz, season) with ridge and 5-fold grouped cross-validation; empirical-Bayes shrunk and standardized. Pressure is the share of defensive snaps with a recorded pressure; sacks are the share of pass-rush snaps with a sack. Playing time is snaps per appearance, standardized within position and season. The allocation gap is performance z minus playing-time z; positive means the player performs above his role.

**Cap and contract.** For 2025, log cap number is modeled on performance, age, experience, and position on the 909-player ledger; adding playing time gives the role-controlled model. For the 2026 class, log APY is modeled on prior-season performance, age, experience, team change, position, and prior snap share; the role premium is the raw minus role-controlled performance coefficient. The dollar counterfactual holds the raw-model level and removes the part of the performance weight the role control absorbs; it uses Duan smearing and a 0.40 capture haircut.

### Models

OLS with player-clustered standard errors; salary models cluster by team with season controls. The Combine models link 10 Hz tracking to regular-season NGS pressure and sacks; they are position-specific. The role models use current role, performance, draft capital, position, and season; the cap model is the 909-player ledger; the contract models use the 2026 class and the 2025 ledger. The agent model calibrates the coach role equation and the GM pay equation; it is a consistency check, not identification.

**Table 3. Selected models.**

| Model | Term | Coefficient (95% CI) | n |
|---|---|---|---:|
| Interior burst → pressure | Burst | +0.354 (0.143, 0.565) | 64 |
| Interior burst → sacks | Burst | +0.317 (0.083, 0.550) | 63 |
| Combine → performance, DL | Combine | +0.734 (0.461, 1.007) | 175 |
| Combine → performance, WR | Combine | +0.366 (−0.049, 0.781) | 149 |
| Next-season role | Performance | −0.011 (−0.119, 0.097) | 233 |
| Cap model, raw | Performance | +0.328 (0.264, 0.392) | 909 |
| Cap model, + role | Performance | +0.143 (0.078, 0.208) | 908 |
| Agent difference | Coach − GM | +0.28 (cross-construct) | 233/908 |

### Validation and robustness

The next-season model has out-of-sample R² 0.503; the performance coefficient stays between −0.038 and +0.026 across folds. The Combine coefficient is a cross-player association, not a season forecast. The position-specific estimates are exploratory; the interaction test is the stronger evidence. The pressure model is cross-player; the sack model is temporally more stable. The cap residual is an accounting residual; the role null is absence of evidence; the allocation gap is descriptive. The contract gap is a cross-sectional association.

**Table 4. What the contract result survives.**

| Check | Estimate | Read |
|---|---|---|
| 2025 cap ledger | +0.185 (0.094, 0.276, n=909) | anchor |
| Draft-matched 2026 | +0.151 (0.016, 0.286) | survives |
| 2025 active APY | +0.105 (−0.005, 0.214) | CI crosses zero |
| 2024 APY | +0.029 (−0.169, 0.227) | null |
| + years + guarantee | +0.049 (−0.093, 0.191, n=253) | not robust to contract structure |

### Limits

Observational; no causal claims. Playing time is snaps per appearance, not depth-chart rank or intent. Defensive-back performance is unidentifiable and excluded. Salary is a proxy: cap hits reflect proration, restructures, and timing; APY is not cash; the role premium is not a player ranking. Opponent, injuries, scheme, and game script are unavailable. The RJF/transition-zone analysis returned a wide null.

### Code

Public notebook: https://www.kaggle.com/code/patrickm/nfl-bdb-2027-the-allocation-gap

Code: [Combine movement](https://github.com/PatrickMockridge/nfl-big-data-bowl-2027/blob/main/src/features/combine_movement.py), [performance](https://github.com/PatrickMockridge/nfl-big-data-bowl-2027/blob/main/src/features/performance.py), [cost-risk](https://github.com/PatrickMockridge/nfl-big-data-bowl-2027/blob/main/src/discovery/cost_risk.py), [agent model](https://github.com/PatrickMockridge/nfl-big-data-bowl-2027/blob/main/src/framework/agentic_allocation.py), [free agency](https://github.com/PatrickMockridge/nfl-big-data-bowl-2027/tree/main/implications/free_agency).
