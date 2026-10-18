"""Merge the corrected panel with position-specific performance, dynamic state, and career."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from data import load

ROOT = load.ROOT
PANEL = ROOT / "outputs" / "panel"


def _z(series: pd.Series) -> pd.Series:
    std = series.std(ddof=0)
    return (series - series.mean()) / std if std > 0 else series * 0


def load_full_panel() -> pd.DataFrame:
    panel = pd.read_parquet(PANEL / "player_season.parquet")
    perfs = []
    for group in ["DL", "WR", "TE", "OL", "DB"]:
        path = PANEL / f"perf_{group}.parquet"
        if path.exists():
            perf = pd.read_parquet(path)
            perf["perf_group"] = group
            perfs.append(
                perf[["nfl_id", "season", "raw_mean", "n_plays", "within_var", "shrunk_mean", "perf_group"]]
            )
    if perfs:
        perf = pd.concat(perfs, ignore_index=True).rename(
            columns={
                "raw_mean": "perf_raw",
                "n_plays": "perf_n",
                "within_var": "perf_var",
                "shrunk_mean": "perf_shrunk",
            }
        )
        panel = panel.merge(perf, on=["nfl_id", "season"], how="left")
    else:
        panel["perf_raw"] = np.nan
        panel["perf_n"] = np.nan
        panel["perf_var"] = np.nan
        panel["perf_shrunk"] = np.nan
        panel["perf_group"] = np.nan
    panel["perf_z"] = panel.groupby(["position_group", "season"])["perf_shrunk"].transform(_z)

    dynamic_path = PANEL / "dynamic_state.parquet"
    if dynamic_path.exists():
        dyn = pd.read_parquet(dynamic_path)[
            [
                "nfl_id",
                "season",
                "A_t",
                "B_t",
                "C_abs",
                "square",
                "phi",
                "resilience",
                "mobius_continuous",
                "mobius_flag",
            ]
        ]
        panel = panel.merge(dyn, on=["nfl_id", "season"], how="left")
    panel["yellow"] = (panel.get("square") == "Yellow").astype(float)
    panel.loc[panel.get("square").isna(), "yellow"] = np.nan

    career = load.load_career()
    career["career_snaps"] = (
        career["career_offensive_snaps"]
        + career["career_defensive_snaps"]
        + career["career_special_teams_snaps"]
    )
    career["career_start_rate"] = career["career_games_started"] / career[
        "career_games_active"
    ].replace(0, np.nan)
    career["career_accolades"] = (
        career["ap_all_pro_1st_team"]
        + career["ap_all_pro_2nd_team"]
        + career["pro_bowl_original_ballot"]
    )
    panel = panel.merge(
        career[
            [
                "nfl_id",
                "career_snaps",
                "career_games_active",
                "career_games_started",
                "career_start_rate",
                "career_accolades",
            ]
        ],
        on="nfl_id",
        how="left",
    )
    panel["career_status_z"] = panel.groupby(["position_group", "draft_year"])[
        "career_snaps"
    ].transform(_z)
    # Draft-free prestige: NGS/college only, so it is not circular with the price.
    panel["prestige_nodraft"] = panel[
        ["ngs_final_score", "ngs_college_production_score"]
    ].apply(_z).mean(axis=1)
    return panel


def main() -> None:
    panel = load_full_panel()
    panel.to_parquet(PANEL / "panel_full.parquet", index=False)
    print("rows", len(panel), "players", panel["nfl_id"].nunique())
    print("perf non-null", panel["perf_shrunk"].notna().sum())
    print("career non-null", panel["career_snaps"].notna().sum())


if __name__ == "__main__":
    main()
