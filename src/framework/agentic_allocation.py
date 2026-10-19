"""A two-agent allocation model: coach role rule, GM pay rule.

The model is a transparent decision model, not a causal identification. It
calibrates the coach's role equation and the GM's pay equation to the observed
moments, measures the performance-weight wedge, and simulates the lever:
what happens to the top-performance group's role if the coach weights
performance like the cap does, or reduces the draft/status weight.

Outputs:
- outputs/discovery/agentic_allocation_moments.csv
- outputs/discovery/agentic_allocation_levers.csv
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[2]
DISC = ROOT / "outputs" / "discovery"
SAL = ROOT / "outputs" / "salary"
PANEL = ROOT / "outputs" / "panel" / "panel_full.parquet"
ROLE = DISC / "role_allocation_player_seasons_full.parquet"
RENT = SAL / "rent_players.csv"


def _fit(formula: str, data: pd.DataFrame, cluster: str):
    model = smf.ols(formula, data=data)
    used = model.data.row_labels
    groups = data.loc[used, cluster] if used is not None else data[cluster]
    return model.fit(cov_type="cluster", cov_kwds={"groups": groups})


def _pay_sample() -> pd.DataFrame:
    rent = pd.read_csv(RENT)
    mapping = pd.read_csv(
        ROOT / "data" / "external" / "players.csv", usecols=["gsis_id", "nfl_id"]
    )
    rent = rent.merge(mapping, on="gsis_id", how="left")
    rent["logcap"] = np.log(rent["cap_number"].where(rent["cap_number"].gt(0)))
    return rent


def build() -> tuple[pd.DataFrame, pd.DataFrame]:
    role = pd.read_parquet(ROLE).copy()
    role["season_c"] = role["season"].astype(str)
    role_fit = _fit(
        "role_z ~ perf_z + B_draft + prestige_nodraft + C(position_group) + C(season_c)",
        role,
        "nfl_id",
    )
    pay = _pay_sample()
    pay_fit = _fit(
        "logcap ~ perf_z + snap_share + age_start + years_exp + C(pos_group)",
        pay,
        "team",
    )

    beta_c = float(role_fit.params["perf_z"])
    gamma_c = float(role_fit.params["B_draft"])
    alpha_g = float(pay_fit.params["perf_z"])
    ci_c = role_fit.conf_int().loc["perf_z"].tolist()
    ci_g = pay_fit.conf_int().loc["perf_z"].tolist()

    # The observed role equation's fitted values; the lever shifts the
    # performance or status coefficient and re-predicts role.
    base_role = role_fit.predict(role)
    top = role["perf_z"] >= role["perf_z"].quantile(0.75)
    moments = pd.DataFrame(
        [
            {
                "agent": "coach",
                "decision": "role",
                "term": "performance",
                "coef": beta_c,
                "ci_low": ci_c[0],
                "ci_high": ci_c[1],
                "n": int(role_fit.nobs),
                "note": "concurrent role model; calibrated",
            },
            {
                "agent": "coach",
                "decision": "role",
                "term": "draft_status",
                "coef": gamma_c,
                "ci_low": float(role_fit.conf_int().loc["B_draft", 0]),
                "ci_high": float(role_fit.conf_int().loc["B_draft", 1]),
                "n": int(role_fit.nobs),
                "note": "concurrent role model; calibrated",
            },
            {
                "agent": "gm",
                "decision": "pay",
                "term": "performance",
                "coef": alpha_g,
                "ci_low": ci_g[0],
                "ci_high": ci_g[1],
                "n": int(pay_fit.nobs),
                "note": "full 909-player pay model; calibrated",
            },
        ]
    )
    moments = pd.concat(
        [
            moments,
            pd.DataFrame(
                [
                    {
                        "agent": "wedge",
                        "decision": "performance_weight",
                        "term": "gm_minus_coach",
                        "coef": alpha_g - beta_c,
                        "ci_low": np.nan,
                        "ci_high": np.nan,
                        "n": np.nan,
                        "note": "GM performance weight minus coach performance weight",
                    }
                ]
            ),
        ],
        ignore_index=True,
    )

    # Lever: coach performance weight from observed to GM weight. The status
    # lever was tested and failed its directional validation (the top-performance
    # group is draft-correlated), so it is not used.
    tail = (role["perf_z"] >= role["perf_z"].quantile(0.75)) & (
        role["role_z"] <= role["role_z"].quantile(0.25)
    )
    base_tail = float(base_role[tail].mean())
    betas = np.linspace(beta_c, alpha_g, 9)
    perf_lever = []
    for beta in betas:
        cf = base_role + (beta - beta_c) * role["perf_z"]
        perf_lever.append(
            {
                "lever": "coach_performance_weight",
                "value": float(beta),
                "top_perf_role": float(cf[top].mean()),
                "allocation_gap": float((role["perf_z"] - cf).mean()),
                "expected_production": float((role["perf_z"] * cf).mean()),
                "strict_tail_gain": float(cf[tail].mean() - base_tail),
            }
        )
    levers = pd.DataFrame(perf_lever)

    # Negative control: shuffle performance within position and season; the
    # coach's performance coefficient should collapse toward zero.
    rng = np.random.default_rng(20261020)
    shuffled = role.copy()
    shuffled["perf_z"] = shuffled.groupby(["position_group", "season"])["perf_z"].transform(
        lambda s: rng.permutation(s.to_numpy())
    )
    shuf_fit = _fit(
        "role_z ~ perf_z + B_draft + prestige_nodraft + C(position_group) + C(season_c)",
        shuffled,
        "nfl_id",
    )
    control = pd.DataFrame(
        [
            {
                "real_coach_perf": beta_c,
                "shuffled_coach_perf": float(shuf_fit.params["perf_z"]),
                "real_p": float(role_fit.pvalues["perf_z"]),
                "shuffled_p": float(shuf_fit.pvalues["perf_z"]),
                "n": int(role_fit.nobs),
            }
        ]
    )
    moments.to_csv(DISC / "agentic_allocation_moments.csv", index=False)
    levers.to_csv(DISC / "agentic_allocation_levers.csv", index=False)
    control.to_csv(DISC / "agentic_allocation_control.csv", index=False)
    return moments, levers


def main() -> None:
    moments, levers = build()
    print(moments.to_string(index=False))
    print("\nLevers:")
    print(levers.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
