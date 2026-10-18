"""Build the corrected regular-season player-season panel."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from features import panel  # noqa: E402


if __name__ == "__main__":
    panel.main()
