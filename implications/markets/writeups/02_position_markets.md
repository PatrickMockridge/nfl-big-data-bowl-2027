# Position markets

The position markets count **selection + role** in their own totals. Their
contract rows are **legacy top-down display only**; the free-agency market is
now the dedicated [`free_agency/`](../../free_agency/README.md) bottom-up
estimate from the actual 2026 signing class. Do not add the display rows to the
free-agency total. All dollars are $M/year and are inferences.

## EDGE

| Route | Low | Base | High | Evidence |
|---|---:|---:|---:|---|
| Selection | 0.03 | 0.37 | 1.16 | transfer L1 +0.166 (0.029, 0.303), Holm p=0.054 |
| Role | 0.20 | 1.87 | 6.93 | DL role subgroup; descriptive |
| Contract (display) | 1.76 | 7.83 | 16.43 | pricing gap 0.326 (0.084, 0.567) |
| **Position net** | **−0.27** | **1.24** | **6.09** | selection + role − implementation |

EDGE is the only new market with a supported transfer coefficient, and it is
borderline: the task-matched pass-rush signal clears zero at the unadjusted
level but not after the Holm correction, and it adds no out-of-sample R² over
the stopwatch. The role route uses the EDGE subgroup of the DL role panel
(56 player-seasons); the allocation pattern is descriptive. The contract
contribution is the largest of the position display rows because EDGE has the
largest pricing gap and a large portfolio.

**Chunk:** add the pass-rush drill to the EDGE board as a screening input;
reallocate 10–15% of pass-rush snaps; review EDGE renewals. **Losers:** the
low-burst veteran and the stopwatch-first scout.

## WR

| Route | Low | Base | High | Evidence |
|---|---:|---:|---:|---|
| Selection | 0.00 | 0.00 | 0.42 | weak signal; high case only |
| Role | 0.10 | 1.40 | 6.12 | allocation gap +0.56 to −1.46; descriptive |
| Contract (display) | 0.14 | 0.60 | 1.27 | pricing gap 0.030 (−0.207, 0.267) |
| **Position net** | **−0.40** | **0.40** | **4.54** | selection + role − implementation |

WR is the strongest non-DL **allocation** market and the weakest new
**measurement** market. The route-drill signal is +0.053 with a CI spanning
zero; the base selection route is zero, and the high case is a sensitivity. The
role gap is monotonic and large. The pricing correction is small and its gap CI
includes zero, so the WR contract row is conservative.

**Chunk:** use the route drill as a sensitivity, not a base-case rank; reallocate
10–15% of route participation; review WR renewals. **Losers:** the low-route
veteran and the scout who trusts the stopwatch.

## DB (CB/S)

| Route | Low | Base | High | Evidence |
|---|---:|---:|---:|---|
| Selection | 0 | 0 | 0 | unidentifiable |
| Role | 0 | 0 | 0 | performance residual has zero variance |
| Contract (display) | 1.61 | 7.14 | 15.00 | CB gap 0.224 (0.031, 0.418); S gap 0.331 (0.170, 0.492) |
| **Position net** | **0** | **0** | **0** | no own initiative |

DB is a **pricing-only** market. The measurement and allocation links are
unidentifiable; the contract route is estimable in the salary layer. The
40-yard-priced / back-pedal-unpriced contrast is the cleanest transfer in the
dataset, but it is descriptive. The $7.14M contract contribution is counted in
the free-agency total, not here.

**Chunk:** contract review only; no coaching or role change. **Loser:** the
incumbent contract, not the coach.

## OL

| Route | Low | Base | High | Evidence |
|---|---:|---:|---:|---|
| Selection | 0 | 0 | 0 | signal reliability 0.448 |
| Role | 0.17 | 1.89 | 6.52 | allocation gap +0.71 to −0.80; descriptive |
| Contract | 0 | 0 | 0 | no individual performance in the cap ledger |
| **Position net** | **−0.33** | **0.89** | **4.53** | role − implementation |

OL is **allocation-only**. The role gap is strong and monotonic, but the
pass-set signal fails reliability and the cap ledger has no individual
performance measure, so there is no pricing route. The role route uses the NGS
pressure-allowed residual (reliability 0.553).

**Chunk:** role review using pressure allowed; no contract route. **Loser:** the
coach's discretionary depth chart.

## TE

| Route | Low | Base | High | Evidence |
|---|---:|---:|---:|---|
| Selection | 0 | 0 | 0 | outcome reliability 0.449 |
| Role | 0 | 0 | 4.05 | sensitivity only; 27 role rows |
| Contract (display) | 0 | 0 | 0 | pricing correction zero |
| **Position net** | **0** | **0** | **4.05** | high-case role only |

TE is a descriptive market. The outcome reliability and role sample fail the
gates; the pricing correction is zero. The high-case role value is a sensitivity,
not a base case. **Chunk:** role review only; no base-case dollar claim.

## What the position markets are not

- They are not a sum of every route. The contract rows are legacy top-down
  display only; the free-agency market is the dedicated bottom-up report and
  does not add these rows.
- They are not a claim that the Combine signal works outside DL. EDGE is
  borderline; WR is a sensitivity; TE/OL/DB are unidentifiable for measurement.
- They are not causal. The role route is a descriptive allocation pattern; the
  selection route is an association plus a hit-rate assumption.
