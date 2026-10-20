# NFL Big Data Bowl 2027

This repo contains the judged 2027 Big Data Bowl entry and the post-competition analysis built on it.

**The judged entry:** a 10 Hz Combine burst predicts interior pressure and sacks; the 40-yard dash and 10-yard split do not. The depth chart does not reward measured performance — next-season role follows current role and draft. The cap does reward performance.

**The headline extension:** the contract market pays for role. A median team's actual 2026 free-agent signing class implies **$7.05M gross / $6.05M net per year**. The earlier top-down estimate of **$24.9M** was a 90.6th-percentile synthetic portfolio, not the median team.

![The old $24.9M estimate was a 90.6th-percentile team; the median team's actual 2026 class is $7.05M gross / $6.05M net.](implications/free_agency/writeups/figures/fa_headline.png)

## The headline number

| Measure | Value |
|---|---:|
| Median team, 2026 free-agent class | **$7.05M gross / $6.05M net** |
| Conservative (EDGE/S/CB) | $1.38M gross / $0.38M net |
| Low | $0.52M gross / $0.02M net |
| Old top-down estimate | $24.91M (90.6th percentile) |
| Portfolio total | $11.03M base / $5.37M conservative / −$0.68M low |

- 2026 APY role premium: **+0.179** (95% CI 0.022–0.336, n=306). 2025 cap ledger: **+0.185** (0.094–0.276, n=909).
- The cross-checks are weaker: 2025 active APY +0.105 (CI crosses zero); 2024 +0.029 (null); draft-matched 2026 +0.151 (0.016–0.286).
- Role is also priced in guarantees: guarantee share rises from 0.46 to 0.60 across snap-share quintiles.
- The premium is concentrated: the top 10% of contracts carry **51%** of it.
- Team changes do not earn a detectable free-agent premium: +0.499 (95% CI −0.164 to 1.162).

The dollar figures are inferences from the 2026 class, not forecasts or causal estimates.

## What the judged entry found

- Burst → pressure **+0.354** (0.143–0.565, n=64); sacks **+0.317** (0.083–0.550, n=63). The 40/10 joint test is p=0.998; out-of-sample R² is −0.113 for the stopwatch and +0.178 for the burst.
- Position-specific: DL **+0.734** (0.461–1.007); WR +0.366 (p=0.084); OL +0.058; TE +0.093; interaction p=0.0004.
- Cap pays performance: **+0.328** raw (0.264–0.392); **+0.143** with role (0.078–0.208).
- Next-season role: current role **+0.606**, draft **+0.785**, performance **−0.011** (−0.119 to 0.097).
- Allocation gap: **+0.59 SD** for late picks/UDFAs, **−0.92 SD** for early picks.
- The two-agent wedge (+0.28), the Yellow Square fallback (wide null), and the weekly check are in the entry.

Full text: [`writeup/submission.md`](writeup/submission.md). Public notebook: [`notebooks/02_final_public.ipynb`](notebooks/02_final_public.ipynb).

## Why the brief led here

The brief asked for a non-obvious, actionable linkage between 10 Hz Combine tracking and NFL performance, focused on one position group, and usable by coaches, scouts, and front offices. The work followed that order:

1. **Non-obvious:** compare the 10 Hz burst with the stopwatch. The burst carries the pressure signal; the stopwatch does not.
2. **One position:** DL. The cross-position check showed the measurement is position-specific, so the allocation side is what travels.
3. **Actionable:** a signal that does not change who plays is not useful. The depth chart does not reward performance; the cap does.
4. **Dollar:** the contract market is where the role premium has a price. The median team's 2026 class is $6.05M net; the old $24.9M was an upper-tail team.

The judging dimensions reported for the event are Innovation, Accuracy, Impact, and Clarity; the official weighted rubric is not public. The NFL [announcement](https://media.nfl.com/news-and-releases/consumer-products/national-football-league-announces-ninth-annual-big-data-bowl-po) states the brief's focus.

## Repo map

- [`writeup/submission.md`](writeup/submission.md) — judged entry (frozen at `c652424`).
- [`notebooks/02_final_public.ipynb`](notebooks/02_final_public.ipynb) — public notebook.
- [`implications/free_agency/`](implications/free_agency/README.md) — the headline deep dive: APY pricing, guarantees, surplus, bottom-up valuation.
- [`implications/markets/`](implications/markets/README.md) — portfolio across positions, free agency, coaching, special teams.
- [`transfer/`](transfer/README.md) — cross-position check of the allocation-gap pattern.
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
