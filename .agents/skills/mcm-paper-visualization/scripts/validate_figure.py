"""Lightweight figure artifact validator."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    files = list(args.directory.glob("*"))
    if not files:
        raise SystemExit(f"No figure files found: {args.directory}")
    for suffix in (".pdf", ".svg", ".png"):
        matches = [p for p in files if p.suffix.lower() == suffix]
        if not matches:
            raise SystemExit(f"Missing {suffix} export in {args.directory}")
        if any(p.stat().st_size == 0 for p in matches):
            raise SystemExit(f"Empty {suffix} export in {args.directory}")
    for png in (p for p in files if p.suffix.lower() == ".png"):
        with Image.open(png) as image:
            if image.width < 900 or image.height < 600:
                raise SystemExit(f"PNG is too small for paper QA: {png} -> {image.size}")
    print(f"Validated {len(files)} figure artifacts in {args.directory}")


if __name__ == "__main__":
    main()
