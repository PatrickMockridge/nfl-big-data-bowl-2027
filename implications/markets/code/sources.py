"""Public market data acquisition and audit for the market portfolio.

Downloads nflverse trades and draft picks (public; cited), derives coach
tenure from the existing nflverse games file, and summarizes the historical
contract snapshot. Raw downloads stay in ``data/external/market/`` (gitignored);
derived aggregates go to ``outputs/market/``.
"""

from __future__ import annotations

import hashlib
import io
import json
import urllib.request
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "external" / "market"
OUT = ROOT / "implications" / "markets" / "outputs"
GAMES = ROOT / "data" / "external" / "games.csv"
HIST_CONTRACTS = ROOT / "data" / "external" / "historical_contracts.csv.gz"

SOURCES = {
    "trades": "https://github.com/nflverse/nflverse-data/releases/download/trades/trades.csv",
    "draft_picks": "https://github.com/nflverse/nflverse-data/releases/download/draft_picks/draft_picks.csv",
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download(name: str, force: bool = False) -> Path:
    """Download a source to the cache; return the local path.

    Falls back to an existing local file and records the failure rather than
    silently substituting.
    """
    RAW.mkdir(parents=True, exist_ok=True)
    path = RAW / f"{name}.csv"
    if path.exists() and not force:
        return path
    try:
        with urllib.request.urlopen(SOURCES[name], timeout=120) as response:
            data = response.read()
    except Exception as exc:  # pragma: no cover - network dependent
        if path.exists():
            print(f"{name}: download failed ({exc}); using cached {path.name}")
            return path
        raise RuntimeError(f"could not download {name}: {exc}") from exc
    path.write_bytes(data)
    return path


def build_manifest() -> pd.DataFrame:
    rows = []
    for name, url in SOURCES.items():
        path = download(name)
        rows.append(
            {
                "source": name,
                "url": url,
                "path": str(path.relative_to(ROOT)),
                "bytes": path.stat().st_size,
                "sha256": _sha256(path),
            }
        )
    manifest = pd.DataFrame(rows)
    RAW.mkdir(parents=True, exist_ok=True)
    (RAW / "manifest.json").write_text(manifest.to_json(orient="records", indent=2))
    return manifest


def load_trades() -> pd.DataFrame:
    return pd.read_csv(download("trades"))


def load_draft_picks() -> pd.DataFrame:
    return pd.read_csv(download("draft_picks"))


def trades_summary(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame(columns=["season", "trades", "player_rows", "pick_rows"])
    d = trades.copy()
    d["is_pick"] = d["pick_season"].notna()
    return (
        d.groupby("season")
        .agg(trades=("trade_id", "nunique"), rows=("trade_id", "size"),
             pick_rows=("is_pick", "sum"))
        .reset_index()
        .assign(player_rows=lambda x: x["rows"] - x["pick_rows"])
        .drop(columns="rows")
    )


def draft_summary(picks: pd.DataFrame) -> pd.DataFrame:
    if picks.empty:
        return pd.DataFrame(columns=["season", "picks", "rounds"])
    return (
        picks.groupby("season")
        .agg(picks=("pick", "size"), rounds=("round", "max"),
             teams=("team", "nunique"))
        .reset_index()
    )


def coaching_seasons() -> pd.DataFrame:
    """Coach-team-season tenure from nflverse games (1999-present).

    Uses the first/last regular-season game date as the tenure proxy. Hire/fire
    dates are not available in the public game file; a local
    ``data/external/market/coaching_hires.csv`` is merged if present.
    """
    games = pd.read_csv(GAMES, usecols=[
        "game_id", "season", "game_type", "week", "gameday",
        "home_team", "away_team", "home_score", "away_score",
        "home_coach", "away_coach",
    ])
    games = games[games["game_type"].eq("REG")].copy()
    games["gameday"] = pd.to_datetime(games["gameday"], errors="coerce")
    home = games.rename(columns={
        "home_team": "team", "away_team": "opponent",
        "home_score": "points_for", "away_score": "points_against",
        "home_coach": "coach",
    })[["game_id", "season", "week", "gameday", "team", "opponent",
        "points_for", "points_against", "coach"]]
    away = games.rename(columns={
        "away_team": "team", "home_team": "opponent",
        "away_score": "points_for", "home_score": "points_against",
        "away_coach": "coach",
    })[["game_id", "season", "week", "gameday", "team", "opponent",
        "points_for", "points_against", "coach"]]
    long = pd.concat([home, away], ignore_index=True)
    long["win"] = long["points_for"] > long["points_against"]
    out = (
        long.groupby(["team", "season", "coach"])
        .agg(
            games=("game_id", "nunique"),
            wins=("win", "sum"),
            points_for=("points_for", "sum"),
            points_against=("points_against", "sum"),
            first_game=("gameday", "min"),
            last_game=("gameday", "max"),
        )
        .reset_index()
    )
    out["win_rate"] = out["wins"] / out["games"].replace(0, float("nan"))
    out["point_diff"] = out["points_for"] - out["points_against"]
    out = out.sort_values(["team", "season", "games"], ascending=[True, True, False])
    return out


def coaching_team_season(long: pd.DataFrame) -> pd.DataFrame:
    """One row per team-season: the primary coach and retention.

    A mid-season change is resolved to the coach with the most games; the number
    of coaches is kept as ``n_coaches``. Retention compares the primary coach
    with the next season's primary coach.
    """
    d = long.copy()
    d = d.sort_values(["team", "season", "games", "last_game"],
                      ascending=[True, True, False, False])
    primary = d.drop_duplicates(["team", "season"]).copy()
    n_coaches = (
        d.groupby(["team", "season"])["coach"].nunique().rename("n_coaches")
    )
    primary = primary.merge(n_coaches, on=["team", "season"], how="left")
    primary = primary.sort_values(["team", "season"]).reset_index(drop=True)
    primary["next_season"] = primary.groupby("team")["season"].shift(-1)
    primary["next_coach"] = primary.groupby("team")["coach"].shift(-1)
    primary["retained_next"] = (
        (primary["next_season"] == primary["season"] + 1)
        & (primary["next_coach"] == primary["coach"])
    ).astype(int)

    primary["prev_season_same"] = primary.groupby(["team", "coach"])["season"].shift()
    primary["new_stint"] = (
        primary["prev_season_same"].isna()
        | (primary["season"] != primary["prev_season_same"] + 1)
    ).astype(int)
    primary["stint_id"] = primary.groupby(["team", "coach"])["new_stint"].cumsum()
    primary["tenure"] = (
        primary.groupby(["team", "coach", "stint_id"]).cumcount() + 1
    )
    primary = primary.drop(columns="prev_season_same")

    hires = RAW / "coaching_hires.csv"
    if hires.exists():
        extra = pd.read_csv(hires)
        primary = primary.merge(extra, on=["team", "season", "coach"], how="left")
    return primary


def historical_contracts_summary() -> pd.DataFrame:
    d = pd.read_csv(HIST_CONTRACTS, usecols=[
        "position", "year_signed", "apy", "apy_cap_pct", "guaranteed", "value"
    ])
    d = d[d["year_signed"].between(1994, 2022)].copy()
    return (
        d.groupby(["year_signed", "position"])
        .agg(
            contracts=("apy", "size"),
            median_apy_m=("apy", lambda s: s.median() / 1e6),
            median_apy_cap_pct=("apy_cap_pct", "median"),
            median_guaranteed_m=("guaranteed", lambda s: s.median() / 1e6),
        )
        .reset_index()
        .rename(columns={"year_signed": "season"})
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = build_manifest()
    trades = load_trades()
    picks = load_draft_picks()
    coaching_coaches = coaching_seasons()
    coaching = coaching_team_season(coaching_coaches)
    contracts = historical_contracts_summary()

    manifest.to_csv(OUT / "source_manifest.csv", index=False)
    trades_summary(trades).to_csv(OUT / "trades_summary.csv", index=False)
    draft_summary(picks).to_csv(OUT / "draft_picks_summary.csv", index=False)
    coaching_coaches.to_csv(OUT / "coaching_coaches.csv", index=False)
    coaching.to_csv(OUT / "coaching_seasons.csv", index=False)
    contracts.to_csv(OUT / "historical_contracts_summary.csv", index=False)

    audit = pd.DataFrame(
        [
            {
                "source": "nflverse trades",
                "rows": len(trades),
                "min_season": int(trades["season"].min()),
                "max_season": int(trades["season"].max()),
                "note": "team-level trade rows; picks and players",
            },
            {
                "source": "nflverse draft_picks",
                "rows": len(picks),
                "min_season": int(picks["season"].min()),
                "max_season": int(picks["season"].max()),
                "note": "career outcomes attached; PFR source",
            },
            {
                "source": "nflverse games coaches",
                "rows": len(coaching),
                "min_season": int(coaching["season"].min()),
                "max_season": int(coaching["season"].max()),
                "note": "team-season primary coach; first/last game proxy",
            },
            {
                "source": "historical contracts",
                "rows": len(contracts),
                "min_season": int(contracts["season"].min()),
                "max_season": int(contracts["season"].max()),
                "note": "APY context 1994-2022; not linked to 2023-25 performance",
            },
        ]
    )
    audit.to_csv(OUT / "source_audit.csv", index=False)
    print(audit.to_string(index=False))


if __name__ == "__main__":
    main()
