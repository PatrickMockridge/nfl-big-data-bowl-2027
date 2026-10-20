# A low-political-cost chunk, six team fits, and the first-mover clock

**Status:** extension to the 2027 NFL Big Data Bowl entry, not part of it. GitHub only; not published on Kaggle. Staffing is date-stamped **2026-10-19** and must be re-verified before quoting the table. Team fit here is structural — roster state, regime tenure, cap position — not a claim about any executive's personal analytics views.

## The chunk

The finding does not require a club to abandon its draft board or its coaching philosophy. The low-political-cost chunk is three actions:

1. **Add the burst signal to the interior-DL draft board** as one input alongside tape, college production, and draft slot. It is a screening input, not a rank.
2. **In obvious pass-rush sub-packages, reallocate 10–15% of snaps** from a low-burst, high-cap veteran to a high-burst, low-cost interior lineman. The veteran loses pass-rush snaps, not starting status or pay.
3. **Price the next interior-DL contract on role-controlled performance** (+0.143) rather than the raw performance coefficient (+0.328).

**Who loses:** the low-burst veteran loses snaps; the coach loses some discretionary authority; the incumbent scout loses the comfort of the stopwatch. That is why this is **Pareto-adjacent**, not strictly Pareto efficient. A strict Pareto improvement would require no one to lose anything, and a snap reallocation cannot meet that test. The losses are concentrated; whether they are politically manageable is a judgment, not a finding.

## Team archetypes

The natural reader is a GM or analytics director with roster authority, a rebuild or a cap reset, and a coach they can plausibly align or challenge. The archetypes are described without naming current executives:

| Archetype | Why the structure fits | Caveat |
|---|---|---|
| New regime, defensive coach, high draft capital | Interior pressure is a live need; the regime can act together. | GM and coach may be aligned, which lowers the "challenge the coach" tension but raises the ability to act together. |
| Analytics-native GM, cap reset | The cap-versus-role frame is directly salient. | Ownership and a large guaranteed contract can constrain a clean reallocation. |
| Young, analytics-forward, draft-and-develop | The regime has a mandate to develop and re-price roles. | Not a full rebuild; pressure to win now. |
| New regime, roster and cap reset | Authority to re-price roles. | Both are new together, so the two-agent wedge is a design choice, not a live conflict. |
| New regime, defensive coach, clean slate | The teardown creates room for a role review. | The teardown may take precedence over fine-grained role allocation. |
| Patient, draft-heavy GM, new coach, young roster | Long horizon; role review fits the development plan. | The fit is structural, not a claim about personal analytics views. |

Stable or contending teams are poor fits for this specific piece: the coach has authority, and there is no allocation crisis to solve. This is a **transition-regime document**, not a contender document.

## Implementation sequence

1. **Data audit (week 1).** Reproduce the burst metric on the team's own charting and the competition data. Check the position-specific split and the outcome reliability: pressure split-half 0.44 (0.61 Spearman-Brown), sacks 0.33 (0.49). Do not use the signal outside interior defensive line.
2. **Coaching review (weeks 2–3).** Identify one or two pass-rush sub-package swaps, not a depth-chart overhaul. The coach keeps the starting lineup and the veteran's base snaps; the change is situational.
3. **Cap and legal review (weeks 3–4).** Model guarantees and dead money. The nominal $6M saving per decision can be smaller after proration and offsets; the role route is the largest single assumption in the valuation.
4. **Pilot (weeks 4–10).** Track pressure rate, sack rate, and snap counts for the affected players. Pre-register the decision rule: extend if the pressure differential holds and the locker-room cost is contained. Stop if the veteran's performance or the unit's pressure rate declines.
5. **Contract review (next cycle).** Use the role-controlled coefficient in the next interior-DL negotiation; do not use the raw +0.328 as a valuation anchor.

## The first-mover clock

The value is a **transition rent**, not a permanent edge. If one team adopts the principle, it captures the surplus from players the market has not repriced. If every team adopts it, the market re-prices and the surplus flows to the players. The window is plausibly **2–5 years**.

This is why the timing matters more than the precision of the dollar estimate. A team that waits for the academic literature to settle will find the mispricing gone. A team that pilots the chunk now can learn whether the signal survives its own scheme and roster.

## Failure modes

- **The coach vetoes the snap change.** The GM controls contracts, not the depth chart. Without a willing coach, the role route is zero.
- **The signal does not survive the team's scheme.** The pressure association is +0.354 in the competition sample; the team-fixed-effects estimate is +0.298 (p=0.089). A different front or coverage scheme may attenuate it further.
- **The cap saving is smaller than nominal.** Guarantees, dead money, and the cap floor can absorb the $6M. The valuation's low case uses $3M per decision for this reason.
- **The market already prices pressure.** PFF, NGS, and college production may capture the signal. If so, the selection route is small — as the model's $0.79M base already assumes.
- **The veteran's agent escalates.** A public role reduction can become a negotiation. The low-political-cost version keeps the veteran's base snaps and pay; the pass-rush sub-package is the only loss.
- **The sample is small.** The pressure evidence is 64 interior player-seasons; the strict tail is 13 player-seasons (12 players). The pilot should be judged on its own data, not on the competition point estimate alone.

## What the team is buying

Not a guarantee of $5.6M. A structured way to decide whether the allocation gap is real in its own building, and a defensible language for the decision: the cap pays performance; the depth chart pays status; the gap is the cost of the difference. If the pilot fails, the team has spent one analyst-cycle and learned something about its own allocation. If it works, the first-mover rent is the upside.
