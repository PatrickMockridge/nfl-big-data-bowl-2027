"""Transparent dollar-value model for the implications extension.

All dollar figures are inferences, not measurements. The model takes the
measured coefficients from the frozen competition outputs as calibration
anchors and applies explicit low/base/high assumptions to one team.

Two accounting choices matter:
- The selection route is annualised. A pick's four-year surplus is
  hit_lift * (market - rookie) * years; spread over the control window and
  multiplied by picks per year, the years cancel. The annual flow is
  hit_lift * (market - rookie) * picks_per_year.
- The role and contract routes are annual flows. The implementation cost is
  subtracted before the adoption probability is applied.

Outputs (gitignored):
- implications/outputs/value_bridge.csv
- implications/outputs/sensitivity.csv
- implications/outputs/monte_carlo.csv
"""

from __future__ import annotations

from dataclasses import dataclass, fields, replace
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "implications" / "outputs"


@dataclass(frozen=True)
class Assumptions:
    """All dollar inputs are in $M per year unless noted."""

    cap: float = 280.0
    market: float = 12.0
    rookie: float = 1.5
    hit_lift: float = 0.15
    years: float = 4.0
    picks_per_year: float = 0.5
    role_saving: float = 6.0
    role_decisions: float = 0.5
    reallocation_eff: float = 0.7
    contract_portfolio: float = 50.0
    pricing_correction: float = 0.075
    implementation_cost: float = 1.0
    adoption_prob: float = 0.4


BASE = Assumptions()
LOW = Assumptions(
    cap=260.0,
    market=8.0,
    rookie=0.8,
    hit_lift=0.05,
    years=4.0,
    picks_per_year=0.25,
    role_saving=3.0,
    role_decisions=0.25,
    reallocation_eff=0.5,
    contract_portfolio=30.0,
    pricing_correction=0.03,
    implementation_cost=0.5,
    adoption_prob=0.2,
)
HIGH = Assumptions(
    cap=300.0,
    market=18.0,
    rookie=2.5,
    hit_lift=0.20,
    years=4.0,
    picks_per_year=0.75,
    role_saving=8.0,
    role_decisions=0.75,
    reallocation_eff=0.8,
    contract_portfolio=60.0,
    pricing_correction=0.10,
    implementation_cost=2.0,
    adoption_prob=0.6,
)

# Inputs that move the annual net total. Cap is context; years sets the
# per-pick control window and cancels in the annual selection flow.
TOTAL_INPUTS = [
    "market",
    "rookie",
    "hit_lift",
    "picks_per_year",
    "role_saving",
    "role_decisions",
    "reallocation_eff",
    "contract_portfolio",
    "pricing_correction",
    "implementation_cost",
]

LABELS = {
    "market": "Interior DL market value",
    "rookie": "Rookie cost",
    "hit_lift": "Hit-rate lift from the signal",
    "picks_per_year": "Such picks per year",
    "role_saving": "Role-reallocation saving per decision",
    "role_decisions": "Role decisions per cycle",
    "reallocation_eff": "Reallocation efficiency",
    "contract_portfolio": "Contract portfolio",
    "pricing_correction": "Pricing correction",
    "implementation_cost": "Implementation cost",
    "adoption_prob": "Adoption probability",
}


def route_selection(a: Assumptions) -> float:
    """Annual surplus from using the burst signal in the draft.

    The four-year per-pick surplus is hit_lift * (market - rookie) * years.
    At picks_per_year, the steady-state annual flow is that total divided by
    the control window, so years cancels.
    """
    return a.hit_lift * (a.market - a.rookie) * a.picks_per_year


def surplus_per_hit_4y(a: Assumptions) -> float:
    """Undiscounted four-year surplus for one hit, before the hit rate."""
    return (a.market - a.rookie) * a.years


def route_role(a: Assumptions) -> float:
    """Annual cap value from reallocating snaps to higher-performance players."""
    return a.role_saving * a.role_decisions * a.reallocation_eff


def route_contract(a: Assumptions) -> float:
    """Annual value from pricing role-controlled performance, not raw role."""
    return a.contract_portfolio * a.pricing_correction


def evaluate(a: Assumptions) -> dict[str, float]:
    selection = route_selection(a)
    role = route_role(a)
    contract = route_contract(a)
    gross = selection + role + contract
    net = gross - a.implementation_cost
    return {
        "selection_m": selection,
        "role_m": role,
        "contract_m": contract,
        "gross_m": gross,
        "implementation_cost_m": a.implementation_cost,
        "net_m": net,
        "ev_m": net * a.adoption_prob,
        "share_of_cap": net / a.cap,
        "surplus_per_hit_4y_m": surplus_per_hit_4y(a),
    }


def deterministic_table() -> pd.DataFrame:
    rows = []
    for name, assumptions in [("Low", LOW), ("Base", BASE), ("High", HIGH)]:
        rows.append({"scenario": name, **evaluate(assumptions)})
    columns = [
        "scenario",
        "selection_m",
        "role_m",
        "contract_m",
        "gross_m",
        "implementation_cost_m",
        "net_m",
        "ev_m",
        "share_of_cap",
        "surplus_per_hit_4y_m",
    ]
    return pd.DataFrame(rows)[columns]


def sensitivity() -> pd.DataFrame:
    base = evaluate(BASE)["net_m"]
    rows = []
    for field in TOTAL_INPUTS:
        low_value = getattr(LOW, field)
        high_value = getattr(HIGH, field)
        low_net = evaluate(replace(BASE, **{field: low_value}))["net_m"]
        high_net = evaluate(replace(BASE, **{field: high_value}))["net_m"]
        rows.append(
            {
                "input": field,
                "label": LABELS[field],
                "low_value": low_value,
                "high_value": high_value,
                "low_net_m": low_net,
                "high_net_m": high_net,
                "low_delta_m": low_net - base,
                "high_delta_m": high_net - base,
                "swing_m": high_net - low_net,
                "abs_swing_m": abs(high_net - low_net),
                "basis": "net",
            }
        )
    # Adoption scales the expected value, not the annual net total.
    rows.append(
        {
            "input": "adoption_prob",
            "label": LABELS["adoption_prob"],
            "low_value": LOW.adoption_prob,
            "high_value": HIGH.adoption_prob,
            "low_net_m": base * LOW.adoption_prob,
            "high_net_m": base * HIGH.adoption_prob,
            "low_delta_m": base * (LOW.adoption_prob - BASE.adoption_prob),
            "high_delta_m": base * (HIGH.adoption_prob - BASE.adoption_prob),
            "swing_m": base * (HIGH.adoption_prob - LOW.adoption_prob),
            "abs_swing_m": base * (HIGH.adoption_prob - LOW.adoption_prob),
            "basis": "EV",
        }
    )
    return (
        pd.DataFrame(rows)
        .sort_values("abs_swing_m", ascending=False)
        .reset_index(drop=True)
    )


def monte_carlo(n: int = 20_000, seed: int = 20261019) -> pd.DataFrame:
    """Independent triangular draws over the low/base/high inputs.

    Independence is a limitation: role savings and pricing corrections are
    plausibly correlated through the same organisational adoption decision.
    The deterministic low/high is therefore the wider stress range.
    """
    rng = np.random.default_rng(seed)
    draws = {}
    for field in fields(Assumptions):
        if field.name in {"cap", "years"}:
            continue
        draws[field.name] = rng.triangular(
            getattr(LOW, field.name),
            getattr(BASE, field.name),
            getattr(HIGH, field.name),
            n,
        )
    frame = pd.DataFrame(draws)
    selection = (
        frame["hit_lift"]
        * (frame["market"] - frame["rookie"])
        * frame["picks_per_year"]
    )
    role = (
        frame["role_saving"]
        * frame["role_decisions"]
        * frame["reallocation_eff"]
    )
    contract = frame["contract_portfolio"] * frame["pricing_correction"]
    gross = selection + role + contract
    net = gross - frame["implementation_cost"]
    ev = net * frame["adoption_prob"]

    rows = []
    for name, series in [
        ("selection", selection),
        ("role", role),
        ("contract", contract),
        ("gross", gross),
        ("net", net),
        ("expected_value", ev),
    ]:
        rows.append(
            {
                "metric": name,
                "p10_m": float(np.percentile(series, 10)),
                "p50_m": float(np.percentile(series, 50)),
                "p90_m": float(np.percentile(series, 90)),
                "mean_m": float(np.mean(series)),
                "prob_above_zero": float((series > 0).mean()),
            }
        )
    return pd.DataFrame(rows)


def build_all() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    OUT.mkdir(parents=True, exist_ok=True)
    bridge = deterministic_table()
    sens = sensitivity()
    mc = monte_carlo()
    bridge.to_csv(OUT / "value_bridge.csv", index=False)
    sens.to_csv(OUT / "sensitivity.csv", index=False)
    mc.to_csv(OUT / "monte_carlo.csv", index=False)
    return bridge, sens, mc


def main() -> None:
    bridge, sens, mc = build_all()
    indexed = bridge.set_index("scenario")
    base = indexed.loc["Base"]
    low = indexed.loc["Low"]
    high = indexed.loc["High"]
    print(
        "Base: selection ${:.2f}M + role ${:.2f}M + contract ${:.2f}M "
        "= gross ${:.2f}M; net ${:.2f}M ({:.1%} of cap); EV ${:.2f}M/yr".format(
            base.selection_m,
            base.role_m,
            base.contract_m,
            base.gross_m,
            base.net_m,
            base.share_of_cap,
            base.ev_m,
        )
    )
    print(
        "Low: net ${:.2f}M/yr; High: net ${:.2f}M/yr".format(
            low.net_m, high.net_m
        )
    )
    net = mc.set_index("metric").loc["net"]
    ev = mc.set_index("metric").loc["expected_value"]
    print(
        "Monte Carlo net: P10 ${:.2f}M, P50 ${:.2f}M, P90 ${:.2f}M".format(
            net.p10_m, net.p50_m, net.p90_m
        )
    )
    print(
        "Monte Carlo EV: P10 ${:.2f}M, P50 ${:.2f}M, P90 ${:.2f}M".format(
            ev.p10_m, ev.p50_m, ev.p90_m
        )
    )
    print("\nLargest sensitivities (swing, $M/yr):")
    print(
        sens[["label", "low_net_m", "high_net_m", "swing_m"]]
        .head(6)
        .round(2)
        .to_string(index=False)
    )
    print("\nWrote:", OUT)


if __name__ == "__main__":
    main()
