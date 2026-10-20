"""Shared helpers for the transfer pilots.

Tier 1 descriptive only: no causal identification, no dollar model. The
constants mirror ``config.yaml`` ``transfer:`` and ``docs/TRANSFER_PROTOCOL.md``.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "outputs" / "panel" / "panel_full.parquet"
ROLE_PANEL = ROOT / "outputs" / "discovery" / "role_allocation_player_seasons_full.parquet"
BURST_PLAYERS = ROOT / "outputs" / "discovery" / "interior_burst_players.parquet"
OUT = ROOT / "outputs" / "transfer"

POSITIONS = ["WR", "TE", "OL", "DL", "DB"]
DL_SUBGROUPS = ["INTERIOR", "EDGE"]


def load_config() -> dict:
    with open(ROOT / "config.yaml") as handle:
        return yaml.safe_load(handle)["transfer"]


CONFIG = load_config()
SEED = int(CONFIG["seed"])


def load_panel() -> pd.DataFrame:
    return pd.read_parquet(PANEL)


def load_role_panel() -> pd.DataFrame:
    return pd.read_parquet(ROLE_PANEL)


def position_subgroup(players: pd.DataFrame) -> pd.Series:
    """DL split used throughout the entry: DE/OLB are EDGE, DT/NT INTERIOR."""
    return pd.Series(
        np.where(
            players["nfl_position"].isin(["DE", "OLB"]),
            "EDGE",
            np.where(
                players["nfl_position"].isin(["DT", "NT"]),
                "INTERIOR",
                players["position_group"],
            ),
        ),
        index=players.index,
    )


def bh_fdr(pvalues: pd.Series) -> pd.Series:
    """Benjamini-Hochberg q-values (ported from scripts/05_test_hypotheses.py)."""
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


def holm_adjust(pvalues: pd.Series) -> pd.Series:
    """Holm step-down adjusted p-values."""
    p = pvalues.astype(float).copy()
    valid = p.notna()
    out = pd.Series(np.nan, index=p.index)
    if valid.sum() == 0:
        return out
    values = p[valid].to_numpy()
    order = np.argsort(values)
    ranked = values[order]
    m = len(ranked)
    adjusted = np.maximum.accumulate(ranked * (m - np.arange(m)))
    result = np.empty(m)
    result[order] = np.clip(adjusted, 0, 1)
    out.loc[valid] = result
    return out


def status_from_beta(beta: float, ci_low: float, ci_high: float) -> str:
    """Pre-registered status vocabulary for L1."""
    if pd.isna(beta) or pd.isna(ci_low) or pd.isna(ci_high):
        return "unidentifiable"
    if beta > 0 and ci_low > 0:
        return "supported"
    if beta > 0 and ci_high > 0:
        return "weak"
    return "null"


def pricing_label(rho: float) -> str:
    """Pre-registered L2 interpretation."""
    if pd.isna(rho):
        return "unidentifiable"
    value = abs(rho)
    if value < float(CONFIG["pricing_unpriced_max"]):
        return "unpriced"
    if value < float(CONFIG["pricing_priced_min"]):
        return "partly priced"
    return "priced"


def bootstrap_spearman(
    df: pd.DataFrame,
    x: str,
    y: str,
    cluster: str = "nfl_id",
    n: int | None = None,
    seed: int | None = None,
) -> tuple[float, float, float, int]:
    """Spearman correlation with a cluster bootstrap (resample clusters)."""
    from scipy.stats import spearmanr

    d = df[[x, y, cluster]].dropna()
    if len(d) < 3 or d[x].nunique() < 2 or d[y].nunique() < 2:
        return np.nan, np.nan, np.nan, len(d)
    rho = float(spearmanr(d[x], d[y]).statistic)
    draws = int(n or CONFIG["bootstrap_draws"])
    rng = np.random.default_rng(seed if seed is not None else SEED)
    units = d[cluster].unique()
    values = []
    for _ in range(draws):
        sample = rng.choice(units, len(units), replace=True)
        sub = d[d[cluster].isin(sample)]
        if sub[x].nunique() < 2 or sub[y].nunique() < 2:
            continue
        values.append(spearmanr(sub[x], sub[y]).statistic)
    if not values:
        return rho, np.nan, np.nan, len(d)
    lo, hi = np.percentile(values, [2.5, 97.5])
    return rho, float(lo), float(hi), len(d)


def bootstrap_mean(
    values: pd.Series,
    n: int | None = None,
    seed: int | None = None,
) -> tuple[float, float, float, int]:
    """Mean with a row bootstrap; rows are one per player for the gap tables."""
    v = values.dropna().to_numpy(dtype=float)
    if len(v) < 2:
        return np.nan, np.nan, np.nan, len(v)
    draws = int(n or CONFIG["bootstrap_draws"])
    rng = np.random.default_rng(seed if seed is not None else SEED)
    means = [rng.choice(v, len(v), replace=True).mean() for _ in range(draws)]
    lo, hi = np.percentile(means, [2.5, 97.5])
    return float(v.mean()), float(lo), float(hi), len(v)


def bootstrap_mean_cluster(
    df: pd.DataFrame,
    value: str,
    cluster: str = "nfl_id",
    n: int | None = None,
    seed: int | None = None,
) -> tuple[float, float, float, int, int]:
    """Mean with a cluster bootstrap, for player-season gap tables."""
    d = df[[value, cluster]].dropna()
    if len(d) < 2:
        return np.nan, np.nan, np.nan, len(d), d[cluster].nunique()
    draws = int(n or CONFIG["bootstrap_draws"])
    rng = np.random.default_rng(seed if seed is not None else SEED)
    units = d[cluster].unique()
    values = []
    for _ in range(draws):
        sample = rng.choice(units, len(units), replace=True)
        sub = d[d[cluster].isin(sample)]
        if len(sub):
            values.append(sub[value].mean())
    lo, hi = np.percentile(values, [2.5, 97.5])
    return float(d[value].mean()), float(lo), float(hi), len(d), d[cluster].nunique()


def save(df: pd.DataFrame, name: str) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    df.to_csv(path, index=False)
    print(f"wrote {path.relative_to(ROOT)} ({len(df)} rows)")
    return path
