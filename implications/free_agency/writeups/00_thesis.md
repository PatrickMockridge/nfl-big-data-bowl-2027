# The free-agency market is large, but the top-down estimate was an upper-tail team

**Status:** GitHub-only extension of `implications/`, not part of the judged
entry. Date-stamped 2026-10-20.

## The question

The market portfolio's free-agency/contract correction was **$24.91M base /
$13.97M conservative / $5.33M low**, an order of magnitude above the DL
position case. That number came from nine per-position coefficient differences
on one 2025 cross-section, a judgment haircut of 0.40, a synthetic contract
portfolio (50 × team position spend / team IDL spend), and a simple sum. It was
a portfolio inference, not a contract-level estimate.

This report asks the player-level version of the question:

1. What does the free-agent market pay for performance, role, age, and
   experience?
2. How large is the raw-vs-role premium in actual APY, guarantees, and
   contract length?
3. What would the actual 2026 signing class save under role-controlled pricing?
4. Does that confirm, shrink, or overturn the $24.9M?

## The answer

**The market is large, but the old estimate was an upper-tail team.** The
actual 2026 signing class implies a median-team uncut annual role premium of
**$7.05M**; at the 0.40 capture assumption the annual capture is **$2.82M gross
/ $1.82M net** after a $1M implementation cost. The mean team is **$10.7M**,
the distribution runs from near zero to about $39M, and the old $24.9M sits at
the **90.6th percentile**. The conservative subset — only positions whose
cap-ledger gap CI is above zero (EDGE, S, CB) — is **$1.38M uncut / $0.55M
gross / −$0.45M net** for the median team. The low case is **$1.38M uncut /
$0.21M gross / −$0.29M net**.

This is not a rejection of the free-agency lever. It is a correction of its
scale: the contract market is still the largest single market in the portfolio
($6.05M uncut / $1.82M capture base versus $2.45M for the DL anchor's selection
+ role), but it is not an order of magnitude larger for a typical team. The
synthetic portfolio was a big-spending team's renewal wave, not the median
team's.

## What is measured, what is inferred

| Claim | Tier | Source |
|---|---|---|
| 2026 free-agent APY role premium +0.179 (0.022, 0.336) | measured association | `outputs/role_premium.csv` |
| 2025 cap-ledger gap +0.185 (0.094, 0.276) | measured association | `outputs/role_premium.csv` |
| 2025 APY cross-check +0.105 (−0.005, 0.214) | measured association | `outputs/role_premium.csv` |
| 2024 APY gap +0.029 (−0.169, 0.227) | measured association, thin | `outputs/role_premium.csv` |
| Draft-matched 2026 gap +0.151 (0.016, 0.286) | measured association | `outputs/role_premium.csv` |
| Team FE 2025 gap +0.099 (−0.036, 0.234) | measured association | `outputs/role_premium.csv` |
| Guarantees track role: snap-share coefficient 8.30 | measured association | `outputs/guarantee_years_models.csv` |
| The role premium is concentrated: top 10% = 51% | descriptive | `outputs/surplus_concentration.csv` |
| Median-team annual role premium $7.05M | inference | `outputs/valuation_summary.csv` |
| Old $24.9M sits at the 90.6th percentile | inference + descriptive | `outputs/valuation_bridge.csv` |
| Team changes vs re-signs | descriptive, inferred | `outputs/fa_class_2026.csv` |

## What this report does not claim

- **Not causal.** Free agents are selected; team changes are not random; APY is
  negotiated with unobserved information, injuries, and agent strategy.
- **Not a complete free-agency event study.** There is no transaction feed,
  signing date, franchise-tag field, or prior-contract history. Team changes
  and re-signs are inferred from the prior-season team.
- **Not a player ranking of who is "overpaid."** The residuals are deviations
  from a cross-sectional market model, not proof of a mistake.
- **Not a claim that the old $24.9M is wrong for every team.** It is a real
  upper-tail outcome; it is not the median team's outcome.
- **Not a replacement for the DL measurement.** The contract route uses the
  salary layer's nflverse performance composite, not the BDB NGS residual.
  The measurement link remains position-specific.

## Why the bottom-up estimate is more credible

The top-down estimate multiplied a coefficient difference by a synthetic
portfolio. The bottom-up estimate uses **actual contracts**: each 2026 signing's
observed APY, years, performance, role, age, and team. It still relies on a
model and a haircut, but the contract population and the dollar base are
observed. The report shows the bridge between the two, so the reader can see
exactly which assumption moved the number.
