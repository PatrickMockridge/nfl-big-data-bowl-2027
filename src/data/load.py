"""Typed loaders for the NFL Big Data Bowl 2027 competition data.

Raw CSVs live behind the ``data/raw`` symlink created by ``scripts/01_download.py``.
Nothing here writes to the raw data.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterator, Sequence

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"

COMPETITION_COLUMNS = {
    "players": [
        "nfl_id",
        "display_name",
        "draft_year",
        "nfl_position",
        "birth_date",
        "college_name",
        "college_conference",
        "draft_round",
        "draft_pick_within_round",
        "draft_overall_pick",
    ],
    "combine_results": [
        "draft_year",
        "nfl_id",
        "combine_position",
        "combine_height",
        "combine_weight",
        "hand_size",
        "arm_length",
        "wing_span",
        "ten_yd_split",
        "forty",
        "vertical",
        "broad_jump",
        "three_cone",
        "short_shuttle",
        "bench_reps",
        "ngs_athleticism_score",
        "ngs_college_production_score",
        "ngs_final_score",
    ],
    "career": [
        "nfl_id",
        "career_offensive_snaps",
        "career_defensive_snaps",
        "career_special_teams_snaps",
        "career_games_active",
        "career_games_started",
        "ap_all_pro_1st_team",
        "ap_all_pro_2nd_team",
        "pro_bowl_original_ballot",
    ],
    "games": [
        "game_id",
        "game_key",
        "season",
        "season_type",
        "week",
        "home_team_abbr",
        "visitor_team_abbr",
    ],
    "combine_tracking": [
        "draft_year",
        "event_id",
        "nfl_id",
        "entity_type",
        "time",
        "drill_type",
        "drill_name",
        "attempt",
        "x",
        "y",
        "s",
        "a",
        "dis",
        "dir",
    ],
    "player_play": [
        "game_id",
        "play_id",
        "team_abbr",
        "nfl_id",
        "lined_up_position",
        "play_description",
        "quarter",
        "down",
        "yards_to_go",
        "possession_team",
        "yardline_side",
        "yardline_number",
        "game_clock",
        "pre_snap_home_score",
        "pre_snap_visitor_score",
        "play_direction",
        "pre_snap_home_team_win_probability",
        "pre_snap_visitor_team_win_probability",
        "home_team_win_probability_added",
        "visitor_team_win_probility_added",
        "expected_points_added",
        "expected_points",
        "offense_formation",
        "receiver_alignment",
        "pass_result",
        "pass_length",
        "play_nullified_by_penalty",
        "penalty_yards",
        "pre_penalty_yards_gained",
        "yards_gained",
        "team_coverage_man_zone",
        "team_coverage_type",
        "in_motion_at_ball_snap",
        "target",
        "rec_yards",
        "rush_yards",
        "yards_after_catch",
        "fumble",
        "fumble_lost",
        "route_ran",
        "separation_at_pass_forward",
        "cushion",
        "expected_yards_after_catch",
        "dropback_duration",
        "extended_sack_allowed",
        "pass_rushers_encountered",
        "peak_pressure_probability_allowed",
        "pressure_allowed",
        "sack_allowed",
        "time_to_pressure_allowed",
        "quick_pressure",
        "unblocked_pressure",
        "blitzing",
        "player_get_off",
        "sack",
        "tackle",
        "assist",
        "caused_forced_fumble",
        "recovered_fumble",
        "tackle_for_loss",
        "time_to_pressure",
        "time_to_qb_hurry",
        "coverage_assignment",
        "coverage_assignment_at_snap",
    ],
}

GAME_TRACKING_COLUMNS = [
    "game_id",
    "play_id",
    "nfl_id",
    "time",
    "x",
    "y",
    "s",
    "a",
    "dis",
    "o",
    "dir",
    "event",
]

FILE_NAMES = {
    "career": "player_career_successes",
}

TEAM_ABBR_FIX = {"LA": "LAR"}

POSITION_GROUP_MAP = {
    "WR": "WR",
    "TE": "TE",
    "CB": "DB",
    "SS": "DB",
    "FS": "DB",
    "DB": "DB",
    "T": "OL",
    "G": "OL",
    "C": "OL",
    "DE": "DL",
    "DT": "DL",
    "NT": "DL",
    "OLB": "DL",
    "ILB": "LB",
    "MLB": "LB",
}


def raw_dir() -> Path:
    """Return the directory containing the nine competition CSVs."""
    if not RAW_DIR.exists():
        raise FileNotFoundError(
            f"{RAW_DIR} is missing. Run `python scripts/01_download.py` first."
        )
    return RAW_DIR


def _read(name: str, usecols: Sequence[str] | None = None, **kwargs) -> pd.DataFrame:
    filename = FILE_NAMES.get(name, name)
    path = raw_dir() / f"{filename}.csv"
    cols = list(usecols) if usecols is not None else COMPETITION_COLUMNS.get(name)
    return pd.read_csv(path, usecols=cols, **kwargs)


def load_players() -> pd.DataFrame:
    df = _read("players")
    df["birth_date"] = pd.to_datetime(df["birth_date"], errors="coerce")
    df["position_group"] = df["nfl_position"].map(POSITION_GROUP_MAP).fillna("OTHER")
    return df


def load_combine_results() -> pd.DataFrame:
    return _read("combine_results")


def load_career() -> pd.DataFrame:
    return _read("career")


def load_games() -> pd.DataFrame:
    df = _read("games")
    for col in ["home_team_abbr", "visitor_team_abbr"]:
        df[col] = df[col].replace(TEAM_ABBR_FIX)
    return df


def load_combine_tracking(usecols: Sequence[str] | None = None) -> pd.DataFrame:
    df = _read("combine_tracking", usecols=usecols)
    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"], errors="coerce")
    return df


def load_player_play(usecols: Sequence[str] | None = None) -> pd.DataFrame:
    df = _read("player_play", usecols=usecols)
    if "team_abbr" in df.columns:
        df["team_abbr"] = df["team_abbr"].replace(TEAM_ABBR_FIX)
    if "possession_team" in df.columns:
        df["possession_team"] = df["possession_team"].replace(TEAM_ABBR_FIX)
    return df


def cohort() -> pd.DataFrame:
    """Players plus Combine result and career rows, one row per prospect."""
    players = load_players()
    combine = load_combine_results()
    career = load_career()
    return players.merge(combine, on=["nfl_id", "draft_year"], how="left").merge(
        career, on="nfl_id", how="left"
    )


def iter_game_tracking(
    year: int,
    usecols: Sequence[str] | None = None,
    chunksize: int = 500_000,
) -> Iterator[pd.DataFrame]:
    """Yield chunks from one season's 10 Hz game tracking file."""
    path = raw_dir() / f"game_tracking_{year}.csv"
    cols = list(usecols) if usecols is not None else GAME_TRACKING_COLUMNS
    yield from pd.read_csv(path, usecols=cols, chunksize=chunksize)
