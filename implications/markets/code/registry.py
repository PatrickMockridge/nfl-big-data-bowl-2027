"""Market definitions and route gating for the portfolio.

Position markets carry selection + role; contract routes are displayed on the
position market but counted in the free-agency market. The DL anchor uses the
existing implications assumptions unchanged.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "implications" / "code"))

from value_model import BASE as DL_BASE, HIGH as DL_HIGH, LOW as DL_LOW, Assumptions

INPUTS = ROOT / "implications" / "markets" / "outputs" / "market_inputs.csv"
CAP_GROUPS = ["QB", "RB", "WR", "TE", "EDGE", "IDL", "LB", "S", "CB"]


@dataclass(frozen=True)
class Market:
    key: str
    label: str
    positions: tuple[str, ...]
    routes: dict[str, str]
    overlap_group: str
    audience: tuple[str, ...]
    adoption_chunk: str
    losers: tuple[str, ...]
    evidence: dict[str, str]
    assumptions: dict[str, Assumptions]
    contract_components: tuple[tuple[str, tuple[float, float, float], tuple[float, float, float]], ...] = ()
    valuation_override: dict | None = None
    notes: str = ""


def _load_inputs() -> pd.DataFrame:
    if not INPUTS.exists():
        raise FileNotFoundError(f"run scripts/27_market_calibration.py first: {INPUTS}")
    return pd.read_csv(INPUTS).set_index("pos_group")


def free_agency_override() -> dict | None:
    """Read the dedicated report's valuation summary, if it exists."""
    path = ROOT / "implications" / "free_agency" / "outputs" / "valuation_summary.csv"
    if not path.exists():
        return None
    d = pd.read_csv(path)
    return {row["scenario"]: row.to_dict() for _, row in d.iterrows()}


def _row(inputs: pd.DataFrame, pos: str) -> dict:
    return inputs.loc[pos].to_dict()


def _components(
    inputs: pd.DataFrame, positions: list[str]
) -> tuple[tuple[str, tuple[float, float, float], tuple[float, float, float]], ...]:
    out = []
    for pos in positions:
        r = _row(inputs, pos)
        out.append(
            (
                pos,
                (r["portfolio_low"], r["portfolio_base"], r["portfolio_high"]),
                (
                    r["pricing_correction_low"],
                    r["pricing_correction_base"],
                    r["pricing_correction_high"],
                ),
            )
        )
    return tuple(out)


def _zero_assumptions() -> dict[str, Assumptions]:
    """All route inputs zero; used by contract-only and descriptive markets."""
    return {
        "low": Assumptions(
            market=0.0, rookie=0.0, hit_lift=0.0, picks_per_year=0.0,
            role_saving=0.0, role_decisions=0.0, reallocation_eff=0.0,
            contract_portfolio=0.0, pricing_correction=0.0,
            implementation_cost=0.5, adoption_prob=0.2,
        ),
        "base": Assumptions(
            market=0.0, rookie=0.0, hit_lift=0.0, picks_per_year=0.0,
            role_saving=0.0, role_decisions=0.0, reallocation_eff=0.0,
            contract_portfolio=0.0, pricing_correction=0.0,
            implementation_cost=1.0, adoption_prob=0.4,
        ),
        "high": Assumptions(
            market=0.0, rookie=0.0, hit_lift=0.0, picks_per_year=0.0,
            role_saving=0.0, role_decisions=0.0, reallocation_eff=0.0,
            contract_portfolio=0.0, pricing_correction=0.0,
            implementation_cost=2.0, adoption_prob=0.6,
        ),
    }


def _assumptions(
    r: dict,
    hit_lift: tuple[float, float, float] = (0.0, 0.0, 0.0),
    picks: tuple[float, float, float] = (0.0, 0.0, 0.0),
    role: bool = False,
    role_sensitivity: bool = False,
    implementation_cost: tuple[float, float, float] = (0.5, 1.0, 2.0),
) -> dict[str, Assumptions]:
    role_decisions = (
        (0.25, 0.50, 0.75)
        if role
        else (0.0, 0.0, 0.50)
        if role_sensitivity
        else (0.0, 0.0, 0.0)
    )
    out = {}
    for i, scenario in enumerate(["low", "base", "high"]):
        out[scenario] = Assumptions(
            cap=280.0,
            market=float(r[f"market_{scenario}"]),
            rookie=(0.8, 1.5, 2.5)[i],
            hit_lift=hit_lift[i],
            years=4.0,
            picks_per_year=picks[i],
            role_saving=float(r[f"role_saving_{scenario}"]),
            role_decisions=role_decisions[i],
            reallocation_eff=(0.5, 0.7, 0.8)[i],
            contract_portfolio=0.0,
            pricing_correction=0.0,
            implementation_cost=implementation_cost[i],
            adoption_prob=(0.2, 0.4, 0.6)[i],
        )
    return out


def build_markets() -> list[Market]:
    inputs = _load_inputs()
    markets: list[Market] = []

    # Anchor: the existing interior-DL package, all three routes.
    markets.append(
        Market(
            key="dl_anchor",
            label="Interior DL (anchor)",
            positions=("IDL",),
            routes={"selection": "modeled", "role": "modeled", "contract": "modeled"},
            overlap_group="anchor",
            audience=("GM", "analytics", "coach", "cap"),
            adoption_chunk="Existing implications chunk: draft screen, sub-package snaps, contract review.",
            losers=("low-burst veteran", "incumbent scout"),
            evidence={
                "selection": "measured association",
                "role": "descriptive",
                "contract": "measured association",
            },
            assumptions={"low": DL_LOW, "base": DL_BASE, "high": DL_HIGH},
            notes="Existing package; reconciliation anchor. Not added on top of the portfolio.",
        )
    )

    # EDGE: borderline signal, role subgroup, contract in the free-agency view.
    r = _row(inputs, "EDGE")
    markets.append(
        Market(
            key="edge",
            label="EDGE",
            positions=("EDGE",),
            routes={"selection": "modeled", "role": "modeled", "contract": "display_only"},
            overlap_group="position",
            audience=("GM", "coach", "analytics"),
            adoption_chunk="Pass-rush drill screen; 10–15% pass-rush snap reallocation; renewal review.",
            losers=("low-burst veteran", "stopwatch-first scout"),
            evidence={
                "selection": "measured association, borderline",
                "role": "descriptive",
                "contract": "measured association (free-agency view)",
            },
            assumptions=_assumptions(
                r, hit_lift=(0.02, 0.08, 0.12), picks=(0.25, 0.50, 0.75), role=True
            ),
            contract_components=_components(inputs, ["EDGE"]),
            notes="Holm-marginal transfer signal; no incremental R² over the stopwatch.",
        )
    )

    # WR: weak signal, strong allocation, small pricing correction.
    r = _row(inputs, "WR")
    markets.append(
        Market(
            key="wr",
            label="WR",
            positions=("WR",),
            routes={"selection": "sensitivity", "role": "modeled", "contract": "display_only"},
            overlap_group="position",
            audience=("GM", "coach", "analytics"),
            adoption_chunk="Route-drill screen as a sensitivity only; 10–15% route-participation reallocation; renewal review.",
            losers=("low-route veteran", "scout who trusts the stopwatch"),
            evidence={
                "selection": "weak; sensitivity only",
                "role": "descriptive",
                "contract": "measured association, small gap (free-agency view)",
            },
            assumptions=_assumptions(
                r, hit_lift=(0.0, 0.0, 0.05), picks=(0.25, 0.50, 0.75), role=True
            ),
            contract_components=_components(inputs, ["WR"]),
            notes="Selection route is zero in the base case; high case is a sensitivity.",
        )
    )

    # DB: pricing only (CB + S).
    markets.append(
        Market(
            key="db",
            label="DB (CB/S)",
            positions=("CB", "S"),
            routes={"selection": "not_modeled", "role": "not_modeled", "contract": "display_only"},
            overlap_group="position",
            audience=("GM", "cap", "analytics"),
            adoption_chunk="Contract review only; no coaching or role change.",
            losers=("incumbent contract",),
            evidence={
                "selection": "unidentifiable",
                "role": "unidentifiable (zero-variance performance residual)",
                "contract": "measured association (free-agency view)",
            },
            assumptions=_zero_assumptions(),
            contract_components=_components(inputs, ["CB", "S"]),
            notes="The cleanest transfer is the 40-yard-priced / task-signal-unpriced contrast; no dollar role route.",
        )
    )

    # OL: allocation only, no cap-ledger performance.
    r = _row(inputs, "OL")
    markets.append(
        Market(
            key="ol",
            label="OL",
            positions=("OL",),
            routes={"selection": "not_modeled", "role": "modeled", "contract": "not_modeled"},
            overlap_group="position",
            audience=("GM", "coach", "analytics"),
            adoption_chunk="Role review using the pressure-allowed residual; no contract route.",
            losers=("coach's discretionary depth chart",),
            evidence={
                "selection": "unidentifiable (signal reliability 0.448)",
                "role": "descriptive",
                "contract": "not modeled (no individual performance in the cap ledger)",
            },
            assumptions=_assumptions(r, role=True),
            notes="Allocation-only market; the contract leg is unavailable.",
        )
    )

    # TE: thin; role sensitivity and no pricing correction.
    r = _row(inputs, "TE")
    markets.append(
        Market(
            key="te",
            label="TE",
            positions=("TE",),
            routes={"selection": "not_modeled", "role": "sensitivity", "contract": "display_only"},
            overlap_group="position",
            audience=("GM", "coach", "analytics"),
            adoption_chunk="Role review only; no base-case dollar claim.",
            losers=("incumbent depth chart",),
            evidence={
                "selection": "unidentifiable",
                "role": "descriptive, thin",
                "contract": "no correction; thin cell",
            },
            assumptions=_assumptions(
                r, role_sensitivity=True, implementation_cost=(0.0, 0.0, 0.0)
            ),
            contract_components=_components(inputs, ["TE"]),
            notes="Outcome reliability 0.449; 27 role rows; correction is zero.",
        )
    )

    # Free agency / contract: contract across cap-covered positions.
    markets.append(
        Market(
            key="free_agency",
            label="Free agency / contract",
            positions=tuple(CAP_GROUPS),
            routes={"selection": "not_modeled", "role": "not_modeled", "contract": "modeled"},
            overlap_group="contract",
            audience=("GM", "cap", "analytics", "league office"),
            adoption_chunk="Reprice the next renewal wave on role-controlled performance; lowest political cost.",
            losers=("incumbent agent/player",),
            evidence={
                "selection": "not modeled",
                "role": "not modeled",
                "contract": "measured association + inference",
            },
            assumptions=_zero_assumptions(),
            contract_components=_components(inputs, CAP_GROUPS),
            valuation_override=free_agency_override(),
            notes=(
                "Dedicated report bottom-up estimate when available; "
                "legacy top-down components remain a cross-check."
            ),
        )
    )

    return markets


def market_frame() -> pd.DataFrame:
    rows = []
    for m in build_markets():
        rows.append(
            {
                "key": m.key,
                "label": m.label,
                "positions": ",".join(m.positions),
                "overlap_group": m.overlap_group,
                "selection": m.routes["selection"],
                "role": m.routes["role"],
                "contract": m.routes["contract"],
                "evidence_selection": m.evidence["selection"],
                "evidence_role": m.evidence["role"],
                "evidence_contract": m.evidence["contract"],
                "notes": m.notes,
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    OUT = ROOT / "implications" / "markets" / "outputs"
    OUT.mkdir(parents=True, exist_ok=True)
    frame = market_frame()
    frame.to_csv(OUT / "market_registry.csv", index=False)
    print(frame.to_string(index=False))


if __name__ == "__main__":
    main()
