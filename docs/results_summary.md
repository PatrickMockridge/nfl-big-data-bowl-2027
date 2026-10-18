# Results summary — Yellow Square DL analysis

> **Historical artifact.** This is the DL-only exploratory scan from before the
> final regular-season correction and adversarial audit. It is superseded by
> `writeup/submission.md` and `docs/APPENDIX.md`. The “rent” and
> “predictability” labels below were cut after review; do not cite them.

Date: 2026-10-18. Primary outcome: context-adjusted get-off (no team identity).

## Square counts
square
Green     86
Yellow    16
Blue      10
Red        6

## Headline results
- **H1 Yellow risk** — Yellow - RedBlue: C: 0.176 (95% CI -0.020 to 0.357), p=0.077, n=30
- **H1 Yellow risk** — Yellow - RedBlue: bust: 0.179 (95% CI -0.080 to 0.438), p=0.209, n=30
- **H1 Yellow risk** — Yellow - RedBlue: shrunk_mean: -0.037 (95% CI -0.084 to 0.008), p=0.084, n=30
- **H1 Yellow risk** — Yellow - RedBlue: raw_speed_mean: -0.072 (95% CI -0.136 to -0.010), p=0.036, n=30
- **H1 sensitivity** — Yellow A[0.2,0.8] - RedBlue: C: 0.104 (95% CI -0.078 to 0.283), p=0.246, n=37
- **H1 sensitivity** — Yellow A[0.25,0.75] - RedBlue: C: 0.123 (95% CI -0.064 to 0.304), p=0.201, n=34
- **H1 sensitivity** — Yellow A[0.35,0.65] - RedBlue: C: 0.160 (95% CI -0.047 to 0.362), p=0.152, n=27
- **H1 sensitivity** — Full context (team included): C: 0.177 (95% CI 0.008 to 0.345), p=0.109, n=30
- **H2 Möbius** — all DL: mobius_continuous vs C: 0.015 (95% CI -0.196 to 0.229), p=0.887, n=94
- **H2 Möbius** — all DL: flip_composite vs C: -0.018 (95% CI -0.221 to 0.199), p=0.863, n=94
- **H2 Möbius** — all DL: dwell_composite vs C: -0.092 (95% CI -0.286 to 0.104), p=0.379, n=94
- **H2 Möbius** — Yellow: mobius_continuous vs C: 0.079 (95% CI -0.539 to 0.600), p=0.770, n=16
- **H2 Möbius** — Yellow: flip_composite vs C: 0.150 (95% CI -0.437 to 0.640), p=0.579, n=16
- **H2 Möbius** — Yellow: dwell_composite vs C: 0.109 (95% CI -0.401 to 0.637), p=0.688, n=16
- **H2 Möbius** — Yellow Möbius flag count: 1.000, n=16
- **H2 power** — min detectable |rho| at 80% power: 0.651, n=16
- **H3 Green bargains** — Green - highB bargain rate: -0.066 (95% CI -0.264 to 0.128), p=0.502, n=94
- **H3 Green bargains** — Green highA vs lowA bargain rate: -0.219 (95% CI -0.438 to -0.031), p=0.041, n=64
- **H4 out-of-time** — official: OOF R2 for verified get-off: -0.338, n=94
- **H4 out-of-time** — tracking: OOF R2 for verified get-off: -0.395, n=94
- **H4 out-of-time** — framework: OOF R2 for verified get-off: -0.424, n=94
- **H4 out-of-time** — incremental R2: framework - tracking: -0.028 (95% CI -0.161 to 0.100), n=94
- **H4 out-of-time** — tracking: OOF AUC for bust: 0.607, n=94
- **H4 out-of-time** — framework: OOF AUC for bust: 0.597, n=94
- **H7 fragility** — phi AUC for bust: 0.478, n=94
- **H7 fragility** — observed - main-effect bust rate (3+ flags): 0.329, n=9
- **H8 team compounding** — mean compounding excess (teams >=2): -0.101, n=62
- **H8 team compounding** — within-team eta2 of bust residuals: 0.431 (95% CI 0.213 to 0.478), p=0.086, n=94
- **H9 resilience** — resilient - captured: flip_composite: 0.080 (95% CI -0.429 to 0.587), n=48
- **H9 resilience** — resilient - captured: dwell_composite: 0.171 (95% CI -0.228 to 0.562), n=48
- **H9 resilience** — resilient - captured: first_step: -0.125 (95% CI -0.313 to 0.041), n=48
- **H9 resilience** — resilient - captured: agility: 0.139 (95% CI -0.048 to 0.330), n=46
- **H9 resilience** — resilient - captured: path_efficiency: -0.006 (95% CI -0.036 to 0.024), n=48
- **H9 resilience** — resilient - captured: n_attempts: 1.292 (95% CI -0.125 to 2.708), n=48
- **H9 resilience** — resilient - captured: n_plays: -38.917 (95% CI -123.252 to 52.545), n=48
- **H9 resilience** — resilient - captured: raw_speed_mean: 0.187 (95% CI 0.136 to 0.238), n=48

## Caveats
- Player-level N is small (115 with outcomes; 16 Yellow). CIs are wide.
- The Yellow effect is sensitive to context adjustment; the full-context sensitivity is reported.
- The Möbius signature is not supported in this sample; the binary flag is too rare for a contrast.
- Team-level compounding is exploratory; the permutation test is the defensible check.