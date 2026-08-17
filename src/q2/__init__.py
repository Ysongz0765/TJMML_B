"""Question 2: scenario-specific KL-CES utility evaluation.

This package is deliberately independent from ``src.q1``.  Q1 communicates
with Q2 only through the documented tabular interface in ``data/q2``.
"""

from .config import ABILITY_COLUMNS, EPS, SCENES
from .pipeline import Q2PipelineResult, build_q2_pipeline

__all__ = [
    "ABILITY_COLUMNS",
    "EPS",
    "SCENES",
    "Q2PipelineResult",
    "build_q2_pipeline",
]
