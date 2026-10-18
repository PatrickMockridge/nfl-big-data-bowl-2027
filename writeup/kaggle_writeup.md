# The testing is informative; the decisions are not

## Part 1 — For the boardroom

The Combine tests tell you how a player moves: top speed, acceleration, time to the first yard, path efficiency. They do not tell you the same thing about every position. And the decisions that follow — who plays, who is paid — reward status and predictability more than the movement signal itself.

We studied the 2023–2025 draft classes: 543 player-seasons with Combine movement and regular-season performance, 233 with a next season, and 909 players in the 2025 cap ledger.

### What we found

**The movement signal is position-specific.** Compare Combine movement with performance, holding position, season, and draft range constant. For defensive linemen the link is clear: +0.73 standard deviations of performance per unit of movement (95% CI 0.46 to 1.01), or +0.42 SD per SD. For receivers it is smaller and marginal (+0.37, p=0.08); for offensive linemen and tight ends it is not detectable (+0.06 and +0.09). The difference across positions is significant (interaction p=0.0004). The pooled +0.30 is a defensive-line result, not a universal one. The defensive-line outcome is get-off, a movement-adjacent measure, so part of that result is a tracking-validity check rather than a production claim. Figure 1 shows the position-by-position estimates.

![Figure 1. The Combine signal is real for defensive linemen, not universal.](https://raw.githubusercontent.com/PatrickMockridge/nfl-big-data-bowl-2027/main/writeup/figures/combine_linkage.png?v=3)

**The cap pays for status.** For 2025, we model each player's cap charge on performance, age, experience, and position, then keep the signed residual: dollars above or below the model, netted across over- and under-payments. No player is counted twice. Stars average about +$6.3M above the model; young high performers average −$1.1M. The top cap quartile averages +$6.4M per player; the bottom two quartiles average −$1.0M. Players aged 28–29 average +$3.5M; players 23 or younger average −$0.1M. Early draft picks average +$0.56M; late picks and undrafted players average −$0.91M. Figure 2 shows the gradient.

![Figure 2. The cap pays for status; measured performance fades once role and draft enter.](https://raw.githubusercontent.com/PatrickMockridge/nfl-big-data-bowl-2027/main/writeup/figures/net_rent.png?v=3)

The mechanism is visible in the nested pay model. Performance enters at +0.128 log points per standard deviation (p=0.006). Add playing time and the coefficient falls to +0.064 (p=0.23); add draft capital and it falls to +0.040 (p=0.22). Draft capital enters at +1.40 log points per unit. Once role and draft status are in the model, the cap's performance gradient is not distinguishable from zero. Part of that is the rookie wage scale: the cap formula itself pays draft status. The rest is a market that pays for a known role and a known draft slot.

**The depth chart pays for status too.** Current playing time (+0.606) and draft capital (+0.785) predict next-season playing time; performance does not (−0.011, 95% CI −0.119 to 0.097, n=233). The within-player test agrees: when the same player's performance changes, his snaps do not follow (−0.095, p=0.11, n=235). Figure 3 shows the drivers by position; Figure 4 shows the persistence and the within-player null.

![Figure 3. Current snaps and draft position predict next season; performance does not.](https://raw.githubusercontent.com/PatrickMockridge/nfl-big-data-bowl-2027/main/writeup/figures/next_role_forest.png?v=3)

![Figure 4. Snaps persist; a better season does not earn more snaps.](https://raw.githubusercontent.com/PatrickMockridge/nfl-big-data-bowl-2027/main/writeup/figures/persistence_within_player.png?v=3)

**The allocation gap is systematic.** Performance minus playing time, both standardized within position and season, is +0.59 for late picks and undrafted players and −0.92 for early picks in the full sample. In the reliable 192-row sample the gap is +0.28 and −0.93. The extreme group — top-quartile performance in the bottom role quartile — contains 13 player-seasons (12 players). Their mean gap is 2.24 SD, their mean draft percentile is 0.24, and their next-season role falls by 0.57 SD. The broader top-tercile/bottom-tercile group contains 23 player-seasons (21 players). Figure 5 shows the gap and the draft gradient.

![Figure 5. The depth chart is not allocated to measured performance.](https://raw.githubusercontent.com/PatrickMockridge/nfl-big-data-bowl-2027/main/writeup/figures/allocation_gap.png?v=3)

**The predictability lens is exploratory.** Volatility is associated with fewer snaps than performance and draft predict (−1.49, p<0.001), but the association disappears with current role controlled (+0.13, p=0.31).

### Why it matters

If a young player performs but sits, the team pays for a skill it is not using. If a veteran plays but does not perform, the team spends on playing time that produces little. The cap pays for performance, but also for draft status and role; the depth chart is the tighter constraint. The cost is the foregone production; the rent is the premium stars, veterans, and early picks capture above the model.

### What a team should do

Use the Combine test where it works: defensive-line get-off. Do not compare offensive linemen, tight ends, and defensive linemen on one movement score. Use the signed net rent and the performance-role gap as review lists: the cap staff sees who is paid above the model; the coaching staff sees who performs above his role. The data do not identify an optimal cadence; a monthly review is a process choice, not a tested rule. Name one accountable person — the head coach with the scouting department — and let analysts supply evidence. No algorithm sets a lineup.

### What this does not say

This is a pattern, not a controlled experiment. It does not say that more snaps will make a player perform, or that paying a quarterback less will win more. It does not prove intent. The cap residual is an accounting residual; the role gap is descriptive; the predictability result is exploratory. A flag is a reason to look, not a verdict.

**Table 1. Football scorecard.**

| Criterion | Evidence | Operational use | Status and caveat |
|---|---|---|---|
| Week-to-week usability | Snaps persist; performance does not move next-week or next-season role. | Review the largest performance-role gaps; no tested cadence. | Exploratory weekly check; snaps are not depth-chart rank. |
| Complexity | Position-specific Combine; 543 performance player-seasons; 233/192 role rows; 909 cap rows. | One analyst can maintain it; output is a short review list. | No private data; performance measures differ by position; defensive backs excluded. |
| Uniqueness | The testing signal is position-specific; the cap and depth chart reward draft status and role. | Ask whether the depth chart and cap sheet use the signal the testing shows. | A pattern in the data. No causal claim. Cap spending is an estimate, not intent. |

## Part 2 — Method and evidence

### Data

The 2023–2025 Combine cohorts: 510 players; 401 with 722 regular-season player-seasons. Combine tracking: 10 Hz. Performance comes from Next Gen Stats `player_play`; snaps and games from the tracking panel, with nflverse snap counts used in the salary layer. Salary data combine OverTheCap positional spending (96 team-seasons), archived 2025 OTC active-cap pages (32 teams; 99.3% of active-cap dollars match a 2025 snap on player ID and team), and a contract snapshot for sensitivity.

The performance sample is 543 player-seasons: 722 minus 165 defensive backs, 14 without a performance measure, 4 linebackers, and 3 others. The role sample is 233 with a next season, 192 with at least 50 performance plays. The cap sample is 909 players, 68.7% of 2025 active-cap dollars; offensive linemen and specialists are excluded.

### Measures

**Combine movement.** Attempt-level z-scores within drill and position group for max speed, first-step acceleration (0.5 s), time to 1 yard (reversed), and path efficiency. Attempt scores are averaged per player, re-standardized, and averaged into one movement score.

**Performance.** Position-specific play outcome, oriented higher-is-better: defensive-line get-off, receiver and tight-end separation, offensive-line pressure allowed, defensive-back pass result. Residualized against play context (down, distance, pressure, coverage, field position, motion, blitz, season) with ridge regression and 5-fold grouped cross-validation by player; empirical-Bayes shrunk and standardized within position group and season.

**Playing time.** Snaps per appearance, standardized within position group and season. The role gap is the residual from playing time regressed on performance, draft capital, draft-free prestige, position group, and season; positive means more snaps than comparable players.

**Signed net rent.** For 2025, log cap number is modeled on performance, age, experience, and position; the residual is dollars above or below the pay model. We report the signed residual, not a positive-part sum. The nested model adds playing time and `B_draft` to show how much of the performance gradient is absorbed by role and draft.

**Allocation gap.** Performance z minus playing-time z, both within position group and season. Positive means the player performs above his role.

### Models

OLS with player-clustered standard errors; salary models cluster by team with season controls. Table 2 reports selected estimates.

Combine linkages by position: defensive line +0.734 (0.461 to 1.007); receiver +0.366 (−0.049 to 0.781); offensive line +0.058 (−0.114 to 0.230); tight end +0.093 (−0.221 to 0.407); pooled +0.299 (0.153 to 0.446), n=543; interaction p=0.0004.

Next-season playing time: current playing time +0.606 (0.510 to 0.701); performance −0.011 (−0.119 to 0.097); draft capital +0.785 (0.347 to 1.222); n=233. Within-player change: −0.095 (−0.211 to 0.022, n=235). Weekly: next-week playing time on current-week playing time +0.753 (0.717 to 0.788); current-week performance −0.006 (−0.027 to 0.015); n=3,885 player-weeks, 249 players.

Signed net rent: stars +$6.3M; young high performers −$1.1M; cap quartiles −$0.98M, −$1.04M, +$0.48M, +$6.40M; early picks +$0.56M; late/UDFA −$0.91M. Nested pay model: performance +0.128 (0.037 to 0.219), +0.064 (−0.041 to 0.168) with role, +0.040 (−0.024 to 0.104) with role and draft; draft +1.40 (1.20 to 1.61); R²=0.646; n=153.

Allocation gap: full sample late/UDFA +0.59, early picks −0.92; reliable sample +0.28 and −0.93; strict tail 13 player-seasons, mean gap 2.24, next-season role −0.57; tercile tail 23 player-seasons.

**Table 2. Selected models (coefficient, 95% CI, n).**

| Model | Term | Coefficient (95% CI) | n |
|---|---|---|---|
| Combine → performance, DL | Combine movement | +0.734 (0.461, 1.007) | 175 |
| Combine → performance, WR | Combine movement | +0.366 (−0.049, 0.781) | 149 |
| Combine → performance, OL | Combine movement | +0.058 (−0.114, 0.230) | 156 |
| Combine → performance, TE | Combine movement | +0.093 (−0.221, 0.407) | 63 |
| Combine → performance, pooled | Combine movement | +0.299 (0.153, 0.446) | 543 |
| Next-season playing time | Current playing time | +0.606 (0.510, 0.701) | 233 |
| Next-season playing time | Performance | −0.011 (−0.119, 0.097) | 233 |
| Next-season playing time | Draft capital | +0.785 (0.347, 1.222) | 233 |
| Within-player change | Δ performance | −0.095 (−0.211, 0.022) | 235 |
| Pay model | Performance, base | +0.128 (0.037, 0.219) | 153 |
| Pay model | Performance, + role + draft | +0.040 (−0.024, 0.104) | 153 |
| Pay model | Draft capital | +1.40 (1.20, 1.61) | 153 |

### Validation and robustness

The next-season playing-time model has out-of-sample R² 0.503; the performance coefficient stays between −0.038 and +0.026 across folds. The Combine coefficient is a cross-player association, not a season forecast. The position-specific estimates are exploratory subgroup analyses; the interaction test is the stronger evidence. The signed rent is an accounting residual; it is not a causal rent and does not measure intent. The allocation gap is descriptive; the strict tail is 12 players. The predictability lens is exploratory and does not survive role controls.

### Limits

Observational; no causal claims. Playing time is snaps per appearance, not depth-chart rank or coaching intent. Defensive-back performance is unidentifiable and excluded from pooled models. Salary is a proxy: cap hits reflect proration, restructures, and timing; the net rent is descriptive. The weekly check is exploratory. Opponent, injuries, scheme, and game script are unavailable. The 2025 cap snapshot covers 68.7% of active-cap dollars and excludes offensive linemen and specialists.

The preregistered RJF/Yellow Square/pond analysis is reported in the repository appendix. It returned a wide null/underpowered pattern: Yellow +0.176 (95% CI −0.020 to 0.357, p=0.077, n=30); 2024–25 +0.144 (−0.070 to 0.351, p=0.18, n=23); Möbius and pond increments null; out-of-time R² negative. The CIs rule out only large effects. We treat it as fallback evidence, not confirmation.

### Code

Public notebook: https://www.kaggle.com/code/patrickm/nfl-bdb-2027-the-allocation-gap

Code: [Combine movement](https://github.com/PatrickMockridge/nfl-big-data-bowl-2027/blob/main/src/features/combine_movement.py), [performance](https://github.com/PatrickMockridge/nfl-big-data-bowl-2027/blob/main/src/features/performance.py), [role allocation](https://github.com/PatrickMockridge/nfl-big-data-bowl-2027/blob/main/src/discovery/role_allocation.py), [cost-risk](https://github.com/PatrickMockridge/nfl-big-data-bowl-2027/blob/main/src/discovery/cost_risk.py), [salary](https://github.com/PatrickMockridge/nfl-big-data-bowl-2027/blob/main/src/salary/rents.py).
