"""Cost-risk writeup figures for the kept entry.

Three new figures: position-specific Combine linkage, signed net rent, and the
performance-role allocation gap. They share the ``viz.figures`` grammar.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .figures import (
    ANNOT_SIZE,
    AQUA,
    BASELINE,
    BLUE,
    GRAY,
    INK,
    ORANGE,
    SECONDARY,
    SURFACE,
    TICK_SIZE,
    WRITEUP_FIG,
    _boot_ci,
    _figure_title,
    _save_both,
)

ROOT = Path(__file__).resolve().parents[2]
DISC = ROOT / "outputs" / "discovery"
SAL = ROOT / "outputs" / "salary"
RNG = np.random.default_rng(20261019)


def _save(fig, name: str) -> Path:
    WRITEUP_FIG.mkdir(parents=True, exist_ok=True)
    path = WRITEUP_FIG / name
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    return path


def combine_by_position() -> Path:
    """Figure 1: the Combine signal is real for DL, not universal."""
    d = pd.read_csv(DISC / "combine_linkage_by_position.csv")
    rows = d[d["sample"].eq("by_position")].copy()
    pooled = d[d["sample"].eq("pooled")].iloc[0]
    order = ["DL", "WR", "OL", "TE"]
    rows["position_group"] = pd.Categorical(rows["position_group"], order, ordered=True)
    rows = rows.sort_values("position_group")
    rows["beta"] = rows["std_beta"]
    rows["beta_lo"] = rows["ci_low"] * rows["sd_x"] / rows["sd_y"]
    rows["beta_hi"] = rows["ci_high"] * rows["sd_x"] / rows["sd_y"]
    labels = {
        "DL": "DL\n(get-off)",
        "WR": "WR\n(separation)",
        "OL": "OL\n(pressure allowed)",
        "TE": "TE\n(separation)",
    }

    fig, ax = plt.subplots(figsize=(7.4, 4.3))
    y = np.arange(len(rows))
    for i, (_, r) in enumerate(rows.iterrows()):
        color = BLUE if r["p"] < 0.05 else GRAY
        ax.plot([r["beta_lo"], r["beta_hi"]], [i, i], color=color, lw=1.8, zorder=2)
        ax.plot(r["beta"], i, "o", color=color, markersize=8, markeredgecolor=SURFACE,
                markeredgewidth=0.8, zorder=3)
        p_txt = "p<0.001" if r["p"] < 0.001 else f"p={r['p']:.2f}"
        ax.annotate(f"{r['beta']:+.2f}  ({p_txt})", (r["beta_hi"], i), xytext=(8, 0),
                    textcoords="offset points", va="center", fontsize=ANNOT_SIZE,
                    color=color, fontweight="bold" if r["p"] < 0.05 else "normal")
    ax.axvline(0, color=BASELINE, lw=1.0, zorder=1)
    ax.axvline(pooled["std_beta"], color=GRAY, lw=1.0, ls="--", zorder=1)
    ax.annotate(
        f"pooled {pooled['std_beta']:+.2f}",
        (pooled["std_beta"], len(rows) - 0.35), xytext=(4, 0),
        textcoords="offset points", va="center", fontsize=8.5, color=SECONDARY,
    )
    ax.set_yticks(y)
    ax.set_yticklabels([labels[p] for p in rows["position_group"]], fontsize=TICK_SIZE)
    ax.set_xlabel("Performance (SD per SD of Combine movement)")
    ax.set_xlim(-0.12, 0.62)
    ax.set_ylim(-0.6, len(rows) - 0.2)
    ax.grid(axis="x", alpha=0.7)
    ax.tick_params(labelsize=TICK_SIZE)
    _figure_title(
        fig,
        "The Combine signal is real for defensive linemen, not universal.",
        "Standardized coefficient, 95% CI; DL is the only position group with a detectable link; interaction p=0.0004.",
    )
    return _save(fig, "combine_linkage.png")


def net_rent() -> Path:
    """Figure 4: signed net rent and the nested pay model."""
    groups = pd.read_csv(SAL / "net_rent_groups.csv")
    nested = pd.read_csv(SAL / "pay_model_nested.csv")
    cap = groups[groups["grouping"].eq("cap_quartile")].copy()
    cap["group"] = pd.Categorical(cap["group"], ["Q1", "Q2", "Q3", "Q4"], ordered=True)
    cap = cap.sort_values("group")
    perf = nested[nested["term"].eq("perf_z")].copy()
    perf["model"] = pd.Categorical(perf["model"], ["base", "role", "role_draft"], ordered=True)
    perf = perf.sort_values("model")

    fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.2))
    ax = axes[0]
    colors = [GRAY if v < 0 else ORANGE for v in cap["mean_m"]]
    ax.bar(np.arange(len(cap)), cap["mean_m"], color=colors, width=0.6,
           edgecolor=SURFACE, linewidth=1.5, zorder=2)
    for i, v in enumerate(cap["mean_m"]):
        ax.annotate(f"{v:+.1f}", (i, v), xytext=(0, 5 if v >= 0 else -12),
                    textcoords="offset points", ha="center", fontsize=9.5,
                    color=INK if v >= 0 else SECONDARY)
    ax.axhline(0, color=BASELINE, lw=1.0, zorder=1)
    ax.set_xticks(np.arange(len(cap)))
    ax.set_xticklabels(["Q1\nlowest cap", "Q2", "Q3", "Q4\nhighest cap"])
    ax.set_ylabel("$M per player above the pay model")
    ax.set_ylim(-2.0, 7.6)
    ax.set_title("Signed net rent by cap quartile", loc="left", fontsize=10.5, color=INK, pad=8)
    ax.grid(axis="y", alpha=0.7)
    ax.tick_params(labelsize=TICK_SIZE)

    ax = axes[1]
    x = np.arange(len(perf))
    ax.plot(perf["coef"], x, "o", color=BLUE, markersize=8,
            markeredgecolor=SURFACE, markeredgewidth=0.8, zorder=3)
    for i, (_, r) in enumerate(perf.iterrows()):
        ax.plot([r["ci_low"], r["ci_high"]], [i, i], color=BLUE, lw=1.8, zorder=2)
        ax.annotate(f"{r['coef']:+.3f}", (r["ci_high"], i), xytext=(8, 0),
                    textcoords="offset points", va="center", fontsize=ANNOT_SIZE, color=BLUE)
    ax.axvline(0, color=BASELINE, lw=1.0, zorder=1)
    ax.set_yticks(x)
    ax.set_yticklabels(["Base", "+ role", "+ role & draft"], fontsize=TICK_SIZE)
    ax.set_xlabel("Performance coefficient (log cap per SD)")
    ax.set_xlim(-0.06, 0.28)
    ax.set_ylim(-0.6, len(perf) - 0.2)
    ax.set_title("The performance gradient fades", loc="left", fontsize=10.5, color=INK, pad=8)
    ax.grid(axis="x", alpha=0.7)
    ax.tick_params(labelsize=TICK_SIZE)
    _figure_title(
        fig,
        "The cap pays for status; measured performance fades once role and draft enter.",
        "2025 OTC cap ledger; signed residual (not a positive-part sum); 95% CI; 909 players.",
    )
    return _save(fig, "net_rent.png")


def allocation_gap() -> Path:
    """Figure 5: performance minus role, by draft position."""
    players = pd.read_parquet(DISC / "allocation_gap.parquet")
    groups = pd.read_csv(DISC / "allocation_gap_groups.csv")
    tails = pd.read_csv(DISC / "allocation_gap_tails.csv")
    rel = players[players["sample"].eq("reliable_192")].copy()
    tail = rel[(rel["perf_t"].eq("high")) & (rel["role_t"].eq("low"))]
    opp = rel[(rel["perf_t"].eq("low")) & (rel["role_t"].eq("high"))]

    fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.4))
    ax = axes[0]
    ax.scatter(rel["perf_z"], rel["role_z"], s=14, c=GRAY, alpha=0.45,
               edgecolors=SURFACE, linewidths=0.3, zorder=1)
    ax.scatter(tail["perf_z"], tail["role_z"], s=32, c=ORANGE, alpha=0.95,
               edgecolors=SURFACE, linewidths=0.5, zorder=3,
               label=f"top performance / bottom role (n={len(tail)})")
    ax.scatter(opp["perf_z"], opp["role_z"], s=32, c=BLUE, alpha=0.9,
               edgecolors=SURFACE, linewidths=0.5, zorder=3,
               label=f"bottom performance / top role (n={len(opp)})")
    lim = (-2.6, 2.9)
    ax.plot(lim, lim, color=BASELINE, lw=1.0, ls="--", zorder=1)
    ax.set_xlim(lim)
    ax.set_ylim(lim)
    ax.set_xlabel("Performance (SD, within position and season)")
    ax.set_ylabel("Playing time (SD, within position and season)")
    ax.set_title("Above the line: performs more than he plays", loc="left",
                 fontsize=10.5, color=INK, pad=8)
    ax.legend(loc="upper left", fontsize=8.5, frameon=False)
    ax.grid(alpha=0.6)
    ax.tick_params(labelsize=TICK_SIZE)

    ax = axes[1]
    full = groups[groups["sample"].eq("full_233")].copy()
    relg = groups[groups["sample"].eq("reliable_192")].copy()
    order = ["Q1 late/UDFA", "Q2", "Q3", "Q4 early"]
    for label, frame, color, offset in [
        ("Full 233", full, GRAY, -0.12),
        ("Reliable 192", relg, ORANGE, 0.12),
    ]:
        frame = frame.set_index("draft_q").loc[order].reset_index()
        sub = players[players["sample"].eq("full_233" if label == "Full 233" else "reliable_192")]
        xs = np.arange(len(order)) + offset
        means = frame["mean_gap"].to_numpy()
        los, his = [], []
        for q in order:
            vals = sub.loc[sub["draft_q"].eq(q), "gap"]
            lo, hi = _boot_ci(vals)
            los.append(lo)
            his.append(hi)
        ax.errorbar(xs, means, yerr=[means - np.array(los), np.array(his) - means],
                    fmt="o", color=color, ecolor=color, elinewidth=1.2,
                    capsize=0, markersize=7, markeredgecolor=SURFACE,
                    markeredgewidth=0.7, label=label, zorder=3)
    ax.axhline(0, color=BASELINE, lw=1.0, zorder=1)
    ax.set_xticks(np.arange(len(order)))
    ax.set_xticklabels(["Q1\nlate/UDFA", "Q2", "Q3", "Q4\nearly"])
    ax.set_xlabel("Draft-capital quartile")
    ax.set_ylabel("Performance minus playing time (SD)")
    ax.set_title("Late picks outperform their role; early picks play above it", loc="left",
                 fontsize=10.5, color=INK, pad=8)
    ax.legend(loc="upper left", fontsize=8.5, frameon=False)
    ax.grid(axis="y", alpha=0.7)
    ax.tick_params(labelsize=TICK_SIZE)
    strict = tails[(tails["sample"].eq("reliable_192")) &
                   (tails["tail"].str.contains("quartile"))].iloc[0]
    _figure_title(
        fig,
        "The depth chart is not allocated to measured performance.",
        f"Top-quartile performance in the bottom role quartile: n={int(strict['n'])}; "
        f"next-season role {strict['next_role']:+.2f} SD; 95% bootstrap CI.",
    )
    return _save(fig, "allocation_gap.png")


def main() -> None:
    print(combine_by_position())
    print(net_rent())
    print(allocation_gap())


if __name__ == "__main__":
    main()
