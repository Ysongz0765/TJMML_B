"""Validate integrated-paper figure artifacts."""

from __future__ import annotations

from pathlib import Path
import argparse

from PIL import Image


def main(directory: Path) -> None:
    stems = sorted({p.stem for p in directory.iterdir() if p.suffix in {".pdf", ".svg", ".png"}})
    stems = [stem for stem in stems if not stem.startswith("crop")]
    if not stems:
        raise SystemExit(f"No figure outputs found in {directory}")
    errors = []
    for stem in stems:
        for suffix in (".pdf", ".svg", ".png"):
            p = directory / f"{stem}{suffix}"
            if not p.exists() or p.stat().st_size == 0:
                errors.append(f"missing or empty: {p}")
        png = directory / f"{stem}.png"
        if png.exists():
            with Image.open(png) as image:
                if image.width < 900 or image.height < 500:
                    errors.append(f"small PNG: {png} {image.size}")
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"Validated {len(stems)} figures in {directory}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path, nargs="?", default=Path("paper_final") / "figures")
    main(parser.parse_args().directory)
