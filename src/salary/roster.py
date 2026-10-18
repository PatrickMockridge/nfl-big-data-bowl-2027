"""Youth, rookie, and homegrown snap shares from nflverse snaps and players.

The unit is the player-team-season. A player traded mid-season contributes to
each team's share for the snaps he played there. Age is measured on 1 September
of the season; ``youth`` means age <= 24.

Attributes come from the nflverse master ``players.csv`` (pfr_id -> birth date,
rookie season, draft team), which matches 99.9% of snap-weighted player rows.
The weekly roster snapshots are not used because they are single-row snapshots
and miss players who finished the season on injured reserve.
"""

from __future__ import annotations

import pandas as pd

from .common import EXTERNAL, OUT, ensure_dirs, normalize_name, normalize_team, season_age

SNAP_FILES = {y: EXTERNAL / f"snap_counts_{y}.csv" for y in (2023, 2024, 2025)}
PLAYERS = EXTERNAL / "players.csv"


def load_snaps() -> pd.DataFrame:
    frames = []
    for season, path in SNAP_FILES.items():
        df = pd.read_csv(
            path,
            usecols=[
                "game_id",
                "season",
                "game_type",
                "week",
                "player",
                "pfr_player_id",
                "position",
                "team",
                "offense_snaps",
                "defense_snaps",
                "st_snaps",
            ],
        )
        df = df[df["game_type"] == "REG"].copy()
        df["team"] = normalize_team(df["team"])
        frames.append(df)
    snap = pd.concat(frames, ignore_index=True)
    for c in ["offense_snaps", "defense_snaps", "st_snaps"]:
        snap[c] = pd.to_numeric(snap[c], errors="coerce").fillna(0)
    snap["total_snaps"] = snap[["offense_snaps", "defense_snaps", "st_snaps"]].sum(axis=1)
    snap["name_key"] = normalize_name(snap["player"])

    agg = (
        snap.groupby(["season", "team", "pfr_player_id"], as_index=False)
        .agg(
            player=("player", "first"),
            name_key=("name_key", "first"),
            position=("position", "first"),
            games=("game_id", "nunique"),
            offense_snaps=("offense_snaps", "sum"),
            defense_snaps=("defense_snaps", "sum"),
            st_snaps=("st_snaps", "sum"),
            total_snaps=("total_snaps", "sum"),
        )
        .rename(columns={"pfr_player_id": "pfr_id"})
    )
    return agg


def load_players() -> pd.DataFrame:
    df = pd.read_csv(
        PLAYERS,
        usecols=[
            "gsis_id", "pfr_id", "display_name", "birth_date",
            "rookie_season", "draft_team", "draft_year", "draft_pick",
        ],
    )
    df = df.dropna(subset=["pfr_id"]).drop_duplicates("pfr_id").copy()
    df["draft_team"] = normalize_team(df["draft_team"])
    return df


def _attach_attributes(snaps: pd.DataFrame, players: pd.DataFrame) -> pd.DataFrame:
    out = snaps.merge(players, on="pfr_id", how="left", validate="many_to_one")
    out["matched"] = out["gsis_id"].notna()
    out["years_exp"] = out["season"] - pd.to_numeric(out["rookie_season"], errors="coerce")
    out["age_start"] = season_age(out["birth_date"], out["season"])
    out["youth"] = (out["age_start"] <= 24).fillna(False)
    out["rookie"] = out["years_exp"].eq(0).fillna(False)
    out["draft_club"] = out["draft_team"]
    out["homegrown"] = out["draft_club"].eq(out["team"]).fillna(False)
    return out


def team_shares(player: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (season, team), g in player.groupby(["season", "team"]):
        total = g["total_snaps"].sum()
        age_known = g["age_start"].notna()
        rows.append(
            {
                "season": season,
                "team": team,
                "team_total_snaps": total,
                "team_off_snaps": g["offense_snaps"].sum(),
                "team_def_snaps": g["defense_snaps"].sum(),
                "team_st_snaps": g["st_snaps"].sum(),
                "roster_match_share": g.loc[g["matched"], "total_snaps"].sum() / total if total else float("nan"),
                "age_known_snap_share": g.loc[age_known, "total_snaps"].sum() / total if total else float("nan"),
                "draft_known_snap_share": g.loc[g["draft_club"].notna(), "total_snaps"].sum() / total if total else float("nan"),
                "youth_snap_share": g.loc[g["youth"], "total_snaps"].sum() / g.loc[age_known, "total_snaps"].sum()
                if g.loc[age_known, "total_snaps"].sum() else float("nan"),
                "youth_snap_share_off": g.loc[g["youth"], "offense_snaps"].sum() / g.loc[age_known, "offense_snaps"].sum()
                if g.loc[age_known, "offense_snaps"].sum() else float("nan"),
                "youth_snap_share_def": g.loc[g["youth"], "defense_snaps"].sum() / g.loc[age_known, "defense_snaps"].sum()
                if g.loc[age_known, "defense_snaps"].sum() else float("nan"),
                "youth_snap_share_st": g.loc[g["youth"], "st_snaps"].sum() / g.loc[age_known, "st_snaps"].sum()
                if g.loc[age_known, "st_snaps"].sum() else float("nan"),
                "rookie_snap_share": g.loc[g["rookie"], "total_snaps"].sum() / total if total else float("nan"),
                "homegrown_snap_share": g.loc[g["homegrown"], "total_snaps"].sum() / total if total else float("nan"),
                "mean_age_snap_weighted": (g.loc[age_known, "age_start"] * g.loc[age_known, "total_snaps"]).sum()
                / g.loc[age_known, "total_snaps"].sum()
                if g.loc[age_known, "total_snaps"].sum() else float("nan"),
                "n_players": len(g),
            }
        )
    return pd.DataFrame(rows)


def build() -> tuple[pd.DataFrame, pd.DataFrame]:
    snaps = load_snaps()
    players = load_players()
    player = _attach_attributes(snaps, players)
    team = team_shares(player)
    ensure_dirs()
    player.to_csv(OUT / "player_snaps.csv", index=False)
    team.to_csv(OUT / "team_youth.csv", index=False)
    return player, team


def main() -> None:
    player, team = build()
    print(f"player-team-seasons: {len(player)}; team-seasons: {len(team)}")
    print("roster match share:", round(player.matched.mul(player.total_snaps).sum() / player.total_snaps.sum(), 3))
    print("age known share:", round(player.age_start.notna().mul(player.total_snaps).sum() / player.total_snaps.sum(), 3))
    print(team.groupby("season")[["youth_snap_share", "rookie_snap_share", "homegrown_snap_share"]].median().round(3).to_string())


if __name__ == "__main__":
    main()
