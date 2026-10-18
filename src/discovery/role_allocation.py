"""Robust role-allocation core.

Primary role: total snaps per game (playing time per appearance).
Sensitivities: pass-play role, cohort-relative role share, team mean role.
DB is excluded from pooled performance models (performance residual is
unidentifiable); it is reported separately.

The headline is: next-season role follows current role and draft capital, not
the per-play performance residual; within-player changes in performance do not
predict changes in role.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from sklearn.model_selection import GroupKFold
from sklearn.metrics import r2_score

ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "outputs" / "panel" / "panel_full.parquet"
OUT = ROOT / "outputs" / "discovery"
RNG = np.random.default_rng(42)


def _z_by(df: pd.DataFrame, col: str, by: list[str]) -> pd.Series:
    return df.groupby(by)[col].transform(
        lambda x: (x - x.mean()) / x.std(ddof=0) if x.std(ddof=0) > 0 else x * 0
    )


def _fit(formula: str, data: pd.DataFrame):
    return smf.ols(formula, data=data).fit(
        cov_type="cluster", cov_kwds={"groups": data["nfl_id"]}
    )


def _coef_rows(fit, label: str) -> list[dict]:
    rows = []
    for term in fit.params.index:
        if term == "Intercept" or term.startswith("C("):
            continue
        rows.append(
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
    return rows


def _player_cluster_diff(df: pd.DataFrame, a_label: str, b_label: str, metric: str, n: int = 5000):
    players = df["nfl_id"].unique()
    observed_a = df.loc[df["allocation"] == a_label, metric]
    observed_b = df.loc[df["allocation"] == b_label, metric]
    if len(observed_a) < 3 or len(observed_b) < 3:
        return np.nan, np.nan, np.nan
    draws = []
    for _ in range(n):
        sampled = RNG.choice(players, len(players), replace=True)
        sub = df[df["nfl_id"].isin(sampled)]
        a = sub.loc[sub["allocation"] == a_label, metric]
        b = sub.loc[sub["allocation"] == b_label, metric]
        if len(a) and len(b):
            draws.append(a.mean() - b.mean())
    return (
        float(observed_a.mean() - observed_b.mean()),
        float(np.percentile(draws, 2.5)),
        float(np.percentile(draws, 97.5)),
    )


def build() -> dict[str, pd.DataFrame]:
    panel = pd.read_parquet(PANEL)
    d = panel[panel["perf_z"].notna()].copy()
    # Primary playing-time role; sensitivities.
    d["role_pg"] = d["snaps"] / d["games"].replace(0, np.nan)
    d["role_pass"] = (
        d[["pass_rush_plays", "routes", "pass_block_plays", "coverage_plays"]]
        .max(axis=1)
        / d["games"].replace(0, np.nan)
    )
    d["role_share"] = d["role_share_room"]
    for col, name in [("role_pg", "role_z"), ("role_pass", "role_pass_z"), ("role_share", "role_share_z")]:
        d[name] = _z_by(d, col, ["position_group", "season"])
    d = d.sort_values(["nfl_id", "season"]).reset_index(drop=True)
    d["next_role"] = d.groupby("nfl_id")["role_z"].shift(-1)
    d["next2_role"] = d.groupby("nfl_id")["role_z"].shift(-2)
    d["next_season"] = d.groupby("nfl_id")["season"].shift(-1)
    d["next2_season"] = d.groupby("nfl_id")["season"].shift(-2)
    d["season_c"] = d["season"].astype(str)
    d["position_group"] = d["position_group"].fillna("OTHER")

    t1 = d[(d["next_season"] == d["season"] + 1) & d["next_role"].notna()].copy()
    t2 = d[(d["next2_season"] == d["season"] + 2) & d["next2_role"].notna()].copy()
    fe = " + C(position_group) + C(season_c)"

    # Pooled models exclude DB (unidentifiable performance).
    base = t1[t1["position_group"] != "DB"].dropna(
        subset=["role_z", "perf_z", "B_draft", "prestige_nodraft", "season_c",
                "position_group", "primary_team"]
    ).copy()
    t2 = t2[t2["position_group"] != "DB"].dropna(
        subset=["role_z", "perf_z", "B_draft", "season_c", "position_group"]
    ).copy()
    concurrent = _fit(f"role_z ~ perf_z + B_draft + prestige_nodraft{fe}", base)
    base["role_gap"] = concurrent.resid
    next1 = _fit(f"next_role ~ role_z + perf_z + B_draft{fe}", base)
    next1p = _fit(f"next_role ~ perf_z + B_draft + prestige_nodraft{fe}", base)
    next2 = _fit(f"next2_role ~ role_z + perf_z + B_draft{fe}", t2)
    # Team-mean-role sensitivity.
    base["team_role_mean"] = base.groupby(["primary_team", "season"])["role_z"].transform("mean")
    base = base.dropna(subset=["team_role_mean"]).copy()
    next1_team = _fit(f"next_role ~ role_z + perf_z + B_draft + team_role_mean{fe}", base)
    # Role-measure sensitivities.
    sens = {}
    for role_col, label in [("role_pass_z", "pass-play role"), ("role_share_z", "cohort role share")]:
        sub = t1[t1["position_group"] != "DB"].dropna(subset=[role_col, "next_role"])
        fit = _fit(f"next_role ~ {role_col} + perf_z + B_draft{fe}", sub)
        sens[label] = fit
    # Within-player first differences.
    dd = d[d["position_group"] != "DB"].sort_values(["nfl_id", "season"]).copy()
    dd["d_role"] = dd.groupby("nfl_id")["role_z"].diff()
    dd["d_perf"] = dd.groupby("nfl_id")["perf_z"].diff()
    dd["d_next"] = dd.groupby("nfl_id")["season"].diff()
    diff = dd[dd["d_next"] == 1].dropna(subset=["d_role", "d_perf"])
    within_player = diff[["nfl_id", "season", "d_role", "d_perf", "position_group"]].copy()
    diff_fit = _fit("d_role ~ d_perf", diff)

    rows = []
    rows += _coef_rows(concurrent, "concurrent_role")
    rows += _coef_rows(next1, "next_role_full")
    rows += _coef_rows(next1p, "next_role_perf_only")
    rows += _coef_rows(next2, "next2_role_full")
    rows += _coef_rows(next1_team, "next_role_team_control")
    rows += _coef_rows(diff_fit, "within_player_change")
    for label, fit in sens.items():
        rows += _coef_rows(fit, f"next_role_{label.replace(' ', '_')}")
    coefs = pd.DataFrame(rows)

    # Position-specific replication, DB separate.
    pos_rows = []
    for group in ["DL", "WR", "OL", "TE", "DB"]:
        sub = t1[t1["position_group"] == group].dropna(
            subset=["role_z", "perf_z", "B_draft", "next_role"]
        ).copy()
        if len(sub) < 25:
            continue
        fit = _fit("next_role ~ role_z + perf_z + B_draft", sub)
        identifiable = bool(sub["perf_z"].std(ddof=0) > 0)
        pos_rows.append(
            {
                "position_group": group,
                "n": len(sub),
                "role_coef": float(fit.params["role_z"]),
                "role_ci_low": float(fit.conf_int().loc["role_z", 0]),
                "role_ci_high": float(fit.conf_int().loc["role_z", 1]),
                "role_p": float(fit.pvalues["role_z"]),
                "perf_coef": float(fit.params["perf_z"]) if identifiable else np.nan,
                "perf_ci_low": float(fit.conf_int().loc["perf_z", 0]) if identifiable else np.nan,
                "perf_ci_high": float(fit.conf_int().loc["perf_z", 1]) if identifiable else np.nan,
                "perf_p": float(fit.pvalues["perf_z"]) if identifiable else np.nan,
                "perf_identifiable": identifiable,
                "draft_coef": float(fit.params["B_draft"]),
                "draft_ci_low": float(fit.conf_int().loc["B_draft", 0]),
                "draft_ci_high": float(fit.conf_int().loc["B_draft", 1]),
                "draft_p": float(fit.pvalues["B_draft"]),
                "r2": float(fit.rsquared),
            }
        )
    positions = pd.DataFrame(pos_rows)

    # Out-of-sample (leave-one-player-out) role prediction.
    X = base[["role_z", "perf_z", "B_draft", "position_group", "season_c"]].copy()
    y = base["next_role"].copy()
    groups = base["nfl_id"].to_numpy()
    oof = np.full(len(base), np.nan)
    for tr, te in GroupKFold(5).split(X, y, groups):
        fit = smf.ols("next_role ~ role_z + perf_z + B_draft + C(position_group) + C(season_c)",
                      data=base.iloc[tr]).fit()
        oof[te] = fit.predict(base.iloc[te])
    oof_r2 = r2_score(y, oof)
    oof_perf = []
    for tr, te in GroupKFold(5).split(X, y, groups):
        fit = smf.ols("next_role ~ role_z + perf_z + B_draft + C(position_group) + C(season_c)",
                      data=base.iloc[tr]).fit()
        oof_perf.append(float(fit.params["perf_z"]))
    oof_summary = pd.DataFrame(
        [
            {
                "oof_r2": float(oof_r2),
                "perf_coef_min": float(np.min(oof_perf)),
                "perf_coef_max": float(np.max(oof_perf)),
                "n": len(base),
            }
        ]
    )

    # Descriptive tails on reliable samples; player-cluster bootstrap.
    base["role_gap"] = concurrent.resid
    full_base = base.copy()
    base = base[base["perf_n"] >= 50].copy()
    base["allocation"] = "mid"
    base.loc[
        (base["perf_z"] >= base["perf_z"].quantile(0.75))
        & (base["role_gap"] <= base["role_gap"].quantile(0.25)),
        "allocation",
    ] = "low role / high performance"
    base.loc[
        (base["perf_z"] <= base["perf_z"].quantile(0.25))
        & (base["role_gap"] >= base["role_gap"].quantile(0.75)),
        "allocation",
    ] = "high role / low performance"
    groups_tbl = (
        base.groupby("allocation")
        .agg(
            n=("nfl_id", "size"),
            players=("nfl_id", "nunique"),
            role=("role_z", "mean"),
            perf=("perf_z", "mean"),
            gap=("role_gap", "mean"),
            next_role=("next_role", "mean"),
            draft=("B_draft", "mean"),
        )
        .reset_index()
    )
    contrasts = []
    for metric in ["next_role", "role_z", "perf_z"]:
        a = base.loc[base["allocation"] == "high role / low performance", metric]
        b = base.loc[base["allocation"] == "low role / high performance", metric]
        delta, lo, hi = _player_cluster_diff(
            base, "high role / low performance", "low role / high performance", metric
        )
        contrasts.append(
            {
                "metric": metric,
                "high_role_mean": a.mean(),
                "low_role_mean": b.mean(),
                "diff": delta,
                "ci_low": lo,
                "ci_high": hi,
                "n_high": int(a.notna().sum()),
                "n_low": int(b.notna().sum()),
            }
        )
    return {
        "coefficients": coefs,
        "positions": positions,
        "oof": oof_summary,
        "groups": groups_tbl,
        "contrasts": pd.DataFrame(contrasts),
        "player_seasons": base,
        "player_seasons_full": full_base,
        "within_player": within_player,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    out = build()
    out["coefficients"].to_csv(OUT / "role_allocation_coefficients.csv", index=False)
    out["positions"].to_csv(OUT / "role_allocation_positions.csv", index=False)
    out["oof"].to_csv(OUT / "role_allocation_oof.csv", index=False)
    out["groups"].to_csv(OUT / "role_allocation_groups.csv", index=False)
    out["contrasts"].to_csv(OUT / "role_allocation_contrasts.csv", index=False)
    out["player_seasons"].to_parquet(OUT / "role_allocation_player_seasons.parquet", index=False)
    out["player_seasons_full"].to_parquet(
        OUT / "role_allocation_player_seasons_full.parquet", index=False
    )
    out["within_player"].to_parquet(OUT / "role_within_player.parquet", index=False)
    print(out["coefficients"].to_string(index=False))
    print("\nPositions:")
    print(out["positions"].to_string(index=False))
    print("\nOOF:")
    print(out["oof"].to_string(index=False))
    print("\nGroups:")
    print(out["groups"].to_string(index=False))
    print("\nContrasts:")
    print(out["contrasts"].to_string(index=False))
    (OUT / "role_allocation_manifest.json").write_text(
        json.dumps(
            {
                "rows": len(out["player_seasons"]),
                "players": int(out["player_seasons"]["nfl_id"].nunique()),
                "rows_full": len(out["player_seasons_full"]),
                "players_full": int(out["player_seasons_full"]["nfl_id"].nunique()),
                "models": out["coefficients"]["model"].unique().tolist(),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
