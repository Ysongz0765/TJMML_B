"""Central configuration for the Q2 KL-CES model.

All numerical scenario assumptions live here.  The ranges are development
defaults for sensitivity analysis, not frozen competition conclusions.
"""

from __future__ import annotations

from dataclasses import dataclass


ABILITY_COLUMNS = ("C1", "C2", "C3", "C4", "C5")
ABILITY_LABELS = {
    "C1": "复杂推理能力",
    "C2": "知识与事实可靠性",
    "C3": "长上下文处理能力",
    "C4": "代码与软件工程能力",
    "C5": "多模态能力",
}

EPS = 1e-6
BASE_WEIGHT_SOURCE = "Q1_FINAL"
Q1_FINALIZED = False
TENTATIVE_PARAMETER_RANGE = True
DEFAULT_ALPHA_GRID_SIZE = 9
DEFAULT_RHO_GRID_SIZE = 9
OPTIMIZER_TOLERANCE = 1e-10
CONSTRAINT_TOLERANCE = 1e-8


@dataclass(frozen=True)
class SceneConfig:
    """Parameterised demand system for one application scene."""

    key: str
    label: str
    core_dimensions: tuple[str, ...]
    alpha_range: tuple[float, float]
    alpha_development_default: float
    rho_range: tuple[float, float]
    rho_development_default: float
    lower_bounds: tuple[tuple[str, float], ...] = ()
    order_constraints: tuple[tuple[str, str], ...] = ()


SCENES: dict[str, SceneConfig] = {
    "research": SceneConfig(
        key="research",
        label="科研长文本分析",
        core_dimensions=("C3", "C1", "C2"),
        alpha_range=(0.55, 0.75),
        alpha_development_default=0.65,
        rho_range=(-0.60, 0.20),
        rho_development_default=-0.20,
        order_constraints=(("C3", "C4"), ("C1", "C5"), ("C2", "C4")),
    ),
    "dialogue": SceneConfig(
        key="dialogue",
        label="大众日常通用对话",
        core_dimensions=("C1", "C2", "C5"),
        alpha_range=(0.50, 0.70),
        alpha_development_default=0.60,
        rho_range=(0.10, 0.80),
        rho_development_default=0.45,
        lower_bounds=(("C2", 0.15),),
        order_constraints=(("C2", "C4"), ("C1", "C4"), ("C5", "C4")),
    ),
    "coding": SceneConfig(
        key="coding",
        label="计算机代码开发",
        core_dimensions=("C4", "C1"),
        alpha_range=(0.55, 0.75),
        alpha_development_default=0.65,
        rho_range=(-0.70, 0.20),
        rho_development_default=-0.25,
        lower_bounds=(("C4", 0.30),),
        order_constraints=(("C4", "C2"), ("C4", "C3"), ("C1", "C5")),
    ),
}


def equal_reference(dimensions: tuple[str, ...] = ABILITY_COLUMNS) -> dict[str, float]:
    """Return the equal-weight robustness prior on the requested dimensions."""

    if not dimensions:
        raise ValueError("At least one ability dimension is required.")
    value = 1.0 / len(dimensions)
    return {dimension: value for dimension in dimensions}
