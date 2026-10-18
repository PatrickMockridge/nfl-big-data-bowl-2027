"""Explicit 10 Hz Combine-tracking -> regular-season performance/role linkage.

The generic Combine movement composite (first-step acceleration, path
efficiency, top speed, -time to 1 yd) is tested against context-adjusted
performance and role, with the DL Yellow lens reported alongside.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs" / "discovery"


def _fit(formula: str, data: pd.DataFrame):
    return smf.ols(formula, data=data).fit(
        cov_type="cluster", cov_kwds={"groups": data["nfl_id"]}
    )


PERF_FORMULA = "perf_z ~ combine_movement + B_draft + C(position_group) + C(season_c)"
ROLE_FORMULA = "role_z ~ combine_movement + B_draft + C(position_group) + C(season_c)"
GAP_FORMULA = "role_gap ~ combine_movement + role_z + B_draft + C(position_group)"


def movement_cohort() -> pd.DataFrame:
    """All Combine participants with a movement score (the 510-player cohort)."""
    cm = pd.read_parquet(ROOT / "outputs" / "panel" / "combine_movement.parquet")
    return cm.dropna(subset=["combine_movement"]).copy()


def samples() -> tuple[pd.DataFrame, pd.DataFrame]:
    """The exact estimation samples used by :func:`build`."""
    cm = movement_cohort()
    panel = pd.read_parquet(ROOT / "outputs" / "panel" / "panel_full.parquet")
    role = pd.read_parquet(OUT / "role_allocation_player_seasons.parquet")
    role = role[role["role_gap"].notna()].copy()

    perf_sample = (
        panel.merge(cm, on="nfl_id", how="left")
        .dropna(subset=["combine_movement", "perf_z"])
        .query("position_group != 'DB'")
        .copy()
    )
    perf_sample["season_c"] = perf_sample["season"].astype(str)
    role_sample = (
        role.merge(cm, on="nfl_id", how="left")
        .dropna(subset=["combine_movement"])
        .query("position_group != 'DB'")
        .copy()
    )
    role_sample["season_c"] = role_sample["season"].astype(str)
    return perf_sample, role_sample


def fit_models(
    perf_sample: pd.DataFrame | None = None,
    role_sample: pd.DataFrame | None = None,
) -> dict[str, tuple[object, pd.DataFrame]]:
    """Fit the three linkage models and return ``label -> (fit, data)``."""
    if perf_sample is None or role_sample is None:
        perf_sample, role_sample = samples()
    return {
        "performance": (_fit(PERF_FORMULA, perf_sample), perf_sample),
        "role": (_fit(ROLE_FORMULA, role_sample), role_sample),
        "role gap (role-controlled)": (_fit(GAP_FORMULA, role_sample), role_sample),
    }


def partial_residual(fit, data: pd.DataFrame, term: str = "combine_movement") -> pd.Series:
    """The outcome with the controls held constant (coefficient × term + residual)."""
    return fit.resid + fit.params[term] * data[term]


def build() -> pd.DataFrame:
    rows = []
    for label, (fit, _) in fit_models().items():
        rows.append(
            {
                "outcome": label,
                "term": "combine_movement",
                "coef": float(fit.params["combine_movement"]),
                "ci_low": float(fit.conf_int().loc["combine_movement", 0]),
                "ci_high": float(fit.conf_int().loc["combine_movement", 1]),
                "p": float(fit.pvalues["combine_movement"]),
                "n": int(fit.nobs),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df = build()
    df.to_csv(OUT / "combine_linkage.csv", index=False)
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
