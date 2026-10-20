"""Historical contract trends, 1983-2022.

No performance link: this is positional-value and contract-structure context,
not a test of the role premium.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
IN = ROOT / "implications" / "free_agency" / "outputs" / "historical_contracts_clean.csv"
OUT = ROOT / "implications" / "free_agency" / "outputs"


def positional_value(d: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (pos, year), cell in d.groupby(["pos_group", "year_signed"]):
        top5 = cell["apy_m"].nlargest(5).sum()
        total = cell["apy_m"].sum()
        rows.append(
            {
                "pos_group": pos,
                "season": int(year),
                "contracts": len(cell),
                "median_apy_m": cell["apy_m"].median(),
                "p90_apy_m": cell["apy_m"].quantile(0.90),
                "median_apy_cap_pct": cell["apy_cap_pct"].median(),
                "p90_apy_cap_pct": cell["apy_cap_pct"].quantile(0.90),
                "median_guarantee_share": cell["guarantee_share"].median(),
                "median_years": cell["years"].median(),
                "median_age": cell["age_at_signing"].median(),
                "age_coverage": cell["age_at_signing"].notna().mean(),
                "top5_apy_share": top5 / total if total > 0 else None,
            }
        )
    return pd.DataFrame(rows)


def coverage(d: pd.DataFrame) -> pd.DataFrame:
    return (
        d.groupby("year_signed")
        .agg(
            contracts=("player", "size"),
            players=("player", "nunique"),
            age_coverage=("age_at_signing", lambda s: s.notna().mean()),
            guarantee_coverage=("guaranteed_m", lambda s: s.gt(0).mean()),
            median_apy_m=("apy_m", "median"),
        )
        .reset_index()
        .rename(columns={"year_signed": "season"})
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    d = pd.read_csv(IN)
    d = d[d["year_signed"].notna()].copy()
    table = positional_value(d)
    table.to_csv(OUT / "historical_positional_value.csv", index=False)
    coverage(d).to_csv(OUT / "historical_coverage.csv", index=False)

    print("rows:", len(d), "years:", int(d["year_signed"].min()), "-", int(d["year_signed"].max()))
    print("age coverage:", round(float(d["age_at_signing"].notna().mean()), 3))
    print("\nlatest five seasons by position (median APY cap share):")
    latest = table[table["season"].ge(2018)].sort_values(["season", "pos_group"])
    print(latest.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
