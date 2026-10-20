"""Figures for the market portfolio extension."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "implications" / "markets" / "outputs"
FIG = ROOT / "implications" / "markets" / "writeups" / "figures"

BLUE = "#2a78d6"
ORANGE = "#eb6834"
AQUA = "#1baf7a"
GRAY = "#898781"
INK = "#0b0b0b"
SECONDARY = "#52514e"
SURFACE = "#fcfcfb"
BASELINE = "#c3c2b7"
GRID = "#e1e0d9"
RED = "#e34948"

STATUS_COLORS = {
    "modeled": AQUA,
    "sensitivity": ORANGE,
    "display_only": BLUE,
    "not_modeled": "#d9d8d0",
    "unidentifiable": "#d9d8d0",
}

plt.rcParams.update(
    {
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "font.family": "DejaVu Sans",
        "font.size": 10.0,
        "axes.edgecolor": BASELINE,
        "axes.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.color": GRID,
        "grid.linewidth": 0.6,
        "axes.labelcolor": SECONDARY,
        "xtick.color": SECONDARY,
        "ytick.color": SECONDARY,
    }
)


def _read(name: str) -> pd.DataFrame:
    return pd.read_csv(OUT / name)


def _save(fig, name: str) -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    path = FIG / name
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {path.relative_to(ROOT)}")


def route_matrix() -> None:
    reg = _read("market_registry.csv")
    order = ["edge", "wr", "db", "ol", "te", "free_agency"]
    keys = set(reg["key"])
    reg = reg.set_index("key").loc[[k for k in order if k in keys]].reset_index()
    routes = ["selection", "role", "contract"]
    headers = ["Selection\n(signal-led)", "Role\n(allocation-led)", "Contract\n(pricing-led)"]
    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    ax.set_xlim(0, 3)
    ax.set_ylim(0, len(reg) + 0.6)
    ax.axis("off")
    for x, header in enumerate(headers):
        ax.text(x + 0.5, len(reg) + 0.10, header, ha="center", va="bottom",
                fontsize=9.0, color=SECONDARY)
    for y, row in enumerate(reg.itertuples()):
        yy = len(reg) - y - 1
        ax.text(-0.10, yy + 0.5, row.label, ha="right", va="center",
                fontsize=9.5, color=INK)
        for x, route in enumerate(routes):
            status = getattr(row, route)
            color = STATUS_COLORS.get(status, GRAY)
            ax.add_patch(Rectangle((x + 0.02, yy + 0.08), 0.96, 0.84,
                                   facecolor=color, edgecolor="none", alpha=0.85))
            ax.text(x + 0.5, yy + 0.5, status.replace("_", " "), ha="center",
                    va="center", fontsize=8.2,
                    color="white" if status in {"modeled", "display_only"} else INK)
    fig.suptitle(
        "Route-gated markets: model only what the evidence supports",
        x=0.01, y=1.02, ha="left", fontsize=11.5,
    )
    ax.text(
        0, -0.10,
        "Display only: the contract route is counted in the free-agency market,\n"
        "not in the position total. Coaching and special teams are descriptive.",
        transform=ax.transAxes, fontsize=8.0, color=SECONDARY, linespacing=1.5,
    )
    _save(fig, "market_route_matrix.png")


def portfolio_bridge() -> None:
    p = _read("portfolio.csv")
    p = p[p["market"].ne("TOTAL")].copy()
    p = p.sort_values("base_portfolio_net_m")
    fig, ax = plt.subplots(figsize=(7.8, 4.6))
    y = np.arange(len(p))
    ax.barh(y - 0.18, p["base_portfolio_net_m"], height=0.34,
            color=BLUE, label="Base")
    ax.barh(y + 0.18, p["conservative_portfolio_net_m"], height=0.34,
            color=AQUA, label="Conservative (uncertain gaps zeroed)")
    ax.axvline(0, color=BASELINE, linewidth=1)
    ax.set_yticks(y)
    ax.set_yticklabels(p["label"])
    ax.set_xlabel("Portfolio net ($M/year)")
    ax.set_title("Portfolio net by market", loc="left", fontsize=11.5, pad=10)
    ax.legend(frameon=False, fontsize=8.5, loc="lower right")
    total = _read("portfolio.csv").query("market == 'TOTAL'").iloc[0]
    ax.text(
        0.99, 0.98,
        f"Total base ${total['base_portfolio_net_m']:.1f}M; "
        f"conservative ${total['conservative_portfolio_net_m']:.1f}M; "
        f"low ${total['low_portfolio_net_m']:.1f}M",
        transform=ax.transAxes, ha="right", va="top", fontsize=8.2,
        color=SECONDARY,
    )
    _save(fig, "market_portfolio_bridge.png")


def pricing_forest() -> None:
    d = _read("position_pricing.csv").dropna(subset=["raw_coef", "role_coef"])
    d = d.sort_values("gap")
    y = np.arange(len(d))
    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    ax.errorbar(
        d["raw_coef"], y + 0.14,
        xerr=[d["raw_coef"] - d["raw_ci_low"], d["raw_ci_high"] - d["raw_coef"]],
        fmt="o", color=BLUE, ecolor=GRAY, elinewidth=1.2, capsize=2.5,
        markersize=4, label="Raw performance coefficient",
    )
    ax.errorbar(
        d["role_coef"], y - 0.14,
        xerr=[d["role_coef"] - d["role_ci_low"], d["role_ci_high"] - d["role_coef"]],
        fmt="o", color=ORANGE, ecolor=GRAY, elinewidth=1.2, capsize=2.5,
        markersize=4, label="Role-controlled coefficient",
    )
    ax.axvline(0, color=BASELINE, linewidth=1)
    ax.set_yticks(y)
    ax.set_yticklabels(d["pos_group"])
    ax.set_xlabel("Perf_z coefficient on log cap (95% CI)")
    ax.set_title("The role premium by position", loc="left", fontsize=11.5, pad=10)
    ax.legend(frameon=False, fontsize=8.5, loc="lower right")
    ax.text(
        0.01, -0.18,
        "Gap = raw − role; the pricing correction is a haircut of the gap. "
        "Thin cells: QB, RB, TE.",
        transform=ax.transAxes, fontsize=8.0, color=SECONDARY,
    )
    _save(fig, "market_pricing_forest.png")


def contract_components() -> None:
    d = _read("contract_components.csv")
    d = d[d["market"].eq("free_agency")].copy()
    d = d.sort_values("contract_base_m")
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    y = np.arange(len(d))
    ax.barh(y, d["contract_base_m"], color=BLUE, alpha=0.85, label="Base")
    ax.scatter(d["contract_conservative_base_m"], y, color=AQUA, s=42,
               zorder=3, label="Conservative")
    ax.set_yticks(y)
    ax.set_yticklabels(d["pos_group"])
    ax.set_xlabel("Contract value from the pricing correction ($M/year)")
    ax.set_title("Legacy top-down free-agency components", loc="left",
                 fontsize=11.5, pad=10)
    ax.legend(frameon=False, fontsize=8.5, loc="lower right")
    ax.text(
        0.01, -0.20,
        "Superseded by the dedicated free-agency bottom-up report; "
        "kept as a cross-check, not added to the portfolio.",
        transform=ax.transAxes, fontsize=8.0, color=SECONDARY,
    )
    _save(fig, "market_contract_components.png")


def free_agency_scenarios() -> None:
    path = ROOT / "implications" / "free_agency" / "outputs" / "valuation_summary.csv"
    if not path.exists():
        return
    d = pd.read_csv(path)
    order = ["low", "conservative", "base", "high"]
    d = d.set_index("scenario").reindex(order).reset_index()
    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    colors = [GRAY, ORANGE, BLUE, AQUA]
    ax.bar(d["scenario"], d["net_m"], color=colors)
    bridge_path = ROOT / "implications" / "free_agency" / "outputs" / "valuation_bridge.csv"
    bridge = pd.read_csv(bridge_path).set_index("measure")["value"]
    ax.axhline(float(bridge["old_top_down_base_net_m"]), color=RED,
               linestyle="--", linewidth=1.2, label="Old top-down base")
    ax.axhline(float(bridge["old_top_down_conservative_net_m"]), color=GRAY,
               linestyle="--", linewidth=1.0, label="Old conservative")
    ax.set_ylabel("Net ($M/year)")
    ax.set_title("Free agency: bottom-up scenarios vs the old top-down",
                 loc="left", fontsize=11.5, pad=10)
    ax.legend(frameon=False, fontsize=8.0, loc="upper right")
    _save(fig, "market_free_agency_scenarios.png")


def coaching_retention() -> None:
    d = _read("coaching_descriptive.csv")
    d = d[d["dimension"].eq("wins_quartile")].copy()
    fig, ax = plt.subplots(figsize=(6.8, 4.0))
    x = np.arange(len(d))
    ax.bar(x, d["retention_rate"], color=BLUE, alpha=0.85)
    ax.set_xticks(x)
    ax.set_xticklabels([f"Q{i+1}" for i in range(len(d))])
    ax.set_ylim(0, 1.0)
    ax.set_ylabel("Next-season retention rate")
    ax.set_xlabel("Wins quartile")
    ax.set_title("Coaching retention tracks wins", loc="left", fontsize=11.5, pad=10)
    for xi, row in d.reset_index(drop=True).iterrows():
        ax.annotate(f"{row['retention_rate']:.2f}", (xi, row["retention_rate"]),
                    textcoords="offset points", xytext=(0, 6), ha="center",
                    fontsize=8.5, color=SECONDARY)
    ax.text(
        0.01, -0.20,
        "Descriptive; no dollar value. Tenure is a first/last-game proxy.",
        transform=ax.transAxes, fontsize=8.0, color=SECONDARY,
    )
    _save(fig, "market_coaching_retention.png")


def st_reliability() -> None:
    d = _read("st_reliability.csv")
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    x = np.arange(len(d))
    ax.bar(x, d["reliability"].fillna(0), color=[AQUA if v >= 0.5 else GRAY
                                                for v in d["reliability"].fillna(0)])
    ax.axhline(0.50, color=RED, linewidth=1, linestyle="--")
    ax.set_xticks(x)
    ax.set_xticklabels(d["role"])
    ax.set_ylim(0, 1.0)
    ax.set_ylabel("Split-half reliability")
    ax.set_title("Special teams reliability gate", loc="left", fontsize=11.5, pad=10)
    ax.text(
        0.01, -0.22,
        "K and P fail the 0.50 gate; the returner composite passes but has no "
        "separate ST cap market.",
        transform=ax.transAxes, fontsize=8.0, color=SECONDARY,
    )
    _save(fig, "market_st_reliability.png")


def main() -> None:
    route_matrix()
    portfolio_bridge()
    pricing_forest()
    contract_components()
    free_agency_scenarios()
    coaching_retention()
    st_reliability()


if __name__ == "__main__":
    main()
