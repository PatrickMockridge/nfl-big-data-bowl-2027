# Market portfolio protocol

**Status:** pre-registration for a GitHub-only extension of `implications/`. It
is not part of the judged Big Data Bowl entry and does not modify the artifacts
frozen at `c652424`. Date-stamped **2026-10-20**.

Every dollar figure in this extension is an **inference**, not a measurement.
The measured and descriptive inputs are cited to their output files. The
protocol fixes the market × route matrix, calibration rules, gates, and overlap
rules before any valuation is run.

## Scope

The extension asks which parts of the entry's allocation-gap argument can be
priced in NFL-adjacent markets. The finished `transfer/` extension established
the constraint: **the structural pattern travels; the measurement does not.**
The DL interior/edge pass-rush signal is supported; WR is weak; TE, OL, and DB
fail reliability or variance gates. The unpriced-signal and allocation patterns
do travel, and the cap/pricing layer covers most positions.

The markets are:

1. EDGE
2. WR
3. DB (CB/S)
4. OL
5. TE
6. Free agency / contract (cross-position)
7. Coaching retention (descriptive)
8. Special teams (descriptive; pricing only if the reliability gate passes)

Interior DL is retained as the **anchor**, not a new claim. QB, RB, and LB have
no BDB transfer evidence and appear only as contract-pricing rows in the
free-agency market.

## Market × route matrix

| Market | Selection | Role | Contract | Evidence tier |
|---|---|---|---|---|
| Interior DL (anchor) | modeled (existing) | modeled (existing) | modeled (existing) | measured + inference |
| EDGE | modeled, borderline | modeled (subgroup; n≥40 gate) | in free-agency view | measured association |
| WR | sensitivity only; base 0 | modeled | in free-agency view | measurement weak; allocation/pricing descriptive |
| DB (CB/S) | not modeled | not modeled | in free-agency view | pricing-only |
| OL | not modeled | modeled | not modeled | allocation-only |
| TE | not modeled | sensitivity only | exploratory | unidentifiable / thin |
| Free agency / contract | — | — | modeled across cap-covered positions | measured association + inference |
| Coaching retention | — | — | — | descriptive / reading |
| Special teams | — | descriptive | descriptive if gate passes | descriptive |

`route_status` is one of `modeled`, `sensitivity`, `display_only`,
`not_modeled`, or `unidentifiable`. `display_only` means the route is estimated
but its dollars are counted in the free-agency market, not in the position
total. A disabled route is implemented by setting its inputs to zero in all
three scenarios; the route remains visible in the table with its status.

**Cross-construct caveat.** Every contract route uses the salary layer's
`perf_z` (nflverse production), not the BDB NGS performance residual. The
pricing leg is internally consistent with the existing cap model, but it is not
the same construct as the transfer L1/L3 performance measure. For DB, the
contract route is estimable while measurement and allocation remain
unidentifiable.

## Evidence tiers

- **Measured:** a coefficient with a 95% CI from the entry, transfer, or salary
  outputs.
- **Measured association:** an observational coefficient from the salary layer,
  not causal.
- **Descriptive:** a decomposition or gap table.
- **Inference:** a dollar figure produced by this protocol's assumptions.
- **Reading:** a market fit or messaging judgment, date-stamped.

No claim in this extension is causal.

## Calibration rules

All dollar inputs are $M/year. Quantiles are 2025 data, rounded to $0.1M.

| Input | Rule | Source |
|---|---|---|
| `market` | P75 / P90 / P95 of `cap_number` by position; DL anchor keeps 8 / 12 / 18 | `outputs/salary/otc_cap_2025_players.csv` |
| `rookie` | 0.8 / 1.5 / 2.5 for comparability; position-specific P25/P50/P75 (years_exp ≤ 1) as sensitivity | same |
| `role_saving` | 0.25 / 0.50 / 0.75 × market for new markets; DL anchor keeps 3 / 6 / 8 | derived |
| `role_decisions` | 0.25 / 0.50 / 0.75 where role is modeled; 0 otherwise | judgment |
| `reallocation_eff` | 0.50 / 0.70 / 0.80 | judgment |
| `contract_portfolio` | base = 50 × (mean team position spend / mean team IDL spend); low/high = 0.6 / 1.0 / 1.4 × base | `outputs/salary/otc_panel.csv` (2025) |
| `pricing_correction` | 0.15 / 0.40 / 0.60 × max(raw − role perf coefficient, 0) | new per-position models |
| `hit_lift` | DL interior 0.05/0.15/0.20; EDGE 0.02/0.08/0.12; WR 0/0.02/0.05 (sensitivity); others 0 | transfer L1 + judgment |
| `picks_per_year` | DL/EDGE/WR 0.25/0.50/0.75; others 0 | judgment |
| `implementation_cost` | 0.5 / 1.0 / 2.0 | judgment |
| `adoption_prob` | 0.20 / 0.40 / 0.60 | judgment |
| `cap` | 280 (context only) | existing |

The DL anchor is preserved for reconciliation even though the IDL ledger
P75/P90/P95 is lower (roughly 3.9/7.7/13.9). New markets use the ledger
quantiles; the difference is reported in the evidence ledger. The DL contract
portfolio keeps the existing 50.

## Per-position pricing model

On `outputs/salary/rent_players.csv` (2025, 909 rows), fit by `pos_group`,
team-clustered:

```
raw:   np.log(cap_number) ~ perf_z + age_start + years_exp
role:  np.log(cap_number) ~ perf_z + snap_share + age_start + years_exp
```

Extract the `perf_z` coefficient and 95% CI. `gap = raw − role`; the correction
is `0.15/0.40/0.60 × max(gap, 0)`.

- `primary`: n ≥ 80 and both coefficients estimable.
- `exploratory`: 40 ≤ n < 80, or the CIs overlap heavily.
- `not_modeled`: n < 40 or no `perf_z` (OL).
- If `gap ≤ 0`, set the correction to 0 and record `no_correction`.

QB (42), TE (46), and RB (66) are exploratory; LB (205), S (128), CB (122), WR
(106), IDL (105), and EDGE (89) are primary. OL is not modeled.

## EDGE role gate

The existing per-position role equation is fit on DL as a group. For EDGE,
refit `next_role ~ role_z + perf_z + B_draft` on the EDGE subgroup of the DL
role panel with player-clustered SE. If the subgroup has fewer than 40
player-seasons or the performance coefficient is not estimable, mark the role
route `sensitivity` or `unidentifiable`; do not report a base-case role value.

## Overlap and non-double-counting

- Position markets display selection + role as their own totals.
- The free-agency market displays contract pricing across positions.
- Each position market also shows its contract contribution, marked
  `in_free_agency_total`, excluded from the position total.
- Portfolio total = Σ(position selection + role) + free-agency contract total.
- The DL anchor's contract route is reconciled against the free-agency total,
  not added twice.
- Report the sum of base-case nets and the sum of low-case nets. The low-case
  sum is the conservative guide when role and contract decisions share an
  organizational driver. No additional ad hoc overlap haircut.

**Free-agency aggregate.** For each cap-covered position `p`, contract gross is
`contract_portfolio_p × pricing_correction_p`. The market total is
`Σ_p contract_p − implementation_cost`; one adoption probability applies to the
net. Do not subtract an implementation cost per position.

## Free-agency descriptive layer

- `rent_players.csv` residuals (`resid_cap`) describe over/underpay by position
  and experience; this is the existing rent proxy, not a causal claim.
- `ngs_status` (UFA/TRD/TRC/etc.) and contract start/end years distinguish
  free-agent-eligible from signed players; compare residual distributions
  descriptively.
- nflverse `trades.csv` and `draft_picks.csv` provide market context (trade
  frequency, pick values). No causal event study.
- `historical_contracts.csv.gz` (1983–2022) provides long-run APY/cap-share
  context; it is not linked to 2023–25 performance and is not a valuation input.

## Coaching retention

- Derive coach-team-season tenure from `data/external/games.csv`
  (`home_coach`/`away_coach`, 1999–2026).
- Add public hire/fire dates (PFR/Wikipedia), date-stamped; use first/last game
  season as the tenure proxy if exact dates are unavailable.
- Descriptive model: `retained_next ~ wins + point_diff + tenure + C(season)`,
  linear probability with team-clustered SE (primary); logit as sensitivity.
  No dollar value.
- Reading: retention is wins/status-driven; the allocation chunk protects the
  coach, not challenges him.

## Special teams

- Build an ST composite from `stats_player_reg_*.csv`: K (FG%, PAT%, long FG,
  touchback), P (net yards, inside-20, touchback), return (yards/attempt, TDs),
  coverage/blocks (tackles, blocks).
- Minimum attempts (20 FG, 30 punts); split-half reliability by odd/even games
  within ST role (K, P, returner), Spearman-Brown corrected.
- If reliability ≥ 0.50: descriptive `logcap ~ st_perf_z + age + exp` by ST
  role; otherwise mark `unidentifiable` and keep the market
  descriptive/messaging-only.
- No selection or role dollar model; ST is a salary-layer market.

## Data sources

| Source | URL | Use | License |
|---|---|---|---|
| nflverse trades | `github.com/nflverse/nflverse-data/releases/download/trades/trades.csv` | trade context | public nflverse; cite |
| nflverse draft picks | `github.com/nflverse/nflverse-data/releases/download/draft_picks/draft_picks.csv` | draft/trade context | public; cite nflverse/PFR |
| PFR coaches / Wikipedia | `pro-football-reference.com/coaches/`; `en.wikipedia.org/wiki/List_of_current_NFL_head_coaches` | coach tenure/hire dates | cite; no bulk redistribution |
| historical contracts | local `data/external/historical_contracts.csv.gz` | contract APY context | Apache-2.0 |
| nflverse stats | local `data/external/stats_player_reg_*.csv` | ST composite | public nflverse; cite |

Raw downloads stay in `data/external/market/` (gitignored); only derived
aggregates are written to `outputs/`.

## Non-goals

- No causal identification, no claim that the pricing correction causes a
  change in pay, no claim about any executive's intent.
- No paid coaching/contract feeds; no raw source redistribution.
- No modification of `writeup/`, the public notebook, the existing
  `implications/` package, or the `transfer/` extension.
- No signal-led selection outside DL/EDGE; WR is a sensitivity only.
