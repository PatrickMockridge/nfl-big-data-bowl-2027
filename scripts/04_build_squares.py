"""Build the Green/Yellow/Red/Blue player table and team/cohort table."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from framework import squares  # noqa: E402


if __name__ == "__main__":
    squares.main()
