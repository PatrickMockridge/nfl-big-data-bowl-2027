"""10 Hz Combine tracking features.

Attempt-level kinematics and movement-state sequences, then player-level
aggregates standardized within drill so drill design does not masquerade as
player volatility.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from data import load

ATTEMPT_KEYS = ["event_id", "nfl_id", "attempt"]
STATE_ORDER = ["straight", "accelerate", "decelerate", "turn_neg", "turn_pos"]

FIRST_STEP_DRILLS = {
    "PASS_RUSH_DRILL",
    "FRONT_START_WAVE_DRILL_AND_LATERAL_REACTION",
    "FORTY_YARD_DASH",
}
AGILITY_DRILLS = {
    "FOUR_BAG_AGILITY_DRILL",
    "RUN_AND_CLUB_DRILL",
    "RUN_THE_HOOP_DRILL",
    "BODY_CONTROL_DRILL",
}
COD_DRILLS = {"THREE_CONE_DRILL", "SHORT_SHUTTLE"}
VOLATILITY_DRILLS = FIRST_STEP_DRILLS | AGILITY_DRILLS | COD_DRILLS


def drill_family(drill_name: str) -> str:
    if drill_name in FIRST_STEP_DRILLS:
        return "first_step"
    if drill_name in AGILITY_DRILLS:
        return "agility"
    if drill_name in COD_DRILLS:
        return "cod"
    return "other"


def add_motion_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(ATTEMPT_KEYS + ["time"]).copy()
    grp = df.groupby(ATTEMPT_KEYS, sort=False)
    df["dt"] = grp["time"].diff().dt.total_seconds()
    df["dx"] = grp["x"].diff()
    df["dy"] = grp["y"].diff()
    df["s_fd"] = np.hypot(df["dx"], df["dy"]) / df["dt"].replace(0, np.nan)
    ddir = grp["dir"].diff()
    df["ddir"] = ((ddir + 180.0) % 360.0) - 180.0
    df["abs_ddir"] = df["ddir"].abs()
    df["jerk"] = grp["a"].diff() / df["dt"].replace(0, np.nan)
    return df


def classify_states(
    df: pd.DataFrame, turn_deg: float = 15.0, accel: float = 0.5
) -> pd.DataFrame:
    """One categorical movement state per frame.

    Priority: a turn dominates a linear acceleration/deceleration. ``turn_pos``
    and ``turn_neg`` are signed direction changes, not anatomical left/right
    (the tracking convention is not documented).
    """
    conditions = [
        df["ddir"] > turn_deg,
        df["ddir"] < -turn_deg,
        df["a"] > accel,
        df["a"] < -accel,
    ]
    choices = ["turn_pos", "turn_neg", "accelerate", "decelerate"]
    df = df.copy()
    df["state"] = np.select(conditions, choices, default="straight")
    return df


def _first_time_at_distance(
    elapsed: np.ndarray, distance: np.ndarray, threshold: float
) -> float:
    hits = np.where(distance >= threshold)[0]
    return float(elapsed[hits[0]]) if len(hits) else np.nan


def _speed_at_time(elapsed: np.ndarray, speed: np.ndarray, t: float) -> float:
    idx = np.where(elapsed >= t)[0]
    return float(speed[idx[0]]) if len(idx) else np.nan


def _state_metrics(states: pd.Series) -> dict[str, float]:
    values = states.to_numpy()
    if len(values) < 2:
        return {
            "flip_rate": np.nan,
            "dwell_median": np.nan,
            "dwell_mean": np.nan,
            "n_states": np.nan,
            "state_entropy": np.nan,
        }
    flips = np.sum(values[1:] != values[:-1])
    # run lengths
    runs = []
    current = values[0]
    length = 1
    for value in values[1:]:
        if value == current:
            length += 1
        else:
            runs.append(length)
            current = value
            length = 1
    runs.append(length)
    counts = pd.Series(values).value_counts(normalize=True)
    entropy = float(-(counts * np.log(counts + 1e-12)).sum())
    return {
        "flip_rate": float(flips / (len(values) - 1)),
        "dwell_median": float(np.median(runs)),
        "dwell_mean": float(np.mean(runs)),
        "n_states": float(len(set(values))),
        "state_entropy": entropy,
    }


def _attempt_metrics(sub: pd.DataFrame) -> dict[str, float]:
    sub = sub.sort_values("time")
    elapsed = (sub["time"] - sub["time"].iloc[0]).dt.total_seconds().to_numpy()
    x = sub["x"].to_numpy()
    y = sub["y"].to_numpy()
    speed = sub["s"].to_numpy()
    accel = sub["a"].to_numpy()
    distance_from_start = np.hypot(x - x[0], y - y[0])
    path_length = float(sub["dis"].sum())
    path_length_xy = float(np.sum(np.hypot(np.diff(x), np.diff(y))))
    net = float(distance_from_start[-1])
    path_efficiency = (
        min(net / path_length_xy, 1.0) if path_length_xy > 0 else np.nan
    )

    peak_idx = int(np.argmax(speed))
    first_half = elapsed <= 0.5
    first_third = elapsed <= 0.3
    turn_mask = sub["abs_ddir"].to_numpy() > 15.0

    out = {
        "frames": len(sub),
        "duration": float(elapsed[-1]) if len(elapsed) else np.nan,
        "path_length": path_length,
        "path_length_xy": path_length_xy,
        "net_displacement": net,
        "path_efficiency": path_efficiency,
        "max_speed": float(np.nanmax(speed)),
        "mean_speed": float(np.nanmean(speed)),
        "max_accel": float(np.nanmax(accel)),
        "min_accel": float(np.nanmin(accel)),
        "max_abs_accel": float(np.nanmax(np.abs(accel))),
        "time_to_peak_speed": float(elapsed[peak_idx]),
        "speed_at_02": _speed_at_time(elapsed, speed, 0.2),
        "speed_at_05": _speed_at_time(elapsed, speed, 0.5),
        "speed_at_10": _speed_at_time(elapsed, speed, 1.0),
        "max_accel_first_03": float(np.nanmax(accel[first_third]))
        if first_third.any()
        else np.nan,
        "max_accel_first_05": float(np.nanmax(accel[first_half]))
        if first_half.any()
        else np.nan,
        "mean_accel_first_05": float(np.nanmean(accel[first_half]))
        if first_half.any()
        else np.nan,
        "time_to_1yd": _first_time_at_distance(elapsed, distance_from_start, 1.0),
        "time_to_2yd": _first_time_at_distance(elapsed, distance_from_start, 2.0),
        "time_to_3yd": _first_time_at_distance(elapsed, distance_from_start, 3.0),
        "time_to_5yd": _first_time_at_distance(elapsed, distance_from_start, 5.0),
        "n_turns": float(turn_mask.sum()),
        "turn_rate": float(turn_mask.mean()),
        "max_turn_deg": float(np.nanmax(sub["abs_ddir"])),
        "mean_turn_deg": float(np.nanmean(sub["abs_ddir"])),
        "mean_jerk_abs": float(np.nanmean(np.abs(sub["jerk"]))),
    }
    out.update(_state_metrics(sub["state"]))
    return out


def attempt_features(position_group: str | None = None) -> pd.DataFrame:
    players = load.load_players()
    ct = load.load_combine_tracking()
    ct = ct[(ct["entity_type"] == "PLAYER") & ct["nfl_id"].notna()].copy()
    ct["nfl_id"] = ct["nfl_id"].astype(int)
    if position_group is not None:
        ids = set(players.loc[players["position_group"] == position_group, "nfl_id"])
        ct = ct[ct["nfl_id"].isin(ids)].copy()
    ct = add_motion_columns(ct)
    ct = classify_states(ct)

    rows = []
    for keys, sub in ct.groupby(ATTEMPT_KEYS, sort=False):
        event_id, nfl_id, attempt = keys
        meta = sub.iloc[0]
        row = {
            "event_id": event_id,
            "nfl_id": int(nfl_id),
            "attempt": int(attempt),
            "draft_year": int(meta["draft_year"]),
            "drill_type": meta["drill_type"],
            "drill_name": meta["drill_name"],
        }
        row.update(_attempt_metrics(sub))
        rows.append(row)
    out = pd.DataFrame(rows)
    out["position_group"] = out["nfl_id"].map(
        players.set_index("nfl_id")["position_group"]
    )
    out["nfl_position"] = out["nfl_id"].map(players.set_index("nfl_id")["nfl_position"])
    return out


def _zscore_by(df: pd.DataFrame, cols: list[str], by: list[str]) -> pd.DataFrame:
    out = df.copy()
    for col in cols:
        grouped = out.groupby(by, dropna=False)[col]
        mean = grouped.transform("mean")
        std = grouped.transform("std")
        out[f"z_{col}"] = (out[col] - mean) / std.replace(0, np.nan)
    return out


def _attempt_volatility(sub: pd.DataFrame, metric: str = "time_to_1yd") -> pd.Series:
    """Attempt-to-attempt instability for one player x drill."""
    vals = sub.sort_values("attempt")[metric].dropna().to_numpy()
    if len(vals) < 2:
        return pd.Series(
            {"attempt_flip": np.nan, "attempt_cv": np.nan, "attempt_range": np.nan}
        )
    deviations = vals - vals.mean()
    signs = np.sign(deviations)
    signs = signs[signs != 0]
    if len(signs) > 1:
        flips = float(np.sum(signs[1:] != signs[:-1]))
        flip_rate = flips / (len(signs) - 1)
    else:
        flip_rate = np.nan
    mean = np.mean(vals)
    cv = np.std(vals, ddof=1) / abs(mean) if mean != 0 else np.nan
    return pd.Series(
        {
            "attempt_flip": flip_rate,
            "attempt_cv": cv,
            "attempt_range": float(np.max(vals) - np.min(vals)),
        }
    )


def player_features(attempts: pd.DataFrame) -> pd.DataFrame:
    """Aggregate attempts to players with drill-standardized features.

    ``z_`` columns are standardized within ``drill_name`` so a drill's design
    does not count as player volatility. The Möbius flip/dwell features are
    standardized the same way.
    """
    scale_cols = [
        "max_speed",
        "max_accel",
        "max_accel_first_05",
        "time_to_1yd",
        "time_to_2yd",
        "path_efficiency",
        "flip_rate",
        "dwell_median",
        "turn_rate",
        "max_turn_deg",
    ]
    attempts = _zscore_by(attempts, scale_cols, ["drill_name", "position_group"])

    # Keep one row per player x drill_name, then average standardized metrics.
    drill_agg = (
        attempts.groupby(["nfl_id", "drill_name"], dropna=False)
        .agg(
            attempts=("event_id", "size"),
            z_max_speed=("z_max_speed", "mean"),
            z_max_accel=("z_max_accel", "mean"),
            z_max_accel_first_05=("z_max_accel_first_05", "mean"),
            z_time_to_1yd=("z_time_to_1yd", "mean"),
            z_time_to_2yd=("z_time_to_2yd", "mean"),
            z_path_efficiency=("z_path_efficiency", "mean"),
            z_flip_rate=("z_flip_rate", "mean"),
            z_dwell_median=("z_dwell_median", "mean"),
            z_turn_rate=("z_turn_rate", "mean"),
            z_max_turn_deg=("z_max_turn_deg", "mean"),
            raw_flip_rate=("flip_rate", "mean"),
            raw_dwell_median=("dwell_median", "mean"),
            raw_max_speed=("max_speed", "mean"),
            raw_max_accel_first_05=("max_accel_first_05", "mean"),
            raw_time_to_1yd=("time_to_1yd", "mean"),
            raw_path_efficiency=("path_efficiency", "mean"),
        )
        .reset_index()
    )

    def first_step(row: pd.Series) -> float:
        return np.nanmean(
            [
                -row["z_max_accel"],
                -row["z_time_to_1yd"],
                -row["z_time_to_2yd"],
                row["z_path_efficiency"],
            ]
        )

    def agility(row: pd.Series) -> float:
        return np.nanmean(
            [row["z_turn_rate"], row["z_max_turn_deg"], -row["z_path_efficiency"]]
        )

    drill_agg["first_step_z"] = drill_agg.apply(first_step, axis=1)
    drill_agg["agility_z"] = drill_agg.apply(agility, axis=1)
    drill_agg["cod_z"] = drill_agg.apply(agility, axis=1)
    drill_agg["family"] = drill_agg["drill_name"].map(drill_family)

    base = (
        drill_agg.groupby("nfl_id")
        .agg(
            n_attempts=("attempts", "sum"),
            n_drills=("drill_name", "nunique"),
            max_speed=("raw_max_speed", "mean"),
            max_accel_first_05=("raw_max_accel_first_05", "mean"),
            time_to_1yd=("raw_time_to_1yd", "mean"),
            path_efficiency=("raw_path_efficiency", "mean"),
        )
        .reset_index()
    )
    families = {}
    for family in ["first_step", "agility", "cod"]:
        sub = drill_agg[drill_agg["family"] == family]
        agg = (
            sub.groupby("nfl_id")
            .agg(
                **{
                    family: (f"{family}_z", "mean"),
                    f"{family}_flip": ("z_flip_rate", "mean"),
                    f"{family}_dwell": ("z_dwell_median", "mean"),
                }
            )
            .reset_index()
        )
        families[family] = agg
    players = base
    for agg in families.values():
        players = players.merge(agg, on="nfl_id", how="outer")

    vol = drill_agg[drill_agg["drill_name"].isin(VOLATILITY_DRILLS)]
    vol_agg = (
        vol.groupby("nfl_id")
        .agg(
            flip_rate=("raw_flip_rate", "mean"),
            dwell=("raw_dwell_median", "mean"),
            mean_z_flip=("z_flip_rate", "mean"),
            mean_z_dwell=("z_dwell_median", "mean"),
        )
        .reset_index()
    )
    players = players.merge(vol_agg, on="nfl_id", how="left")

    # Attempt-to-attempt instability: the closest analogue to alignment flips.
    # These metrics are scale-free, so average raw values across drills and
    # standardize across players (not within tiny drill groups).
    vol = (
        attempts.groupby(["nfl_id", "drill_name", "position_group"], dropna=False)
        .apply(_attempt_volatility, include_groups=False)
        .reset_index()
    )
    vol_player = (
        vol.groupby("nfl_id")
        .agg(
            attempt_flip=("attempt_flip", "mean"),
            attempt_cv=("attempt_cv", "mean"),
        )
        .reset_index()
    )
    players = players.merge(vol_player, on="nfl_id", how="left")

    def zscore_across(series: pd.Series) -> pd.Series:
        std = series.std(ddof=0)
        return (series - series.mean()) / std if std > 0 else series * 0

    players["z_flip_movement"] = zscore_across(players["mean_z_flip"])
    players["z_flip_attempt"] = zscore_across(players["attempt_flip"])
    players["z_dwell_movement"] = zscore_across(players["mean_z_dwell"])
    players["z_cv_attempt"] = zscore_across(players["attempt_cv"])
    players["flip_composite"] = players[["z_flip_movement", "z_flip_attempt"]].mean(
        axis=1
    )
    players["dwell_composite"] = players[["z_dwell_movement", "z_cv_attempt"]].mean(
        axis=1
    )
    players["mobius_continuous"] = players["flip_composite"] - players["dwell_composite"]
    return players


def reliability_table(attempts: pd.DataFrame, metrics: list[str]) -> pd.DataFrame:
    """Within-player ICC across attempts, within drill."""
    rows = []
    for drill, sub in attempts.groupby("drill_name"):
        for metric in metrics:
            data = sub.dropna(subset=[metric])
            if data["nfl_id"].nunique() < 10:
                continue
            grand = data[metric].mean()
            between = data.groupby("nfl_id")[metric].mean()
            within_var = data.groupby("nfl_id")[metric].var(ddof=0).mean()
            between_var = between.var(ddof=0)
            icc = between_var / (between_var + within_var) if (between_var + within_var) > 0 else np.nan
            rows.append(
                {
                    "drill_name": drill,
                    "metric": metric,
                    "players": data["nfl_id"].nunique(),
                    "attempts": len(data),
                    "icc": icc,
                    "mean": grand,
                    "sd": data[metric].std(),
                }
            )
    return pd.DataFrame(rows)
