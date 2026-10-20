"""Contract-event panel for the free-agency investigation.

Builds three linked samples:
- 2026 free-agent class (observed signings, prior-season performance/role);
- 2025 active APY contracts (cross-check, concurrent performance);
- 2025 OTC cap ledger (cap-number reconciliation).

Also cleans the 1983-2022 historical contract file for trend context.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from salary.common import contract_group, normalize_name, normalize_team

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "implications" / "free_agency" / "outputs"
RAW_CONTRACTS = ROOT / "data" / "external" / "player_contracts.csv"
ACTIVE_CONTRACTS = ROOT / "outputs" / "salary" / "contract_players.csv"
PLAYERS = ROOT / "data" / "external" / "players.csv"
PERF = ROOT / "outputs" / "salary" / "player_performance.csv"
SNAPS = ROOT / "outputs" / "salary" / "player_snaps.csv"
CAP = ROOT / "outputs" / "salary" / "rent_players.csv"
HIST = ROOT / "data" / "external" / "historical_contracts.csv.gz"

CONTRACT_COLS = [
    "player", "pos", "team", "age_at_signing", "start", "end", "years",
    "value", "average", "guarantee", "practical",
]


def _b_draft(players: pd.DataFrame) -> pd.Series:
    out = pd.Series(0.0, index=players.index)
    for _, idx in players.groupby(["draft_year", "pos_group"], dropna=False).groups.items():
        sub = players.loc[idx]
        picks = sub["draft_pick"]
        rank = picks.rank(method="average", ascending=False)
        out.loc[idx] = (rank - 1) / max(len(sub) - 1, 1)
        out.loc[sub.index[picks.isna()]] = 0.0
    return out.clip(0, 1)


def load_players() -> pd.DataFrame:
    d = pd.read_csv(PLAYERS, usecols=[
        "gsis_id", "display_name", "pfr_id", "otc_id", "birth_date",
        "rookie_season", "draft_year", "draft_round", "draft_pick",
        "draft_team", "position", "position_group", "ngs_status",
        "latest_team",
    ])
    d["name_key"] = normalize_name(d["display_name"])
    d["pos_group"] = contract_group(d["position"])
    d["B_draft"] = _b_draft(d)
    return d.drop_duplicates(["name_key"], keep="first")


def load_snaps() -> pd.DataFrame:
    d = pd.read_csv(SNAPS)
    d["team"] = normalize_team(d["team"])
    team_total = d.groupby(["team", "season"])["total_snaps"].transform("sum")
    d["snap_share"] = d["total_snaps"] / team_total.replace(0, np.nan)
    return d


def load_perf() -> pd.DataFrame:
    d = pd.read_csv(PERF, usecols=[
        "player_id", "player_name", "name_key", "season", "position_group",
        "group", "perf_z", "perf_n", "perf_metric",
    ])
    d = d.rename(columns={"player_id": "gsis_id", "position_group": "perf_position_group"})
    return d


def _prior_team(snaps: pd.DataFrame, season: int) -> pd.DataFrame:
    d = snaps[snaps["season"].eq(season)]
    return (
        d.sort_values("total_snaps", ascending=False)
        .drop_duplicates("name_key")[["name_key", "team"]]
        .rename(columns={"team": "prior_team"})
    )


def _join_context(
    contracts: pd.DataFrame, snaps: pd.DataFrame, perf: pd.DataFrame,
    players: pd.DataFrame, prior_season: int, perf_season: int,
) -> pd.DataFrame:
    d = contracts.copy()
    d["name_key"] = normalize_name(d["player"])
    d["team"] = normalize_team(d["team"])
    d["pos_group"] = contract_group(d["pos"])

    master = players[[
        "name_key", "gsis_id", "rookie_season", "draft_year", "draft_pick",
        "draft_round", "ngs_status", "B_draft",
    ]]
    d = d.merge(master, on="name_key", how="left")

    prior = _prior_team(snaps, prior_season)
    d = d.merge(prior, on="name_key", how="left")

    snap = snaps[snaps["season"].eq(perf_season)][
        ["name_key", "snap_share", "total_snaps"]
    ]
    d = d.merge(snap, on="name_key", how="left")

    p = perf[perf["season"].eq(perf_season)][
        ["name_key", "perf_z", "perf_n", "perf_metric"]
    ]
    d = d.merge(p, on="name_key", how="left")

    d["years_exp"] = (d["signing_year"] - d["rookie_season"]).clip(lower=0)
    d["team_change"] = (d["team"] != d["prior_team"]).astype("Int64")
    d.loc[d["prior_team"].isna(), "team_change"] = pd.NA
    d["same_team"] = 1 - d["team_change"].astype("float")
    d["rookie"] = (d["start"] == d["rookie_season"]).astype(int)
    d["one_year"] = (d["years"] == 1).astype(int)
    d["re_sign"] = (
        (d["team_change"].eq(0) & d["rookie"].eq(0))
        .fillna(False)
        .astype(int)
    )
    return d


def build_2026_class(players: pd.DataFrame, snaps: pd.DataFrame, perf: pd.DataFrame) -> pd.DataFrame:
    raw = pd.read_csv(RAW_CONTRACTS, usecols=CONTRACT_COLS)
    raw = raw[raw["start"].eq(2026)].copy()
    raw = raw.drop_duplicates(["player", "team", "start", "end"])
    raw["apy"] = raw["average"] / 1e6
    raw["value_m"] = raw["value"] / 1e6
    raw["guaranteed_m"] = raw["guarantee"].fillna(raw["practical"]) / 1e6
    raw["guarantee_share"] = raw["guaranteed_m"] / raw["value_m"].replace(0, np.nan)
    raw["signing_year"] = 2026
    d = _join_context(raw, snaps, perf, players, prior_season=2025, perf_season=2025)
    d["sample"] = "fa_class_2026"
    return d


def build_active_apy(
    season: int,
    prior_season: int,
    perf_season: int,
    players: pd.DataFrame,
    snaps: pd.DataFrame,
    perf: pd.DataFrame,
) -> pd.DataFrame:
    d = pd.read_csv(ACTIVE_CONTRACTS)
    d = d[d["season"].eq(season)].copy()
    d["apy"] = d["apy"] / 1e6
    d["value_m"] = d["value"] / 1e6
    d["guaranteed_m"] = d["guaranteed"] / 1e6
    d["guarantee_share"] = d["guaranteed_m"] / d["value_m"].replace(0, np.nan)
    d["signing_year"] = d["start"]
    d = _join_context(
        d, snaps, perf, players, prior_season=prior_season, perf_season=perf_season
    )
    d["sample"] = f"active_{season}_apy"
    return d


def build_cap_ledger() -> pd.DataFrame:
    d = pd.read_csv(CAP)
    d["sample"] = "cap_ledger_2025"
    return d


def build_historical() -> pd.DataFrame:
    d = pd.read_csv(HIST, usecols=[
        "player", "position", "team", "is_active", "year_signed", "years",
        "value", "apy", "guaranteed", "apy_cap_pct", "inflated_apy",
        "date_of_birth", "otc_id", "draft_year", "draft_round", "draft_overall",
    ])
    d = d[d["year_signed"].between(1983, 2022)].copy()
    d["pos_group"] = contract_group(d["position"])
    d["dob"] = pd.to_datetime(d["date_of_birth"], errors="coerce")
    d["age_at_signing"] = (
        (pd.to_datetime(d["year_signed"].astype(str) + "-09-01") - d["dob"]).dt.days
        / 365.25
    )
    d["apy_m"] = d["apy"] / 1e6
    d["value_m"] = d["value"] / 1e6
    d["guaranteed_m"] = d["guaranteed"] / 1e6
    d["guarantee_share"] = d["guaranteed_m"] / d["value_m"].replace(0, np.nan)
    d["sample"] = "historical"
    return d


def audit(fa: pd.DataFrame, apy: pd.DataFrame, cap: pd.DataFrame, hist: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for name, d, perf_col in [
        ("2026 FA class", fa, "perf_z"),
        ("2025 active APY", apy, "perf_z"),
        ("2025 cap ledger", cap, "perf_z"),
        ("historical", hist, None),
    ]:
        row = {
            "sample": name,
            "rows": len(d),
            "players": int(d["player"].nunique()) if "player" in d else np.nan,
            "with_performance": int(d[perf_col].notna().sum()) if perf_col else np.nan,
            "with_snaps": int(d["snap_share"].notna().sum()) if "snap_share" in d else np.nan,
            "with_draft": int(d["B_draft"].notna().sum()) if "B_draft" in d else np.nan,
        }
        rows.append(row)
    return pd.DataFrame(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    players = load_players()
    snaps = load_snaps()
    perf = load_perf()

    fa = build_2026_class(players, snaps, perf)
    apy = build_active_apy(2025, 2024, 2025, players, snaps, perf)
    apy24 = build_active_apy(2024, 2023, 2023, players, snaps, perf)
    cap = build_cap_ledger()
    hist = build_historical()

    fa.to_csv(OUT / "fa_class_2026.csv", index=False)
    apy.to_csv(OUT / "contract_events_2025.csv", index=False)
    apy24.to_csv(OUT / "contract_events_2024.csv", index=False)
    cap.to_csv(OUT / "cap_ledger_2025.csv", index=False)
    hist.to_csv(OUT / "historical_contracts_clean.csv", index=False)
    table = audit(fa, apy, cap, hist)
    table.to_csv(OUT / "panel_audit.csv", index=False)
    print(table.to_string(index=False))

    print("\n2026 class types:")
    print(fa[["team_change", "rookie", "one_year", "re_sign"]].sum().to_string())
    print("\n2026 class by position (performance available):")
    print(
        fa.groupby("pos_group")
        .agg(rows=("player", "size"), perf=("perf_z", "count"),
             apy_median=("apy", "median"))
        .round(2)
        .to_string()
    )


if __name__ == "__main__":
    main()
