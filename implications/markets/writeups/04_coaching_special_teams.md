# Coaching retention and special teams

Both markets are descriptive. Neither supports a dollar route in this
extension, and saying so is the useful result.

## Coaching retention

**Data.** Coach-team-season tenure is derived from the 893 regular-season
team-seasons in nflverse games (1999–2026), using the coach with the most games
in a season and the first/last game as the tenure proxy. Hire/fire dates are not
in the public game file; no paid coaching data is used.

**Model.** Linear probability with team-clustered SE; logit as a sensitivity:

```
retained_next ~ wins + point_diff + tenure + C(season)
```

| Term | LPM coefficient (95% CI) | p | Logit coefficient | p |
|---|---:|---:|---:|---:|
| Wins | **+0.073 (0.054, 0.091)** | <0.001 | +0.522 (0.396, 0.648) | <0.001 |
| Point differential | −0.000 (−0.001, 0.000) | 0.203 | −0.003 (−0.007, 0.001) | 0.188 |
| Tenure | **−0.010 (−0.017, −0.002)** | 0.013 | −0.075 (−0.130, −0.020) | 0.008 |

n = 858 team-seasons; retention rate 0.769. Retention rises from **0.52** in
the bottom wins quartile to **0.97** in the top. Once wins are included, point
differential adds nothing; tenure is negative, consistent with a stale-tenure
effect.

**Reading.** Coaching retention is wins/status-driven. There is no coach-level
allocation-efficiency measure in the data, so the model cannot test whether
retention rewards role allocation. The market implication is a framing choice:
the allocation chunk should be presented as **protecting the coach** (fewer
avoidable role mistakes) rather than challenging him. No dollar value is
attached.

## Special teams

**Data.** K/P/returner season composites from nflverse weekly stats, 2023–2025.
Roles are assigned on season attempts (K: 20+ FG attempts; P: 30+ punts; RET:
20+ returns). Split-half reliability is odd/even weeks within role.

| Role | n | Split-half r | Reliability | Gate |
|---|---:|---:|---:|---|
| K | 92 | 0.060 | 0.114 | fail |
| P | 94 | 0.296 | 0.457 | fail |
| RET | 105 | 0.635 | 0.776 | pass |

K and P fail the 0.50 gate, so the descriptive `logcap ~ st_perf_z + age + exp`
model is not estimated. The returner composite passes, but returners are paid
through their offensive/defensive position, not a separate ST cap market. The
pricing cell is therefore empty.

**Reading.** Special teams are a role-review market only. The snap and
kicking/punting data are available, but the season-to-season signal is too noisy
for a pricing claim. The honest market map entry is: **descriptive; no dollar
route.**

## What would make them quantifiable

- **Coaching:** a coach-level allocation-efficiency measure (e.g., role-gap
  reduction relative to scheme/roster expectations) and hire/fire dates.
- **Special teams:** a multi-season composite with better reliability, or
  game-level tracking that separates coverage, blocking, and return skill.
  Returner value would still need to be priced through the player's offensive
  or defensive position.
