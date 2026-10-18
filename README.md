# The testing is informative; the decisions are not

Entry for the [NFL Big Data Bowl 2027](https://www.kaggle.com/competitions/nfl-big-data-bowl-2027). We test whether the 10 Hz Combine movement signal predicts regular-season performance, whether teams reward that performance with playing time, and whether the salary cap rewards it.

## Headline findings

- **The Combine signal is position-specific.** Movement predicts defensive-line performance (**+0.734**, 95% CI 0.461 to 1.007, n=175; standardized 0.42) but is marginal for receivers (+0.366, p=0.084) and undetectable for offensive linemen (+0.058) and tight ends (+0.093); interaction p=0.0004. The pooled +0.299 (standardized 0.185) is a defensive-line result. The defensive-line outcome is get-off, a movement-adjacent measure.
- **The cap pays for status.** The signed 2025 net rent is about **+$6.3M** for stars and **−$1.1M** for young high performers; the top cap quartile averages +$6.4M, the bottom two −$1.0M; players aged 28–29 average +$3.5M; early picks +$0.56M, late picks and UDFAs −$0.91M. The nested pay model's performance coefficient falls from +0.128 to +0.040 once role and draft enter; draft capital enters at +1.40.
- **Playing time is sticky and draft-driven.** Next-season playing time follows current playing time (+0.606) and draft position (+0.785), not performance (−0.011); leave-one-player-out R² = 0.503. The within-player test is the identification move: when the same player’s performance changes, his playing time does not follow (**−0.095**, p=0.11, n=235). The weekly check is +0.753 for current snaps and −0.006 for current performance; no tested review cadence follows.
- **The allocation gap is systematic.** Performance minus playing time is +0.59 for late picks and UDFAs and −0.92 for early picks in the full 233-row sample (+0.28 and −0.93 in the reliable 192-row sample). The strict top-performance/bottom-role quartile group has 13 player-seasons (12 players); its next-season role falls by 0.57 SD.
- **The predictability lens is exploratory.** Volatility is associated with fewer snaps than performance and draft predict (−1.49, p<0.001), but the association disappears with current role controlled (+0.13, p=0.31). It does not carry the argument.
- **The RJF/Yellow Square fallback is a wide null.** The preregistered test gives Yellow +0.176 (p=0.077, n=30), 2024–25 +0.144 (p=0.18, n=23), null Möbius/pond increments, and negative out-of-time R². The CIs rule out only large effects.

The entry is honest about what is not identified: no causal claims about coaches, teams, schemes, injuries, or contracts; DB performance is unidentifiable and excluded from pooled models; the Combine, role, salary, weekly, and cost-risk analyses are exploratory/post-hoc; the net rent is an accounting residual, not intent; the soccer table is illustrative and lives in `docs/SOCCER_DATA.md`.

## Deliverables

- `writeup/submission.md` — 1,979 words, 5 figures, 2 tables (the Football scorecard and selected models), within the competition limits.
- `notebooks/02_final_public.ipynb` — public Kaggle notebook with the Combine, role, cost-risk, and weekly checks.
- `notebooks/kernel-metadata.json` — Kaggle push metadata (public, competition data mounted).
- `writeup/figures/` — the five writeup figures: position-specific Combine, signed net rent, next-role forest, persistence, and allocation gap.
- `outputs/discovery/` — frozen role, Combine, weekly, cost-risk, and audit outputs (gitignored).
- `outputs/salary/` — salary panel, models, signed net rent, and soccer outputs (gitignored).
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
python -c "import sys; sys.path.insert(0,'src'); from discovery import cost_risk; cost_risk.main()"
python -c "import sys; sys.path.insert(0,'src'); from viz import cost_risk_figures; cost_risk_figures.main()"
python -c "import sys; sys.path.insert(0,'src'); from viz import figures; figures.main()"
python scripts/17_build_salary_panel.py
python scripts/18_test_salary.py
python scripts/19_salary_figures.py
python scripts/16_build_notebook.py
jupyter nbconvert --execute --to notebook --inplace notebooks/02_final_public.ipynb
```

## Data

Competition data is CC BY-NC 4.0; it is not committed and must not be redistributed. External data sources, coverage, and licenses are documented in `docs/EXTERNAL_DATA.md`. See `DATA_LICENSE.md`.

