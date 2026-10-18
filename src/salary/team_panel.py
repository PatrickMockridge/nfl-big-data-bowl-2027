"""Merge the team-season salary, youth, performance, and contract panels."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .common import CAP_LIMIT, OUT, ensure_dirs
from . import contracts, otc, otc_cap, performance, roster


def build() -> pd.DataFrame:
    o = otc.build()
    _, youth = roster.build()
    _, perf = performance.build()
    con, _ = contracts.build()
    _, cap = otc_cap.build()

    panel = o.merge(youth, on=["season", "team"], how="left", validate="one_to_one")
    panel = panel.merge(perf, on=["season", "team"], how="left", validate="one_to_one")
    panel = panel.merge(
        con[
            [
                "season", "team", "n_contracts", "top5_apy_share", "star_position_apy_share",
                "qb_apy_share", "guarantee_share", "guarantee_coverage", "top_quartile_guarantee_share",
                "apy_sum",
            ]
        ],
        on=["season", "team"],
        how="left",
        validate="one_to_one",
    )
    panel = panel.merge(
        cap.rename(
            columns={
                "active_cap": "cap_active",
                "n_active": "cap_n_active",
                "top5_cap_share": "cap_top5_share",
                "qb_cap_share": "cap_qb_share",
                "star_cap_share": "cap_star_share",
                "trench_cap_share": "cap_trench_share",
                "guaranteed_share": "cap_guaranteed_share",
            }
        ),
        on=["season", "team"],
        how="left",
        validate="one_to_one",
    )
    panel["cap_limit"] = panel["season"].map(CAP_LIMIT)
    panel["payroll_cap_share"] = panel["payroll_od"] / panel["cap_limit"]
    panel["log_payroll"] = np.log(panel["payroll_od"])
    panel["skill_share"] = panel[["wr_share", "rb_share", "te_share"]].sum(axis=1)
    panel["star_nonqb_share"] = panel["star_share"] - panel["qb_share"]
    panel["wins_per_100m"] = panel["wins"] / (panel["payroll_od"] / 1e8)
    panel["point_diff_per_100m"] = panel["point_diff"] / (panel["payroll_od"] / 1e8)
    panel["off_epa_per_100m"] = panel["off_epa"] / (panel["payroll_od"] / 1e8)
    panel["contract_primary"] = panel["season"].eq(2025)
    panel["cap_primary"] = panel["season"].eq(2025)
    panel["season_c"] = panel["season"].astype(str)

    if len(panel) != 96:
        raise ValueError(f"team panel is {len(panel)} rows, expected 96")
    if panel[["wins", "point_diff", "off_epa", "youth_snap_share"]].isna().any().any():
        raise ValueError("team panel has missing core performance/youth values")
    if panel.loc[panel["season"].eq(2025), "cap_active"].isna().any():
        raise ValueError("2025 OTC cap measures are incomplete")

    ensure_dirs()
    panel.to_csv(OUT / "team_salary_panel.csv", index=False)
    return panel


def main() -> None:
    d = build()
    print(f"team salary panel: {len(d)} rows; seasons {sorted(d.season.unique())}")
    print(d.groupby("season")[["payroll_od", "wins_per_100m", "star_share", "youth_snap_share"]].median().round(3).to_string())


if __name__ == "__main__":
    main()
