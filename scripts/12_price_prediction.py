"""Run the price-vs-prediction 2x2 discovery engine."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from discovery import price_prediction  # noqa: E402


if __name__ == "__main__":
    price_prediction.main()
