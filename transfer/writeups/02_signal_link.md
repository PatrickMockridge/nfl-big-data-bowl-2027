# L2 — the unpriced-signal link

**Question.** Is the position-specific drill signal weakly related to draft
capital, while the incumbent stopwatch is priced?

## Method

- One row per player. Spearman correlations with `B_draft` (the within-position,
  within-class draft percentile) and with `prestige_nodraft` (the NGS composite
  without draft).
- Player-cluster bootstrap CIs (5,000 draws, seed 20261020).
- Pre-registered labels: `unpriced` if |ρ| < 0.20, `partly priced` if 0.20–0.30,
  `priced` if ≥ 0.30.
- `stopwatch_40` is the negative 40-yard time (higher = faster);
  `stopwatch_10` is the negative 10-yard split. `generic_movement` is the entry's
  pooled composite.

## Results

| Position | Signal | ρ with draft (95% CI) | ρ with prestige | Label |
|---|---|---|---:|---|
| WR | route drill | −0.020 (−0.192, 0.152) | 0.046 | **unpriced** |
| WR | 40-yard dash | **0.335 (0.157, 0.500)** | 0.232 | **priced** |
| WR | 10-yard split | 0.062 (−0.105, 0.221) | 0.013 | unpriced |
| WR | generic movement | −0.010 (−0.176, 0.160) | 0.003 | unpriced |
| TE | route drill | 0.048 (−0.276, 0.354) | 0.014 | unpriced |
| TE | 40-yard dash | 0.093 (−0.185, 0.378) | −0.125 | unpriced |
| OL | pass-set drill | 0.011 (−0.148, 0.162) | −0.041 | **unpriced** |
| OL | 40-yard dash | **0.266 (0.086, 0.435)** | 0.226 | **partly priced** |
| OL | 10-yard split | **0.206 (0.028, 0.381)** | 0.174 | **partly priced** |
| DL | pass-rush drill | −0.057 (−0.204, 0.097) | 0.027 | **unpriced** |
| DL | 40-yard dash | 0.133 (−0.039, 0.290) | 0.358 | unpriced |
| DL | 10-yard split | 0.090 (−0.087, 0.254) | 0.340 | unpriced |
| DB | back-pedal drill | 0.093 (−0.078, 0.257) | 0.008 | **unpriced** |
| DB | 40-yard dash | **0.398 (0.238, 0.540)** | 0.210 | **priced** |
| DB | 10-yard split | **0.216 (0.046, 0.382)** | 0.130 | **partly priced** |
| DB | generic movement | 0.275 (0.127, 0.420) | 0.239 | partly priced |

## Reading

This is the cleanest transfer of the entry's "lid": the signal that measures the
position's task is not what the draft prices. The pattern is strongest for
receivers and defensive backs, where the 40-yard dash is clearly priced
(ρ=0.335 and 0.398) and the task-matched drill signal is not (ρ=−0.020 and
0.093). Offensive line shows the same ordering, more weakly: the stopwatch is
partly priced, the pass-set signal is not. Defensive line is the case where
neither the drill signal nor the 40 is strongly priced, consistent with the
entry's burst–draft +0.034.

Tight end is unpriced on every candidate because the sample is small (n=33) and
the draft range is compressed; it is descriptive only.

The prestige correlations point the same way: the 40-yard dash carries the NGS
composite for WR (0.232), OL (0.226), DL (0.358), and DB (0.210); the
task-matched drill signals are near zero.

**Caveat.** Draft capital is a proxy for the market's belief, not a price. The
40-yard dash is not the only public signal, and the NGS composite may already
capture part of what the drill measures. The result is a descriptive
association, not a claim that teams ignore the drill.
