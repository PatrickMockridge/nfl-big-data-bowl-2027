"""Route-gated market valuations, sensitivity, Monte Carlo, and portfolio.

The route formulas are imported from ``implications/code/value_model.py``.
Parameterized wrappers are needed because the original helpers read the module's
global LOW/BASE/HIGH values.
"""

from __future__ import annotations

import sys
from dataclasses import fields, replace
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "implications" / "code"))
sys.path.insert(0, str(ROOT / "implications" / "markets" / "code"))

from value_model import (  # noqa: E402
    Assumptions,
    TOTAL_INPUTS,
    evaluate,
    route_role,
    route_selection,
)
from registry import Market, build_markets  # noqa: E402

OUT = ROOT / "implications" / "markets" / "outputs"
SEED = 20261020
DRAWS = 20000
SCENARIOS = ["low", "base", "high"]

INPUT_LABELS = {
    "market": "Market value",
    "rookie": "Rookie cost",
    "hit_lift": "Hit-rate lift",
    "picks_per_year": "Picks per year",
    "role_saving": "Role saving per decision",
    "role_decisions": "Role decisions per cycle",
    "reallocation_eff": "Reallocation efficiency",
    "contract_portfolio": "Contract portfolio",
    "pricing_correction": "Pricing correction",
    "implementation_cost": "Implementation cost",
    "adoption_prob": "Adoption probability",
}


def _uncertain_map() -> dict[str, bool]:
    path = OUT / "market_inputs.csv"
    if not path.exists():
        return {}
    d = pd.read_csv(path)
    return dict(zip(d["pos_group"], d["gap_uncertain"].fillna(True).astype(bool)))


def _component_contract(market: Market, index: int, conservative: bool = False) -> float:
    uncertain = _uncertain_map()
    total = 0.0
    for pos, portfolio, correction in market.contract_components:
        corr = correction[index]
        if conservative and uncertain.get(pos, True):
            corr = 0.0
        total += portfolio[index] * corr
    return float(total)


def _portfolio_net(market: Market, scenario: str, base: dict, contract: float) -> tuple[float, float, float]:
    a = market.assumptions[scenario]
    if market.key == "dl_anchor":
        sel_role = base["selection_m"] + base["role_m"]
        total = base["gross_m"]
        cost = a.implementation_cost * (sel_role / total) if total > 0 else 0.0
        value = sel_role - cost
        return value, value * a.adoption_prob, base["net_m"]
    if market.key == "db":
        return 0.0, 0.0, 0.0
    if market.key == "free_agency":
        value = base["gross_m"] - a.implementation_cost
        return value, value * a.adoption_prob, base["net_m"]
    if market.contract_components:
        # Position market: selection + role only; contract is in free agency.
        value = base["selection_m"] + base["role_m"] - a.implementation_cost
        return value, value * a.adoption_prob, base["net_m"]
    return base["net_m"], base["ev_m"], base["net_m"]


def evaluate_market(market: Market, scenario: str) -> dict:
    if market.valuation_override and scenario in market.valuation_override:
        o = market.valuation_override[scenario]
        gross = float(o["gross_m"])
        cost = float(o["implementation_cost_m"])
        net = float(o["net_m"])
        ev = float(o["ev_m"])
        cons = market.valuation_override.get("conservative", {})
        return {
            "selection_m": 0.0,
            "role_m": 0.0,
            "contract_m": gross,
            "gross_m": gross,
            "implementation_cost_m": cost,
            "net_m": net,
            "ev_m": ev,
            "share_of_cap": net / 280.0,
            "portfolio_net_m": net,
            "portfolio_ev_m": ev,
            "anchor_net_m": np.nan,
            "contract_conservative_m": float(cons.get("gross_m", gross)),
        }
    a = market.assumptions[scenario]
    base = evaluate(a)
    index = SCENARIOS.index(scenario)
    contract = _component_contract(market, index)
    contract_conservative = _component_contract(market, index, conservative=True)
    if market.contract_components:
        gross = base["selection_m"] + base["role_m"] + contract
        base = {
            **base,
            "contract_m": contract,
            "gross_m": gross,
            "net_m": gross - a.implementation_cost,
            "ev_m": (gross - a.implementation_cost) * a.adoption_prob,
            "share_of_cap": (gross - a.implementation_cost) / a.cap,
        }
    pnet, pev, anchor_net = _portfolio_net(market, scenario, base, contract)
    return {
        **base,
        "portfolio_net_m": pnet,
        "portfolio_ev_m": pev,
        "anchor_net_m": anchor_net if market.key == "dl_anchor" else np.nan,
        "contract_conservative_m": contract_conservative,
    }


def valuations(markets: list[Market]) -> pd.DataFrame:
    rows = []
    for m in markets:
        for scenario in SCENARIOS:
            r = evaluate_market(m, scenario)
            rows.append(
                {
                    "market": m.key,
                    "label": m.label,
                    "scenario": scenario,
                    "positions": ",".join(m.positions),
                    "overlap_group": m.overlap_group,
                    "selection_status": m.routes["selection"],
                    "role_status": m.routes["role"],
                    "contract_status": m.routes["contract"],
                    "selection_m": r["selection_m"],
                    "role_m": r["role_m"],
                    "contract_m": r["contract_m"],
                    "contract_conservative_m": r["contract_conservative_m"],
                    "gross_m": r["gross_m"],
                    "implementation_cost_m": r["implementation_cost_m"],
                    "net_m": r["net_m"],
                    "ev_m": r["ev_m"],
                    "share_of_cap": r["share_of_cap"],
                    "portfolio_net_m": r["portfolio_net_m"],
                    "portfolio_ev_m": r["portfolio_ev_m"],
                    "anchor_net_m": r["anchor_net_m"],
                    "in_free_agency_total": bool(
                        m.contract_components and m.key != "free_agency"
                    ),
                    "notes": m.notes,
                }
            )
    return pd.DataFrame(rows)


def sensitivity(markets: list[Market]) -> pd.DataFrame:
    rows = []
    for m in markets:
        if m.valuation_override:
            o = m.valuation_override
            lo = float(o["low"]["net_m"])
            hi = float(o["high"]["net_m"])
            rows.append(
                {
                    "market": m.key,
                    "input": "free_agency_report",
                    "label": "Dedicated report (bottom-up)",
                    "low_net_m": lo,
                    "high_net_m": hi,
                    "swing_m": hi - lo,
                    "basis": "net",
                }
            )
            rows.append(
                {
                    "market": m.key,
                    "input": "adoption_prob",
                    "label": INPUT_LABELS["adoption_prob"],
                    "low_net_m": float(o["low"]["ev_m"]),
                    "high_net_m": float(o["high"]["ev_m"]),
                    "swing_m": float(o["high"]["ev_m"]) - float(o["low"]["ev_m"]),
                    "basis": "EV",
                }
            )
            continue
        low, base, high = (m.assumptions[s] for s in SCENARIOS)
        base_net = evaluate_market(m, "base")["portfolio_net_m"]
        for field in TOTAL_INPUTS:
            if field in {"contract_portfolio", "pricing_correction"} and m.contract_components:
                continue
            lo_m = replace(
                m,
                assumptions={
                    **m.assumptions,
                    "base": replace(base, **{field: getattr(low, field)}),
                },
            )
            hi_m = replace(
                m,
                assumptions={
                    **m.assumptions,
                    "base": replace(base, **{field: getattr(high, field)}),
                },
            )
            lo_net = evaluate_market(lo_m, "base")["portfolio_net_m"]
            hi_net = evaluate_market(hi_m, "base")["portfolio_net_m"]
            rows.append(
                {
                    "market": m.key,
                    "input": field,
                    "label": INPUT_LABELS.get(field, field),
                    "low_net_m": lo_net,
                    "high_net_m": hi_net,
                    "swing_m": hi_net - lo_net,
                    "basis": "net",
                }
            )
        if m.contract_components:
            lo = evaluate_market(m, "low")
            hi = evaluate_market(m, "high")
            if m.key == "free_agency":
                low_value = lo["portfolio_net_m"]
                high_value = hi["portfolio_net_m"]
                label = "Contract components (portfolio x correction)"
            else:
                low_value = lo["contract_m"]
                high_value = hi["contract_m"]
                label = "Contract display (counted in free agency)"
            rows.append(
                {
                    "market": m.key,
                    "input": "contract_components",
                    "label": label,
                    "low_net_m": low_value,
                    "high_net_m": high_value,
                    "swing_m": high_value - low_value,
                    "basis": "net",
                }
            )
        # Adoption scales expected value, not the net flow.
        lo_ev = evaluate_market(
            replace(
                m,
                assumptions={
                    **m.assumptions,
                    "base": replace(base, adoption_prob=low.adoption_prob),
                },
            ),
            "base",
        )["portfolio_ev_m"]
        hi_ev = evaluate_market(
            replace(
                m,
                assumptions={
                    **m.assumptions,
                    "base": replace(base, adoption_prob=high.adoption_prob),
                },
            ),
            "base",
        )["portfolio_ev_m"]
        rows.append(
            {
                "market": m.key,
                "input": "adoption_prob",
                "label": INPUT_LABELS["adoption_prob"],
                "low_net_m": lo_ev,
                "high_net_m": hi_ev,
                "swing_m": hi_ev - lo_ev,
                "basis": "EV",
            }
        )
    out = pd.DataFrame(rows)
    out["abs_swing_m"] = out["swing_m"].abs()
    return out.sort_values(["market", "abs_swing_m"], ascending=[True, False])


def monte_carlo(markets: list[Market], n: int = DRAWS, seed: int = SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for m in markets:
        if m.valuation_override:
            # The dedicated free-agency report owns its Monte Carlo.
            continue
        low, base, high = (m.assumptions[s] for s in SCENARIOS)
        draws = {}
        def draw(triple: tuple[float, float, float]) -> np.ndarray:
            lo, mode, hi = triple
            if not (np.isfinite(lo) and np.isfinite(mode) and np.isfinite(hi)) or hi <= lo:
                return np.full(n, mode)
            return rng.triangular(lo, mode, hi, n)

        for f in fields(Assumptions):
            if f.name in {"cap", "years"}:
                continue
            draws[f.name] = draw(
                (getattr(low, f.name), getattr(base, f.name), getattr(high, f.name))
            )
        if m.contract_components:
            contract = np.zeros(n)
            for _, portfolio, correction in m.contract_components:
                p = draw(portfolio)
                c = draw(correction)
                contract += p * c
        else:
            contract = draws["contract_portfolio"] * draws["pricing_correction"]
        selection = draws["hit_lift"] * (draws["market"] - draws["rookie"]) * draws["picks_per_year"]
        role = draws["role_saving"] * draws["role_decisions"] * draws["reallocation_eff"]
        gross = selection + role + contract
        net = gross - draws["implementation_cost"]
        ev = net * draws["adoption_prob"]
        # Portfolio net excludes display-only contract for position markets.
        if m.key in {"edge", "wr", "te", "ol"}:
            net = selection + role - draws["implementation_cost"]
            ev = net * draws["adoption_prob"]
        elif m.key == "db":
            net = np.zeros(n)
            ev = np.zeros(n)
        elif m.key == "dl_anchor":
            sel_role = selection + role
            share = np.divide(sel_role, gross, out=np.zeros_like(gross), where=gross > 0)
            net = sel_role - draws["implementation_cost"] * share
            ev = net * draws["adoption_prob"]
        for metric, values in [("net_m", net), ("ev_m", ev)]:
            rows.append(
                {
                    "market": m.key,
                    "metric": metric,
                    "n": n,
                    "seed": seed,
                    "p10_m": float(np.percentile(values, 10)),
                    "p50_m": float(np.percentile(values, 50)),
                    "p90_m": float(np.percentile(values, 90)),
                    "mean_m": float(np.mean(values)),
                    "prob_above_zero": float(np.mean(values > 0)),
                }
            )
    return pd.DataFrame(rows)


def contract_components(markets: list[Market]) -> pd.DataFrame:
    uncertain = _uncertain_map()
    rows = []
    for m in markets:
        for pos, portfolio, correction in m.contract_components:
            gross = [portfolio[i] * correction[i] for i in range(3)]
            is_uncertain = bool(uncertain.get(pos, True))
            rows.append(
                {
                    "market": m.key,
                    "pos_group": pos,
                    "portfolio_low": portfolio[0],
                    "portfolio_base": portfolio[1],
                    "portfolio_high": portfolio[2],
                    "correction_low": correction[0],
                    "correction_base": correction[1],
                    "correction_high": correction[2],
                    "contract_low_m": gross[0],
                    "contract_base_m": gross[1],
                    "contract_high_m": gross[2],
                    "gap_uncertain": is_uncertain,
                    "contract_conservative_base_m": 0.0 if is_uncertain else gross[1],
                    "in_free_agency_total": m.key != "free_agency",
                    "legacy_top_down": m.key == "free_agency",
                }
            )
    return pd.DataFrame(rows)


def portfolio(markets: list[Market]) -> pd.DataFrame:
    vals = valuations(markets)
    rows = []
    for m in markets:
        sub = vals[vals["market"] == m.key].set_index("scenario")
        if m.key == "free_agency":
            conservative = (
                sub.loc["base", "contract_conservative_m"]
                - sub.loc["base", "implementation_cost_m"]
            )
        else:
            conservative = sub.loc["base", "portfolio_net_m"]
        rows.append(
            {
                "market": m.key,
                "label": m.label,
                "in_portfolio": True,
                "base_portfolio_net_m": sub.loc["base", "portfolio_net_m"],
                "low_portfolio_net_m": sub.loc["low", "portfolio_net_m"],
                "conservative_portfolio_net_m": conservative,
                "base_portfolio_ev_m": sub.loc["base", "portfolio_ev_m"],
                "low_portfolio_ev_m": sub.loc["low", "portfolio_ev_m"],
                "notes": m.notes,
            }
        )
    out = pd.DataFrame(rows)
    total = pd.DataFrame(
        [
            {
                "market": "TOTAL",
                "label": "Portfolio total",
                "in_portfolio": True,
                "base_portfolio_net_m": out["base_portfolio_net_m"].sum(),
                "low_portfolio_net_m": out["low_portfolio_net_m"].sum(),
                "conservative_portfolio_net_m": out["conservative_portfolio_net_m"].sum(),
                "base_portfolio_ev_m": out["base_portfolio_ev_m"].sum(),
                "low_portfolio_ev_m": out["low_portfolio_ev_m"].sum(),
                "notes": "Position selection+role plus free-agency contract; no double counting.",
            }
        ]
    )
    return pd.concat([out, total], ignore_index=True)


def evidence_ledger(markets: list[Market], vals: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for m in markets:
        base = vals[(vals["market"] == m.key) & (vals["scenario"] == "base")].iloc[0]
        for route in ["selection", "role", "contract"]:
            value = {
                "selection": base["selection_m"],
                "role": base["role_m"],
                "contract": base["contract_m"],
            }[route]
            rows.append(
                {
                    "market": m.key,
                    "route": route,
                    "status": m.routes[route],
                    "evidence_tier": m.evidence[route],
                    "base_gross_m": value,
                    "source": m.notes,
                    "caveat": (
                        "not modeled" if m.routes[route] == "not_modeled"
                        else "sensitivity only" if m.routes[route] == "sensitivity"
                        else ""
                    ),
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    markets = build_markets()
    from registry import market_frame

    market_frame().to_csv(OUT / "market_registry.csv", index=False)
    vals = valuations(markets)
    vals.to_csv(OUT / "market_valuations.csv", index=False)
    sensitivity(markets).to_csv(OUT / "market_sensitivity.csv", index=False)
    monte_carlo(markets).to_csv(OUT / "market_monte_carlo.csv", index=False)
    contract_components(markets).to_csv(OUT / "contract_components.csv", index=False)
    port = portfolio(markets)
    port.to_csv(OUT / "portfolio.csv", index=False)
    evidence_ledger(markets, vals).to_csv(OUT / "evidence_ledger.csv", index=False)

    print(port.round(2).to_string(index=False))
    print("\nBase valuations:")
    print(
        vals[vals["scenario"] == "base"][
            ["market", "selection_m", "role_m", "contract_m", "net_m", "portfolio_net_m"]
        ].round(2).to_string(index=False)
    )


if __name__ == "__main__":
    main()
