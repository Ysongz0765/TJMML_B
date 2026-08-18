"""Shared style entry point for the repo-local visualization skill."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
PLOTTING = ROOT / "scripts" / "plotting"
if str(PLOTTING) not in sys.path:
    sys.path.insert(0, str(PLOTTING))

from style import *  # noqa: F401,F403
