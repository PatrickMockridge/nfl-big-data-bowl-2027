"""Calibrate market inputs from the 2025 cap ledger, positional spending, and
the per-position pricing models.

Every input is a transparent quantile or a fixed judgment range. The DL anchor
keeps the existing package's 8 / 12 / 18 market and 3 / 6 / 8 role saving.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
CAP = ROOT / "outputs" / "salary" / "otc_cap_2025_players.csv"
PANEL = ROOT / "outputs" / "salary" / "otc_panel.csv"
PRICING = ROOT / "implications" / "markets" / "outputs" / "position_pricing.csv"
OUT = ROOT / "implications" / "markets" / "outputs"

POSITIONS = ["QB", "RB", "WR", "TE", "EDGE", "IDL", "LB", "S", "CB", "OL"]
ANCHOR = {
    "IDL": {"market": (8.0, 12.0, 18.0), "role_saving": (3.0, 6.0, 8.0)},
}


def _quantiles(series: pd.Series, qs=(0.75, 0.90, 0.95)) -> tuple[float, ...]:
    s = series.dropna()
    if s.empty:
        return (np.nan,) * len(qs)
    return tuple(float(s.quantile(q)) / 1e6 for q in qs)


def market_values() -> pd.DataFrame:
    cap = pd.read_csv(CAP)
    rows = []
    for pos in POSITIONS:
        sub = cap[cap["pos_group"] == pos]
        q75, q90, q95 = _quantiles(sub["cap_number"])
        if pos in ANCHOR:
            m_low, m_base, m_high = ANCHOR[pos]["market"]
            anchor = True
        else:
            m_low, m_base, m_high = q75, q90, q95
            anchor = False
        rook = sub[sub["years_exp"].le(1)]["cap_number"]
        r25, r50, r75 = _quantiles(rook, qs=(0.25, 0.50, 0.75))
        rows.append(
            {
                "pos_group": pos,
                "n_cap_rows": len(sub),
                "market_p75": q75,
                "market_p90": q90,
                "market_p95": q95,
                "market_low": round(m_low, 1) if np.isfinite(m_low) else np.nan,
                "market_base": round(m_base, 1) if np.isfinite(m_base) else np.nan,
                "market_high": round(m_high, 1) if np.isfinite(m_high) else np.nan,
                "market_anchor": anchor,
                "rookie_p25": r25,
                "rookie_p50": r50,
                "rookie_p75": r75,
                "rookie_low": 0.8,
                "rookie_base": 1.5,
                "rookie_high": 2.5,
            }
        )
    return pd.DataFrame(rows)


def portfolios() -> pd.DataFrame:
    panel = pd.read_csv(PANEL)
    panel = panel[panel["season"].eq(2025)]
    means = {
        col: float(panel[col].mean()) / 1e6
        for col in ["QB", "RB", "WR", "TE", "OL", "IDL", "EDGE", "LB", "S", "CB"]
    }
    idl = means["IDL"]
    rows = []
    for pos in POSITIONS:
        spend = means.get(pos, np.nan)
        base = 50.0 * spend / idl if np.isfinite(spend) and idl else np.nan
        rows.append(
            {
                "pos_group": pos,
                "team_spend_mean_m": spend,
                "portfolio_low": round(0.6 * base, 1) if np.isfinite(base) else np.nan,
                "portfolio_base": round(base, 1) if np.isfinite(base) else np.nan,
                "portfolio_high": round(1.4 * base, 1) if np.isfinite(base) else np.nan,
            }
        )
    return pd.DataFrame(rows)


def build() -> pd.DataFrame:
    mv = market_values()
    pf = portfolios()
    pricing = pd.read_csv(PRICING)
    d = mv.merge(pf, on="pos_group", how="left").merge(
        pricing[
            [
                "pos_group",
                "pricing_correction_low",
                "pricing_correction_base",
                "pricing_correction_high",
                "status",
                "gap",
                "gap_uncertain",
                "note",
            ]
        ],
        on="pos_group",
        how="left",
    )
    d["pricing_status"] = d["status"].fillna("not_modeled")
    d["pricing_note"] = d["note"].fillna("")
    for i, label in enumerate(["low", "base", "high"]):
        anchor_col = d["pos_group"].map(
            lambda p: ANCHOR[p]["role_saving"][i] if p in ANCHOR else np.nan
        )
        derived = {
            "low": 0.25 * d["market_low"],
            "base": 0.50 * d["market_base"],
            "high": 0.75 * d["market_high"],
        }[label]
        d[f"role_saving_{label}"] = anchor_col.fillna(derived)
    d["evidence_market"] = d["market_anchor"].map(
        {True: "existing DL anchor", False: "2025 cap-ledger P75/P90/P95"}
    )
    d["evidence_pricing"] = d["pricing_status"].map(
        {
            "primary": "measured association, n>=80",
            "exploratory": "measured association, thin cell",
            "not_modeled": "not modeled",
        }
    )
    return d


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    d = build()
    d.to_csv(OUT / "market_inputs.csv", index=False)
    cols = [
        "pos_group", "market_low", "market_base", "market_high",
        "portfolio_low", "portfolio_base", "portfolio_high",
        "pricing_correction_low", "pricing_correction_base", "pricing_correction_high",
        "pricing_status",
    ]
    print(d[cols].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
