"""Regular-season player-season panel for the broadened Yellow Square analysis.

One row per (nfl_id, season). Regular season is primary; preseason/postseason are
excluded. Team abbreviations are normalized in ``data.load`` (LA -> LAR).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata

from data import load
from features import player_play as pp

ROOT = load.ROOT
OUT = ROOT / "outputs" / "panel"
KEYS = ["nfl_id", "season"]

TIER1 = {
    "Southeastern Conference",
    "Big Ten Conference",
    "Atlantic Coast Conference",
    "Big Twelve Conference",
    "Pacific Twelve Conference",
}
TIER2 = {
    "American Athletic Conference",
    "Mountain West Conference",
    "Sun Belt Conference",
    "Mid-American Conference",
    "Conference USA",
    "Independent",
    "Missouri Valley Football Conference",
}


def _mode(series: pd.Series):
    mode = series.mode()
    return mode.iloc[0] if len(mode) else np.nan


def _entropy(counts: pd.Series) -> float:
    values = counts[counts > 0].to_numpy(dtype=float)
    probs = values / values.sum()
    return float(-(probs * np.log(probs)).sum()) if len(probs) > 1 else 0.0


def _z(series: pd.Series) -> pd.Series:
    std = series.std(ddof=0)
    return (series - series.mean()) / std if std > 0 else series * 0


def _percentile(series: pd.Series) -> pd.Series:
    return series.rank(pct=True, method="average")


def _b_draft(players: pd.DataFrame) -> pd.Series:
    out = pd.Series(0.0, index=players.index)
    for (year, group), idx in players.groupby(["draft_year", "position_subgroup"]).groups.items():
        sub = players.loc[idx]
        picks = sub["draft_overall_pick"]
        rank = picks.rank(method="average", ascending=False)
        out.loc[idx] = (rank - 1) / max(len(sub) - 1, 1)
        out.loc[sub.index[picks.isna()]] = 0.0
    return out.clip(0, 1)


def _conference_tier(name: str) -> int:
    if name in TIER1:
        return 1
    if name in TIER2:
        return 2
    return 3


def base_panel() -> pd.DataFrame:
    players = load.load_players()
    combine = load.load_combine_results()
    games = load.load_games()[["game_id", "season", "week", "season_type"]]
    pp_df = load.load_player_play(
        usecols=[
            "game_id",
            "play_id",
            "team_abbr",
            "nfl_id",
            "lined_up_position",
            "possession_team",
            "player_get_off",
            "pressure_allowed",
            "coverage_assignment",
            "route_ran",
            "target",
            "separation_at_pass_forward",
            "quick_pressure",
            "sack",
            "blitzing",
            "team_coverage_man_zone",
        ]
    )
    pp_df = pp_df.merge(games, on="game_id", how="left")
    pp_df = pp_df[(pp_df["season_type"] == "REG") & pp_df["nfl_id"].isin(players["nfl_id"])].copy()
    pp_df["nfl_position"] = pp_df["nfl_id"].map(players.set_index("nfl_id")["nfl_position"])
    pp_df["position_group"] = pp_df["nfl_id"].map(players.set_index("nfl_id")["position_group"])
    pp_df["draft_year"] = pp_df["nfl_id"].map(players.set_index("nfl_id")["draft_year"])
    pp_df["position_subgroup"] = np.where(
        pp_df["nfl_position"].isin(["DE", "OLB"]),
        "EDGE",
        np.where(pp_df["nfl_position"].isin(["DT", "NT"]), "INTERIOR", pp_df["position_group"]),
    )
    pp_df["is_defense"] = pp_df["team_abbr"] != pp_df["possession_team"]

    team_counts = (
        pp_df.groupby(["nfl_id", "season", "team_abbr"])
        .agg(team_snaps=("game_id", "size"))
        .reset_index()
    )
    n_teams = (
        team_counts.groupby(KEYS)["team_abbr"].nunique().rename("n_teams").reset_index()
    )
    primary = (
        team_counts.sort_values("team_snaps")
        .drop_duplicates(KEYS, keep="last")[["nfl_id", "season", "team_abbr", "team_snaps"]]
        .rename(columns={"team_abbr": "primary_team"})
    )

    ps = (
        pp_df.groupby(KEYS)
        .agg(
            snaps=("game_id", "size"),
            games=("game_id", "nunique"),
            weeks=("week", "nunique"),
            def_plays=("is_defense", "sum"),
            off_plays=("is_defense", lambda x: int((~x).sum())),
            primary_role=("lined_up_position", _mode),
            n_roles=("lined_up_position", "nunique"),
            pass_rush_plays=("player_get_off", lambda x: int(x.notna().sum())),
            pass_block_plays=("pressure_allowed", lambda x: int(x.notna().sum())),
            coverage_plays=("coverage_assignment", lambda x: int(x.notna().sum())),
            routes=("route_ran", lambda x: int(x.notna().sum())),
            targets=("target", "sum"),
            separation_obs=("separation_at_pass_forward", lambda x: int(x.notna().sum())),
            getoff_obs=("player_get_off", lambda x: int(x.notna().sum())),
            pressure_obs=("pressure_allowed", lambda x: int(x.notna().sum())),
            man_share=("team_coverage_man_zone", lambda x: float((x == "MAN_COVERAGE").mean())),
            zone_share=("team_coverage_man_zone", lambda x: float((x == "ZONE_COVERAGE").mean())),
            blitz_share=("blitzing", "mean"),
            quick_pressure_rate=("quick_pressure", "mean"),
            sack_rate=("sack", "mean"),
        )
        .reset_index()
    )
    role_counts = (
        pp_df.groupby(KEYS + ["lined_up_position"]).size().reset_index(name="n")
    )
    role_entropy = (
        role_counts.groupby(KEYS)["n"].apply(_entropy).rename("role_entropy").reset_index()
    )
    ps = ps.merge(role_entropy, on=KEYS).merge(primary, on=KEYS).merge(n_teams, on=KEYS)

    # Team/position room: cohort players only.
    pp_df = pp_df.merge(primary[["nfl_id", "season", "primary_team"]], on=KEYS, how="left")
    room = (
        pp_df.groupby(["season", "primary_team", "position_group", "nfl_id"])
        .size()
        .reset_index(name="room_snaps")
    )
    room_total = (
        room.groupby(["season", "primary_team", "position_group"])["room_snaps"]
        .sum()
        .rename("team_position_snaps")
        .reset_index()
    )
    room = room.merge(room_total, on=["season", "primary_team", "position_group"], how="left")
    room["role_share_room"] = room["room_snaps"] / room["team_position_snaps"]
    ps = ps.merge(
        room[["nfl_id", "season", "role_share_room", "team_position_snaps"]],
        on=KEYS,
        how="left",
    )

    # Static player/Combine/college context.
    players = players.merge(
        combine[
            [
                "nfl_id",
                "ngs_athleticism_score",
                "ngs_college_production_score",
                "ngs_final_score",
                "combine_height",
                "combine_weight",
                "arm_length",
                "hand_size",
                "wing_span",
                "ten_yd_split",
                "forty",
                "vertical",
                "broad_jump",
                "three_cone",
                "short_shuttle",
                "bench_reps",
            ]
        ],
        on="nfl_id",
        how="left",
    )
    players["position_subgroup"] = np.where(
        players["nfl_position"].isin(["DE", "OLB"]),
        "EDGE",
        np.where(players["nfl_position"].isin(["DT", "NT"]), "INTERIOR", players["position_group"]),
    )
    players["B_draft"] = _b_draft(players)
    players["conf_tier"] = players["college_conference"].map(_conference_tier).fillna(3).astype(int)
    # Conference strength: mean B_draft of drafted peers, leave-one-out.
    conf = (
        players.groupby(["college_conference", "draft_year"])["B_draft"]
        .agg(["sum", "count"])
        .reset_index()
        .rename(columns={"sum": "conf_sum", "count": "conf_n"})
    )
    players = players.merge(conf, on=["college_conference", "draft_year"], how="left")
    players["conf_strength"] = (players["conf_sum"] - players["B_draft"]) / (
        players["conf_n"] - 1
    ).replace(0, np.nan)
    program = (
        players.groupby(["college_name", "draft_year"])["B_draft"]
        .agg(["sum", "count"])
        .reset_index()
        .rename(columns={"sum": "prog_sum", "count": "prog_n"})
    )
    players = players.merge(program, on=["college_name", "draft_year"], how="left")
    players["program_strength"] = (players["prog_sum"] - players["B_draft"]) / (
        players["prog_n"] - 1
    ).replace(0, np.nan)
    for col in ["ngs_college_production_score", "ngs_athleticism_score"]:
        players[f"{col}_pct"] = players.groupby(["conf_tier", "draft_year"])[col].rank(pct=True)
    players["college_dominance"] = players[
        ["ngs_college_production_score_pct", "ngs_athleticism_score_pct"]
    ].mean(axis=1)
    players["big_fish"] = players["college_dominance"] >= players["college_dominance"].quantile(2 / 3)
    players["small_pond"] = players["conf_tier"] > 1
    players["big_fish_small_pond"] = players["big_fish"] & players["small_pond"]
    players["pond_mismatch"] = _z(players["college_dominance"]) - _z(players["conf_strength"])
    players["prestige"] = players[
        ["B_draft", "ngs_final_score", "ngs_college_production_score"]
    ].apply(_z).mean(axis=1)

    static_cols = [
        "nfl_id",
        "display_name",
        "draft_year",
        "nfl_position",
        "position_group",
        "position_subgroup",
        "college_name",
        "college_conference",
        "conf_tier",
        "B_draft",
        "conf_strength",
        "program_strength",
        "college_dominance",
        "big_fish",
        "small_pond",
        "big_fish_small_pond",
        "pond_mismatch",
        "prestige",
        "ngs_final_score",
        "ngs_college_production_score",
        "ngs_athleticism_score",
        "ten_yd_split",
        "forty",
        "three_cone",
        "short_shuttle",
        "vertical",
        "broad_jump",
        "bench_reps",
        "combine_height",
        "combine_weight",
        "arm_length",
        "hand_size",
        "wing_span",
    ]
    ps = ps.merge(players[static_cols], on="nfl_id", how="left")
    return ps


def dl_performance() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    plays = pp.dl_plays(rookie_only=False, season_type="REG")
    plays["context_residual"] = pp.cross_fitted_residuals(plays)
    season = pp.player_season_outcomes(plays)
    weekly = pp.weekly_residuals(plays)
    fd = pp.flip_dwell(weekly)
    return season, weekly, fd


def nfl_pond(panel: pd.DataFrame) -> pd.DataFrame:
    d = panel[panel["position_group"] == "DL"].copy()
    # Prior-season teammate performance, shifted so season t sees season t-1 only.
    prior = d[["nfl_id", "season", "getoff_shrunk"]].copy()
    prior["season"] = prior["season"] + 1
    prior = prior.rename(columns={"getoff_shrunk": "prior_getoff"})
    d = d.merge(prior, on=["nfl_id", "season"], how="left")
    rows = []
    for (season, team), sub in d.groupby(["season", "primary_team"]):
        for idx, row in sub.iterrows():
            others = sub[sub["nfl_id"] != row["nfl_id"]]
            rows.append(
                {
                    "nfl_id": row["nfl_id"],
                    "season": season,
                    "team_dl_n": len(others),
                    "team_dl_draft_strength": others["B_draft"].mean() if len(others) else np.nan,
                    "team_dl_prior_resid": others["prior_getoff"].mean()
                    if len(others)
                    else np.nan,
                    "pond_rank": float(
                        rankdata(-sub["B_draft"], method="average")[
                            list(sub.index).index(idx)
                        ]
                    ),
                }
            )
    out = pd.DataFrame(rows)
    parts = []
    for col in ["team_dl_n", "team_dl_draft_strength", "team_dl_prior_resid"]:
        parts.append(_z(out[col]).fillna(0))
    out["team_dl_competition"] = pd.concat(parts, axis=1).mean(axis=1)
    out["pond_size"] = out["team_dl_n"] + 1
    return out


def add_transitions(panel: pd.DataFrame) -> pd.DataFrame:
    d = panel.sort_values(["nfl_id", "season"]).copy()
    group = d.groupby("nfl_id")
    d["prev_season"] = group["season"].shift()
    d["prev_team"] = group["primary_team"].shift()
    d["prev_role"] = group["primary_role"].shift()
    d["prev_role_share"] = group["role_share_room"].shift()
    d["prev_getoff"] = group["getoff_shrunk"].shift()
    d["prev_competition"] = group["team_dl_competition"].shift()
    d["team_change"] = (
        d["primary_team"].ne(d["prev_team"])
        & d["prev_team"].notna()
        & (d["season"] == d["prev_season"] + 1)
    )
    d["midseason_move"] = d["n_teams"] > 1
    d["role_label_change"] = d["primary_role"].ne(d["prev_role"]) & d["prev_role"].notna()
    d["role_share_change"] = d["role_share_room"] - d["prev_role_share"]
    d["pond_upgrade"] = d["team_dl_competition"] - d["prev_competition"]
    d["setup_change"] = d["team_change"] | d["midseason_move"]
    d["delta_getoff"] = d["getoff_shrunk"] - d["prev_getoff"]
    return d


def build() -> dict[str, pd.DataFrame]:
    panel = base_panel()
    season, weekly, fd = dl_performance()
    panel = panel.merge(
        season[["nfl_id", "season", "raw_mean", "n_plays", "within_var", "shrunk_mean"]],
        on=KEYS,
        how="left",
    ).rename(
        columns={
            "raw_mean": "getoff_raw",
            "n_plays": "getoff_n",
            "within_var": "getoff_within_var",
            "shrunk_mean": "getoff_shrunk",
        }
    )
    panel = panel.merge(
        fd[["nfl_id", "season", "flip_rate", "dwell", "weekly_sd"]].rename(
            columns={
                "flip_rate": "weekly_flip_rate",
                "dwell": "weekly_dwell",
                "weekly_sd": "weekly_sd",
            }
        ),
        on=KEYS,
        how="left",
    )
    pond = nfl_pond(panel)
    panel = panel.merge(pond, on=KEYS, how="left")
    panel = add_transitions(panel)
    panel["perf_pct"] = panel.groupby(["position_subgroup", "season"])[
        "getoff_shrunk"
    ].rank(pct=True)
    return {"player_season": panel, "weekly": weekly, "transitions": panel[panel["team_change"] | panel["midseason_move"] | panel["role_label_change"]]}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    tables = build()
    panel = tables["player_season"]
    panel.to_parquet(OUT / "player_season.parquet", index=False)
    tables["weekly"].to_parquet(OUT / "weekly.parquet", index=False)
    tables["transitions"].to_parquet(OUT / "transitions.parquet", index=False)
    panel[panel["position_group"] == "DL"].to_parquet(OUT / "dl_player_season.parquet", index=False)
    manifest = {
        "rows": len(panel),
        "players": int(panel["nfl_id"].nunique()),
        "dl_rows": int((panel["position_group"] == "DL").sum()),
        "dl_players": int(panel.loc[panel["position_group"] == "DL", "nfl_id"].nunique()),
        "regular_season_only": True,
        "team_abbr_fix": load.TEAM_ABBR_FIX,
        "team_changes": int(panel["team_change"].sum()),
        "midseason_moves": int(panel["midseason_move"].sum()),
        "role_label_changes": int(panel["role_label_change"].sum()),
        "columns": list(panel.columns),
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(json.dumps({k: v for k, v in manifest.items() if k != "columns"}, indent=2))


if __name__ == "__main__":
    main()
