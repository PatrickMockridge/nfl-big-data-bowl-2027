"""Audit the competition data and score the position-group gate.

The audit is deliberately separate from feature engineering: it establishes
sample sizes, key integrity, tracking quality, outcome reliability, and a
preliminary translation screen before the focus is frozen.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from . import load

OUT = load.ROOT / "outputs" / "audit"


def _ensure_out() -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    return OUT


def schema_report() -> pd.DataFrame:
    rows = []
    for name in [
        "players",
        "combine_results",
        "career",
        "games",
        "combine_tracking",
        "player_play",
        "game_tracking_2023",
        "game_tracking_2024",
        "game_tracking_2025",
    ]:
        if name.startswith("game_tracking"):
            path = load.raw_dir() / f"{name}.csv"
            head = pd.read_csv(path, nrows=0)
            n_rows = sum(1 for _ in open(path, "rb")) - 1
        else:
            df = load._read(name)
            head = df.head(0)
            n_rows = len(df)
        for col in head.columns:
            rows.append(
                {
                    "file": f"{name}.csv",
                    "column": col,
                    "rows": n_rows,
                    "dtype": str(head[col].dtype),
                }
            )
    return pd.DataFrame(rows)


def key_report() -> pd.DataFrame:
    players = load.load_players()
    combine = load.load_combine_results()
    career = load.load_career()
    games = load.load_games()
    pp = load.load_player_play(usecols=["game_id", "play_id", "nfl_id"])
    ct = load.load_combine_tracking(
        usecols=["event_id", "nfl_id", "entity_type", "time"]
    )

    checks = [
        ("players", ["nfl_id"], players),
        ("combine_results", ["draft_year", "nfl_id"], combine),
        ("player_career_successes", ["nfl_id"], career),
        ("games", ["game_id"], games),
        ("player_play", ["game_id", "play_id", "nfl_id"], pp),
        ("combine_tracking", ["event_id", "nfl_id", "entity_type", "time"], ct),
    ]
    rows = []
    for name, keys, df in checks:
        rows.append(
            {
                "table": name,
                "keys": "+".join(keys),
                "rows": len(df),
                "distinct_keys": len(df.drop_duplicates(keys)),
                "duplicate_rows": int(df.duplicated(keys, keep=False).sum()),
            }
        )
    return pd.DataFrame(rows)


def missingness_report() -> pd.DataFrame:
    players = load.load_players()
    pp = load.load_player_play()
    ct = load.load_combine_tracking()
    pp["position_group"] = pp["nfl_id"].map(players.set_index("nfl_id")["position_group"])
    ct["position_group"] = ct["nfl_id"].map(players.set_index("nfl_id")["position_group"])

    rows = []
    for name, df in [("player_play", pp), ("combine_tracking", ct)]:
        for col in df.columns:
            if col == "position_group":
                continue
            overall = df[col].notna().mean()
            rows.append(
                {
                    "table": name,
                    "column": col,
                    "non_null_rate": overall,
                    "n": len(df),
                    "n_groups": df["position_group"].nunique(),
                }
            )
            for group, sub in df.groupby("position_group"):
                rows.append(
                    {
                        "table": name,
                        "column": col,
                        "non_null_rate": sub[col].notna().mean(),
                        "n": len(sub),
                        "n_groups": group,
                    }
                )
    return pd.DataFrame(rows)


def drill_counts() -> pd.DataFrame:
    players = load.load_players()
    ct = load.load_combine_tracking(
        usecols=[
            "draft_year",
            "event_id",
            "nfl_id",
            "entity_type",
            "drill_type",
            "drill_name",
            "attempt",
        ]
    )
    ct = ct[ct.entity_type == "PLAYER"].copy()
    ct["position_group"] = ct["nfl_id"].map(players.set_index("nfl_id")["position_group"])
    counts = (
        ct.groupby(["position_group", "drill_type", "drill_name", "draft_year"])
        .agg(
            rows=("nfl_id", "size"),
            players=("nfl_id", "nunique"),
            attempts=("attempt", "nunique"),
            events=("event_id", "nunique"),
        )
        .reset_index()
    )
    return counts.sort_values(["position_group", "players"], ascending=[True, False])


def tracking_quality() -> pd.DataFrame:
    ct = load.load_combine_tracking(
        usecols=[
            "event_id",
            "nfl_id",
            "entity_type",
            "time",
            "x",
            "y",
            "s",
            "a",
            "dis",
            "dir",
            "drill_type",
            "drill_name",
            "attempt",
            "draft_year",
        ]
    )
    ct = ct[(ct.entity_type == "PLAYER") & ct.nfl_id.notna()].copy()
    ct = ct.sort_values(["event_id", "nfl_id", "attempt", "time"])
    grp = ct.groupby(["event_id", "nfl_id", "attempt"], sort=False)
    ct["dt"] = grp["time"].diff().dt.total_seconds()
    ct["dx"] = grp["x"].diff()
    ct["dy"] = grp["y"].diff()
    ct["s_fd"] = np.hypot(ct["dx"], ct["dy"]) / ct["dt"].replace(0, np.nan)
    ct["speed_err"] = (ct["s_fd"] - ct["s"]).abs()
    ct["dup_time"] = ct.duplicated(["event_id", "nfl_id", "attempt", "time"], keep=False)
    ct["gap"] = ct["dt"] > 0.3
    ct["a_outlier"] = ct["a"].abs() > 15

    quality = (
        ct.groupby(["event_id", "nfl_id", "attempt", "drill_type", "drill_name", "draft_year"])
        .agg(
            frames=("s", "size"),
            duration=("time", lambda x: (x.max() - x.min()).total_seconds()),
            speed_err_mean=("speed_err", "mean"),
            duplicate_frames=("dup_time", "sum"),
            gap_frames=("gap", "sum"),
            accel_outliers=("a_outlier", "sum"),
            max_speed=("s", "max"),
            max_accel=("a", "max"),
            min_accel=("a", "min"),
        )
        .reset_index()
    )
    quality["flag"] = (
        (quality["frames"] < 5)
        | (quality["speed_err_mean"] > 2.0)
        | (quality["duplicate_frames"] > 0)
        | (quality["gap_frames"] > 0)
        | (quality["accel_outliers"] > 0)
    )
    return quality


def _primary_outcome(
    players: pd.DataFrame, pp: pd.DataFrame, group: str
) -> tuple[pd.Series, str] | None:
    group_ids = set(players.loc[players["position_group"] == group, "nfl_id"])
    sub = pp[pp["nfl_id"].isin(group_ids)]
    if group in {"WR", "TE"}:
        return sub.groupby("nfl_id")["separation_at_pass_forward"].mean(), "separation_at_pass_forward"
    if group == "OL":
        return sub.groupby("nfl_id")["pressure_allowed"].mean(), "pressure_allowed"
    if group == "DL":
        return sub.groupby("nfl_id")["player_get_off"].mean(), "player_get_off"
    if group == "DB":
        allowed = sub["pass_result"].map({"C": 1.0, "I": 0.0, "IN": 0.0})
        tmp = sub.assign(allowed_completion=allowed).dropna(subset=["allowed_completion"])
        return tmp.groupby("nfl_id")["allowed_completion"].mean(), "allowed_completion"
    return None


def _split_half(df: pd.DataFrame, col: str) -> tuple[float, float, int]:
    d = df.dropna(subset=[col]).copy()
    d["row"] = d.groupby("nfl_id").cumcount()
    odd = d[d["row"] % 2 == 1].groupby("nfl_id")[col].mean()
    even = d[d["row"] % 2 == 0].groupby("nfl_id")[col].mean()
    paired = pd.concat([odd, even], axis=1).dropna()
    if len(paired) < 10:
        return np.nan, np.nan, len(paired)
    raw = spearmanr(paired.iloc[:, 0], paired.iloc[:, 1]).statistic
    sb = 2 * raw / (1 + raw) if raw > -1 else np.nan
    return float(raw), float(sb), len(paired)


def outcome_reliability() -> pd.DataFrame:
    players = load.load_players()
    pp = load.load_player_play(
        usecols=[
            "nfl_id",
            "separation_at_pass_forward",
            "player_get_off",
            "pressure_allowed",
            "pass_result",
        ]
    )
    rows = []
    for group in ["WR", "TE", "OL", "DL", "DB"]:
        result = _primary_outcome(players, pp, group)
        if result is None:
            continue
        series, outcome = result
        ids = set(series.index)
        sub = pp[pp["nfl_id"].isin(ids)]
        if outcome == "allowed_completion":
            allowed = sub["pass_result"].map({"C": 1.0, "I": 0.0, "IN": 0.0})
            sub = sub.assign(allowed_completion=allowed)
        raw, sb, n = _split_half(sub, outcome)
        rows.append(
            {
                "position_group": group,
                "outcome": outcome,
                "players_with_outcome": int(series.notna().sum()),
                "observations": int(sub[outcome].notna().sum()),
                "split_half_rho": raw,
                "spearman_brown": sb,
            }
        )
    return pd.DataFrame(rows)


def _simple_combine_player_features(players: pd.DataFrame) -> pd.DataFrame:
    ct = load.load_combine_tracking(
        usecols=[
            "event_id",
            "nfl_id",
            "entity_type",
            "time",
            "x",
            "y",
            "s",
            "a",
            "dis",
            "dir",
            "drill_type",
            "attempt",
        ]
    )
    ct = ct[(ct.entity_type == "PLAYER") & ct.nfl_id.notna()].copy()
    ct = ct.sort_values(["event_id", "nfl_id", "attempt", "time"])
    grp = ct.groupby(["event_id", "nfl_id", "attempt"], sort=False)
    ct["dt"] = grp["time"].diff().dt.total_seconds()
    ct["ddir"] = grp["dir"].diff()
    ct["ddir"] = np.where(ct["ddir"].abs() > 180, 360 - ct["ddir"].abs(), ct["ddir"].abs())
    feat = (
        grp.agg(
            frames=("s", "size"),
            max_s=("s", "max"),
            max_accel=("a", "max"),
            min_accel=("a", "min"),
            path=("dis", "sum"),
            x0=("x", "first"),
            y0=("y", "first"),
            x1=("x", "last"),
            y1=("y", "last"),
            mean_ddir=("ddir", "mean"),
        )
        .reset_index()
    )
    feat["net"] = np.hypot(feat["x1"] - feat["x0"], feat["y1"] - feat["y0"])
    feat["path_eff"] = feat["net"] / feat["path"].replace(0, np.nan)
    feat = feat.merge(
        ct[["event_id", "nfl_id", "attempt", "drill_type"]].drop_duplicates(),
        on=["event_id", "nfl_id", "attempt"],
        how="left",
    )
    feat["is_skill"] = feat["drill_type"].str.startswith("SKILL")
    rows = []
    for nfl_id, sub in feat.groupby("nfl_id"):
        use = sub[sub["is_skill"]] if sub["is_skill"].any() else sub
        rows.append(
            {
                "nfl_id": nfl_id,
                "n_attempts": len(use),
                "max_speed": use["max_s"].mean(),
                "max_accel": use["max_accel"].mean(),
                "max_decel": use["min_accel"].mean(),
                "path_eff": use["path_eff"].mean(),
                "mean_ddir": use["mean_ddir"].mean(),
            }
        )
    return pd.DataFrame(rows)


def preliminary_screen(players: pd.DataFrame, pp: pd.DataFrame) -> pd.DataFrame:
    features = _simple_combine_player_features(players)
    rows = []
    for group in ["WR", "TE", "OL", "DL", "DB"]:
        result = _primary_outcome(players, pp, group)
        if result is None:
            continue
        series, outcome = result
        merged = series.rename("outcome").reset_index().merge(features, on="nfl_id")
        for feat_name in ["max_speed", "max_accel", "max_decel", "path_eff", "mean_ddir"]:
            if merged[feat_name].notna().sum() < 10:
                continue
            rho, p = spearmanr(merged[feat_name], merged["outcome"], nan_policy="omit")
            rows.append(
                {
                    "position_group": group,
                    "outcome": outcome,
                    "feature": feat_name,
                    "n": int(merged[feat_name].notna().sum()),
                    "spearman_rho": float(rho),
                    "p_value": float(p),
                }
            )
    return pd.DataFrame(rows)


def gate_scorecard(
    reliability: pd.DataFrame, screen: pd.DataFrame, players: pd.DataFrame
) -> pd.DataFrame:
    rows = []
    for group in ["WR", "TE", "OL", "DL", "DB"]:
        ids = set(players.loc[players["position_group"] == group, "nfl_id"])
        n_players = len(ids)
        rel = reliability[reliability["position_group"] == group]
        sb = rel["spearman_brown"].max() if len(rel) else np.nan
        scr = screen[screen["position_group"] == group]
        best = scr["spearman_rho"].abs().max() if len(scr) else np.nan

        sample_score = 2 if n_players >= 80 else 1 if n_players >= 40 else 0
        rel_score = 2 if (sb or 0) >= 0.6 else 1 if (sb or 0) >= 0.4 else 0
        signal_score = 2 if (best or 0) >= 0.3 else 1 if (best or 0) >= 0.15 else 0
        rows.append(
            {
                "position_group": group,
                "players": n_players,
                "best_outcome_reliability": sb,
                "best_abs_screen_rho": best,
                "sample_score": sample_score,
                "reliability_score": rel_score,
                "signal_score": signal_score,
                "total": sample_score + rel_score + signal_score,
            }
        )
    return pd.DataFrame(rows).sort_values("total", ascending=False)


def trajectory_gallery(ct: pd.DataFrame, out_dir: Path) -> Path:
    player = ct[(ct.entity_type == "PLAYER") & ct.nfl_id.notna()]
    drills = sorted(player["drill_type"].unique())
    fig, axes = plt.subplots(3, 3, figsize=(13, 11))
    axes = axes.ravel()
    for ax, drill in zip(axes, drills):
        sample = player[player["drill_type"] == drill]
        event = sample["event_id"].iloc[0]
        sub = sample[sample["event_id"] == event]
        ax.plot(sub["x"], sub["y"], marker=".", ms=2, lw=1)
        ax.set_title(f"{drill}\n{event[:18]}", fontsize=8)
        ax.set_aspect("equal", adjustable="datalim")
        ax.tick_params(labelsize=6)
    for ax in axes[len(drills) :]:
        ax.axis("off")
    fig.suptitle("Combine tracking: one sample trajectory per drill type", fontsize=11)
    fig.tight_layout()
    path = out_dir / "trajectory_gallery.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def run() -> dict[str, Path]:
    out = _ensure_out()
    players = load.load_players()

    schema_report().to_csv(out / "schema.csv", index=False)
    key_report().to_csv(out / "keys.csv", index=False)
    missingness_report().to_csv(out / "missingness.csv", index=False)
    drill_counts().to_csv(out / "drill_counts.csv", index=False)
    quality = tracking_quality()
    quality.to_csv(out / "tracking_quality.csv", index=False)
    reliability = outcome_reliability()
    reliability.to_csv(out / "outcome_reliability.csv", index=False)
    pp = load.load_player_play(
        usecols=[
            "nfl_id",
            "separation_at_pass_forward",
            "player_get_off",
            "pressure_allowed",
            "pass_result",
        ]
    )
    screen = preliminary_screen(players, pp)
    screen.to_csv(out / "translation_screen.csv", index=False)
    scorecard = gate_scorecard(reliability, screen, players)
    scorecard.to_csv(out / "gate_scorecard.csv", index=False)
    ct = load.load_combine_tracking()
    gallery = trajectory_gallery(ct, out)

    return {
        "schema": out / "schema.csv",
        "keys": out / "keys.csv",
        "missingness": out / "missingness.csv",
        "drill_counts": out / "drill_counts.csv",
        "tracking_quality": out / "tracking_quality.csv",
        "outcome_reliability": out / "outcome_reliability.csv",
        "translation_screen": out / "translation_screen.csv",
        "gate_scorecard": out / "gate_scorecard.csv",
        "trajectory_gallery": gallery,
    }
