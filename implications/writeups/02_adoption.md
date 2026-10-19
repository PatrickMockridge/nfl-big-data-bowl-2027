# A low-political-cost chunk, six team fits, and the first-mover clock

**Status:** extension to the 2027 NFL Big Data Bowl entry, not part of it. GitHub only; not published on Kaggle. Staffing is date-stamped **2026-10-19** and must be re-verified before quoting the table. Team fit here is structural — roster state, regime tenure, cap position — not a claim about any executive's personal analytics views.

## The chunk

The finding does not require a club to abandon its draft board or its coaching philosophy. The low-political-cost chunk is three actions:

1. **Add the burst signal to the interior-DL draft board** as one input alongside tape, college production, and draft slot. It is a screening input, not a rank.
2. **In obvious pass-rush sub-packages, reallocate 10–15% of snaps** from a low-burst, high-cap veteran to a high-burst, low-cost interior lineman. The veteran loses pass-rush snaps, not starting status or pay.
3. **Price the next interior-DL contract on role-controlled performance** (+0.143) rather than the raw performance coefficient (+0.328).

**Who loses:** the low-burst veteran loses snaps; the coach loses some discretionary authority; the incumbent scout loses the comfort of the stopwatch. That is why this is **Pareto-adjacent**, not strictly Pareto efficient. A strict Pareto improvement would require no one to lose anything, and a snap reallocation cannot meet that test. The claim is that the losses are small, concentrated, and politically manageable relative to the gain.

## Team archetypes

The natural reader is a GM or analytics director with roster authority, a rebuild or a cap reset, and a coach he can plausibly align or challenge. Current staffing (Wikipedia's current NFL general manager and head coach lists, retrieved 2026-10-19):

| Team | GM | Head coach | Why the structure fits | Caveat |
|---|---|---|---|---|
| **Titans** | Mike Borgonzi | Robert Saleh | New regime, defensive coach, rebuild, high draft capital; interior pressure is a live need. | GM and coach may be aligned, which lowers the "challenge the coach" tension but raises the ability to act together. |
| **Browns** | Andrew Berry | Todd Monken | Analytics-native GM; cap reset; the cap-versus-role frame is directly salient. | Ownership and the Watson contract constrain a clean reallocation. |
| **Jaguars** | James Gladstone | Liam Coen | Young, analytics-forward regime with a draft-and-develop mandate. | Not a full rebuild; pressure to win now. |
| **Falcons** | Ian Cunningham | Kevin Stefanski | New regime; roster and cap reset; authority to re-price roles. | Both are new together, so the two-agent wedge is a design choice, not a live conflict. |
| **Dolphins** | Jon-Eric Sullivan | Jeff Hafley | New regime, defensive coach, clean slate. | The teardown may take precedence over fine-grained role allocation. |
| **Cardinals** | Monti Ossenfort | Mike LaFleur | Patient, draft-heavy GM; new coach; young roster. | The fit is structural, not a claim about personal analytics views. |

The obvious "smart" teams — Ravens, Eagles, Steelers, 49ers, Rams — are poor fits for this specific piece: they are stable or contending, the coach has authority, and there is no allocation crisis to solve. This is a **transition-regime document**, not a contender document.

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
