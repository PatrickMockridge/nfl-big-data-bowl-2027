# Market portfolio — extending the implications package

**Status:** a GitHub-only extension of `implications/`. It is not part of the
judged Big Data Bowl entry and does not modify the artifacts frozen at
`c652424`. Date-stamped **2026-10-20**.

The existing implications package prices one interior-DL chunk. The `transfer/`
extension showed that the **structural pattern travels; the measurement does
not**. This folder asks which adjacent NFL markets can be priced under that
constraint, using a route-gated model: model only the routes the evidence
supports, and carry every number's evidence tier.

## Headline

| Market | Base portfolio net | Conservative | Low | Evidence |
|---|---:|---:|---:|---|
| Interior DL (anchor, selection + role) | $2.45M | $2.45M | $0.29M | measured + inference |
| EDGE | $1.24M | $1.24M | −$0.27M | measured association, borderline |
| WR | $0.40M | $0.40M | −$0.40M | measurement weak; role descriptive |
| OL | $0.89M | $0.89M | −$0.33M | allocation only |
| DB (CB/S) | $0.00M | $0.00M | $0.00M | legacy contract display; free agency is bottom-up |
| TE | $0.00M | $0.00M | $0.00M | unidentifiable / thin |
| Free agency / contract | $6.05M uncut / $1.82M capture | $0.38M uncut / −$0.45M capture | $0.88M uncut / −$0.29M capture | dedicated bottom-up report |
| **Portfolio total (uncut)** | **$11.03M** | **$5.37M** | **$0.18M** | inference |

**Dual totals.**

| Total | Base | Conservative | Low |
|---|---:|---:|---:|
| Uncut premium | **$11.03M** | **$5.37M** | **$0.18M** |
| Capturable at the scenario haircut | **$6.80M** | **$4.54M** | **−$0.99M** |

- The uncut total is **$11.03M base / $5.37M conservative / $0.18M low**. The
  capturable total is **$6.80M / $4.54M / −$0.99M**. The low stress case is the
  capturable **−$0.99M**, not the uncut $0.18M. The uncut EV is **$4.41M**;
  the capture EV is **$2.72M**.
- The conservative and low columns are different stress axes: conservative
  zeroes the pricing gaps whose CI includes zero in the contract/free-agency
  market; low uses the low assumptions throughout. Position-market nets have no
  pricing-gap leg, so their conservative equals base. Neither column is a
  confidence interval.
- The contract market is still the largest single market: **$6.05M uncut /
  $1.82M capture base; $0.38M uncut / −$0.45M capture conservative**, versus
  about **$5.0M** for all position selection + role. The dedicated
  [`free_agency/`](../free_agency/) report found the old **$24.9M** was a
  90.6th-percentile synthetic portfolio, not the median team's actual 2026
  signing class.
- The DL anchor's legacy one-team package still reconciles to **$6.6M gross / $5.6M net**;
  the portfolio counts its selection + role ($2.45M). Its contract route is
  part of the legacy top-down estimate and is **superseded** by the dedicated
  [`free_agency/`](../free_agency/) bottom-up report; it is not counted
  separately.

## Read in this order

1. [`writeups/00_thesis.md`](writeups/00_thesis.md) — the route-gated thesis and
   evidence tiers.
2. [`writeups/01_market_map.md`](writeups/01_market_map.md) — which market can
   defend which route, and why.
3. [`writeups/02_position_markets.md`](writeups/02_position_markets.md) — EDGE,
   WR, DB, OL, TE.
4. [`writeups/03_free_agency.md`](writeups/03_free_agency.md) — the
   cross-position contract market.
5. [`writeups/04_coaching_special_teams.md`](writeups/04_coaching_special_teams.md)
   — the descriptive markets.
6. [`writeups/05_portfolio.md`](writeups/05_portfolio.md) — totals, overlap, and
   sequencing.
7. [`writeups/06_messaging.md`](writeups/06_messaging.md) — message house,
   audiences, and what not to say.

## Reproduce

```bash
python scripts/25_market_sources.py
python scripts/26_position_pricing.py
python scripts/27_market_calibration.py
python scripts/28_market_valuations.py
python scripts/29_coaching_st.py
python scripts/30_market_figures.py
```

The free-agency row reads
`implications/free_agency/outputs/valuation_summary.csv` if it exists. Run the
[`free_agency/`](../free_agency/README.md) pipeline before script 28 (or rerun
28 after 35) to use the bottom-up estimate; otherwise the market model falls
back to the legacy top-down components with a warning.

Outputs are written to `implications/markets/outputs/` (gitignored). The frozen
protocol is [`PROTOCOL.md`](PROTOCOL.md); the configuration is the `transfer:`
and market constants in the code.

## Data and limits

- Competition data, nflverse, OTC positional spending, the 2025 cap ledger, the
  Kaggle/historical contract files, nflverse trades and draft picks, and public
  coaching tenure derived from nflverse games.
- Raw downloads stay in `data/external/market/` (gitignored); only derived
  aggregates are written to `outputs/`.
- Every dollar figure is an inference. The role and pricing patterns are
  observational; the pricing correction is a measured association plus a
  haircut assumption. No causal claim.
- QB, RB, TE pricing cells are thin and exploratory; OL has no individual
  performance in the cap ledger; special teams fail the reliability gate.
- The judged entry, the public notebook, and the existing `implications/`
  package are unchanged.
