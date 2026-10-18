"""Run the salary efficiency, QB-premium, rent, and soccer analyses."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from salary import analysis, rents, soccer  # noqa: E402


if __name__ == "__main__":
    analysis.main()
    rents.main()
    soccer.main()
