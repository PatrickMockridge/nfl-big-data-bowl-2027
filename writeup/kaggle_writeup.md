# The testing is informative for defensive linemen; the decisions are not

## Part 1 — For the boardroom

The Combine tests tell you how a player moves, but not the same thing about every position. The decisions that follow — who plays — reward status and predictability more than the movement signal. The cap is more rational than the depth chart: it pays for performance.

We studied the 2023–2025 draft classes: 543 player-seasons with Combine movement and regular-season performance, 233 with a next season, and 909 players in the 2025 cap ledger.

### What we found

All of the analyses below are exploratory; the preregistered tests are in the appendix.

**The movement signal is position-specific.** Compare Combine movement with performance, holding position, season, and draft range constant. For defensive linemen the link is clear: +0.42 SD of performance per SD of movement (95% CI 0.26 to 0.58; raw +0.73, 95% CI 0.46 to 1.01). For receivers it is +0.17 SD (p=0.08); for offensive linemen +0.04 and tight ends +0.08, neither detectable. The pooled +0.19 SD (raw +0.30) is a defensive-line result, not a universal one. The difference across positions is significant (interaction p=0.0004). The defensive-line outcome is get-off, a movement-adjacent measure, so part of that result is a tracking-validity check rather than a production claim. Figure 1 shows the standardized estimates; Table 2 reports the raw coefficients.

![Figure 1. The Combine signal is real for defensive linemen, not universal.](https://raw.githubusercontent.com/PatrickMockridge/nfl-big-data-bowl-2027/main/writeup/figures/combine_linkage.png?v=4)

**The cap pays for performance.** On the full 2025 ledger of 909 players, a standard deviation of measured performance is associated with +0.328 log points of cap charge (95% CI 0.264 to 0.392), controlling age, experience, and position. Adding playing time reduces the coefficient to +0.143 (0.078 to 0.208) but does not eliminate it. The salary performance measure is nflverse public production, not the NGS `player_play` residual used in the Combine models; the two halves of this entry use different performance constructs.

A 153-player draft-matched subsample — the 2023–25 draft classes, mostly rookie contracts — shows the coefficient falling from +0.128 to +0.064 with role and +0.040 with role and draft capital (+1.40 log points per unit). That subsample is a rookie-wage-scale sensitivity, not the headline: it contains no quarterbacks or running backs, and its mean cap charge is about one-third of the full ledger. On the ledger the entry is about, the cap pays for performance. Figure 2 shows both.

![Figure 2. The cap pays for performance; the 153-player fade is a rookie-scale subsample.](https://raw.githubusercontent.com/PatrickMockridge/nfl-big-data-bowl-2027/main/writeup/figures/net_rent.png?v=4)

**The depth chart does not.** Current playing time (+0.606) and draft capital (+0.785) predict next-season playing time; the performance coefficient is −0.011 (95% CI −0.119 to 0.097, n=233). That CI rules out only modest positive effects; it is an absence of evidence, not proof of zero. The within-player test gives −0.095 (95% CI −0.211 to 0.022, n=235). Figure 3 shows the drivers by position; Figure 4 shows the persistence and the within-player null.

![Figure 3. Current snaps and draft position predict next season; performance does not.](https://raw.githubusercontent.com/PatrickMockridge/nfl-big-data-bowl-2027/main/writeup/figures/next_role_forest.png?v=4)

![Figure 4. Snaps persist; a better season does not earn more snaps.](https://raw.githubusercontent.com/PatrickMockridge/nfl-big-data-bowl-2027/main/writeup/figures/persistence_within_player.png?v=4)

**The allocation gap is descriptive.** Performance minus playing time is +0.59 for late picks and undrafted players and −0.92 for early picks in the full 233-row sample (+0.28 and −0.93 in the reliable 192-row sample). The strict group — top-quartile performance in the bottom role quartile — has 13 player-seasons (12 players), mean gap 2.24 SD, mean draft percentile 0.24. Its current role is −0.82 SD and its next-season role is −0.57 SD, a +0.25 SD recovery, still below the mean. The broader tercile group has 23 player-seasons (21 players). The gap is mostly a role effect; it is not evidence that coaches suppress performance. Figure 5 shows the scatter and the draft gradient.

![Figure 5. The allocation gap is descriptive: early picks play above performance; late picks perform above role.](https://raw.githubusercontent.com/PatrickMockridge/nfl-big-data-bowl-2027/main/writeup/figures/allocation_gap.png?v=4)

**The predictability lens is exploratory.** Volatility is associated with fewer snaps than performance and draft predict (−1.49, p<0.001), but the association disappears with current role controlled (+0.13, p=0.31).

### Why it matters

If a young player performs but sits, the team pays for a skill it is not using. The cap is not the main problem: it pays for performance. The depth chart is the tighter constraint. The cost is the foregone production in the gap; the pattern is descriptive, not proof of intent.

### What a team should do

Use the Combine test where it works: defensive-line get-off. Do not compare offensive linemen, tight ends, and defensive linemen on one movement score. Use the performance-role gap as a review list: the coaching staff sees who performs above his role. The cap staff does not need the same list; the cap already pays for performance. The data do not identify an optimal cadence; a monthly review is a process choice, not a tested rule. Name one accountable person — the head coach with the scouting department — and let analysts supply evidence. No algorithm sets a lineup.

### What this does not say

This is a pattern, not a controlled experiment. It does not say that more snaps will make a player perform. It does not prove intent. The cap model is an accounting model; the salary performance measure is public production, not the tracking residual; the role gap is descriptive; the predictability result is exploratory. A flag is a reason to look, not a verdict.

Table 1 summarizes the Football score.

**Table 1. Football scorecard.**

| Criterion | Evidence | Operational use | Status and caveat |
|---|---|---|---|
| Week-to-week usability | Snaps persist; performance does not move next-week or next-season role (absence of evidence). | Review the largest performance-role gaps; no tested cadence. | Exploratory weekly check; snaps are not depth-chart rank. |
| Complexity | Position-specific Combine; 543 performance player-seasons; 233/192 role rows; 909 cap rows. | One analyst can maintain it; output is a short review list. | No private data; performance measures differ by position; defensive backs excluded; cap model uses nflverse production. |
| Uniqueness | The testing signal is position-specific; the cap pays for performance while the depth chart does not detectably reward it. | Ask whether the depth chart uses the signal the testing shows. | A pattern in the data. No causal claim. Cap spending is an estimate, not intent. |

## Part 2 — Method and evidence

### Data

The 2023–2025 Combine cohorts: 510 players; 401 with 722 regular-season player-seasons. Combine tracking: 10 Hz. Performance comes from Next Gen Stats `player_play`; snaps and games from the tracking panel, with nflverse snap counts used in the salary layer. Salary data combine OverTheCap positional spending (96 team-seasons), archived 2025 OTC active-cap pages (32 teams; 99.3% of active-cap dollars match a 2025 snap on player ID and team), and a contract snapshot for sensitivity.

The performance sample is 543 player-seasons: 722 minus 165 defensive backs and 14 without a performance measure (including 4 linebackers and 3 others). The role sample is 233 with a next season, 192 with at least 50 performance plays. The cap sample is 909 players, 68.7% of 2025 active-cap dollars; offensive linemen and specialists are excluded. The cap model uses nflverse public production; the Combine and role models use the NGS `player_play` residual. The draft-matched cap model uses the 153 players with a draft record.

### Measures

**Combine movement.** Attempt-level z-scores within drill and position group for max speed, first-step acceleration (0.5 s), time to 1 yard (reversed), and path efficiency. Attempt scores are averaged per player, re-standardized, and averaged into one movement score.

**Performance.** Position-specific play outcome, oriented higher-is-better: defensive-line get-off, receiver and tight-end separation, offensive-line pressure allowed, defensive-back pass result. Residualized against play context (down, distance, pressure, coverage, field position, motion, blitz, season) with ridge regression and 5-fold grouped cross-validation by player; empirical-Bayes shrunk and standardized within position group and season.

**Playing time.** Snaps per appearance, standardized within position group and season. The role residual is the residual from playing time regressed on performance, draft capital, draft-free prestige, position group, and season; positive means more snaps than comparable players.

**Cap model.** For 2025, log cap number is modeled on performance, age, experience, and position on the full 909-player ledger; adding playing time gives the role-controlled model. The 153-player draft-matched model adds `B_draft` as a rookie-scale sensitivity. The salary performance is nflverse public production, not the NGS residual.

**Draft capital.** `B_draft` is a within-position, within-class percentile; early and late picks are its quartiles.

**Allocation gap.** Performance z minus playing-time z, both within position group and season. Positive means the player performs above his role; it is not the role residual.

### Models

OLS with player-clustered standard errors; salary models cluster by team with season controls. Table 2 reports selected estimates. The Combine models are position-specific; the role models use current role, performance, draft capital, position, and season; the cap model is on the full 909-player ledger, with the 153-player draft-matched model as a sensitivity. Weekly: next-week role +0.753, performance −0.006, n=3,885.

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
| Cap model, full ledger | Performance, base | +0.328 (0.264, 0.392) | 909 |
| Cap model, full ledger | Performance, + role | +0.143 (0.078, 0.208) | 908 |
| Cap model, draft-matched | Performance, + role + draft | +0.040 (−0.024, 0.104) | 153 |
| Cap model, draft-matched | Draft capital | +1.40 (1.20, 1.61) | 153 |

### Validation and robustness

The next-season playing-time model has out-of-sample R² 0.503; the performance coefficient stays between −0.038 and +0.026 across folds. The Combine coefficient is a cross-player association, not a season forecast. The position-specific estimates are exploratory subgroup analyses; the interaction test is the stronger evidence. The cap residual is an accounting residual; the role null is an absence-of-evidence result; the allocation gap is descriptive and the strict tail recovers +0.25 SD. The predictability lens does not survive role controls. The notebook's reconstruction gives +0.295/−0.034 (n=195) and DL +0.726/TE +0.076; the pipeline gives +0.299/−0.019 (n=192) and +0.734/+0.093; the differences are reconstruction scale and role universe.

### Limits

Observational; no causal claims. Playing time is snaps per appearance, not depth-chart rank or coaching intent. Defensive-back performance is unidentifiable and excluded from pooled models. Salary is a proxy: cap hits reflect proration, restructures, and timing; the cap residual is descriptive; the 153-player draft-matched model is a rookie-scale sensitivity. The weekly check is exploratory. Opponent, injuries, scheme, and game script are unavailable. The 2025 cap snapshot covers 68.7% of active-cap dollars and excludes offensive linemen and specialists.

The preregistered transition-zone (RJF/Yellow Square) analysis is reported in the repository appendix. It returned a wide null/underpowered pattern: Yellow +0.176 (95% CI −0.020 to 0.357, p=0.077, n=30); 2024–25 +0.144 (−0.070 to 0.351, p=0.18, n=23); Möbius and pond increments null; out-of-time R² negative. The CIs rule out only large effects. We treat it as fallback evidence, not confirmation.

### Code

Public notebook: https://www.kaggle.com/code/patrickm/nfl-bdb-2027-the-allocation-gap

Code: [Combine movement](https://github.com/PatrickMockridge/nfl-big-data-bowl-2027/blob/main/src/features/combine_movement.py), [performance](https://github.com/PatrickMockridge/nfl-big-data-bowl-2027/blob/main/src/features/performance.py), [role allocation](https://github.com/PatrickMockridge/nfl-big-data-bowl-2027/blob/main/src/discovery/role_allocation.py), [cost-risk](https://github.com/PatrickMockridge/nfl-big-data-bowl-2027/blob/main/src/discovery/cost_risk.py), [salary](https://github.com/PatrickMockridge/nfl-big-data-bowl-2027/blob/main/src/salary/rents.py).
