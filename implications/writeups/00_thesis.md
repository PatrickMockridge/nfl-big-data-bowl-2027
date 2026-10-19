# The stopwatch prices pressure; the depth chart and the cap price something else

**Status:** extension to the 2027 NFL Big Data Bowl entry, not part of it. GitHub only; not published on Kaggle. Date-stamped 2026-10-19. The competition artifacts are frozen at `c652424`.

## The claim

The entry's measured result is not "tracking predicts performance." It is that three pricing mechanisms see three different things:

| Mechanism | What it prices | Measured evidence |
|---|---|---|
| The stopwatch | Sacks, not pressure | The 40-yard dash and 10-yard split add nothing to pressure (joint p=0.998). Out-of-sample pressure R² is −0.113 for the stopwatch and +0.178 for the 10 Hz burst. |
| The depth chart | Status and prior role | Next-season role: current role +0.606, draft capital +0.785, performance −0.011 (95% CI −0.119 to 0.097, n=233). The concurrent estimate is −0.132 (p=0.031), marginal. |
| The cap | Performance, partly role | Full 909-player ledger: performance +0.328 (0.264–0.392); +0.143 (0.078–0.208) with playing time. |

The pure measurement finding is the 10 Hz burst: it predicts interior pressure at **+0.354 SD/SD** (0.143–0.565, n=64). Top versus bottom burst tercile pressure is **3.83% vs 2.47%** (+1.36 pp); sacks are **0.97% vs 0.35%** (2.7×). The signal is position-specific: DL +0.734, WR +0.366 (p=0.084), OL +0.058, TE +0.093; interaction p=0.0004. The stopwatch is not blind to sacks, but it is blind to the pressure that precedes them.

The structural reading is: **the allocation technology is status-legible; the pricing technology is performance-legible; the gap between them is measurable.** That is not a claim that coaches are irrational. It is a claim about information: draft slot and prior role are cheap, public, and predictable; performance is noisy and slow to update.

## What is measured, and what is inferred

| Claim | Status | Source |
|---|---|---|
| The burst predicts interior pressure and sacks | Measured | `outputs/discovery/interior_burst_models.csv` |
| The stopwatch does not carry the pressure signal | Measured | `interior_burst_validation.csv`, `interior_burst_incremental.csv` |
| The Combine signal is position-specific | Measured | `combine_linkage_by_position.csv` |
| Role is sticky and draft-driven; performance is not detectable | Measured | `role_allocation_coefficients.csv` |
| The cap pays performance, partly through role | Measured association | `outputs/salary/pay_model_full.csv` |
| The allocation gap is mostly role | Descriptive decomposition | `allocation_gap_groups.csv`, `allocation_gap.parquet` |
| The two-agent wedge is a decision-weight difference | Model-reproduced, not identified | `agentic_allocation_moments.csv`, `agentic_allocation_levers.csv` |
| The dollar value to one team | Inference | `implications/code/value_model.py` |
| The team fits and the outreach map | Reading, date-stamped | `02_adoption.md`, `03_outreach.md` |

The allocation gap is descriptive. Late picks and UDFAs sit at **+0.59 SD** performance-minus-role; early picks sit at **−0.92 SD** in the full 233-row sample (+0.28 and −0.93 in the reliable 192-row sample). The group means show why: across draft quartiles, the role spread is **1.462 SD** versus a performance spread of **0.046 SD** in the full sample; in the reliable sample, the role spread is **1.104** versus **0.106**. The gap is mostly role, not a late-pick performance advantage. The strict top-performance/bottom-role quartile is 13 player-seasons (12 players); its current role is −0.82 SD and its next-season role is −0.57 SD, a +0.25 SD recovery that is still below the mean and consistent with mean reversion.

## The lid

The strongest version of the argument is already in the outputs but not in one sentence: the burst is essentially uncorrelated with draft capital (**+0.034, 95% CI −0.044 to 0.111**). The market does not price the signal that predicts pressure; the depth chart then suppresses the players who have it; the cap would pay them if they played. That is the chain from measurement blind spot to draft mispricing to role suppression to the cap/role gap.

It is a structural claim, not a moral one. The coach is not foolish to weight a noisy performance signal less than a stable prior role. The GM is not foolish to weight performance in a cap model. The two are optimising different objectives with different information. The gap is the cost of that difference.

## Why this is a distinct entry

Most Big Data Bowl work asks whether a tracking metric predicts an outcome. That is a useful question, and the answer here is narrow: the burst is a position-specific pressure signal, not a universal talent score. The distinct move is to use the measurement as a probe into how the league allocates labour. The competition's rubric rewards football insight and a readable argument as much as model fit; a structural claim with a reproducible measurement underneath is a different product from a metric leaderboard.

## What would change the thesis

- **The pressure signal fails out of sample.** The team-fixed-effects estimate is +0.298 (95% CI −0.045 to 0.640, p=0.089); the 2025 temporal R² is −0.045. The association is not robust enough to call a validated tool.
- **Role allocation is efficient for unobserved reasons.** Injuries, scheme fit, and coaching trust are not in the model. If those explain the gap, the policy lever shrinks.
- **The market already prices pressure.** PFF, NGS, and college production may already capture what the stopwatch misses. If so, the selection surplus is smaller than the burst-versus-stopwatch contrast implies.
- **The cap and depth chart use the same performance measure.** They do not: the cap uses nflverse production, the role model uses the NGS residual. The cross-construct wedge is the weakest link in the Tier 2 model.

The thesis survives the first three as a descriptive finding; the fourth limits the dollar case, not the measurement case.
