"""Generic Combine-tracking movement lens for all positions.

Attempt-level 10 Hz features are standardized within drill, then averaged per
player. The composite is oriented so higher = better movement quality.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from features.combine_tracking import _zscore_by, attempt_features

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs" / "panel"

FEATURES = [
    "max_speed",
    "max_accel_first_05",
    "time_to_1yd",
    "path_efficiency",
    "flip_rate",
    "dwell_median",
    "turn_rate",
]


def player_movement() -> pd.DataFrame:
    attempts = attempt_features(position_group=None)
    attempts = _zscore_by(
        attempts,
        FEATURES,
        ["drill_name", "position_group"],
    )
    agg = (
        attempts.groupby("nfl_id")
        .agg(
            combine_speed=("z_max_speed", "mean"),
            combine_accel=("z_max_accel_first_05", "mean"),
            combine_time1=("z_time_to_1yd", "mean"),
            combine_path=("z_path_efficiency", "mean"),
            combine_flip=("z_flip_rate", "mean"),
            combine_dwell=("z_dwell_median", "mean"),
            combine_turn=("z_turn_rate", "mean"),
            combine_attempts=("event_id", "size"),
        )
        .reset_index()
    )
    parts = agg[["combine_speed", "combine_accel", "combine_time1", "combine_path"]].copy()
    parts["combine_time1"] = -parts["combine_time1"]
    for col in parts.columns:
        std = parts[col].std(ddof=0)
        parts[col] = (parts[col] - parts[col].mean()) / std if std > 0 else 0.0
    agg["combine_movement"] = parts.mean(axis=1)
    return agg


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df = player_movement()
    df.to_parquet(OUT / "combine_movement.parquet", index=False)
    print(df.describe().T[["count", "mean", "std", "min", "max"]].round(3).to_string())


if __name__ == "__main__":
    main()
