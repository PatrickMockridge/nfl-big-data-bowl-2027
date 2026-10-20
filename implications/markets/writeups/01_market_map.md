# The market map: which route can each market defend?

## Matrix

| Market | Selection | Role | Contract | Why |
|---|---|---|---|---|
| Interior DL (anchor) | modeled | modeled | modeled | All three links are measured or descriptive; existing package. |
| EDGE | modeled | modeled | display only | Borderline pass-rush signal; DL role subgroup; contract row is legacy top-down. |
| WR | sensitivity | modeled | display only | Route signal weak; allocation gap strong; pricing gap small. |
| DB (CB/S) | not modeled | not modeled | display only | Zero-variance performance residual; the 40-yard/back-pedal contrast is descriptive. |
| OL | not modeled | modeled | not modeled | Signal reliability 0.448; allocation gap strong; no cap-ledger performance. |
| TE | not modeled | sensitivity | display only | Outcome reliability 0.449; 27 role rows; pricing correction zero. |
| Free agency / contract | — | — | modeled | Per-position role-controlled pricing across nine groups. |
| Coaching retention | — | — | — | Descriptive: wins/tenure, no dollar. |
| Special teams | — | descriptive | descriptive | K/P reliability below 0.50; returner composite passes but no separate cap market. |

"Display only" means the position market shows the contract contribution for
completeness, but that amount is counted in the free-agency market, not in the
position total.

## The anchor

The DL anchor is the existing implications package. It reconciles exactly:

| Item | Existing package | Portfolio treatment |
|---|---:|---|
| Selection | $0.79M | counted in the DL position row |
| Role | $2.10M | counted in the DL position row |
| Contract | $3.75M | legacy top-down; superseded by the dedicated report |
| Gross | $6.64M | — |
| Net | $5.64M | — |
| Portfolio DL selection + role | — | $2.45M after proportional cost |

The portfolio does not add the $5.64M on top of the market rows. It counts the
selection + role piece in the DL row. The contract piece is part of the legacy
top-down free-agency estimate; the dedicated
[`free_agency/`](../../free_agency/README.md) report replaces it with a
bottom-up estimate from the actual 2026 signing class. The legacy contract
component remains in `contract_components.csv` as a cross-check and is not added
to the portfolio.

## What is not modeled, and why

- **DB:** the BDB performance residual has zero variance; the Combine and role
  links are unidentifiable. The contract route uses the salary layer's
  performance composite, which is a different construct. The market is a
  contract-pricing contribution only.
- **OL:** the cap ledger has no individual performance measure, so the
  contract route is not modeled. The role route uses the NGS pressure-allowed
  residual (reliability 0.553).
- **TE:** the outcome reliability is 0.449 and the role cell has 27 rows. The
  role route is a high-case sensitivity only; the pricing correction is zero.
- **Special teams:** K reliability 0.114 and P reliability 0.457 fail the 0.50
  gate. The returner composite passes (0.776) but returners are paid through
  their offensive/defensive position, not a separate ST cap market.
- **Coaching:** no coach-level allocation-efficiency measure. The retention
  model is descriptive and has no dollar value.

## Data coverage

| Source | Coverage | Use |
|---|---|---|
| 2025 OTC cap ledger | 1,693 players; OL 290, ST 91, LB 248, WR 187 | market values, portfolios |
| 2025 rent ledger | 909 players with `perf_z`; nine groups | per-position pricing |
| OTC team positional spending | 32 teams × 2025 | contract portfolio scaling |
| nflverse trades | 4,975 rows, 2002–2026 | market context |
| nflverse draft picks | 12,927 rows, 1980–2026 | market context |
| Coaching tenure | 893 team-seasons, 1999–2026 | retention description |
| Historical contracts | 423 season-position cells, 1994–2022 | long-run APY context |
| ST weekly stats | 2023–2025 | reliability gate |

## Cross-construct caveat

Every contract route uses the salary layer's `perf_z` (nflverse production), not
the BDB NGS performance residual. The pricing leg is internally consistent with
the existing cap model, but it is not the same construct as the transfer L1/L3
performance measure. This is why DB can be priced while its measurement and
allocation links remain unidentifiable.
