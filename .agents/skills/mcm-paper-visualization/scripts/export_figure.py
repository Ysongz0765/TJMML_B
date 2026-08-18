"""Run a source-data plotting script; do not accept raster-derived inputs."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--script", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("figures"))
    args = parser.parse_args()

    namespace = {"OUTPUT_DIR": args.output_dir}
    exec(compile(args.script.read_text(encoding="utf-8"), str(args.script), "exec"), namespace)
    plt.close("all")


if __name__ == "__main__":
    main()
