# Free-agency investigation protocol

**Status:** pre-registration for a GitHub-only extension. It is not part of the
judged Big Data Bowl entry and does not modify the artifacts frozen at
`c652424`. Date-stamped **2026-10-20**.

Every dollar figure is an **inference**. The contract models are player-level
cross-sectional associations plus robustness; they are not causal estimates.
The contract market is selection-heavy: free agents are not a random sample,
and the report says so.

## Questions

1. **Market description.** Who reaches free agency? What terms do they sign
   (APY, guarantees, years, age)? How do team-changing free agents differ from
   re-signings and rookie deals? How has positional value changed since 1983?
2. **Pricing.** What does the market pay for performance, role, age, and
   experience? Is the raw-vs-role premium present in APY, guarantees, and
   length? Is it larger for free agents than for re-signings?
3. **Surplus.** Which players, positions, and teams are above or below the
   market model? Is the surplus concentrated? Do guarantees track it?
4. **Bottom-up valuation.** What would the actual renewal population save under
   role-controlled pricing? Does that confirm, shrink, or overturn the
   market-portfolio's top-down **$24.91M base / $13.97M conservative**?
5. **Adoption and messaging.** What does a cap manager do, when, and with what
   contract structure? Who loses? What can and cannot be claimed?

## Samples

| Sample | Rows | Use | Caveat |
|---|---:|---|---|
| 2025 OTC cap ledger (`rent_players.csv`) | 909 with `perf_z` | cap-number reconciliation, cash robustness | one season; cap hit not APY |
| 2025 active APY contracts (`contract_players.csv`, season 2025) | 932; 496 with `perf_z` | APY cross-check | ~48% of 2025 snaps |
| 2026 free-agent class (`player_contracts.csv`, `start == 2026`) | 1,046 signings; ~594 with 2025 performance | primary pre-signing event sample | no signing dates; type inferred |
| Historical contracts (`historical_contracts.csv.gz`) | 31,893 raw; 30,769 after dropping `year_signed=0`, 1983–2022 | positional value, guarantees, age trends | no performance link |
| 2024 contracts | 430 active rows | sensitivity | thin |

**Primary pre-signing model:** 2026 signings with a 2025 performance row,
excluding rookie deals and players without prior-season performance. The full
2026 class is used for composition and terms description.

**Data audit correction (2026-10-20).** The first panel build found 1,086
contract rows / 1,043 players in the 2026 class, 696 with 2025 snaps, **307 with
a 2025 performance row**, and **306 with a usable APY and non-null `perf_z`**
(one of the 307 has no usable APY). The 306 are non-rookie; the role model uses
**n=301** because five lack a non-missing `snap_share`. The "~594 with
performance" figure in the samples table counted a performance row, not a
non-null `perf_z`. The primary 2026 model therefore uses n=306; the pooled
2025+2026 APY model (with a sample dummy) is the larger cross-check. This is a
sample-size correction, not a gate change.

**Primary cross-check:** 2025 active APY contracts with 2025 performance.

**Cap-ledger reconciliation:** the 909-player sample; must reproduce the
existing 0.328 raw / 0.143 role coefficients and the IDL gap 0.185.

**Historical:** descriptive only; no performance link.

## Contract-event panel

One row per contract event:

- identity: player, `otc_id`, `gsis_id`, `pfr_id`, `name_key`;
- team and prior team; `team_change`; `same_team`;
- contract: `start`, `end`, `years`, `value`, `apy`, `guaranteed`,
  `guarantee_share`, `guarantee_source`, `age_at_signing`;
- type dummies: `rookie` (`start == rookie_season`), `team_change`, `one_year`;
  reference `re_sign` (same team, not rookie). Dummies are not mutually
  exclusive; franchise tag is not identifiable;
- performance: prior-season `perf_z` (2025 for 2026 signings; 2024 for 2025
  contracts where available);
- role: prior-season `snap_share`;
- draft: `draft_year`, `draft_round`, `draft_pick`, `B_draft` within
  position × class;
- market: position group, season, team.

Join discipline: `gsis_id` first; `otc_id` for historical; `name_key` fallback.
Expected match rates: contracts→performance 84.7%, contracts→snaps 80.2%; cap
ledger→performance 89.1%, →snaps 98.2%; historical→players 87.3%.

Use only the contract columns of `data/external/player_contracts.csv`; its
embedded weekly-stat columns are corrupted and are not used. Re-join performance
from nflverse.

Free-agent status is inferred: no transaction feed, no signing dates, no
franchise-tag field. `ngs_status` is a current point-in-time flag, not a time
series. Every free-agent premium table states this.

## Pricing models

### Primary: 2026 free-agent class (APY)

```
raw:   log(apy) ~ perf_z_2025 + age_at_signing + age_at_signing^2
                  + years_exp + team_change + C(position)
role:  raw + snap_share_2025
```

- Primary sample excludes rookie deals. A full-sample sensitivity adds a
  `rookie` dummy and `C(signing_year)`.
- Team-clustered SE (32 teams); HC1 robustness.
- The **role premium** is the raw `perf_z` coefficient minus the role-controlled
  one. The pooled APY model is the contract-term evidence; per-position APY
  cells are exploratory below n=60, while position-level claims lean on the
  909-player cap-ledger models.
- `perf_z × team_change` and `snap_share × team_change` test the
  free-agent-specific premium.
- `B_draft` in a draft-matched robustness.

### Cross-check: 2025 active APY contracts

Same specification with 2025 performance and role, `C(position)` and
`C(start_year)`. n≈496. This asks whether the gap is an APY result or a cap-hit
artifact.

### Cap-ledger reconciliation

```
log(cap_number) ~ perf_z + snap_share + age_start + years_exp + C(pos_group)
```

Must reproduce 0.328 (0.264, 0.392) raw and 0.143 (0.078, 0.208) role, and the
per-position IDL gap 0.185.

### Guarantees and length

```
guarantee_share ~ perf_z + snap_share + age + age^2 + years
                  + team_change + C(position) + C(signing_year)
years           ~ perf_z + snap_share + age + age^2 + team_change
                  + C(position) + C(signing_year)
```

Bounded outcomes use OLS with robust SE; fractional logit as a sensitivity.

### Robustness

- APY vs cap number vs current-year cash.
- Prior-season vs concurrent performance.
- Draft-matched sample with `B_draft`.
- 2024 contracts as a thin sensitivity.
- Position-specific vs pooled.
- Age quadratic vs binned/spline.
- Team fixed effects as a sensitivity, not primary.

## Surplus

- Raw-market residual: `actual_apy − exp(pred_raw_apy)`.
- Role-controlled residual: `actual_apy − exp(pred_role_apy)`.
- The difference between raw and role predictions is the player-level role
  premium.
- Aggregate by position, age, contract type, and team; report the distribution
  and top-decile concentration.
- Guarantee share and years for above/below-market contracts.
- Team surplus linked descriptively to wins, point differential, and offensive
  EPA. No causal claim.

## Bottom-up valuation

Two populations:

- **Actual 2026 signings** (observed APY and terms) — primary.
- **Contracts ending 2026–2028** — forward renewal wave, projected with current
  APY/performance; labeled a projection.

For each contract:

```
role_premium_apy_i = exp(pred_raw_i) − exp(pred_role_i)
saving_i           = max(role_premium_apy_i, 0) × years_i × haircut
```

- Primary haircut **0.40** to mirror the existing package; **0.15 / 0.60** and
  the uncut premium are sensitivities.
- Report annual and contract-total savings; APY primary, cash/cap robustness.
- Scenarios: base, conservative (only position gaps with CI excluding zero),
  low (lower coefficient/haircut).
- Monte Carlo: coefficient uncertainty, haircut, adoption, and contract
  sampling; seed fixed at **20261020**.
- Build a bridge from the top-down synthetic portfolio ($24.91M base /
  $13.97M conservative) to the bottom-up estimate: APY vs cap, prior vs
  concurrent performance, draft controls, actual renewal population,
  guarantees. State plainly whether the new estimate confirms, shrinks, or
  overturns the old one.

## Portfolio-update interface

The market portfolio reads
`implications/free_agency/outputs/valuation_summary.csv` for its
`free_agency` row. Columns:

`scenario` (`low`/`base`/`conservative`/`high`), `gross_m`,
`implementation_cost_m`, `net_m`, `ev_m`, `method` (`bottom_up`),
`n_contracts`, `notes`.

If the file is missing, the market model falls back to the legacy top-down
components with a warning. The old `contract_components.csv` remains a
`legacy_top_down` cross-check. The dedicated report owns the free-agency
sensitivity and Monte Carlo; the market model imports the summary/MC or marks
the legacy rows `legacy_top_down`, and does not present the synthetic tornado as
the headline.

## Historical trends

- `age_at_signing` from `date_of_birth` and `year_signed`; map positions to
  groups; compute guarantee share and APY cap share.
- Date of birth is available for ~62% of historical rows; age series drop the
  rest and state coverage. Drop `year_signed = 0`.
- Descriptive series: median APY cap share, guarantee share, age at signing,
  contract count, top-5 APY share, by position × year.
- No performance link; historical is trend context, not a role-premium test.

## Evidence tiers

- **Measured association:** a player-level model coefficient with a 95% CI.
- **Descriptive:** a distribution, median, or group contrast.
- **Inference:** a dollar figure produced by the valuation assumptions.
- **Reading:** adoption/messaging judgment, date-stamped.

No causal claim. Free agents are selected; APY, cap hit, and cash are different
measures; guarantees and length are selection-laden.

## Non-goals

- No causal free-agency event study; the data lack a transaction feed, signing
  dates, injuries, prior contracts, and agent representation.
- No paid or private data.
- No modification of the judged entry or the transfer extension.
- No claim that the top-down $24.9M must be preserved; the bottom-up estimate
  may be smaller.
