"""Small public-data soccer comparison (illustrative, not causal).

Five clubs span the two models named in the brief: academy-led / cost-conscious
clubs (Nordsjaelland, Bodø/Glimt, Viking, and Barcelona's La Masia) and
star-name spending in the doldrums (Manchester United). Barcelona is a hybrid:
a famous academy and one of the largest wage bills in Europe. The table is
therefore an order-of-magnitude illustration, not a natural experiment.

Season note: Norwegian clubs use the 2024 calendar season; the other three use
2024-25. Wage scopes differ by source and are stated in the table.
"""

from __future__ import annotations

import pandas as pd

from .common import OUT, ensure_dirs

ROWS = [
    {
        "club": "FC Barcelona",
        "league": "La Liga",
        "season": "2024-25",
        "position": "1st (88 pts)",
        "model": "La Masia + global star spending",
        "wage_measure": "Total wage bill EUR 551m (UEFA, players+coaches+staff)",
        "revenue_measure": "Revenue EUR 975m (Deloitte)",
        "wage_revenue_ratio": 551 / 975,
        "wage_tier": "top-3 European wage bill",
        "source": "UEFA European Club Finance and Investment Landscape 2025; Deloitte Money League 2025 (figures reported by Reuters, 22 Jan 2026)",
        "source_url": "https://www.uefa.com/insideuefa/protecting-the-game/club-licensing-and-financial-sustainability/",
        "caveat": "Hybrid model; wage scope differs from Deloitte's wages-only measure.",
    },
    {
        "club": "Manchester United",
        "league": "Premier League",
        "season": "2024-25",
        "position": "15th",
        "model": "star-name spending",
        "wage_measure": "Total wage bill EUR 416m (UEFA, players+coaches+staff)",
        "revenue_measure": "Revenue EUR 793m (Deloitte)",
        "wage_revenue_ratio": 416 / 793,
        "wage_tier": "top-10 European wage bill",
        "source": "UEFA European Club Finance and Investment Landscape 2025; Deloitte Money League 2025 (figures reported by Reuters, 22 Jan 2026)",
        "source_url": "https://www.uefa.com/insideuefa/protecting-the-game/club-licensing-and-financial-sustainability/",
        "caveat": "No European football in 2025-26; revenue and wage scope differ by source.",
    },
    {
        "club": "FC Nordsjaelland",
        "league": "Danish Superliga",
        "season": "2024-25",
        "position": "5th",
        "model": "academy / player trading",
        "wage_measure": "Personnel costs DKK 174.5m (2023 annual report); first-team player budget DKK 60-75m (2024-25 estimates)",
        "revenue_measure": "Revenue not disclosed in the available source",
        "wage_revenue_ratio": None,
        "wage_tier": "mid-tier Danish",
        "source": "FC Nordsjaelland A/S annual report (CVR 24257703); Tipsbladet player-budget estimate; Capology EUR 6.26m estimate as cross-check only",
        "source_url": "https://www.fcn.dk/",
        "caveat": "Player budget is not total wage bill; personnel costs are 2023; revenue unavailable.",
    },
    {
        "club": "Bodø/Glimt",
        "league": "Eliteserien",
        "season": "2024",
        "position": "1st (62 pts)",
        "model": "regional academy + continuity",
        "wage_measure": "Personnel costs NOK 260.9m (salary NOK 230.0m)",
        "revenue_measure": "Revenue NOK 602.8m",
        "wage_revenue_ratio": 260.9 / 602.8,
        "wage_tier": "top Norwegian wage bill",
        "source": "Bodø/Glimt 2024 annual report / årsmøtepapirer; NRK coverage of the 2024 accounts",
        "source_url": "https://www.glimt.no/nyheter/arsmelding-regnskap-og-budsjett-2024",
        "caveat": "Norwegian accounting; player-sale revenue inflates the denominator; Deloitte uses a different scope.",
    },
    {
        "club": "Viking FK",
        "league": "Eliteserien",
        "season": "2024",
        "position": "3rd (57 pts)",
        "model": "regional academy + continuity",
        "wage_measure": "Sport salary NOK 61.6m (players/coaches/staff); total personnel NOK 72.7m including other employees",
        "revenue_measure": "Viking Fotball AS revenue NOK 220.3m",
        "wage_revenue_ratio": 61.6 / 220.3,
        "wage_tier": "upper-mid Norwegian",
        "source": "Viking FK 2024 annual report (note 2); Viking Fotball AS accounts via Regnskapstall/Proff",
        "source_url": "https://www.vikingfotball.no/",
        "caveat": "Sport salary covers A-team players/coaches/staff paid by Viking Fotball AS; total personnel includes other staff.",
    },
]


def build() -> pd.DataFrame:
    df = pd.DataFrame(ROWS)
    df["wage_revenue_ratio"] = df["wage_revenue_ratio"].round(3)
    ensure_dirs()
    df.to_csv(OUT / "soccer_table.csv", index=False)
    return df


def markdown(df: pd.DataFrame) -> str:
    lines = [
        "| Club | League / season | Pos. | Model | Wage measure | Revenue | Wage/revenue | Source | Caveat |",
        "|:--|:--|:--|:--|:--|:--|--:|:--|:--|",
    ]
    for r in df.itertuples():
        ratio = "n/a" if pd.isna(r.wage_revenue_ratio) else f"{r.wage_revenue_ratio:.0%}"
        lines.append(
            f"| {r.club} | {r.league} {r.season} | {r.position} | {r.model} | {r.wage_measure} | "
            f"{r.revenue_measure} | {ratio} | {r.source} | {r.caveat} |"
        )
    return "\n".join(lines)


def main() -> None:
    df = build()
    print(markdown(df))
    print("\nWage/revenue ratios:")
    print(df[["club", "wage_revenue_ratio"]].dropna().to_string(index=False))


if __name__ == "__main__":
    main()
