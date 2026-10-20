"""Figures for the free-agency investigation."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "implications" / "free_agency" / "outputs"
FIG = ROOT / "implications" / "free_agency" / "writeups" / "figures"

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


def headline() -> None:
    """One-panel README chart: the team distribution versus the old estimate."""
    d = _read("valuation_by_team.csv")
    d = d[d["positions"].eq("all")].sort_values("annual_role_premium_m").reset_index(drop=True)
    values = d["annual_role_premium_m"]
    bridge = _read("valuation_bridge.csv").set_index("measure")["value"]
    median = float(values.median())
    p90 = float(values.quantile(0.90))
    old = float(bridge["old_top_down_base_net_m"])
    old_pct = float(bridge["old_top_down_percentile_in_team_distribution"])
    colors = [BLUE if v >= median else "#9bb9e0" for v in values]

    fig, ax = plt.subplots(figsize=(9.4, 5.2))
    y = np.arange(len(d))
    ax.barh(y, values, color=colors, height=0.82)
    ax.axvline(median, color=INK, linewidth=1.4)
    ax.axvline(p90, color=GRAY, linewidth=1.0, linestyle=":")
    ax.axvline(old, color=RED, linewidth=1.6, linestyle="--")
    ax.set_yticks([])
    ax.set_ylabel("32 teams, sorted")
    ax.set_xlabel("Annual role premium, actual 2026 signing class ($M/year)")
    ax.set_xlim(0, max(values.max(), old) * 1.08)
    fig.suptitle(
        f"The old \\${old:.1f}M estimate was a {old_pct*100:.1f}th-percentile team",
        x=0.01, y=1.03, ha="left", fontsize=13.0,
    )
    ax.set_title(
        f"Median team: \\${median:.2f}M gross / \\${median-1.0:.2f}M net. "
        "Conservative EDGE/S/CB: \\$1.38M gross / \\$0.38M net.",
        loc="left", fontsize=9.0, color=SECONDARY, pad=8,
    )
    box = dict(facecolor=SURFACE, edgecolor="none", pad=2)
    ax.annotate(
        f"median \\${median:.1f}M", xy=(median, len(d) * 0.50),
        xytext=(6, 0), textcoords="offset points", fontsize=8.5,
        color=INK, va="center", bbox=box,
    )
    ax.annotate(
        f"P90 \\${p90:.1f}M", xy=(p90, len(d) * 0.10),
        xytext=(6, 0), textcoords="offset points", fontsize=8.0,
        color=SECONDARY, va="center", bbox=box,
    )
    ax.annotate(
        f"old top-down \\${old:.1f}M ({old_pct*100:.1f}th pct)", xy=(old, len(d) * 0.55),
        xytext=(6, 0), textcoords="offset points", fontsize=8.5,
        color=RED, va="center", bbox=box,
    )
    ax.text(
        0.99, 0.02,
        "Actual 2026 signings; APY role premium. Inference, not a forecast.",
        transform=ax.transAxes, ha="right", fontsize=7.8, color=SECONDARY,
    )
    _save(fig, "fa_headline.png")


def market_terms() -> None:
    d = _read("fa_terms_by_position.csv")
    d = d[d["type"].isin(["re_sign", "team_change", "rookie"])].copy()
    order = d.groupby("pos_group")["median_apy_m"].max().sort_values().index
    fig, ax = plt.subplots(figsize=(8.0, 4.6))
    colors = {"re_sign": BLUE, "team_change": ORANGE, "rookie": AQUA}
    for i, pos in enumerate(order):
        sub = d[d["pos_group"].eq(pos)]
        for j, row in enumerate(sub.itertuples()):
            ax.scatter(
                row.median_apy_m, i + (j - 1) * 0.18,
                color=colors.get(row.type, GRAY), s=38, zorder=3,
            )
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels(order)
    ax.set_xlabel("Median APY ($M)")
    ax.set_title("2026 free-agent terms by position and type",
                 loc="left", fontsize=11.5, pad=10)
    handles = [plt.Line2D([], [], marker="o", color=c, linestyle="", label=l)
               for l, c in colors.items()]
    ax.legend(handles=handles, frameon=False, fontsize=8.5, loc="lower right")
    ax.text(0.01, -0.18,
            "Team change is inferred from the prior-season team; no signing dates.",
            transform=ax.transAxes, fontsize=8.0, color=SECONDARY)
    _save(fig, "fa_market_terms.png")


def role_premium() -> None:
    d = _read("role_premium.csv")
    labels = {
        "fa_2026": "2026 FA class (APY)",
        "apy_2025": "2025 active APY",
        "apy_2024": "2024 active APY",
        "cap_ledger_2025": "2025 cap ledger",
        "fa_2026_draft_matched": "2026 APY, draft-matched",
        "apy_2025_team_fe": "2025 APY, team FE",
    }
    d = d.sort_values("gap")
    y = np.arange(len(d))
    fig, ax = plt.subplots(figsize=(7.6, 4.4))
    ax.errorbar(
        d["gap"], y,
        xerr=[d["gap"] - d["gap_ci_low"], d["gap_ci_high"] - d["gap"]],
        fmt="o", color=INK, ecolor=GRAY, elinewidth=1.3, capsize=3,
        markersize=5, zorder=3,
    )
    ax.scatter(d["gap"], y,
               c=[AQUA if lo > 0 else ORANGE for lo in d["gap_ci_low"]],
               s=44, zorder=4)
    ax.axvline(0, color=BASELINE, linewidth=1)
    ax.set_yticks(y)
    ax.set_yticklabels([labels.get(s, s) for s in d["sample"]])
    ax.set_xlabel("Raw minus role-controlled perf_z coefficient (95% CI)")
    ax.set_title("The APY role premium is close to the cap gap, but fragile",
                 loc="left", fontsize=11.5, pad=10)
    ax.text(0.01, -0.20,
            "Green: gap CI above zero. Orange: includes zero. "
            "The 2026 sample is 306 contracts; the cap ledger is 909 players.",
            transform=ax.transAxes, fontsize=8.0, color=SECONDARY)
    _save(fig, "fa_role_premium.png")


def position_gaps() -> None:
    d = _read("pricing_by_position.csv")
    d = d[d["sample"].eq("cap_ledger_2025")].sort_values("gap")
    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    y = np.arange(len(d))
    ax.errorbar(
        d["gap"], y,
        xerr=[d["gap"] - d["gap_ci_low"], d["gap_ci_high"] - d["gap"]],
        fmt="o", color=INK, ecolor=GRAY, elinewidth=1.3, capsize=3,
        markersize=5, zorder=3,
    )
    ax.scatter(d["gap"], y,
               c=[AQUA if lo > 0 else ORANGE for lo in d["gap_ci_low"]],
               s=44, zorder=4)
    ax.axvline(0, color=BASELINE, linewidth=1)
    ax.set_yticks(y)
    ax.set_yticklabels(d["pos_group"])
    ax.set_xlabel("Cap-ledger raw minus role perf_z coefficient (approx. 95% CI)")
    ax.set_title("Only EDGE, S, and CB have gap CIs above zero",
                 loc="left", fontsize=11.5, pad=10)
    _save(fig, "fa_position_gaps.png")


def guarantees() -> None:
    d = _read("fa_class_2026.csv")
    d = d[d["snap_share"].notna() & d["guarantee_share"].notna()].copy()
    d["role_q"] = pd.qcut(d["snap_share"], 5, labels=False, duplicates="drop")
    g = d.groupby("role_q").agg(
        guarantee_share=("guarantee_share", "mean"),
        apy=("apy", "median"),
        n=("player", "size"),
    ).reset_index()
    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    ax.plot(g["role_q"], g["guarantee_share"], marker="o", color=BLUE, linewidth=2)
    ax.set_xticks(g["role_q"])
    ax.set_xticklabels([f"Q{i+1}" for i in g["role_q"]])
    ax.set_xlabel("Prior-season snap-share quintile")
    ax.set_ylabel("Mean guarantee share")
    ax.set_title("Guarantees track role, not just performance",
                 loc="left", fontsize=11.5, pad=10)
    ax.text(0.01, -0.20,
            "2026 signings with a 2025 snap share and guarantee term.",
            transform=ax.transAxes, fontsize=8.0, color=SECONDARY)
    _save(fig, "fa_guarantees.png")


def surplus() -> None:
    d = _read("surplus_players.csv")
    c = _read("surplus_concentration.csv")
    fig, axes = plt.subplots(1, 2, figsize=(9.8, 4.0))
    axes[0].hist(d["resid_raw"].clip(-8, 15), bins=30, color=BLUE, alpha=0.8)
    axes[0].axvline(0, color=BASELINE, linewidth=1)
    axes[0].set_xlabel("Actual APY minus market model ($M)")
    axes[0].set_ylabel("Contracts")
    axes[0].set_title("Residual distribution", loc="left", fontsize=10.5)

    rp = c[c["metric"].eq("role_premium")]
    axes[1].plot(rp["top_share"], rp["share_of_positive"], marker="o", color=ORANGE)
    axes[1].plot([0, 0.25], [0, 1], color=BASELINE, linestyle="--", linewidth=1)
    axes[1].set_xlabel("Top share of contracts")
    axes[1].set_ylabel("Share of positive role premium")
    axes[1].set_title("Concentration", loc="left", fontsize=10.5)
    fig.suptitle("The free-agent role premium is concentrated",
                 x=0.01, y=1.02, ha="left", fontsize=11.5)
    _save(fig, "fa_surplus.png")


def valuation() -> None:
    b = _read("valuation_bridge.csv").set_index("measure")["value"]
    teams = _read("valuation_by_team.csv")
    teams = teams[teams["positions"].eq("all")]
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.4))
    labels = ["Old top-down\nbase", "Old top-down\nconservative",
              "New median\nteam annual", "New mean\nteam annual",
              "New supported\nmedian annual"]
    values = [
        b.get("old_top_down_base_net_m", np.nan),
        b.get("old_top_down_conservative_net_m", np.nan),
        b.get("new_median_team_annual_m", np.nan),
        b.get("new_mean_team_annual_m", np.nan),
        b.get("new_supported_median_annual_m", np.nan),
    ]
    axes[0].bar(labels, values, color=[GRAY, GRAY, BLUE, BLUE, ORANGE])
    axes[0].set_ylabel("$M/year")
    axes[0].tick_params(axis="x", labelsize=7.5)
    axes[0].set_title("Top-down vs bottom-up", loc="left", fontsize=10.5)

    axes[1].hist(teams["annual_role_premium_m"], bins=16, color=BLUE, alpha=0.8)
    axes[1].axvline(b.get("old_top_down_base_net_m", np.nan), color=RED,
                    linestyle="--", linewidth=1.2, label="Old base")
    axes[1].axvline(teams["annual_role_premium_m"].median(), color=INK,
                    linewidth=1.2, label="Median team")
    axes[1].set_xlabel("Team annual role premium ($M)")
    axes[1].set_ylabel("Teams")
    axes[1].set_title("Team distribution", loc="left", fontsize=10.5)
    axes[1].legend(frameon=False, fontsize=8.0)
    fig.suptitle("The old $24.9M is a 90th-percentile team, not the median",
                 x=0.01, y=1.02, ha="left", fontsize=11.5)
    _save(fig, "fa_valuation.png")


def historical() -> None:
    d = _read("historical_coverage.csv")
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.8))
    axes[0].bar(d["season"], d["contracts"], color=BLUE, alpha=0.85)
    axes[0].set_xlabel("Contract signing year")
    axes[0].set_ylabel("Contracts in file")
    axes[0].set_title("Sample size", loc="left", fontsize=10.5)
    axes[1].plot(d["season"], d["age_coverage"] * 100, color=ORANGE, linewidth=2)
    axes[1].set_xlabel("Contract signing year")
    axes[1].set_ylabel("Age coverage (%)")
    axes[1].set_ylim(0, 100)
    axes[1].set_title("Date-of-birth coverage", loc="left", fontsize=10.5)
    fig.suptitle("The historical contract file is not a census",
                 x=0.01, y=1.02, ha="left", fontsize=11.5)
    _save(fig, "fa_historical_coverage.png")


def age_curves() -> None:
    d = _read("fa_age_curves.csv")
    positions = ["QB", "WR", "EDGE", "CB"]
    fig, axes = plt.subplots(1, len(positions), figsize=(10.4, 3.8), sharey=True)
    for ax, pos in zip(axes, positions):
        sub = d[d["pos_group"].eq(pos)]
        if sub.empty:
            continue
        ax.plot(range(len(sub)), sub["median_apy_m"], marker="o", color=BLUE)
        ax.set_xticks(range(len(sub)))
        ax.set_xticklabels(sub["age_bucket"], rotation=45, ha="right", fontsize=7.5)
        ax.set_title(pos, loc="left", fontsize=10.0)
    axes[0].set_ylabel("Median APY ($M)")
    fig.suptitle("Age curves for the 2026 free-agent class",
                 x=0.01, y=1.02, ha="left", fontsize=11.5)
    _save(fig, "fa_age_curves.png")


def main() -> None:
    headline()
    market_terms()
    role_premium()
    position_gaps()
    guarantees()
    surplus()
    valuation()
    historical()
    age_curves()


if __name__ == "__main__":
    main()
