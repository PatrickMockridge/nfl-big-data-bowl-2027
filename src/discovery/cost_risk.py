"""Cost-risk artifacts for the kept entry.

Builds the position-specific Combine table, the signed net-rent summaries, the
nested pay model, the performance-role allocation gap, and the volatility
robustness table. All analyses are exploratory; see
``docs/PREREGISTRATION_v2.md`` amendments 1-3.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from data import load
from discovery import combine_linkage
from discovery.rent import _load as _load_volatility
from discovery.role_allocation import _z_by

ROOT = Path(__file__).resolve().parents[2]
DISC = ROOT / "outputs" / "discovery"
SAL = ROOT / "outputs" / "salary"
PANEL = ROOT / "outputs" / "panel" / "panel_full.parquet"
RNG = np.random.default_rng(20261019)


def _fit(formula: str, data: pd.DataFrame, cluster: str = "nfl_id"):
    model = smf.ols(formula, data=data)
    used = model.data.row_labels
    groups = data.loc[used, cluster] if used is not None else data[cluster]
    return model.fit(cov_type="cluster", cov_kwds={"groups": groups})


def _row(fit, term: str, **extra) -> dict:
    ci = fit.conf_int().loc[term]
    out = {
        "term": term,
        "coef": float(fit.params[term]),
        "se": float(fit.bse[term]),
        "ci_low": float(ci[0]),
        "ci_high": float(ci[1]),
        "p": float(fit.pvalues[term]),
        "n": int(fit.nobs),
        "r2": float(fit.rsquared),
    }
    out.update(extra)
    return out


# ---------------------------------------------------------------------------
# 1. Position-specific Combine -> performance
# ---------------------------------------------------------------------------


def combine_by_position() -> pd.DataFrame:
    perf, _ = combine_linkage.samples()
    rows = []
    for group in ["DL", "WR", "OL", "TE"]:
        sub = perf[perf["position_group"] == group].copy()
        fit = _fit("perf_z ~ combine_movement + B_draft + C(season_c)", sub)
        sd_x = float(sub["combine_movement"].std(ddof=0))
        sd_y = float(sub["perf_z"].std(ddof=0))
        rows.append(
            _row(
                fit,
                "combine_movement",
                sample="by_position",
                position_group=group,
                std_beta=float(fit.params["combine_movement"] * sd_x / sd_y) if sd_y else np.nan,
                sd_x=sd_x,
                sd_y=sd_y,
            )
        )
    pooled = _fit(
        "perf_z ~ combine_movement + B_draft + C(position_group) + C(season_c)", perf
    )
    sd_x = float(perf["combine_movement"].std(ddof=0))
    sd_y = float(perf["perf_z"].std(ddof=0))
    rows.append(
        _row(
            pooled,
            "combine_movement",
            sample="pooled",
            position_group="ALL",
            std_beta=float(pooled.params["combine_movement"] * sd_x / sd_y) if sd_y else np.nan,
            sd_x=sd_x,
            sd_y=sd_y,
        )
    )
    inter = _fit(
        "perf_z ~ combine_movement * C(position_group) + B_draft + C(season_c)", perf
    )
    terms = [t for t in inter.params.index if t.startswith("combine_movement:")]
    joint = inter.f_test(", ".join(f"{t} = 0" for t in terms)) if terms else None
    rows.append(
        {
            "term": "interaction_joint",
            "coef": np.nan,
            "se": np.nan,
            "ci_low": np.nan,
            "ci_high": np.nan,
            "p": float(joint.pvalue) if joint is not None else np.nan,
            "n": int(inter.nobs),
            "r2": float(inter.rsquared),
            "sample": "interaction",
            "position_group": "ALL",
            "std_beta": np.nan,
            "sd_x": np.nan,
            "sd_y": np.nan,
        }
    )
    out = pd.DataFrame(rows)
    out.to_csv(DISC / "combine_linkage_by_position.csv", index=False)
    return out


# ---------------------------------------------------------------------------
# 2. Signed net rent and nested pay model
# ---------------------------------------------------------------------------


def _rent_players() -> pd.DataFrame:
    rent = pd.read_csv(SAL / "rent_players.csv")
    mapping = pd.read_csv(
        ROOT / "data" / "external" / "players.csv", usecols=["gsis_id", "nfl_id"]
    )
    rent = rent.merge(mapping, on="gsis_id", how="left")
    panel = pd.read_parquet(PANEL)
    p25 = (
        panel[panel["season"].eq(2025)][["nfl_id", "B_draft"]]
        .drop_duplicates("nfl_id")
    )
    rent = rent.merge(p25, on="nfl_id", how="left")
    rent["logcap"] = np.log(rent["cap_number"].where(rent["cap_number"].gt(0)))
    rent["age_grp"] = pd.cut(
        rent["age_start"], [0, 23, 25, 27, 29, 100], labels=["<=23", "24-25", "26-27", "28-29", "30+"]
    )
    rent["cap_q"] = pd.qcut(rent["cap_number"], 4, labels=["Q1", "Q2", "Q3", "Q4"])
    rent["star_only"] = rent["star"].eq(1) & rent["underperformer"].ne(1)
    rent["under_only"] = rent["underperformer"].eq(1) & rent["star"].ne(1)
    rent["both"] = rent["star"].eq(1) & rent["underperformer"].eq(1)
    rent["young_high_perf"] = rent["young"].eq(1) & rent["high_perf"].eq(1)
    return rent


def _status_bucket(d: pd.DataFrame) -> pd.Series:
    out = pd.Series("other", index=d.index)
    out[d["young_high_perf"]] = "young high performer"
    out[d["both"]] = "star & underperformer"
    out[d["under_only"]] = "underperformer only"
    out[d["star_only"]] = "star only"
    return out


def net_rent() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rent = _rent_players().copy()
    rent["status_bucket"] = _status_bucket(rent)
    # Existing signed residual (base pay model) for the descriptive groups.
    rent["resid_cap"] = rent["resid_cap"].astype(float)

    groups = []
    for label, col in [
        ("cap_quartile", "cap_q"),
        ("age_group", "age_grp"),
        ("status", "status_bucket"),
    ]:
        for key, sub in rent.groupby(col, observed=True):
            groups.append(
                {
                    "grouping": label,
                    "group": str(key),
                    "n": len(sub),
                    "mean_m": sub["resid_cap"].mean() / 1e6,
                    "median_m": sub["resid_cap"].median() / 1e6,
                    "share_positive": float((sub["resid_cap"] > 0).mean()),
                    "total_m": sub["resid_cap"].sum() / 1e6,
                }
            )
    sub = rent.dropna(subset=["B_draft"]).copy()
    sub["draft_q"] = pd.qcut(sub["B_draft"], 4, labels=["Q1 late/UDFA", "Q2", "Q3", "Q4 early"])
    for key, g in sub.groupby("draft_q", observed=True):
        groups.append(
            {
                "grouping": "draft_quartile_2025",
                "group": str(key),
                "n": len(g),
                "mean_m": g["resid_cap"].mean() / 1e6,
                "median_m": g["resid_cap"].median() / 1e6,
                "share_positive": float((g["resid_cap"] > 0).mean()),
                "total_m": g["resid_cap"].sum() / 1e6,
            }
        )
    groups = pd.DataFrame(groups)

    # Nested pay model on the same draft-matched sample.
    nested = []
    sample = rent.dropna(subset=["B_draft"]).copy()
    specs = {
        "base": "logcap ~ perf_z + age_start + years_exp + C(pos_group)",
        "role": "logcap ~ perf_z + snap_share + age_start + years_exp + C(pos_group)",
        "role_draft": "logcap ~ perf_z + snap_share + B_draft + age_start + years_exp + C(pos_group)",
    }
    for name, formula in specs.items():
        fit = _fit(formula, sample, cluster="team")
        nested.append(
            _row(
                fit,
                "perf_z",
                model=name,
                n_terms=int(len(fit.params)),
                note="team-clustered; draft-matched sample",
            )
        )
        if name == "role_draft":
            nested.append(_row(fit, "B_draft", model=name, n_terms=int(len(fit.params))))
    nested = pd.DataFrame(nested)

    # Team signed net rent.
    team = (
        rent.groupby("team")
        .agg(net_rent_cap=("resid_cap", "sum"), n_players=("player", "size"))
        .reset_index()
    )
    team = team.merge(
        pd.read_csv(SAL / "rent_team.csv")[["team", "wins_per_100m", "eff_quartile"]],
        on="team",
        how="left",
    )
    payroll = pd.read_csv(SAL / "team_salary_panel.csv").query("season == 2025")[
        ["team", "log_payroll", "payroll_od"]
    ]
    team = team.merge(payroll, on="team", how="left")
    team["net_rent_m"] = team["net_rent_cap"] / 1e6
    team.to_csv(SAL / "net_rent_team.csv", index=False)
    groups.to_csv(SAL / "net_rent_groups.csv", index=False)
    nested.to_csv(SAL / "pay_model_nested.csv", index=False)
    return groups, nested, team


# ---------------------------------------------------------------------------
# 3. Performance-role allocation gap
# ---------------------------------------------------------------------------


def _gap_table(frame: pd.DataFrame, label: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    d = frame.copy()
    d["gap"] = d["perf_z"] - d["role_z"]
    d["draft_q"] = pd.qcut(d["B_draft"], 4, labels=["Q1 late/UDFA", "Q2", "Q3", "Q4 early"])
    d["perf_t"] = pd.qcut(d["perf_z"], 3, labels=["low", "mid", "high"])
    d["role_t"] = pd.qcut(d["role_z"], 3, labels=["low", "mid", "high"])
    d["perf_q"] = pd.qcut(d["perf_z"], 4, labels=["P1", "P2", "P3", "P4"])
    d["role_q"] = pd.qcut(d["role_z"], 4, labels=["R1", "R2", "R3", "R4"])
    d["sample"] = label

    groups = (
        d.groupby("draft_q", observed=True)
        .agg(n=("gap", "size"), mean_gap=("gap", "mean"), median_gap=("gap", "median"))
        .reset_index()
    )
    groups["sample"] = label

    tail = d[(d["perf_t"] == "high") & (d["role_t"] == "low")]
    strict = d[(d["perf_q"] == "P4") & (d["role_q"] == "R1")]
    tails = pd.DataFrame(
        [
            {
                "sample": label,
                "tail": "top performance tercile / bottom role tercile",
                "n": len(tail),
                "players": int(tail["nfl_id"].nunique()),
                "mean_gap": float(tail["gap"].mean()),
                "next_role": float(tail["next_role"].mean()),
                "mean_B_draft": float(tail["B_draft"].mean()),
            },
            {
                "sample": label,
                "tail": "top performance quartile / bottom role quartile",
                "n": len(strict),
                "players": int(strict["nfl_id"].nunique()),
                "mean_gap": float(strict["gap"].mean()),
                "next_role": float(strict["next_role"].mean()),
                "mean_B_draft": float(strict["B_draft"].mean()),
            },
        ]
    )
    return d, groups, tails


def allocation_gap() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    full = pd.read_parquet(DISC / "role_allocation_player_seasons_full.parquet")
    reliable = pd.read_parquet(DISC / "role_allocation_player_seasons.parquet")
    f, fg, ft = _gap_table(full, "full_233")
    r, rg, rt = _gap_table(reliable, "reliable_192")
    players = pd.concat([f, r], ignore_index=True)
    groups = pd.concat([fg, rg], ignore_index=True)
    tails = pd.concat([ft, rt], ignore_index=True)
    players.to_parquet(DISC / "allocation_gap.parquet", index=False)
    groups.to_csv(DISC / "allocation_gap_groups.csv", index=False)
    tails.to_csv(DISC / "allocation_gap_tails.csv", index=False)
    return players, groups, tails


# ---------------------------------------------------------------------------
# 4. Volatility -> role gap robustness
# ---------------------------------------------------------------------------


def volatility_role_gap() -> pd.DataFrame:
    d = _load_volatility()
    d = d.dropna(subset=["volatility", "age", "experience", "role_z", "role_gap"]).copy()
    specs = {
        "base": "role_gap ~ volatility + age + experience + B_draft + C(position_group)",
        "season_fe": "role_gap ~ volatility + age + experience + B_draft + C(position_group) + C(season_c)",
        "role_control": "role_gap ~ volatility + role_z + age + experience + B_draft + C(position_group)",
        "role_play_control": "role_gap ~ volatility + role_z + snaps + age + experience + B_draft + C(position_group)",
        "next_role": "next_role ~ perf_z + volatility + age + experience + B_draft + role_z + C(position_group) + C(season_c)",
    }
    rows = []
    for name, formula in specs.items():
        try:
            fit = _fit(formula, d)
        except Exception as exc:  # pragma: no cover - defensive
            rows.append({"model": name, "term": "volatility", "error": str(exc), "n": len(d)})
            continue
        rows.append(_row(fit, "volatility", model=name))
    out = pd.DataFrame(rows)
    out.to_csv(DISC / "volatility_role_gap.csv", index=False)
    return out


def main() -> None:
    DISC.mkdir(parents=True, exist_ok=True)
    print("combine by position")
    print(combine_by_position().to_string(index=False))
    print("\nnet rent")
    groups, nested, team = net_rent()
    print(groups.to_string(index=False))
    print(nested.to_string(index=False))
    print("\nallocation gap")
    _, gap_groups, tails = allocation_gap()
    print(gap_groups.to_string(index=False))
    print(tails.to_string(index=False))
    print("\nvolatility")
    print(volatility_role_gap().to_string(index=False))


if __name__ == "__main__":
    main()
