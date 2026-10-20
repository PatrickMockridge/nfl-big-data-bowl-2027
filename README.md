# The NFL free-agent market carries about $7M a year of uncut role premium

Role is prior-season snap share in this model. A median team's 2026 free-agent class carries about **$7.0M a year** of uncut modeled role premium — pay that tracks role beyond measured performance. At the base **0.40** capture assumption, the modeled annual capture is about **$2.8M gross / $1.8M net** after a **$1M** implementation cost.

*Role premium* means the raw minus role-controlled performance coefficient. It is a conditional association, not an unearned-pay verdict.

The judged entry established the chain: a 10 Hz Combine burst predicts interior pressure while the stopwatch does not; the depth chart does not detectably reward measured performance; the cap is associated with measured performance.

![Median team: $7.0M a year of uncut role premium from the actual 2026 free-agent class; 32 teams sorted.](implications/free_agency/writeups/figures/fa_headline.png)

## The finding

| Measure | Value | Details |
|---|---:|---|
| Median team, uncut annual role premium | **$7.05M** | [valuation](implications/free_agency/writeups/04_valuation.md) |
| Capture at 0.40, gross | **$2.82M** | [valuation](implications/free_agency/writeups/04_valuation.md) |
| Capture at 0.40, net after $1M | **$1.82M** | [valuation](implications/free_agency/writeups/04_valuation.md) |
| Team distribution (P10 / P50 / P90) | $1.81M / $7.05M / $22.51M | uncut premium, 32 teams |
| Conservative: only EDGE/S/CB | $1.38M uncut / −$0.45M net at 0.40 capture | [valuation](implications/free_agency/writeups/04_valuation.md) |
| Low: only EDGE/S/CB | $1.38M uncut / −$0.29M net at 0.15 capture | [valuation](implications/free_agency/writeups/04_valuation.md) |

- The regression estimate of the role premium is **+0.179 log points** (95% CI 0.022–0.336, n=306). The 2025 cap ledger gives **+0.185** (0.094–0.276, n=909). Adding contract length and guarantee share as commitment controls reduces the gap to **+0.049** (−0.093 to 0.191, n=253); the premium is not robust to contract-structure controls. [Pricing details](implications/free_agency/writeups/02_pricing.md), [model code](implications/free_agency/code/pricing.py).
- The cross-checks are weaker: 2025 active APY +0.105 (CI crosses zero); 2024 +0.029 (null); draft-matched 2026 +0.151 (0.016–0.286). [Pricing details](implications/free_agency/writeups/02_pricing.md).
- Role is also priced in guarantees: guarantee share rises from 0.46 to 0.60 across snap-share quintiles. [Guarantee model](implications/free_agency/writeups/02_pricing.md).
- The premium is concentrated: the top 10% of contracts carry **51%** of it. [Surplus details](implications/free_agency/writeups/03_surplus.md), [code](implications/free_agency/code/surplus.py).
- Team changes do not earn a detectable free-agent premium: +0.499 (95% CI −0.164 to 1.162). [Pricing details](implications/free_agency/writeups/02_pricing.md).

The dollar figures are inferences from the 2026 class, not forecasts or causal estimates. The full investigation is in [`implications/free_agency/`](implications/free_agency/README.md).

**Adversarial audit:** [red-team/blue-team review of every implied finding](audit/README.md).

**Discussion:** [Kaggle thread on whether to include this finding in the submission](https://www.kaggle.com/competitions/nfl-big-data-bowl-2027/discussion/751037).

## What the judged entry found

- Burst → pressure **+0.354** (0.143–0.565, n=64); sacks **+0.317** (0.083–0.550, n=63). The 40/10 joint test is p=0.998; out-of-sample R² is −0.113 for the stopwatch and +0.178 for the burst. The stopwatch is the stronger out-of-sample sack model, and the sack outcome is below the 0.50 reliability gate.
- Concentrated in interior linemen: DL **+0.734** (0.461–1.007); WR +0.366 (p=0.084); OL +0.058; TE +0.093. The Combine-movement interaction is p=0.0004; the burst-pressure interaction is p=0.137 and is not significant.
- Cap pays performance: **+0.328** raw (0.264–0.392); **+0.143** with role (0.078–0.208).
- Next-season role: current role **+0.606**, draft **+0.785**, performance **−0.011** (−0.119 to 0.097).
- Allocation gap: **+0.59 SD** for late picks/UDFAs, **−0.92 SD** for early picks.
- The two-agent cross-construct difference (+0.28; not a behavioral weight), the Yellow Square fallback (wide null), and the weekly check are in the entry.

**Genealogy.** The burst and allocation analyses were added after the preregistered tests and are labeled exploratory. The preregistered Yellow/Möbius framework returned a wide null. The novelty is the allocation probe, not the burst metric alone. See the [audit](audit/README.md).

**Data ethics.** The Combine tracking data are league-provided; this work does not collect new biometric data and does not recommend expanding collection. It is a validity check on measurements the league already takes.

Full text: [`writeup/submission.md`](writeup/submission.md) (Tier 0/1/2), [`docs/APPENDIX.md`](docs/APPENDIX.md) (exploratory cuts). Public notebook: [`notebooks/02_final_public.ipynb`](notebooks/02_final_public.ipynb). Code: [`interior_burst.py`](src/discovery/interior_burst.py), [`combine_movement.py`](src/features/combine_movement.py), [`role_allocation.py`](src/discovery/role_allocation.py), [`cost_risk.py`](src/discovery/cost_risk.py), [`agentic_allocation.py`](src/framework/agentic_allocation.py).

## Why the brief led here

The brief asked for a non-obvious, actionable linkage between 10 Hz Combine tracking and NFL performance, focused on one position group, and usable by coaches, scouts, and front offices. The work followed that order:

1. **Non-obvious:** compare the 10 Hz burst with the stopwatch. The burst carries the pressure signal; the stopwatch does not. The entry's distinct move is the allocation probe that follows.
2. **One position:** DL. The cross-position check showed the measurement is concentrated in interior linemen, so the allocation side is what travels.
3. **Plausibly actionable (untested):** a signal that does not change who plays is not useful. The depth chart does not detectably reward measured performance; the cap is associated with measured performance.
4. **Dollar:** the contract market is where the role premium has a price. The median team's 2026 class carries $7.05M uncut a year; at the 0.40 capture assumption the annual capture is $2.82M gross / $1.82M net after a $1M implementation cost.

The judging dimensions reported for the event are Innovation, Accuracy, Impact, and Clarity; the official weighted rubric is not public. The NFL [announcement](https://media.nfl.com/news-and-releases/consumer-products/national-football-league-announces-ninth-annual-big-data-bowl-po) states the brief's focus.

## Repo map

- [`writeup/submission.md`](writeup/submission.md) — judged entry (frozen at `c652424`).
- [`notebooks/02_final_public.ipynb`](notebooks/02_final_public.ipynb) — public notebook.
- [`implications/free_agency/`](implications/free_agency/README.md) — the headline deep dive: APY pricing, guarantees, surplus, bottom-up valuation.
- [`implications/markets/`](implications/markets/README.md) — portfolio across positions, free agency, coaching, special teams.
- [`transfer/`](transfer/README.md) — cross-position check of the allocation-gap pattern.
- [`audit/`](audit/README.md) — red-team/blue-team audit of every implied finding.
- [`docs/`](docs/) — protocols, data sources, appendix.

## Reproduce

Free-agency deep dive:

```bash
python scripts/31_free_agency_events.py
python scripts/32_free_agency_market.py
python scripts/33_free_agency_pricing.py
python scripts/34_free_agency_surplus.py
python scripts/35_free_agency_valuation.py
python scripts/36_free_agency_history.py
python scripts/37_free_agency_figures.py
```

Market portfolio:

```bash
python scripts/25_market_sources.py
python scripts/26_position_pricing.py
python scripts/27_market_calibration.py
python scripts/28_market_valuations.py
python scripts/29_coaching_st.py
python scripts/30_market_figures.py
```

Transfer check:

```bash
python scripts/20_transfer_drills.py
python scripts/21_transfer_signals.py
python scripts/22_transfer_breadth.py
python scripts/23_transfer_career.py
python scripts/24_transfer_figures.py
```

<details>
<summary>Judged entry pipeline</summary>

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

</details>

## License and data

Code is MIT (`LICENSE`). Competition data is CC BY-NC 4.0 (`DATA_LICENSE.md`), is not committed, and is not redistributed. External data sources and licenses are in [`docs/EXTERNAL_DATA.md`](docs/EXTERNAL_DATA.md).
