"""Build the combined core and salary figures used in the writeup."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from viz import salary_figures  # noqa: E402


if __name__ == "__main__":
    salary_figures.main()
