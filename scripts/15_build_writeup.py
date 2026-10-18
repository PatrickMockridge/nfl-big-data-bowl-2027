"""Historical builder for the old DL-only tables; not used by the final submission.

The final writeup tables are in ``writeup/submission.md``. This script retains
the earlier DL-only outputs, including the rent/predictability labels that were
cut after adversarial review. Do not cite it.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DISC = ROOT / "outputs" / "discovery"
OUT = ROOT / "writeup"
OUT.mkdir(parents=True, exist_ok=True)


def fmt(row: pd.Series) -> str:
    coef = row["coef"]
    lo = row["ci_low"]
    hi = row["ci_high"]
    p = row["p"]
    star = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
    return f"{coef:+.3f}{star} ({lo:+.3f}, {hi:+.3f})"


def table2() -> str:
    coef = pd.read_csv(DISC / "role_allocation_coefficients.csv")
    rent = pd.read_csv(DISC / "rent_coefficients.csv")
    rows = []
    model_labels = {
        "concurrent_role": "Concurrent role",
        "next_role_full": "Next-season role (with current role)",
        "next2_role_full": "Role at t+2",
        "career_status_gap": "Career status",
        "career_start_rate_gap": "Career start rate",
        "rent_career_status": "Rent: career status",
        "rent_start_rate": "Rent: start rate",
    }
    term_labels = {
        "role_z": "Current role",
        "perf_z": "Performance",
        "B_draft": "Draft capital",
        "role_gap": "Role gap",
        "prestige": "Prestige",
        "role": "Role",
        "perf": "Performance",
        "volatility": "Volatility",
    }
    for model, label in model_labels.items():
        source = coef if model in coef["model"].values else rent
        sub = source[source["model"] == model]
        for _, row in sub.iterrows():
            if row["term"] not in term_labels:
                continue
            rows.append(
                {
                    "Model": label,
                    "Term": term_labels[row["term"]],
                    "Coefficient (95% CI)": fmt(row),
                    "n": int(row["n"]),
                }
            )
    df = pd.DataFrame(rows)
    return df.to_markdown(index=False)


def table1() -> str:
    rows = [
        ("Regular-season player-seasons", "722"),
        ("Players", "401"),
        ("Player-seasons with a t+1 role observation", "304"),
        ("Players in the t+1 sample", "212"),
        ("Position groups", "DL, WR, OL, DB, TE"),
        ("Role measure", "Position-specific opportunity per game: DL pass-rush, WR/TE routes, OL pass-block, DB coverage, others snaps"),
        ("Performance outcome", "Context-adjusted, empirical-Bayes residual; oriented higher = better"),
        ("Outcome reliability (Spearman-Brown)", "DL 0.95; WR 0.68; OL 0.55; TE 0.45; DB 0.12 (measurement check)"),
        ("Volatility", "Within-season SD of weekly performance residuals"),
        ("Rent", "Career status/start rate/accolades residual after performance, draft capital, and position"),
        ("Primary validation", "Leave-one-player-out; 2025 temporal check"),
    ]
    df = pd.DataFrame(rows, columns=["Item", "Definition"])
    return df.to_markdown(index=False)


def main() -> None:
    t1 = table1()
    t2 = table2()
    (OUT / "table1_data.md").write_text(t1)
    (OUT / "table2_models.md").write_text(t2)
    print(t1)
    print("\n")
    print(t2)


if __name__ == "__main__":
    main()
