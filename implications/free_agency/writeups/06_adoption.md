# The cap-manager playbook

## The chunk

The free-agency chunk is a **contract-pricing change**, not a depth-chart
change:

1. **Price the next renewal wave on role-controlled performance.** Use the
   role-controlled coefficient for the performance term; do not use the raw
   coefficient as the valuation anchor.
2. **Treat guarantees and length as part of the price.** Role predicts
   guarantee share (0.46 → 0.60 across snap-share quintiles) and contract years.
   A role-controlled APY with a raw guarantee structure is only half a
   correction.
3. **Target the concentrated tail first.** The top 10% of contracts account for
   51% of the positive role premium. A small number of high-APY renewals is the
   whole case.

## Timing

- **Early extension window:** the premium is largest where a high-performance,
  high-role player is paid on the raw coefficient. Extending before the market
  reprices captures the transition rent.
- **First-mover clock:** 2–5 years. If every team adopts role-controlled
  pricing, the surplus moves to players; the value is a transition rent, not a
  permanent edge.
- **Renewal wave:** contracts ending 2026–2028 are the forward population. The
  median team's actual 2026 class is 9 contracts with observed performance; a
  larger wave moves toward the top decile.

## Who loses

- The **incumbent agent/player** whose next contract is priced lower. This is a
  negotiation, not a coaching decision.
- **Teams that overpay** on the raw coefficient; the correction is a
  competitive advantage only until the market catches up.
- No coach loses snaps or authority. That is why this is the lowest-political-
  cost lever in the portfolio.

## Implementation sequence

1. **Data audit (week 1).** Build the team's own renewal ledger: APY,
  guarantees, years, age, prior-season performance, role, draft. Check the
  performance/role match rates; do not use the public model's coefficients
  blindly.
2. **Model the team's renewal wave (weeks 2–3).** Fit the raw and role-controlled
  APY models on the team's own contracts or the league sample; compare the
  coefficient gap. If the team's gap is near zero, stop.
3. **Select the tail (week 3).** Rank the renewal wave by role premium × years.
  The top decile is the negotiation list; the rest is monitoring.
4. **Negotiate structure (weeks 3–6).** Use APY, guarantees, and length
  together. A role-controlled APY with a raw guarantee is a partial win.
5. **Monitor (next cycle).** Track the realized APY/guarantee outcomes and the
  player's role/performance. If the role premium is a model artifact, the
  correction will not hold.

## Failure modes

- **The role premium is not stable.** The 2025 APY cross-check is 0.105 with a
  CI crossing zero; the 2024 sample is null. The 2026 event sample is the
  strongest evidence, but it is one class.
- **Draft and team controls absorb it.** The draft-matched gap is 0.151, 16%
  smaller than 0.179; the team-FE 2025 gap is 0.099 and crosses zero.
- **Guarantees offset the APY saving.** Role predicts guarantees; netting the
  guaranteed portion reduces the cash saving.
- **The agent responds.** A holdout, franchise tag, or extension threat can
  claw back the correction. The flat 40% adoption is a placeholder.
- **The sample is thin.** 302 non-rookie veterans with performance in the 2026
  class; the per-position cells are exploratory.

## Team fit

The natural reader is a cap manager or GM with a renewal wave and roster
authority. Transition regimes with many expiring contracts and a new
decision-maker are the best structural fit; stable contenders with few
renewals are a poor fit for this specific lever. This is a structural reading,
not a claim about any executive's views.
