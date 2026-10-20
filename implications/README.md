# Implications of results

**Status:** a separate extension to the 2027 NFL Big Data Bowl entry. It is not part of the judged entry, not attached to the competition, and not published on Kaggle. The judged artifacts are frozen at `c652424`.

This folder extends the entry's logic beyond the competition: the three pricing mechanisms (stopwatch, depth chart, cap), a transparent dollar value for one team, a low-political-cost adoption chunk, team fit, and messaging. Every dollar figure is an **inference**, not a measurement; the measured coefficients are cited with their source files.

The headline: a scenario, not a value. The one-change guide is the **low case ($0.9M net)**; the arithmetic base is **$6.6M gross per year**, **$5.6M net** after implementation cost, and **$2.3M expected** at 40% adoption. The route decomposition is selection **$0.79M** + role **$2.10M** + contract **$3.75M**; the routes are not causally additive. The range is **$0.9M to $11.1M net**. The value is a first-mover transition rent, not a permanent edge.

## Map

```
implications/
├── code/
│   ├── value_model.py       # assumptions, three routes, sensitivity, Monte Carlo
│   ├── figures.py           # value bridge + tornado
│   ├── build_notebook.py    # builds the standalone notebook with embedded tables
│   └── implications.ipynb   # executed, self-contained notebook
├── writeups/
│   ├── 00_thesis.md         # three pricing mechanisms; measured vs inferred
│   ├── 01_valuation.md      # the dollar model and sensitivity
│   ├── 02_adoption.md       # the chunk, team fits, first-mover clock
│   ├── 03_messaging.md      # message house, audience framings, what not to say
│   └── figures/             # value_bridge.png, sensitivity.png
└── outputs/                 # generated CSVs; gitignored
```

## Read in this order

1. [`writeups/00_thesis.md`](writeups/00_thesis.md) — the structural claim and what is measured.
2. [`writeups/01_valuation.md`](writeups/01_valuation.md) — the dollar model, assumptions, and what would make it zero.
3. [`writeups/02_adoption.md`](writeups/02_adoption.md) — the low-political-cost chunk and the team archetypes.
4. [`writeups/03_messaging.md`](writeups/03_messaging.md) — the message, audience framings, and what not to say.

The notebook, [`code/implications.ipynb`](code/implications.ipynb), is the executable version. It embeds the model tables and runs without the gitignored `outputs/` directory.

## Market portfolio extension

[`markets/`](markets/) extends this package into NFL-adjacent markets (EDGE, WR,
DB, OL, TE, free agency/contract, coaching, special teams) with a route-gated
model. It is a separate GitHub-only extension; the interior-DL numbers above are
unchanged.

## Free-agency investigation

[`free_agency/`](free_agency/) is a player-level deep dive that supersedes the
market portfolio's top-down free-agency section. It finds a median-team annual
role premium of $7.05M uncut / $1.82M capture net, with the old $24.9M at the 90.6th
percentile of the team distribution.

## Reproduce

```bash
python implications/code/value_model.py
python implications/code/figures.py
python implications/code/build_notebook.py
jupyter nbconvert --execute --to notebook --inplace implications/code/implications.ipynb
```

- `value_model.py` writes `value_bridge.csv`, `sensitivity.csv`, and `monte_carlo.csv` to `implications/outputs/`.
- `figures.py` writes `value_bridge.png` and `sensitivity.png` to `implications/writeups/figures/`.
- `build_notebook.py` embeds the tables and writes `implications/code/implications.ipynb`.

## Separation and data

- The competition entry is `writeup/submission.md` and `notebooks/02_final_public.ipynb`; this folder does not modify them.
- The raw competition data is CC BY-NC 4.0 and is not copied or redistributed. Only derived summary numbers appear here.
- The team staffing table is date-stamped 2026-10-19 and sourced from Wikipedia's current NFL general manager and head coach lists; re-verify before quoting the table.
- The dollar model is an inference. The measured inputs are in `outputs/discovery/` and `outputs/salary/`, reproduced by the committed pipeline.
- Code is MIT, consistent with the repository license.
