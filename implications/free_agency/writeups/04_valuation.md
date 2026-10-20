# Bottom-up valuation: the actual 2026 signing class

## The estimate

The one-team estimate is the **median team's annual role premium** in the 2026
signing class. The league total is context; the mean is reported because the
distribution is skewed.

| Scenario | Gross $M/yr | Contract-total median $M | Cost $M | Net $M/yr | EV $M/yr |
|---|---:|---:|---:|---:|---:|
| Low (supported positions, 0.15 haircut) | 0.52 | 0.42 | 0.50 | 0.02 | 0.00 |
| **Base (all positions, 0.40)** | **7.05** | **5.80** | **1.00** | **6.05** | **2.42** |
| Conservative (EDGE/S/CB, 0.40) | 1.38 | 1.13 | 1.00 | 0.38 | 0.15 |
| High (all positions, 0.60) | 10.57 | 8.70 | 2.00 | 8.57 | 5.14 |

The **base** is $7.05M gross / $6.05M net / $2.42M expected at 40% adoption.
The **conservative** view keeps only the positions whose cap-ledger role-premium
CI is above zero (EDGE, S, CB) and is $1.38M gross / $0.38M net. The **low**
case is near zero.

The base covers the median team's 9 contracts with observed APY, performance,
role, age, and team. The contract-total median ($5.80M) multiplies the APY
premium by contract years and the 0.40 haircut.

## Team distribution

| Percentile | Annual role premium ($M) |
|---|---:|
| P10 | 1.81 |
| P25 | 4.68 |
| P50 | 7.05 |
| P75 | 13.62 |
| P90 | 22.51 |
| Mean | 10.73 |
| Min | 0.40 |
| Max | 43.31 |

The distribution is right-skewed. The median team is $7.05M; the mean is
$10.73M; the top decile starts at $22.5M. The **old top-down $24.91M sits at the
90.6th percentile**. The old conservative $13.97M is near the 75th percentile
($13.62M).

## The bridge from the top-down estimate

| Measure | Value ($M) | Note |
|---|---:|---|
| Old top-down base | 24.91 | synthetic one-team portfolio |
| Old top-down conservative | 13.97 | CI-supported positions |
| Old top-down low | 5.33 | low assumptions |
| New median team annual | 7.05 | actual 2026 signings |
| New mean team annual | 10.73 | distribution mean |
| New median team contract total | 5.80 | APY premium × years × 0.40 |
| New league annual | 343.37 | all 32 teams; context only |
| Old base percentile | 90.6% | share of teams below $24.9M |
| New supported median annual | 1.38 | EDGE/S/CB only |

The difference is not one error. It is the combination of:

1. **Actual contract population vs synthetic portfolio.** The top-down model
   scaled a $50M DL portfolio by team positional spending. The median team's
   actual 2026 signing class has 9 contracts with observed performance; the
   synthetic portfolio was much larger. This is the largest driver.
2. **All positions vs CI-supported positions.** The base uses every position's
   pooled role premium; the conservative keeps only EDGE/S/CB, whose cap-ledger
   gap CIs are above zero. $7.05M → $1.38M.
3. **APY vs cap hit.** The 2026 APY gap 0.179 is close to the 2025 cap gap
   0.185; this is not the main driver.
4. **Prior vs concurrent performance.** The 2026 event sample gap 0.179 is
   larger than the 2025 active APY cross-check 0.105; the event sample is the
   appropriate one for a signing decision.
5. **Draft controls.** The draft-matched gap 0.151 is 16% smaller than 0.179;
   a modest haircut.
6. **Haircut.** 0.40 is a judgment; the low (0.15) and high (0.60) cases show
   the range.

The honest conclusion: **the free-agency lever is real, but the old $24.9M was
an upper-tail team's synthetic portfolio, not the median team's actual
renewal wave.** The median team's bottom-up base is about $6M net per year; the
CI-supported subset is about $0.4M.

![Top-down vs bottom-up and the team distribution.](figures/fa_valuation.png)

## Monte Carlo

20,000 draws, seed 20261020; team resampling, haircut triangular
(0.15, 0.40, 0.60), cost (0.5, 1.0, 2.0), adoption (0.2, 0.4, 0.6).

| Population | Net P10 | Net P50 | Net P90 | EV P50 | P(net > 0) |
|---|---:|---:|---:|---:|---:|
| All positions | 3.35 | 5.96 | 9.23 | 2.32 | 1.00 |
| EDGE/S/CB only | −0.69 | 0.09 | 0.87 | 0.03 | 0.56 |

The all-position case is positive across the draws; the CI-supported subset is
a coin flip. That is why the report leads with both.

## Portfolio update

The market portfolio now uses this report's bottom-up summary:

- Free agency: **$6.05M base / $0.38M conservative / $0.02M low**.
- Portfolio total: **$11.03M base / $5.37M conservative / −$0.68M low**.
- The free-agency market is still the largest single market ($6.05M versus
  $2.45M for the DL anchor's selection + role), but no longer an order of
  magnitude larger.
- The old top-down components remain in `contract_components.csv` as a
  `legacy_top_down` cross-check; they are not added to the portfolio.

## What would change the estimate

- **A larger renewal population.** A team with more high-APY contracts with
  observed performance moves toward the top decile.
- **More CI-supported positions.** If IDL, LB, or WR gaps become CI-supported,
  the conservative view rises toward the base.
- **Guarantees and structure.** If the role premium is paid in guarantees
  rather than APY, the headline APY saving overstates the cash saving. The
  guarantee model shows role predicts guarantees; the report does not net them
  out in the base.
- **Adoption and negotiation.** The EV applies a flat adoption probability; a
  real negotiation response would reduce it.
- **A different haircut.** 0.40 is a judgment; 0.15 gives a near-zero low case,
  0.60 a high case around $8.6M net.
