"""Player-level contract aggregates from the public Kaggle contract snapshot.

Coverage warning: this is a snapshot of *current* contracts (signed 2020-2026,
active as of the 2026 league year), not a complete historical cap ledger. It is
well covered for 2025 and poorly covered for 2023. Contract-based measures are
therefore reported for 2025 (2024 as a sensitivity), not for the full panel.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .common import EXTERNAL, OUT, contract_group, ensure_dirs, normalize_team

RAW = EXTERNAL / "player_contracts.csv"
CONTRACT_COLS = [
    "player",
    "pos",
    "team",
    "age_at_signing",
    "start",
    "end",
    "years",
    "value",
    "average",
    "guarantee",
    "practical",
]


def load_contracts() -> pd.DataFrame:
    df = pd.read_csv(RAW, usecols=CONTRACT_COLS)
    df = df.drop_duplicates(["player", "team", "start", "end"]).copy()
    df["team"] = normalize_team(df["team"])
    df["pos_group"] = contract_group(df["pos"])
    df["start"] = pd.to_numeric(df["start"], errors="coerce").astype("Int64")
    df["end"] = pd.to_numeric(df["end"], errors="coerce").fillna(df["start"]).astype("Int64")
    df["years"] = pd.to_numeric(df["years"], errors="coerce")
    for c in ["value", "average", "guarantee", "practical", "age_at_signing"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["apy"] = df["average"]
    # Practical guarantee is the better available measure when the full
    # guarantee is missing; keep the source flag.
    df["guaranteed"] = df["guarantee"].where(df["guarantee"].notna(), df["practical"])
    df["guarantee_source"] = np.where(df["guarantee"].notna(), "guarantee",
                                      np.where(df["practical"].notna(), "practical", "missing"))
    df["name_key"] = df["player"].astype("string").str.lower().str.strip()
    return df


def active_players(df: pd.DataFrame, season: int) -> pd.DataFrame:
    act = df[(df["start"] <= season) & (df["end"] >= season)].copy()
    act["season"] = season
    act = act[act["apy"].notna() & (act["apy"] > 0)].copy()
    return act


def team_aggregates(act: pd.DataFrame) -> pd.DataFrame:
    """Team-season contract aggregates from one season of active contracts."""
    rows = []
    for team, g in act.groupby("team"):
        od = g[g["pos_group"] != "ST"]
        apy = od["apy"]
        apy_sum = apy.sum()
        if apy_sum <= 0:
            continue
        top5 = apy.nlargest(5).sum()
        star = od[od["pos_group"].isin(["QB", "RB", "WR", "TE", "EDGE"])]["apy"].sum()
        qb = od[od["pos_group"] == "QB"]["apy"].sum()
        value_sum = od["value"].sum(min_count=1)
        guaranteed = od["guaranteed"].fillna(0).sum()
        guarantee_coverage = od["guaranteed"].notna().mul(od["value"].fillna(0)).sum() / value_sum if value_sum and value_sum > 0 else np.nan
        q75 = apy.quantile(0.75)
        top_q = od[od["apy"] >= q75]
        top_q_value = top_q["value"].sum(min_count=1)
        top_q_guaranteed = top_q["guaranteed"].fillna(0).sum()
        rows.append(
            {
                "team": team,
                "n_contracts": len(od),
                "apy_sum": apy_sum,
                "value_sum": value_sum,
                "top5_apy_share": top5 / apy_sum,
                "star_position_apy_share": star / apy_sum,
                "qb_apy_share": qb / apy_sum,
                "guarantee_share": guaranteed / value_sum if value_sum and value_sum > 0 else np.nan,
                "guarantee_coverage": guarantee_coverage,
                "top_quartile_guarantee_share": top_q_guaranteed / top_q_value if top_q_value and top_q_value > 0 else np.nan,
            }
        )
    out = pd.DataFrame(rows)
    out["season"] = act["season"].iloc[0]
    return out


def build() -> tuple[pd.DataFrame, pd.DataFrame]:
    df = load_contracts()
    agg = []
    players = []
    for season in (2023, 2024, 2025):
        act = active_players(df, season)
        agg.append(team_aggregates(act))
        players.append(act)
    team = pd.concat(agg, ignore_index=True)
    player = pd.concat(players, ignore_index=True)
    ensure_dirs()
    team.to_csv(OUT / "contract_team_season.csv", index=False)
    player.to_csv(OUT / "contract_players.csv", index=False)
    return team, player


def main() -> None:
    team, player = build()
    print(f"contract team-seasons: {len(team)}; player-seasons: {len(player)}")
    print(team.groupby("season")[["n_contracts", "top5_apy_share", "qb_apy_share", "guarantee_coverage"]].median().round(3).to_string())
    print("2025 top-5 APY share range:", round(team.query("season == 2025").top5_apy_share.min(), 3),
          round(team.query("season == 2025").top5_apy_share.max(), 3))


if __name__ == "__main__":
    main()
