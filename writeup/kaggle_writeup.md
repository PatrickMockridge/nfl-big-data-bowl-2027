# The testing is informative; the decisions are not

## Part 1 — For the boardroom

The Combine tests tell you how a player moves: top speed, acceleration, time to the first yard, path efficiency. Playing time and contract decisions mostly do not reflect it. We studied the 2023–2025 draft classes: 543 player-years and 96 team-years.

### What we found

Compare Combine movement with how well he performs on Sundays, holding position, season, and draft range constant. Better movement goes with better performance. The relationship is modest: about one-third of the typical spread, roughly the 50th to 62nd percentile. Figure 1 shows the result: performance rises, playing time is flat.

![Figure 1. Combine movement separates performers, not playing time.](https://raw.githubusercontent.com/PatrickMockridge/nfl-big-data-bowl-2027/main/writeup/figures/combine_linkage.png)

The same movement score shows no detectable link to playing time. Next season's snaps follow this season's snaps and draft position; performance barely matters.

Spending a large share on star positions — quarterback, running back, receiver, tight end, and edge rusher — has no clear relationship with wins per $100 million. Teams that give a larger share of snaps to rookies average fewer wins per $100 million. That does not mean rookies cause losses; losing teams often play rookies. Teams that give more snaps to their own drafted players average more wins per $100 million. That may reflect winning teams keeping their players, not a causal effect. Figure 3 shows the quarterback detail: wins rise as quarterback spending rises, up to about 14% of the offense-and-defense cap, then level off, with a wide margin of error.

![Figure 2. Star spending is flat; rookie and homegrown snap shares move with wins.](https://raw.githubusercontent.com/PatrickMockridge/nfl-big-data-bowl-2027/main/writeup/figures/salary_efficiency.png)

![Figure 3. Quarterback spending flattens near 14%, with a wide margin of error.](https://raw.githubusercontent.com/PatrickMockridge/nfl-big-data-bowl-2027/main/writeup/figures/qb_premium.png)

### Why it matters

Homegrown means a player ends the season with the team that drafted him; undrafted players who stay with their first team are not counted. Star spending is the share of offense-and-defense cap hits — not cash — going to five premium positions: quarterback, running back, receiver, tight end, and edge rusher. It is positional spending, not a judgment that the player is a star. Rookies are usually homegrown, but homegrown also includes drafted veterans, so the two findings are not a contradiction.

If a young player performs but sits, the team pays for a skill it is not using. If a veteran plays but does not perform, the team spends cap space on playing time that produces little. Contracts can lock in that mistake, because pay is often set by draft status and reputation, not just current production.

### What a team should do

Run a review every four to six weeks, not every week. This week's snaps predict next week's snaps. Performance does not. One game is noise; four to six weeks shows whether a flag persists.

Use two flags over the review window. First: a player in the bottom third of snaps at his position and the top third of performance. Second: a player in the top third of snaps and the bottom third of performance. Both are questions for the position coach and area scout, not instructions. Ask about assignment, health, scheme fit, and game script before changing a lineup.

Name one accountable person — the head coach with the scouting department — with analysts supplying evidence. No algorithm should set a lineup. The general manager and cap staff can use the same list for contract, extension, and free-agency planning.

At the league office, use the same numbers as a league-wide check. Look for persistent mismatches between performance and playing time. Ask whether the pattern reflects coaching, roster construction, or a flaw in the data. Do not use it for punishment or public rankings.

### What this does not say

This is a pattern in the data, not a controlled experiment. It does not say that giving a player more snaps will make him perform, or that paying a quarterback less will win more games. It says the pattern is inconsistent with the goals teams state: winning and getting value from the cap. A flag is a reason to look, not a verdict.

The cap results describe where money went. They are not proof that a team intended to overpay. Contracts reflect timing, guarantees, and the market. The review is a decision aid, not a scoreboard.

### The three Football Score questions

On week-to-week usability, the answer is no for a weekly decision rule and yes for a four-to-six-week review. On complexity, the comparison holds position, season, draft range, current snaps, and play situation constant, but not opponent, injuries, scheme, or game script; it needs Combine movement data, snaps, and public cap data, and one analyst can maintain it. Defensive backs are excluded; their performance measure is unreliable. Public draft models usually stop at predicting who will be good. To our knowledge, this is the next question: whether playing time and contract decisions use that prediction. The answer is that they mostly do not.

**Table 3. Football scorecard.**

| Criterion | Evidence | Operational use | Caveat |
|---|---|---|---|
| Week-to-week usability | Snaps this week strongly predict snaps next week; performance does not. Early performance does not predict late snaps. | Review every four to six weeks. Do not change the depth chart off one game. | Exploratory weekly check. Snaps are not depth-chart rank. Injuries and game script are unobserved. |
| Complexity | One movement score, one performance score, public cap figures; 543 player-years and 96 team-years. | One analyst can maintain it. Output is a short review list. | No private data; performance measures differ by position; defensive backs are excluded. |
| Uniqueness | Public draft models predict who will be good; this asks whether playing time and contract decisions use that prediction. | Ask whether the depth chart and cap sheet use the signal the testing shows. | A pattern in the data. No causal claim. Cap spending is an estimate, not proof of intent. |

The testing is informative; the decisions are not.

## Part 2 — Method and evidence

### Data

The 2023–2025 Combine cohorts: 510 players; 401 with 722 regular-season player-seasons. Combine tracking: 10 Hz. Performance comes from Next Gen Stats `player_play`; snaps and games from nflverse. Salary data combine OverTheCap positional spending (96 team-seasons), archived 2025 OTC active-cap pages (32 teams; 99.3% of active-cap dollars match a 2025 snap on player ID and team), and a public contract snapshot used only for sensitivity.

### Measures

**Combine movement.** Attempt-level z-scores within drill and position group for max speed, first-step acceleration (0.5 s), time to 1 yard (reversed), and path efficiency. Attempt scores are averaged per player, re-standardized, and averaged into one movement score.

**Performance.** Position-specific play outcome, oriented higher-is-better, residualized (the part not explained by controls) against play context including down, distance, pressure, coverage, field position, motion, blitz, and season, using ridge regression and 5-fold grouped cross-validation by player. Player-seasons are empirical-Bayes shrunk (small samples pulled toward the group-season mean) and standardized within position group and season (mean 0, SD 1).

**Playing time.** Snaps per appearance (snaps/games), standardized within position group and season. The playing-time gap is the residual from playing time regressed on performance, draft capital, draft-free prestige, position group, and season; positive means more snaps than comparable players.

**Draft capital.** `B_draft` is a 0–1 percentile of overall pick within class and position subgroup; higher is an earlier pick; undrafted players are set to 0.

**Cap measures.** Star share is quarterback, running back, receiver, tight end, and edge spending divided by offense plus defense spending; quarterback share uses the same denominator. Payroll is OTC offense plus defense spending. Rookie and homegrown shares are shares of team snaps; homegrown means draft team equals current team. Wins per $100M is wins divided by payroll in $100M.

**Cap-allocation measure.** For 2025, log cap number (the season's salary-cap charge) is modeled on performance, age, experience, and position; the residual is dollars above or below the pay model. Positive values are cap dollars above the model, not evidence of intent. "Star" here means top-quartile 2025 cap number, not the star-share category. Underperformer means bottom-quartile performance with above-median snap share; young high performer means age ≤24 with top-quartile performance.

### Models

Models use ordinary least squares with standard errors clustered by player; salary models cluster by team with season controls. Table 1 reports selected estimates.

Combine linkages: performance and playing time on combine movement, draft capital, position group, and season. Performance +0.299 (95% CI 0.153 to 0.446, n=543); playing time −0.019 (−0.194 to 0.156, n=192); the playing-time gap (with current snaps) +0.012 (−0.049 to 0.073, n=192).

Next-season playing time: current playing time +0.606 (0.510 to 0.701); performance −0.011 (−0.119 to 0.097); draft capital +0.785 (0.347 to 1.222); n=233. Within-player change in performance: −0.095 (−0.211 to 0.022, n=235).

![Figure 4. Current snaps and draft position predict next season; performance does not.](https://raw.githubusercontent.com/PatrickMockridge/nfl-big-data-bowl-2027/main/writeup/figures/next_role_forest.png)

Week-to-week: next-week playing time on current-week playing time +0.753 (0.717 to 0.788); current-week performance −0.006 (−0.027 to 0.015, p=0.586); n=3,885 player-weeks, 249 players. Early-season (weeks 1–6) performance to late-season (weeks 7+) playing time +0.008 (−0.072 to 0.087, p=0.846); n=282 player-seasons, 180 players. Controls: current playing time, performance, draft capital, position group, season, week; early-late adds early playing time and performance.

![Figure 5. Snaps persist; a better season does not earn more snaps.](https://raw.githubusercontent.com/PatrickMockridge/nfl-big-data-bowl-2027/main/writeup/figures/persistence_within_player.png)

Salary panel: wins on star share, payroll, and season: −0.70 (−10.23 to +8.83, p=0.886, n=96); the wins-per-$100M model is −0.40 (−5.20 to +4.39, p=0.869). Rookie snap share −28.39 (−47.96 to −8.82, p=0.004); homegrown +9.21 (+3.81 to +14.62, p=0.001); n=96. Quarterback quadratic on wins (OTC positional share, not the 2025 cap measure): linear +42.37 (−2.87 to +87.60), quadratic −149.17 (−309.99 to +11.64, p=0.069), fitted turning point 0.142, n=96; the vertex is not statistically identified.

**Table 1. Selected models (coefficient, 95% CI, n).**

| Model | Term | Coefficient (95% CI) | n |
|---|---|---|---|
| Combine → performance | Combine movement | +0.299 (0.153, 0.446) | 543 |
| Combine → playing time | Combine movement | −0.019 (−0.194, 0.156) | 192 |
| Next-season playing time | Current playing time | +0.606 (0.510, 0.701) | 233 |
| Next-season playing time | Draft capital | +0.785 (0.347, 1.222) | 233 |
| Within-player change | Δ performance | −0.095 (−0.211, 0.022) | 235 |
| Next-week playing time | Current-week playing time | +0.753 (0.717, 0.788) | 3,885 |
| Next-week playing time | Current-week performance | −0.006 (−0.027, 0.015) | 3,885 |
| Early → late playing time | Early performance | +0.008 (−0.072, 0.087) | 282 |
| Wins | Star share | −0.70 (−10.23, 8.83) | 96 |
| Wins | Rookie snap share | −28.39 (−47.96, −8.82) | 96 |
| Wins | Homegrown snap share | +9.21 (3.81, 14.62) | 96 |

Figure 6 shows the cap residuals by efficiency quartile. Efficiency quartiles are 2025 team wins per $100M. Cap residuals by quartile (Q1 low to Q4 high): total $51.2M, $69.4M, $57.7M, $30.7M; Q4−Q1 −$20.5M (95% CI −$40.9M to −$2.0M). Star −$14.2M (−$29.3M to +$0.7M); underperformer −$6.3M (−$14.5M to −$0.2M); youth +$1.9M (+$0.1M to +$4.0M). Above-model dollars, not intent. Sample: 909 players, 69% of active-cap dollars; OL and specialists excluded.

![Figure 6. The most efficient teams carry the least overpay.](https://raw.githubusercontent.com/PatrickMockridge/nfl-big-data-bowl-2027/main/writeup/figures/overpay_quartiles.png)

### Validation and robustness

Out-of-sample R² 0.503 is for next-season playing time, not the Combine coefficient; the performance coefficient stays between −0.038 and +0.026, n=233. 

### Limits

Observational; no causal claims. Playing time is snaps per appearance, not depth-chart rank or coaching intent. DB performance is unidentifiable and excluded from pooled models. Salary is a proxy: cap hits reflect proration, restructures, timing; the cap measure is descriptive. The weekly check is exploratory. Opponent, injuries, scheme, game script are unavailable. The review is a decision aid.

### Code

Public notebook: https://www.kaggle.com/code/patrickm/nfl-bdb-2027-the-allocation-gap

The notebook's self-contained reconstruction gives +0.41 and −0.05 for the two Combine links; the full pipeline gives +0.299 and −0.019.

Code: [Combine movement](https://github.com/PatrickMockridge/nfl-big-data-bowl-2027/blob/main/src/features/combine_movement.py), [performance](https://github.com/PatrickMockridge/nfl-big-data-bowl-2027/blob/main/src/features/performance.py), [role allocation](https://github.com/PatrickMockridge/nfl-big-data-bowl-2027/blob/main/src/discovery/role_allocation.py), [Combine linkage](https://github.com/PatrickMockridge/nfl-big-data-bowl-2027/blob/main/src/discovery/combine_linkage.py), [weekly role](https://github.com/PatrickMockridge/nfl-big-data-bowl-2027/blob/main/src/discovery/weekly_role.py), [salary analysis](https://github.com/PatrickMockridge/nfl-big-data-bowl-2027/blob/main/src/salary/analysis.py), [rent](https://github.com/PatrickMockridge/nfl-big-data-bowl-2027/blob/main/src/salary/rents.py).
