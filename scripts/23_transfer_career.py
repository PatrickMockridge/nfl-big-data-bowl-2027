"""Build the BDB-native career reward ladder."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from transfer import career  # noqa: E402


if __name__ == "__main__":
    career.main()
