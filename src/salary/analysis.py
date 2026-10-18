"""Cost-efficiency models: the headline dollar test.

All models are observational. Standard errors are clustered by team (32
clusters), and season fixed effects absorb league-wide cap growth. The
efficiency outcomes divide by payroll, so payroll is included as a control;
the levels models (wins, point differential, EPA per play) are the cleaner
specifications and are reported alongside.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from .common import OUT, ensure_dirs

PANEL = OUT / "team_salary_panel.csv"


def fit(df: pd.DataFrame, formula: str, outcome: str, spec: str, groups: str = "team") -> pd.DataFrame:
    data = df.dropna(subset=[c for c in df.columns if c in formula or c == groups]).copy()
    model = smf.ols(formula, data=data).fit(cov_type="cluster", cov_kwds={"groups": data[groups]})
    rows = []
    for term in model.params.index:
        if term.startswith("C(") or term == "Intercept":
            continue
        rows.append(
            {
                "outcome": outcome,
                "spec": spec,
                "term": term,
                "coef": model.params[term],
                "se": model.bse[term],
                "ci_low": model.conf_int().loc[term, 0],
                "ci_high": model.conf_int().loc[term, 1],
                "p": model.pvalues[term],
                "n": int(model.nobs),
                "r2": model.rsquared,
            }
        )
    return pd.DataFrame(rows)


def run_models(panel: pd.DataFrame) -> pd.DataFrame:
    specs = {
        "star": "star_share + log_payroll + C(season_c)",
        "star_decomp": "star_nonqb_share + qb_share + log_payroll + C(season_c)",
        "skill_qb": "skill_share + qb_share + log_payroll + C(season_c)",
        "youth": "youth_snap_share + log_payroll + C(season_c)",
        "rookie_homegrown": "rookie_snap_share + homegrown_snap_share + log_payroll + C(season_c)",
        "joint": "star_share + youth_snap_share + log_payroll + C(season_c)",
        "star_youth_homegrown": "star_share + youth_snap_share + homegrown_snap_share + log_payroll + C(season_c)",
    }
    outcomes = ["wins", "point_diff", "off_epa_per_play", "wins_per_100m", "point_diff_per_100m", "off_epa_per_100m"]
    rows = []
    for outcome in outcomes:
        if outcome not in panel.columns:
            continue
        for spec, rhs in specs.items():
            rows.append(fit(panel, f"{outcome} ~ {rhs}", outcome, spec))
    return pd.concat(rows, ignore_index=True)


def qb_premium(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for outcome in ["wins", "point_diff", "off_epa_per_play", "wins_per_100m", "off_epa_per_100m"]:
        df = panel.dropna(subset=[outcome, "qb_share", "log_payroll", "season_c"]).copy()
        model = smf.ols(
            f"{outcome} ~ qb_share + I(qb_share**2) + log_payroll + C(season_c)",
            data=df,
        ).fit(cov_type="cluster", cov_kwds={"groups": df["team"]})
        b1, b2 = model.params["qb_share"], model.params["I(qb_share ** 2)"]
        inflection = -b1 / (2 * b2) if b2 < 0 else np.nan
        for term in ["qb_share", "I(qb_share ** 2)"]:
            rows.append(
                {
                    "outcome": outcome,
                    "term": term,
                    "coef": model.params[term],
                    "se": model.bse[term],
                    "ci_low": model.conf_int().loc[term, 0],
                    "ci_high": model.conf_int().loc[term, 1],
                    "p": model.pvalues[term],
                    "n": int(model.nobs),
                    "inflection_qb_share": inflection,
                }
            )
    return pd.DataFrame(rows)


def top_qb_tiers(panel: pd.DataFrame) -> pd.DataFrame:
    """Compare top-quartile QB-spend teams with the rest, 2025 cross-section."""
    d = panel[panel["season"].eq(2025)].copy()
    rows = []
    for col, label in [("cap_qb_share", "cap_qb_share"), ("qb_share", "otc_qb_share")]:
        d["_top"] = d[col] >= d[col].quantile(0.75)
        for outcome in ["wins", "point_diff", "off_epa_per_play", "wins_per_100m", "off_epa_per_100m"]:
            a = d.loc[d["_top"], outcome]
            b = d.loc[~d["_top"], outcome]
            rows.append(
                {
                    "measure": label,
                    "outcome": outcome,
                    "top_mean": a.mean(),
                    "rest_mean": b.mean(),
                    "difference": a.mean() - b.mean(),
                    "n_top": len(a),
                    "n_rest": len(b),
                }
            )
    return pd.DataFrame(rows)


def cap_sensitivity(panel: pd.DataFrame) -> pd.DataFrame:
    """2025 OTC active-cap measures as an alternative to positional spending."""
    d = panel[panel["season"].eq(2025)].copy()
    specs = {
        "cap_star": "cap_star_share + log_payroll",
        "cap_star_qb": "cap_star_share + cap_qb_share + log_payroll",
        "cap_top5": "cap_top5_share + log_payroll",
        "cap_qb": "cap_qb_share + log_payroll",
    }
    rows = []
    for outcome in ["wins", "point_diff", "off_epa_per_play", "wins_per_100m", "point_diff_per_100m", "off_epa_per_100m"]:
        for spec, rhs in specs.items():
            rows.append(fit(d, f"{outcome} ~ {rhs}", outcome, spec))
    return pd.concat(rows, ignore_index=True)


def standardize_results(results: pd.DataFrame, panel: pd.DataFrame) -> pd.DataFrame:
    """Add per-1-SD and per-10pp effect sizes for the headline predictors."""
    out = results.copy()
    predictors = ["star_share", "star_nonqb_share", "qb_share", "skill_share", "youth_snap_share", "rookie_snap_share", "homegrown_snap_share", "cap_star_share", "cap_qb_share", "cap_top5_share"]
    out["sd_predictor"] = out["term"].map(panel[predictors].std(numeric_only=True))
    out["per_sd"] = out["coef"] * out["sd_predictor"]
    out["per_10pp"] = out["coef"] * 0.10
    return out


def main() -> None:
    panel = pd.read_csv(PANEL)
    ensure_dirs()
    results = standardize_results(run_models(panel), panel)
    qb = qb_premium(panel)
    tiers = top_qb_tiers(panel)
    cap = standardize_results(cap_sensitivity(panel), panel)
    results.to_csv(OUT / "salary_results.csv", index=False)
    qb.to_csv(OUT / "qb_premium.csv", index=False)
    tiers.to_csv(OUT / "qb_tiers.csv", index=False)
    cap.to_csv(OUT / "cap_sensitivity.csv", index=False)
    print(f"salary models: {len(results)} term rows; cap models: {len(cap)}")
    print("\nHeadline: wins ~ star")
    print(results.query("outcome == 'wins' and spec == 'star'")[["term", "coef", "ci_low", "ci_high", "p", "n", "per_sd"]].round(3).to_string(index=False))
    print("\nHeadline: wins ~ rookie + homegrown")
    print(results.query("outcome == 'wins' and spec == 'rookie_homegrown'")[["term", "coef", "ci_low", "ci_high", "p", "n", "per_sd"]].round(3).to_string(index=False))
    print("\nQB quadratic")
    print(qb[["outcome", "term", "coef", "p", "inflection_qb_share"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
