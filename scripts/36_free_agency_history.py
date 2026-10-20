"""Build the historical contract trends."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "implications" / "free_agency" / "code"))

from historical import main  # noqa: E402


if __name__ == "__main__":
    main()
