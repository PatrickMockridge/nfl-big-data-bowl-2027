"""The predictability premium and the rent residual.

Hypothesis: teams shift the risk burden of unpredictable youth by favoring
predictable low performers; career rewards then accrue to role/predictability
rather than performance (a structural rent).

Volatility = within-season weekly residual SD.
Role gap = role unexplained by concurrent performance/draft (from role_allocation).
Rent = career reward residual after performance, draft capital, and position.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "outputs" / "panel" / "panel_full.parquet"
DISC = ROOT / "outputs" / "discovery"
OUT = DISC


def _load() -> pd.DataFrame:
    panel = pd.read_parquet(PANEL)
    players = pd.read_csv(ROOT / "data" / "raw" / "players.csv", usecols=["nfl_id", "birth_date"])
    players["birth_date"] = pd.to_datetime(players["birth_date"], errors="coerce")
    panel = panel.merge(players, on="nfl_id", how="left")
    panel["age"] = panel["season"] - panel["birth_date"].dt.year
    panel["experience"] = panel["season"] - panel["draft_year"]
    weekly = []
    for group in ["DL", "WR", "TE", "OL", "DB"]:
        path = ROOT / "outputs" / "panel" / f"weekly_{group}.parquet"
        if path.exists():
            w = pd.read_parquet(path)
            w = (
                w.sort_values(["nfl_id", "season", "week"])
                .drop_duplicates(["nfl_id", "season"], keep="last")
                .rename(columns={"weekly_sd": "volatility"})
            )
            weekly.append(w[["nfl_id", "season", "volatility"]])
    if weekly:
        panel = panel.merge(pd.concat(weekly, ignore_index=True), on=["nfl_id", "season"], how="left")
    role = pd.read_parquet(DISC / "role_allocation_player_seasons.parquet")
    role = role[role["role_gap"].notna()].copy()
    d = role.merge(
        panel[["nfl_id", "season", "age", "experience", "volatility"]],
        on=["nfl_id", "season"],
        how="left",
    )
    d["season_c"] = d["season"].astype(str)
    return d


def _fit(formula: str, data: pd.DataFrame):
    return smf.ols(formula, data=data).fit(
        cov_type="cluster", cov_kwds={"groups": data["nfl_id"]}
    )


def _rows(fit, label: str) -> list[dict]:
    out = []
    for term in fit.params.index:
        if term == "Intercept" or term.startswith("C("):
            continue
        out.append(
            {
                "model": label,
                "term": term,
                "coef": float(fit.params[term]),
                "se": float(fit.bse[term]),
                "p": float(fit.pvalues[term]),
                "ci_low": float(fit.conf_int().loc[term, 0]),
                "ci_high": float(fit.conf_int().loc[term, 1]),
                "n": int(fit.nobs),
                "r2": float(fit.rsquared),
            }
        )
    return out


def build() -> dict[str, pd.DataFrame]:
    d = _load().dropna(subset=["volatility", "age", "experience"]).copy()
    models = [
        ("role_gap ~ volatility + age + experience + B_draft + C(position_group)", "role_gap"),
        (
            "next_role ~ perf_z + volatility + age + experience + B_draft + role_z "
            "+ C(position_group) + C(season_c)",
            "next_role",
        ),
        (
            "career_status_z ~ role_gap + volatility + age + experience + B_draft "
            "+ C(position_group)",
            "career_status",
        ),
        (
            "career_start_rate ~ role_gap + volatility + age + experience + B_draft "
            "+ C(position_group)",
            "career_start",
        ),
    ]
    rows = []
    for formula, label in models:
        rows += _rows(_fit(formula, d), label)
    coefficients = pd.DataFrame(rows)

    # Player-level rent: rewards beyond performance/draft.
    agg = (
        d.groupby("nfl_id")
        .agg(
            perf=("perf_z", "mean"),
            role=("role_z", "mean"),
            volatility=("volatility", "mean"),
            career_status=("career_status_z", "first"),
            start_rate=("career_start_rate", "first"),
            accolades=("career_accolades", "first"),
            B_draft=("B_draft", "first"),
            position=("position_group", "first"),
            seasons=("season", "nunique"),
        )
        .reset_index()
        .dropna(subset=["volatility", "perf", "role"])
    )
    for target in ["career_status", "start_rate", "accolades"]:
        base = smf.ols(f"{target} ~ perf + B_draft + C(position)", data=agg).fit()
        agg[f"rent_{target}"] = base.resid
        fit = smf.ols(
            f"rent_{target} ~ role + volatility + perf + B_draft + C(position)", data=agg
        ).fit(cov_type="HC3")
        for term in ["role", "volatility", "perf", "B_draft"]:
            rows.append(
                {
                    "model": f"rent_{target}",
                    "term": term,
                    "coef": float(fit.params[term]),
                    "se": float(fit.bse[term]),
                    "p": float(fit.pvalues[term]),
                    "ci_low": float(fit.conf_int().loc[term, 0]),
                    "ci_high": float(fit.conf_int().loc[term, 1]),
                    "n": int(fit.nobs),
                    "r2": float(fit.rsquared),
                }
            )
    coefficients = pd.DataFrame(rows)

    # Predictability groups: low vs high volatility within position.
    agg["vol_group"] = np.where(
        agg["volatility"] >= agg.groupby("position")["volatility"].transform("median"),
        "high volatility",
        "low volatility",
    )
    predictability = (
        agg.groupby(["position", "vol_group"])
        .agg(
            n=("nfl_id", "size"),
            perf=("perf", "mean"),
            role=("role", "mean"),
            career_status=("career_status", "mean"),
            start_rate=("start_rate", "mean"),
            rent_status=("rent_career_status", "mean"),
            rent_start=("rent_start_rate", "mean"),
        )
        .reset_index()
    )
    return {
        "coefficients": coefficients,
        "players": agg,
        "predictability": predictability,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    out = build()
    out["coefficients"].to_csv(OUT / "rent_coefficients.csv", index=False)
    out["players"].to_parquet(OUT / "rent_players.parquet", index=False)
    out["predictability"].to_csv(OUT / "predictability_groups.csv", index=False)
    print(out["coefficients"].to_string(index=False))
    print("\nPredictability groups:")
    print(out["predictability"].to_string(index=False))
    (OUT / "rent_manifest.json").write_text(
        json.dumps(
            {
                "player_rows": len(out["players"]),
                "models": out["coefficients"]["model"].unique().tolist(),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
