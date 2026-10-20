"""Player-level free-agency pricing models.

Raw versus role-controlled performance on log APY, guarantees, and length.
All estimates are cross-sectional associations, not causal price effects.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from salary.analysis import fit

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "implications" / "free_agency" / "outputs"
CAP = ROOT / "outputs" / "salary" / "rent_players.csv"
GROUPS = ["QB", "RB", "WR", "TE", "EDGE", "IDL", "LB", "S", "CB"]


def prepare(d: pd.DataFrame, year_fe: bool = False) -> pd.DataFrame:
    d = d.copy()
    d["apy"] = pd.to_numeric(d["apy"], errors="coerce")
    d = d[d["apy"].gt(0) & d["perf_z"].notna()].copy()
    d["logapy"] = np.log(d["apy"])
    d["age_sq"] = d["age_at_signing"] ** 2
    d["team_change"] = d["team_change"].fillna(0).astype(int)
    d["one_year"] = d["one_year"].fillna(0).astype(int)
    d["rookie"] = d["rookie"].fillna(0).astype(int)
    d["pos_group"] = d["pos_group"].fillna("OTHER")
    if year_fe:
        d["signing_year_c"] = d["signing_year"].astype(str)
    return d


def _perf_terms(d: pd.DataFrame, spec: str, formula: str) -> pd.DataFrame:
    return fit(d, formula, outcome="logapy", spec=spec, groups="team")


def role_premium(
    d: pd.DataFrame,
    sample: str,
    year_fe: bool = False,
    extra: str = "",
    min_n: int = 60,
) -> tuple[dict, pd.DataFrame]:
    d = prepare(d, year_fe=year_fe)
    fe = " + C(signing_year_c)" if year_fe else ""
    base = (
        "logapy ~ perf_z + age_at_signing + age_sq + years_exp + team_change"
        f" + C(pos_group){fe}{extra}"
    )
    raw = _perf_terms(d, "raw", base)
    role = _perf_terms(d, "role", base + " + snap_share")
    r = raw[raw["term"].eq("perf_z")]
    c = role[role["term"].eq("perf_z")].iloc[0]
    raw_coef = float(r.iloc[0]["coef"])
    role_coef = float(c["coef"])
    gap = raw_coef - role_coef
    se = float(np.sqrt(r.iloc[0]["se"] ** 2 + c["se"] ** 2))
    n = int(r.iloc[0]["n"])
    return (
        {
            "sample": sample,
            "raw_coef": raw_coef,
            "raw_ci_low": float(r.iloc[0]["ci_low"]),
            "raw_ci_high": float(r.iloc[0]["ci_high"]),
            "role_coef": role_coef,
            "role_ci_low": float(c["ci_low"]),
            "role_ci_high": float(c["ci_high"]),
            "gap": gap,
            "gap_ci_low": gap - 1.96 * se,
            "gap_ci_high": gap + 1.96 * se,
            "n": n,
            "status": "primary" if n >= min_n else "exploratory",
        },
        pd.concat([raw, role], ignore_index=True),
    )


def cap_ledger_models() -> tuple[dict, pd.DataFrame]:
    d = pd.read_csv(CAP)
    d["logapy"] = np.log(d["cap_number"])
    d = d[d["logapy"].notna() & d["perf_z"].notna()].copy()
    base = "logapy ~ perf_z + age_start + years_exp + C(pos_group)"
    raw = fit(d, base, "logapy", "cap_raw", groups="team")
    role = fit(d, base + " + snap_share", "logapy", "cap_role", groups="team")
    r = raw[raw["term"].eq("perf_z")].iloc[0]
    c = role[role["term"].eq("perf_z")].iloc[0]
    gap = float(r["coef"]) - float(c["coef"])
    se = float(np.sqrt(r["se"] ** 2 + c["se"] ** 2))
    return (
        {
            "sample": "cap_ledger_2025",
            "raw_coef": float(r["coef"]),
            "raw_ci_low": float(r["ci_low"]),
            "raw_ci_high": float(r["ci_high"]),
            "role_coef": float(c["coef"]),
            "role_ci_low": float(c["ci_low"]),
            "role_ci_high": float(c["ci_high"]),
            "gap": gap,
            "gap_ci_low": gap - 1.96 * se,
            "gap_ci_high": gap + 1.96 * se,
            "n": int(r["n"]),
            "status": "primary",
        },
        pd.concat([raw, role], ignore_index=True),
    )


def by_position(d: pd.DataFrame, sample: str) -> pd.DataFrame:
    d = prepare(d)
    rows = []
    for pos, cell in d.groupby("pos_group"):
        if pos in {"OL", "ST", "OTHER"} or len(cell) < 15:
            continue
        base = (
            "logapy ~ perf_z + age_at_signing + age_sq + years_exp + team_change"
        )
        try:
            raw = fit(cell, base, "logapy", f"{sample}_raw", groups="team")
            role = fit(cell, base + " + snap_share", "logapy", f"{sample}_role", groups="team")
            r = raw[raw["term"].eq("perf_z")].iloc[0]
            c = role[role["term"].eq("perf_z")].iloc[0]
            gap = float(r["coef"]) - float(c["coef"])
            se = float(np.sqrt(r["se"] ** 2 + c["se"] ** 2))
            rows.append(
                {
                    "sample": sample,
                    "pos_group": pos,
                    "n": int(r["n"]),
                    "raw_coef": float(r["coef"]),
                    "role_coef": float(c["coef"]),
                    "gap": gap,
                    "gap_ci_low": gap - 1.96 * se,
                    "gap_ci_high": gap + 1.96 * se,
                    "raw_ci_low": float(r["ci_low"]),
                    "raw_ci_high": float(r["ci_high"]),
                    "role_ci_low": float(c["ci_low"]),
                    "role_ci_high": float(c["ci_high"]),
                    "status": "primary" if r["n"] >= 60 else "exploratory",
                }
            )
        except Exception as exc:  # pragma: no cover - thin cells
            print(f"  {sample} {pos} skipped: {exc}")
    return pd.DataFrame(rows)


def cap_by_position() -> pd.DataFrame:
    d = pd.read_csv(CAP)
    d["logapy"] = np.log(d["cap_number"])
    rows = []
    for pos, cell in d.groupby("pos_group"):
        if len(cell) < 15:
            continue
        base = "logapy ~ perf_z + age_start + years_exp"
        try:
            raw = fit(cell, base, "logapy", "cap_raw", groups="team")
            role = fit(cell, base + " + snap_share", "logapy", "cap_role", groups="team")
            r = raw[raw["term"].eq("perf_z")].iloc[0]
            c = role[role["term"].eq("perf_z")].iloc[0]
            gap = float(r["coef"]) - float(c["coef"])
            se = float(np.sqrt(r["se"] ** 2 + c["se"] ** 2))
            rows.append(
                {
                    "sample": "cap_ledger_2025",
                    "pos_group": pos,
                    "n": int(r["n"]),
                    "raw_coef": float(r["coef"]),
                    "role_coef": float(c["coef"]),
                    "gap": gap,
                    "gap_ci_low": gap - 1.96 * se,
                    "gap_ci_high": gap + 1.96 * se,
                    "raw_ci_low": float(r["ci_low"]),
                    "raw_ci_high": float(r["ci_high"]),
                    "role_ci_low": float(c["ci_low"]),
                    "role_ci_high": float(c["ci_high"]),
                    "status": "primary" if r["n"] >= 80 else "exploratory",
                }
            )
        except Exception as exc:  # pragma: no cover
            print(f"  cap {pos} skipped: {exc}")
    return pd.DataFrame(rows)


def guarantee_years(d: pd.DataFrame, sample: str) -> pd.DataFrame:
    d = prepare(d, year_fe=True)
    d = d[d["guarantee_share"].notna() & d["years"].notna()].copy()
    d = d.dropna(subset=[
        "guarantee_share", "years", "perf_z", "snap_share", "age_at_signing",
        "age_sq", "team_change", "pos_group", "signing_year_c",
    ])
    base = (
        " + perf_z + snap_share + age_at_signing + age_sq + years"
        " + team_change + C(pos_group) + C(signing_year_c)"
    )
    rows = []
    for outcome, formula in [
        ("guarantee_share", "guarantee_share ~ 1" + base),
        ("years", "years ~ 1" + base.replace(" + years", "")),
    ]:
        try:
            model = smf.ols(formula, data=d).fit(
                cov_type="cluster", cov_kwds={"groups": d["team"]}
            )
            for term in model.params.index:
                if term == "Intercept" or term.startswith("C("):
                    continue
                ci = model.conf_int().loc[term]
                rows.append(
                    {
                        "sample": sample,
                        "outcome": outcome,
                        "term": term,
                        "coef": float(model.params[term]),
                        "se": float(model.bse[term]),
                        "ci_low": float(ci[0]),
                        "ci_high": float(ci[1]),
                        "p": float(model.pvalues[term]),
                        "n": int(model.nobs),
                        "r2": float(model.rsquared),
                    }
                )
        except Exception as exc:  # pragma: no cover
            print(f"  {outcome} skipped: {exc}")
    return pd.DataFrame(rows)


def free_agent_interactions(d: pd.DataFrame, sample: str) -> pd.DataFrame:
    d = prepare(d)
    d = d.dropna(subset=[
        "logapy", "perf_z", "snap_share", "age_at_signing", "age_sq",
        "years_exp", "team_change", "pos_group", "team",
    ])
    formula = (
        "logapy ~ perf_z * team_change + snap_share * team_change"
        " + age_at_signing + age_sq + years_exp + C(pos_group)"
    )
    model = smf.ols(formula, data=d).fit(
        cov_type="cluster", cov_kwds={"groups": d["team"]}
    )
    rows = []
    for term in model.params.index:
        if term == "Intercept" or term.startswith("C("):
            continue
        ci = model.conf_int().loc[term]
        rows.append(
            {
                "sample": sample,
                "term": term,
                "coef": float(model.params[term]),
                "se": float(model.bse[term]),
                "ci_low": float(ci[0]),
                "ci_high": float(ci[1]),
                "p": float(model.pvalues[term]),
                "n": int(model.nobs),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    fa = pd.read_csv(OUT / "fa_class_2026.csv")
    apy25 = pd.read_csv(OUT / "contract_events_2025.csv")
    apy24 = pd.read_csv(OUT / "contract_events_2024.csv")

    premiums = []
    models = []
    for d, sample, year_fe in [
        (fa, "fa_2026", False),
        (apy25, "apy_2025", True),
        (apy24, "apy_2024", True),
    ]:
        row, m = role_premium(d, sample, year_fe=year_fe)
        premiums.append(row)
        models.append(m)
    # Expected-role / commitment sensitivity: contract length and guarantee
    # share are proxies for the role the team expects to buy.
    for label, extra in [
        ("fa_2026_years", " + years"),
        ("fa_2026_guarantee", " + guarantee_share"),
        ("fa_2026_expected_role", " + years + guarantee_share"),
    ]:
        row, m = role_premium(fa, label, extra=extra, min_n=60)
        premiums.append(row)
        models.append(m)
    cap_row, cap_models = cap_ledger_models()
    premiums.append(cap_row)
    models.append(cap_models)

    # Draft-matched robustness on the 2026 sample.
    fa_draft = fa.copy()
    fa_draft["B_draft"] = fa_draft["B_draft"].fillna(0)
    row, m = role_premium(
        fa_draft, "fa_2026_draft_matched", extra=" + B_draft", min_n=60
    )
    premiums.append(row)
    models.append(m)

    # Team-FE sensitivity on the 2025 APY sample.
    row, m = role_premium(
        apy25, "apy_2025_team_fe", year_fe=True, extra=" + C(team)", min_n=60
    )
    premiums.append(row)
    models.append(m)

    pd.concat(models, ignore_index=True).to_csv(
        OUT / "pricing_models.csv", index=False
    )
    premium = pd.DataFrame(premiums)
    premium.to_csv(OUT / "role_premium.csv", index=False)

    by_pos = pd.concat(
        [by_position(fa, "fa_2026"), by_position(apy25, "apy_2025"), cap_by_position()],
        ignore_index=True,
    )
    by_pos.to_csv(OUT / "pricing_by_position.csv", index=False)

    g = pd.concat(
        [guarantee_years(fa, "fa_2026"), guarantee_years(apy25, "apy_2025")],
        ignore_index=True,
    )
    g.to_csv(OUT / "guarantee_years_models.csv", index=False)

    inter = pd.concat(
        [free_agent_interactions(fa, "fa_2026"),
         free_agent_interactions(apy25, "apy_2025")],
        ignore_index=True,
    )
    inter.to_csv(OUT / "free_agent_interactions.csv", index=False)

    print(premium.round(3).to_string(index=False))
    print("\nby position:")
    print(by_pos.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
