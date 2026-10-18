"""Build the 2023-2025 team-season salary panel.

Requires the public external files in ``data/external`` and the archived OTC
2025 cap pages in ``data/external/otc_cap_2025`` (the latter are downloaded on
first run). Writes ``outputs/salary/team_salary_panel.csv`` and the component
tables.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from salary import team_panel  # noqa: E402


if __name__ == "__main__":
    team_panel.main()
