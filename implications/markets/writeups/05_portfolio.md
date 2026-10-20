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
| Free agency / contract | 6.05 uncut / 1.82 capture | 0.38 uncut / −0.45 capture | 0.88 uncut / −0.29 capture | 2.42 |
| **Total (uncut)** | **11.03** | **5.37** | **0.18** | **4.41** |

**Dual totals.**

| Total | Base | Conservative | Low | Base EV |
|---|---:|---:|---:|---:|
| Uncut premium | 11.03 | 5.37 | 0.18 | 4.41 |
| Capturable at the scenario haircut | 6.80 | 4.54 | −0.99 | 2.72 |

All values $M/year. The **base** uses the point estimates and the base
assumptions; the **conservative** view zeroes the pricing gaps whose CI includes
zero in the contract/free-agency market; the **low** case uses the low
assumptions throughout. Position-market nets have no pricing-gap leg, so their
conservative equals base. The low stress case is the capturable **−$0.99M**.

The composition is the headline: **position selection + role is about $5.0M;
the contract market is $6.05M uncut / $1.82M capture base and $0.38M uncut /
−$0.45M capture conservative.** The contract market is still the largest single
market, but no longer an order of magnitude larger. The old $24.9M top-down
estimate was a 90.6th-percentile synthetic portfolio; the dedicated
[`free_agency/`](../../free_agency/README.md) report finds a median-team annual
role premium of $7.05M uncut / $1.82M net at the 0.40 capture assumption. The
dollar case is still a pricing-correction case, not a Combine-signal case.

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
| Free agency (all), uncut | 3.35 | 5.96 | 9.23 | 2.32 |
| Free agency (all), capture at 0.40 | 0.58 | 1.69 | 3.04 | 0.65 |
| Free agency (EDGE/S/CB), capture at 0.40 | −1.16 | −0.65 | −0.19 | −0.25 |

The per-market draws are independent; the portfolio does not add a joint Monte
Carlo total because the role and contract routes are correlated through the same
adoption decision. The deterministic capturable low case (−$0.99M) is the wider
stress range. The free-agency rows are from the dedicated
[`free_agency/`](../../free_agency/README.md) Monte Carlo;
`market_monte_carlo.csv` does not duplicate them. At the 0.40 capture
assumption, the EDGE/S/CB subset is negative in 97% of draws; the capture does
not cover the implementation cost in the conservative case.

The per-market sensitivity table is on the **portfolio net**. For the DL anchor,
that is selection + role only; the contract route's sensitivity lives in the
free-agency market and in the existing
`implications/outputs/sensitivity.csv`.

## Sequencing

1. **Contract market first.** It is the largest route: reprice the next renewal
   wave on role-controlled performance. It does not touch the depth chart, but
   it is not politically costless; the cost falls on the incumbent player and
   agent whose price is repriced.
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
  conservative view rises toward the all-position base ($7.05M uncut / $1.82M
  capture net). The old $24.9M remains an upper-tail team, not the median.
- **Portfolio size.** The contract value is linear in the renewal portfolio. A
  team with fewer renewals or more guaranteed money sees less.
- **Adoption.** The EV is net × adoption. The base 40% is a judgment; the low
  case is 20%.
- **Role route.** If the depth-chart null is a measurement artifact rather than
  a real allocation pattern, the position markets shrink. The transfer
  extension already reports the reliability caveats.
- **Overlap.** If role and contract decisions are one organizational change,
  the capturable low case (−$0.99M) is the right guide, not the arithmetic base.

## What the portfolio is not

- It is not a forecast. It is a structured way to see which routes carry the
  dollars and which assumptions matter.
- It is not a causal claim about any team, coach, or executive.
- It is not a sum of every route. The contract rows on the position markets are
  display-only.
- It is not a claim that the Combine signal works outside DL. The position
  selection values are zero or sensitivity-only outside DL/EDGE.
- It is not a social saving. The contract route is a transfer from players to
  clubs; the incumbent player and agent bear the cost. The model is symmetric:
  agents can use it too.
