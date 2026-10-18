"""Green/Yellow/Red/Blue squares, fragility, and resilience for DL prospects.

The framework follows the "Green Square, Yellow Square" post:
- B = bridge score (draft-capital percentile).
- A = alignment with the learned successful-NFL archetype.
- Green: B below the median.
- Red: high B, A < 0.30.
- Yellow: high B, 0.30 <= A <= 0.70 (the transition zone).
- Blue: high B, A > 0.70.
- F/D = movement-state flip rate / dwell from 10 Hz Combine tracking.
- C = bust severity relative to draft capital.
- Phi/R = fragility and counter-wise resilience.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

from data import load

ROOT = load.ROOT
FEATURE_DIR = ROOT / "outputs" / "features"
OUT = ROOT / "outputs" / "models"

DL_FEATURES = [
    "first_step",
    "agility",
    "cod",
    "max_speed",
    "max_accel_first_05",
    "time_to_1yd",
    "path_efficiency",
]

OFFICIAL_FEATURES = [
    "ten_yd_split",
    "forty",
    "three_cone",
    "short_shuttle",
    "vertical",
    "broad_jump",
    "combine_height",
    "combine_weight",
    "arm_length",
    "hand_size",
    "wing_span",
    "ngs_athleticism_score",
]


def subgroup(position: str) -> str:
    if position in {"DE", "OLB"}:
        return "EDGE"
    if position in {"DT", "NT"}:
        return "INTERIOR"
    return "OTHER"


def percentile(series: pd.Series) -> pd.Series:
    return series.rank(pct=True, method="average")


def build_base_table() -> pd.DataFrame:
    cohort = load.cohort()
    cohort = cohort[cohort["combine_position"] == "DL"].copy()
    cohort["position_subgroup"] = cohort["nfl_position"].map(subgroup)
    feats = pd.read_parquet(FEATURE_DIR / "dl_player_features.parquet")
    outcomes = pd.read_parquet(FEATURE_DIR / "dl_player_outcomes.parquet")
    df = cohort.merge(feats, on="nfl_id", how="left").merge(
        outcomes.drop(columns=["draft_year", "nfl_position"], errors="ignore"),
        on="nfl_id",
        how="left",
    )
    return df


def bridge_score(df: pd.DataFrame) -> pd.Series:
    """B in [0,1]; higher = more central. UDFAs are the bottom of the class."""
    out = pd.Series(0.0, index=df.index)
    for (year, group), idx in df.groupby(["draft_year", "position_subgroup"]).groups.items():
        sub = df.loc[idx]
        picks = sub["draft_overall_pick"]
        # Higher pick number = lower bridge. UDFAs (NaN) are below all drafted players.
        rank = picks.rank(method="average", ascending=False)
        out.loc[idx] = (rank - 1) / max(len(sub) - 1, 1)
        out.loc[sub.index[picks.isna()]] = 0.0
    return out.clip(0, 1)


def _standardize(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    out = df[cols].copy()
    for col in cols:
        if col not in df.columns:
            out[col] = np.nan
            continue
        values = out[col].astype(float)
        med = values.median()
        values = values.fillna(med)
        std = values.std(ddof=0)
        out[col] = (values - values.mean()) / std if std > 0 else 0.0
    return out


def archetype_alignment(df: pd.DataFrame) -> pd.DataFrame:
    """Out-of-fold cosine similarity to the successful-NFL archetype.

    For 2023 and 2024, the archetype is learned from the other training year.
    For 2025, it is learned from 2023-2024. The player's own outcome is never
    used to build the archetype applied to that player.
    """
    feature_cols = [c for c in DL_FEATURES + OFFICIAL_FEATURES if c in df.columns]
    X = _standardize(df, feature_cols)
    results = pd.DataFrame(index=df.index)
    results["A_raw"] = np.nan
    results["A"] = np.nan
    results["archetype_source"] = pd.NA

    folds = {
        2023: [2024],
        2024: [2023],
        2025: [2023, 2024],
    }
    for year, source_years in folds.items():
        target = df["draft_year"] == year
        source = df["draft_year"].isin(source_years) & df["shrunk_mean"].notna()
        if target.sum() == 0 or source.sum() < 8:
            continue
        for group in ["EDGE", "INTERIOR"]:
            tgt = target & (df["position_subgroup"] == group)
            src = source & (df["position_subgroup"] == group)
            if tgt.sum() == 0 or src.sum() < 6:
                continue
            src_outcome = df.loc[src, "shrunk_mean"]
            cutoff = src_outcome.quantile(2 / 3)
            success = src & (df["shrunk_mean"] >= cutoff)
            if success.sum() < 4:
                success = src
            centroid = X.loc[success].mean()
            norm = np.linalg.norm(centroid)
            if norm == 0:
                continue
            sims = X.loc[tgt].dot(centroid) / (
                np.linalg.norm(X.loc[tgt], axis=1) * norm
            )
            results.loc[tgt, "A_raw"] = sims
            results.loc[tgt, "A"] = percentile(pd.Series(sims, index=df.loc[tgt].index))
            results.loc[tgt, "archetype_source"] = "-".join(map(str, source_years))
    return results


def bust_severity(df: pd.DataFrame) -> pd.Series:
    """C in [0,1]; high = underperformance relative to draft capital."""
    out = pd.Series(np.nan, index=df.index)
    valid = df["shrunk_mean"].notna() & df["B"].notna()
    if valid.sum() < 10:
        return out
    design = pd.get_dummies(
        df.loc[valid, ["B", "position_subgroup", "draft_year"]],
        columns=["position_subgroup", "draft_year"],
        drop_first=True,
        dtype=float,
    )
    y = df.loc[valid, "shrunk_mean"]
    model = Ridge(alpha=1.0)
    model.fit(design, y)
    residual = y - model.predict(design)
    out.loc[valid] = 1.0 - percentile(residual)
    return out


def assign_squares(df: pd.DataFrame) -> pd.Series:
    squares = pd.Series("Unassigned", index=df.index, dtype=object)
    green = df["B"] < 0.5
    squares[green] = "Green"
    red = (df["B"] >= 0.5) & (df["A"] < 0.30)
    yellow = (df["B"] >= 0.5) & (df["A"] >= 0.30) & (df["A"] <= 0.70)
    blue = (df["B"] >= 0.5) & (df["A"] > 0.70)
    squares[red] = "Red"
    squares[yellow] = "Yellow"
    squares[blue] = "Blue"
    return squares


def mobius_flags(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    out["mobius_continuous"] = df["flip_composite"] - df["dwell_composite"]
    out["mobius_flag"] = False
    yellow = df["square"] == "Yellow"
    if yellow.sum() >= 4:
        f_cut = df.loc[yellow, "flip_composite"].quantile(0.75)
        d_cut = df.loc[yellow, "dwell_composite"].quantile(0.25)
    else:
        f_cut = df["flip_composite"].quantile(0.75)
        d_cut = df["dwell_composite"].quantile(0.25)
    out.loc[yellow, "mobius_flag"] = (
        (df.loc[yellow, "flip_composite"] >= f_cut)
        & (df.loc[yellow, "dwell_composite"] <= d_cut)
    )
    out["mobius_f_cut"] = f_cut
    out["mobius_d_cut"] = d_cut
    return out


def _phi_model() -> Pipeline:
    categorical = OneHotEncoder(handle_unknown="ignore", sparse_output=True)
    pre = ColumnTransformer(
        [("cat", categorical, ["position_subgroup", "draft_year"])],
        remainder="passthrough",
        sparse_threshold=1.0,
    )
    return Pipeline(
        [
            ("pre", pre),
            ("logit", LogisticRegression(max_iter=2000, C=1.0)),
        ]
    )


def fragility(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    out["bust"] = (df["C"] >= 0.75).astype(float)
    out.loc[df["C"].isna(), "bust"] = np.nan
    valid = out["bust"].notna()
    out["phi"] = np.nan
    if valid.sum() < 30 or out.loc[valid, "bust"].nunique() < 2:
        return out
    cols = [
        "B",
        "A",
        "flip_composite",
        "dwell_composite",
        "mobius_continuous",
        "position_subgroup",
        "draft_year",
    ]
    X = df.loc[valid, cols].copy()
    y = out.loc[valid, "bust"].astype(int)
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    pred = np.full(len(X), np.nan)
    for train_idx, test_idx in skf.split(X, y):
        model = _phi_model()
        model.fit(X.iloc[train_idx], y.iloc[train_idx])
        pred[test_idx] = model.predict_proba(X.iloc[test_idx])[:, 1]
    out.loc[valid, "phi"] = pred

    # Calibrate C on phi, then define resilience as better-than-predicted C.
    out["calibrated_C"] = np.nan
    out["resilience"] = np.nan
    out["resilience_binary"] = np.nan
    valid_c = valid & df["C"].notna() & out["phi"].notna()
    if valid_c.sum() >= 20:
        x = out.loc[valid_c, "phi"].to_numpy().reshape(-1, 1)
        y = df.loc[valid_c, "C"].to_numpy()
        from sklearn.model_selection import KFold

        pred_c = np.full(len(x), np.nan)
        for train_idx, test_idx in KFold(
            n_splits=5, shuffle=True, random_state=42
        ).split(x):
            cal = Ridge(alpha=1.0)
            cal.fit(x[train_idx], y[train_idx])
            pred_c[test_idx] = cal.predict(x[test_idx])
        out.loc[valid_c, "calibrated_C"] = pred_c
        out.loc[valid_c, "resilience"] = pred_c - y
        out.loc[valid_c, "resilience_binary"] = (
            out.loc[valid_c, "phi"] - out.loc[valid_c, "bust"]
        )
    return out


def team_table(df: pd.DataFrame) -> pd.DataFrame:
    d = df[df["rookie_team"].notna()].copy()
    rows = []
    for (team, year), sub in d.groupby(["rookie_team", "draft_year"]):
        phi = sub["phi"].fillna(sub["phi"].mean())
        rows.append(
            {
                "team": team,
                "draft_year": year,
                "players": len(sub),
                "yellow": int((sub["square"] == "Yellow").sum()),
                "mobius": int(sub["mobius_flag"].sum()),
                "yellow_share": (sub["square"] == "Yellow").mean(),
                "mobius_share": sub["mobius_flag"].mean(),
                "phi_team": 1 - np.prod(1 - phi),
                "expected_failures": phi.sum(),
                "observed_failures": sub["bust"].sum(),
                "compounding_excess": sub["bust"].sum() - phi.sum(),
                "mean_C": sub["C"].mean(),
                "mean_resilience": sub["resilience"].mean(),
            }
        )
    return pd.DataFrame(rows)


def build() -> tuple[pd.DataFrame, pd.DataFrame]:
    df = build_base_table()
    df["B"] = bridge_score(df)
    alignment = archetype_alignment(df)
    df = df.join(alignment)
    df["C"] = bust_severity(df)
    df["square"] = assign_squares(df)
    df = df.drop(columns=["mobius_continuous"], errors="ignore")
    flags = mobius_flags(df)
    df = df.join(flags)
    frag = fragility(df)
    df = df.join(frag)
    teams = team_table(df)
    return df, teams


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df, teams = build()
    df.to_parquet(OUT / "dl_players.parquet", index=False)
    teams.to_parquet(OUT / "dl_teams.parquet", index=False)
    print("Players:", len(df))
    print(df["square"].value_counts().to_string())
    print("\nMöbius:", int(df["mobius_flag"].sum()))
    print("\nC by square:")
    print(df.groupby("square")["C"].agg(["count", "mean", "median"]).to_string())
    print("\nA/B correlation:", df[["A", "B"]].corr().iloc[0, 1].round(3))
    print("\nTeams:")
    print(teams.sort_values("compounding_excess", ascending=False).head(10).to_string(index=False))


if __name__ == "__main__":
    main()
