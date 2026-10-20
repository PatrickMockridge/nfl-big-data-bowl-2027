"""Per-drill Combine tracking signals for the transfer pilots.

The judged entry collapses every drill into one ``combine_movement`` composite.
This module keeps the drill layer: attempt-level 10 Hz metrics are standardized
within ``drill_name x position_group``, averaged to player x drill, then to
player x family with equal drill weight.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from data import load
from features.combine_tracking import _zscore_by, attempt_features
from transfer.common import POSITIONS, ROOT, load_panel, position_subgroup

OUT = ROOT / "outputs" / "transfer"

# Exact drill_name membership from outputs/audit/drill_counts.csv.
DRILL_FAMILIES: dict[str, dict[str, list[str]]] = {
    "WR": {
        "route": [
            "CIRCUS_ROUTE_LEFT",
            "COMEBACK_ROUTE_RIGHT",
            "CURL_ROUTE_RIGHT",
            "DAGGER_ROUTE_LEFT",
            "GO_ROUTE_RIGHT",
            "POST_CORNER_ROUTE_LEFT",
            "POST_CORNER_ROUTE_RIGHT",
            "RED_ZONE_FADE_RIGHT",
            "SLANT_ROUTE_LEFT",
            "SLOT_SAIL_ROUTE_RIGHT",
            "SLOT_STRIKE_ROUTE_LEFT",
            "SPEED_OUT_LEFT",
            "SPEED_OUT_ROUTE_LEFT",
        ],
        "other": ["GAUNTLET_DRILL", "OVER_SHOULDER_ADJUST"],
    },
    "TE": {
        "route": [
            "COMEBACK_ROUTE_RIGHT",
            "CORNER_ROUTE",
            "CURL_ROUTE_RIGHT",
            "DAGGER_ROUTE_LEFT",
            "END_ZONE_FADE_RIGHT",
            "FLAT_ROUTE_LEFT",
            "GO_ROUTE_RIGHT",
            "HOOK_ROUTE_RIGHT",
            "IN_ROUTE_LEFT",
            "OVER_SHOULDER_ADJUST",
            "OVER_THE_SHOULDER_ADJUST",
            "POST_CORNER_ROUTE_LEFT",
            "POST_CORNER_ROUTE_RIGHT",
            "RED_ZONE_FADE_RIGHT",
            "SLANT_ROUTE_LEFT",
            "SLOT_SAIL_ROUTE_RIGHT",
            "SLOT_STRIKE_ROUTE_LEFT",
            "SPEED_OUT_ROUTE_LEFT",
            "WHEEL_ROUTE_LEFT",
        ],
        "block": ["BLOCK_EXPLOSION"],
    },
    "DB": {
        "backpedal": [
            "BACK_PEDAL_AND_90_DEGREE_BREAK_TO_BALL",
            "BACK_PEDAL_AND_TRANSITION_45_DEGREE_REACTION",
        ],
        "agility": [
            "BOX_DRILL",
            "GAUNTLET_DRILL",
            "LINE",
            "LINE_DRILL",
            "TERYL_AUSTIN_DRILL_1",
            "TERYL_AUSTIN_DRILL_2",
            "W_DRILL",
        ],
        "cod": ["SHORT_SHUTTLE", "THREE_CONE_DRILL"],
    },
    "OL": {
        "pass_set": [
            "PASS_PRO-MIRROR_DRILL",
            "PASS_PRO_MIRROR_DRILL",
            "PASS_RUSH_DROP",
        ],
        "pull": [
            "OL_PULL_DRILL_DEEP_SHORT_PULL_LEFT",
            "OL_PULL_DRILL_FOLD_BLOCK_RIGHT",
            "OL_PULL_DRILL_LONG_PULL_RIGHT",
        ],
        "mirror": ["FIVE_YARD_WAVE_DRILL_SLIDE_AND_SHUFFLE", "SCREEN_DRILL"],
    },
    "DL": {
        "pass_rush": ["PASS_RUSH_DRILL"],
        "first_step": ["FRONT_START_WAVE_DRILL_AND_LATERAL_REACTION"],
        "agility": [
            "BODY_CONTROL_DRILL",
            "FOUR_BAG_AGILITY_DRILL",
            "FOUR_BAG_SHUFFLE_DRILL",
            "RUN_AND_CLUB_DRILL",
            "RUN_THE_HOOP_DRILL",
        ],
        "cod": ["SHORT_SHUTTLE", "THREE_CONE_DRILL"],
    },
}

# Primary signal definition: (family, {metric: sign}). The composite is the
# mean over drills of the mean over signed standardized components.
PRIMARY_DEFINITIONS: dict[str, tuple[str, dict[str, float]]] = {
    "WR": ("route", {"max_accel_first_05": 1.0, "time_to_1yd": -1.0}),
    "TE": ("route", {"max_accel_first_05": 1.0, "time_to_1yd": -1.0}),
    "DB": ("backpedal", {"time_to_1yd": -1.0, "path_efficiency": 1.0}),
    "OL": ("pass_set", {"time_to_1yd": -1.0, "max_accel_first_05": 1.0}),
    "DL": ("pass_rush", {"max_speed": 1.0, "max_accel_first_05": 1.0}),
}

PRIMARY_NAMES = {
    "WR": "route_burst",
    "TE": "route_burst",
    "DB": "transition_quick",
    "OL": "pass_set_quick",
    "DL": "pass_rush_burst",
}

Z_METRICS = [
    "max_speed",
    "max_accel_first_05",
    "time_to_1yd",
    "path_efficiency",
    "flip_rate",
    "dwell_median",
    "turn_rate",
    "max_turn_deg",
]


def _family_lookup() -> pd.DataFrame:
    rows = []
    for position, families in DRILL_FAMILIES.items():
        for family, drills in families.items():
            for drill in drills:
                rows.append(
                    {"position_group": position, "drill_name": drill, "family": family}
                )
    return pd.DataFrame(rows)


def build_attempts() -> pd.DataFrame:
    """Attempt-level 10 Hz metrics, z-scored within drill x position."""
    attempts = attempt_features(position_group=None)
    attempts = attempts[attempts["position_group"].isin(POSITIONS)].copy()
    players = load.load_players()
    players["position_subgroup"] = position_subgroup(players)
    subgroup = players.set_index("nfl_id")["position_subgroup"]
    attempts["position_subgroup"] = attempts["nfl_id"].map(subgroup)
    attempts = _zscore_by(
        attempts,
        Z_METRICS,
        ["drill_name", "position_group"],
    )
    return attempts


def build_player_drill(attempts: pd.DataFrame) -> pd.DataFrame:
    """Player x drill means of the standardized metrics."""
    lookup = _family_lookup()
    attempts = attempts.merge(lookup, on=["position_group", "drill_name"], how="left")
    attempts["family"] = attempts["family"].fillna("other")
    agg = (
        attempts.groupby(
            ["nfl_id", "position_group", "position_subgroup", "drill_name", "family"],
            dropna=False,
        )
        .agg(
            attempts=("event_id", "size"),
            **{f"z_{metric}": (f"z_{metric}", "mean") for metric in Z_METRICS},
        )
        .reset_index()
    )
    return agg


def _component_score(df: pd.DataFrame, components: dict[str, float]) -> pd.Series:
    parts = [sign * df[f"z_{metric}"] for metric, sign in components.items()]
    return pd.concat(parts, axis=1).mean(axis=1)


def build_player_signals(player_drill: pd.DataFrame) -> pd.DataFrame:
    """One row per player with family composites and the primary signal."""
    player_drill = player_drill.copy()
    player_drill["family_first_step"] = _component_score(
        player_drill,
        {"time_to_1yd": -1.0, "max_accel_first_05": 1.0, "path_efficiency": 1.0},
    )
    player_drill["family_agility"] = _component_score(
        player_drill,
        {"turn_rate": 1.0, "max_turn_deg": 1.0, "path_efficiency": -1.0},
    )
    player_drill["family_smooth"] = _component_score(
        player_drill, {"flip_rate": -1.0, "dwell_median": 1.0}
    )

    # Primary signal per position: mean of per-drill composites in the family.
    frames = []
    for position, (family, components) in PRIMARY_DEFINITIONS.items():
        sub = player_drill[
            (player_drill["position_group"] == position)
            & (player_drill["family"] == family)
        ].copy()
        if sub.empty:
            continue
        sub["primary_component"] = _component_score(sub, components)
        agg = (
            sub.groupby(["nfl_id", "position_group", "position_subgroup"])
            .agg(
                **{
                    PRIMARY_NAMES[position]: ("primary_component", "mean"),
                    "primary_drills": ("drill_name", "nunique"),
                    "primary_attempts": ("attempts", "sum"),
                }
            )
            .reset_index()
        )
        frames.append(agg)
    signals = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

    # Family-level summaries for every family (secondary, exploratory).
    family = (
        player_drill.groupby(
            ["nfl_id", "position_group", "position_subgroup", "family"], dropna=False
        )
        .agg(
            drills=("drill_name", "nunique"),
            attempts=("attempts", "sum"),
            first_step=("family_first_step", "mean"),
            agility=("family_agility", "mean"),
            smooth=("family_smooth", "mean"),
        )
        .reset_index()
    )
    wide = family.pivot_table(
        index=["nfl_id", "position_group", "position_subgroup"],
        columns="family",
        values=["first_step", "agility", "smooth"],
        aggfunc="mean",
    )
    wide.columns = [f"{metric}_{family_name}" for metric, family_name in wide.columns]
    wide = wide.reset_index()

    signals = signals.merge(
        wide, on=["nfl_id", "position_group", "position_subgroup"], how="outer"
    )
    return signals


def build_drill_level(player_drill: pd.DataFrame) -> pd.DataFrame:
    """Exploratory player x drill composite for the primary family.

    One row per player x drill. Used for FDR-controlled secondary estimates so
    a narrow, drill-specific signal is visible even when the family composite
    is unidentifiable.
    """
    frames = []
    for position, (family, components) in PRIMARY_DEFINITIONS.items():
        sub = player_drill[
            (player_drill["position_group"] == position)
            & (player_drill["family"] == family)
        ].copy()
        if sub.empty:
            continue
        sub["signal"] = _component_score(sub, components)
        frames.append(
            sub[
                [
                    "nfl_id",
                    "position_group",
                    "position_subgroup",
                    "drill_name",
                    "attempts",
                    "signal",
                ]
            ]
        )
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def _spearman_brown(r: float) -> float:
    return float(2 * r / (1 + r)) if np.isfinite(r) and r > -1 else np.nan


def family_reliability(
    attempts: pd.DataFrame,
    player_drill: pd.DataFrame,
    position: str,
) -> pd.DataFrame:
    """Odd/even-drill split-half reliability of the primary family composite.

    Falls back to odd/even attempts when the family has a single drill. The
    Spearman-Brown correction is reported alongside the raw split-half r.
    """
    family, components = PRIMARY_DEFINITIONS[position]
    drills = DRILL_FAMILIES[position][family]
    rows = []

    if len(drills) >= 2:
        sub = player_drill[
            (player_drill["position_group"] == position)
            & (player_drill["drill_name"].isin(drills))
        ].copy()
        sub["primary_component"] = _component_score(sub, components)
        ordered = sorted(drills)
        odd = set(ordered[0::2])
        even = set(ordered[1::2])
        sub["half"] = np.where(sub["drill_name"].isin(odd), "odd", "even")
        wide = sub.pivot_table(
            index="nfl_id", columns="half", values="primary_component", aggfunc="mean"
        ).dropna()
        n = len(wide)
        r = float(wide["odd"].corr(wide["even"])) if n >= 3 else np.nan
        rows.append(
            {
                "position_group": position,
                "family": family,
                "split": "drills",
                "n": n,
                "split_half_r": r,
                "spearman_brown": _spearman_brown(r),
            }
        )
    else:
        drill = drills[0]
        sub = attempts[
            (attempts["position_group"] == position) & (attempts["drill_name"] == drill)
        ].copy()
        sub["primary_component"] = _component_score(sub, components)
        sub["half"] = np.where(sub["attempt"] % 2 == 1, "odd", "even")
        wide = sub.pivot_table(
            index="nfl_id",
            columns="half",
            values="primary_component",
            aggfunc="mean",
        ).dropna()
        n = len(wide)
        r = float(wide["odd"].corr(wide["even"])) if n >= 3 else np.nan
        rows.append(
            {
                "position_group": position,
                "family": family,
                "split": "attempts",
                "n": n,
                "split_half_r": r,
                "spearman_brown": _spearman_brown(r),
            }
        )
    return pd.DataFrame(rows)


def outcome_reliability() -> pd.DataFrame:
    """Existing split-half reliability from the audit, by position group."""
    path = ROOT / "outputs" / "audit" / "outcome_reliability.csv"
    rel = pd.read_csv(path)
    keep = rel[["position_group", "outcome", "players_with_outcome", "spearman_brown"]]
    return keep.rename(columns={"spearman_brown": "outcome_reliability"})


def build_signal_table() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Player-level signal table, player x drill table, and reliability table."""
    attempts = build_attempts()
    player_drill = build_player_drill(attempts)
    signals = build_player_signals(player_drill)

    players = load.load_players()
    players["position_subgroup"] = position_subgroup(players)
    players = players[
        [
            "nfl_id",
            "nfl_position",
            "position_group",
            "position_subgroup",
            "draft_year",
            "draft_overall_pick",
        ]
    ]
    signals = signals.merge(players, on="nfl_id", how="left", suffixes=("", "_player"))

    combine = load.load_combine_results()[
        ["nfl_id", "forty", "ten_yd_split", "three_cone", "short_shuttle"]
    ]
    signals = signals.merge(combine, on="nfl_id", how="left")

    movement_path = ROOT / "outputs" / "panel" / "combine_movement.parquet"
    if movement_path.exists():
        movement = pd.read_parquet(movement_path)[["nfl_id", "combine_movement"]]
        signals = signals.merge(movement, on="nfl_id", how="left")

    panel = load_panel()
    status = panel.sort_values("season").drop_duplicates("nfl_id")[
        ["nfl_id", "B_draft", "prestige_nodraft", "ngs_final_score"]
    ]
    signals = signals.merge(status, on="nfl_id", how="left")

    reliability = pd.concat(
        [family_reliability(attempts, player_drill, position) for position in POSITIONS],
        ignore_index=True,
    )
    return signals, player_drill, reliability


def sample_audit(
    signals: pd.DataFrame,
    reliability: pd.DataFrame,
) -> pd.DataFrame:
    from transfer.common import load_panel, load_role_panel

    panel = load_panel()
    role = load_role_panel()
    outcome = outcome_reliability().set_index("position_group")["outcome_reliability"]
    signal_rel = reliability.set_index("position_group")["spearman_brown"]
    rows = []
    for position in POSITIONS:
        p = signals[signals["position_group"] == position]
        rows.append(
            {
                "position_group": position,
                "players": int(p["nfl_id"].nunique()),
                "player_seasons": int((panel["position_group"] == position).sum()),
                "perf_rows": int(
                    ((panel["position_group"] == position) & panel["perf_z"].notna()).sum()
                ),
                "role_rows": int((role["position_group"] == position).sum()),
                "signal_reliability": float(signal_rel.get(position, np.nan)),
                "outcome_reliability": float(outcome.get(position, np.nan)),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    signals, player_drill, reliability = build_signal_table()
    signals.to_csv(OUT / "player_signals.csv", index=False)
    player_drill.to_csv(OUT / "player_drill_features.csv", index=False)
    build_drill_level(player_drill).to_csv(
        OUT / "player_drill_signals.csv", index=False
    )
    reliability.to_csv(OUT / "signal_reliability.csv", index=False)
    sample_audit(signals, reliability).to_csv(OUT / "sample_audit.csv", index=False)
    print(f"players: {signals['nfl_id'].nunique()}  rows: {len(signals)}")
    print(reliability.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
