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
    _cluster_boot_ci,
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
    ax.set_xlim(-0.22, 0.62)
    ax.set_ylim(-0.6, len(rows) - 0.2)
    ax.grid(axis="x", alpha=0.7)
    ax.tick_params(labelsize=TICK_SIZE)
    _figure_title(
        fig,
        "The Combine signal is concentrated in interior linemen, not universal.",
        "Standardized coefficient, 95% CI; DL is the only position group with a detectable link; interaction p=0.0004.",
    )
    return _save(fig, "combine_linkage.png")


def net_rent() -> Path:
    """Figure 2: the cap pays for performance; the 153-player fade is a rookie-scale subsample."""
    full = pd.read_csv(SAL / "pay_model_full.csv")
    nested = pd.read_csv(SAL / "pay_model_nested.csv")
    full = full[full["term"].eq("perf_z")].copy()
    full["model"] = pd.Categorical(full["model"], ["base_full", "role_full"], ordered=True)
    full = full.sort_values("model")
    perf = nested[nested["term"].eq("perf_z")].copy()
    perf["model"] = pd.Categorical(perf["model"], ["base", "role", "role_draft"], ordered=True)
    perf = perf.sort_values("model")

    fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.2))
    ax = axes[0]
    x = np.arange(len(full))
    ax.plot(full["coef"], x, "o", color=BLUE, markersize=8,
            markeredgecolor=SURFACE, markeredgewidth=0.8, zorder=3)
    for i, (_, r) in enumerate(full.iterrows()):
        ax.plot([r["ci_low"], r["ci_high"]], [i, i], color=BLUE, lw=1.8, zorder=2)
        ax.annotate(f"{r['coef']:+.3f}", (r["ci_high"], i), xytext=(8, 0),
                    textcoords="offset points", va="center", fontsize=ANNOT_SIZE, color=BLUE)
    ax.axvline(0, color=BASELINE, lw=1.0, zorder=1)
    ax.set_yticks(x)
    ax.set_yticklabels(["Base", "+ role"], fontsize=TICK_SIZE)
    ax.set_xlabel("Performance coefficient (log cap per SD)")
    ax.set_xlim(-0.02, 0.46)
    ax.set_ylim(-0.6, len(full) - 0.2)
    ax.set_title("Full 909-player ledger", loc="left", fontsize=10.5, color=INK, pad=8)
    ax.grid(axis="x", alpha=0.7)
    ax.tick_params(labelsize=TICK_SIZE)

    ax = axes[1]
    x = np.arange(len(perf))
    ax.plot(perf["coef"], x, "o", color=ORANGE, markersize=8,
            markeredgecolor=SURFACE, markeredgewidth=0.8, zorder=3)
    for i, (_, r) in enumerate(perf.iterrows()):
        ax.plot([r["ci_low"], r["ci_high"]], [i, i], color=ORANGE, lw=1.8, zorder=2)
        ax.annotate(f"{r['coef']:+.3f}", (r["ci_high"], i), xytext=(8, 0),
                    textcoords="offset points", va="center", fontsize=ANNOT_SIZE, color=ORANGE)
    ax.axvline(0, color=BASELINE, lw=1.0, zorder=1)
    ax.set_yticks(x)
    ax.set_yticklabels(["Base", "+ role", "+ role & draft"], fontsize=TICK_SIZE)
    ax.set_xlabel("Performance coefficient (log cap per SD)")
    ax.set_xlim(-0.06, 0.28)
    ax.set_ylim(-0.6, len(perf) - 0.2)
    ax.set_title("Draft-matched subsample (n=153)", loc="left", fontsize=10.5, color=INK, pad=8)
    ax.text(0.98, 0.04, "rookie-scale sensitivity,\nnot the headline", transform=ax.transAxes,
            ha="right", va="bottom", fontsize=8.5, color=SECONDARY)
    ax.grid(axis="x", alpha=0.7)
    ax.tick_params(labelsize=TICK_SIZE)
    _figure_title(
        fig,
        "The cap pays for performance; the 153-player fade is a rookie-scale subsample.",
        "2025 OTC cap ledger; team-clustered 95% CI; the full ledger is the headline.",
    )
    return _save(fig, "net_rent.png")


def allocation_gap() -> Path:
    """Figure 5: performance minus role, by draft position."""
    players = pd.read_parquet(DISC / "allocation_gap.parquet")
    groups = pd.read_csv(DISC / "allocation_gap_groups.csv")
    tails = pd.read_csv(DISC / "allocation_gap_tails.csv")
    rel = players[players["sample"].eq("reliable_192")].copy()
    tail = rel[(rel["perf_q"].eq("P4")) & (rel["role_q"].eq("R1"))]
    opp = rel[(rel["perf_q"].eq("P1")) & (rel["role_q"].eq("R4"))]

    fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.4))
    ax = axes[0]
    ax.scatter(rel["perf_z"], rel["role_z"], s=14, c=GRAY, alpha=0.45,
               edgecolors=SURFACE, linewidths=0.3, zorder=1)
    ax.scatter(tail["perf_z"], tail["role_z"], s=32, c=ORANGE, alpha=0.95,
               edgecolors=SURFACE, linewidths=0.5, zorder=3,
               label=f"top-quartile performance / bottom-quartile role (n={len(tail)})")
    ax.scatter(opp["perf_z"], opp["role_z"], s=32, c=BLUE, alpha=0.9,
               edgecolors=SURFACE, linewidths=0.5, zorder=3,
               label=f"bottom-quartile performance / top-quartile role (n={len(opp)})")
    lim = (-2.6, 2.9)
    ax.plot(lim, lim, color=BASELINE, lw=1.0, ls="--", zorder=1)
    ax.set_xlim(lim)
    ax.set_ylim(lim)
    ax.set_xlabel("Performance (SD, within position and season)")
    ax.set_ylabel("Playing time (SD, within position and season)")
    ax.set_title("Below the line: performance exceeds playing time", loc="left",
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
    current_role = float(tail["role_z"].mean())
    _figure_title(
        fig,
        "The allocation gap is descriptive: early picks play above performance; late picks perform above role.",
        f"Strict top-quartile performance / bottom-quartile role tail: n={int(strict['n'])}; "
        f"current role {current_role:+.2f} SD, next role {strict['next_role']:+.2f} SD "
        f"({strict['next_role'] - current_role:+.2f} recovery); 95% bootstrap CI.",
    )
    return _save(fig, "allocation_gap.png")


def pressure_signal() -> Path:
    """Figure 1: the tracking burst sees pressure; the stopwatch sees sacks."""
    d = pd.read_parquet(DISC / "interior_burst_players.parquet")
    i = d[(d["position_subgroup"] == "INTERIOR") & d["pressure_rate"].notna()].copy()
    i["third"] = pd.qcut(i["burst_z"], 3, labels=["Bottom", "Middle", "Top"])
    val = pd.read_csv(DISC / "interior_burst_validation.csv")
    oof = val[val["check"].eq("oof_r2")].copy()

    fig, axes = plt.subplots(1, 3, figsize=(11.0, 4.2))
    for ax, rate, title, color in [
        (axes[0], "pressure_rate", "Pressure rate (%)", BLUE),
        (axes[1], "sack_rate", "Sack rate (%)", ORANGE),
    ]:
        means, los, his = [], [], []
        for g in ["Bottom", "Middle", "Top"]:
            sub = i[i["third"] == g]
            means.append(sub[rate].mean())
            lo, hi = _cluster_boot_ci(sub, rate)
            los.append(lo)
            his.append(hi)
        x = np.arange(3)
        ax.bar(x, means, color=color, width=0.6, edgecolor=SURFACE, linewidth=1.5, zorder=2)
        ax.errorbar(
            x, means,
            yerr=[np.array(means) - np.array(los), np.array(his) - np.array(means)],
            fmt="none", ecolor=color, elinewidth=1.2, capsize=0, zorder=3,
        )
        for xi, m in zip(x, means):
            ax.annotate(f"{m:.2f}", (xi, m), xytext=(0, 5), textcoords="offset points",
                        ha="center", fontsize=ANNOT_SIZE, color=INK)
        ax.set_xticks(x)
        ax.set_xticklabels(["Bottom", "Middle", "Top"], fontsize=TICK_SIZE)
        ax.set_title(title, loc="left", fontsize=10.5, color=INK, pad=8)
        ax.set_ylabel("Per 100 snaps")
        ax.grid(axis="y", alpha=0.7)
        ax.tick_params(labelsize=TICK_SIZE)
    axes[0].set_ylim(0, 5.2)
    axes[1].set_ylim(0, 1.05)
    p_bottom = float(i.loc[i["third"] == "Bottom", "pressure_rate"].mean())
    p_top = float(i.loc[i["third"] == "Top", "pressure_rate"].mean())
    s_bottom = float(i.loc[i["third"] == "Bottom", "sack_rate"].mean())
    s_top = float(i.loc[i["third"] == "Top", "sack_rate"].mean())
    axes[0].text(0.02, 0.96, f"+{p_top - p_bottom:.1f} pp top-bottom", transform=axes[0].transAxes,
                 ha="left", va="top", fontsize=8.5, color=SECONDARY)
    axes[1].text(0.02, 0.96, f"{s_top / s_bottom:.1f}x top/bottom", transform=axes[1].transAxes,
                 ha="left", va="top", fontsize=8.5, color=SECONDARY)

    ax = axes[2]
    models = [("M_trad", GRAY, "Stopwatch"), ("M_burst", BLUE, "Burst"), ("M_both", AQUA, "Both")]
    width = 0.25
    for j, (model, color, label) in enumerate(models):
        vals = []
        for outcome in ["pressure_rate_z", "sack_rate_z"]:
            r = oof[(oof["outcome"] == outcome) & (oof["model"] == model)]
            vals.append(float(r["value"].iloc[0]) if len(r) else np.nan)
        ax.bar(np.arange(2) + (j - 1) * width, vals, width=width, color=color,
               label=label, edgecolor=SURFACE, linewidth=0.8, zorder=2)
    ax.axhline(0, color=BASELINE, lw=1.0, zorder=1)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Pressure", "Sacks"], fontsize=TICK_SIZE)
    ax.set_ylabel("Out-of-sample R2")
    ax.set_title("The stopwatch does not carry the pressure signal", loc="left", fontsize=10.5, color=INK, pad=8)
    ax.legend(loc="lower right", fontsize=8.5, frameon=False)
    ax.grid(axis="y", alpha=0.7)
    ax.tick_params(labelsize=TICK_SIZE)
    _figure_title(
        fig,
        "The stopwatch sees sacks, not pressure; the tracking burst sees pressure.",
        "Interior defensive line; burst terciles and GroupKFold-by-player out-of-sample R2; 95% bootstrap CI.",
    )
    return _save(fig, "pressure_signal.png")


def agentic_model() -> Path:
    """Figure 6: the performance-weight wedge and the role-allocation lever."""
    moments = pd.read_csv(DISC / "agentic_allocation_moments.csv")
    levers = pd.read_csv(DISC / "agentic_allocation_levers.csv")
    coach = moments[(moments["agent"].eq("coach")) & (moments["term"].eq("performance"))].iloc[0]
    gm = moments[(moments["agent"].eq("gm")) & (moments["term"].eq("performance"))].iloc[0]

    fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.3))
    ax = axes[0]
    for i, (label, row, color) in enumerate(
        [("Coach\n(role)", coach, ORANGE), ("GM\n(pay)", gm, BLUE)]
    ):
        ax.plot([row["ci_low"], row["ci_high"]], [i, i], color=color, lw=1.8, zorder=2)
        ax.plot(row["coef"], i, "o", color=color, markersize=8,
                markeredgecolor=SURFACE, markeredgewidth=0.8, zorder=3)
        ax.annotate(f"{row['coef']:+.3f}", (row["ci_high"], i), xytext=(8, 0),
                    textcoords="offset points", va="center", fontsize=ANNOT_SIZE, color=color)
    ax.axvline(0, color=BASELINE, lw=1.0, zorder=1)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["Coach\n(role)", "GM\n(pay)"], fontsize=TICK_SIZE)
    ax.set_xlabel("Performance weight (per SD)")
    ax.set_xlim(-0.32, 0.26)
    ax.set_ylim(-0.6, 1.6)
    ax.set_title("The performance-weight wedge", loc="left", fontsize=10.5, color=INK, pad=8)
    ax.grid(axis="x", alpha=0.7)
    ax.tick_params(labelsize=TICK_SIZE)

    ax = axes[1]
    ax.plot(levers["value"], levers["top_perf_role"], color=BLUE, lw=2.0,
            marker="o", markersize=4, label="Top-performance role")
    ax.plot(levers["value"], levers["strict_tail_gain"], color=ORANGE, lw=2.0,
            marker="o", markersize=4, label="Strict-tail gain")
    ax.axvline(float(coach["coef"]), color=GRAY, lw=1.0, ls="--", zorder=1)
    ax.axvline(float(gm["coef"]), color=GRAY, lw=1.0, ls=":", zorder=1)
    ax.annotate("observed", (float(coach["coef"]), 0.30), xytext=(4, 0),
                textcoords="offset points", fontsize=8.5, color=SECONDARY)
    ax.annotate("cap-aligned", (float(gm["coef"]), 0.30), xytext=(-4, 0),
                textcoords="offset points", ha="right", fontsize=8.5, color=SECONDARY)
    ax.axhline(0, color=BASELINE, lw=1.0, zorder=1)
    ax.set_xlabel("Coach performance weight")
    ax.set_ylabel("Role (SD)")
    ax.set_title("The lever: align the weights", loc="left", fontsize=10.5, color=INK, pad=8)
    ax.legend(loc="lower right", fontsize=8.5, frameon=False)
    ax.grid(axis="y", alpha=0.7)
    ax.tick_params(labelsize=TICK_SIZE)
    _figure_title(
        fig,
        "The cap and the depth chart weight performance differently.",
        "Two-agent model calibrated to the observed role and pay equations; model-reproduced, not identified; the coach weight is marginal.",
    )
    return _save(fig, "agentic_allocation.png")


def main() -> None:
    print(combine_by_position())
    print(net_rent())
    print(allocation_gap())
    print(agentic_model())


if __name__ == "__main__":
    main()
