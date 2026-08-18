"""Generate all integrated-paper figures."""

from __future__ import annotations

from pathlib import Path
import argparse

from framework_figure import main as framework_main
from q1_figures import main as q1_main
from q2_figures import main as q2_main
from q3_figures import main as q3_main


def main(output_dir: Path) -> None:
    framework_main(output_dir)
    q1_main(output_dir)
    q2_main(output_dir)
    q3_main(output_dir)
    print(f"Generated integrated figures in {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("paper_final") / "figures")
    main(parser.parse_args().output_dir)
