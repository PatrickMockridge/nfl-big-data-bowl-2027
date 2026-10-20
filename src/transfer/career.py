"""Career reward ladder: the BDB-native reward proxy.

Career starts, snaps, and awards are cumulative and mechanically related to
role. This is a descriptive reward-legibility ladder, not a pricing model.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from data import load
from features.panel import _b_draft
from transfer.common import POSITIONS, load_panel, load_role_panel, position_subgroup, save

OUTCOMES = {
    "career_start_rate": "starts / active games",
    "career_snaps_per_game": "career snaps / active game",
}


def build_player_table() -> pd.DataFrame:
    players = load.load_players().copy()
    players["position_subgroup"] = position_subgroup(players)
    players["B_draft"] = _b_draft(players)
    career = load.load_career()
    d = players.merge(career, on="nfl_id", how="left")
    career_cols = [
        "career_offensive_snaps",
        "career_defensive_snaps",
        "career_special_teams_snaps",
        "career_games_active",
        "career_games_started",
    ]
    d[career_cols] = d[career_cols].fillna(0)
    # Never-active players are kept as zero-career rows rather than dropped,
    # so the draft ladder does not condition on surviving to a first game.
    active = d["career_games_active"].clip(lower=1)
    d["career_start_rate"] = d["career_games_started"] / active
    d["career_snaps_per_game"] = (
        d[["career_offensive_snaps", "career_defensive_snaps", "career_special_teams_snaps"]]
        .sum(axis=1)
        / active
    )
    d["award_any"] = (
        d[["ap_all_pro_1st_team", "ap_all_pro_2nd_team", "pro_bowl_original_ballot"]]
        .fillna(0)
        .sum(axis=1)
        .gt(0)
    )

    panel = load_panel()
    perf = (
        panel.groupby("nfl_id")
        .agg(mean_perf_z=("perf_z", "mean"), seasons=("season", "nunique"))
        .reset_index()
    )
    role = load_role_panel()
    role_mean = role.groupby("nfl_id").agg(mean_role_z=("role_z", "mean")).reset_index()
    d = d.merge(perf, on="nfl_id", how="left").merge(role_mean, on="nfl_id", how="left")
    d = d[d["position_group"].isin(POSITIONS)].copy()
    return d


def _fit(formula: str, data: pd.DataFrame, model: str, outcome: str) -> list[dict]:
    d = data.dropna(subset=[outcome])
    if len(d) < 10:
        return []
    fit = smf.ols(formula, data=d).fit(cov_type="HC1")
    rows = []
    for term in fit.params.index:
        if term == "Intercept" or term.startswith("C("):
            continue
        ci = fit.conf_int().loc[term]
        rows.append(
            {
                "model": model,
                "outcome": outcome,
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


def models(d: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for outcome in OUTCOMES:
        rows += _fit(
            f"{outcome} ~ B_draft + C(position_group)",
            d,
            "draft_only",
            outcome,
        )
        rows += _fit(
            f"{outcome} ~ B_draft + mean_perf_z + C(position_group)",
            d,
            "draft_plus_performance",
            outcome,
        )
        rows += _fit(
            f"{outcome} ~ B_draft + mean_perf_z + mean_role_z + C(position_group)",
            d,
            "draft_performance_role",
            outcome,
        )
    return pd.DataFrame(rows)


def _draft_quartile(series: pd.Series) -> pd.Series:
    """Rank-based quartiles: B_draft has a large tie at 0 (undrafted)."""
    labels = ["Q1 late/UDFA", "Q2", "Q3", "Q4 early"]
    ranks = series.rank(method="first")
    return pd.qcut(ranks, 4, labels=labels)


def ladder(d: pd.DataFrame) -> pd.DataFrame:
    d = d.copy()
    d["draft_q"] = _draft_quartile(d["B_draft"])
    rows = []
    for draft_q, cell in d.groupby("draft_q", observed=True):
        rows.append(
            {
                "draft_q": draft_q,
                "n": len(cell),
                "start_rate_mean": cell["career_start_rate"].mean(),
                "snaps_per_game_mean": cell["career_snaps_per_game"].mean(),
                "award_rate": cell["award_any"].mean(),
                "awards": int(cell["award_any"].sum()),
            }
        )
    return pd.DataFrame(rows)


def awards_by_tier(d: pd.DataFrame) -> pd.DataFrame:
    d = d.copy()
    d["draft_q"] = _draft_quartile(d["B_draft"])
    out = (
        d.groupby("draft_q", observed=True)
        .agg(
            n=("nfl_id", "size"),
            players_with_award=("award_any", "sum"),
            award_rate=("award_any", "mean"),
            all_pro_1st=("ap_all_pro_1st_team", "sum"),
            all_pro_2nd=("ap_all_pro_2nd_team", "sum"),
            pro_bowl=("pro_bowl_original_ballot", "sum"),
        )
        .reset_index()
    )
    return out


def main() -> None:
    d = build_player_table()
    table = models(d)
    save(table, "career_reward.csv")
    save(ladder(d), "career_ladder.csv")
    save(awards_by_tier(d), "career_awards_by_tier.csv")
    print(table.round(3).to_string(index=False))
    print()
    print(ladder(d).round(3).to_string(index=False))


if __name__ == "__main__":
    main()
