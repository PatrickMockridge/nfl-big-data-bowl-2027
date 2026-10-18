"""Cross-position replication of the static Yellow Square pattern.

WR/TE: separation over expected (higher better).
OL: pressure allowed (lower better; oriented negative).
DB: allowed completion (lower better; measurement check only).
Regular season only.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from data import load

ROOT = load.ROOT
OUT = ROOT / "outputs" / "models"
RNG = np.random.default_rng(42)

OFFICIAL = [
    "ten_yd_split",
    "forty",
    "three_cone",
    "short_shuttle",
    "vertical",
    "broad_jump",
    "ngs_athleticism_score",
    "ngs_college_production_score",
    "combine_height",
    "combine_weight",
    "arm_length",
    "hand_size",
    "wing_span",
]

GROUP_POSITIONS = {
    "WR": {"WR"},
    "TE": {"TE"},
    "OL": {"T", "G", "C"},
    "DB": {"CB", "SS", "FS", "DB"},
}

CONTEXT_NUM = ["yards_to_go", "pass_length", "cushion", "dropback_duration", "pass_rushers_encountered"]
CONTEXT_CAT = [
    "route_ran",
    "team_coverage_man_zone",
    "team_coverage_type",
    "down",
    "in_motion_at_ball_snap",
    "blitzing",
    "coverage_assignment",
    "receiver_alignment",
    "season",
]


def _z(series: pd.Series) -> pd.Series:
    std = series.std(ddof=0)
    return (series - series.mean()) / std if std > 0 else series * 0


def _outcome(group: str, df: pd.DataFrame) -> pd.Series:
    if group in {"WR", "TE"}:
        return df["separation_at_pass_forward"]
    if group == "OL":
        return -df["pressure_allowed"].astype(float)
    allowed = df["pass_result"].map({"C": 1.0, "I": 0.0, "IN": 0.0})
    return -allowed


def _context_model() -> Pipeline:
    num = Pipeline(
        [("imp", SimpleImputer(strategy="median", add_indicator=True)), ("sc", StandardScaler())]
    )
    cat = Pipeline(
        [
            ("imp", SimpleImputer(strategy="most_frequent")),
            ("oh", OneHotEncoder(handle_unknown="ignore", sparse_output=True)),
        ]
    )
    pre = ColumnTransformer(
        [("num", num, CONTEXT_NUM), ("cat", cat, CONTEXT_CAT)],
        sparse_threshold=1.0,
    )
    return Pipeline([("pre", pre), ("ridge", Ridge(alpha=1.0))])


def _player_residuals(group: str) -> pd.DataFrame:
    players = load.load_players()
    ids = set(players.loc[players["nfl_position"].isin(GROUP_POSITIONS[group]), "nfl_id"])
    pp = load.load_player_play(
        usecols=[
            "nfl_id",
            "game_id",
            "play_id",
            "separation_at_pass_forward",
            "pressure_allowed",
            "pass_result",
            "route_ran",
            "team_coverage_man_zone",
            "team_coverage_type",
            "cushion",
            "down",
            "yards_to_go",
            "pass_length",
            "in_motion_at_ball_snap",
            "blitzing",
            "pass_rushers_encountered",
            "dropback_duration",
            "coverage_assignment",
            "receiver_alignment",
        ]
    )
    games = load.load_games()[["game_id", "season", "season_type"]]
    pp = pp.merge(games, on="game_id", how="left")
    pp = pp[(pp["season_type"] == "REG") & pp["nfl_id"].isin(ids)].copy()
    pp["y"] = _outcome(group, pp)
    pp = pp.dropna(subset=["y"])
    X = pp[CONTEXT_NUM + CONTEXT_CAT]
    y = pp["y"].to_numpy()
    groups = pp["nfl_id"].to_numpy()
    residual = np.full(len(pp), np.nan)
    for train_idx, test_idx in GroupKFold(5).split(X, y, groups):
        model = _context_model().fit(X.iloc[train_idx], y[train_idx])
        residual[test_idx] = y[test_idx] - model.predict(X.iloc[test_idx])
    pp["residual"] = residual
    out = (
        pp.groupby("nfl_id")["residual"]
        .agg(mean="mean", count="count", var="var")
        .reset_index()
        .rename(columns={"mean": "resid_mean", "count": "n_obs", "var": "within_var"})
    )
    out = out[out["n_obs"] >= 20].copy()
    # Empirical Bayes.
    out["within_var"] = out["within_var"].fillna(0)
    noise = out["within_var"] / out["n_obs"]
    tau2 = max(float(out["resid_mean"].var(ddof=0) - noise.mean()), 0.0)
    out["resid_shrunk"] = out["resid_mean"] * tau2 / (tau2 + noise) if tau2 > 0 else 0.0
    return out


def _static_features(players: pd.DataFrame) -> pd.DataFrame:
    combine = load.load_combine_results()
    df = players.merge(combine[["nfl_id"] + OFFICIAL], on="nfl_id", how="left")
    df["B"] = 0.0
    for (year, pos), idx in df.groupby(["draft_year", "nfl_position"]).groups.items():
        sub = df.loc[idx]
        picks = sub["draft_overall_pick"]
        rank = picks.rank(method="average", ascending=False)
        df.loc[idx, "B"] = (rank - 1) / max(len(sub) - 1, 1)
        df.loc[sub.index[picks.isna()], "B"] = 0.0
    df["B"] = df["B"].clip(0, 1)
    return df


def _leave_one_out_alignment(features: pd.DataFrame, residual: pd.Series) -> pd.Series:
    X = features[OFFICIAL].copy()
    for col in OFFICIAL:
        values = pd.to_numeric(X[col], errors="coerce")
        X[col] = values.fillna(values.median())
        std = X[col].std(ddof=0)
        X[col] = (X[col] - X[col].mean()) / std if std > 0 else 0.0
    out = pd.Series(np.nan, index=features.index)
    for idx in features.index:
        others = features.index[features.index != idx]
        values = residual.loc[others].dropna()
        if len(values) < 8:
            continue
        cutoff = values.quantile(2 / 3)
        success = values[values >= cutoff].index
        if len(success) < 4:
            success = values.index
        centroid = X.loc[success].mean()
        norm = np.linalg.norm(centroid)
        if norm == 0:
            continue
        vec = X.loc[idx].to_numpy()
        out.loc[idx] = float(np.dot(vec, centroid) / (np.linalg.norm(vec) * norm))
    return out.rank(pct=True)


def replicate_group(group: str) -> tuple[pd.DataFrame, dict]:
    players = load.load_players()
    res = _player_residuals(group)
    static = _static_features(players)
    d = res.merge(static, on="nfl_id", how="inner")
    d["A"] = _leave_one_out_alignment(d, d["resid_shrunk"])
    d["C"] = 1.0 - d["resid_shrunk"].rank(pct=True)
    d["square"] = "Green"
    high = d["B"] >= 0.5
    d.loc[high & (d["A"] < 0.30), "square"] = "Red"
    d.loc[high & (d["A"] >= 0.30) & (d["A"] <= 0.70), "square"] = "Yellow"
    d.loc[high & (d["A"] > 0.70), "square"] = "Blue"
    y = d.loc[d["square"] == "Yellow", "C"].dropna()
    rb = d.loc[d["square"].isin(["Red", "Blue"]), "C"].dropna()
    result = {"group": group, "players": len(d), "yellow_n": len(y), "redblue_n": len(rb)}
    if len(y) >= 5 and len(rb) >= 5:
        diff = y.mean() - rb.mean()
        draws = [
            RNG.choice(y, len(y), replace=True).mean()
            - RNG.choice(rb, len(rb), replace=True).mean()
            for _ in range(3000)
        ]
        lo, hi = np.percentile(draws, [2.5, 97.5])
        result.update(
            {
                "yellow_mean_C": float(y.mean()),
                "redblue_mean_C": float(rb.mean()),
                "diff": float(diff),
                "ci_low": float(lo),
                "ci_high": float(hi),
                "mwu_p": float(mannwhitneyu(y, rb).pvalue),
            }
        )
    return d, result


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    results = []
    for group in ["WR", "TE", "OL", "DB"]:
        d, result = replicate_group(group)
        d.to_parquet(OUT / f"replication_{group}.parquet", index=False)
        results.append(result)
        print(group, result)
    pd.DataFrame(results).to_csv(OUT / "replication_results.csv", index=False)
    (OUT / "replication_manifest.json").write_text(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
