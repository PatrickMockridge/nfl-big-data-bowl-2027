"""Player- and team-level surplus in the free-agent market.

Residuals are actual APY minus the model's predicted APY. Positive means the
contract is above the market model; negative means below. This is descriptive,
not a causal over/under-payment claim.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from pricing import prepare

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "implications" / "free_agency" / "outputs"
PANEL = ROOT / "outputs" / "salary" / "team_salary_panel.csv"


def _fit_predict(d: pd.DataFrame, formula: str) -> tuple[np.ndarray, float]:
    """Lognormal prediction with a Duan smearing correction."""
    model = smf.ols(formula, data=d).fit(
        cov_type="cluster", cov_kwds={"groups": d["team"]}
    )
    smear = float(np.mean(np.exp(model.resid)))
    pred = np.exp(model.predict(d)) * smear
    return pred, float(model.params["perf_z"])


def build_players() -> pd.DataFrame:
    d = prepare(pd.read_csv(OUT / "fa_class_2026.csv"))
    d = d.dropna(subset=[
        "logapy", "perf_z", "snap_share", "age_at_signing", "age_sq",
        "years_exp", "team_change", "pos_group", "team",
    ]).copy()
    base = (
        "logapy ~ perf_z + age_at_signing + age_sq + years_exp + team_change"
        " + C(pos_group)"
    )
    pred_raw, b_raw = _fit_predict(d, base)
    _, b_role = _fit_predict(d, base + " + snap_share")
    gap = b_raw - b_role
    # Counterfactual: hold the raw-model level and remove the part of the
    # performance weight that the role control absorbs.
    d["pred_raw"] = pred_raw
    d["role_premium"] = pred_raw * (1 - np.exp(-gap * d["perf_z"]))
    d["pred_role"] = pred_raw - d["role_premium"]
    d["resid_raw"] = d["apy"] - d["pred_raw"]
    d["resid_role"] = d["apy"] - d["pred_role"]
    d["above_market"] = d["resid_raw"] > 0
    d["age_bucket"] = pd.cut(
        d["age_at_signing"], [0, 23, 25, 27, 29, 31, 100],
        labels=["<=23", "24-25", "26-27", "28-29", "30-31", "32+"],
    )
    d["type"] = np.select(
        [d["rookie"].eq(1), d["team_change"].eq(1)],
        ["rookie", "team_change"],
        default="re_sign",
    )
    return d


def groups(d: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for dim, col in [
        ("position", "pos_group"),
        ("age", "age_bucket"),
        ("type", "type"),
        ("guarantee_quartile", "guarantee_q"),
    ]:
        if col == "guarantee_q":
            d[col] = pd.qcut(d["guarantee_share"], 4, labels=False, duplicates="drop")
        for value, cell in d.groupby(col, observed=True):
            positive = cell["resid_raw"].clip(lower=0).sum()
            total = cell["resid_raw"].sum()
            rows.append(
                {
                    "dimension": dim,
                    "group": str(value),
                    "n": len(cell),
                    "mean_resid_raw_m": cell["resid_raw"].mean(),
                    "total_resid_raw_m": total,
                    "share_positive": cell["above_market"].mean(),
                    "mean_role_premium_m": cell["role_premium"].mean(),
                    "total_role_premium_m": cell["role_premium"].sum(),
                    "concentration": positive / total if total > 0 else np.nan,
                }
            )
    return pd.DataFrame(rows)


def teams(d: pd.DataFrame) -> pd.DataFrame:
    out = (
        d.groupby("team")
        .agg(
            n=("player", "size"),
            total_resid_raw_m=("resid_raw", "sum"),
            total_role_premium_m=("role_premium", "sum"),
            mean_resid_raw_m=("resid_raw", "mean"),
            median_apy_m=("apy", "median"),
        )
        .reset_index()
    )
    panel = pd.read_csv(PANEL)
    panel = panel[panel["season"].eq(2025)][
        ["team", "wins", "point_diff", "off_epa_per_play", "wins_per_100m"]
    ]
    return out.merge(panel, on="team", how="left")


def concentration(d: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for metric in ["resid_raw", "role_premium"]:
        positive = d[d[metric] > 0][metric].sort_values(ascending=False)
        total = positive.sum()
        for share in [0.01, 0.05, 0.10, 0.25]:
            k = max(1, int(np.ceil(len(positive) * share)))
            rows.append(
                {
                    "metric": metric,
                    "top_share": share,
                    "contracts": k,
                    "value_m": positive.head(k).sum(),
                    "share_of_positive": positive.head(k).sum() / total if total > 0 else np.nan,
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    d = build_players()
    d.to_csv(OUT / "surplus_players.csv", index=False)
    groups(d).to_csv(OUT / "surplus_groups.csv", index=False)
    teams(d).to_csv(OUT / "surplus_teams.csv", index=False)
    concentration(d).to_csv(OUT / "surplus_concentration.csv", index=False)

    print("n:", len(d))
    print("mean resid raw ($M):", round(float(d["resid_raw"].mean()), 3))
    print("mean role premium ($M):", round(float(d["role_premium"].mean()), 3))
    print("\nby position:")
    print(
        d.groupby("pos_group")
        .agg(n=("player", "size"), mean_resid=("resid_raw", "mean"),
             mean_role_premium=("role_premium", "mean"))
        .round(3)
        .to_string()
    )
    print("\nconcentration:")
    print(concentration(d).round(3).to_string(index=False))


if __name__ == "__main__":
    main()
