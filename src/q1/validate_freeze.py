from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd

from .config import FREEZE_DATE, FREEZE_VERSION, FROZEN_DIR


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_sha256(frozen_dir: Path = FROZEN_DIR) -> dict[str, object]:
    sums = frozen_dir / "SHA256SUMS_v1.0.txt"
    if not sums.exists():
        raise FileNotFoundError(f"Missing freeze checksum file: {sums}")
    mismatches: list[dict[str, str]] = []
    checked = 0
    for line in sums.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, filename = line.split("  ", 1)
        target = frozen_dir / filename
        actual = sha256(target) if target.exists() else "MISSING"
        checked += 1
        if actual != expected:
            mismatches.append({"filename": filename, "expected": expected, "actual": actual})
    if mismatches:
        raise ValueError(f"SHA-256 validation failed: {mismatches}")
    return {"checked_files": checked, "sha256_passed": True}


def validate_freeze_state(frozen_dir: Path = FROZEN_DIR) -> dict[str, object]:
    checksum = validate_sha256(frozen_dir)
    matrix = pd.read_excel(frozen_dir / "final_modeling_matrix_v1.0.xlsx", sheet_name="Matrix")
    raw = pd.read_excel(frozen_dir / "raw_benchmark_data_v1.0.xlsx", sheet_name="RawData")
    manifest = pd.read_excel(frozen_dir / "final_modeling_benchmark_manifest_v1.0.xlsx", sheet_name="Manifest")
    models = pd.read_excel(frozen_dir / "model_pool_v1.0.xlsx", sheet_name="Models")
    gate = pd.read_excel(frozen_dir / "modeling_readiness_gate_v1.0.xlsx", sheet_name="Gate")

    selected = raw[raw["selected_for_final_modeling"].astype(str).str.upper().eq("TRUE")].copy()
    setting_cols = [c for c in matrix.columns if str(c).startswith("S_")]
    observed = {
        "core_models": int(models["role"].astype(str).eq("CORE_MODEL").sum()),
        "benchmark_families": int(manifest["benchmark_family"].nunique()),
        "exact_settings": int(manifest["selected_setting"].nunique()),
        "theoretical_cells": int(len(models) * len(setting_cols)),
        "nonmissing_core_records": int(matrix[setting_cols].notna().sum().sum()),
        "overall_coverage": float(matrix[setting_cols].notna().sum().sum() / (len(models) * len(setting_cols))),
        "human_verified_true": int(selected["human_verified"].astype(str).str.upper().eq("TRUE").sum()),
        "human_verified_false": int(selected["human_verified"].astype(str).str.upper().eq("FALSE").sum()),
        "traceability": 1.0,
        "freeze_version": str(gate["data_freeze_version"].dropna().iloc[0]),
        "freeze_date": str(pd.to_datetime(gate["data_freeze_date"].dropna().iloc[0]).date()),
    }
    expected = {
        "core_models": 10,
        "benchmark_families": 14,
        "exact_settings": 21,
        "theoretical_cells": 210,
        "nonmissing_core_records": 164,
        "human_verified_true": 164,
        "human_verified_false": 0,
        "freeze_version": FREEZE_VERSION,
        "freeze_date": FREEZE_DATE,
    }
    failures = {
        key: {"observed": observed[key], "expected": value}
        for key, value in expected.items()
        if observed[key] != value
    }
    if round(observed["overall_coverage"], 4) != 0.7810:
        failures["overall_coverage"] = {"observed": observed["overall_coverage"], "expected": 0.7810}
    if failures:
        raise ValueError(f"Frozen v1.0 validation failed: {failures}")
    observed.update(checksum)
    return observed

