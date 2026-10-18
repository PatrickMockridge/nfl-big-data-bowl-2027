"""Pay-performance residuals (rent proxy) from the 2025 OTC cap ledger.

This is a second-layer, descriptive analysis. The pay model compares a player's
2025 cap number (and, as a sensitivity, current-year cash) with what players at
the same position, age, experience, and measured performance were paid. The
residual is a cap-allocation residual, not a causal rent: cap hits reflect
signing-bonus proration, restructures, timing, and expected future performance.
The 2025 active-roster snapshot covers 98% of snaps; OL and special-teamers are
excluded because they have no individual performance measure in the public data.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from .common import OUT, ensure_dirs

CAP = OUT / "otc_cap_2025_players.csv"
PERF = OUT / "player_performance.csv"
SNAP = OUT / "player_snaps.csv"
PANEL = OUT / "team_salary_panel.csv"
GROUPS = ["QB", "RB", "WR", "TE", "EDGE", "IDL", "LB", "S", "CB"]
RNG = np.random.default_rng(42)


def build_player_table() -> pd.DataFrame:
    cap = pd.read_csv(CAP)
    perf = pd.read_csv(PERF)
    perf = perf[perf["season"].eq(2025)].copy()
    snap = pd.read_csv(SNAP)
    snap = snap[snap["season"].eq(2025)].copy()
    snap["snap_share"] = snap["total_snaps"] / snap.groupby("team")["total_snaps"].transform("sum")

    d = cap.merge(
        perf[["player_id", "group", "perf_z", "perf_n", "perf_metric"]],
        left_on="gsis_id",
        right_on="player_id",
        how="left",
    )
    d = d.merge(
        snap[["gsis_id", "team", "total_snaps", "snap_share"]],
        on=["gsis_id", "team"],
        how="left",
        suffixes=("", "_snap"),
    )
    d = d[d["pos_group"].isin(GROUPS)].copy()
    d = d[d["perf_z"].notna() & d["cap_number"].gt(0) & d["age_start"].notna()].copy()
    d["cash"] = d[["base_salary", "roster_regular", "roster_per_game", "workout_bonus", "other_bonus"]].fillna(0).sum(axis=1)
    return d


def residuals(d: pd.DataFrame, pay_col: str, suffix: str) -> tuple[pd.DataFrame, object]:
    d = d.copy()
    d["_pay"] = d[pay_col]
    d = d[d["_pay"].gt(0)].copy()
    formula = f"np.log(_pay) ~ perf_z + age_start + years_exp + C(pos_group)"
    model = smf.ols(formula, data=d).fit(cov_type="cluster", cov_kwds={"groups": d["team"]})
    d[f"pred_{suffix}"] = np.exp(model.predict(d))
    d[f"resid_{suffix}"] = d["_pay"] - d[f"pred_{suffix}"]

    q_pay = d["_pay"].quantile(0.75)
    q_perf = d["perf_z"].quantile(0.25)
    snap_med = d["snap_share"].median()
    d["star"] = d["_pay"] >= q_pay
    d["underperformer"] = d["perf_z"] <= q_perf
    d["above_median_role"] = d["snap_share"].fillna(0) >= snap_med
    d["young"] = d["age_start"] <= 24
    d["high_perf"] = d["perf_z"] >= d["perf_z"].quantile(0.75)

    d[f"star_rent_{suffix}"] = np.where(d["star"] & d[f"resid_{suffix}"].gt(0), d[f"resid_{suffix}"], 0.0)
    d[f"under_rent_{suffix}"] = np.where(
        d["underperformer"] & d["above_median_role"] & d[f"resid_{suffix}"].gt(0), d[f"resid_{suffix}"], 0.0
    )
    d[f"youth_surplus_{suffix}"] = np.where(
        d["young"] & d["high_perf"] & d[f"resid_{suffix}"].lt(0), -d[f"resid_{suffix}"], 0.0
    )
    return d, model


def team_rents(players: pd.DataFrame, panel: pd.DataFrame) -> pd.DataFrame:
    cap = players.groupby("team").agg(
        n_players=("player", "size"),
        star_rent_cap=("star_rent_cap", "sum"),
        under_rent_cap=("under_rent_cap", "sum"),
        youth_surplus_cap=("youth_surplus_cap", "sum"),
    )
    cap["total_rent_cap"] = cap["star_rent_cap"] + cap["under_rent_cap"]
    cash = players.groupby("team").agg(
        star_rent_cash=("star_rent_cash", "sum"),
        under_rent_cash=("under_rent_cash", "sum"),
        youth_surplus_cash=("youth_surplus_cash", "sum"),
    )
    cash["total_rent_cash"] = cash["star_rent_cash"] + cash["under_rent_cash"]
    out = cap.join(cash).reset_index()
    p25 = panel[panel["season"].eq(2025)][["team", "wins_per_100m", "wins", "point_diff", "off_epa_per_play"]]
    out = out.merge(p25, on="team", how="left")
    out["eff_quartile"] = pd.qcut(out["wins_per_100m"], 4, labels=["Q1 low", "Q2", "Q3", "Q4 high"])
    return out


def quartile_summary(team: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for q, g in team.groupby("eff_quartile", observed=True):
        rows.append(
            {
                "eff_quartile": str(q),
                "n_teams": len(g),
                "star_rent_m": g["star_rent_cap"].mean() / 1e6,
                "under_rent_m": g["under_rent_cap"].mean() / 1e6,
                "total_rent_m": g["total_rent_cap"].mean() / 1e6,
                "youth_surplus_m": g["youth_surplus_cap"].mean() / 1e6,
                "wins_per_100m": g["wins_per_100m"].mean(),
            }
        )
    return pd.DataFrame(rows)


def bootstrap_corr(x: pd.Series, y: pd.Series, n: int = 3000) -> tuple[float, float, float]:
    d = pd.DataFrame({"x": x, "y": y}).dropna()
    r = d["x"].corr(d["y"])
    draws = []
    for _ in range(n):
        s = d.sample(len(d), replace=True, random_state=int(RNG.integers(1e9)))
        draws.append(s["x"].corr(s["y"]))
    lo, hi = np.percentile(draws, [2.5, 97.5])
    return r, lo, hi


def quartile_difference(team: pd.DataFrame, col: str, n: int = 3000) -> tuple[float, float, float]:
    q1 = team.loc[team["eff_quartile"].eq("Q1 low"), col]
    q4 = team.loc[team["eff_quartile"].eq("Q4 high"), col]
    obs = q4.mean() - q1.mean()
    draws = []
    for _ in range(n):
        a = RNG.choice(q4.to_numpy(), len(q4), True).mean()
        b = RNG.choice(q1.to_numpy(), len(q1), True).mean()
        draws.append(a - b)
    lo, hi = np.percentile(draws, [2.5, 97.5])
    return obs, lo, hi


def main() -> None:
    players = build_player_table()
    base_cols = ["player", "team", "pos_group", "gsis_id", "age_start", "years_exp", "perf_z",
                 "perf_n", "snap_share", "cap_number", "cash", "star", "underperformer",
                 "above_median_role", "young", "high_perf"]
    cap_players, cap_model = residuals(players, "cap_number", "cap")
    cash_players, cash_model = residuals(players[players["cash"].gt(0)].copy(), "cash", "cash")
    cap_players = cap_players.merge(
        cash_players[["gsis_id", "team", "star_rent_cash", "under_rent_cash", "youth_surplus_cash"]],
        on=["gsis_id", "team"],
        how="left",
    )
    for c in ["star_rent_cash", "under_rent_cash", "youth_surplus_cash"]:
        cap_players[c] = cap_players[c].fillna(0.0)

    panel = pd.read_csv(PANEL)
    team = team_rents(cap_players, panel)
    quart = quartile_summary(team)

    # Correlations and quartile contrasts with bootstrap CIs.
    rows = []
    for col in ["star_rent_cap", "under_rent_cap", "youth_surplus_cap",
                "star_rent_cash", "under_rent_cash", "youth_surplus_cash"]:
        r, lo, hi = bootstrap_corr(team[col], team["wins_per_100m"])
        rows.append({"measure": col, "stat": "corr_wins_per_100m", "value": r, "ci_low": lo, "ci_high": hi})
    for col in ["star_rent_cap", "under_rent_cap", "total_rent_cap", "youth_surplus_cap"]:
        d, lo, hi = quartile_difference(team, col)
        rows.append({"measure": col, "stat": "Q4_minus_Q1", "value": d, "ci_low": lo, "ci_high": hi})
    results = pd.DataFrame(rows)

    ensure_dirs()
    keep = base_cols + [c for c in cap_players.columns if c.startswith(("pred_", "resid_", "star_rent_", "under_rent_", "youth_surplus_"))]
    cap_players[keep].to_csv(OUT / "rent_players.csv", index=False)
    team.to_csv(OUT / "rent_team.csv", index=False)
    quart.to_csv(OUT / "rent_quartiles.csv", index=False)
    results.to_csv(OUT / "rent_results.csv", index=False)

    print(f"rent sample: {len(cap_players)} players, {cap_players.team.nunique()} teams; "
          f"cap coverage {cap_players.cap_number.sum() / pd.read_csv(CAP).cap_number.sum():.1%}")
    print(f"pay models R2: cap {cap_model.rsquared:.3f}, cash {cash_model.rsquared:.3f}")
    print("\nRent by efficiency quartile ($M per team, cap-hit measure):")
    print(quart.round(2).to_string(index=False))
    print("\nRent-vs-efficiency statistics:")
    print(results.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
