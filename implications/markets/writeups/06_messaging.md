# Messaging: one house, different rooms

## Message house

**Roof:** the allocation pattern travels; the measurement does not. Price the
role, not the stopwatch.

**Pillars:**

1. **Measurement is position-specific.** The DL pass-rush signal reproduces;
   EDGE is borderline; WR is weak; TE/OL/DB fail reliability or variance gates.
2. **The unpriced-signal and allocation patterns travel.** Task-matched drill
   signals are unpriced by draft; performance→role is null; the gap follows the
   draft in WR, OL, and DL.
3. **The dollars are a contract-pricing inference.** The contract market is
   still the largest single lever, but the median team's actual 2026 class is
   $6.05M uncut / $1.82M capture net; the old $24.9M was a 90th-percentile
   synthetic portfolio. The conservative view is $0.38M uncut / −$0.45M
   capture.

**Foundation:** the tiers. Measurement is measured; allocation is descriptive;
the contract gap is a measured association; the dollars are inference; the team
fits are a date-stamped reading. The message is strongest when the order is
explicit.

## Three lengths

**One sentence.** The league's allocation pattern travels across markets, but
the Combine measurement does not; the defensible dollar case is a role-controlled
contract correction, not a new universal talent signal.

**Three sentences.** DL is the measured case: the pass-rush signal predicts
pressure, and the stopwatch does not carry it. EDGE is borderline, WR is weak,
and TE/OL/DB are unidentifiable for measurement reasons. The portable pattern is
that the cap pays performance while the depth chart pays status; price the role,
and use the drill signal only where it has passed its own reliability gate.

**One paragraph.** The entry measured a position-specific pressure signal and
read it as an allocation gap. The transfer extension shows the structure travels
further than the signal: task-matched drill signals are unpriced, performance
is unrewarded in next-season role, and the gap follows the draft in WR, OL, and
DL. The market portfolio prices that structure. The largest lever is the
free-agency contract correction — reprice the next renewal wave on
role-controlled performance. Position selection is small and mostly DL/EDGE.
The uncut portfolio is about $11M base / $5.4M conservative / $0.2M low; the
capture total is about $6.8M / $4.5M / −$1.0M. The free-agency component is
$6.05M uncut / $1.82M capture base and $0.38M uncut / −$0.45M capture
conservative. Every figure is an inference, and the contract gap is an
association, not a causal effect.

## Audience framings

| Audience | Lead with | Do not lead with | The ask |
|---|---|---|---|
| GM / roster | The allocation gap and the contract correction; DL is the measured case. | A universal "Combine signal" or a win-total promise. | Reprice the next renewal wave; pilot one EDGE sub-package. |
| Cap / contract | Role-controlled vs raw performance by position; EDGE/S/CB gaps have CIs excluding zero. | The $11M uncut base without the $5.4M conservative and $0.2M low, or the $6.8M/$4.5M/−$1.0M capture totals; the free-agency component is $6.05M uncut / $1.82M capture. | Model the renewal portfolio with the role-controlled coefficient. |
| Coach / personnel | Role stickiness and the performance null; the chunk protects the coach. | "The depth chart is a status market." | Review the largest role gaps; keep the starting lineup intact. |
| Analytics | The transfer matrix and the reliability gates. | The DL signal as a WR/DB result. | Re-run the reliability and out-of-sample checks in the team's own data. |
| League office | The rookie-scale/role-pipeline question; the measurement is position-specific. | Club-specific blame or a causal claim. | Ask whether the role pipeline uses the signals the testing shows. |
| Media / portfolio | The three pricing mechanisms and the route-gated market map. | A single big number without the range and tiers. | Keep the measured/descriptive/inferred separation explicit. |

## Proof points

| Number | Status | Source |
|---|---|---|
| DL burst → pressure +0.354 (0.143, 0.565) | measured | `outputs/discovery/interior_burst_models.csv` |
| DL benchmark +0.368 (0.149, 0.587); +0.050 incremental R² | measured | `outputs/transfer/drill_translation.csv` |
| EDGE pass-rush +0.166 (0.029, 0.303); Holm p=0.054 | measured association, borderline | `outputs/transfer/drill_translation.csv` |
| WR route +0.053 (−0.174, 0.280) | weak | `outputs/transfer/drill_translation.csv` |
| Task-matched signals unpriced, \|ρ\| ≤ 0.10 | descriptive | `outputs/transfer/signal_pricing.csv` |
| Performance→role null in DL/WR/OL/TE | descriptive | `outputs/discovery/role_allocation_positions.csv` |
| EDGE/S/CB pricing gaps 0.326/0.331/0.224 | measured association | `implications/markets/outputs/position_pricing.csv` |
| Free-agency APY role premium +0.179 (0.022, 0.336) | measured association | `implications/free_agency/outputs/role_premium.csv` |
| Free-agency contract $6.05M uncut / $1.82M capture base; $0.38M uncut / −$0.45M capture conservative | inference | `implications/free_agency/outputs/valuation_summary.csv` |
| Portfolio uncut $11.03M / $5.37M / $0.18M; capture $6.80M / $4.54M / −$0.99M | inference | `implications/markets/outputs/portfolio.csv` |
| Coaching retention 0.52 → 0.97 by wins quartile | descriptive | `implications/markets/outputs/coaching_descriptive.csv` |
| ST reliability K 0.11 / P 0.46 / RET 0.78 | descriptive | `implications/markets/outputs/st_reliability.csv` |

## Objection handling

| Objection | Response |
|---|---|
| "The Combine signal is real; why not use it everywhere?" | It is real for DL, borderline for EDGE, weak for WR, and unidentifiable for TE/OL/DB. Use it only where it passes the reliability gate. |
| "The portfolio is dominated by one number." | The contract correction is still the largest single market ($6.05M uncut / $1.82M capture), but it is no longer dominant; the old $24.9M was an upper-tail team. The conservative and low capture cases are reported alongside the base. |
| "The pricing gap is not causal." | Correct. It is a measured association plus a haircut assumption. The market model is an inference. |
| "You are double-counting role and contract." | No. Position markets count selection + role; the free-agency row is the dedicated bottom-up report; the position contract rows are legacy top-down display only. The low-case convention covers shared drivers. |
| "Coaching and special teams are missing." | They are descriptive: retention tracks wins; ST fails the reliability gate. They carry no dollar claim. |
| "Why no OL contract route?" | The cap ledger has no individual OL performance measure. The role route is modeled; the pricing route is not. |

## What not to say

1. Not "the DL burst predicts WR/DB/OL performance." The measurement is
   position-specific.
2. Not "the portfolio proves $11M." It is an inference with an uncut $5.4M
   conservative and $0.2M low; the capture total is $6.8M/$4.5M/−$1.0M; the
   free-agency component is $6.05M uncut / $1.82M capture.
3. Not "the pricing correction causes lower pay." It is an association plus an
   assumption.
4. Not "the depth chart is irrational." The pattern is about information and
   risk weights, not intent.
5. Not "Pareto efficient." The role and contract chunks have losers; say
   "Pareto-adjacent" and name them.
6. Not "the career ladder is a pricing model." It is a reward-legibility
   description.
7. Not "sum the position contract rows." They are display-only and counted in
   the free-agency total.
