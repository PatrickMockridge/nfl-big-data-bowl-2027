"""Player performance residuals and team performance from nflverse.

Player performance is position-specific and standardized within position group
and season. Team offense is passing EPA plus rushing EPA from weekly player
stats (receiving EPA is the receiver-side view of the same pass plays and is
not added, to avoid double counting). Wins and point differential come from
the game file.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .common import EXTERNAL, OUT, ensure_dirs, normalize_team, stats_group

SEASONS = (2023, 2024, 2025)
MIN_Q = 100
MIN_RB_TOUCHES = 50
MIN_TARGETS = 30
MIN_DEF_GAMES = 8


def load_player_stats() -> pd.DataFrame:
    frames = []
    for season in SEASONS:
        df = pd.read_csv(EXTERNAL / f"stats_player_reg_{season}.csv")
        df = df[df["season_type"] == "REG"].copy()
        df["recent_team"] = normalize_team(df["recent_team"])
        df["group"] = stats_group(df["position_group"], df["position"])
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def _z(s: pd.Series) -> pd.Series:
    sd = s.std(ddof=0)
    return (s - s.mean()) / sd if sd and not np.isnan(sd) else s * 0.0


def player_performance() -> pd.DataFrame:
    df = load_player_stats()
    rows = []
    for (season, group), g in df.groupby(["season", "group"]):
        g = g.copy()
        if group == "QB":
            g["perf_n"] = g["attempts"].fillna(0) + g["sacks_suffered"].fillna(0)
            g["perf_rate"] = g["passing_epa"] / g["perf_n"].replace(0, np.nan)
            g.loc[g["perf_n"] < MIN_Q, "perf_rate"] = np.nan
            g["perf_metric"] = "passing EPA per dropback"
        elif group == "RB":
            g["perf_n"] = g["carries"].fillna(0) + g["targets"].fillna(0)
            g["perf_rate"] = (g["rushing_epa"].fillna(0) + g["receiving_epa"].fillna(0)) / g["perf_n"].replace(0, np.nan)
            g.loc[g["perf_n"] < MIN_RB_TOUCHES, "perf_rate"] = np.nan
            g["perf_metric"] = "rushing + receiving EPA per touch"
        elif group in ("WR", "TE"):
            g["perf_n"] = g["targets"].fillna(0)
            g["perf_rate"] = g["receiving_epa"] / g["perf_n"].replace(0, np.nan)
            g.loc[g["perf_n"] < MIN_TARGETS, "perf_rate"] = np.nan
            g["perf_metric"] = "receiving EPA per target"
        elif group in ("EDGE", "IDL"):
            g["perf_n"] = g["games"]
            comps = {
                "sacks": g["def_sacks"] / g["games"].replace(0, np.nan),
                "qb_hits": g["def_qb_hits"] / g["games"].replace(0, np.nan),
                "tfl": g["def_tackles_for_loss"] / g["games"].replace(0, np.nan),
                "tackles": (g["def_tackles_solo"] + 0.5 * g["def_tackles_with_assist"]) / g["games"].replace(0, np.nan),
            }
            z = pd.concat([_z(v).rename(k) for k, v in comps.items()], axis=1)
            g["perf_rate"] = z.mean(axis=1, skipna=True)
            g.loc[g["perf_n"] < MIN_DEF_GAMES, "perf_rate"] = np.nan
            g["perf_metric"] = "sacks/QB hits/TFL/tackles per game (composite z)"
        elif group == "LB":
            g["perf_n"] = g["games"]
            comps = {
                "tackles": (g["def_tackles_solo"] + 0.5 * g["def_tackles_with_assist"]) / g["games"].replace(0, np.nan),
                "tfl": g["def_tackles_for_loss"] / g["games"].replace(0, np.nan),
                "sacks": g["def_sacks"] / g["games"].replace(0, np.nan),
                "qb_hits": g["def_qb_hits"] / g["games"].replace(0, np.nan),
                "ints": g["def_interceptions"] / g["games"].replace(0, np.nan),
                "pds": g["def_pass_defended"] / g["games"].replace(0, np.nan),
            }
            z = pd.concat([_z(v).rename(k) for k, v in comps.items()], axis=1)
            g["perf_rate"] = z.mean(axis=1, skipna=True)
            g.loc[g["perf_n"] < MIN_DEF_GAMES, "perf_rate"] = np.nan
            g["perf_metric"] = "tackles/TFL/sacks/QB hits/INT/PD per game (composite z)"
        elif group in ("S", "CB"):
            g["perf_n"] = g["games"]
            comps = {
                "ints": g["def_interceptions"] / g["games"].replace(0, np.nan),
                "pds": g["def_pass_defended"] / g["games"].replace(0, np.nan),
                "tackles": (g["def_tackles_solo"] + 0.5 * g["def_tackles_with_assist"]) / g["games"].replace(0, np.nan),
            }
            z = pd.concat([_z(v).rename(k) for k, v in comps.items()], axis=1)
            g["perf_rate"] = z.mean(axis=1, skipna=True)
            g.loc[g["perf_n"] < MIN_DEF_GAMES, "perf_rate"] = np.nan
            g["perf_metric"] = "INT/PD/tackles per game (composite z)"
        elif group == "OL":
            g["perf_n"] = g["games"]
            g["perf_rate"] = np.nan
            g["perf_metric"] = "no individual measure"
        else:
            continue
        g["perf_z"] = _z(g["perf_rate"]) if g["perf_rate"].notna().sum() > 1 else np.nan
        rows.append(g)
    out = pd.concat(rows, ignore_index=True)
    out["name_key"] = (
        out["player_display_name"].astype("string").str.lower().str.strip()
    )
    keep = [
        "player_id", "player_name", "player_display_name", "name_key", "position", "position_group",
        "group", "recent_team", "season", "games", "perf_n", "perf_rate", "perf_z", "perf_metric",
        "passing_epa", "rushing_epa", "receiving_epa", "attempts", "carries", "targets",
        "def_sacks", "def_qb_hits", "def_tackles_for_loss", "def_tackles_solo",
        "def_tackles_with_assist", "def_interceptions", "def_pass_defended",
    ]
    out = out[[c for c in keep if c in out.columns]].copy()
    return out


def team_performance() -> pd.DataFrame:
    # Offensive EPA by team-week, so traded players are attributed to the team
    # they played for that week.
    frames = []
    for season in SEASONS:
        df = pd.read_csv(
            EXTERNAL / f"stats_player_week_{season}.csv",
            usecols=["season", "week", "season_type", "team", "passing_epa", "rushing_epa", "attempts", "sacks_suffered", "carries"],
        )
        df = df[(df["season_type"] == "REG") & (df["season"] == season)].copy()
        df["team"] = normalize_team(df["team"])
        frames.append(df)
    wk = pd.concat(frames, ignore_index=True)
    wk["off_epa"] = wk["passing_epa"].fillna(0) + wk["rushing_epa"].fillna(0)
    wk["off_plays"] = wk["attempts"].fillna(0) + wk["sacks_suffered"].fillna(0) + wk["carries"].fillna(0)
    epa = (
        wk.groupby(["season", "team"], as_index=False)
        .agg(off_epa=("off_epa", "sum"), off_plays=("off_plays", "sum"))
    )
    epa["off_epa_per_play"] = epa["off_epa"] / epa["off_plays"].replace(0, np.nan)

    games = pd.read_csv(EXTERNAL / "games.csv", usecols=["season", "game_type", "week", "home_team", "away_team", "home_score", "away_score"])
    games = games[(games["game_type"] == "REG") & games["season"].isin(SEASONS)].copy()
    games["home_team"] = normalize_team(games["home_team"])
    games["away_team"] = normalize_team(games["away_team"])
    long = pd.concat(
        [
            games.rename(columns={"home_team": "team", "away_team": "opponent", "home_score": "points_for", "away_score": "points_against"})[
                ["season", "team", "opponent", "points_for", "points_against"]
            ],
            games.rename(columns={"away_team": "team", "home_team": "opponent", "away_score": "points_for", "home_score": "points_against"})[
                ["season", "team", "opponent", "points_for", "points_against"]
            ],
        ],
        ignore_index=True,
    )
    long["win"] = np.select(
        [long["points_for"] > long["points_against"], long["points_for"] < long["points_against"]],
        [1.0, 0.0],
        default=0.5,
    )
    long["point_diff"] = long["points_for"] - long["points_against"]
    team = (
        long.groupby(["season", "team"], as_index=False)
        .agg(games=("win", "size"), wins=("win", "sum"), points_for=("points_for", "sum"),
             points_against=("points_against", "sum"), point_diff=("point_diff", "sum"))
    )
    team = team.merge(epa, on=["season", "team"], how="left")
    return team


def build() -> tuple[pd.DataFrame, pd.DataFrame]:
    player = player_performance()
    team = team_performance()
    ensure_dirs()
    player.to_csv(OUT / "player_performance.csv", index=False)
    team.to_csv(OUT / "team_performance.csv", index=False)
    return player, team


def main() -> None:
    player, team = build()
    print(f"player rows: {len(player)}; team rows: {len(team)}")
    print(player.groupby("group")["perf_z"].agg(["count", "mean", "std"]).round(2).to_string())
    print(team.groupby("season")[["wins", "point_diff", "off_epa"]].mean().round(1).to_string())


if __name__ == "__main__":
    main()
