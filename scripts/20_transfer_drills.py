"""Build the per-drill Combine signals and their reliability."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from transfer import drills  # noqa: E402


if __name__ == "__main__":
    drills.main()
