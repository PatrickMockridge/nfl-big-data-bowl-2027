"""Dynamic Yellow Square state on the regular-season player-season panel.

Leakage discipline: A_t and Phi_t use only prior-class or prior-season
information. 2023 is excluded from confirmatory dynamic tests because no
strictly prior draft class exists.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.model_selection import GroupKFold, KFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from data import load
from framework import squares as sq

ROOT = load.ROOT
PANEL = ROOT / "outputs" / "panel"
OUT = ROOT / "outputs" / "panel"

DL_FEATURES = sq.DL_FEATURES
OFFICIAL_FEATURES = sq.OFFICIAL_FEATURES


def _z(series: pd.Series) -> pd.Series:
    std = series.std(ddof=0)
    return (series - series.mean()) / std if std > 0 else series * 0


def _pct(series: pd.Series) -> pd.Series:
    return series.rank(pct=True, method="average")


def c_abs(dl: pd.DataFrame) -> pd.Series:
    out = pd.Series(np.nan, index=dl.index)
    valid = dl["getoff_shrunk"].notna() & dl["B_draft"].notna()
    if valid.sum() < 10:
        return out
    design = pd.get_dummies(
        dl.loc[valid, ["B_draft", "position_subgroup", "season"]],
        columns=["position_subgroup", "season"],
        drop_first=True,
        dtype=float,
    )
    y = dl.loc[valid, "getoff_shrunk"]
    model = Ridge(alpha=1.0).fit(design, y)
    residual = y - model.predict(design)
    out.loc[valid] = 1.0 - residual.rank(pct=True)
    return out


def strict_alignment(panel: pd.DataFrame) -> pd.Series:
    """Cosine alignment to the success archetype of strictly prior draft classes."""
    feats = pd.read_parquet(ROOT / "outputs" / "features" / "dl_player_features.parquet")
    static = panel.drop_duplicates("nfl_id")[
        ["nfl_id", "draft_year", "position_subgroup"] + OFFICIAL_FEATURES
    ]
    data = feats[["nfl_id"] + DL_FEATURES].merge(static, on="nfl_id", how="outer")
    cols = [c for c in DL_FEATURES + OFFICIAL_FEATURES if c in data.columns]
    X = data[cols].copy()
    for col in cols:
        values = pd.to_numeric(X[col], errors="coerce")
        X[col] = values.fillna(values.median())
        std = X[col].std(ddof=0)
        X[col] = (X[col] - X[col].mean()) / std if std > 0 else 0.0
    alignment = pd.Series(np.nan, index=data.index)
    for target in [2024, 2025]:
        target_mask = data["draft_year"] == target
        source = panel[(panel["draft_year"] < target) & panel["getoff_shrunk"].notna()]
        if target_mask.sum() == 0 or len(source) < 8:
            continue
        for group in ["EDGE", "INTERIOR"]:
            tgt = target_mask & (data["position_subgroup"] == group)
            src_ids = source.loc[source["position_subgroup"] == group, "nfl_id"].unique()
            if tgt.sum() == 0 or len(src_ids) < 4:
                continue
            src_means = (
                source[source["nfl_id"].isin(src_ids)]
                .groupby("nfl_id")["getoff_shrunk"]
                .mean()
            )
            cutoff = src_means.quantile(2 / 3)
            success_ids = src_means[src_means >= cutoff].index
            success_rows = data[data["nfl_id"].isin(success_ids)]
            if len(success_rows) < 4:
                continue
            centroid = X.loc[success_rows.index].mean()
            norm = np.linalg.norm(centroid)
            if norm == 0:
                continue
            sims = X.loc[tgt].dot(centroid) / (
                np.linalg.norm(X.loc[tgt], axis=1) * norm
            )
            alignment.loc[tgt] = _pct(pd.Series(sims, index=data.loc[tgt].index))
    out = data[["nfl_id"]].copy()
    out["A_strict"] = alignment
    return out.set_index("nfl_id")["A_strict"]


def build_player_state(panel: pd.DataFrame) -> pd.DataFrame:
    d = panel[panel["position_group"] == "DL"].copy()
    d["C_abs"] = c_abs(d)
    d["bust"] = (d["C_abs"] >= 0.75).astype(float)
    d.loc[d["C_abs"].isna(), "bust"] = np.nan

    # Strict pre-draft alignment.
    d["A_t"] = d["nfl_id"].map(strict_alignment(panel))

    # Prior-season status for B_t.
    d = d.sort_values(["nfl_id", "season"]).copy()
    d["prev_role_share"] = d.groupby("nfl_id")["role_share_room"].shift()
    d["prev_C"] = d.groupby("nfl_id")["C_abs"].shift()
    status = 0.5 * _z(d["prev_role_share"]) + 0.5 * _z(1 - d["prev_C"])
    status = _pct(status)
    d["B_status"] = status
    d["B_t"] = np.where(d["B_status"].notna(), 0.7 * d["B_draft"] + 0.3 * d["B_status"], d["B_draft"])
    d["B_t"] = d.groupby(["position_subgroup", "season"])["B_t"].rank(pct=True)

    # Prior-only volatility: prior-season weekly F/D; rookies use Combine F/D.
    combine = pd.read_parquet(ROOT / "outputs" / "features" / "dl_player_features.parquet")[
        ["nfl_id", "flip_composite", "dwell_composite"]
    ]
    d = d.merge(combine, on="nfl_id", how="left")
    d["prev_flip"] = d.groupby("nfl_id")["weekly_flip_rate"].shift()
    d["prev_dwell"] = d.groupby("nfl_id")["weekly_dwell"].shift()
    d["F_prior"] = d["prev_flip"].where(d["prev_flip"].notna(), d["flip_composite"])
    d["D_prior"] = d["prev_dwell"].where(d["prev_dwell"].notna(), d["dwell_composite"])
    d["F_z"] = _z(d["F_prior"])
    d["D_z"] = _z(d["D_prior"])
    d["mobius_continuous"] = d["F_z"] - d["D_z"]

    # Yellow: high bridge, mid alignment. 2023 has no strict prior archetype.
    d["square"] = "Green"
    high_b = d["B_t"] >= 0.5
    d.loc[high_b & (d["A_t"] < 0.30), "square"] = "Red"
    d.loc[high_b & (d["A_t"] >= 0.30) & (d["A_t"] <= 0.70), "square"] = "Yellow"
    d.loc[high_b & (d["A_t"] > 0.70), "square"] = "Blue"
    d.loc[d["A_t"].isna(), "square"] = "Unassigned"

    # Fragility: prior-information-only logistic model.
    cols = [
        "B_t",
        "A_t",
        "F_z",
        "D_z",
        "pond_mismatch",
        "team_dl_competition",
        "position_subgroup",
        "season",
    ]
    d["phi"] = np.nan
    valid = d["bust"].notna() & d["A_t"].notna()
    if valid.sum() >= 40 and d.loc[valid, "bust"].nunique() == 2:
        X = d.loc[valid, cols].copy()
        y = d.loc[valid, "bust"].astype(int)
        cats = ["position_subgroup", "season"]
        nums = [c for c in cols if c not in cats]
        pre = ColumnTransformer(
            [
                ("num", Pipeline([("imp", SimpleImputer(strategy="median")), ("sc", StandardScaler())]), nums),
                ("cat", Pipeline([("imp", SimpleImputer(strategy="most_frequent")), ("oh", OneHotEncoder(handle_unknown="ignore", sparse_output=True))]), cats),
            ],
            sparse_threshold=1.0,
        )
        model = Pipeline([("pre", pre), ("logit", LogisticRegression(max_iter=2000, C=1.0))])
        pred = np.full(len(X), np.nan)
        groups = d.loc[valid, "nfl_id"].to_numpy()
        for train_idx, test_idx in GroupKFold(n_splits=5).split(X, y, groups):
            model.fit(X.iloc[train_idx], y.iloc[train_idx])
            pred[test_idx] = model.predict_proba(X.iloc[test_idx])[:, 1]
        d.loc[valid, "phi"] = pred
    # Calibrated resilience.
    d["calibrated_C"] = np.nan
    d["resilience"] = np.nan
    valid_c = d["phi"].notna() & d["C_abs"].notna()
    if valid_c.sum() >= 20:
        x = d.loc[valid_c, "phi"].to_numpy().reshape(-1, 1)
        y = d.loc[valid_c, "C_abs"].to_numpy()
        pred_c = np.full(len(x), np.nan)
        for train_idx, test_idx in KFold(5, shuffle=True, random_state=42).split(x):
            cal = Ridge(alpha=1.0).fit(x[train_idx], y[train_idx])
            pred_c[test_idx] = cal.predict(x[test_idx])
        d.loc[valid_c, "calibrated_C"] = pred_c
        d.loc[valid_c, "resilience"] = pred_c - y
    d["mobius_flag"] = (d["square"] == "Yellow") & (
        d["F_z"] >= d.loc[d["square"] == "Yellow", "F_z"].quantile(0.75)
    ) & (d["D_z"] <= d.loc[d["square"] == "Yellow", "D_z"].quantile(0.25))
    return d


def build_team_state(d: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (season, team), sub in d.groupby(["season", "primary_team"]):
        if len(sub) < 2:
            continue
        # Enforcement: low role entropy, high concentration, scheme homogeneity.
        role_entropy = sub["role_entropy"].mean()
        concentration = sub["role_share_room"].max()
        scheme_homogeneity = max(sub["man_share"].mean(), sub["zone_share"].mean())
        beta = float(np.nanmean([-role_entropy, concentration, scheme_homogeneity]))
        # State vector for diversity/coherence.
        state_cols = ["B_t", "A_t", "getoff_shrunk", "role_share_room", "pond_mismatch"]
        z = sub[state_cols].apply(_z).fillna(0)
        if len(z) >= 2:
            pairwise = []
            for i in range(len(z)):
                for j in range(i + 1, len(z)):
                    a = z.iloc[i].to_numpy()
                    b = z.iloc[j].to_numpy()
                    denom = np.linalg.norm(a) * np.linalg.norm(b)
                    pairwise.append(1 - np.dot(a, b) / denom if denom else 0)
            diversity = float(np.mean(pairwise))
        else:
            diversity = np.nan
        coherence = float(np.mean(np.linalg.norm(z - z.mean(), axis=1)))
        rigidity = float(np.mean(1 - sub["A_t"]))
        performance = float(sub["getoff_shrunk"].mean())
        rows.append(
            {
                "season": season,
                "team": team,
                "n_dl": len(sub),
                "beta": beta,
                "diversity": diversity,
                "coherence": coherence,
                "rigidity": rigidity,
                "performance": performance,
                "ti": coherence / rigidity if rigidity > 0 else np.nan,
                "mean_C": sub["C_abs"].mean(),
                "yellow_share": (sub["square"] == "Yellow").mean(),
                "mobius_share": sub["mobius_flag"].mean(),
            }
        )
    out = pd.DataFrame(rows)
    if len(out):
        out["beta"] = _z(out["beta"])
        out["div"] = out["diversity"]
        out["coh"] = out["coherence"]
        out["rig"] = out["rigidity"]
    return out


def main() -> None:
    panel = pd.read_parquet(PANEL / "player_season.parquet")
    state = build_player_state(panel)
    state.to_parquet(OUT / "dynamic_state.parquet", index=False)
    team = build_team_state(state)
    team.to_parquet(OUT / "team_state.parquet", index=False)
    manifest = {
        "dl_rows": len(state),
        "dl_players": int(state["nfl_id"].nunique()),
        "square_counts": state["square"].value_counts().to_dict(),
        "yellow": int((state["square"] == "Yellow").sum()),
        "mobius_flags": int(state["mobius_flag"].sum()),
        "phi_non_null": int(state["phi"].notna().sum()),
        "team_rows": len(team),
    }
    (OUT / "dynamic_manifest.json").write_text(json.dumps(manifest, indent=2))
    print(json.dumps(manifest, indent=2))
    print("\nC by square:")
    print(state.groupby("square")["C_abs"].agg(["count", "mean", "median"]).round(3).to_string())
    print("\nYellow overlap with transitions:")
    y = state[state["square"] == "Yellow"]
    print("team changes:", int(y["team_change"].sum()), "midseason:", int(y["midseason_move"].sum()), "role label:", int(y["role_label_change"].sum()))


if __name__ == "__main__":
    main()
