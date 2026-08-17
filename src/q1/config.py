from __future__ import annotations

import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FROZEN_DIR = ROOT / "frozen" / "v1.0"
OUTPUT_DIR = ROOT / "outputs" / "q1"
TABLE_DIR = OUTPUT_DIR / "tables"
FIGURE_DIR = OUTPUT_DIR / "figures"
DIAG_DIR = OUTPUT_DIR / "diagnostics"
BOOT_DIR = OUTPUT_DIR / "bootstrap"
LOG_DIR = OUTPUT_DIR / "logs"

FREEZE_VERSION = "v1.0"
FREEZE_DATE = "2026-08-17"
RANDOM_SEED = 20260817
MAIN_LAMBDA = 1.0
LAMBDA_GRID = [0.1, 0.3, 1.0, 3.0, 10.0]
MARGIN_EPSILON = 0.1
REDUNDANCY_THRESHOLDS = [0.80, 0.85, 0.90]
DEFAULT_BOOTSTRAP_B = int(os.environ.get("Q1_BOOTSTRAP_B", "2000"))

CORE_MODELS = [
    "kimi_k3_max",
    "gpt_5_6_sol_max",
    "gpt_5_5_xhigh",
    "claude_fable_5_max",
    "claude_opus_4_8_max",
    "gemini_3_1_pro_high",
    "deepseek_v4_pro_max",
    "deepseek_v4_flash_max",
    "qwen3_8_max",
    "glm_5_2_max",
]

KIMI_MODEL_ID = "kimi_k3_max"


def ensure_output_dirs() -> None:
    for path in [OUTPUT_DIR, TABLE_DIR, FIGURE_DIR, DIAG_DIR, BOOT_DIR, LOG_DIR]:
        path.mkdir(parents=True, exist_ok=True)

