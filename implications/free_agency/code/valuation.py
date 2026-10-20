"""Bottom-up free-agency valuation.

Replaces the market portfolio's top-down synthetic portfolio with the actual
2026 signing class. The one-team estimate is the median team's annual role
premium; the league-wide total is context, not a one-team number.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from surplus import build_players

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "implications" / "free_agency" / "outputs"
PANEL = ROOT / "outputs" / "salary" / "team_salary_panel.csv"
SEED = 20261020

# Fixed legacy top-down values from the market portfolio before the override.
# Kept as constants so the reconciliation does not read the updated portfolio.
OLD_TOP_DOWN = {"base": 24.908, "conservative": 13.966, "low": 5.334}

SCENARIOS = {
    "low": {"haircut": 0.15, "positions": "supported", "cost": 0.5, "adoption": 0.2},
    "base": {"haircut": 0.40, "positions": "all", "cost": 1.0, "adoption": 0.4},
    "conservative": {"haircut": 0.40, "positions": "supported", "cost": 1.0, "adoption": 0.4},
    "high": {"haircut": 0.60, "positions": "all", "cost": 2.0, "adoption": 0.6},
}


def supported_positions() -> set[str]:
    path = OUT / "pricing_by_position.csv"
    if not path.exists():
        return {"EDGE", "S", "CB"}
    d = pd.read_csv(path)
    d = d[d["sample"].eq("cap_ledger_2025")]
    return set(d[d["gap_ci_low"].gt(0)]["pos_group"])


def contract_table(d: pd.DataFrame, haircut: float) -> pd.DataFrame:
    out = d.copy()
    out["role_premium_apy_m"] = out["role_premium"].clip(lower=0)
    out["role_premium_total_m"] = out["role_premium_apy_m"] * out["years"] * haircut
    return out


def team_table(d: pd.DataFrame, positions: str) -> pd.DataFrame:
    supported = supported_positions()
    sub = d if positions == "all" else d[d["pos_group"].isin(supported)]
    t = (
        sub.groupby("team")
        .agg(
            n=("player", "size"),
            annual_role_premium_m=("role_premium_apy_m", "sum"),
            contract_total_m=("role_premium_total_m", "sum"),
        )
        .reset_index()
    )
    panel = pd.read_csv(PANEL)
    panel = panel[panel["season"].eq(2025)][
        ["team", "wins", "point_diff", "off_epa_per_play", "wins_per_100m"]
    ]
    all_teams = panel["team"].drop_duplicates()
    t = (
        t.set_index("team")
        .reindex(all_teams, fill_value=0)
        .rename_axis("team")
        .reset_index()
    )
    return t.merge(panel, on="team", how="left")


def summary(d: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for scenario, cfg in SCENARIOS.items():
        sub = contract_table(d, cfg["haircut"])
        teams = team_table(sub, cfg["positions"])
        median_annual = float(teams["annual_role_premium_m"].median())
        median_total = float(teams["contract_total_m"].median())
        # The uncut annual premium is the market fact. The capture is the part
        # a team can realize at the scenario haircut, after implementation cost.
        gross = median_annual
        net = gross - cfg["cost"]
        capture_gross = median_annual * cfg["haircut"]
        capture_net = capture_gross - cfg["cost"]
        rows.append(
            {
                "scenario": scenario,
                "uncut_annual_m": median_annual,
                "gross_m": gross,
                "capture_gross_m": capture_gross,
                "contract_total_median_m": median_total,
                "implementation_cost_m": cfg["cost"],
                "net_m": net,
                "capture_net_m": capture_net,
                "ev_m": net * cfg["adoption"],
                "capture_ev_m": capture_net * cfg["adoption"],
                "method": "bottom_up",
                "n_contracts": int(teams["n"].median()),
                "n_teams": int(len(teams)),
                "positions": cfg["positions"],
                "haircut": cfg["haircut"],
                "notes": (
                    "Median team. uncut=annual role premium; "
                    "capture=uncut*haircut-cost. "
                    f"positions={cfg['positions']}; haircut={cfg['haircut']}."
                ),
            }
        )
    return pd.DataFrame(rows)


def by_team(d: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for positions in ["all", "supported"]:
        sub = contract_table(d, 0.40)
        t = team_table(sub, positions)
        t["positions"] = positions
        rows.append(t)
    out = pd.concat(rows, ignore_index=True)
    return out.sort_values(["positions", "contract_total_m"], ascending=[True, False])


def bridge(d: pd.DataFrame) -> pd.DataFrame:
    teams_all = team_table(contract_table(d, 0.40), "all")
    teams_supported = team_table(contract_table(d, 0.40), "supported")
    top = OLD_TOP_DOWN["base"]
    annual = teams_all["annual_role_premium_m"]
    percentile = float((annual < top).mean())
    rows = [
        {
            "measure": "old_top_down_base_net_m",
            "value": top,
            "note": "synthetic one-team portfolio; legacy top-down",
        },
        {
            "measure": "old_top_down_conservative_net_m",
            "value": OLD_TOP_DOWN["conservative"],
            "note": "only CI-supported position gaps; legacy top-down",
        },
        {
            "measure": "old_top_down_low_net_m",
            "value": OLD_TOP_DOWN["low"],
            "note": "low assumptions; legacy top-down",
        },
        {
            "measure": "new_median_team_annual_m",
            "value": float(annual.median()),
            "note": "actual 2026 signings; median team; uncut",
        },
        {
            "measure": "new_median_team_capture_net_m",
            "value": float(annual.median()) * SCENARIOS["base"]["haircut"]
            - SCENARIOS["base"]["cost"],
            "note": "median team; uncut annual x 0.40 minus $1M",
        },
        {
            "measure": "new_mean_team_annual_m",
            "value": float(annual.mean()),
            "note": "actual 2026 signings; mean team",
        },
        {
            "measure": "new_median_team_contract_total_m",
            "value": float(teams_all["contract_total_m"].median()),
            "note": "APY premium x years x 0.40 haircut",
        },
        {
            "measure": "new_league_annual_m",
            "value": float(annual.sum()),
            "note": "all 32 teams; context, not a one-team number",
        },
        {
            "measure": "old_top_down_percentile_in_team_distribution",
            "value": percentile,
            "note": "share of teams below the old $24.9M",
        },
        {
            "measure": "new_supported_median_annual_m",
            "value": float(teams_supported["annual_role_premium_m"].median()),
            "note": "EDGE/S/CB only; cap-ledger gap CI excludes zero",
        },
    ]
    return pd.DataFrame(rows)


def monte_carlo(d: pd.DataFrame, n: int = 20000, seed: int = SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    teams_all = team_table(contract_table(d, 0.40), "all")
    teams_sup = team_table(contract_table(d, 0.40), "supported")
    rows = []
    for label, teams in [("all", teams_all), ("supported", teams_sup)]:
        annual = teams["annual_role_premium_m"].to_numpy()
        draws = []
        for _ in range(n):
            sample = rng.choice(annual, len(annual), replace=True)
            haircut = rng.triangular(0.15, 0.40, 0.60)
            cost = rng.triangular(0.5, 1.0, 2.0)
            adoption = rng.triangular(0.2, 0.4, 0.6)
            uncut = float(np.median(sample))
            net = uncut - cost
            capture_net = uncut * haircut - cost
            draws.append((net, net * adoption, capture_net, capture_net * adoption))
        draws = np.array(draws)
        for i, metric in enumerate(
            ["net_m", "ev_m", "capture_net_m", "capture_ev_m"]
        ):
            values = draws[:, i]
            rows.append(
                {
                    "positions": label,
                    "metric": metric,
                    "n": n,
                    "seed": seed,
                    "p10_m": float(np.percentile(values, 10)),
                    "p50_m": float(np.percentile(values, 50)),
                    "p90_m": float(np.percentile(values, 90)),
                    "mean_m": float(values.mean()),
                    "prob_above_zero": float((values > 0).mean()),
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    d = build_players()
    contracts = contract_table(d, 0.40)
    contracts.to_csv(OUT / "valuation_contracts.csv", index=False)
    by_team(d).to_csv(OUT / "valuation_by_team.csv", index=False)
    summary(d).to_csv(OUT / "valuation_summary.csv", index=False)
    bridge(d).to_csv(OUT / "valuation_bridge.csv", index=False)
    monte_carlo(d).to_csv(OUT / "valuation_monte_carlo.csv", index=False)

    print("summary:")
    print(summary(d).round(2).to_string(index=False))
    print("\nbridge:")
    print(bridge(d).round(3).to_string(index=False))
    print("\nmonte carlo:")
    print(monte_carlo(d).round(2).to_string(index=False))


if __name__ == "__main__":
    main()
