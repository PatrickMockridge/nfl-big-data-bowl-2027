"""Special teams: a descriptive market with a reliability gate.

Builds K/P/returner season composites from the nflverse weekly stats, checks
odd/even-game reliability, and fits a descriptive cap model only if the gate
passes. No selection or role dollar route.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[3]
EXT = ROOT / "data" / "external"
CAP = ROOT / "outputs" / "salary" / "otc_cap_2025_players.csv"
OUT = ROOT / "implications" / "markets" / "outputs"
SEASONS = [2023, 2024, 2025]

COLS = [
    "player_id", "player_name", "position", "position_group", "season", "week",
    "season_type", "fg_made", "fg_att", "pat_made", "pat_att", "fg_long",
    "pt_att", "pt_yards", "pt_net_yards", "pt_inside_20", "pt_touchback",
    "punt_returns", "punt_return_yards", "kickoff_returns",
    "kickoff_return_yards", "special_teams_tds", "recent_team",
]


def load_weekly() -> pd.DataFrame:
    frames = []
    for season in SEASONS:
        path = EXT / f"stats_player_week_{season}.csv"
        d = pd.read_csv(path, usecols=lambda c: c in COLS)
        if "season_type" in d:
            d = d[d["season_type"].eq("REG")]
        frames.append(d)
    d = pd.concat(frames, ignore_index=True)
    for col in COLS:
        if col not in d:
            d[col] = np.nan
    d = d.fillna({c: 0 for c in COLS if c not in {"season_type", "recent_team"}})
    return d


def assign_role(d: pd.DataFrame) -> pd.Series:
    role = pd.Series("", index=d.index)
    role.loc[d["fg_att"] >= 20] = "K"
    role.loc[d["pt_att"] >= 30] = "P"
    ret = d["punt_returns"] + d["kickoff_returns"]
    role.loc[(role == "") & (ret >= 20)] = "RET"
    return role


def season_metrics(weekly: pd.DataFrame) -> pd.DataFrame:
    agg = (
        weekly.groupby(["player_id", "player_name", "season", "position"], dropna=False)
        .agg(
            team=("recent_team", "first"),
            games=("week", "nunique"),
            fg_made=("fg_made", "sum"),
            fg_att=("fg_att", "sum"),
            pat_made=("pat_made", "sum"),
            pat_att=("pat_att", "sum"),
            fg_long=("fg_long", "max"),
            pt_att=("pt_att", "sum"),
            pt_yards=("pt_yards", "sum"),
            pt_net_yards=("pt_net_yards", "sum"),
            pt_inside_20=("pt_inside_20", "sum"),
            pt_touchback=("pt_touchback", "sum"),
            punt_returns=("punt_returns", "sum"),
            punt_return_yards=("punt_return_yards", "sum"),
            kickoff_returns=("kickoff_returns", "sum"),
            kickoff_return_yards=("kickoff_return_yards", "sum"),
            special_teams_tds=("special_teams_tds", "sum"),
        )
        .reset_index()
    )
    agg["role"] = assign_role(agg)
    agg = agg[agg["role"].ne("")].copy()
    agg["fg_pct"] = agg["fg_made"] / agg["fg_att"].replace(0, np.nan)
    agg["pat_pct"] = agg["pat_made"] / agg["pat_att"].replace(0, np.nan)
    agg["net_per_att"] = agg["pt_net_yards"] / agg["pt_att"].replace(0, np.nan)
    agg["inside20_rate"] = agg["pt_inside_20"] / agg["pt_att"].replace(0, np.nan)
    agg["touchback_rate"] = agg["pt_touchback"] / agg["pt_att"].replace(0, np.nan)
    returns = agg["punt_returns"] + agg["kickoff_returns"]
    ret_yards = agg["punt_return_yards"] + agg["kickoff_return_yards"]
    agg["return_yards_per"] = ret_yards / returns.replace(0, np.nan)
    agg["return_td_rate"] = agg["special_teams_tds"] / returns.replace(0, np.nan)
    return agg


def _z(series: pd.Series) -> pd.Series:
    sd = series.std(ddof=0)
    return (series - series.mean()) / sd if sd and not np.isnan(sd) else series * 0.0


def composite(d: pd.DataFrame) -> pd.DataFrame:
    d = d.copy()
    d["st_perf_z"] = np.nan
    for role, cols in {
        "K": [("fg_pct", 1), ("pat_pct", 1), ("fg_long", 1)],
        "P": [("net_per_att", 1), ("inside20_rate", 1), ("touchback_rate", -1)],
        "RET": [("return_yards_per", 1), ("return_td_rate", 1)],
    }.items():
        idx = d["role"] == role
        if not idx.any():
            continue
        parts = []
        for col, sign in cols:
            z = d.loc[idx].groupby("season")[col].transform(_z)
            parts.append(sign * z)
        d.loc[idx, "st_perf_z"] = pd.concat(parts, axis=1).mean(axis=1)
    return d


def reliability(weekly: pd.DataFrame, season: pd.DataFrame) -> pd.DataFrame:
    """Odd/even-week split-half reliability of the primary metric per role."""
    weekly = weekly.copy()
    weekly["parity"] = weekly["week"] % 2
    weekly = weekly.merge(
        season[["player_id", "season", "role"]],
        on=["player_id", "season"],
        how="inner",
    )
    weekly["fg_pct"] = weekly["fg_made"] / weekly["fg_att"].replace(0, np.nan)
    weekly["net_per_att"] = weekly["pt_net_yards"] / weekly["pt_att"].replace(0, np.nan)
    returns = weekly["punt_returns"] + weekly["kickoff_returns"]
    ret_yards = weekly["punt_return_yards"] + weekly["kickoff_return_yards"]
    weekly["return_yards_per"] = ret_yards / returns.replace(0, np.nan)

    metrics = {"K": "fg_pct", "P": "net_per_att", "RET": "return_yards_per"}
    rows = []
    for role, metric in metrics.items():
        sub = weekly[weekly["role"] == role]
        halves = (
            sub.groupby(["player_id", "season", "parity"])[metric]
            .mean()
            .unstack()
            .dropna()
        )
        if len(halves) < 10:
            rows.append(
                {"role": role, "metric": metric, "n": len(halves),
                 "split_half_r": np.nan, "reliability": np.nan}
            )
            continue
        r = float(halves[0].corr(halves[1]))
        sb = float(2 * r / (1 + r)) if np.isfinite(r) and r > -1 else np.nan
        rows.append(
            {"role": role, "metric": metric, "n": len(halves),
             "split_half_r": r, "reliability": sb}
        )
    return pd.DataFrame(rows)


def pricing(season: pd.DataFrame, rel: pd.DataFrame) -> pd.DataFrame:
    cap = pd.read_csv(CAP)
    cap = cap[cap["pos_group"].eq("ST")].copy()
    d = season[season["season"].eq(2025)].merge(
        cap[["gsis_id", "cap_number", "age_start", "years_exp", "team", "position"]],
        left_on="player_id",
        right_on="gsis_id",
        how="inner",
    )
    d = d[d["cap_number"].gt(0) & d["st_perf_z"].notna()].copy()
    d["logcap"] = np.log(d["cap_number"])
    rows = []
    for role, cell in d.groupby("role"):
        gate = rel.loc[rel["role"].eq(role), "reliability"]
        gate_value = float(gate.iloc[0]) if len(gate) else np.nan
        if len(cell) < 20 or not np.isfinite(gate_value) or gate_value < 0.50:
            rows.append(
                {"role": role, "n": len(cell), "reliability": gate_value,
                 "term": "st_perf_z", "coef": np.nan, "ci_low": np.nan,
                 "ci_high": np.nan, "p": np.nan, "status": "unidentifiable"}
            )
            continue
        model = smf.ols(
            "logcap ~ st_perf_z + age_start + years_exp", data=cell
        ).fit(cov_type="cluster", cov_kwds={"groups": cell["team"]})
        ci = model.conf_int().loc["st_perf_z"]
        rows.append(
            {
                "role": role,
                "n": int(model.nobs),
                "reliability": gate_value,
                "term": "st_perf_z",
                "coef": float(model.params["st_perf_z"]),
                "ci_low": float(ci[0]),
                "ci_high": float(ci[1]),
                "p": float(model.pvalues["st_perf_z"]),
                "status": "exploratory",
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    weekly = load_weekly()
    season = composite(season_metrics(weekly))
    rel = reliability(weekly, season)
    market = pricing(season, rel)
    season.to_csv(OUT / "st_performance.csv", index=False)
    rel.to_csv(OUT / "st_reliability.csv", index=False)
    market.to_csv(OUT / "st_market.csv", index=False)
    print(rel.round(3).to_string(index=False))
    print()
    print(market.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
