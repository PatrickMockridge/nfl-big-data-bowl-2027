"""Build the dynamic Yellow Square state and team/cohort state."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from framework import dynamic  # noqa: E402


if __name__ == "__main__":
    dynamic.main()
