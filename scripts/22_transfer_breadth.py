"""Test whether the interior burst predicts pressure-adjacent or box-score outcomes."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from transfer import breadth  # noqa: E402


if __name__ == "__main__":
    breadth.main()
