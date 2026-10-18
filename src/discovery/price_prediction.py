"""Price-vs-prediction 2x2 for the discovery lenses.

Price axes: draft capital (market) and role share (team allocation).
Prediction axis: position-standardized performance over the strong baseline.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from discovery import baseline

ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "outputs" / "panel" / "panel_full.parquet"
OUT = ROOT / "outputs" / "discovery"

# Clean conventional controls. Prestige and team competition are excluded from
# the baseline because they contain draft/team information that would make the
# market-price model circular.
BASE_NUM = [
    c
    for c in baseline.CONV_NUM
    if c not in {"prestige", "team_dl_competition"}
]
BASE_NUM_NO_PRICE = [c for c in BASE_NUM if c != "B_draft"]
BASE_CAT = list(baseline.CONV_CAT)

# Price axes are only meaningful for pre-draft/exogenous features.
PRE_PRICE = [
    "A_t",
    "weekly_flip_rate",
    "weekly_dwell",
    "mobius_continuous",
    "pond_mismatch",
    "prestige_nodraft",
]
# All features are evaluated on the prediction axis.
PREDICT_FEATURES = PRE_PRICE + [
    "yellow",
    "B_t",
    "role_share_room",
    "team_dl_competition",
    "team_change",
    "midseason_move",
    "pond_upgrade",
]
FEATURES = list(dict.fromkeys(PRE_PRICE + PREDICT_FEATURES))

PRICE_SEOI = 0.01
PREDICT_SEOI = 0.02


def _row(feature: str, price_type: str, metrics: dict) -> dict:
    return {
        "feature": feature,
        "price_type": price_type,
        "target": metrics["target"],
        "n": metrics["n"],
        "r2_baseline": metrics["r2_baseline"],
        "r2_lens": metrics["r2_lens"],
        "delta_r2": metrics["delta_r2"],
        "ci_low": metrics["ci_low"],
        "ci_high": metrics["ci_high"],
    }


def run() -> pd.DataFrame:
    panel = pd.read_parquet(PANEL)
    rows = []
    for feature in FEATURES:
        d = panel[panel[feature].notna()].copy()
        if len(d) < 40:
            print(f"skip {feature}: n={len(d)}")
            continue
        # Price axes only for pre-draft/exogenous features.
        if feature in PRE_PRICE:
            try:
                m = baseline.delta_r2(
                    d, "B_draft", [feature], base_num=BASE_NUM_NO_PRICE, base_cat=BASE_CAT
                )
                rows.append(_row(feature, "market", m))
            except Exception as exc:
                print(f"{feature} market failed: {exc}")
            try:
                m = baseline.delta_r2(
                    d, "role_share_room", [feature], base_num=BASE_NUM, base_cat=BASE_CAT
                )
                rows.append(_row(feature, "team", m))
            except Exception as exc:
                print(f"{feature} team failed: {exc}")
        # Performance prediction for every feature.
        if feature != "perf_z":
            try:
                m = baseline.delta_r2(
                    d, "perf_z", [feature], base_num=BASE_NUM, base_cat=BASE_CAT
                )
                rows.append(_row(feature, "performance", m))
            except Exception as exc:
                print(f"{feature} performance failed: {exc}")
        # Career/status prediction: one row per player, first observed season.
        dc = d.sort_values("season").groupby("nfl_id").first().reset_index()
        if dc["career_status_z"].notna().sum() >= 40:
            try:
                m = baseline.delta_r2(
                    dc, "career_status_z", [feature], base_num=BASE_NUM, base_cat=BASE_CAT
                )
                rows.append(_row(feature, "career", m))
            except Exception as exc:
                print(f"{feature} career failed: {exc}")
    out = pd.DataFrame(rows)
    if len(out):
        out["sig_price"] = out["delta_r2"] - 1.96 * (
            (out["ci_high"] - out["ci_low"]) / 3.92
        )
        out["sig_predict"] = out["target"].eq("perf_z") & (out["delta_r2"] >= PREDICT_SEOI)
        out.to_csv(OUT / "price_prediction.csv", index=False)
    return out


def summarize(out: pd.DataFrame) -> pd.DataFrame:
    if not len(out):
        return out
    rows = []
    for feature, sub in out.groupby("feature"):
        price = sub[sub["price_type"].isin(["market", "team"])]
        predict = sub[sub["target"].isin(["perf_z", "career_status_z"])]
        price_best = price["delta_r2"].max() if len(price) else np.nan
        predict_best = predict["delta_r2"].max() if len(predict) else np.nan
        predict_lo = predict.loc[predict["delta_r2"].idxmax(), "ci_low"] if len(predict) else np.nan
        predict_hi = predict.loc[predict["delta_r2"].idxmax(), "ci_high"] if len(predict) else np.nan
        price_lo = price.loc[price["delta_r2"].idxmax(), "ci_low"] if len(price) else np.nan
        # A lens is only "predictive" if the incremental CI excludes zero and
        # clears the smallest effect of interest; a wide null is not absorption.
        predictive = bool(
            pd.notna(predict_best)
            and predict_best >= PREDICT_SEOI
            and pd.notna(predict_lo)
            and predict_lo > 0
        )
        priced = bool(
            pd.notna(price_best)
            and price_best >= PRICE_SEOI
            and pd.notna(price_lo)
            and price_lo > 0
        )
        perf_baseline = sub.loc[sub["target"] == "perf_z", "r2_baseline"]
        career_baseline = sub.loc[sub["target"] == "career_status_z", "r2_baseline"]
        baseline_absorption = float(
            np.nanmax([perf_baseline.max() if len(perf_baseline) else np.nan,
                       career_baseline.max() if len(career_baseline) else np.nan])
        )
        if predictive:
            quadrant = "efficient" if priced else "residual opportunity"
        elif priced:
            quadrant = "overpriced/noise"
        elif pd.notna(predict_hi) and predict_hi < PREDICT_SEOI:
            quadrant = "absorbed" if baseline_absorption >= 0.5 else "irrelevant"
        else:
            quadrant = "no detectable increment"
        rows.append(
            {
                "feature": feature,
                "price_best": price_best,
                "price_ci_low": price_lo,
                "predict_best": predict_best,
                "predict_ci_low": predict_lo,
                "predict_ci_high": predict_hi,
                "baseline_absorption": baseline_absorption,
                "priced": priced,
                "predictive": predictive,
                "quadrant": quadrant,
                "n_price": int(price["n"].max()) if len(price) else 0,
                "n_predict": int(predict["n"].max()) if len(predict) else 0,
            }
        )
    return pd.DataFrame(rows).sort_values(["quadrant", "predict_best"], ascending=[True, False])


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    out = run()
    summary = summarize(out)
    summary.to_csv(OUT / "price_prediction_summary.csv", index=False)
    (OUT / "price_prediction_manifest.json").write_text(
        json.dumps(
            {
                "price_seoi": PRICE_SEOI,
                "predict_seoi": PREDICT_SEOI,
                "rows": len(out),
                "quadrants": summary["quadrant"].value_counts().to_dict(),
            },
            indent=2,
        )
    )
    print(out.to_string(index=False))
    print("\nSummary:")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
