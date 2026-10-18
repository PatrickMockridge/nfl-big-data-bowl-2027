"""Run the data audit and write outputs/audit/ artifacts."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from data.audit import run  # noqa: E402


def main() -> None:
    paths = run()
    for name, path in paths.items():
        print(f"{name}: {path}")


if __name__ == "__main__":
    main()
