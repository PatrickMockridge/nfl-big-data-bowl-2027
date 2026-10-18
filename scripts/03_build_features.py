"""Build DL Combine-tracking features and context-adjusted get-off outcomes."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from features import combine_tracking as ct  # noqa: E402
from features import player_play as pp  # noqa: E402

OUT = ROOT / "outputs" / "features"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    print("Building DL attempt features ...")
    attempts = ct.attempt_features(position_group="DL")
    attempts.to_parquet(OUT / "dl_attempts.parquet", index=False)
    print(f"  attempts: {len(attempts)}  players: {attempts['nfl_id'].nunique()}")

    print("Building player-level Combine features ...")
    player_feats = ct.player_features(attempts)
    player_feats.to_parquet(OUT / "dl_player_features.parquet", index=False)
    print(f"  players: {len(player_feats)}")

    print("Combine feature reliability ...")
    reliability = ct.reliability_table(
        attempts,
        [
            "max_speed",
            "max_accel_first_05",
            "time_to_1yd",
            "path_efficiency",
            "flip_rate",
            "dwell_median",
            "turn_rate",
        ],
    )
    reliability.to_csv(OUT / "dl_combine_reliability.csv", index=False)

    print("Building DL game outcomes ...")
    plays = pp.dl_plays()
    plays["context_residual"] = pp.cross_fitted_residuals(plays)
    plays.to_parquet(OUT / "dl_plays.parquet", index=False)
    print(f"  plays: {len(plays)}  players: {plays['nfl_id'].nunique()}")

    outcomes = pp.player_outcomes(plays)
    outcomes.to_parquet(OUT / "dl_player_outcomes.parquet", index=False)
    print(f"  player outcomes: {len(outcomes)}")

    print("Outcome reliability (multi-season table, for season-to-season check) ...")
    all_plays = pp.dl_plays(rookie_only=False)
    all_plays["context_residual"] = pp.cross_fitted_residuals(all_plays)
    rel = pp.reliability(all_plays)
    rel.to_csv(OUT / "dl_outcome_reliability.csv", index=False)
    print(rel.to_string(index=False))

    print("Summary:")
    print(player_feats.describe().T[["count", "mean", "std", "min", "max"]].to_string())


if __name__ == "__main__":
    main()
