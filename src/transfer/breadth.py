"""Outcome breadth of the interior burst.

Does the burst predict only pressure-adjacent production, or also box-score
outcomes? Tier 1 descriptive: one model per outcome, Holm within subgroup.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from data import load
from discovery.role_allocation import _fit
from transfer.common import (
    BURST_PLAYERS,
    CONFIG,
    holm_adjust,
    save,
    status_from_beta,
)

OUTCOMES = {
    # outcome: (numerator flag, denominator, family)
    "pressure_rate": ("pressure", "def_snaps", "pressure-adjacent"),
    "sack_rate": ("sack", "rush_snaps", "pressure-adjacent"),
    "hurry_rate": ("hurry", "def_snaps", "pressure-adjacent"),
    "quick_pressure_rate": ("quick", "def_snaps", "pressure-adjacent"),
    "unblocked_pressure_rate": ("unblocked", "def_snaps", "pressure-adjacent"),
    "tfl_rate": ("tfl", "def_snaps", "box-score"),
    "tackle_rate": ("tackle", "def_snaps", "box-score"),
    "forced_fumble_rate": ("ff", "def_snaps", "box-score"),
}

MIN_DEF_SNAPS = 100
MIN_RUSH_SNAPS = 100


def _flag(series: pd.Series) -> pd.Series:
    if series.dtype == object:
        return series.astype(str).str.lower().isin(["true", "1", "1.0"])
    return series.fillna(False).astype(bool)


def build_play_flags() -> pd.DataFrame:
    """Regular-season play rows with the breadth flags."""
    cols = [
        "game_id",
        "play_id",
        "team_abbr",
        "nfl_id",
        "possession_team",
        "time_to_pressure",
        "player_get_off",
        "sack",
        "time_to_qb_hurry",
        "quick_pressure",
        "unblocked_pressure",
        "tackle_for_loss",
        "tackle",
        "caused_forced_fumble",
    ]
    pp = load.load_player_play(usecols=cols)
    games = load.load_games()[["game_id", "season", "season_type"]]
    pp = pp.merge(games, on="game_id", how="left")
    pp = pp[pp["season_type"] == "REG"].copy()
    pp["is_defense"] = pp["team_abbr"] != pp["possession_team"]
    pp["pressure"] = pp["time_to_pressure"].notna()
    pp["rush"] = pp["player_get_off"].notna()
    pp["sack"] = pp["sack"].fillna(0).gt(0)
    pp["hurry"] = pp["time_to_qb_hurry"].notna()
    pp["quick"] = _flag(pp["quick_pressure"])
    pp["unblocked"] = _flag(pp["unblocked_pressure"])
    pp["tfl"] = pp["tackle_for_loss"].fillna(0).gt(0)
    pp["tackle"] = pp["tackle"].fillna(0).gt(0)
    pp["ff"] = pp["caused_forced_fumble"].fillna(0).gt(0)
    return pp


def build_rates(pp: pd.DataFrame | None = None) -> pd.DataFrame:
    """Player-season rates for the breadth outcomes."""
    pp = build_play_flags() if pp is None else pp
    agg = (
        pp.groupby(["nfl_id", "season"])
        .agg(
            def_snaps=("is_defense", "sum"),
            rush_snaps=("rush", "sum"),
            pressure=("pressure", "sum"),
            sack=("sack", "sum"),
            hurry=("hurry", "sum"),
            quick=("quick", "sum"),
            unblocked=("unblocked", "sum"),
            tfl=("tfl", "sum"),
            tackle=("tackle", "sum"),
            ff=("ff", "sum"),
        )
        .reset_index()
    )
    for outcome, (num, den, _) in OUTCOMES.items():
        agg[outcome] = 100 * agg[num] / agg[den].replace(0, np.nan)
    return agg


def split_half_reliability(
    keys: pd.DataFrame, outcome: str, numerator: str, denominator: str
) -> tuple[float, float, int]:
    """Odd/even play split-half reliability for one rate."""
    pp = keys.copy()
    pp["parity"] = pd.to_numeric(pp["play_id"], errors="coerce").fillna(-1).astype(int) % 2
    den_raw = {"def_snaps": "is_defense", "rush_snaps": "rush"}[denominator]
    halves = (
        pp.groupby(["nfl_id", "season", "parity"])
        .agg(num=(numerator, "sum"), den=(den_raw, "sum"))
        .reset_index()
    )
    wide = halves.pivot_table(
        index=["nfl_id", "season"], columns="parity", values=["num", "den"]
    )
    wide.columns = [f"{a}_{b}" for a, b in wide.columns]
    wide = wide.dropna(subset=["num_0", "num_1", "den_0", "den_1"])
    wide = wide[(wide["den_0"] > 0) & (wide["den_1"] > 0)]
    if len(wide) < 3:
        return np.nan, np.nan, len(wide)
    rate0 = wide["num_0"] / wide["den_0"]
    rate1 = wide["num_1"] / wide["den_1"]
    r = float(rate0.corr(rate1))
    sb = float(2 * r / (1 + r)) if np.isfinite(r) and r > -1 else np.nan
    return r, sb, len(wide)


def build_reliability(raw: pd.DataFrame) -> pd.DataFrame:
    """Reliability for each outcome, by DL subgroup."""
    rows = []
    players = load.load_players()[["nfl_id", "nfl_position"]].copy()
    players["subgroup"] = np.where(
        players["nfl_position"].isin(["DE", "OLB"]),
        "EDGE",
        np.where(players["nfl_position"].isin(["DT", "NT"]), "INTERIOR", "OTHER"),
    )
    raw = raw.merge(players, on="nfl_id", how="left")
    for subgroup in ["INTERIOR", "EDGE"]:
        sub = raw[raw["subgroup"] == subgroup]
        for outcome, (num, den, family) in OUTCOMES.items():
            r, sb, n = split_half_reliability(sub, outcome, num, den)
            rows.append(
                {
                    "subgroup": subgroup,
                    "outcome": outcome,
                    "family": family,
                    "split_half_r": r,
                    "reliability": sb,
                    "n": n,
                }
            )
    return pd.DataFrame(rows)


def fit_breadth(rates: pd.DataFrame, reliability: pd.DataFrame) -> pd.DataFrame:
    burst = pd.read_parquet(BURST_PLAYERS)[
        ["nfl_id", "season", "position_subgroup", "burst_z", "B_draft"]
    ]
    d = burst.merge(rates, on=["nfl_id", "season"], how="left")
    rows = []
    for subgroup in ["INTERIOR", "EDGE"]:
        sub = d[d["position_subgroup"] == subgroup].copy()
        sub = sub[sub["def_snaps"].ge(MIN_DEF_SNAPS) & sub["burst_z"].notna()].copy()
        sub["season_c"] = sub["season"].astype(str)
        cells = []
        for outcome, (_, _, family) in OUTCOMES.items():
            if outcome == "sack_rate":
                cell = sub[sub["rush_snaps"].ge(MIN_RUSH_SNAPS)].copy()
            else:
                cell = sub[sub["def_snaps"].ge(MIN_DEF_SNAPS)].copy()
            cell = cell[
                cell[outcome].notna() & cell["B_draft"].notna() & cell["season"].notna()
            ]
            if len(cell) < 10:
                cells.append(
                    {
                        "subgroup": subgroup,
                        "outcome": outcome,
                        "family": family,
                        "n": int(cell["nfl_id"].nunique()),
                        "reliability": np.nan,
                        "beta": np.nan,
                        "ci_low": np.nan,
                        "ci_high": np.nan,
                        "p": np.nan,
                    }
                )
                continue
            fit = _fit(f"{outcome} ~ burst_z + B_draft + C(season_c)", cell)
            ci = fit.conf_int().loc["burst_z"]
            cells.append(
                {
                    "subgroup": subgroup,
                    "outcome": outcome,
                    "family": family,
                    "n": int(cell["nfl_id"].nunique()),
                    "reliability": float(
                        reliability[
                            (reliability["subgroup"] == subgroup)
                            & (reliability["outcome"] == outcome)
                        ]["reliability"].iloc[0]
                    ),
                    "beta": float(fit.params["burst_z"]),
                    "ci_low": float(ci[0]),
                    "ci_high": float(ci[1]),
                    "p": float(fit.pvalues["burst_z"]),
                }
            )
        table = pd.DataFrame(cells)
        table["p_holm"] = holm_adjust(table["p"])
        table["status"] = [
            status_from_beta(row.beta, row.ci_low, row.ci_high)
            if row.reliability >= float(CONFIG["outcome_reliability_gate"])
            else "unidentifiable"
            for row in table.itertuples()
        ]
        rows.append(table)
    return pd.concat(rows, ignore_index=True)


def main() -> None:
    pp = build_play_flags()
    rates = build_rates(pp)
    reliability = build_reliability(pp)
    table = fit_breadth(rates, reliability)
    save(table, "burst_outcome_breadth.csv")
    save(reliability, "burst_outcome_reliability.csv")
    print(table.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
