# The message: three pricing mechanisms, one allocation gap

**Status:** extension to the 2027 NFL Big Data Bowl entry, not part of it. GitHub only; not published on Kaggle. Date-stamped 2026-10-19. This is a messaging guide: it defines what the work says, to whom, and in what order.

## The message house

**Roof:** *The stopwatch does not carry the pressure signal; the depth chart does not detectably reward measured performance; the cap is associated with measured performance.*

**Pillars:**

1. **Measurement.** The 10 Hz Combine burst predicts interior pressure at +0.354 SD/SD (0.143–0.565, n=64). Top versus bottom burst tercile pressure is 3.83% vs 2.47%; sacks are 0.97% vs 0.35%. The 40-yard dash and 10-yard split add nothing to pressure (joint p=0.998); out-of-sample pressure R² is −0.113 for the stopwatch and +0.178 for the burst. The signal is concentrated in interior linemen: DL +0.734, WR +0.366 (p=0.084), OL +0.058, TE +0.093. The Combine-movement interaction is p=0.0004; the burst-pressure interaction is p=0.137 and is not significant.
2. **Allocation.** Next-season role follows current role (+0.606) and draft capital (+0.785); the performance coefficient is −0.011 (95% CI −0.119 to 0.097, n=233). The allocation gap is +0.59 SD for late picks and UDFAs and −0.92 SD for early picks in the full 233-row sample. The gap is mostly role: the group-mean role spread is 1.462 SD versus a performance spread of 0.046 SD in the full sample, and 1.104 versus 0.106 in the reliable sample.
3. **Value.** For one team that adopts a low-political-cost chunk, the base case is $6.6M gross per year, $5.6M net after implementation cost, and $2.3M expected at 40% adoption. The range is $0.9M to $11.1M net. The value is a first-mover transition rent, not a permanent edge.

**Foundation:** the tiers. The measurement is measured; the allocation reading is descriptive; the agent model is model-reproduced; the dollar value is an inference. The message is strongest when the order is explicit.

## Three lengths

**One sentence.** The Combine's 10 Hz burst sees the pressure the stopwatch misses, the cap pays for performance, the depth chart does not detectably, and the gap is mostly role.

**Three sentences.** The 10 Hz burst predicts interior pressure where the stopwatch does not. The cap pays performance, but next-season playing time follows prior role and draft status, not performance. The allocation gap is mostly role, and the first team to reallocate the chunk captures a transition rent of roughly $5–6M a year, with a high case above $10M.

**One paragraph.** The entry measures three pricing mechanisms. The stopwatch prices sacks, not pressure; the 10 Hz burst prices pressure, but only for interior defensive linemen. The depth chart prices status and prior role; its performance coefficient is −0.011 with a confidence interval that includes zero. The cap prices performance at +0.328, or +0.143 with playing time. The gap between the cap and the depth chart is mostly role, not a late-pick performance advantage. Under normal assumptions about risk-averse coaches and noisy performance, that gap is a measurable allocation problem; the first team to act on it captures a transition rent, and the market re-prices once the principle is widely adopted.

## Audience framings

| Audience | Lead with | Do not lead with | The ask |
|---|---|---|---|
| Club analytics | The burst-versus-stopwatch result, concentrated in interior linemen, with the OOS contrast. | The dollar figure or the "emperor" framing. | Test it on your board; tell me where it fails. |
| Cap / contract staff | The role-controlled coefficient (+0.143) versus the raw (+0.328); the exp≥4 split (+0.443 / +0.217). | A promise of cap savings. | Does this match your valuation model? |
| Coaching / personnel | The weekly stickiness result (last week's role +0.753, performance −0.006); the low-political-cost chunk. | "The depth chart is a status market." | Which 10–15% of pass-rush snaps would you test? |
| League office | The rookie-scale and role-pipeline question; the structural allocation gap. | Club-specific blame. | Is this a policy question worth studying? |
| Analytics media | The three pricing mechanisms; the "stopwatch does not carry pressure" result. | The model's Tier 2 wedge as if it were identified. | A conversation after the competition deadline. |
| General / portfolio | The tiers and the measured-versus-inferred split. | A single big number without a range. | Read the thesis and the valuation. |

The order is deliberate. The measurement is the hardest evidence; the allocation reading is the interpretation; the dollar value is the consequence. A reader who rejects the interpretation can still keep the measurement.

## Proof points

| Claim | Number | Status |
|---|---|---|
| Burst → interior pressure | +0.354 (0.143–0.565, n=64) | Measured |
| Burst → interior sacks | +0.317 (0.083–0.550, n=63) | Measured |
| Stopwatch pressure increment | joint p=0.998; OOS −0.113 vs +0.178 | Measured |
| Position interaction | p=0.0004; DL +0.734; OL/TE null | Measured |
| Next-season role | current +0.606; draft +0.785; performance −0.011 (−0.119–0.097) | Measured |
| Cap performance | +0.328 (0.264–0.392); +0.143 (0.078–0.208) with role | Measured association |
| Allocation gap | late +0.59; early −0.92 full; +0.28/−0.93 reliable | Descriptive |
| Burst vs draft capital | +0.034 (−0.044–0.111) | Measured |
| Value, base | $6.6M gross / $5.6M net / $2.3M EV | Inference |
| Value, range | $0.9M–$11.1M net | Inference |

## Objection handling

| Objection | Response |
|---|---|
| "The sample is small." | Yes: 64 interior player-seasons, 13 player-seasons in the strict tail. It is a screen, not a validated tool; the team-fixed-effects estimate is +0.298 (p=0.089). |
| "Coaches know more than the model." | The claim is about information, not intelligence. Performance is noisy; prior role and draft status are cheap, stable signals. A rational coach can still weight them. |
| "The cap already pays performance." | Yes, +0.328 raw and +0.143 with role. The gap is in playing time, not the cap. |
| "This is sociology, not football." | The Tier 0 result is football-specific: a 10 Hz burst predicts interior pressure where the stopwatch does not. The structural reading is labelled as a reading. |
| "The dollar number is made up." | It is an inference with an explicit assumptions table, a low/high range, and a list of what would make it zero. The measured coefficients are separate. |
| "Teams already do this." | Then the market is priced and the surplus is smaller. That is a useful answer; it tells us the first-mover window is closing. |

## What not to say

- Do not say the work "proves" coaches are biased or that the depth chart is irrational. It measures an allocation pattern, not intent.
- Do not say "Pareto efficient." The chunk makes someone lose snaps. Say "Pareto-adjacent" and name the loser.
- Do not repeat "nine parts role to one part performance." The group-mean decomposition is 31.7:1 full and 10.4:1 reliable; the phrase is not traceable to one sample.
- Do not lead a club conversation with "the emperor has no clothes." It is a media/portfolio line, not a room line.
- Do not promise savings, a win total, or a contract outcome. The dollar figures are inferences.
- Do not present the agent model as identified. It is model-reproduced; the coach weight is marginal and the wedge is cross-construct.
- Do not share raw competition data. It is CC BY-NC 4.0 and is not redistributed.

## Closing lines

- For a football audience: *The stopwatch sees sacks; the burst sees pressure. The cap pays performance; the depth chart pays status. The gap is mostly role, and it is measurable.*
- For a portfolio audience: *Most entries ask whether tracking predicts performance. This one asks what the measurement says about how the league allocates labour.*
- For a media audience: *The emperor is not naked; the tailors are using a different measurement system.*
