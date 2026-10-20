"""Per-position raw versus role-controlled cap models.

The existing cap model is pooled with position dummies. This module fits the
same specification separately by position on the 909-player 2025 rent ledger,
so the market extension can calibrate a position-specific pricing correction.

The coefficient is a measured association, not a causal price effect.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from salary.analysis import fit

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "outputs" / "salary" / "rent_players.csv"
OUT = ROOT / "implications" / "markets" / "outputs"
GROUPS = ["QB", "RB", "WR", "TE", "EDGE", "IDL", "LB", "S", "CB"]
MIN_PRIMARY = 80
MIN_EXPLORATORY = 40


def load_rent() -> pd.DataFrame:
    d = pd.read_csv(RAW)
    d = d[d["pos_group"].isin(GROUPS)].copy()
    d["logcap"] = np.log(d["cap_number"])
    return d


def _perf_row(d: pd.DataFrame, formula: str, spec: str) -> dict:
    rows = fit(d, formula, outcome="logcap", spec=spec, groups="team")
    row = rows[rows["term"] == "perf_z"]
    if row.empty:
        return {
            "spec": spec,
            "coef": np.nan,
            "se": np.nan,
            "ci_low": np.nan,
            "ci_high": np.nan,
            "p": np.nan,
            "n": 0,
            "r2": np.nan,
        }
    r = row.iloc[0]
    return {
        "spec": spec,
        "coef": float(r["coef"]),
        "se": float(r["se"]),
        "ci_low": float(r["ci_low"]),
        "ci_high": float(r["ci_high"]),
        "p": float(r["p"]),
        "n": int(r["n"]),
        "r2": float(r["r2"]),
    }


def build() -> tuple[pd.DataFrame, pd.DataFrame]:
    d = load_rent()
    rows = []
    model_rows = []
    for group in GROUPS:
        sub = d[d["pos_group"] == group].copy()
        raw = _perf_row(sub, "logcap ~ perf_z + age_start + years_exp", "raw")
        role = _perf_row(
            sub,
            "logcap ~ perf_z + snap_share + age_start + years_exp",
            "role",
        )
        for spec in (raw, role):
            model_rows.append({"pos_group": group, **spec})

        gap = raw["coef"] - role["coef"] if np.isfinite(raw["coef"]) and np.isfinite(role["coef"]) else np.nan
        gap_se = (
            np.sqrt(raw["se"] ** 2 + role["se"] ** 2)
            if np.isfinite(raw["se"]) and np.isfinite(role["se"])
            else np.nan
        )
        n = raw["n"]
        if n < MIN_EXPLORATORY or not np.isfinite(gap):
            status = "not_modeled"
        elif n < MIN_PRIMARY:
            status = "exploratory"
        else:
            status = "primary"

        # If the gap is non-positive, the role-controlled model is not cheaper.
        correction_gap = max(gap, 0.0) if np.isfinite(gap) else 0.0
        gap_lo = gap - 1.96 * gap_se if np.isfinite(gap_se) else np.nan
        gap_hi = gap + 1.96 * gap_se if np.isfinite(gap_se) else np.nan
        gap_uncertain = bool(np.isfinite(gap_lo) and gap_lo <= 0)
        notes = []
        if np.isfinite(gap) and gap <= 0:
            notes.append("no_correction")
        if status == "exploratory":
            notes.append("thin cell")
        if gap_uncertain:
            notes.append("gap CI includes zero")
        rows.append(
            {
                "pos_group": group,
                "n": n,
                "raw_coef": raw["coef"],
                "raw_ci_low": raw["ci_low"],
                "raw_ci_high": raw["ci_high"],
                "raw_p": raw["p"],
                "raw_r2": raw["r2"],
                "role_coef": role["coef"],
                "role_ci_low": role["ci_low"],
                "role_ci_high": role["ci_high"],
                "role_p": role["p"],
                "role_r2": role["r2"],
                "gap": gap,
                "gap_se_approx": gap_se,
                "gap_ci_low_approx": gap_lo,
                "gap_ci_high_approx": gap_hi,
                "gap_uncertain": gap_uncertain,
                "pricing_correction_low": 0.15 * correction_gap,
                "pricing_correction_base": 0.40 * correction_gap,
                "pricing_correction_high": 0.60 * correction_gap,
                "status": status,
                "note": "; ".join(notes),
            }
        )

    # OL has cap rows but no individual performance measure.
    rows.append(
        {
            "pos_group": "OL",
            "n": 0,
            "raw_coef": np.nan,
            "raw_ci_low": np.nan,
            "raw_ci_high": np.nan,
            "raw_p": np.nan,
            "raw_r2": np.nan,
            "role_coef": np.nan,
            "role_ci_low": np.nan,
            "role_ci_high": np.nan,
            "role_p": np.nan,
            "role_r2": np.nan,
            "gap": np.nan,
            "gap_se_approx": np.nan,
            "gap_ci_low_approx": np.nan,
            "gap_ci_high_approx": np.nan,
            "gap_uncertain": True,
            "pricing_correction_low": 0.0,
            "pricing_correction_base": 0.0,
            "pricing_correction_high": 0.0,
            "status": "not_modeled",
            "note": "no individual performance measure",
        }
    )
    return pd.DataFrame(rows), pd.DataFrame(model_rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    table, models = build()
    table.to_csv(OUT / "position_pricing.csv", index=False)
    models.to_csv(OUT / "position_pricing_models.csv", index=False)
    print(table.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
