"""Salary and combined core figures for the dollar extension.

The palette and chrome come from ``viz.figures`` (validated blue/orange/aqua,
light surface, hairline grid). Figures are written directly to
``writeup/figures`` so the writeup and notebook use the same files.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .figures import AQUA, BASELINE, BLUE, GRAY, GRID, INK, ORANGE, SECONDARY, SURFACE

ROOT = Path(__file__).resolve().parents[2]
DISC = ROOT / "outputs" / "discovery"
SAL = ROOT / "outputs" / "salary"
WRITEUP_FIG = ROOT / "writeup" / "figures"
RNG = np.random.default_rng(42)


def _save(fig, name: str) -> Path:
    WRITEUP_FIG.mkdir(parents=True, exist_ok=True)
    path = WRITEUP_FIG / name
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    return path


def _fit(ax, x, y, color, lw=1.5):
    mask = np.isfinite(x) & np.isfinite(y)
    coef = np.polyfit(x[mask], y[mask], 1)
    xs = np.linspace(np.nanmin(x), np.nanmax(x), 60)
    ax.plot(xs, np.polyval(coef, xs), color=color, lw=lw)
    return coef


def persistence_within_player() -> Path:
    d = pd.read_parquet(DISC / "role_allocation_player_seasons.parquet")
    w = pd.read_parquet(DISC / "role_within_player.parquet")

    fig, axes = plt.subplots(1, 3, figsize=(12.6, 4.0))
    specs = [
        (axes[0], d["role_z"], d["next_role"], "Current role (z)", BLUE),
        (axes[1], d["perf_z"], d["next_role"], "Performance (z)", ORANGE),
    ]
    for ax, x, y, label, color in specs:
        ax.scatter(x, y, s=15, c=GRAY, alpha=0.40, edgecolors=SURFACE, linewidths=0.3)
        coef = _fit(ax, x.to_numpy(), y.to_numpy(), color)
        ax.axhline(0, color=BASELINE, lw=0.8)
        ax.set_xlabel(label)
        ax.set_title(f"{label.split(' (')[0]} → next role", loc="left", fontsize=10)
        ax.annotate(f"slope {coef[0]:+.2f}", (0.04, 0.92), xycoords="axes fraction",
                    fontsize=8, color=SECONDARY)
        ax.grid(alpha=0.7)
    axes[0].set_ylabel("Next-season role (z)")

    ax = axes[2]
    ax.scatter(w["d_perf"], w["d_role"], s=18, c=GRAY, alpha=0.50,
               edgecolors=SURFACE, linewidths=0.3)
    coef = _fit(ax, w["d_perf"].to_numpy(), w["d_role"].to_numpy(), ORANGE)
    ax.axhline(0, color=BASELINE, lw=0.8)
    ax.axvline(0, color=BASELINE, lw=0.8)
    ax.set_xlabel("Change in performance (z)")
    ax.set_ylabel("Change in role (z)")
    ax.set_title("Within-player change", loc="left", fontsize=10)
    ax.annotate(f"slope {coef[0]:+.3f} (n={len(w)})", (0.04, 0.92), xycoords="axes fraction",
                fontsize=8, color=SECONDARY)
    ax.grid(alpha=0.7)

    fig.suptitle("Role persists; performance does not", x=0.01, ha="left",
                 fontsize=12, color=INK)
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    return _save(fig, "persistence_within_player.png")


def salary_efficiency() -> Path:
    d = pd.read_csv(SAL / "team_salary_panel.csv")
    seasons = sorted(d["season"].unique())
    colors = dict(zip(seasons, [BLUE, ORANGE, AQUA]))

    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.3))
    ax = axes[0]
    for season in seasons:
        s = d[d["season"] == season]
        ax.scatter(s["star_share"], s["wins_per_100m"], s=26, c=colors[season],
                   alpha=0.75, edgecolors=SURFACE, linewidths=0.4, label=str(season))
    _fit(ax, d["star_share"].to_numpy(), d["wins_per_100m"].to_numpy(), GRAY, lw=1.2)
    ax.set_xlabel("Star / highlight-reel share of offense+defense cap spending")
    ax.set_ylabel("Wins per $100M (offense+defense)")
    ax.set_title("Star share: flat", loc="left", fontsize=10)
    ax.grid(alpha=0.7)
    ax.legend(loc="upper right", fontsize=7.5, title="Season")

    ax = axes[1]
    ax.scatter(d["rookie_snap_share"], d["wins_per_100m"], s=24, c=ORANGE,
               alpha=0.75, edgecolors=SURFACE, linewidths=0.4, label="Rookie snap share")
    ax.scatter(d["homegrown_snap_share"], d["wins_per_100m"], s=24, c=BLUE,
               alpha=0.65, edgecolors=SURFACE, linewidths=0.4, label="Homegrown snap share")
    _fit(ax, d["rookie_snap_share"].to_numpy(), d["wins_per_100m"].to_numpy(), ORANGE)
    _fit(ax, d["homegrown_snap_share"].to_numpy(), d["wins_per_100m"].to_numpy(), BLUE)
    ax.set_xlabel("Share of team snaps")
    ax.set_ylabel("Wins per $100M")
    ax.set_title("Rookie volume vs homegrown continuity", loc="left", fontsize=10)
    ax.grid(alpha=0.7)
    ax.legend(loc="lower right", fontsize=7.5)

    fig.suptitle("The dollar data do not show a simple star or youth premium",
                 x=0.01, ha="left", fontsize=12, color=INK)
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    return _save(fig, "salary_efficiency.png")


def qb_premium() -> Path:
    d = pd.read_csv(SAL / "team_salary_panel.csv")
    q = pd.read_csv(SAL / "qb_premium.csv")
    seasons = sorted(d["season"].unique())
    colors = dict(zip(seasons, [BLUE, ORANGE, AQUA]))

    fig, axes = plt.subplots(2, 2, figsize=(10.8, 8.0))
    ax = axes[0, 0]
    for season in seasons:
        s = d[d["season"] == season]
        ax.scatter(s["qb_share"], s["wins_per_100m"], s=26, c=colors[season],
                   alpha=0.75, edgecolors=SURFACE, linewidths=0.4, label=str(season))
    coef = np.polyfit(d["qb_share"], d["wins_per_100m"], 2)
    xs = np.linspace(d["qb_share"].min(), d["qb_share"].max(), 80)
    ax.plot(xs, np.polyval(coef, xs), color=GRAY, lw=1.5)
    inf = q.loc[q["outcome"].eq("wins_per_100m"), "inflection_qb_share"].dropna()
    if len(inf):
        ax.axvline(float(inf.iloc[0]), color=ORANGE, lw=1.0, linestyle="--")
        ax.annotate(f"model peak ≈ {float(inf.iloc[0]):.0%}",
                    (float(inf.iloc[0]), ax.get_ylim()[1]), xytext=(6, -12),
                    textcoords="offset points", fontsize=7.5, color=ORANGE)
    ax.set_xlabel("QB share of offense+defense cap spending")
    ax.set_ylabel("Wins per $100M")
    ax.set_title("Raw quadratic fit", loc="left", fontsize=10)
    ax.grid(alpha=0.7)
    ax.legend(loc="lower right", fontsize=7.5, title="Season")

    d25 = d[d["season"] == 2025].copy()
    d25["top_qb"] = d25["cap_qb_share"] >= d25["cap_qb_share"].quantile(0.75)

    def dot(ax, outcome: str, label: str):
        vals_top = d25.loc[d25["top_qb"], outcome].to_numpy()
        vals_rest = d25.loc[~d25["top_qb"], outcome].to_numpy()
        rows = []
        for vals, name, color in [(vals_top, "Top quartile", ORANGE), (vals_rest, "Rest", BLUE)]:
            draws = [RNG.choice(vals, len(vals), True).mean() for _ in range(2000)]
            rows.append((vals.mean(), np.percentile(draws, 2.5), np.percentile(draws, 97.5), name, color))
        for i, (mean, lo, hi, name, color) in enumerate(rows):
            y = 1 - i
            ax.errorbar(mean, y, xerr=[[mean - lo], [hi - mean]], fmt="o",
                        color=color, ecolor=color, capsize=0, markersize=7,
                        markeredgecolor=SURFACE, markeredgewidth=0.5, label=name)
            ax.annotate(f"{mean:+.1f}", (mean, y), xytext=(0, 8),
                        textcoords="offset points", ha="center", fontsize=7.5, color=SECONDARY)
        ax.set_yticks([0, 1])
        ax.set_yticklabels(["Rest", "Top quartile"])
        ax.set_xlabel(label)
        ax.grid(axis="x", alpha=0.7)
        ax.legend(loc="lower right", fontsize=7.5)

    dot(axes[0, 1], "wins", "2025 wins (bootstrap 95% CI)")
    axes[0, 1].set_title("Top-quartile QB cap share: wins", loc="left", fontsize=10)
    dot(axes[1, 0], "point_diff", "2025 point differential (bootstrap 95% CI)")
    axes[1, 0].set_title("Top-quartile QB cap share: point differential", loc="left", fontsize=10)

    ax = axes[1, 1]
    d25 = d25.sort_values("cap_qb_share")
    ax.scatter(d25["cap_qb_share"], d25["wins_per_100m"], s=26, c=GRAY, alpha=0.65,
               edgecolors=SURFACE, linewidths=0.4)
    _fit(ax, d25["cap_qb_share"].to_numpy(), d25["wins_per_100m"].to_numpy(), ORANGE)
    ax.set_xlabel("2025 QB share of active cap (OTC)")
    ax.set_ylabel("Wins per $100M")
    ax.set_title("2025 cross-section", loc="left", fontsize=10)
    ax.grid(alpha=0.7)

    fig.suptitle("The perfect-QB premium flattens", x=0.01, ha="left",
                 fontsize=12, color=INK)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    return _save(fig, "qb_premium.png")


def main() -> None:
    print(persistence_within_player())
    print(salary_efficiency())
    print(qb_premium())


if __name__ == "__main__":
    main()
