"""Build the market portfolio figures."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "implications" / "markets" / "code"))

from figures import main  # noqa: E402


if __name__ == "__main__":
    main()
