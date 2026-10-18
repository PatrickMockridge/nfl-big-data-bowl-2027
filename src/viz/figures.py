"""Publication figures for the role-allocation discovery.

Palette: validated default categorical slots 1-3 (blue, orange, aqua), light
surface, hairline chrome. No dual axes; small multiples where scales differ.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

ROOT = Path(__file__).resolve().parents[2]
DISC = ROOT / "outputs" / "discovery"
FIG = ROOT / "outputs" / "figures"
RNG = np.random.default_rng(42)

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
        "font.size": 9,
        "axes.edgecolor": BASELINE,
        "axes.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "xtick.color": GRAY,
        "ytick.color": GRAY,
        "text.color": INK,
        "axes.labelcolor": SECONDARY,
        "grid.color": GRID,
        "grid.linewidth": 0.6,
        "grid.linestyle": "-",
        "legend.frameon": False,
        "figure.dpi": 150,
    }
)


def _save(fig, name: str) -> Path:
    FIG.mkdir(parents=True, exist_ok=True)
    path = FIG / name
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    return path


def _boot_ci(values: pd.Series, n: int = 3000) -> tuple[float, float]:
    values = values.dropna().to_numpy()
    if len(values) < 3:
        return (np.nan, np.nan)
    draws = [RNG.choice(values, len(values), True).mean() for _ in range(n)]
    return tuple(np.percentile(draws, [2.5, 97.5]))


def role_gap_scatter() -> Path:
    d = pd.read_parquet(DISC / "role_allocation_player_seasons.parquet")
    d = d[d["role_gap"].notna()].copy()
    fig, ax = plt.subplots(figsize=(8.2, 6.0))
    normal = d[d["allocation"] == "normal"]
    under = d[d["allocation"] == "underused"]
    over = d[d["allocation"] == "overused"]
    ax.scatter(normal["perf_z"], normal["role_gap"], s=14, c=GRAY, alpha=0.35,
               edgecolors=SURFACE, linewidths=0.4, label="normal")
    ax.scatter(under["perf_z"], under["role_gap"], s=42, c=BLUE,
               edgecolors=SURFACE, linewidths=0.6, label="underused (high performance, low role)")
    ax.scatter(over["perf_z"], over["role_gap"], s=42, c=ORANGE,
               edgecolors=SURFACE, linewidths=0.6, label="overused (low performance, high role)")
    ax.axhline(0, color=BASELINE, lw=0.9)
    ax.axvline(0, color=BASELINE, lw=0.9)
    ax.grid(axis="both", alpha=0.7)
    # Selective direct labels: the most extreme examples, one per player.
    seen = set()
    for _, row in under.nlargest(5, "perf_z").iterrows():
        if row["display_name"] in seen:
            continue
        seen.add(row["display_name"])
        ax.annotate(row["display_name"], (row["perf_z"], row["role_gap"]),
                    xytext=(5, -9), textcoords="offset points", fontsize=7, color=BLUE)
    seen = set()
    for _, row in over.nsmallest(5, "perf_z").iterrows():
        if row["display_name"] in seen:
            continue
        seen.add(row["display_name"])
        ax.annotate(row["display_name"], (row["perf_z"], row["role_gap"]),
                    xytext=(5, 7), textcoords="offset points", fontsize=7, color=ORANGE)
    ax.text(0.98, 0.03, "underused", transform=ax.transAxes, ha="right", va="bottom",
            fontsize=8, color=BLUE, alpha=0.8)
    ax.text(0.02, 0.97, "overused", transform=ax.transAxes, ha="left", va="top",
            fontsize=8, color=ORANGE, alpha=0.8)
    ax.set_xlabel("Performance residual (position-standardized; higher = better)")
    ax.set_ylabel("Role gap (playing time unexplained by performance/draft)")
    ax.set_title("The depth chart does not follow performance", loc="left", fontsize=12, color=INK)
    ax.legend(loc="upper right", fontsize=7.5, markerscale=1.2)
    return _save(fig, "role_gap_scatter.png")


def next_role_forest() -> Path:
    pos = pd.read_csv(DISC / "role_allocation_positions.csv")
    order = ["DL", "WR", "OL", "DB", "TE"]
    pos = pos.set_index("position_group").loc[[p for p in order if p in pos["position_group"].values]].reset_index()
    fig, ax = plt.subplots(figsize=(8.4, 5.0))
    y = np.arange(len(pos))
    specs = [
        ("role", "Current role", BLUE, -0.20),
        ("perf", "Performance", ORANGE, 0.0),
        ("draft", "Draft capital", AQUA, 0.20),
    ]
    for key, label, color, offset in specs:
        coef = pos[f"{key}_coef"]
        lo = pos[f"{key}_ci_low"]
        hi = pos[f"{key}_ci_high"]
        mask = coef.notna() & lo.notna() & hi.notna()
        ax.errorbar(coef[mask], (y + offset)[mask],
                    xerr=[(coef - lo)[mask], (hi - coef)[mask]], fmt="o",
                    color=color, ecolor=color, elinewidth=1.2, capsize=0,
                    markersize=6, markeredgecolor=SURFACE, markeredgewidth=0.6,
                    label=label)
        if key == "perf":
            for idx in pos.index[~mask]:
                ax.text(0.02, y[idx] + offset, "unidentifiable", fontsize=6.5,
                        color=GRAY, va="center")
    ax.axvline(0, color=BASELINE, lw=0.9)
    ax.set_yticks(y)
    ax.set_yticklabels(pos["position_group"])
    ax.invert_yaxis()
    ax.grid(axis="x", alpha=0.7)
    ax.set_xlabel("Coefficient for next-season role (z; 95% CI)")
    ax.set_title("Role persists and follows draft capital — not performance",
                 loc="left", fontsize=12, color=INK)
    ax.legend(loc="lower right", fontsize=8)
    return _save(fig, "next_role_forest.png")


def career_divergence() -> Path:
    d = pd.read_parquet(DISC / "role_allocation_player_seasons.parquet")
    metrics = [
        ("next_role", "Next-season role (z)", "Next role"),
        ("career_start_rate", "Career start rate", "Starts / games"),
        ("career_status_z", "Career status (z)", "Career status"),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(9.6, 3.6), sharey=False)
    for ax, (col, ylabel, title) in zip(axes, metrics):
        rows = []
        for group, color in [("underused", BLUE), ("overused", ORANGE)]:
            values = d.loc[d["allocation"] == group, col]
            mean = values.mean()
            lo, hi = _boot_ci(values)
            rows.append((group, mean, lo, hi, color))
        for i, (group, mean, lo, hi, color) in enumerate(rows):
            ax.errorbar(i, mean, yerr=[[mean - lo], [hi - mean]], fmt="o",
                        color=color, ecolor=color, elinewidth=1.3, capsize=0,
                        markersize=7, markeredgecolor=SURFACE, markeredgewidth=0.6)
            offset = (10, 0) if i == 0 else (-10, 0)
            ha = "left" if i == 0 else "right"
            ax.annotate(f"{mean:.2f}", (i, mean), xytext=offset,
                        textcoords="offset points", ha=ha, va="center",
                        fontsize=8, color=color)
        ax.set_xticks([0, 1])
        ax.set_xticklabels(["underused", "overused"], fontsize=8)
        ax.set_ylabel(ylabel)
        ax.set_title(title, loc="left", fontsize=10, color=INK)
        ax.grid(axis="y", alpha=0.7)
    fig.suptitle("Overused low performers out-earn underused high performers",
                 x=0.01, ha="left", fontsize=12, color=INK)
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    return _save(fig, "career_divergence.png")


def persistence() -> Path:
    coef = pd.read_csv(DISC / "role_allocation_coefficients.csv")
    horizons = [("next_role_full", "t + 1"), ("next2_role_full", "t + 2")]
    fig, ax = plt.subplots(figsize=(7.6, 3.8))
    terms = [("role_z", "Current role", BLUE), ("perf_z", "Performance", ORANGE),
             ("B_draft", "Draft capital", AQUA)]
    for i, (model, label) in enumerate(horizons):
        sub = coef[coef["model"] == model]
        for j, (term, term_label, color) in enumerate(terms):
            row = sub[sub["term"] == term]
            if len(row) == 0:
                continue
            row = row.iloc[0]
            y = i + (j - 1) * 0.18
            ax.errorbar(row["coef"], y, xerr=[[row["coef"] - row["ci_low"]],
                                              [row["ci_high"] - row["coef"]]],
                        fmt="o", color=color, ecolor=color, elinewidth=1.2,
                        capsize=0, markersize=6, markeredgecolor=SURFACE,
                        markeredgewidth=0.6, label=term_label if i == 0 else None)
    ax.axvline(0, color=BASELINE, lw=0.9)
    ax.set_yticks([0, 1])
    ax.set_yticklabels([h[1] for h in horizons])
    ax.set_xlabel("Coefficient for next role (z; 95% CI)")
    ax.set_title("Even after two seasons, performance does not buy role",
                 loc="left", fontsize=12, color=INK)
    ax.grid(axis="x", alpha=0.7)
    ax.legend(loc="lower right", fontsize=8)
    return _save(fig, "persistence.png")


def symptom_heatmap() -> Path:
    out = pd.read_csv(DISC / "price_prediction.csv")
    axes_order = [("market", "Market price"), ("team", "Team role"),
                  ("performance", "Performance"), ("career", "Career")]
    pivot = out.pivot_table(index="feature", columns="price_type", values="delta_r2", aggfunc="first")
    pivot = pivot.reindex(columns=[a for a, _ in axes_order])
    pivot = pivot.loc[pivot.abs().max(axis=1).sort_values(ascending=False).index]
    data = pivot.to_numpy(dtype=float)
    vmax = max(abs(np.nanmax(data)), abs(np.nanmin(data)), 0.05)
    cmap = LinearSegmentedColormap.from_list(
        "blue_gray_red", ["#184f95", "#f0efec", "#e34948"]
    )
    fig, ax = plt.subplots(figsize=(8.6, 5.6))
    im = ax.imshow(data, cmap=cmap, vmin=-vmax, vmax=vmax, aspect="auto")
    ax.set_xticks(range(len(axes_order)))
    ax.set_xticklabels([label for _, label in axes_order], fontsize=8)
    ax.set_yticks(range(len(pivot)))
    ax.set_yticklabels(pivot.index, fontsize=8)
    ax.tick_params(length=0)
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            value = data[i, j]
            if np.isnan(value):
                ax.text(j, i, "—", ha="center", va="center", fontsize=8, color=GRAY)
            else:
                ax.text(j, i, f"{value:+.3f}", ha="center", va="center", fontsize=7,
                        color=INK if abs(value) < vmax * 0.55 else "white")
    ax.set_title("Almost every lens is absorbed or undetectable; role allocation is the residual",
                 loc="left", fontsize=11, color=INK)
    cbar = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.02)
    cbar.set_label("Incremental out-of-sample ΔR²", fontsize=8, color=SECONDARY)
    cbar.ax.tick_params(labelsize=7, colors=GRAY)
    return _save(fig, "symptom_heatmap.png")


def case_studies() -> Path:
    d = pd.read_parquet(DISC / "role_allocation_player_seasons.parquet")
    d = d[d["role_gap"].notna()].copy()
    picks = []
    for group in ["underused", "overused"]:
        sub = d[d["allocation"] == group].groupby("nfl_id").size()
        ids = sub[sub >= 2].index
        picks.extend(list(ids[:2] if group == "overused" else ids[:1]))
    fig, axes = plt.subplots(1, 3, figsize=(10.2, 3.6), sharey=True)
    for ax, nfl_id in zip(axes, picks):
        sub = d[d["nfl_id"] == nfl_id].sort_values("season")
        name = sub["display_name"].iloc[0]
        group = sub["allocation"].iloc[0]
        ax.plot(sub["season"], sub["role_z"], marker="o", color=BLUE, lw=2,
                ms=5, label="role (z)")
        ax.plot(sub["season"], sub["perf_z"], marker="o", color=ORANGE, lw=2,
                ms=5, label="performance (z)")
        ax.axhline(0, color=BASELINE, lw=0.8)
        ax.set_title(f"{name} — {group}", loc="left", fontsize=9, color=INK)
        ax.set_xticks(sorted(sub["season"].unique()))
        ax.grid(axis="y", alpha=0.7)
    axes[0].set_ylabel("Standardized")
    axes[0].legend(loc="best", fontsize=7)
    fig.suptitle("Same performance, different depth chart", x=0.01, ha="left",
                 fontsize=12, color=INK)
    fig.tight_layout(rect=[0, 0, 1, 0.90])
    return _save(fig, "case_studies.png")


def predictability_premium() -> Path:
    players = pd.read_parquet(DISC / "rent_players.parquet")
    groups = pd.read_csv(DISC / "predictability_groups.csv")
    fig, axes = plt.subplots(1, 2, figsize=(9.8, 4.2))
    ax = axes[0]
    for label, color in [("low volatility", BLUE), ("high volatility", ORANGE)]:
        sub = players[players["vol_group"] == label]
        ax.scatter(sub["volatility"], sub["role"], s=18, c=color, alpha=0.55,
                   edgecolors=SURFACE, linewidths=0.3, label=label)
    # Regression line.
    x = players["volatility"].to_numpy()
    y = players["role"].to_numpy()
    coef = np.polyfit(x, y, 1)
    xs = np.linspace(np.nanmin(x), np.nanmax(x), 50)
    ax.plot(xs, np.polyval(coef, xs), color=GRAY, lw=1.2)
    ax.axhline(0, color=BASELINE, lw=0.8)
    ax.set_xlabel("Within-season performance volatility (weekly SD)")
    ax.set_ylabel("Role (z)")
    ax.set_title("Low volatility buys role", loc="left", fontsize=10, color=INK)
    ax.grid(alpha=0.7)
    ax.legend(loc="upper right", fontsize=7.5)
    ax = axes[1]
    order = ["DL", "WR", "OL", "DB", "TE"]
    offsets = {"low volatility": -0.12, "high volatility": 0.12}
    for label, color in [("low volatility", BLUE), ("high volatility", ORANGE)]:
        sub = groups[groups["vol_group"] == label].set_index("position")
        ys = [order.index(p) for p in order if p in sub.index]
        vals = [sub.loc[p, "career_status"] for p in order if p in sub.index]
        ax.scatter(vals, [yy + offsets[label] for yy in ys], s=28, c=color,
                   edgecolors=SURFACE, linewidths=0.4, label=label)
    ax.axvline(0, color=BASELINE, lw=0.8)
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels(order)
    ax.invert_yaxis()
    ax.set_xlabel("Career status (z)")
    ax.set_title("The premium is career-wide", loc="left", fontsize=10, color=INK)
    ax.grid(axis="x", alpha=0.7)
    ax.legend(loc="lower right", fontsize=7.5)
    fig.suptitle("The predictability premium: teams favor known failure over volatile upside",
                 x=0.01, ha="left", fontsize=12, color=INK)
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    return _save(fig, "predictability_premium.png")


def rent_figure() -> Path:
    players = pd.read_parquet(DISC / "rent_players.parquet")
    fig, axes = plt.subplots(1, 2, figsize=(9.4, 4.0))
    specs = [
        ("role", "Role (z)", "Career rewards follow role"),
        ("perf", "Performance (z)", "Not performance"),
    ]
    for ax, (col, xlabel, title) in zip(axes, specs):
        for label, color in [("low volatility", BLUE), ("high volatility", ORANGE)]:
            sub = players[players["vol_group"] == label]
            ax.scatter(sub[col], sub["rent_career_status"], s=16, c=color,
                       alpha=0.55, edgecolors=SURFACE, linewidths=0.3, label=label)
        x = players[col].to_numpy()
        y = players["rent_career_status"].to_numpy()
        coef = np.polyfit(x, y, 1)
        xs = np.linspace(np.nanmin(x), np.nanmax(x), 50)
        ax.plot(xs, np.polyval(coef, xs), color=GRAY, lw=1.2)
        ax.axhline(0, color=BASELINE, lw=0.8)
        ax.axvline(0, color=BASELINE, lw=0.8)
        ax.set_xlabel(xlabel)
        ax.set_ylabel("Career-status rent (residual)")
        ax.set_title(title, loc="left", fontsize=10, color=INK)
        ax.grid(alpha=0.7)
    axes[0].legend(loc="upper left", fontsize=7.5)
    fig.suptitle("The star premium is a role rent, not a performance reward",
                 x=0.01, ha="left", fontsize=12, color=INK)
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    return _save(fig, "rent_figure.png")


def combine_linkage_figure() -> Path:
    df = pd.read_csv(DISC / "combine_linkage.csv")
    df = df.iloc[::-1].reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(8.2, 3.8))
    labels = []
    for i, row in df.iterrows():
        positive = row["ci_low"] > 0
        color = BLUE if positive else ORANGE
        ax.errorbar(row["coef"], i, xerr=[[row["coef"] - row["ci_low"]],
                                          [row["ci_high"] - row["coef"]]],
                    fmt="o", color=color, ecolor=color, elinewidth=1.3,
                    capsize=0, markersize=7, markeredgecolor=SURFACE,
                    markeredgewidth=0.5)
        labels.append(row["outcome"])
        ax.annotate(f"n={int(row['n'])}", (row["ci_high"], i), xytext=(6, 0),
                    textcoords="offset points", va="center", fontsize=7, color=GRAY)
    ax.axvline(0, color=BASELINE, lw=0.9)
    ax.set_yticks(range(len(df)))
    ax.set_yticklabels(labels)
    ax.set_xlabel("Coefficient per SD of Combine movement (95% CI)")
    ax.set_title("Combine movement predicts performance — but not role",
                 loc="left", fontsize=12, color=INK)
    ax.grid(axis="x", alpha=0.7)
    return _save(fig, "combine_linkage.png")


def within_player_figure() -> Path:
    d = pd.read_parquet(DISC / "role_within_player.parquet")
    coef = np.polyfit(d["d_perf"], d["d_role"], 1)
    fig, ax = plt.subplots(figsize=(6.6, 4.2))
    ax.scatter(d["d_perf"], d["d_role"], s=20, c=GRAY, alpha=0.55,
               edgecolors=SURFACE, linewidths=0.3)
    xs = np.linspace(d["d_perf"].min(), d["d_perf"].max(), 50)
    ax.plot(xs, np.polyval(coef, xs), color=ORANGE, lw=1.5)
    ax.axhline(0, color=BASELINE, lw=0.8)
    ax.axvline(0, color=BASELINE, lw=0.8)
    ax.set_xlabel("Change in performance (z)")
    ax.set_ylabel("Change in role (z)")
    ax.set_title("When performance changes, role does not", loc="left",
                 fontsize=12, color=INK)
    ax.annotate(f"slope {coef[0]:+.3f} (n={len(d)})", (0.02, 0.95),
                xycoords="axes fraction", fontsize=8, color=SECONDARY)
    ax.grid(alpha=0.7)
    return _save(fig, "within_player_change.png")


def role_persistence_figure() -> Path:
    d = pd.read_parquet(DISC / "role_allocation_player_seasons.parquet")
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 4.0), sharey=True)
    specs = [("role_z", "Current role (z)"), ("perf_z", "Performance (z)")]
    for ax, (col, label) in zip(axes, specs):
        ax.scatter(d[col], d["next_role"], s=16, c=GRAY, alpha=0.45,
                   edgecolors=SURFACE, linewidths=0.3)
        coef = np.polyfit(d[col], d["next_role"], 1)
        xs = np.linspace(d[col].min(), d[col].max(), 50)
        ax.plot(xs, np.polyval(coef, xs), color=BLUE if col == "role_z" else ORANGE, lw=1.5)
        ax.axhline(0, color=BASELINE, lw=0.8)
        ax.set_xlabel(label)
        ax.set_title(f"{label.split(' (')[0]} → next role", loc="left", fontsize=10)
        ax.annotate(f"slope {coef[0]:+.2f}", (0.04, 0.92), xycoords="axes fraction",
                    fontsize=8, color=SECONDARY)
        ax.grid(alpha=0.7)
    axes[0].set_ylabel("Next-season role (z)")
    fig.suptitle("Role persists; performance does not", x=0.01, ha="left",
                 fontsize=12, color=INK)
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    return _save(fig, "role_persistence.png")


def role_sensitivity_figure() -> Path:
    coef = pd.read_csv(DISC / "role_allocation_coefficients.csv")
    models = [
        ("next_role_full", "role_z", "Raw snaps"),
        ("next_role_pass-play_role", "role_pass_z", "Pass-play role"),
        ("next_role_cohort_role_share", "role_share_z", "Cohort role share"),
        ("next_role_team_control", "role_z", "Team control"),
    ]
    fig, ax = plt.subplots(figsize=(8.4, 4.0))
    y = np.arange(len(models))
    series = [
        ("role", "Role measure", BLUE),
        ("perf_z", "Performance", ORANGE),
        ("B_draft", "Draft capital", AQUA),
    ]
    for key, label, color in series:
        values = []
        lows = []
        highs = []
        for model, role_term, _ in models:
            term = role_term if key == "role" else key
            row = coef[(coef["model"] == model) & (coef["term"] == term)]
            if len(row):
                values.append(row.iloc[0]["coef"])
                lows.append(row.iloc[0]["ci_low"])
                highs.append(row.iloc[0]["ci_high"])
            else:
                values.append(np.nan); lows.append(np.nan); highs.append(np.nan)
        values = np.array(values); lows = np.array(lows); highs = np.array(highs)
        mask = ~np.isnan(values)
        ax.errorbar(values[mask], y[mask] + (list(series).index((key, label, color)) - 1) * 0.18,
                    xerr=[values[mask] - lows[mask], highs[mask] - values[mask]],
                    fmt="o", color=color, ecolor=color, elinewidth=1.2, capsize=0,
                    markersize=6, markeredgecolor=SURFACE, markeredgewidth=0.5,
                    label=label)
    ax.axvline(0, color=BASELINE, lw=0.9)
    ax.set_yticks(y)
    ax.set_yticklabels([m[2] for m in models])
    ax.invert_yaxis()
    ax.set_xlabel("Coefficient for next-season role (z; 95% CI)")
    ax.set_title("The performance null survives role-measure choices", loc="left",
                 fontsize=12, color=INK)
    ax.grid(axis="x", alpha=0.7)
    ax.legend(loc="lower right", fontsize=8)
    return _save(fig, "role_sensitivity.png")


def role_gap_tails() -> Path:
    d = pd.read_parquet(DISC / "role_allocation_player_seasons.parquet")
    d = d[d["allocation"].isin(["high role / low performance",
                                "low role / high performance"])]
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    colors = {"high role / low performance": ORANGE, "low role / high performance": BLUE}
    for label, sub in d.groupby("allocation"):
        ax.scatter(sub["perf_z"], sub["role_gap"], s=38, c=colors[label],
                   edgecolors=SURFACE, linewidths=0.5, label=label)
    ax.axhline(0, color=BASELINE, lw=0.8)
    ax.axvline(0, color=BASELINE, lw=0.8)
    ax.set_xlabel("Performance (z)")
    ax.set_ylabel("Role gap")
    ax.set_title("Role is not allocated to measured performance", loc="left",
                 fontsize=12, color=INK)
    ax.grid(alpha=0.7)
    ax.legend(loc="lower right", fontsize=7.5)
    return _save(fig, "role_gap_tails.png")


def main() -> None:
    paths = [
        combine_linkage_figure(),
        next_role_forest(),
        role_persistence_figure(),
        within_player_figure(),
        role_sensitivity_figure(),
        role_gap_tails(),
    ]
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()
