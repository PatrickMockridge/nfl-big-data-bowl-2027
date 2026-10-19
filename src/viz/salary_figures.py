"""Writeup figures for the dollar extension and the persistence tests.

All six writeup figures share one grammar: sentence-case takeaway titles,
plain units in Part 1, direct labels, hairline chrome. This module writes the
salary and persistence figures directly to ``writeup/figures``; the two core
figures live in ``viz.figures`` and also land there.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from .figures import (
    ANNOT_SIZE,
    AQUA,
    BASELINE,
    BLUE,
    GRAY,
    INK,
    LABELS,
    ORANGE,
    SECONDARY,
    SURFACE,
    TICK_SIZE,
    WRITEUP_FIG,
    _cluster_boot_ci,
    _figure_title,
    _title_block,
)

ROOT = Path(__file__).resolve().parents[2]
DISC = ROOT / "outputs" / "discovery"
SAL = ROOT / "outputs" / "salary"
RNG = np.random.default_rng(42)


def _save(fig, name: str) -> Path:
    WRITEUP_FIG.mkdir(parents=True, exist_ok=True)
    path = WRITEUP_FIG / name
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    return path


def _quartile_rows(
    frame: pd.DataFrame, xcol: str, ycol: str, cluster: str, nq: int = 4
) -> np.ndarray:
    """Mean x, mean y and cluster-bootstrap CI per quantile."""
    d = frame.copy()
    d["_q"] = pd.qcut(d[xcol], nq, labels=False)
    rows = []
    for _, sub in d.groupby("_q"):
        lo, hi = _cluster_boot_ci(sub, ycol, cluster)
        rows.append((sub[xcol].mean(), sub[ycol].mean(), lo, hi, len(sub)))
    return np.asarray(rows, dtype=float)


def salary_efficiency() -> Path:
    """Figure 2: star spending is flat; rookie and homegrown snaps move."""
    d = pd.read_csv(SAL / "team_salary_panel.csv")
    specs = [
        ("star_share", "Star spending", "Star spending (% of cap)", ORANGE),
        ("rookie_snap_share", "Rookie snaps", "Rookie snap share (%)", AQUA),
        ("homegrown_snap_share", "Homegrown snaps", "Homegrown snap share (%)", AQUA),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(9.6, 4.2), sharey=True)
    for ax, (col, title, xlabel, color) in zip(axes, specs):
        rows = _quartile_rows(d, col, "wins_per_100m", "team")
        x, y, lo, hi = rows[:, 0] * 100, rows[:, 1], rows[:, 2], rows[:, 3]
        ax.plot(x, y, color=color, lw=1.5, zorder=2)
        ax.errorbar(
            x, y, yerr=[y - lo, hi - y], fmt="o", color=color, ecolor=color,
            elinewidth=1.2, capsize=0, markersize=7,
            markeredgecolor=SURFACE, markeredgewidth=0.7, zorder=3,
        )
        ax.annotate(
            f"{y[-1]:.1f}", (x[-1], y[-1]), xytext=(7, 9),
            textcoords="offset points", fontsize=ANNOT_SIZE, color=color,
            fontweight="bold",
        )
        change = y[-1] - y[0]
        change_txt = "0.0" if abs(change) < 0.05 else f"{change:+.1f}".replace("-", "−")
        ax.text(
            0.98, 0.96, f"Q4 − Q1: {change_txt}",
            transform=ax.transAxes, ha="right", va="top",
            fontsize=ANNOT_SIZE, color=SECONDARY,
            bbox=dict(facecolor=SURFACE, edgecolor="none", pad=1.5),
        )
        ax.set_title(title, loc="left", fontsize=11, color=INK, pad=8)
        ax.set_xlabel(xlabel)
        ax.grid(axis="y", alpha=0.7)
        ax.tick_params(labelsize=TICK_SIZE)
    axes[0].set_ylabel("Wins per $100M")
    axes[0].set_ylim(3.0, 5.6)
    _figure_title(fig, LABELS["fig2_title"], LABELS["fig2_subtitle"])
    return _save(fig, "salary_efficiency.png")


def qb_premium() -> Path:
    """Figure 3: a fitted quadratic peak with an honest uncertainty band."""
    d = pd.read_csv(SAL / "team_salary_panel.csv").dropna(
        subset=["wins", "qb_share", "log_payroll", "season_c"]
    ).copy()
    fit = smf.ols(
        "wins ~ qb_share + I(qb_share**2) + log_payroll + C(season_c)", data=d
    ).fit(cov_type="cluster", cov_kwds={"groups": d["team"]})
    q2 = [k for k in fit.params.index if k.startswith("I(")][0]
    b1, b2 = float(fit.params["qb_share"]), float(fit.params[q2])
    partial = fit.resid + b1 * d["qb_share"] + b2 * d["qb_share"] ** 2
    xbar = float(d["qb_share"].mean())
    xbar2 = float((d["qb_share"] ** 2).mean())
    base = float(partial.mean())
    xs = np.linspace(float(d["qb_share"].min()), float(d["qb_share"].max()), 120)
    curve = base + b1 * (xs - xbar) + b2 * (xs**2 - xbar2)

    cov = fit.cov_params().loc[["qb_share", q2], ["qb_share", q2]].to_numpy()
    draws = RNG.multivariate_normal(np.array([b1, b2]), cov, size=2000)
    curves = (
        base
        + draws[:, 0][:, None] * (xs[None, :] - xbar)
        + draws[:, 1][:, None] * (xs[None, :] ** 2 - xbar2)
    )
    lo, hi = np.percentile(curves, [2.5, 97.5], axis=0)
    inflection = -b1 / (2 * b2)

    fig, ax = plt.subplots(figsize=(7.4, 4.5))
    ax.scatter(
        d["qb_share"] * 100, partial, s=16, c=GRAY, alpha=0.55,
        edgecolors=SURFACE, linewidths=0.35, zorder=2,
    )
    ax.fill_between(xs * 100, lo, hi, color=ORANGE, alpha=0.15, lw=0, zorder=1)
    ax.plot(xs * 100, curve, color=ORANGE, lw=2.0, zorder=3)
    ax.axvline(inflection * 100, color=ORANGE, lw=1.0, ls="--", zorder=1)
    ax.set_xlim(0, max(xs * 100) + 1)
    y_top = float(np.nanmax(partial)) + 0.8
    ax.set_ylim(float(np.nanmin(partial)) - 0.8, y_top)
    ax.annotate(
        f"fitted turning point ≈{inflection * 100:.0f}%",
        (inflection * 100, y_top), xytext=(6, -12),
        textcoords="offset points", fontsize=ANNOT_SIZE, color=ORANGE,
    )
    ax.text(
        0.02, 0.05, "shaded band: 95% (clustered covariance); vertex not statistically identified",
        transform=ax.transAxes, ha="left", va="bottom",
        fontsize=8.5, color=SECONDARY,
        bbox=dict(facecolor=SURFACE, edgecolor="none", pad=2),
    )
    ax.set_xlabel("QB share of offense+defense cap spending (%)")
    ax.set_ylabel("Wins, adjusted for payroll and season")
    ax.grid(axis="y", alpha=0.7)
    ax.tick_params(labelsize=TICK_SIZE)
    _title_block(ax, LABELS["fig3_title"], LABELS["fig3_subtitle"])
    return _save(fig, "qb_premium.png")


def persistence_within_player() -> Path:
    """Figure 5: snaps persist; a better season does not earn more snaps."""
    d = pd.read_parquet(DISC / "role_allocation_player_seasons_full.parquet")
    d = d[d["next_role"].notna()].copy()
    w = pd.read_parquet(DISC / "role_within_player.parquet").copy()

    fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.3))
    x = np.arange(5)
    specs = [
        (
            axes[0], d, "role_z", "next_role",
            "Current snaps → next season",
            "Playing time quintile\n(low → high)",
            "Next-season playing time (SD)",
            ORANGE, "n=233", "model: +0.61 per SD",
        ),
        (
            axes[1], w, "d_perf", "d_role",
            "Change in performance → change in snaps",
            "Change in performance quintile\n(worst → best)",
            "Change in playing time (SD)",
            BLUE, "n=235", "model: −0.10 (p=0.11)",
        ),
    ]
    for ax, frame, xcol, ycol, title, xlabel, ylabel, color, ntext, slope in specs:
        rows = _quartile_rows(frame, xcol, ycol, "nfl_id", nq=5)
        y, lo, hi = rows[:, 1], rows[:, 2], rows[:, 3]
        ax.axhline(0, color=BASELINE, lw=0.9, zorder=1)
        ax.plot(x, y, color=color, lw=1.5, zorder=2)
        ax.errorbar(
            x, y, yerr=[y - lo, hi - y], fmt="o", color=color, ecolor=color,
            elinewidth=1.2, capsize=0, markersize=7,
            markeredgecolor=SURFACE, markeredgewidth=0.7, zorder=3,
        )
        ax.annotate(
            f"{y[-1]:+.2f}", (x[-1], y[-1]), xytext=(8, 0),
            textcoords="offset points", va="center", fontsize=9.5,
            color=color, fontweight="bold",
        )
        ax.set_xticks(x)
        ax.set_xticklabels(["1", "2", "3", "4", "5"])
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_ylim(-1.1, 1.5)
        ax.set_title(title, loc="left", fontsize=10.5, color=INK, pad=8)
        ax.grid(axis="y", alpha=0.7)
        ax.tick_params(labelsize=TICK_SIZE)
        ax.text(0.02, 0.96, ntext, transform=ax.transAxes, ha="left", va="top",
                fontsize=ANNOT_SIZE, color=GRAY)
        ax.text(0.02, 0.89, slope, transform=ax.transAxes, ha="left", va="top",
                fontsize=8.5, color=SECONDARY)
    _figure_title(fig, LABELS["fig5_title"], LABELS["fig5_subtitle"])
    return _save(fig, "persistence_within_player.png")


def overpay_quartiles() -> Path:
    """Figure 6: above-model cap dollars by 2025 efficiency quartile."""
    d = pd.read_csv(SAL / "rent_quartiles.csv")
    x = np.arange(len(d))
    star = d["star_rent_m"].to_numpy(dtype=float)
    under = d["under_rent_m"].to_numpy(dtype=float)
    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    ax.bar(
        x, star, width=0.58, color=GRAY, edgecolor=SURFACE, linewidth=1.5,
        label="Star cap dollars", zorder=2,
    )
    ax.bar(
        x, under, width=0.58, bottom=star, color=ORANGE, edgecolor=SURFACE,
        linewidth=1.5, label="Underperformers", zorder=2,
    )
    for xi, total in zip(x, star + under):
        ax.annotate(
            f"${total:.0f}M", (xi, total), xytext=(0, 6),
            textcoords="offset points", ha="center", va="bottom",
            fontsize=9.5, color=INK,
        )
    ax.set_xticks(x)
    ax.set_xticklabels(["Q1\nleast efficient", "Q2", "Q3", "Q4\nmost efficient"])
    ax.set_xlabel("2025 efficiency quartile (wins per $100M)")
    ax.set_ylabel("$M per team above the pay model")
    ax.set_ylim(0, 82)
    ax.grid(axis="y", alpha=0.7)
    ax.tick_params(labelsize=TICK_SIZE)
    ax.text(
        3.42, 80,
        "Most vs least efficient\n"
        "Total −$20.5M (−$40.9M to −$2.0M)\n"
        "Underperformers −$6.3M (−$14.5M to −$0.2M)",
        ha="right", va="top", fontsize=8.5, color=SECONDARY,
        linespacing=1.35,
    )
    ax.legend(loc="upper left", fontsize=8.5)
    _title_block(ax, LABELS["fig6_title"], LABELS["fig6_subtitle"])
    return _save(fig, "overpay_quartiles.png")


def main() -> None:
    print(persistence_within_player())
    print(salary_efficiency())
    print(qb_premium())
    print(overpay_quartiles())


if __name__ == "__main__":
    main()
