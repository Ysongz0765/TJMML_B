import math

import pandas as pd

from cost_performance_fit import fit_cost_performance
from incremental_cost import compute_icer


def test_icer_handles_zero_delta_utility():
    pareto = pd.DataFrame(
        [
            {"scenario": "S", "model_id": "a", "utility": 10, "cost": 1, "pareto": True},
            {"scenario": "S", "model_id": "b", "utility": 10, "cost": 2, "pareto": True},
        ]
    )
    result = compute_icer(pareto)
    assert math.isinf(result.loc[0, "icer"])


def test_cost_performance_fit_reports_aicc_and_loocv():
    df = pd.DataFrame(
        [
            {"scenario": "S", "model_id": "a", "utility": 10, "cost": 1},
            {"scenario": "S", "model_id": "b", "utility": 15, "cost": 2},
            {"scenario": "S", "model_id": "c", "utility": 18, "cost": 3},
            {"scenario": "S", "model_id": "d", "utility": 20, "cost": 4},
        ]
    )
    result = fit_cost_performance(df)
    assert {"linear", "log"}.issubset(set(result["fit_model"]))
    assert "aicc" in result.columns
    assert "loocv_error" in result.columns

