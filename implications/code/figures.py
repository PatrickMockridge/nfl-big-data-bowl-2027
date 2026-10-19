"""Figures for the implications extension.

Two publication-style figures:
- value_bridge.png: low/base/high stacked value by route.
- sensitivity.png: tornado of the annual total against each assumption.

The palette matches src/viz/figures.py. Dollar figures are inferences.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "implications" / "outputs"
FIG = ROOT / "implications" / "writeups" / "figures"

BLUE = "#2a78d6"
ORANGE = "#eb6834"
AQUA = "#1baf7a"
GRAY = "#898781"
INK = "#0b0b0b"
SECONDARY = "#52514e"
SURFACE = "#fcfcfb"
BASELINE = "#c3c2b7"
GRID = "#e1e0d9"

plt.rcParams.update(
    {
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "axes.titlesize": 12.5,
        "axes.labelsize": 10,
        "axes.edgecolor": BASELINE,
        "axes.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "xtick.color": SECONDARY,
        "ytick.color": SECONDARY,
        "text.color": INK,
        "axes.labelcolor": SECONDARY,
        "grid.color": GRID,
        "grid.linewidth": 0.7,
        "legend.frameon": False,
    }
)


def _save(fig: plt.Figure, name: str) -> Path:
    FIG.mkdir(parents=True, exist_ok=True)
    path = FIG / name
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return path


def value_bridge() -> Path:
    d = (
        pd.read_csv(OUT / "value_bridge.csv")
        .set_index("scenario")
        .loc[["Low", "Base", "High"]]
    )
    fig, ax = plt.subplots(figsize=(8.8, 4.6))
    x = np.arange(len(d))
    width = 0.56
    bottom = np.zeros(len(d))
    segments = [
        ("selection_m", BLUE, "Selection surplus", "white"),
        ("role_m", ORANGE, "Role reallocation", "white"),
        ("contract_m", AQUA, "Contract pricing", INK),
    ]
    for col, color, label, text_color in segments:
        values = d[col].to_numpy()
        ax.bar(
            x,
            values,
            width,
            bottom=bottom,
            color=color,
            label=label,
            edgecolor=SURFACE,
            linewidth=1.5,
        )
        for xi, value, base in zip(x, values, bottom):
            if value >= 1.2:
                ax.text(
                    xi,
                    base + value / 2,
                    f"${value:.1f}M",
                    ha="center",
                    va="center",
                    fontsize=8,
                    color=text_color,
                )
        bottom += values
    for xi, total in zip(x, bottom):
        ax.text(
            xi,
            total + 0.35,
            f"Gross ${total:.1f}M",
            ha="center",
            va="bottom",
            fontsize=9.5,
            fontweight="bold",
            color=INK,
        )
    ax.set_xticks(x)
    ax.set_xticklabels(["Low", "Base", "High"])
    ax.set_ylabel("$M per year")
    ax.set_ylim(0, max(bottom) * 1.24)
    ax.grid(axis="y", alpha=0.8)
    ax.set_axisbelow(True)
    ax.set_title(
        "Value to one team: ~$6.6M gross/year at base",
        loc="left",
        fontsize=13,
        color=INK,
        pad=24,
    )
    ax.text(
        0,
        1.045,
        "Base net $5.6M; EV $2.3M at 40% adoption. "
        "Low/base/high assumptions; dollar figures are inferences.",
        transform=ax.transAxes,
        fontsize=8.2,
        color=SECONDARY,
        va="bottom",
    )
    ax.legend(loc="upper left", ncol=3, fontsize=8.5, handlelength=1.2)
    fig.tight_layout()
    return _save(fig, "value_bridge.png")


def sensitivity() -> Path:
    s = pd.read_csv(OUT / "sensitivity.csv")
    s = s[s["basis"].eq("net")].copy()
    bridge = pd.read_csv(OUT / "value_bridge.csv").set_index("scenario")
    base_total = float(bridge.loc["Base", "net_m"])
    s["low_delta"] = s["low_net_m"] - base_total
    s["high_delta"] = s["high_net_m"] - base_total
    s = s.sort_values("abs_swing_m", ascending=True).reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(9.0, 6.0))
    y = np.arange(len(s))
    ax.barh(
        y,
        s["low_delta"],
        color=ORANGE,
        alpha=0.92,
        label="Low assumption",
        height=0.62,
    )
    ax.barh(
        y,
        s["high_delta"],
        color=BLUE,
        alpha=0.92,
        label="High assumption",
        height=0.62,
    )
    for yi, low, high, low_total, high_total in zip(
        y,
        s["low_delta"],
        s["high_delta"],
        s["low_net_m"],
        s["high_net_m"],
    ):
        if abs(high - low) < 0.6:
            ax.text(
                max(low, high) + 0.12,
                yi,
                f"≈${(low_total + high_total) / 2:.1f}M",
                ha="left",
                va="center",
                fontsize=7.5,
                color=SECONDARY,
            )
            continue
        if abs(low) > 0.05:
            ax.text(
                low - 0.12,
                yi,
                f"${low_total:.1f}M",
                ha="right",
                va="center",
                fontsize=7.5,
                color=SECONDARY,
            )
        if abs(high) > 0.05:
            ax.text(
                high + 0.12,
                yi,
                f"${high_total:.1f}M",
                ha="left",
                va="center",
                fontsize=7.5,
                color=SECONDARY,
            )
    ax.axvline(0, color=BASELINE, lw=1.0)
    ax.set_yticks(y)
    ax.set_yticklabels(s["label"], fontsize=8.5)
    ax.tick_params(axis="y", pad=8)
    span = max(abs(s["low_delta"].min()), abs(s["high_delta"].max()))
    ax.set_xlim(-span - 1.0, span + 1.0)
    ax.set_xlabel("Change from the base net value ($M/year)")
    ax.grid(axis="x", alpha=0.8)
    ax.set_axisbelow(True)
    ax.set_title(
        "Which assumptions move the annual value most",
        loc="left",
        fontsize=13,
        color=INK,
        pad=24,
    )
    ax.text(
        0,
        1.035,
        "Base net ${:.1f}M/year; each input varied low/high with the others at base. "
        "Adoption probability is excluded (it scales expected value, not the net total).".format(
            base_total
        ),
        transform=ax.transAxes,
        fontsize=8.5,
        color=SECONDARY,
        va="bottom",
    )
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.14),
        ncol=2,
        fontsize=8.5,
        handlelength=1.2,
    )
    fig.tight_layout()
    return _save(fig, "sensitivity.png")


def main() -> None:
    print(value_bridge())
    print(sensitivity())


if __name__ == "__main__":
    main()
