"""Download the NFL Big Data Bowl 2027 competition data via kagglehub.

Writes the resolved data path to data/raw_path.txt and a manifest of file
sizes and SHA-256 hashes to data/manifest.json. Raw data stays gitignored.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import kagglehub

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
COMPETITION = "nfl-big-data-bowl-2027"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {COMPETITION} ...")
    raw_root = Path(kagglehub.competition_download(COMPETITION))
    print(f"Resolved cache root: {raw_root}")

    files = sorted(raw_root.rglob("*.csv"))
    if not files:
        raise SystemExit(f"No CSV files found under {raw_root}")
    data_dir = files[0].parent
    if any(file.parent != data_dir for file in files):
        raise SystemExit("CSV files are spread across multiple directories")

    print(f"Data directory: {data_dir}")
    (DATA_DIR / "raw_path.txt").write_text(str(data_dir))

    link = DATA_DIR / "raw"
    if link.is_symlink() or link.exists():
        link.unlink()
    link.symlink_to(data_dir)
    print(f"Linked {link} -> {data_dir}")

    manifest = []
    for file in files:
        entry = {
            "file": file.name,
            "bytes": file.stat().st_size,
            "sha256": sha256(file),
        }
        manifest.append(entry)
        print(f"  {entry['file']}: {entry['bytes']:,} bytes  {entry['sha256'][:16]}...")

    (DATA_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"{len(files)} CSV files recorded in data/manifest.json")
    if len(files) != 9:
        raise SystemExit(f"Expected 9 CSV files, found {len(files)}")


if __name__ == "__main__":
    main()
