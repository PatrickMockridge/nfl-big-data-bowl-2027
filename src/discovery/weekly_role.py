"""Week-to-week role check for the football-score conclusion.

The season-level result is the primary evidence. This module asks the narrower
operational question: within a season, does a player's performance this week
predict his role next week, holding current role, draft capital, position,
season, and week fixed? It uses the weekly performance residuals already built
by ``features.performance`` and weekly role shares from ``player_play``.

The result is reported as a bounded check, not a new thesis. If the performance
coefficient is null, the operational conclusion is a 4-6 week role review, not
a single-week trigger.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from data import load

ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "outputs" / "panel" / "panel_full.parquet"
WEEKLY = ROOT / "outputs" / "panel"
OUT = ROOT / "outputs" / "discovery"
GROUPS = ["DL", "WR", "TE", "OL"]  # DB/LB weekly samples are too thin/unidentifiable
MIN_WEEKLY_PLAYS = 5


def _weekly_performance() -> pd.DataFrame:
    frames = []
    for group in GROUPS:
        path = WEEKLY / f"weekly_{group}.parquet"
        if not path.exists():
            continue
        d = pd.read_parquet(path)
        d = d[d["weekly_n"] >= MIN_WEEKLY_PLAYS].copy()
        frames.append(d[["nfl_id", "season", "week", "weekly_mean", "weekly_n", "group"]])
    return pd.concat(frames, ignore_index=True)


def build_panel() -> pd.DataFrame:
    weekly = _weekly_performance()
    plays = load.load_player_play(usecols=["nfl_id", "game_id", "team_abbr"])
    games = load.load_games()[["game_id", "season", "week", "season_type"]]
    plays = plays.merge(games, on="game_id", how="left")
    plays = plays[(plays["season_type"] == "REG") & plays["nfl_id"].notna() & plays["team_abbr"].notna()].copy()

    counts = (
        plays.groupby(["nfl_id", "season", "week", "team_abbr"], as_index=False)
        .size()
        .rename(columns={"size": "player_rows"})
    )
    team_total = (
        plays.groupby(["season", "week", "team_abbr"], as_index=False)
        .size()
        .rename(columns={"size": "team_rows"})
    )
    counts = counts.merge(team_total, on=["season", "week", "team_abbr"], how="left")
    counts["role_share_week"] = counts["player_rows"] / counts["team_rows"].replace(0, np.nan)

    d = counts.merge(weekly, on=["nfl_id", "season", "week"], how="inner")
    panel = pd.read_parquet(PANEL)[["nfl_id", "season", "position_group", "B_draft"]]
    panel = panel.drop_duplicates(["nfl_id", "season"])
    d = d.merge(panel, on=["nfl_id", "season"], how="left")
    d = d[d["position_group"].isin(GROUPS)].copy()

    # Relative role and performance within position-season-week.
    d["role_z"] = d.groupby(["position_group", "season", "week"])["role_share_week"].transform(
        lambda x: (x - x.mean()) / x.std(ddof=0) if x.std(ddof=0) > 0 else x * 0
    )
    d["perf_z"] = d.groupby(["group", "season", "week"])["weekly_mean"].transform(
        lambda x: (x - x.mean()) / x.std(ddof=0) if x.std(ddof=0) > 0 else x * 0
    )
    d = d.sort_values(["nfl_id", "season", "week"]).reset_index(drop=True)
    d["next_role_z"] = d.groupby(["nfl_id", "season"])["role_z"].shift(-1)
    d["next_week"] = d.groupby(["nfl_id", "season"])["week"].shift(-1)
    d["consecutive"] = d["next_week"].eq(d["week"] + 1)
    return d


def _fit(formula: str, data: pd.DataFrame) -> object:
    return smf.ols(formula, data=data).fit(
        cov_type="cluster", cov_kwds={"groups": data["nfl_id"]}
    )


def _rows(fit, model: str) -> list[dict]:
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
            }
        )
    return rows


def main() -> None:
    d = build_panel()
    lead = d[d["consecutive"] & d["next_role_z"].notna()].copy()
    lead = lead.dropna(subset=["role_z", "perf_z", "B_draft", "position_group", "season", "week"])
    f1 = _fit(
        "next_role_z ~ role_z + perf_z + B_draft + C(position_group) + C(season) + C(week)",
        lead,
    )

    early = (
        d[d["week"] <= 6]
        .groupby(["nfl_id", "season"], as_index=False)
        .agg(early_role_z=("role_z", "mean"), early_perf_z=("perf_z", "mean"), n_early=("week", "nunique"))
    )
    late = (
        d[d["week"] >= 7]
        .groupby(["nfl_id", "season"], as_index=False)
        .agg(late_role_z=("role_z", "mean"), n_late=("week", "nunique"))
    )
    split = early.merge(late, on=["nfl_id", "season"], how="inner")
    split = split[(split["n_early"] >= 3) & (split["n_late"] >= 3)].copy()
    split = split.merge(
        d[["nfl_id", "season", "position_group", "B_draft"]].drop_duplicates(["nfl_id", "season"]),
        on=["nfl_id", "season"],
        how="left",
    )
    split = split.dropna(subset=["early_role_z", "early_perf_z", "late_role_z", "B_draft", "position_group"])
    f2 = _fit(
        "late_role_z ~ early_role_z + early_perf_z + B_draft + C(position_group) + C(season)",
        split,
    )

    rows = _rows(f1, "weekly_lead_lag") + _rows(f2, "early_late")
    out = pd.DataFrame(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT / "weekly_role.csv", index=False)
    lead.to_parquet(OUT / "weekly_role_panel.parquet", index=False)

    print(f"weekly lead-lag rows: {len(lead)}; players: {lead['nfl_id'].nunique()}")
    print(f"early/late rows: {len(split)}; players: {split['nfl_id'].nunique()}")
    print("\nWeekly lead-lag (next-week role):")
    print(out.query("model == 'weekly_lead_lag'")[["term", "coef", "ci_low", "ci_high", "p", "n"]].round(3).to_string(index=False))
    print("\nEarly -> late role:")
    print(out.query("model == 'early_late'")[["term", "coef", "ci_low", "ci_high", "p", "n"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
