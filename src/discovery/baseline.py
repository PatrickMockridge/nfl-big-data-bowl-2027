"""Strong conventional baseline and out-of-sample delta metrics."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.metrics import r2_score

CONV_NUM = [
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
    "team_dl_competition",
]
CONV_CAT = ["position_group", "season", "conf_tier"]


def oof_predict(
    df: pd.DataFrame,
    target: str,
    extra: list[str] | None = None,
    base_num: list[str] | None = None,
    base_cat: list[str] | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    extra = extra or []
    base_num = base_num if base_num is not None else CONV_NUM
    base_cat = base_cat if base_cat is not None else CONV_CAT
    num_cols = list(dict.fromkeys(base_num + extra))
    cat_cols = list(base_cat)
    d = df[df[target].notna()].copy()
    X = d[num_cols + cat_cols]
    y = d[target].to_numpy()
    groups = d["nfl_id"].to_numpy()
    pred = np.full(len(d), np.nan)
    for train_idx, test_idx in GroupKFold(5).split(X, y, groups):
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
            [("num", num, num_cols), ("cat", cat, cat_cols)],
            sparse_threshold=1.0,
        )
        model = Pipeline([("pre", pre), ("ridge", Ridge(alpha=1.0))])
        model.fit(X.iloc[train_idx], y[train_idx])
        pred[test_idx] = model.predict(X.iloc[test_idx])
    return pred, y, d["nfl_id"].to_numpy()


def delta_r2(
    df: pd.DataFrame,
    target: str,
    extra: list[str],
    base_num: list[str] | None = None,
    base_cat: list[str] | None = None,
    n_boot: int = 1000,
) -> dict:
    pred0, y, groups = oof_predict(df, target, [], base_num, base_cat)
    pred1, _, _ = oof_predict(df, target, extra, base_num, base_cat)
    r20 = r2_score(y, pred0)
    r21 = r2_score(y, pred1)
    delta = r21 - r20
    # Player-cluster bootstrap on out-of-fold predictions.
    unique = np.unique(groups)
    draws = []
    for _ in range(n_boot):
        sample = np.random.default_rng(42 + len(draws)).choice(unique, len(unique), replace=True)
        mask = np.isin(groups, sample)
        if mask.sum() < 20:
            continue
        draws.append(r2_score(y[mask], pred1[mask]) - r2_score(y[mask], pred0[mask]))
    lo, hi = np.percentile(draws, [2.5, 97.5]) if draws else (np.nan, np.nan)
    return {
        "target": target,
        "n": int(len(y)),
        "r2_baseline": float(r20),
        "r2_lens": float(r21),
        "delta_r2": float(delta),
        "ci_low": float(lo),
        "ci_high": float(hi),
    }
