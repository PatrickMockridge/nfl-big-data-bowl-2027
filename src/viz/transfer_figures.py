"""Figures for the transfer pilots.

Reuses the palette and surface conventions in ``src/viz/figures.py``. Every
figure is descriptive; the link matrix carries the pre-registered status
vocabulary, not a score.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle

from transfer.common import OUT, ROOT

FIG = ROOT / "transfer" / "writeups" / "figures"

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
    "supported": AQUA,
    "weak": ORANGE,
    "null": GRAY,
    "unidentifiable": "#d9d8d0",
    "unpriced": AQUA,
    "partly priced": ORANGE,
    "priced": GRAY,
    "negative": RED,
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
        "text.color": INK,
        "axes.labelcolor": SECONDARY,
        "xtick.color": SECONDARY,
        "ytick.color": SECONDARY,
    }
)


def _read(name: str) -> pd.DataFrame:
    return pd.read_csv(OUT / name)


def _save(fig, name: str) -> Path:
    FIG.mkdir(parents=True, exist_ok=True)
    path = FIG / name
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {path.relative_to(ROOT)}")
    return path


def _area_label(area: str) -> str:
    return {
        "DL_INTERIOR": "DL interior",
        "DL_EDGE": "DL edge",
    }.get(area, area)


def link_matrix() -> None:
    l1 = _read("drill_translation.csv")
    l2 = _read("signal_pricing.csv")
    role = _read("role_equations_reference.csv")

    l2_primary = l2[l2["signal_kind"] == "primary"].set_index("position_group")
    role = role.set_index("position_group")

    areas = ["WR", "TE", "OL", "DL_INTERIOR", "DL_EDGE", "DB"]
    rows = []
    for area in areas:
        position = "DL" if area.startswith("DL_") else area
        l1_row = l1[l1["area"] == area]
        l1_status = l1_row["status"].iloc[0] if len(l1_row) else "unidentifiable"
        l2_status = (
            l2_primary.loc[position, "interpretation"]
            if position in l2_primary.index
            else "unidentifiable"
        )
        if position not in role.index:
            l3_status = "unidentifiable"
        else:
            r = role.loc[position]
            if not bool(r["perf_identifiable"]):
                l3_status = "unidentifiable"
            elif r["perf_ci_low"] > 0:
                l3_status = "supported"
            elif r["perf_ci_high"] < 0:
                l3_status = "negative"
            else:
                l3_status = "null"
        rows.append((area, l1_status, l2_status, l3_status))

    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    ax.set_xlim(0, 3)
    ax.set_ylim(-0.32, len(areas) + 0.6)
    ax.axis("off")
    headers = ["L1 measurement", "L2 unpriced by draft", "L3 allocation null"]
    for x, header in enumerate(headers):
        ax.text(x + 0.5, len(areas) + 0.12, header, ha="center", va="bottom",
                fontsize=9.5, color=SECONDARY)
    for y, (area, a, b, c) in enumerate(rows):
        yy = len(areas) - y - 1
        ax.text(-0.12, yy + 0.5, _area_label(area), ha="right", va="center",
                fontsize=9.5, color=INK)
        for x, status in enumerate([a, b, c]):
            color = STATUS_COLORS.get(status, GRAY)
            ax.add_patch(
                Rectangle((x + 0.02, yy + 0.08), 0.96, 0.84,
                          facecolor=color, edgecolor="none", alpha=0.85)
            )
            ax.text(x + 0.5, yy + 0.5, status, ha="center", va="center",
                    fontsize=8.5, color="white" if status in {"supported", "weak", "negative"} else INK)
    fig.suptitle(
        "What transfers: the unpriced-signal and allocation links; measurement is position-specific",
        x=0.01, y=1.02, ha="left", fontsize=11.5, color=INK,
    )
    ax.text(
        0, -0.20,
        "Tier 1 descriptive. Supported: beta > 0 and CI excludes zero.\n"
        "Unidentifiable: reliability or sample gate failed. DB: zero performance variance.\n"
        "DL transfer rows are Holm-marginal (p=0.054–0.061) and add no incremental R² over the stopwatch.",
        fontsize=8.0, color=SECONDARY, transform=ax.transAxes,
        linespacing=1.5,
    )
    _save(fig, "transfer_link_matrix.png")


def forest() -> None:
    l1 = _read("drill_translation.csv").dropna(subset=["beta"])
    l1 = l1.sort_values("beta")
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    y = np.arange(len(l1))
    colors = [STATUS_COLORS.get(s, GRAY) for s in l1["status"]]
    ax.errorbar(
        l1["beta"], y,
        xerr=[l1["beta"] - l1["ci_low"], l1["ci_high"] - l1["beta"]],
        fmt="o", color=INK, ecolor=GRAY, elinewidth=1.4, capsize=3, markersize=5, zorder=3,
    )
    ax.scatter(l1["beta"], y, c=colors, s=46, zorder=4)
    ax.axvline(0, color=BASELINE, linewidth=1)
    signal_names = {
        "WR": "route drill",
        "TE": "route drill",
        "OL": "pass-set drill",
        "DB": "backpedal drill",
        "DL": "pass-rush drill",
    }
    labels = []
    for row in l1.itertuples():
        signal = (
            "entry burst"
            if row.role == "benchmark"
            else signal_names.get(row.position_group, "drill")
        )
        label = f"{_area_label(row.area)} — {signal} ({int(row.rows)} rows)"
        if row.role == "primary" and np.isfinite(row.signal_reliability):
            label += f", r={row.signal_reliability:.2f}"
        labels.append(label)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=8.6)
    ax.set_xlabel("Standardized beta: drill signal → position outcome (95% CI)")
    ax.set_title(
        "The DL pressure signal survives the task-matched drill; WR is weak; TE and OL fail the gates",
        loc="left", fontsize=10.8, pad=10,
    )
    ax.text(
        0.01, -0.20,
        "Rows are player-seasons; r is odd/even-drill signal reliability. "
        "TE: outcome reliability 0.45. OL: signal reliability 0.45. DB: outcome zero variance.",
        transform=ax.transAxes, fontsize=8.0, color=SECONDARY,
    )
    _save(fig, "transfer_drill_forest.png")


def gap_by_draft() -> None:
    gap = _read("gap_by_position.csv")
    order = ["Q1 late/UDFA", "Q2", "Q3", "Q4 early"]
    colors = {"WR": BLUE, "TE": ORANGE, "OL": AQUA, "DL": GRAY, "DB": RED}
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    for position, sub in gap.groupby("position_group"):
        sub = sub.set_index("draft_q").reindex(order).reset_index()
        if sub["mean_gap"].isna().all():
            continue
        x = np.arange(len(order))
        ax.plot(x, sub["mean_gap"], marker="o", linewidth=1.8,
                color=colors.get(position, GRAY), label=position)
        ax.fill_between(x, sub["ci_low"], sub["ci_high"],
                        color=colors.get(position, GRAY), alpha=0.10, linewidth=0)
    ax.axhline(0, color=BASELINE, linewidth=1)
    ax.set_xticks(np.arange(len(order)))
    ax.set_xticklabels(order)
    ax.set_ylabel("Performance z − role z")
    ax.set_title(
        "The allocation gap by draft quartile, position by position",
        loc="left", fontsize=11.5, pad=10,
    )
    ax.legend(frameon=False, ncols=5, fontsize=8.5, loc="upper left")
    ax.text(
        0.01, -0.18, "Role sample: 233 player-seasons; whiskers: player-cluster 95% CI.",
        transform=ax.transAxes, fontsize=8.2, color=SECONDARY,
    )
    _save(fig, "transfer_gap_by_draft.png")


def breadth() -> None:
    table = _read("burst_outcome_breadth.csv").dropna(subset=["beta"])
    order = [
        "pressure_rate",
        "hurry_rate",
        "sack_rate",
        "quick_pressure_rate",
        "unblocked_pressure_rate",
        "tfl_rate",
        "tackle_rate",
        "forced_fumble_rate",
    ]
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.6), sharex=True)
    fig.subplots_adjust(wspace=0.62)
    for ax, subgroup in zip(axes, ["INTERIOR", "EDGE"]):
        sub = (
            table[table["subgroup"] == subgroup]
            .set_index("outcome")
            .reindex(order)
            .reset_index()
        )
        y = np.arange(len(order))
        colors = [
            AQUA if f == "pressure-adjacent" else ORANGE for f in sub["family"]
        ]
        ax.errorbar(
            sub["beta"], y,
            xerr=[sub["beta"] - sub["ci_low"], sub["ci_high"] - sub["beta"]],
            fmt="o", color=INK, ecolor=GRAY, elinewidth=1.3, capsize=2.5,
            markersize=4, zorder=3,
        )
        ax.scatter(sub["beta"], y, c=colors, s=40, zorder=4)
        ax.axvline(0, color=BASELINE, linewidth=1)
        ax.set_yticks(y)
        ax.set_ylim(-0.6, len(order) - 0.4)
        ax.set_title(subgroup.title(), loc="left", fontsize=10.5)
        ax.set_xlabel("Burst beta (95% CI)")
    axes[0].set_yticklabels(order, fontsize=8.2)
    axes[1].set_yticklabels([])
    axes[0].text(
        0.01, -0.22,
        "Green: pressure-adjacent. Orange: box-score. Rows ordered identically across facets. "
        "n ≥ 100 snaps; Holm within subgroup.",
        transform=axes[0].transAxes, fontsize=8.0, color=SECONDARY,
    )
    fig.suptitle(
        "Outcome breadth: the burst is a pressure signal, not a box-score signal",
        x=0.01, y=1.02, ha="left", fontsize=11.5,
    )
    _save(fig, "transfer_burst_breadth.png")


def career() -> None:
    ladder = _read("career_ladder.csv")
    order = ["Q1 late/UDFA", "Q2", "Q3", "Q4 early"]
    ladder = ladder.set_index("draft_q").reindex(order).reset_index()
    fig, ax = plt.subplots(figsize=(6.8, 4.0))
    x = np.arange(len(order))
    ax.plot(x, ladder["start_rate_mean"], marker="o", color=BLUE, linewidth=2)
    ax.set_xticks(x)
    ax.set_xticklabels(order)
    ax.set_ylim(0, 0.75)
    ax.set_ylabel("Career starts / active games")
    ax.set_title(
        "The BDB reward proxy is status-legible too",
        loc="left", fontsize=11.5, pad=10,
    )
    for xi, row in ladder.iterrows():
        ax.annotate(
            f"{row['start_rate_mean']:.2f}",
            (xi, row["start_rate_mean"]),
            textcoords="offset points", xytext=(0, 8),
            ha="center", fontsize=8.5, color=SECONDARY,
        )
    ax.text(
        0.01, -0.20,
        "Descriptive only: cumulative starts are mechanically tied to role. "
        f"Awards: {int(ladder['awards'].sum())} of {int(ladder['n'].sum())} players.",
        transform=ax.transAxes, fontsize=8.0, color=SECONDARY,
    )
    _save(fig, "transfer_career_ladder.png")


def main() -> None:
    link_matrix()
    forest()
    gap_by_draft()
    breadth()
    career()


if __name__ == "__main__":
    main()
