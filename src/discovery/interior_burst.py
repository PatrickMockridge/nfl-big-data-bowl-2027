"""Interior defensive-line burst signal: drill translation and production.

Frozen protocol: ``docs/INTERIOR_BURST_PROTOCOL.md``. This module builds the
player-season sample, the in-sample/incremental/out-of-sample models, and the
market checks. It does not modify any existing output.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from sklearn.decomposition import PCA
from sklearn.metrics import r2_score
from sklearn.model_selection import GroupKFold

from data import load

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs" / "discovery"
PANEL = ROOT / "outputs" / "panel" / "panel_full.parquet"
CM = ROOT / "outputs" / "panel" / "combine_movement.parquet"
SAL = ROOT / "outputs" / "salary"
SEED = 20261019

PANEL_COLS = [
    "nfl_id",
    "season",
    "position_group",
    "position_subgroup",
    "nfl_position",
    "B_draft",
    "primary_team",
    "snaps",
    "games",
    "pass_rush_plays",
    "def_plays",
    "forty",
    "ten_yd_split",
    "draft_year",
]

PROD_COLS = [
    "game_id",
    "play_id",
    "team_abbr",
    "possession_team",
    "nfl_id",
    "player_get_off",
    "time_to_pressure",
    "sack",
    "tackle",
    "tackle_for_loss",
]


def _z(series: pd.Series) -> pd.Series:
    std = series.std(ddof=0)
    return (series - series.mean()) / std if std and not np.isnan(std) else series * 0.0


def _subgroup(players: pd.DataFrame) -> pd.Series:
    return np.where(
        players["nfl_position"].isin(["DE", "OLB"]),
        "EDGE",
        np.where(players["nfl_position"].isin(["DT", "NT"]), "INTERIOR", players["position_group"]),
    )


def build_metric() -> pd.DataFrame:
    """Burst score from the Combine movement components, scaled on the 510 cohort."""
    cm = pd.read_parquet(CM)
    players = load.load_players()[["nfl_id", "nfl_position", "position_group", "draft_year", "draft_overall_pick"]]
    players["position_subgroup"] = _subgroup(players)
    cm = cm.merge(players, on="nfl_id", how="left")
    cm["burst_raw"] = (cm["combine_speed"] + cm["combine_accel"]) / 2.0
    cm["burst_z"] = cm.groupby("position_subgroup")["burst_raw"].transform(_z)
    return cm


def build_production(
    cohort_ids: set[int], subgroup_map: pd.Series
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Player-season pressure/sack production and split-half reliability."""
    pp = load.load_player_play(usecols=PROD_COLS)
    games = load.load_games()[["game_id", "season", "season_type"]]
    pp = pp.merge(games, on="game_id", how="left")
    pp = pp[(pp["season_type"] == "REG") & pp["nfl_id"].isin(cohort_ids)].copy()
    pp["position_subgroup"] = pp["nfl_id"].map(subgroup_map)
    pp["is_defense"] = pp["team_abbr"] != pp["possession_team"]
    pp["pressure"] = pp["time_to_pressure"].notna()
    pp["sack_flag"] = pp["sack"].fillna(0).astype(bool)
    pp["tfl_flag"] = pp["tackle_for_loss"].fillna(0).astype(bool)
    pp["tackle_flag"] = pp["tackle"].fillna(0).astype(bool)
    pp["rush"] = pp["player_get_off"].notna()

    keys = ["nfl_id", "season"]
    prod = (
        pp.groupby(keys)
        .agg(
            def_snaps=("is_defense", "sum"),
            rush_snaps=("rush", "sum"),
            pressures=("pressure", "sum"),
            sacks=("sack_flag", "sum"),
            tfl=("tfl_flag", "sum"),
            tackles=("tackle_flag", "sum"),
        )
        .reset_index()
    )
    prod["pressure_rate"] = 100 * prod["pressures"] / prod["def_snaps"].replace(0, np.nan)
    prod["sack_rate"] = 100 * prod["sacks"] / prod["rush_snaps"].replace(0, np.nan)
    prod["tfl_rate"] = 100 * prod["tfl"] / prod["def_snaps"].replace(0, np.nan)
    prod["tackle_rate"] = 100 * prod["tackles"] / prod["def_snaps"].replace(0, np.nan)
    prod["rush_share"] = prod["rush_snaps"] / prod["def_snaps"].replace(0, np.nan)

    # Split-half reliability by play_id parity, per DL subgroup.
    pp["parity"] = pd.to_numeric(pp["play_id"], errors="coerce").fillna(-1).astype(int) % 2
    reliability = []
    for subgroup in ["INTERIOR", "EDGE"]:
        sub = pp[pp["position_subgroup"] == subgroup]
        halves = (
            sub.groupby(keys + ["parity"])
            .agg(
                def_snaps=("is_defense", "sum"),
                rush_snaps=("rush", "sum"),
                pressures=("pressure", "sum"),
                sacks=("sack_flag", "sum"),
            )
            .reset_index()
        )
        wide = halves.pivot_table(
            index=keys, columns="parity", values=["def_snaps", "rush_snaps", "pressures", "sacks"]
        )
        wide.columns = [f"{a}_{b}" for a, b in wide.columns]
        wide = wide.dropna(subset=["def_snaps_0", "def_snaps_1", "rush_snaps_0", "rush_snaps_1"])
        for label, num, den in [
            ("pressure_rate", "pressures", "def_snaps"),
            ("sack_rate", "sacks", "rush_snaps"),
        ]:
            wide[f"{label}_0"] = 100 * wide[f"{num}_0"] / wide[f"{den}_0"].replace(0, np.nan)
            wide[f"{label}_1"] = 100 * wide[f"{num}_1"] / wide[f"{den}_1"].replace(0, np.nan)
        for label in ["pressure_rate", "sack_rate"]:
            pair = wide[[f"{label}_0", f"{label}_1"]].dropna()
            r = float(pair.corr().iloc[0, 1]) if len(pair) > 2 else np.nan
            sb = 2 * r / (1 + r) if pd.notna(r) and r > -1 else np.nan
            reliability.append(
                {"outcome": label, "subgroup": subgroup, "r": r, "spearman_brown": sb, "n": len(pair)}
            )
    return prod, pd.DataFrame(reliability)


def build_players() -> tuple[pd.DataFrame, pd.DataFrame]:
    """One row per DL player-season with burst, production, and outcome z-scores."""
    panel = pd.read_parquet(PANEL)[PANEL_COLS].copy()
    metric = build_metric()
    cohort_ids = set(metric["nfl_id"].astype(int))
    subgroup_map = metric.drop_duplicates("nfl_id").set_index("nfl_id")["position_subgroup"]
    prod, reliability = build_production(cohort_ids, subgroup_map)
    d = (
        panel.merge(
            metric[["nfl_id", "combine_speed", "combine_accel", "burst_raw", "burst_z", "draft_overall_pick"]],
            on="nfl_id",
            how="left",
        )
        .merge(prod, on=["nfl_id", "season"], how="left")
    )
    d = d[(d["position_group"] == "DL") & d["burst_z"].notna() & d["def_snaps"].gt(0)].copy()
    d["season_c"] = d["season"].astype(str)
    d["snap_pg"] = d["snaps"] / d["games"].replace(0, np.nan)
    d["timed"] = d["forty"].notna() & d["ten_yd_split"].notna()
    for col in ["pressure_rate", "sack_rate", "tfl_rate", "tackle_rate"]:
        d[f"{col}_z"] = d.groupby(["position_subgroup", "season"])[col].transform(_z)
    # Traditional times, oriented so higher = better, standardized on the timed
    # INTERIOR sample (the drill-translation sample).
    d["speed_score"] = -d["forty"]
    d["split_score"] = -d["ten_yd_split"]
    timed = d["timed"] & d["position_subgroup"].eq("INTERIOR")
    d["z_forty"] = np.nan
    d["z_ten"] = np.nan
    d.loc[timed, "z_forty"] = _z(d.loc[timed, "speed_score"])
    d.loc[timed, "z_ten"] = _z(d.loc[timed, "split_score"])
    return d, reliability


def _fit(formula: str, data: pd.DataFrame):
    model = smf.ols(formula, data=data)
    used = model.data.row_labels
    groups = data.loc[used, "nfl_id"] if used is not None else data["nfl_id"]
    return model.fit(cov_type="cluster", cov_kwds={"groups": groups})


def _coef_rows(fit, model: str, outcome: str, subgroup: str, term: str, units: str) -> list[dict]:
    ci = fit.conf_int().loc[term]
    return [
        {
            "model": model,
            "outcome": outcome,
            "subgroup": subgroup,
            "term": term,
            "coef": float(fit.params[term]),
            "se": float(fit.bse[term]),
            "ci_low": float(ci[0]),
            "ci_high": float(ci[1]),
            "p": float(fit.pvalues[term]),
            "n": int(fit.nobs),
            "r2": float(fit.rsquared),
            "cluster": "nfl_id",
            "units": units,
        }
    ]


def fit_in_sample(d: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    outcomes = [
        ("pressure_rate_z", "z"),
        ("sack_rate_z", "z"),
        ("pressure_rate", "pp"),
        ("sack_rate", "pp"),
    ]
    for subgroup in ["INTERIOR", "EDGE"]:
        sub = d[d["position_subgroup"] == subgroup]
        for outcome, units in outcomes:
            fit = _fit(f"{outcome} ~ burst_z + B_draft + C(season_c)", sub)
            rows += _coef_rows(fit, f"in_sample_{subgroup.lower()}", outcome, subgroup, "burst_z", units)
    for outcome, units in [("pressure_rate_z", "z"), ("sack_rate_z", "z"), ("pressure_rate", "pp"), ("sack_rate", "pp")]:
        fit = _fit(f"{outcome} ~ burst_z * C(position_subgroup) + B_draft + C(season_c)", d)
        rows += _coef_rows(fit, "interaction", outcome, "DL", "burst_z", units)
        inter = [t for t in fit.params.index if t.startswith("burst_z:")]
        if inter:
            rows += _coef_rows(fit, "interaction", outcome, "DL", inter[0], units)
    return pd.DataFrame(rows)


def _incremental_models(sub: pd.DataFrame, outcome: str) -> dict[str, object]:
    specs = {
        "M0": f"{outcome} ~ B_draft + C(season_c)",
        "M_trad": f"{outcome} ~ z_forty + z_ten + B_draft + C(season_c)",
        "M_burst": f"{outcome} ~ burst_z + B_draft + C(season_c)",
        "M_both": f"{outcome} ~ burst_z + z_forty + z_ten + B_draft + C(season_c)",
    }
    return {name: _fit(formula, sub) for name, formula in specs.items()}


def fit_incremental(d: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: list[dict] = []
    validation: list[dict] = []
    for outcome in ["pressure_rate_z", "sack_rate_z"]:
        sub = d[
            d["timed"] & d["position_subgroup"].eq("INTERIOR") & d[outcome].notna()
        ].dropna(subset=["burst_z", "B_draft", "season_c", "z_forty", "z_ten"]).copy()
        if len(sub) < 20:
            continue
        fits = _incremental_models(sub, outcome)
        for name, fit in fits.items():
            rows.append(
                {
                    "outcome": outcome,
                    "model": name,
                    "r2": float(fit.rsquared),
                    "n": int(fit.nobs),
                    "cluster": "nfl_id",
                }
            )
        both, trad, burst = fits["M_both"], fits["M_trad"], fits["M_burst"]
        joint = both.f_test("z_forty = 0, z_ten = 0")
        rows.append(
            {
                "outcome": outcome,
                "model": "M_both",
                "r2": float(both.rsquared),
                "delta_burst_over_trad": float(both.rsquared - trad.rsquared),
                "delta_trad_over_burst": float(both.rsquared - burst.rsquared),
                "joint_f_p": float(joint.pvalue),
                "n": int(both.nobs),
                "cluster": "nfl_id",
            }
        )
        # OOF with the same folds.
        oof = {name: np.full(len(sub), np.nan) for name in fits}
        for tr, te in GroupKFold(5).split(sub, sub[outcome], sub["nfl_id"]):
            for name, rhs in {
                "M0": "B_draft + season",
                "M_trad": "z_forty + z_ten + B_draft + season",
                "M_burst": "burst_z + B_draft + season",
                "M_both": "burst_z + z_forty + z_ten + B_draft + season",
            }.items():
                fit = smf.ols(f"{outcome} ~ {rhs}", data=sub.iloc[tr]).fit()
                oof[name][te] = fit.predict(sub.iloc[te])
        for name in fits:
            validation.append(
                {
                    "check": "oof_r2",
                    "outcome": outcome,
                    "subgroup": "INTERIOR_timed",
                    "model": name,
                    "value": float(r2_score(sub[outcome], oof[name])),
                    "n": len(sub),
                }
            )
        # Temporal 2023-24 -> 2025, no unseen season FE.
        train, test = sub[sub["season"] < 2025], sub[sub["season"] == 2025]
        for name, rhs in {
            "M0": "B_draft",
            "M_trad": "z_forty + z_ten + B_draft",
            "M_burst": "burst_z + B_draft",
            "M_both": "burst_z + z_forty + z_ten + B_draft",
        }.items():
            fit = smf.ols(f"{outcome} ~ {rhs}", data=train).fit()
            validation.append(
                {
                    "check": "temporal_r2_2025",
                    "outcome": outcome,
                    "subgroup": "INTERIOR_timed",
                    "model": name,
                    "value": float(r2_score(test[outcome], fit.predict(test))),
                    "n": len(test),
                }
            )
        # LOSO.
        loso = np.full(len(sub), np.nan)
        for season in sorted(sub["season"].unique()):
            tr, te = sub[sub["season"] != season], sub[sub["season"] == season]
            fit = smf.ols(f"{outcome} ~ burst_z + B_draft + season", data=tr).fit()
            loso[sub["season"] == season] = fit.predict(te)
        validation.append(
            {
                "check": "loso_r2",
                "outcome": outcome,
                "subgroup": "INTERIOR_timed",
                "model": "M_burst",
                "value": float(r2_score(sub[outcome], loso)),
                "n": len(sub),
            }
        )
    return pd.DataFrame(rows), pd.DataFrame(validation)


def fit_robustness(d: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    interior = d[d["position_subgroup"] == "INTERIOR"].copy()
    for outcome in ["pressure_rate_z", "sack_rate_z"]:
        fit = _fit(f"{outcome} ~ burst_z + B_draft + C(season_c) + C(primary_team)", interior)
        rows += _coef_rows(fit, "team_fe", outcome, "INTERIOR", "burst_z", "z")
        fit = _fit(f"{outcome} ~ burst_z + B_draft + C(season_c) + rush_share + snap_pg", interior)
        rows += _coef_rows(fit, "role_controls", outcome, "INTERIOR", "burst_z", "z")
    # Specification curve.
    interior["speed_z"] = _z(interior["combine_speed"])
    interior["accel_z"] = _z(interior["combine_accel"])
    interior["rank_burst"] = (interior["combine_speed"].rank(pct=True) + interior["combine_accel"].rank(pct=True)) / 2
    pca = PCA(n_components=1).fit(interior[["speed_z", "accel_z"]].dropna())
    interior["pc1"] = pca.transform(interior[["speed_z", "accel_z"]].fillna(0))[:, 0]
    if interior[["pc1", "burst_z"]].corr().iloc[0, 1] < 0:
        interior["pc1"] = -interior["pc1"]
    for label, term in [
        ("speed_only", "speed_z"),
        ("accel_only", "accel_z"),
        ("equal_weight", "burst_z"),
        ("pc1", "pc1"),
        ("rank_average", "rank_burst"),
    ]:
        for outcome in ["pressure_rate_z", "sack_rate_z"]:
            fit = _fit(f"{outcome} ~ {term} + B_draft + C(season_c)", interior)
            rows += _coef_rows(fit, f"spec_{label}", outcome, "INTERIOR", term, "z")
    return pd.DataFrame(rows)


def fit_market(d: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    for subgroup in ["INTERIOR", "EDGE"]:
        sub = d[d["position_subgroup"] == subgroup]
        fit = _fit("B_draft ~ burst_z + C(season_c)", sub)
        rows += _coef_rows(fit, "draft", "B_draft", subgroup, "burst_z", "z")
    timed = d[
        d["timed"] & d["position_subgroup"].eq("INTERIOR") & d["draft_overall_pick"].notna()
    ].copy()
    timed["logpick"] = np.log(timed["draft_overall_pick"])
    fit = _fit("logpick ~ burst_z + z_forty + z_ten + C(season_c)", timed)
    rows += _coef_rows(fit, "draft_pick", "logpick", "INTERIOR_timed", "burst_z", "z")
    # Cap: nflverse production, IDL, with and without snap share.
    rent = pd.read_csv(SAL / "rent_players.csv")
    idl = rent[(rent["pos_group"] == "IDL") & rent["cap_number"].gt(0)].copy()
    idl["logcap"] = np.log(idl["cap_number"])
    for suffix, formula in [
        ("base", "logcap ~ perf_z + age_start + years_exp"),
        ("snap", "logcap ~ perf_z + snap_share + age_start + years_exp"),
    ]:
        fit = smf.ols(formula, data=idl).fit(cov_type="HC1")
        rows += _coef_rows(fit, f"cap_{suffix}", "logcap", "IDL", "perf_z", "log_points")
    return pd.DataFrame(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    d, reliability = build_players()
    d.to_parquet(OUT / "interior_burst_players.parquet", index=False)
    models = pd.concat(
        [fit_in_sample(d), fit_robustness(d), fit_market(d)],
        ignore_index=True,
    )
    models.to_csv(OUT / "interior_burst_models.csv", index=False)
    incremental, validation = fit_incremental(d)
    incremental.to_csv(OUT / "interior_burst_incremental.csv", index=False)
    rel_rows = reliability.assign(
        check="reliability",
        model="split_half",
        value=reliability["r"],
        ci_low=np.nan,
        ci_high=np.nan,
        extra=reliability["spearman_brown"],
    )[
        ["check", "outcome", "subgroup", "model", "value", "n", "ci_low", "ci_high", "extra"]
    ]
    val_rows = validation.assign(ci_low=np.nan, ci_high=np.nan, extra=np.nan)
    pd.concat([rel_rows, val_rows], ignore_index=True).to_csv(
        OUT / "interior_burst_validation.csv", index=False
    )
    print("players:", d.shape, "INTERIOR:", int((d.position_subgroup == "INTERIOR").sum()), "EDGE:", int((d.position_subgroup == "EDGE").sum()))
    print("timed INTERIOR:", int(((d.position_subgroup == "INTERIOR") & d.timed).sum()))
    print(reliability.to_string(index=False))
    print(models[models.model.str.startswith("in_sample")].to_string(index=False))
    print(incremental.to_string(index=False))


if __name__ == "__main__":
    main()
