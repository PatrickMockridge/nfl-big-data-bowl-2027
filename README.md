# From the Combine to the contract market: a ~$6M/year role premium

Entry for the [NFL Big Data Bowl 2027](https://www.kaggle.com/competitions/nfl-big-data-bowl-2027). The judged entry measured whether 10 Hz Combine movement predicts regular-season performance, whether teams reward that performance with playing time, and whether the salary cap rewards it. The headline finding from the full repository is the dollar consequence of that chain:

> **The free-agent contract market pays for role, not just performance. A median team's actual 2026 signing class implies $7.05M gross / $6.05M net per year. The old top-down estimate of $24.9M was a 90.6th-percentile synthetic portfolio, not the median team.**

The judged artifacts are frozen at `c652424`. The dollar finding is a post-competition extension built on the same data and the same competition criteria; it is not a judged claim.

![The old $24.9M estimate was a 90.6th-percentile team; the median team's actual 2026 class is $7.05M gross / $6.05M net.](implications/free_agency/writeups/figures/fa_headline.png)

## Headline finding: the contract-market role premium

| Measure | Value | What it means |
|---|---:|---|
| Median team, 2026 free-agent class | **$7.05M gross / $6.05M net** | bottom-up from actual APY, years, performance, role, age, and team |
| Conservative (EDGE/S/CB) | $1.38M gross / $0.38M net | only positions whose cap-ledger role-premium CI is above zero |
| Low | $0.52M gross / $0.02M net | 0.15 haircut, CI-supported positions |
| Old top-down one-team estimate | $24.91M net | synthetic portfolio; sits at the 90.6th percentile of the team distribution |
| Portfolio total | $11.03M base / $5.37M conservative / −$0.68M low | position selection + role plus the bottom-up free-agency market |

- **The APY role premium is +0.179 log points** (95% CI 0.022–0.336, n=306), close to the 2025 cap-ledger gap of **+0.185** (0.094–0.276, n=909). The 2025 active APY cross-check is +0.105 (CI crosses zero), the 2024 sample is +0.029 (null), the draft-matched 2026 gap is +0.151 (0.016–0.286), and the 2025 team-FE gap is +0.099 (CI crosses zero).
- **Role is priced in guarantees and length.** Guarantee share rises from 0.46 in the bottom prior-season snap-share quintile to 0.60 in the top. The top 10% of contracts carry **51%** of the positive role premium.
- **The free-agent premium for team changes is not detectable** after controls: +0.499 (95% CI −0.164 to 1.162). The role premium is the finding, not a "free agents are overpaid" story.

Every dollar figure is an **inference**, not a forecast or a causal estimate. The role premium is a measured association plus a haircut; the judged entry remains the frozen measurement/allocation analysis. Read the full investigation in [`implications/free_agency/`](implications/free_agency/README.md). The market portfolio is in [`implications/markets/`](implications/markets/README.md).

## How the Big Data Bowl criteria led to the $ value

The competition did not ask for a dollar value. It asked for a **non-obvious, actionable linkage** between 10 Hz Combine tracking and future NFL performance, focused on **one small aspect or position group**, and made **accessible to coaches, scouts, and front offices**. Following those criteria in order is what produced the dollar finding:

1. **Look beyond conventional scouting wisdom.** The convention is the stopwatch. The 10 Hz burst is the non-obvious measurement. Finding: the burst predicts interior pressure (+0.354 SD/SD, 0.143–0.565, n=64) and sacks (+0.317, 0.083–0.550, n=63); the 40-yard dash and 10-yard split do not carry the pressure signal (joint p=0.998).
2. **Focus on one position group.** The DL focus produced the clean measured result. The transfer extension then showed the measurement is position-specific: it is supported for DL, weak for WR, and unidentifiable for TE/OL/DB. That failure is what made the allocation and pricing side the portable finding.
3. **Make it actionable.** A metric that does not change who plays is not actionable. The allocation gap showed the depth chart does not detectably reward performance (next-season role: current role +0.606, draft +0.785, performance −0.011, CI −0.119 to 0.097), while the cap does (+0.328 raw; +0.143 with role). That is the bridge from measurement to money.
4. **Follow the actionable linkage to the market where it has a price.** If the cap pays performance and the depth chart pays role, the contract market is where the role premium becomes dollars. The bottom-up 2026 signing class gives the median team $7.05M gross / $6.05M net; the old $24.9M synthetic portfolio was an upper-tail team, not the median.

| Criterion / focus | How it shaped the work | Finding |
|---|---|---|
| Non-obvious linkage beyond the stopwatch | 10 Hz burst versus 40/10-yard times | Burst predicts pressure; the stopwatch does not. |
| Position-specific, one small aspect | DL focus; then cross-position transfer | Measurement is position-specific; allocation/pricing travels. |
| Actionable for coaches, scouts, front offices | Allocation gap → contract market | Role premium; median team $6.05M net/year. |
| **Innovation** (reported dimension) | Use the signal as a probe into labor allocation, not a metric leaderboard | The three pricing mechanisms and the free-agency deep dive. |
| **Accuracy** (reported dimension) | CIs, reliability gates, pre-registration, draft-matched robustness | +0.179 (0.022–0.336); fragile across cuts; no causal claim. |
| **Impact** (reported dimension) | A dollar value with a distribution and a conservative case | $6.05M net median; $24.9M is 90.6th percentile. |
| **Clarity** (reported dimension) | Tiered argument, evidence ledger, "what not to say" | Every claim is labeled measured, descriptive, or inferred. |

**Sources and caveat.** The NFL's [competition announcement](https://media.nfl.com/news-and-releases/consumer-products/national-football-league-announces-ninth-annual-big-data-bowl-po) states the focus (2023–25 Combine tracking plus in-game data for WR, TE, DB, OL, DL) and the multi-round evaluation by NFL analysts and football operations experts. The competition brief describes the task as finding "non-obvious, actionable linkages" that are "actionable and accessible to coaches, scouts, and front offices," and encourages focusing on one small aspect or position group ([challenge summary](https://www.givemechallenge.com/nfl-big-data-bowl-2027/55872/)). The official weighted rubric is not in the public sources reviewed; the Innovation/Accuracy/Impact/Clarity dimensions are the judging dimensions reported for the event ([ScholarComp](https://www.scholarcomp.com/competition/nfl-big-data-bowl)). The [Kaggle competition page](https://www.kaggle.com/competitions/nfl-big-data-bowl-2027) is the authoritative source.

## The judged entry (frozen at `c652424`)

The judged entry is the measurement and allocation core. Its full text is in [`writeup/submission.md`](writeup/submission.md); the public notebook is [`notebooks/02_final_public.ipynb`](notebooks/02_final_public.ipynb).

- **The pressure signal.** A 10 Hz Combine burst predicts interior pressure (+0.354, 0.143–0.565, n=64) and sacks (+0.317, 0.083–0.550, n=63); the 40/10 does not carry the pressure signal (joint p=0.998; out-of-sample R² −0.113 versus +0.178).
- **Position specificity.** Movement predicts DL performance (+0.734, 0.461–1.007, n=175) but is marginal for WR (+0.366, p=0.084) and undetectable for OL (+0.058) and TE (+0.093); interaction p=0.0004.
- **The cap pays performance.** On the 909-player 2025 ledger, performance enters at +0.328 (0.264–0.392) and +0.143 (0.078–0.208) with playing time. The 153-player draft-matched sensitivity fades to +0.040.
- **The depth chart is sticky.** Next-season role follows current role (+0.606) and draft (+0.785); performance is −0.011 (−0.119 to 0.097). The allocation gap runs from +0.59 SD for late picks/UDFAs to −0.92 SD for early picks.
- **The agent model.** A two-agent calibration puts the coach's performance weight at −0.13 and the GM's at +0.14; aligning them raises the top-performance group's role by 0.32 SD in the model. Model-reproduced, not identified.
- **The fallback is a wide null.** The preregistered Yellow Square test gives +0.176 (p=0.077, n=30), 2024–25 +0.144 (p=0.18, n=23), and negative out-of-time R². The CIs rule out only large effects.

The entry is explicit about identification: no causal claims about coaches, teams, schemes, injuries, or contracts; DB performance is unidentifiable and excluded; the role, salary, weekly, and cost-risk analyses are exploratory/post-hoc; the cap residual is an accounting residual; the cap and Combine halves use different performance measures; the soccer table is illustrative.

## Deliverables

- `writeup/submission.md` — the frozen judged entry (1,946 words, 6 figures, 2 tables).
- `notebooks/02_final_public.ipynb` — the public Kaggle notebook.
- `notebooks/kernel-metadata.json` — Kaggle push metadata.
- `writeup/figures/` — the six entry figures.
- `outputs/discovery/` — frozen role, Combine, weekly, cost-risk, and audit outputs (gitignored).
- `outputs/salary/` — salary panel, models, signed net rent, and soccer outputs (gitignored).
- `docs/PREREGISTRATION_v2.md` — the corrected regular-season preregistration.
- `docs/EXTERNAL_DATA.md` — external data sources, coverage, and limits.
- `docs/SOCCER_DATA.md` — the five-club soccer table sources and scope notes.
- `docs/gate_decision.md` — the DL audit-gate decision.
- `docs/APPENDIX.md` — the broader exploratory lens scan and what was cut after review.
- `implications/` — the original GitHub-only dollar-value, adoption, and messaging extension for one interior-DL chunk. Not part of the judged entry and not published on Kaggle.
- `transfer/` — Tier 1 descriptive pilots testing whether the allocation-gap pattern travels to other positions. The measurement does not generalize; the unpriced-signal and allocation links do. See `docs/TRANSFER_PROTOCOL.md`.
- `implications/markets/` — a GitHub-only, route-gated portfolio extension into EDGE, WR, DB, OL, TE, free agency/contract, coaching, and special teams. Not part of the judged entry. See `implications/markets/PROTOCOL.md`.
- `implications/free_agency/` — a GitHub-only, player-level investigation that supersedes the portfolio's top-down free-agency section: APY pricing, guarantees, surplus, and the bottom-up valuation of the actual 2026 signing class. Not part of the judged entry. See `implications/free_agency/PROTOCOL.md`.

## AI-assisted development

The code and analysis were developed with AI assistance. All results are reproducible from the committed scripts and public data; raw competition data is processed locally and is not redistributed. Verify the competition's AI-tool policy before submission.

## Reproduce

```bash
python scripts/01_download.py
python scripts/02_audit.py
python scripts/03_build_features.py
python scripts/04_build_squares.py
python scripts/05_test_hypotheses.py
python scripts/06_build_panel.py
python scripts/07_build_dynamic.py
python scripts/08_replicate_positions.py
python scripts/12_price_prediction.py
python -c "import sys; sys.path.insert(0,'src'); from features import combine_movement; combine_movement.main()"
python -c "import sys; sys.path.insert(0,'src'); from discovery import role_allocation, combine_linkage, weekly_role; role_allocation.main(); combine_linkage.main(); weekly_role.main()"
python -c "import sys; sys.path.insert(0,'src'); from discovery import interior_burst; interior_burst.main()"
python -c "import sys; sys.path.insert(0,'src'); from discovery import cost_risk; cost_risk.main()"
python -c "import sys; sys.path.insert(0,'src'); from framework import agentic_allocation; agentic_allocation.main()"
python -c "import sys; sys.path.insert(0,'src'); from viz import cost_risk_figures; cost_risk_figures.main()"
python -c "import sys; sys.path.insert(0,'src'); from viz import figures; figures.main()"
python scripts/17_build_salary_panel.py
python scripts/18_test_salary.py
python scripts/19_salary_figures.py
python scripts/16_build_notebook.py
jupyter nbconvert --execute --to notebook --inplace notebooks/02_final_public.ipynb
```

## Transfer extension

```bash
python scripts/20_transfer_drills.py
python scripts/21_transfer_signals.py
python scripts/22_transfer_breadth.py
python scripts/23_transfer_career.py
python scripts/24_transfer_figures.py
```

Outputs are written to `outputs/transfer/`; the writeups are in `transfer/`.

## Market portfolio extension

```bash
python scripts/25_market_sources.py
python scripts/26_position_pricing.py
python scripts/27_market_calibration.py
python scripts/28_market_valuations.py
python scripts/29_coaching_st.py
python scripts/30_market_figures.py
```

Outputs are written to `implications/markets/outputs/`; the writeups are in
`implications/markets/`. The market model reads the free-agency bottom-up
summary if it exists; run the free-agency pipeline below before script 28 (or
rerun 28 after 35) to use it.

## Free-agency investigation

```bash
python scripts/31_free_agency_events.py
python scripts/32_free_agency_market.py
python scripts/33_free_agency_pricing.py
python scripts/34_free_agency_surplus.py
python scripts/35_free_agency_valuation.py
python scripts/36_free_agency_history.py
python scripts/37_free_agency_figures.py
```

Outputs are written to `implications/free_agency/outputs/`; the writeups are in
`implications/free_agency/`.

## License

Code is MIT (`LICENSE`). Competition data is CC BY-NC 4.0 (`DATA_LICENSE.md`)
and is not redistributed. External data sources are documented in
`docs/EXTERNAL_DATA.md`.

## Data

Competition data is CC BY-NC 4.0; it is not committed and must not be redistributed. External data sources, coverage, and licenses are documented in `docs/EXTERNAL_DATA.md`. See `DATA_LICENSE.md`.
