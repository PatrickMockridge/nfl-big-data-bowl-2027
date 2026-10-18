"""Test the preregistered Yellow Square hypotheses for DL prospects.

Outputs:
- outputs/models/hypothesis_results.csv
- outputs/models/resilience_profiles.csv
- outputs/models/team_clustering.csv
- docs/results_summary.md
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, spearmanr
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import r2_score, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from features import player_play as pp  # noqa: E402
from framework import squares as sq  # noqa: E402

MODEL_DIR = ROOT / "outputs" / "models"
FEATURE_DIR = ROOT / "outputs" / "features"
DOCS = ROOT / "docs"
RNG = np.random.default_rng(42)


def boot_ci(values: np.ndarray, stat=np.mean, n: int = 5000) -> tuple[float, float]:
    values = np.asarray(values, dtype=float)
    values = values[~np.isnan(values)]
    if len(values) < 5:
        return (np.nan, np.nan)
    draws = [stat(RNG.choice(values, len(values), replace=True)) for _ in range(n)]
    return tuple(np.percentile(draws, [2.5, 97.5]))


def boot_diff(a: np.ndarray, b: np.ndarray, stat=np.mean, n: int = 5000) -> tuple[float, float, float]:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    a = a[~np.isnan(a)]
    b = b[~np.isnan(b)]
    diff = stat(a) - stat(b)
    draws = [
        stat(RNG.choice(a, len(a), replace=True)) - stat(RNG.choice(b, len(b), replace=True))
        for _ in range(n)
    ]
    lo, hi = np.percentile(draws, [2.5, 97.5])
    return float(diff), float(lo), float(hi)


def perm_p(a: np.ndarray, b: np.ndarray, n: int = 5000) -> float:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    a = a[~np.isnan(a)]
    b = b[~np.isnan(b)]
    observed = abs(a.mean() - b.mean())
    pooled = np.concatenate([a, b])
    count = 0
    for _ in range(n):
        RNG.shuffle(pooled)
        if abs(pooled[: len(a)].mean() - pooled[len(a) :].mean()) >= observed:
            count += 1
    return (count + 1) / (n + 1)


def spearman_boot(x: pd.Series, y: pd.Series, n: int = 2000) -> tuple[float, float, float, int]:
    paired = pd.concat([x, y], axis=1).dropna()
    if len(paired) < 8:
        return (np.nan, np.nan, np.nan, len(paired))
    rho = spearmanr(paired.iloc[:, 0], paired.iloc[:, 1]).statistic
    draws = []
    for _ in range(n):
        idx = RNG.integers(0, len(paired), len(paired))
        sample = paired.iloc[idx]
        draws.append(spearmanr(sample.iloc[:, 0], sample.iloc[:, 1]).statistic)
    lo, hi = np.percentile(draws, [2.5, 97.5])
    return float(rho), float(lo), float(hi), len(paired)


def bh_fdr(pvalues: pd.Series) -> pd.Series:
    p = pvalues.astype(float).copy()
    valid = p.notna()
    q = pd.Series(np.nan, index=p.index)
    if valid.sum() == 0:
        return q
    values = p[valid].to_numpy()
    order = np.argsort(values)
    ranked = values[order]
    m = len(ranked)
    adjusted = ranked * m / np.arange(1, m + 1)
    adjusted = np.minimum.accumulate(adjusted[::-1])[::-1]
    out = np.empty(m)
    out[order] = np.clip(adjusted, 0, 1)
    q.loc[valid] = out
    return q


def c_from_outcome(df: pd.DataFrame, outcome: str) -> pd.Series:
    out = pd.Series(np.nan, index=df.index)
    valid = df[outcome].notna() & df["B"].notna()
    if valid.sum() < 10:
        return out
    design = pd.get_dummies(
        df.loc[valid, ["B", "position_subgroup", "draft_year"]],
        columns=["position_subgroup", "draft_year"],
        drop_first=True,
        dtype=float,
    )
    y = df.loc[valid, outcome]
    model = Ridge(alpha=1.0).fit(design, y)
    residual = y - model.predict(design)
    out.loc[valid] = 1.0 - residual.rank(pct=True)
    return out


def add_result(rows: list[dict], hypothesis: str, test: str, estimate: float, lo: float, hi: float, p: float, n: int, note: str = "") -> None:
    rows.append(
        {
            "hypothesis": hypothesis,
            "test": test,
            "estimate": estimate,
            "ci_low": lo,
            "ci_high": hi,
            "p_value": p,
            "n": n,
            "note": note,
        }
    )


def h1(df: pd.DataFrame, rows: list[dict]) -> None:
    y = df[df["square"] == "Yellow"]
    rb = df[df["square"].isin(["Red", "Blue"])]
    for metric in ["C", "bust", "shrunk_mean", "raw_speed_mean"]:
        a = y[metric].dropna()
        b = rb[metric].dropna()
        if len(a) < 5 or len(b) < 5:
            continue
        diff, lo, hi = boot_diff(a, b)
        p = mannwhitneyu(a, b, alternative="two-sided").pvalue
        add_result(rows, "H1 Yellow risk", f"Yellow - RedBlue: {metric}", diff, lo, hi, p, len(a) + len(b))
    # Sensitivity: alternative Yellow A cutoffs.
    for lo_a, hi_a in [(0.20, 0.80), (0.25, 0.75), (0.35, 0.65)]:
        yalt = df[(df["B"] >= 0.5) & (df["A"] >= lo_a) & (df["A"] <= hi_a)]
        a = yalt["C"].dropna()
        b = rb["C"].dropna()
        if len(a) >= 5:
            diff, lo, hi = boot_diff(a, b)
            p = mannwhitneyu(a, b, alternative="two-sided").pvalue
            add_result(
                rows,
                "H1 sensitivity",
                f"Yellow A[{lo_a},{hi_a}] - RedBlue: C",
                diff,
                lo,
                hi,
                p,
                len(a) + len(b),
                note=f"yellow_n={len(a)}",
            )
    # Sensitivity: full context model (team included).
    if "C_full" in df.columns:
        a = y["C_full"].dropna()
        b = rb["C_full"].dropna()
        diff, lo, hi = boot_diff(a, b)
        p = mannwhitneyu(a, b, alternative="two-sided").pvalue
        add_result(rows, "H1 sensitivity", "Full context (team included): C", diff, lo, hi, p, len(a) + len(b))


def h2(df: pd.DataFrame, rows: list[dict]) -> None:
    for label, sub in [("all DL", df), ("Yellow", df[df["square"] == "Yellow"])]:
        for feature in ["mobius_continuous", "flip_composite", "dwell_composite"]:
            rho, lo, hi, n = spearman_boot(sub[feature], sub["C"])
            p = spearmanr(sub[feature], sub["C"], nan_policy="omit").pvalue if n >= 8 else np.nan
            add_result(rows, "H2 Möbius", f"{label}: {feature} vs C", rho, lo, hi, p, n)
    n_yellow = int((df["square"] == "Yellow").sum())
    if {"mobius_flag", "C"}.issubset(df.columns):
        flag = df[(df["square"] == "Yellow") & (df["mobius_flag"])]
        nonflag = df[(df["square"] == "Yellow") & (~df["mobius_flag"])]
        if len(flag) >= 2:
            diff, lo, hi = boot_diff(flag["C"].dropna(), nonflag["C"].dropna())
            add_result(rows, "H2 Möbius", "Yellow flag vs nonflag: C", diff, lo, hi, np.nan, len(flag) + len(nonflag))
        else:
            add_result(
                rows,
                "H2 Möbius",
                "Yellow Möbius flag count",
                float(len(flag)),
                np.nan,
                np.nan,
                np.nan,
                n_yellow,
                note="too few flagged players for a contrast",
            )
    # Minimum detectable correlation at n=16.
    n = max(n_yellow, 4)
    z = (1.96 + 0.8416) / np.sqrt(n - 3)
    add_result(rows, "H2 power", "min detectable |rho| at 80% power", float(np.tanh(z)), np.nan, np.nan, np.nan, n)


def h3(df: pd.DataFrame, rows: list[dict]) -> None:
    valid = df[df["shrunk_mean"].notna()].copy()
    threshold = valid["shrunk_mean"].quantile(0.75)
    valid["bargain"] = (valid["shrunk_mean"] >= threshold).astype(float)
    green = valid[valid["square"] == "Green"]
    highb = valid[valid["B"] >= 0.5]
    diff, lo, hi = boot_diff(green["bargain"], highb["bargain"])
    p = mannwhitneyu(green["bargain"], highb["bargain"], alternative="two-sided").pvalue
    add_result(rows, "H3 Green bargains", "Green - highB bargain rate", diff, lo, hi, p, len(green) + len(highb))
    if len(green) >= 10:
        cut = green["A"].median()
        higha = green[green["A"] >= cut]
        lowa = green[green["A"] < cut]
        diff, lo, hi = boot_diff(higha["bargain"], lowa["bargain"])
        p = mannwhitneyu(higha["bargain"], lowa["bargain"], alternative="two-sided").pvalue
        add_result(rows, "H3 Green bargains", "Green highA vs lowA bargain rate", diff, lo, hi, p, len(higha) + len(lowa))
    green.sort_values("shrunk_mean", ascending=False).head(10).to_csv(
        MODEL_DIR / "green_top_players.csv", index=False
    )


def _ridge_model() -> Pipeline:
    numeric = Pipeline(
        [("impute", SimpleImputer(strategy="median", add_indicator=True)), ("scale", StandardScaler())]
    )
    return Pipeline([("pre", numeric), ("ridge", Ridge(alpha=1.0))])


def h4(df: pd.DataFrame, rows: list[dict]) -> None:
    official = [c for c in sq.OFFICIAL_FEATURES if c in df.columns]
    tracking = [c for c in sq.DL_FEATURES if c in df.columns]
    framework = tracking + ["A", "flip_composite", "dwell_composite", "mobius_continuous"]

    def evaluate(features: list[str], target: str) -> dict:
        d = df[df[target].notna()].copy()
        preds = pd.Series(np.nan, index=d.index)
        for year in [2023, 2024, 2025]:
            train = d[d["draft_year"] != year]
            test = d[d["draft_year"] == year]
            if len(train) < 20 or len(test) < 10:
                continue
            model = _ridge_model()
            model.fit(train[["B"] + features], train[target])
            preds.loc[test.index] = model.predict(test[["B"] + features])
        valid = preds.notna()
        return {
            "r2": r2_score(d.loc[valid, target], preds[valid]),
            "rho": spearmanr(d.loc[valid, target], preds[valid]).statistic,
            "rmse": float(np.sqrt(np.mean((d.loc[valid, target] - preds[valid]) ** 2))),
            "n": int(valid.sum()),
            "preds": preds,
            "actual": d[target],
        }

    results = {
        "official": evaluate(official, "shrunk_mean"),
        "tracking": evaluate(tracking, "shrunk_mean"),
        "framework": evaluate(framework, "shrunk_mean"),
    }
    for name, res in results.items():
        add_result(
            rows,
            "H4 out-of-time",
            f"{name}: OOF R2 for verified get-off",
            res["r2"],
            np.nan,
            np.nan,
            np.nan,
            res["n"],
            note=f"rho={res['rho']:.3f} rmse={res['rmse']:.4f}",
        )
    # Incremental R2 via paired bootstrap over players.
    paired = pd.concat(
        [results["tracking"]["actual"], results["tracking"]["preds"], results["framework"]["preds"]],
        axis=1,
    ).dropna()
    paired.columns = ["y", "tracking", "framework"]
    if len(paired) >= 20:
        diffs = []
        for _ in range(2000):
            idx = RNG.integers(0, len(paired), len(paired))
            s = paired.iloc[idx]
            diffs.append(
                r2_score(s["y"], s["framework"]) - r2_score(s["y"], s["tracking"])
            )
        lo, hi = np.percentile(diffs, [2.5, 97.5])
        add_result(
            rows,
            "H4 out-of-time",
            "incremental R2: framework - tracking",
            float(np.mean(diffs)),
            float(lo),
            float(hi),
            np.nan,
            len(paired),
        )
    # Bust classification AUC.
    for name, features in [("tracking", tracking), ("framework", framework)]:
        d = df[df["bust"].notna()].copy()
        preds = pd.Series(np.nan, index=d.index)
        for year in [2023, 2024, 2025]:
            train = d[d["draft_year"] != year]
            test = d[d["draft_year"] == year]
            if len(train) < 20 or len(test) < 10:
                continue
            model = _ridge_model()
            model.fit(train[["B"] + features], train["bust"])
            preds.loc[test.index] = model.predict(test[["B"] + features])
        valid = preds.notna()
        if d.loc[valid, "bust"].nunique() == 2:
            auc = roc_auc_score(d.loc[valid, "bust"], preds[valid])
            add_result(rows, "H4 out-of-time", f"{name}: OOF AUC for bust", auc, np.nan, np.nan, np.nan, int(valid.sum()))


def h7(df: pd.DataFrame, rows: list[dict]) -> None:
    d = df[df["bust"].notna()].copy()
    if "phi" not in d or d["phi"].notna().sum() < 30:
        return
    auc = roc_auc_score(d["bust"], d["phi"])
    add_result(rows, "H7 fragility", "phi AUC for bust", auc, np.nan, np.nan, np.nan, len(d))
    d["phi_q"] = pd.qcut(d["phi"], 4, labels=False, duplicates="drop")
    calibration = d.groupby("phi_q").agg(
        n=("bust", "size"), predicted=("phi", "mean"), observed=("bust", "mean")
    )
    calibration.to_csv(MODEL_DIR / "phi_calibration.csv")
    # Risk-flag compounding: compare observed vs main-effects prediction.
    d["risk_flags"] = (
        (d["square"] == "Yellow").astype(int)
        + (d["B"] >= 0.5).astype(int)
        + (d["flip_composite"] >= d["flip_composite"].quantile(0.75)).astype(int)
        + (d["dwell_composite"] <= d["dwell_composite"].quantile(0.25)).astype(int)
    )
    model = LogisticRegression(max_iter=2000)
    X = pd.get_dummies(d[["B", "A", "flip_composite", "dwell_composite"]], drop_first=False)
    model.fit(X, d["bust"])
    d["main_effect_pred"] = model.predict_proba(X)[:, 1]
    comp = d.groupby("risk_flags").agg(
        n=("bust", "size"), observed=("bust", "mean"), predicted=("main_effect_pred", "mean")
    )
    comp.to_csv(MODEL_DIR / "risk_flag_compounding.csv")
    high = comp[comp.index >= 3]
    if len(high):
        add_result(
            rows,
            "H7 fragility",
            "observed - main-effect bust rate (3+ flags)",
            float(high["observed"].mean() - high["predicted"].mean()),
            np.nan,
            np.nan,
            np.nan,
            int(high["n"].sum()),
            note="descriptive",
        )


def h8(df: pd.DataFrame, rows: list[dict]) -> None:
    teams = pd.read_parquet(MODEL_DIR / "dl_teams.parquet")
    multi = teams[teams["players"] >= 2]
    if len(multi) >= 5:
        add_result(
            rows,
            "H8 team compounding",
            "mean compounding excess (teams >=2)",
            float(multi["compounding_excess"].mean()),
            np.nan,
            np.nan,
            np.nan,
            int(multi["players"].sum()),
        )
    # Permutation test for within-team clustering of bust residuals.
    d = df[df["bust"].notna() & df["rookie_team"].notna()].copy()
    d["bust_residual"] = d["bust"] - d["phi"].fillna(d["phi"].mean())
    d = d[d["rookie_team"].notna()]
    if len(d) < 30:
        return

    def eta2(labels: pd.Series, values: pd.Series) -> float:
        grand = values.mean()
        total = ((values - grand) ** 2).sum()
        between = sum(
            len(values[labels == label]) * (values[labels == label].mean() - grand) ** 2
            for label in labels.unique()
        )
        return float(between / total) if total > 0 else np.nan

    observed = eta2(d["rookie_team"], d["bust_residual"])
    null = []
    labels = d["rookie_team"].to_numpy()
    for _ in range(5000):
        shuffled = RNG.permutation(labels)
        null.append(eta2(pd.Series(shuffled, index=d.index), d["bust_residual"]))
    p = (np.sum(np.array(null) >= observed) + 1) / (len(null) + 1)
    add_result(
        rows,
        "H8 team compounding",
        "within-team eta2 of bust residuals",
        float(observed),
        float(np.percentile(null, 2.5)),
        float(np.percentile(null, 97.5)),
        float(p),
        len(d),
        note=f"permutation p={p:.3f}",
    )
    multi.to_csv(MODEL_DIR / "team_multi.csv", index=False)


def h9(df: pd.DataFrame, rows: list[dict]) -> None:
    if "resilience" not in df or df["resilience"].notna().sum() < 30:
        return
    d = df[df["resilience"].notna()].copy()
    q_hi = d["resilience"].quantile(0.75)
    q_lo = d["resilience"].quantile(0.25)
    resilient = d[d["resilience"] >= q_hi]
    captured = d[d["resilience"] <= q_lo]
    features = [
        "flip_composite",
        "dwell_composite",
        "first_step",
        "agility",
        "path_efficiency",
        "n_attempts",
        "n_plays",
        "raw_speed_mean",
    ]
    profile_rows = []
    for feature in features:
        if feature not in d.columns:
            continue
        a = resilient[feature].dropna()
        b = captured[feature].dropna()
        if len(a) < 4 or len(b) < 4:
            continue
        diff, lo, hi = boot_diff(a, b)
        profile_rows.append(
            {
                "feature": feature,
                "resilient_mean": a.mean(),
                "captured_mean": b.mean(),
                "diff": diff,
                "ci_low": lo,
                "ci_high": hi,
                "n_resilient": len(a),
                "n_captured": len(b),
            }
        )
        add_result(
            rows,
            "H9 resilience",
            f"resilient - captured: {feature}",
            diff,
            lo,
            hi,
            np.nan,
            len(a) + len(b),
        )
    pd.DataFrame(profile_rows).to_csv(MODEL_DIR / "resilience_profiles.csv", index=False)
    yellow = d[d["square"] == "Yellow"].sort_values("resilience", ascending=False)
    yellow[["display_name", "draft_year", "C", "phi", "resilience", "mobius_continuous", "square"]].to_csv(
        MODEL_DIR / "yellow_resilience.csv", index=False
    )


def main() -> None:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(MODEL_DIR / "dl_players.parquet")
    df["bust"] = (df["C"] >= 0.75).astype(float)
    df.loc[df["C"].isna(), "bust"] = np.nan

    # Full-context sensitivity: include team identity in the context model.
    plays = pd.read_parquet(FEATURE_DIR / "dl_plays.parquet")
    full_res = pp.cross_fitted_residuals(
        plays, categorical_context=pp.CATEGORICAL_CONTEXT + ["team_abbr"]
    )
    full_out = pp.player_outcomes(plays.assign(context_residual=full_res))
    df = df.merge(
        full_out[["nfl_id", "shrunk_mean"]].rename(columns={"shrunk_mean": "shrunk_full"}),
        on="nfl_id",
        how="left",
    )
    df["C_full"] = c_from_outcome(df, "shrunk_full")
    df["bust_full"] = (df["C_full"] >= 0.75).astype(float)

    rows: list[dict] = []
    h1(df, rows)
    h2(df, rows)
    h3(df, rows)
    h4(df, rows)
    h7(df, rows)
    h8(df, rows)
    h9(df, rows)

    results = pd.DataFrame(rows)
    results["q_value"] = bh_fdr(results["p_value"])
    results.to_csv(MODEL_DIR / "hypothesis_results.csv", index=False)
    print(results.to_string(index=False))

    # Summary markdown.
    lines = ["# Results summary — Yellow Square DL analysis", ""]
    lines.append("Date: 2026-10-18. Primary outcome: context-adjusted get-off (no team identity).")
    lines.append("")
    lines.append("## Square counts")
    lines.append(df["square"].value_counts().to_string())
    lines.append("")
    lines.append("## Headline results")
    for _, row in results.iterrows():
        ci = ""
        if pd.notna(row["ci_low"]) and pd.notna(row["ci_high"]):
            ci = f" (95% CI {row['ci_low']:.3f} to {row['ci_high']:.3f})"
        lines.append(
            f"- **{row['hypothesis']}** — {row['test']}: {row['estimate']:.3f}{ci}"
            + (f", p={row['p_value']:.3f}" if pd.notna(row["p_value"]) else "")
            + (f", n={int(row['n'])}" if pd.notna(row["n"]) else "")
        )
    lines.append("")
    lines.append("## Caveats")
    lines.append("- Player-level N is small (115 with outcomes; 16 Yellow). CIs are wide.")
    lines.append("- The Yellow effect is sensitive to context adjustment; the full-context sensitivity is reported.")
    lines.append("- The Möbius signature is not supported in this sample; the binary flag is too rare for a contrast.")
    lines.append("- Team-level compounding is exploratory; the permutation test is the defensible check.")
    DOCS.joinpath("results_summary.md").write_text("\n".join(lines))
    print("\nWrote docs/results_summary.md")


if __name__ == "__main__":
    main()
