# External data — sources, coverage, and limits

The salary extension uses public data that is equally accessible to other
competitors. Raw downloads live in `data/external/` (gitignored) and are not
redistributed. Derived aggregates live in `outputs/salary/` (gitignored) and a
small public team-season panel is embedded in the notebook.

## Sources

| Source | What it provides | Coverage | Access / license |
|---|---|---|---|
| [OverTheCap positional spending](https://overthecap.com/positional-spending) | Team × position cap spending: QB, RB, WR, TE, OL, Offense, IDL, EDGE, LB, S, CB, Defense | 2023–2025; 96 team-seasons | Public website; cite OTC; raw HTML not redistributed |
| Archived OTC team cap pages (Wayback Machine, 2025 snapshots) | 2025 active-roster cap numbers by player; 32 teams; 1,693 player rows | 2025 | Public archive; cite OTC and the Wayback snapshot; raw HTML cached locally only |
| [nflverse `stats_player`](https://github.com/nflverse/nflverse-data/releases/tag/stats_player) | Season-level and weekly offensive/defensive stats (`stats_player_reg_2023/24/25.csv`, `stats_player_week_2023/24/25.csv`) | 2023–2025 | Public nflverse data; cite nflverse |
| [nflverse snap counts](https://github.com/nflverse/nflverse-data/releases/tag/snap_counts) | Per-game offense/defense/ST snaps by player/team | 2023–2025 | Public nflverse data |
| [nflverse players](https://github.com/nflverse/nflverse-data/releases/tag/players) | Master player table: `gsis_id`, `pfr_id`, `otc_id`, birth date, rookie season, draft team | Full history | Public nflverse data |
| [nflverse games](https://github.com/nflverse/nflverse-data/releases/tag/schedules) | Scores, teams, weeks | 1999–2025 | Public nflverse data |
| [Kaggle current-contract snapshot](https://www.kaggle.com/datasets/panch2112/nfl-active-player-contracts-and-stats-2026) | 1,976 contracts: player, position, team, start/end, value, APY, guarantee | Current contracts (2020–2026 starts); 2025 coverage is only ~50% of snaps | Apache-2.0; used as a sensitivity only |
| [Deloitte Money League 2025](https://www.deloitte.com/uk/en/services/financial-advisory/analysis/deloitte-football-money-league.html) | Club revenue, 2024–25 | Five-club soccer table | Public report; cite Deloitte |
| UEFA European Club Finance and Investment Landscape 2025 | Club wage bills, 2025 | Five-club soccer table | Public report; cite UEFA |
| Club annual reports and official league tables | Bodø/Glimt, Viking, Nordsjælland wage/personnel costs; league positions | 2024 / 2024–25 | Public club/league publications; see `docs/SOCCER_DATA.md` |

## Derived files

| File | Rows | Description |
|---|---:|---|
| `outputs/salary/otc_panel.csv` | 96 | OTC positional spending, shares, and payroll |
| `outputs/salary/team_youth.csv` | 96 | Youth (age ≤24), rookie, and homegrown snap shares |
| `outputs/salary/team_performance.csv` | 96 | Wins, point differential, offensive EPA |
| `outputs/salary/contract_team_season.csv` | 96 | Kaggle contract aggregates (sensitivity) |
| `outputs/salary/otc_cap_2025_team.csv` | 32 | 2025 active-cap totals and position shares |
| `outputs/salary/otc_cap_2025_players.csv` | 1,693 | 2025 player cap numbers, position, age, experience |
| `outputs/salary/team_salary_panel.csv` | 96 | Merged team-season panel |
| `outputs/salary/salary_results.csv` | 120 term rows | Efficiency models |
| `outputs/salary/qb_premium.csv` | 10 term rows | Quadratic QB models |
| `outputs/salary/qb_tiers.csv` | 10 rows | Top-quartile QB comparisons |
| `outputs/salary/cap_sensitivity.csv` | 54 term rows | 2025 active-cap sensitivity |
| `outputs/salary/rent_players.csv` | 909 | Player-level cap/cash residuals |
| `outputs/salary/rent_team.csv` | 32 | Team rent aggregates |
| `outputs/salary/rent_quartiles.csv` | 4 | Rent by efficiency quartile |
| `outputs/salary/rent_results.csv` | 10 rows | Bootstrap correlations and quartile contrasts |
| `outputs/salary/soccer_table.csv` | 5 | Illustrative soccer comparison |

## Matching and coverage

- **OTC player identity:** the archived OTC cap pages link each player to an
  OTC player id. The nflverse master table carries the same `otc_id`, so the
  join to `gsis_id`, birth date, position, and rookie season is exact. The
  name fallback is used only for a handful of rows.
- **Snaps:** nflverse snap counts match 99.9% of snaps to the master player
  table by `pfr_id`. In the 2025 OTC cap ledger, 98.2% of cap rows match to
  snaps by `gsis_id`; the matched rows cover 99.3% of active-cap dollars and
  91.3% of snaps.
- **Performance:** player performance is standardized within position group and
  season. Minimums: 100 QB dropbacks, 50 RB touches, 30 WR/TE targets, 8 games
  for defensive players. Player-seasons below the minimum keep a missing
  performance residual and are excluded from the rent model.
- **Rent sample:** 909 players with a measured performance residual. They cover
  68.7% of 2025 active-cap dollars. Offensive linemen and specialists are
  excluded because the public data have no individual performance measure.
- **Contract snapshot:** the Kaggle current-contract data is a 2026 snapshot;
  only 50% of 2025 snaps are covered, and 2023 coverage is much worse. It is
  used for a top-5 APY sensitivity, not the headline.

## Limitations

- OTC positional spending is cap spending by position, not a full cap ledger;
  it excludes some dead money and accounting adjustments.
- The 2025 cap snapshot is an active-roster snapshot from late 2025. Players
  who were off the roster at the snapshot date may be missing; dead-money
  categories are not used.
- Cap hits reflect signing-bonus proration, restructures, and contract timing,
  not just current performance. The rent proxy is descriptive, not causal.
- The team panel is 96 team-seasons (32 teams × 3 seasons), with 32 clusters.
  Estimates are exploratory and imprecise.
- The soccer comparison uses different accounting scopes and season windows;
  it is illustrative, not a natural experiment.

## Reproduction

```bash
python scripts/17_build_salary_panel.py
python scripts/18_test_salary.py
python scripts/19_salary_figures.py
```

The OTC archive download is cached in `data/external/otc_cap_2025/`. Re-running
`otc_cap.download(force=True)` refreshes the 32 archived pages.

## Market extension sources

The `implications/markets/` portfolio uses additional public market data. Raw
downloads stay in `data/external/market/` (gitignored); only derived aggregates
are written to `implications/markets/outputs/`.

| Source | URL | Coverage | License |
|---|---|---|---|
| nflverse trades | `github.com/nflverse/nflverse-data/releases/download/trades/trades.csv` | 4,975 rows, 2002–2026; team-level trades with player/pick fields | Public nflverse; cite |
| nflverse draft picks | `github.com/nflverse/nflverse-data/releases/download/draft_picks/draft_picks.csv` | 12,927 rows, 1980–2026; career outcomes from PFR | Public; cite nflverse/PFR |
| Coaching tenure | Derived from `data/external/games.csv` (`home_coach`, `away_coach`) | 893 team-seasons, 1999–2026; first/last game proxy | Public nflverse; cite |
| Hire/fire dates | PFR `pro-football-reference.com/coaches/` or Wikipedia | Optional; not downloaded by default | Cite; no bulk redistribution |
| Historical contracts | Local `data/external/historical_contracts.csv.gz` | 31,893 contracts, 1983–2022; APY/guarantee | Apache-2.0 per the contract snapshot |
| Special teams stats | Local `data/external/stats_player_week_2023/24/25.csv` | Weekly kicking/punting/return stats | Public nflverse; cite |

**Notes and limits.**

- Trades and draft picks are market context, not a causal event study. Trade
  terms are not a clean price, and the draft-pick value field is PFR's
  approximate value.
- Coaching hire/fire dates are proxied by the first and last regular-season game
  in the games file. No coach compensation data is public.
- The historical contract file is not linked to the 2023–25 performance data; it
  is a long-run APY context series, not a valuation input.
- K/P special-teams reliability fails the 0.50 gate; the returner composite
  passes but returners are paid through their offensive/defensive position.
- Raw source pages are not redistributed; derived aggregates only.
