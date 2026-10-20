"""Three-link transfer screen: measurement, pricing, allocation.

L1 and L2 are fit here. L3 reuses the per-position role equations already in
``outputs/discovery/role_allocation_positions.csv`` and adds the per-position
gap by draft quartile. Tier 1 descriptive only.

Implementation note (disclosed in the protocol and writeup): the L1 sample gate
counts player-season observations, the unit of the models and of the entry's
n=64 interior result. Unique-player counts are reported alongside. The DL
positive control uses the entry's pressure outcome and ``burst_z``; the
task-matched transfer signal is ``pass_rush_burst``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from discovery.baseline import delta_r2
from discovery.role_allocation import _fit
from transfer.common import (
    BURST_PLAYERS,
    CONFIG,
    POSITIONS,
    ROOT,
    bh_fdr,
    bootstrap_mean_cluster,
    bootstrap_spearman,
    holm_adjust,
    pricing_label,
    save,
    status_from_beta,
)

# Position-appropriate incumbent: stopwatch, NGS composite, draft, and body
# measurements. Deliberately excludes team_dl_competition (DL-specific) and the
# position FE (models are fit within position).
BASE_NUM = [
    "B_draft",
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
    "ngs_athleticism_score",
    "ngs_college_production_score",
    "ngs_final_score",
    "college_dominance",
    "conf_strength",
    "prestige",
]
BASE_CAT = ["season"]

PRIMARY_COL = {
    "WR": "route_burst",
    "TE": "route_burst",
    "DB": "transition_quick",
    "OL": "pass_set_quick",
    "DL": "pass_rush_burst",
}

NON_DL_OUTCOME = "perf_z"
DL_OUTCOME = "pressure_rate_z"


def _z(series: pd.Series) -> pd.Series:
    sd = series.std(ddof=0)
    return (series - series.mean()) / sd if sd and not np.isnan(sd) else series * 0.0


def _coef(fit, term: str) -> tuple[float, float, float, float]:
    return (
        float(fit.params.get(term, np.nan)),
        float(fit.conf_int().loc[term, 0]) if term in fit.params else np.nan,
        float(fit.conf_int().loc[term, 1]) if term in fit.params else np.nan,
        float(fit.pvalues.get(term, np.nan)),
    )


def _reliability_lookup(reliability: pd.DataFrame, outcome_rel: pd.DataFrame) -> dict:
    signal = {
        row.position_group: float(row.spearman_brown)
        for row in reliability.itertuples()
    }
    outcome = {
        row.position_group: float(row.outcome_reliability)
        for row in outcome_rel.itertuples()
    }
    return {"signal": signal, "outcome": outcome}


def _fit_one(
    frame: pd.DataFrame,
    area: str,
    position: str,
    signal_col: str,
    outcome_col: str,
    signal_rel: float,
    outcome_rel: float,
    role: str,
    incremental: bool,
    base_num: list[str] | None = None,
    base_cat: list[str] | None = None,
) -> dict:
    sub = frame[
        frame[outcome_col].notna()
        & frame[signal_col].notna()
        & frame["B_draft"].notna()
        & frame["season"].notna()
    ].copy()
    rows = len(sub)
    players = int(sub["nfl_id"].nunique()) if rows else 0
    base = {
        "area": area,
        "position_group": position,
        "role": role,
        "signal": signal_col,
        "outcome": outcome_col,
        "rows": rows,
        "n": players,
        "beta": np.nan,
        "ci_low": np.nan,
        "ci_high": np.nan,
        "p": np.nan,
        "rho": np.nan,
        "rho_ci_low": np.nan,
        "rho_ci_high": np.nan,
        "signal_reliability": signal_rel,
        "outcome_reliability": outcome_rel,
        "incremental_r2": np.nan,
        "incremental_ci_low": np.nan,
        "incremental_ci_high": np.nan,
        "status": "unidentifiable",
        "note": "",
    }
    if rows < 5:
        base["note"] = "too few rows"
        return base
    if sub[outcome_col].std(ddof=0) == 0:
        base["note"] = "outcome has zero variance"
        return base
    if sub[signal_col].std(ddof=0) == 0:
        base["note"] = "signal has zero variance"
        return base

    sub["signal_z"] = _z(sub[signal_col])
    fit = _fit(f"{outcome_col} ~ signal_z + B_draft + C(season)", sub)
    beta, lo, hi, p = _coef(fit, "signal_z")
    rho, rho_lo, rho_hi, _ = bootstrap_spearman(sub, "signal_z", outcome_col)

    incremental_values = {"delta_r2": np.nan, "ci_low": np.nan, "ci_high": np.nan}
    if incremental:
        try:
            incremental_values = delta_r2(
                sub,
                outcome_col,
                ["signal_z"],
                base_num=base_num or BASE_NUM,
                base_cat=base_cat or BASE_CAT,
                n_boot=300,
            )
        except Exception as exc:  # pragma: no cover - defensive for small cells
            print(f"  incremental R2 skipped for {area}: {exc}")

    status = status_from_beta(beta, lo, hi)
    note = ""
    if role == "primary":
        if rows < int(CONFIG["min_players_primary"]):
            status = "unidentifiable"
            note = f"rows below primary gate ({rows} < {CONFIG['min_players_primary']})"
        if signal_rel < float(CONFIG["signal_reliability_gate"]):
            status = "unidentifiable"
            note = f"signal reliability {signal_rel:.3f} below gate"
        if outcome_rel < float(CONFIG["outcome_reliability_gate"]):
            status = "unidentifiable"
            note = f"outcome reliability {outcome_rel:.3f} below gate"
    elif role == "benchmark":
        note = "entry benchmark, not a transfer primary"

    return {
        **base,
        "beta": beta,
        "ci_low": lo,
        "ci_high": hi,
        "p": p,
        "rho": rho,
        "rho_ci_low": rho_lo,
        "rho_ci_high": rho_hi,
        "incremental_r2": incremental_values["delta_r2"],
        "incremental_ci_low": incremental_values["ci_low"],
        "incremental_ci_high": incremental_values["ci_high"],
        "status": status,
        "note": note,
    }


def _non_dl_frame(panel: pd.DataFrame, signals: pd.DataFrame, position: str) -> pd.DataFrame:
    player_signal = signals[signals["position_group"] == position][
        ["nfl_id", PRIMARY_COL[position]]
    ].drop_duplicates("nfl_id")
    return panel.merge(player_signal, on="nfl_id", how="inner")


def _dl_frame(signals: pd.DataFrame) -> pd.DataFrame:
    burst = pd.read_parquet(BURST_PLAYERS)
    task = signals[signals["position_group"] == "DL"][
        ["nfl_id", "pass_rush_burst"]
    ].drop_duplicates("nfl_id")
    return burst.merge(task, on="nfl_id", how="left")


def l1_table(
    panel: pd.DataFrame,
    signals: pd.DataFrame,
    reliability: pd.DataFrame,
    outcome_rel: pd.DataFrame,
) -> pd.DataFrame:
    lookups = _reliability_lookup(reliability, outcome_rel)
    rows = []
    for position in POSITIONS:
        signal_rel = lookups["signal"].get(position, np.nan)
        outcome = lookups["outcome"].get(position, np.nan)
        if position == "DL":
            frame = _dl_frame(signals)
            for subgroup in ["INTERIOR", "EDGE"]:
                sub = frame[frame["position_subgroup"] == subgroup]
                rows.append(
                    _fit_one(
                        sub,
                        f"DL_{subgroup}",
                        "DL",
                        "burst_z",
                        DL_OUTCOME,
                        np.nan,
                        outcome,
                        "benchmark",
                        incremental=True,
                        base_num=["B_draft", "forty", "ten_yd_split"],
                        base_cat=["season_c"],
                    )
                )
                rows.append(
                    _fit_one(
                        sub,
                        f"DL_{subgroup}",
                        "DL",
                        "pass_rush_burst",
                        DL_OUTCOME,
                        signal_rel,
                        outcome,
                        "primary",
                        incremental=True,
                        base_num=["B_draft", "forty", "ten_yd_split"],
                        base_cat=["season_c"],
                    )
                )
        else:
            frame = _non_dl_frame(panel, signals, position)
            rows.append(
                _fit_one(
                    frame,
                    position,
                    position,
                    PRIMARY_COL[position],
                    NON_DL_OUTCOME,
                    signal_rel,
                    outcome,
                    "primary",
                    incremental=True,
                )
            )
    out = pd.DataFrame(rows)
    valid = out["p"].notna() & out["role"].eq("primary") & out["status"].ne("unidentifiable")
    out["p_holm"] = np.nan
    if valid.any():
        out.loc[valid, "p_holm"] = holm_adjust(out.loc[valid, "p"])
    borderline = (
        out["p_holm"].notna()
        & out["p_holm"].gt(0.05)
        & out["status"].eq("supported")
    )
    out.loc[borderline, "status"] = "borderline"
    return out


def per_drill_table(
    panel: pd.DataFrame,
    signals: pd.DataFrame,
    drill_signals: pd.DataFrame,
) -> pd.DataFrame:
    """Exploratory player x drill L1 estimates, BH-controlled within position."""
    dl = pd.read_parquet(BURST_PLAYERS)
    rows = []
    for position in POSITIONS:
        sub = drill_signals[drill_signals["position_group"] == position]
        for drill, cell in sub.groupby("drill_name"):
            if position == "DL":
                for subgroup in ["INTERIOR", "EDGE"]:
                    frame = dl[dl["position_subgroup"] == subgroup].merge(
                        cell[["nfl_id", "signal"]], on="nfl_id", how="inner"
                    )
                    row = _fit_one(
                        frame,
                        f"DL_{subgroup}",
                        "DL",
                        "signal",
                        DL_OUTCOME,
                        np.nan,
                        np.nan,
                        "exploratory",
                        incremental=False,
                    )
                    row["drill_name"] = drill
                    rows.append(row)
            else:
                frame = panel.merge(
                    cell[["nfl_id", "signal"]], on="nfl_id", how="inner"
                )
                row = _fit_one(
                    frame,
                    position,
                    position,
                    "signal",
                    NON_DL_OUTCOME,
                    np.nan,
                    np.nan,
                    "exploratory",
                    incremental=False,
                )
                row["drill_name"] = drill
                rows.append(row)
    out = pd.DataFrame(rows)
    out["q_value"] = np.nan
    for position, idx in out.groupby("position_group").groups.items():
        out.loc[idx, "q_value"] = bh_fdr(out.loc[idx, "p"])
    out["status_exploratory"] = "exploratory"
    return out


def l2_table(signals: pd.DataFrame) -> pd.DataFrame:
    """Primary drill signal vs draft capital, contrasted with incumbents."""
    rows = []
    for position in POSITIONS:
        primary = PRIMARY_COL[position]
        sub = signals[signals["position_group"] == position].copy()
        if sub.empty:
            continue
        sub["stopwatch_40"] = -sub["forty"]
        sub["stopwatch_10"] = -sub["ten_yd_split"]
        candidates = [
            ("primary", primary),
            ("stopwatch_40", "stopwatch_40"),
            ("stopwatch_10", "stopwatch_10"),
            ("generic_movement", "combine_movement"),
        ]
        for kind, col in candidates:
            if col not in sub or sub[col].notna().sum() < 10:
                continue
            rho, lo, hi, n = bootstrap_spearman(sub, col, "B_draft")
            rho_p, p_lo, p_hi, _ = bootstrap_spearman(sub, col, "prestige_nodraft")
            rows.append(
                {
                    "position_group": position,
                    "signal_kind": kind,
                    "signal": col,
                    "n": n,
                    "priced_by_draft_rho": rho,
                    "ci_low": lo,
                    "ci_high": hi,
                    "priced_by_prestige_rho": rho_p,
                    "prestige_ci_low": p_lo,
                    "prestige_ci_high": p_hi,
                    "interpretation": pricing_label(rho),
                }
            )
    return pd.DataFrame(rows)


def l3_tables(role: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Per-position allocation gap by draft quartile and the strict tails."""
    role = role.copy()
    role["gap"] = role["perf_z"] - role["role_z"]
    labels = ["Q1 late/UDFA", "Q2", "Q3", "Q4 early"]
    rows = []
    for position in POSITIONS:
        sub = role[role["position_group"] == position].copy()
        if sub.empty:
            continue
        sub["draft_q"] = pd.qcut(sub["B_draft"], 4, labels=False, duplicates="drop")
        sub["draft_q"] = sub["draft_q"].map(
            {i: labels[i] for i in range(len(labels))}
        )
        for label, cell in sub.groupby("draft_q", observed=True):
            mean, lo, hi, n, players = bootstrap_mean_cluster(cell, "gap")
            rows.append(
                {
                    "position_group": position,
                    "draft_q": str(label),
                    "n": n,
                    "players": players,
                    "mean_gap": mean,
                    "ci_low": lo,
                    "ci_high": hi,
                    "sample": "role_233",
                }
            )
    gap = pd.DataFrame(rows)

    tail_rows = []
    for position in POSITIONS:
        sub = role[role["position_group"] == position].copy()
        if sub.empty:
            continue
        sub["perf_q"] = pd.qcut(sub["perf_z"], 4, labels=False, duplicates="drop")
        sub["role_q"] = pd.qcut(sub["role_z"], 4, labels=False, duplicates="drop")
        cell = sub[(sub["perf_q"] == sub["perf_q"].max()) & (sub["role_q"] == 0)]
        if cell.empty:
            continue
        mean, lo, hi, n, players = bootstrap_mean_cluster(cell, "gap")
        tail_rows.append(
            {
                "position_group": position,
                "tail": "top performance quartile / bottom role quartile",
                "n": n,
                "players": players,
                "mean_gap": mean,
                "ci_low": lo,
                "ci_high": hi,
                "next_role": float(cell["next_role"].mean()),
                "mean_B_draft": float(cell["B_draft"].mean()),
            }
        )
    return gap, pd.DataFrame(tail_rows)


def _cached_signals() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    signal_path = ROOT / "outputs" / "transfer" / "player_signals.csv"
    rel_path = ROOT / "outputs" / "transfer" / "signal_reliability.csv"
    drill_path = ROOT / "outputs" / "transfer" / "player_drill_signals.csv"
    if signal_path.exists() and rel_path.exists() and drill_path.exists():
        return (
            pd.read_csv(signal_path),
            pd.read_csv(rel_path),
            pd.read_csv(drill_path),
        )
    from transfer.drills import build_drill_level, build_signal_table

    signals, player_drill, reliability = build_signal_table()
    return signals, reliability, build_drill_level(player_drill)


def main() -> None:
    from transfer.common import load_panel, load_role_panel
    from transfer.drills import outcome_reliability

    panel = load_panel()
    role = load_role_panel()
    signals, reliability, drill_signals = _cached_signals()
    outcome_rel = outcome_reliability()

    l1 = l1_table(panel, signals, reliability, outcome_rel)
    save(l1, "drill_translation.csv")

    drill_table = per_drill_table(panel, signals, drill_signals)
    save(drill_table, "drill_level_exploratory.csv")

    l2 = l2_table(signals)
    save(l2, "signal_pricing.csv")

    gap, tails = l3_tables(role)
    save(gap, "gap_by_position.csv")
    save(tails, "gap_tails_by_position.csv")

    equations = ROOT / "outputs" / "discovery" / "role_allocation_positions.csv"
    if equations.exists():
        save(pd.read_csv(equations), "role_equations_reference.csv")

    print("\nL1 status:")
    print(
        l1[["area", "role", "rows", "n", "beta", "status", "note"]]
        .round(3)
        .to_string(index=False)
    )
    print("\nL2 interpretation:")
    print(
        l2[["position_group", "signal_kind", "priced_by_draft_rho", "interpretation"]]
        .round(3)
        .to_string(index=False)
    )
    print("\nStrongest exploratory drills (p < 0.10):")
    top = drill_table[drill_table["p"] < 0.10].sort_values("p")
    print(
        top[["area", "drill_name", "rows", "beta", "p", "q_value"]]
        .round(3)
        .head(15)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
