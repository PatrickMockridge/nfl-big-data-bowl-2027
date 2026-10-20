# Portfolio: totals, overlap, and sequencing

## The portfolio

| Market | Base net | Conservative | Low net | Base EV |
|---|---:|---:|---:|---:|
| Interior DL (selection + role) | 2.45 | 2.45 | 0.29 | 0.98 |
| EDGE | 1.24 | 1.24 | −0.27 | 0.50 |
| WR | 0.40 | 0.40 | −0.40 | 0.16 |
| OL | 0.89 | 0.89 | −0.33 | 0.36 |
| DB (CB/S) | 0.00 | 0.00 | 0.00 | 0.00 |
| TE | 0.00 | 0.00 | 0.00 | 0.00 |
| Free agency / contract | 6.05 | 0.38 | 0.02 | 2.42 |
| **Total** | **11.03** | **5.37** | **−0.68** | **4.41** |

All values $M/year. The **base** uses the point estimates and the base
assumptions; the **conservative** view zeroes the pricing gaps whose CI includes
zero; the **low** case uses the low assumptions throughout.

The composition is the headline: **position selection + role is about $5.0M;
the contract market is $6.05M base / $0.38M conservative.** The contract market
is still the largest single market, but no longer an order of magnitude larger.
The old $24.9M top-down estimate was a 90.6th-percentile synthetic portfolio;
the dedicated [`free_agency/`](../../free_agency/README.md) report finds a
median-team annual role premium of $7.05M gross / $6.05M net. The dollar case is
still a pricing-correction case, not a Combine-signal case.

## No double counting

- Position markets count selection + role. Their contract rows are legacy
  top-down display only and are not added to the free-agency total.
- The free-agency market is the dedicated
  [`free_agency/`](../../free_agency/README.md) bottom-up estimate from the
  actual 2026 signing class, not the sum of the position display rows.
- The DL anchor's full net ($5.64M) is not added. Its selection + role ($2.45M)
  is in the DL row. Its contract route is part of the legacy top-down estimate
  and is superseded by the bottom-up report; it is not counted separately.
- The low-case sum is the conservative guide when role and contract decisions
  share an organizational driver. The arithmetic base and the low case are both
  reported; no additional ad hoc haircut is applied.

## Monte Carlo

20,000 triangular draws, seed 20261020, disabled routes pinned at zero.

| Market | Net P10 | Net P50 | Net P90 | EV P50 |
|---|---:|---:|---:|---:|
| Interior DL | 1.39 | 2.05 | 2.87 | 0.81 |
| EDGE | 0.15 | 1.13 | 2.46 | 0.43 |
| WR | −0.43 | 0.47 | 1.69 | 0.18 |
| OL | −0.25 | 0.70 | 1.94 | 0.27 |
| Free agency (all positions) | 3.35 | 5.96 | 9.23 | 2.32 |

The per-market draws are independent; the portfolio does not add a joint Monte
Carlo total because the role and contract routes are correlated through the same
adoption decision. The deterministic low case is the wider stress range. The
free-agency row is from the dedicated
[`free_agency/`](../../free_agency/README.md) Monte Carlo;
`market_monte_carlo.csv` does not duplicate it.

The per-market sensitivity table is on the **portfolio net**. For the DL anchor,
that is selection + role only; the contract route's sensitivity lives in the
free-agency market and in the existing
`implications/outputs/sensitivity.csv`.

## Sequencing

1. **Contract market first.** It is the largest and lowest-political-cost lever:
   reprice the next renewal wave on role-controlled performance. It does not
   touch the depth chart.
2. **EDGE role second.** The signal is borderline, but the role route is a
   contained sub-package change. If the signal fails its own pilot, the role
   review still has descriptive support.
3. **WR and OL role reviews third.** Both have strong allocation gaps and no
   defensible signal-led selection. The reviews are process changes, not
   player-ranking changes.
4. **Coaching and special teams last, as descriptive.** They inform the
   framing (protect the coach; review ST roles) but carry no dollar case.

The first-mover clock remains 2–5 years. The contract market may reprice faster
than the role market because it is visible in every negotiation.

## What would change the portfolio

- **Pricing-gap CIs.** If the EDGE/S/CB gaps shrink, the conservative
  free-agency total falls. If IDL/QB/LB gaps become CI-supported, the
  conservative view rises toward the all-position base ($7.05M gross / $6.05M
  net). The old $24.9M remains an upper-tail team, not the median.
- **Portfolio size.** The contract value is linear in the renewal portfolio. A
  team with fewer renewals or more guaranteed money sees less.
- **Adoption.** The EV is net × adoption. The base 40% is a judgment; the low
  case is 20%.
- **Role route.** If the depth-chart null is a measurement artifact rather than
  a real allocation pattern, the position markets shrink. The transfer
  extension already reports the reliability caveats.
- **Overlap.** If role and contract decisions are one organizational change,
  the low-case sum is the right guide, not the arithmetic base.

## What the portfolio is not

- It is not a forecast. It is a structured way to see which routes carry the
  dollars and which assumptions matter.
- It is not a causal claim about any team, coach, or executive.
- It is not a sum of every route. The contract rows on the position markets are
  display-only.
- It is not a claim that the Combine signal works outside DL. The position
  selection values are zero or sensitivity-only outside DL/EDGE.
