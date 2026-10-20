"""Coaching retention: a descriptive market map.

No dollar value. The question is whether retention tracks wins/status or
allocation efficiency. The latter is not available as a coach-level measure, so
the model is a wins/tenure description only.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[3]
IN = ROOT / "implications" / "markets" / "outputs" / "coaching_seasons.csv"
OUT = ROOT / "implications" / "markets" / "outputs"


def _fit(formula: str, d: pd.DataFrame, model: str) -> list[dict]:
    fit = smf.ols(formula, data=d).fit(
        cov_type="cluster", cov_kwds={"groups": d["team"]}
    )
    rows = []
    for term in fit.params.index:
        if term == "Intercept" or term.startswith("C("):
            continue
        ci = fit.conf_int().loc[term]
        rows.append(
            {
                "model": model,
                "term": term,
                "coef": float(fit.params[term]),
                "se": float(fit.bse[term]),
                "ci_low": float(ci[0]),
                "ci_high": float(ci[1]),
                "p": float(fit.pvalues[term]),
                "n": int(fit.nobs),
                "r2": float(fit.rsquared),
            }
        )
    return rows


def build_models(d: pd.DataFrame) -> pd.DataFrame:
    rows = _fit(
        "retained_next ~ wins + point_diff + tenure + C(season)",
        d,
        "linear_probability",
    )
    try:
        logit = smf.logit(
            "retained_next ~ wins + point_diff + tenure + C(season)", data=d
        ).fit(disp=0, cov_type="cluster", cov_kwds={"groups": d["team"]})
        for term in logit.params.index:
            if term == "Intercept" or term.startswith("C("):
                continue
            ci = logit.conf_int().loc[term]
            rows.append(
                {
                    "model": "logit_sensitivity",
                    "term": term,
                    "coef": float(logit.params[term]),
                    "se": float(logit.bse[term]),
                    "ci_low": float(ci[0]),
                    "ci_high": float(ci[1]),
                    "p": float(logit.pvalues[term]),
                    "n": int(logit.nobs),
                    "r2": float(logit.prsquared),
                }
            )
    except Exception as exc:  # pragma: no cover - separation dependent
        print(f"logit sensitivity skipped: {exc}")
    return pd.DataFrame(rows)


def descriptive(d: pd.DataFrame) -> pd.DataFrame:
    d = d.copy()
    d["wins_q"] = pd.qcut(d["wins"], 4, labels=False, duplicates="drop")
    d["tenure_bucket"] = pd.cut(
        d["tenure"], [0, 1, 2, 3, 5, 100],
        labels=["1", "2", "3", "4-5", "6+"],
    )
    rows = []
    for label, col in [("wins_quartile", "wins_q"), ("tenure_bucket", "tenure_bucket")]:
        for value, cell in d.groupby(col, observed=True):
            rows.append(
                {
                    "dimension": label,
                    "bucket": str(value),
                    "team_seasons": len(cell),
                    "retention_rate": cell["retained_next"].mean(),
                    "mean_wins": cell["wins"].mean(),
                    "mean_tenure": cell["tenure"].mean(),
                }
            )
    return pd.DataFrame(rows)


def market_map(d: pd.DataFrame) -> pd.DataFrame:
    out = (
        d.groupby("season")
        .agg(
            team_seasons=("team", "nunique"),
            retention_rate=("retained_next", "mean"),
            mean_tenure=("tenure", "mean"),
            mean_wins=("wins", "mean"),
            midseason_changes=("n_coaches", lambda s: int((s > 1).sum())),
        )
        .reset_index()
    )
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    d = pd.read_csv(IN)
    d = d[d["next_season"].notna()].copy()
    models = build_models(d)
    models.to_csv(OUT / "coaching_retention.csv", index=False)
    descriptive(d).to_csv(OUT / "coaching_descriptive.csv", index=False)
    market_map(d).to_csv(OUT / "coaching_market_map.csv", index=False)
    print(models.round(3).to_string(index=False))
    print("\nretention rate:", round(float(d["retained_next"].mean()), 3), "n", len(d))


if __name__ == "__main__":
    main()
