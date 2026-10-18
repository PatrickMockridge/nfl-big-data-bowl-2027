"""OverTheCap positional-spending panel (2023-2025).

OTC reports cap spending by position for each team-season. The file was
downloaded from ``overthecap.com/positional-spending`` (the y2023-y2025
containers) and saved as ``data/external/otc_positional_2023_2025.csv``.
"""

from __future__ import annotations

import pandas as pd

from .common import EXTERNAL, OTC_GROUPS, OUT, ensure_dirs, normalize_team

RAW = EXTERNAL / "otc_positional_2023_2025.csv"


def build() -> pd.DataFrame:
    df = pd.read_csv(RAW)
    df = df.rename(columns={"year": "season", "Team": "team_name"})
    df["team"] = normalize_team(df["team"])
    df["season"] = df["season"].astype(int)

    numeric = ["QB", "RB", "WR", "TE", "OL", "Offense", "IDL", "EDGE", "LB", "S", "CB", "Defense"]
    for c in numeric:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df["payroll_od"] = df["Offense"] + df["Defense"]
    df["star_spend"] = df[["QB", "RB", "WR", "TE", "EDGE"]].sum(axis=1)
    df["trench_spend"] = df[["OL", "IDL", "LB", "S", "CB"]].sum(axis=1)
    df["star_share"] = df["star_spend"] / df["payroll_od"]
    df["trench_share"] = df["trench_spend"] / df["payroll_od"]
    df["qb_share"] = df["QB"] / df["payroll_od"]
    df["off_share"] = df["Offense"] / df["payroll_od"]
    df["def_share"] = df["Defense"] / df["payroll_od"]
    for g in OTC_GROUPS:
        df[f"{g.lower()}_share"] = df[g] / df["payroll_od"]

    # Validation: the published position components sum exactly to the
    # published offense/defense totals.
    off_gap = (df[["QB", "RB", "WR", "TE", "OL"]].sum(axis=1) - df["Offense"]).abs().max()
    def_gap = (df[["IDL", "EDGE", "LB", "S", "CB"]].sum(axis=1) - df["Defense"]).abs().max()
    if off_gap > 1 or def_gap > 1:
        raise ValueError(f"OTC component sums do not reconcile: offense gap {off_gap}, defense gap {def_gap}")
    if len(df) != 96 or df.groupby("season")["team"].nunique().ne(32).any():
        raise ValueError("OTC panel is not 32 teams x 3 seasons")

    ensure_dirs()
    df.to_csv(OUT / "otc_panel.csv", index=False)
    return df


def main() -> None:
    d = build()
    print(f"OTC panel: {len(d)} team-seasons; {d.season.nunique()} seasons")
    print(d.groupby("season")[["payroll_od", "star_share", "qb_share"]].median().round(4).to_string())


if __name__ == "__main__":
    main()
