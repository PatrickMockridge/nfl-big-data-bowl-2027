"""Descriptive free-agency market: who signs, for what, and with what structure."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from salary.common import contract_group, normalize_team

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "implications" / "free_agency" / "outputs"
RAW_CONTRACTS = ROOT / "data" / "external" / "player_contracts.csv"
PLAYERS = ROOT / "data" / "external" / "players.csv"
TRADES = ROOT / "data" / "external" / "market" / "trades.csv"
DRAFT = ROOT / "data" / "external" / "market" / "draft_picks.csv"


def terms_by_position(fa: pd.DataFrame) -> pd.DataFrame:
    d = fa.copy()
    d["type"] = np.select(
        [d["rookie"].eq(1), d["team_change"].eq(1)],
        ["rookie", "team_change"],
        default="re_sign",
    )
    rows = []
    for (pos, typ), cell in d.groupby(["pos_group", "type"]):
        rows.append(
            {
                "pos_group": pos,
                "type": typ,
                "n": len(cell),
                "median_apy_m": cell["apy"].median(),
                "mean_apy_m": cell["apy"].mean(),
                "median_guarantee_share": cell["guarantee_share"].median(),
                "median_years": cell["years"].median(),
                "median_age": cell["age_at_signing"].median(),
                "one_year_share": cell["one_year"].mean(),
            }
        )
    return pd.DataFrame(rows)


def team_changes(fa: pd.DataFrame) -> pd.DataFrame:
    d = fa[fa["rookie"].eq(0)].copy()
    d["type"] = np.where(d["team_change"].eq(1), "team_change", "re_sign")
    return (
        d.groupby(["pos_group", "type"])
        .agg(
            n=("player", "size"),
            median_apy_m=("apy", "median"),
            median_guarantee_share=("guarantee_share", "median"),
            median_years=("years", "median"),
            median_age=("age_at_signing", "median"),
        )
        .reset_index()
    )


def positional_spend(fa: pd.DataFrame) -> pd.DataFrame:
    d = fa.groupby("pos_group").agg(
        n=("player", "size"),
        total_apy_m=("apy", "sum"),
        median_apy_m=("apy", "median"),
    ).reset_index()
    d["apy_share"] = d["total_apy_m"] / d["total_apy_m"].sum()
    return d.sort_values("total_apy_m", ascending=False)


def age_curves(fa: pd.DataFrame) -> pd.DataFrame:
    d = fa.copy()
    d["age_bucket"] = pd.cut(
        d["age_at_signing"],
        [0, 23, 25, 27, 29, 31, 100],
        labels=["<=23", "24-25", "26-27", "28-29", "30-31", "32+"],
    )
    return (
        d.groupby(["pos_group", "age_bucket"], observed=True)
        .agg(
            n=("player", "size"),
            median_apy_m=("apy", "median"),
            median_perf_z=("perf_z", "median"),
            median_guarantee_share=("guarantee_share", "median"),
            median_years=("years", "median"),
        )
        .reset_index()
    )


def renewal_wave() -> pd.DataFrame:
    raw = pd.read_csv(RAW_CONTRACTS, usecols=[
        "player", "pos", "team", "age_at_signing", "start", "end", "years",
        "value", "average", "guarantee", "practical",
    ])
    raw["team"] = normalize_team(raw["team"])
    raw["pos_group"] = contract_group(raw["pos"])
    raw["apy_m"] = raw["average"] / 1e6
    raw = raw.drop_duplicates(["player", "team", "start", "end"])
    wave = raw[raw["end"].between(2026, 2028)].copy()
    return (
        wave.groupby(["end", "pos_group"])
        .agg(
            n=("player", "size"),
            median_apy_m=("apy_m", "median"),
            total_apy_m=("apy_m", "sum"),
            median_age=("age_at_signing", "median"),
        )
        .reset_index()
        .rename(columns={"end": "contract_end"})
    )


def trade_context() -> pd.DataFrame:
    players = pd.read_csv(PLAYERS, usecols=["pfr_id", "position"])
    players["pos_group"] = contract_group(players["position"])
    trades = pd.read_csv(TRADES)
    trades = trades.merge(players, on="pfr_id", how="left")
    trades = trades[trades["pfr_id"].notna()]
    by_pos = (
        trades.groupby("pos_group")
        .agg(trade_rows=("trade_id", "size"), trades=("trade_id", "nunique"))
        .reset_index()
    )
    draft = pd.read_csv(DRAFT, usecols=["position", "season", "pick"])
    draft["pos_group"] = contract_group(draft["position"])
    picks = (
        draft.groupby("pos_group")
        .agg(picks=("pick", "size"), seasons=("season", "nunique"))
        .reset_index()
    )
    return by_pos.merge(picks, on="pos_group", how="outer").sort_values(
        "trade_rows", ascending=False
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    fa = pd.read_csv(OUT / "fa_class_2026.csv")
    fa["guarantee_share"] = pd.to_numeric(fa["guarantee_share"], errors="coerce")

    terms_by_position(fa).to_csv(OUT / "fa_terms_by_position.csv", index=False)
    team_changes(fa).to_csv(OUT / "fa_team_changes.csv", index=False)
    positional_spend(fa).to_csv(OUT / "fa_positional_spend.csv", index=False)
    age_curves(fa).to_csv(OUT / "fa_age_curves.csv", index=False)
    renewal_wave().to_csv(OUT / "fa_renewal_wave.csv", index=False)
    trade_context().to_csv(OUT / "fa_trade_context.csv", index=False)

    overview = pd.DataFrame(
        [
            {"metric": "2026 signings", "value": len(fa)},
            {"metric": "2026 players", "value": fa["player"].nunique()},
            {"metric": "team changes", "value": int(fa["team_change"].eq(1).sum())},
            {"metric": "re-signs", "value": int(fa["re_sign"].eq(1).sum())},
            {"metric": "rookie deals", "value": int(fa["rookie"].eq(1).sum())},
            {"metric": "one-year deals", "value": int(fa["one_year"].eq(1).sum())},
            {"metric": "with 2025 perf_z", "value": int(fa["perf_z"].notna().sum())},
            {"metric": "median APY ($M)", "value": round(float(fa["apy"].median()), 2)},
            {"metric": "median guarantee share", "value": round(float(fa["guarantee_share"].median()), 3)},
        ]
    )
    overview.to_csv(OUT / "market_overview.csv", index=False)
    print(overview.to_string(index=False))
    print("\nterms by position (top):")
    print(terms_by_position(fa).head(12).round(3).to_string(index=False))


if __name__ == "__main__":
    main()
