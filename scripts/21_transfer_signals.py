"""Run the three-link transfer screen (L1, L2, L3)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from transfer import signals  # noqa: E402


if __name__ == "__main__":
    signals.main()
