"""Position-specific regular-season performance residuals for the full audit.

DL: get-off (oriented negative = faster better).
WR/TE: separation at pass forward (higher better).
OL: pressure allowed (oriented negative = less pressure better).
DB: allowed completion (oriented negative = fewer completions better; measurement check).
LB: get-off where available (descriptive).

Player-season and weekly empirical-Bayes residuals, plus temporal flip/dwell.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from data import load
from features import player_play as pp

ROOT = load.ROOT
OUT = ROOT / "outputs" / "panel"

GROUPS = {
    "DL": {"DE", "DT", "NT", "OLB"},
    "WR": {"WR"},
    "TE": {"TE"},
    "OL": {"T", "G", "C"},
    "DB": {"CB", "SS", "FS", "DB"},
    "LB": {"ILB", "MLB"},
}

CONTEXT_NUM = [
    "yards_to_go",
    "pass_length",
    "cushion",
    "dropback_duration",
    "pass_rushers_encountered",
    "yardline_number",
    "expected_points",
]
CONTEXT_CAT = [
    "route_ran",
    "team_coverage_man_zone",
    "team_coverage_type",
    "down",
    "in_motion_at_ball_snap",
    "blitzing",
    "coverage_assignment",
    "receiver_alignment",
    "season",
]

USECOLS = [
    "nfl_id",
    "game_id",
    "play_id",
    "separation_at_pass_forward",
    "pressure_allowed",
    "pass_result",
    "player_get_off",
    "route_ran",
    "team_coverage_man_zone",
    "team_coverage_type",
    "cushion",
    "down",
    "yards_to_go",
    "pass_length",
    "in_motion_at_ball_snap",
    "blitzing",
    "pass_rushers_encountered",
    "dropback_duration",
    "coverage_assignment",
    "receiver_alignment",
    "yardline_number",
    "expected_points",
]


def _outcome(group: str, df: pd.DataFrame) -> pd.Series:
    if group == "DL":
        return -df["player_get_off"].astype(float)
    if group in {"WR", "TE"}:
        return df["separation_at_pass_forward"]
    if group == "OL":
        return -df["pressure_allowed"].astype(float)
    if group == "DB":
        return -df["pass_result"].map({"C": 1.0, "I": 0.0, "IN": 0.0})
    if group == "LB":
        return -df["player_get_off"].astype(float)
    return pd.Series(np.nan, index=df.index)


def _model() -> Pipeline:
    num = Pipeline(
        [("imp", SimpleImputer(strategy="median", add_indicator=True)), ("sc", StandardScaler())]
    )
    cat = Pipeline(
        [
            ("imp", SimpleImputer(strategy="most_frequent")),
            ("oh", OneHotEncoder(handle_unknown="ignore", sparse_output=True)),
        ]
    )
    pre = ColumnTransformer(
        [("num", num, CONTEXT_NUM), ("cat", cat, CONTEXT_CAT)],
        sparse_threshold=1.0,
    )
    return Pipeline([("pre", pre), ("ridge", Ridge(alpha=1.0))])


def _flip_dwell(weekly: pd.DataFrame) -> pd.DataFrame:
    return pp.flip_dwell(weekly)


def group_residuals(group: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    players = load.load_players()
    ids = set(players.loc[players["nfl_position"].isin(GROUPS[group]), "nfl_id"])
    df = load.load_player_play(usecols=USECOLS)
    games = load.load_games()[["game_id", "season", "week", "season_type"]]
    df = df.merge(games, on="game_id", how="left")
    df = df[(df["season_type"] == "REG") & df["nfl_id"].isin(ids)].copy()
    df["y"] = _outcome(group, df)
    df = df.dropna(subset=["y"])
    if len(df) < 50:
        return pd.DataFrame(), pd.DataFrame()
    X = df[CONTEXT_NUM + CONTEXT_CAT]
    y = df["y"].to_numpy()
    groups = df["nfl_id"].to_numpy()
    residual = np.full(len(df), np.nan)
    for train_idx, test_idx in GroupKFold(5).split(X, y, groups):
        model = _model().fit(X.iloc[train_idx], y[train_idx])
        residual[test_idx] = y[test_idx] - model.predict(X.iloc[test_idx])
    df["residual"] = residual

    season = (
        df.groupby(["nfl_id", "season"])["residual"]
        .agg(raw_mean="mean", n_plays="count", within_var="var")
        .reset_index()
    )
    season["within_var"] = season["within_var"].fillna(0.0)
    noise = season["within_var"] / season["n_plays"]
    tau2 = max(float(season["raw_mean"].var(ddof=0) - noise.mean()), 0.0)
    season["shrunk_mean"] = (
        season["raw_mean"] * tau2 / (tau2 + noise) if tau2 > 0 else 0.0
    )
    season["tau2"] = tau2
    season["group"] = group

    weekly = (
        df.groupby(["nfl_id", "season", "week"])
        .agg(weekly_mean=("residual", "mean"), weekly_n=("residual", "size"))
        .reset_index()
    )
    if len(weekly):
        fd = _flip_dwell(weekly)
        weekly = weekly.merge(fd, on=["nfl_id", "season"], how="left")
        weekly["group"] = group
    return season, weekly


def build_all() -> dict[str, tuple[pd.DataFrame, pd.DataFrame]]:
    OUT.mkdir(parents=True, exist_ok=True)
    out = {}
    for group in GROUPS:
        season, weekly = group_residuals(group)
        if len(season):
            season.to_parquet(OUT / f"perf_{group}.parquet", index=False)
            weekly.to_parquet(OUT / f"weekly_{group}.parquet", index=False)
            print(group, "player-seasons", len(season), "weekly rows", len(weekly))
        out[group] = (season, weekly)
    return out


if __name__ == "__main__":
    build_all()
