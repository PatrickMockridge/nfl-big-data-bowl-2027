"""Shared helpers for the salary extension.

Team abbreviations differ across sources (nflverse uses ``LA``; OTC and the
contract dataset use ``LAR``). Historical draft clubs include relocated
franchises. Normalize once here rather than in every module.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
EXTERNAL = ROOT / "data" / "external"
OUT = ROOT / "outputs" / "salary"

SEASONS = (2023, 2024, 2025)
OTC_GROUPS = ["QB", "RB", "WR", "TE", "OL", "IDL", "EDGE", "LB", "S", "CB"]
SKILL_GROUPS = ["QB", "RB", "WR", "TE"]
FRONT_SEVEN = ["IDL", "EDGE", "LB"]
BACK_SEVEN = ["S", "CB"]

# NFL salary-cap limits ($), used only as a denominator sensitivity.
CAP_LIMIT = {2023: 224_800_000, 2024: 255_400_000, 2025: 279_200_000}

TEAM_FIX = {
    "LA": "LAR",
    "STL": "LAR",
    "OAK": "LV",
    "SD": "LAC",
    "LAC": "LAC",
    "LV": "LV",
}

CONTRACT_POS = {
    "QB": "QB",
    "RB": "RB",
    "FB": "RB",
    "WR": "WR",
    "TE": "TE",
    "G": "OL",
    "C": "OL",
    "T": "OL",
    "OT": "OL",
    "OG": "OL",
    "LT": "OL",
    "RT": "OL",
    "OL": "OL",
    "DL": "IDL",
    "DT": "IDL",
    "NT": "IDL",
    "IDL": "IDL",
    "ED": "EDGE",
    "EDGE": "EDGE",
    "DE": "EDGE",
    "LB": "LB",
    "ILB": "LB",
    "MLB": "LB",
    "OLB": "LB",
    "S": "S",
    "FS": "S",
    "SS": "S",
    "SAF": "S",
    "DB": "S",
    "CB": "CB",
    "K": "ST",
    "P": "ST",
    "LS": "ST",
}


def normalize_team(series: pd.Series) -> pd.Series:
    """Normalize team abbreviations to the 2023-2025 nflverse/OTC convention."""
    out = series.astype("string").str.strip().str.upper()
    return out.replace(TEAM_FIX)


def contract_group(pos: pd.Series) -> pd.Series:
    """Map contract positions to OTC position groups."""
    return pos.astype("string").str.strip().str.upper().map(CONTRACT_POS).fillna("OTHER")


def stats_group(position_group: pd.Series, position: pd.Series) -> pd.Series:
    """Map nflverse position groups to OTC groups, splitting EDGE/IDL and CB/S."""
    pg = position_group.astype("string").str.strip().str.upper().fillna("")
    p = position.astype("string").str.strip().str.upper().fillna("")
    out = pd.Series(np.where(pg.eq("DL"), np.where(p.isin(["DE", "EDGE", "OLB"]), "EDGE", "IDL"), pg), index=pg.index)
    out = pd.Series(np.where(pg.eq("DB"), np.where(p.eq("CB"), "CB", "S"), out), index=pg.index)
    out = pd.Series(np.where(pg.eq("SPEC"), "ST", out), index=pg.index)
    return out


def season_age(birth_date: pd.Series, season, month: int = 9, day: int = 1) -> pd.Series:
    """Age at the start of the season (default 1 September)."""
    birth = pd.to_datetime(birth_date, errors="coerce")
    if not isinstance(season, pd.Series):
        season = pd.Series(season, index=birth.index)
    ref = pd.to_datetime(dict(year=season.astype(int), month=month, day=day))
    return (ref - birth).dt.days / 365.25


_SUFFIX = re.compile(r"\b(jr|sr|ii|iii|iv|v)\.?$")


def normalize_name(series: pd.Series) -> pd.Series:
    """Normalize player names for cross-source joins."""
    s = series.astype("string").str.lower().str.strip()
    s = s.str.replace(r"[^a-z0-9\s]", "", regex=True)
    s = s.str.replace(r"\s+", " ", regex=True)
    s = s.apply(lambda x: _SUFFIX.sub("", x).strip() if isinstance(x, str) else x)
    return s


def zscore(series: pd.Series, by: list[str] | None = None) -> pd.Series:
    """Standardize, optionally within groups."""
    if by:
        grp = series.groupby([series.index.get_level_values(b) if isinstance(series.index, pd.MultiIndex) else None for b in by])
        return grp.transform(lambda x: (x - x.mean()) / x.std(ddof=0))
    return (series - series.mean()) / series.std(ddof=0)


def zscore_frame(df: pd.DataFrame, cols: list[str], by: list[str]) -> pd.DataFrame:
    """Add z-scored versions of ``cols`` within ``by`` groups."""
    out = df.copy()
    for c in cols:
        out[f"{c}_z"] = out.groupby(by)[c].transform(lambda x: (x - x.mean()) / x.std(ddof=0) if x.notna().sum() > 1 else 0.0)
    return out


def ensure_dirs() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
