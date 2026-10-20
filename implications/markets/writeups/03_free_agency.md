# Free agency — superseded by the dedicated investigation

**Status:** this section is superseded by
[`implications/free_agency/`](../../free_agency/README.md). The market portfolio
now uses that report's bottom-up estimate. The old top-down components remain in
`contract_components.csv` as a `legacy_top_down` cross-check and are not added
to the portfolio.

## What changed

The original section estimated a cross-position pricing correction by fitting
nine per-position cap models on the 2025 ledger, applying a 0.40 haircut, and
multiplying by a synthetic contract portfolio (`50 × team position spend / team
IDL spend`). It produced:

| Scenario | Old top-down net |
|---|---:|
| Base | $24.91M |
| Conservative | $13.97M |
| Low | $5.33M |

The dedicated report rebuilt the estimate from the **actual 2026 signing
class** (1,086 contract rows; 302 non-rookie veterans with performance) and
replaced the synthetic portfolio with observed APY, years, performance, role,
age, and team. It produces a **median-team** estimate:

| Scenario | New bottom-up gross | New bottom-up net |
|---|---:|---:|
| Base | $7.05M | $6.05M |
| Conservative (EDGE/S/CB) | $1.38M | $0.38M |
| Low | $0.52M | $0.02M |
| High | $10.57M | $8.57M |

The old $24.91M sits at the **90.6th percentile** of the 32-team annual role
premium distribution. The median team is $7.05M; the mean is $10.73M; the top
decile starts at $22.5M.

## Why

The difference is not one error. It is the combination of:

1. **Actual contract population vs synthetic portfolio.** The median team's
   actual 2026 class has 9 contracts with observed performance; the synthetic
   portfolio assumed a much larger renewal wave.
2. **All positions vs CI-supported positions.** Only EDGE, S, and CB have
   cap-ledger role-premium CIs above zero. The base uses all positions; the
   conservative keeps EDGE/S/CB and falls to $1.38M gross / $0.38M net.
3. **APY vs cap hit.** The 2026 APY gap 0.179 is close to the 2025 cap gap
   0.185; this is not the main driver.
4. **Prior vs concurrent performance.** The 2026 pre-signing gap 0.179 is larger
   than the 2025 active APY cross-check 0.105.
5. **Haircut.** 0.40 is a judgment; the low (0.15) and high (0.60) cases bound
   it.

## Reading

Free agency is still the largest single market in the portfolio ($6.05M base
versus $2.45M for the DL anchor's selection + role), but the old estimate was an
upper-tail team, not a typical one. The dedicated report carries the player-level
pricing, guarantees, surplus, valuation, adoption, and messaging. Read it in
full at [`implications/free_agency/`](../../free_agency/README.md).
