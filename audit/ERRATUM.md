# Erratum: corrections to the frozen judged entry

**Status:** the judged Big Data Bowl entry is frozen at `c652424`. This erratum
does not edit it. It records the statements in the frozen entry that the
adversarial audit downgrades, the correct wording, and the evidence. The
extensions and the root README carry the corrected wording.

The full red/blue audit is in [RED_BLUE.md](RED_BLUE.md); the machine-readable
verdicts are in [scorecard.csv](scorecard.csv).

| Location | Frozen text | Correction | Evidence |
|---|---|---|---|
| `writeup/submission.md:1` | "The Combine's pressure signal is real" | "The pressure association is in-sample and cross-player." | The 2025 temporal R² is −0.045; the team-FE estimate is +0.298 (−0.045, 0.640). The repo's own thesis says the association is not robust enough to call a validated tool. |
| `writeup/submission.md:11` | Sacks **+0.317** | Add: "The stopwatch is the stronger out-of-sample sack model, and the sack outcome is below the 0.50 reliability gate." | Interior sack split-half Spearman–Brown is 0.493; OOF R² is +0.120 for the stopwatch and +0.059 for the burst; the burst adds +0.007 R². |
| `writeup/submission.md:13` | "The stopwatch is blind to pressure" | "The stopwatch does not carry the pressure signal in this sample." | A joint p=0.998 is a failure to detect, not proof of blindness. The repo applies "absence of evidence" to the depth chart but not here. |
| `writeup/submission.md:17` | "The Combine signal is position-specific" | "The signal is concentrated in interior linemen; the burst-pressure interaction is p=0.137 and is not significant. The Combine-movement interaction is p=0.0004." | `docs/INTERIOR_BURST_PROTOCOL.md:182-204` records the failed go/no-go (EDGE pressure p=0.036; interaction p=0.137) and says the correct wording is "concentrated in interior." |
| `writeup/submission.md:17` | "interaction p=0.0004" | "The p=0.0004 belongs to the Combine-movement model; the burst-pressure interaction is p=0.137 and is not significant." | The two interaction tests are different models; the protocol records the failed burst-pressure interaction. |
| `writeup/submission.md:31` | "about nine parts role to one part performance" | "The group-mean decomposition is 31.7:1 in the full sample and 10.4:1 in the reliable sample." | `implications/writeups/00_thesis.md:33`; `implications/writeups/03_messaging.md:68` explicitly bans the nine-parts phrase as not traceable to one sample. |
| `writeup/submission.md:31` | Strict tail "13 player-seasons (12 players)" | 12 players is correct; the appendix said 11 and has been corrected. | `outputs/discovery/allocation_gap_tails.csv`: n=13, players=12; `docs/APPENDIX.md:60`. |
| `writeup/submission.md:39` | "The wedge is +0.28" | "The cross-construct difference is about 0.28; it is not a behavioral weight." | The "GM weight" is the measured cap coefficient (n=908); the coach shuffle is −0.10 (p=0.10); the two inputs use different performance measures. |
| `writeup/submission.md:39` | "raises ... role by 0.32 SD / 0.33 SD" | "The model scenario raises role by about 0.32–0.33 SD; it has no CI." | The agent model is deterministic and calibrated to the same regressions. |
| `writeup/submission.md:43-61` | Tier 3 recommendations and scorecard "usability" | Treat as hypotheses/perspectives, not operational findings. | No pilot, no tested cadence; the weekly check is exploratory; the gate decision says public notebooks already cover DL burst. |
| `writeup/submission.md:47` | "the gap is structural" | "The allocation pattern is descriptively consistent with a structural pattern." | The evidence is a descriptive decomposition in 233 player-seasons; no identification strategy supports "structural." |

**What did not change.** The measured core is unchanged: the interior pressure
association (+0.354, 0.143–0.565, n=64), the cap-performance association
(+0.328 raw, +0.264–0.392; +0.143 with role), and the null next-role
coefficient (−0.011, −0.119 to 0.097, n=233). The erratum corrects labels and
overstrong wording, not the measured associations.
