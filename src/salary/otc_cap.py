"""2025 player-level cap ledger from archived OverTheCap team pages.

The public Kaggle contract snapshot is a 2026 current-contract list and covers
only about half of 2025 snaps. Archived OTC team cap pages from late 2025 give
the 2025 active-roster cap numbers and dead-money charges, which is a much
better basis for a 2025 rent proxy.

The archived pages are fetched once and cached in
``data/external/otc_cap_2025`` (gitignored). The parser selects the first table
(active roster) and sums the non-active cap-charge tables as dead money.
"""

from __future__ import annotations

import gzip
import io
import json
import re
import time
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

from .common import EXTERNAL, OUT, ensure_dirs, normalize_name, stats_group, season_age

CACHE = EXTERNAL / "otc_cap_2025"
PLAYERS = EXTERNAL / "players.csv"

TEAM_SLUGS = {
    "ARI": "arizona-cardinals", "ATL": "atlanta-falcons", "BAL": "baltimore-ravens",
    "BUF": "buffalo-bills", "CAR": "carolina-panthers", "CHI": "chicago-bears",
    "CIN": "cincinnati-bengals", "CLE": "cleveland-browns", "DAL": "dallas-cowboys",
    "DEN": "denver-broncos", "DET": "detroit-lions", "GB": "green-bay-packers",
    "HOU": "houston-texans", "IND": "indianapolis-colts", "JAX": "jacksonville-jaguars",
    "KC": "kansas-city-chiefs", "LAC": "los-angeles-chargers", "LAR": "los-angeles-rams",
    "LV": "las-vegas-raiders", "MIA": "miami-dolphins", "MIN": "minnesota-vikings",
    "NE": "new-england-patriots", "NO": "new-orleans-saints", "NYG": "new-york-giants",
    "NYJ": "new-york-jets", "PHI": "philadelphia-eagles", "PIT": "pittsburgh-steelers",
    "SEA": "seattle-seahawks", "SF": "san-francisco-49ers", "TB": "tampa-bay-buccaneers",
    "TEN": "tennessee-titans", "WAS": "washington-commanders",
}

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"


def _get(url: str, timeout: int = 90) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "identity"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read()
        if data[:2] == b"\x1f\x8b" or r.headers.get("Content-Encoding") == "gzip":
            data = gzip.decompress(data)
        return data


def latest_2025_snapshot(slug: str) -> str | None:
    url = (
        "http://web.archive.org/cdx/search/cdx"
        f"?url=overthecap.com/salary-cap/{slug}"
        "&from=20250101&to=20251231&output=json&filter=statuscode:200"
        "&collapse=timestamp:8&limit=200"
    )
    try:
        rows = json.loads(_get(url).decode())
    except Exception:
        return None
    if len(rows) <= 1:
        return None
    # Rows are [urlkey, timestamp, original, mimetype, statuscode, ...].
    return rows[-1][1]


def download(force: bool = False) -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    for team, slug in TEAM_SLUGS.items():
        path = CACHE / f"{team}.html"
        if path.exists() and path.stat().st_size > 100_000 and not force:
            continue
        ts = latest_2025_snapshot(slug)
        if ts is None:
            print(f"  {team}: no 2025 snapshot")
            continue
        urls = [f"https://web.archive.org/web/{ts}id_/https://overthecap.com/salary-cap/{slug}"]
        urls += [
            f"https://web.archive.org/web/{fallback}id_/https://overthecap.com/salary-cap/{slug}"
            for fallback in ("20250901000000", "20251101000000", "20250701000000")
        ]
        ok = False
        for u in urls:
            for attempt in range(2):
                try:
                    path.write_bytes(_get(u))
                    print(f"  {team}: {ts} ({path.stat().st_size:,} bytes)")
                    ok = True
                    break
                except Exception as e:
                    if attempt == 1:
                        print(f"  {team}: download failed: {e}")
                    else:
                        time.sleep(2.0)
            if ok:
                break
        if not ok:
            continue
        time.sleep(1.2)


def _money(x) -> float:
    if pd.isna(x):
        return np.nan
    s = str(x).replace("$", "").replace(",", "").strip()
    if s in ("", "-", "—"):
        return np.nan
    neg = s.startswith("(") and s.endswith(")")
    s = s.strip("()")
    try:
        v = float(s)
    except ValueError:
        return np.nan
    return -v if neg else v


def _flatten(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c[1] if isinstance(c, tuple) else c for c in df.columns]
    return df


def parse_team(team: str, html: str) -> pd.DataFrame:
    tables = pd.read_html(io.StringIO(html), flavor="html5lib")
    if not tables:
        raise ValueError(f"{team}: no tables")
    active = _flatten(tables[0])
    cols = list(active.columns)
    if "Player" not in cols or "Cap Number" not in cols:
        raise ValueError(f"{team}: unexpected active table columns {cols[:8]}")
    cap_idx = cols.index("Cap Number")
    guaranteed_idx = cols.index("Guaranteed Salary") if "Guaranteed Salary" in cols else None
    # Keep by position because several bonus columns share names.
    keep = {
        "player": 0,
        "base_salary": 1,
        "prorated_signing": 2,
        "prorated_option": 3,
        "roster_regular": 4,
        "roster_per_game": 5,
        "workout_bonus": 6,
        "other_bonus": 7,
        "guaranteed_salary": guaranteed_idx,
        "cap_number": cap_idx,
    }
    out = pd.DataFrame({k: active.iloc[:, v] for k, v in keep.items() if v is not None})
    out = out[out["player"].notna() & out["player"].astype(str).str.upper().ne("TOTAL")].copy()
    out["team"] = team
    for c in out.columns:
        if c not in ("player", "team"):
            out[c] = out[c].map(_money)
    out = out[out["cap_number"].notna() & (out["cap_number"] > 0)]

    # OTC player links carry a stable OTC id; the master players table has the
    # same id, which avoids nickname mismatches (Matt vs Matthew, Mike vs
    # Michael, Tariq vs Riq).
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find_all("table")[0]
    links = []
    for tr in table.find_all("tr"):
        a = tr.find("a", href=re.compile(r"/player/"))
        if not a:
            continue
        m = re.search(r"/player/[^/]+/(\d+)/?", a["href"])
        if m:
            links.append({"player": a.get_text(strip=True), "otc_id": m.group(1)})
    if links:
        out = out.merge(pd.DataFrame(links).drop_duplicates("player"), on="player", how="left")
    else:
        out["otc_id"] = pd.NA
    return out


def _attributes() -> pd.DataFrame:
    pl = pd.read_csv(
        PLAYERS,
        usecols=[
            "otc_id", "gsis_id", "display_name", "position", "position_group",
            "birth_date", "rookie_season", "draft_team",
        ],
    )
    pl["otc_id"] = pl["otc_id"].astype("string").str.replace(r"\.0$", "", regex=True)
    pl["name_key"] = normalize_name(pl["display_name"])
    pl["pos_group"] = stats_group(pl["position_group"], pl["position"])
    return pl.drop_duplicates("otc_id")


def build() -> tuple[pd.DataFrame, pd.DataFrame]:
    download()
    frames, team_rows = [], []
    for team in TEAM_SLUGS:
        path = CACHE / f"{team}.html"
        if not path.exists():
            continue
        try:
            players = parse_team(team, path.read_text(errors="ignore"))
        except Exception as e:
            print(f"  {team}: parse failed: {e}")
            continue
        players["name_key"] = normalize_name(players["player"])
        frames.append(players)
        team_rows.append(
            {
                "season": 2025,
                "team": team,
                "active_cap": players["cap_number"].sum(),
                "n_active": len(players),
            }
        )
    if not frames:
        raise RuntimeError("no OTC cap pages parsed")
    players = pd.concat(frames, ignore_index=True)
    team = pd.DataFrame(team_rows)

    attrs = _attributes()
    players["otc_id"] = players["otc_id"].astype("string")
    players = players.merge(attrs.drop(columns=["name_key", "display_name"]), on="otc_id", how="left")
    # Name fallback for the small number of rows without a usable OTC id.
    missing = players["gsis_id"].isna()
    if missing.any():
        fb = players.loc[missing, ["name_key"]].merge(
            attrs.drop_duplicates("name_key")[
                ["name_key", "gsis_id", "position", "position_group", "pos_group", "birth_date", "rookie_season", "draft_team"]
            ],
            on="name_key",
            how="left",
        )
        for c in ["gsis_id", "position", "position_group", "pos_group", "birth_date", "rookie_season", "draft_team"]:
            players.loc[missing, c] = fb[c].to_numpy()
    players["pos_group"] = players["pos_group"].fillna("OTHER")
    players["age_start"] = season_age(players["birth_date"], 2025)
    players["years_exp"] = 2025 - pd.to_numeric(players["rookie_season"], errors="coerce")

    # Team cap shares (active roster; non-ST denominator for position shares).
    od = players[players["pos_group"].ne("ST")]
    for team_name, g in od.groupby("team"):
        cap = g["cap_number"].sum()
        if cap <= 0:
            continue
        idx = team["team"].eq(team_name)
        team.loc[idx, "top5_cap_share"] = g["cap_number"].nlargest(5).sum() / cap
        team.loc[idx, "qb_cap_share"] = g.loc[g["pos_group"].eq("QB"), "cap_number"].sum() / cap
        team.loc[idx, "star_cap_share"] = g.loc[g["pos_group"].isin(["QB", "RB", "WR", "TE", "EDGE"]), "cap_number"].sum() / cap
        team.loc[idx, "trench_cap_share"] = g.loc[g["pos_group"].isin(["OL", "IDL", "LB", "S", "CB"]), "cap_number"].sum() / cap
        team.loc[idx, "guaranteed_share"] = g["guaranteed_salary"].sum() / g["cap_number"].sum()

    ensure_dirs()
    players.to_csv(OUT / "otc_cap_2025_players.csv", index=False)
    team.to_csv(OUT / "otc_cap_2025_team.csv", index=False)
    return players, team


def main() -> None:
    players, team = build()
    print(f"OTC 2025 cap: {len(players)} player rows, {len(team)} teams")
    print("active cap $M range:", round(team.active_cap.min() / 1e6, 1), round(team.active_cap.max() / 1e6, 1))
    print("position group coverage:", players.pos_group.value_counts(dropna=False).to_dict())


if __name__ == "__main__":
    main()
