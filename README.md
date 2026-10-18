# The Allocation Gap: The Combine Signal Is Real; the Depth Chart and the Cap Ignore It

Entry for the [NFL Big Data Bowl 2027](https://www.kaggle.com/competitions/nfl-big-data-bowl-2027), starting from the Romeo–Juliet Framework (RJF) / Green–Yellow Square, then auditing where the evaluation system is and is not self-regulating.

## Headline findings

- **The 10 Hz Combine signal is real, but the depth chart ignores it.** The movement composite predicts context-adjusted regular-season performance: **+0.299 SD per SD** (95% CI 0.153 to 0.446, p < 0.001, n = 543). The same composite does not predict role (**−0.019**, p = 0.83) or the role gap (+0.012, p = 0.70).
- **Role is sticky and draft-driven.** Next-season role follows current role (+0.606) and draft capital (+0.785), not performance (−0.011); leave-one-player-out R² = 0.503. The within-player test is the identification move: when the same player’s performance changes, role does not follow (**−0.095**, p = 0.11, n = 235).
- **The weekly check confirms it.** Next-week role follows this-week role (**+0.753**, 95% CI 0.717 to 0.788); this-week performance does not (**−0.006**, p = 0.59; 3,885 player-weeks, 249 players). Early performance does not predict late role (+0.008, p = 0.85). The operational conclusion is a 4–6 week rolling review, not a single-week trigger.
- **The cap repeats the pattern.** Star/highlight-reel cap share is unrelated to wins per $100M (**−0.70**, p = 0.89). Rookie snap share is negative (**−28.4**, p = 0.004); homegrown snap share is positive (**+9.2**, p = 0.001); QB spending flattens at about **14% of payroll** (p ≈ 0.07).
- **Rent proxy.** Less efficient teams carry more positive cap-allocation residual: Q4−Q1 total rent −$20.5M (bootstrap CI −$40.9M to −$2.0M); underperformer rent −$6.3M (−$14.5M to −$0.2M); youth surplus +$1.9M (+$0.1M to +$4.0M). Descriptive, not causal.
- **The RJF reversal is the method.** The Yellow Square and Möbius lenses were wide nulls; the residual is the allocation layer. The unique contribution is the **translation-to-allocation audit** — Combine → performance → role → cap — not another drill-to-game correlation.

The entry is honest about what is not identified: no causal claims about coaches, teams, schemes, injuries, or contracts; DB performance is unidentifiable (reliability 0.12) and excluded from pooled models; the role, salary, and weekly models are exploratory; the rent proxy is a cap-allocation residual; the soccer table is illustrative and lives in `docs/SOCCER_DATA.md`.

## Deliverables

- `writeup/submission.md` — 1,949 words, 5 figures, 3 tables (including the Football scorecard), within the competition limits.
- `notebooks/02_final_public.ipynb` — self-contained public Kaggle notebook (core + salary panel + weekly check); 23 cells, 0 errors.
- `notebooks/kernel-metadata.json` — Kaggle push metadata (public, competition data mounted).
- `writeup/figures/` — the five figures used in the writeup.
- `outputs/discovery/` — frozen role, Combine linkage, weekly check, and audit outputs (gitignored).
- `outputs/salary/` — salary panel, models, rent, and soccer outputs (gitignored).
- `docs/PREREGISTRATION_v2.md` — corrected regular-season preregistration (Yellow/pond primary; role, salary, and weekly analyses exploratory).
- `docs/EXTERNAL_DATA.md` — external data sources, coverage, and limits.
- `docs/SOCCER_DATA.md` — five-club soccer table sources and scope notes.
- `docs/gate_decision.md` — DL audit-gate decision.
- `docs/APPENDIX.md` — broader exploratory lens scan, salary and weekly appendices, and what was cut after review.

## AI-assisted development

The code and analysis were developed with AI assistance. All results are reproducible from the committed scripts and the public data; raw competition data is processed locally and is not redistributed. Verify the competition's AI-tool policy before submission.

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
python -c "import sys; sys.path.insert(0,'src'); from viz import figures; figures.main()"
python scripts/17_build_salary_panel.py
python scripts/18_test_salary.py
python scripts/19_salary_figures.py
python scripts/16_build_notebook.py
jupyter nbconvert --execute --to notebook --inplace notebooks/02_final_public.ipynb
```

## Data

Competition data is CC BY-NC 4.0; it is not committed and must not be redistributed. External data sources, coverage, and licenses are documented in `docs/EXTERNAL_DATA.md`. See `DATA_LICENSE.md`.

## Status

- [x] Data download and audit
- [x] Corrected regular-season panel (722 player-seasons / 401 players)
- [x] Position-specific performance residuals (DL/WR/TE/OL/DB)
- [x] Yellow, Möbius, pond, market, replication, and price-vs-prediction audits
- [x] 10 Hz Combine movement → performance linkage (positive)
- [x] Role persistence, within-player validation, role-measure sensitivities
- [x] Week-to-week role check (null performance coefficient; 4–6 week review)
- [x] Team-season salary panel (OTC, nflverse, archived OTC 2025 cap)
- [x] Cost-efficiency models, QB premium, rent proxy, soccer table
- [x] Figures and writeup (1,949 words, 5 figures, 3 tables)
- [x] Public notebook built and executed locally
- [x] Notebook salary and weekly cells rebuilt and executed
- [ ] Kaggle notebook published (requires explicit approval)
- [ ] Writeup submitted (requires explicit approval)
