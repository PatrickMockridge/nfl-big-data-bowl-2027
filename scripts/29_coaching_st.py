"""Run the coaching retention and special teams descriptive markets."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "implications" / "markets" / "code"))

from coaching import main as coaching_main  # noqa: E402
from special_teams import main as st_main  # noqa: E402


if __name__ == "__main__":
    coaching_main()
    st_main()
