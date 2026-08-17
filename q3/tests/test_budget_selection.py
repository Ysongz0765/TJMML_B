import math

import pandas as pd

from budget_selection import compute_budget_frontier


def test_budget_below_all_models_has_no_feasible_interval():
    df = pd.DataFrame(
        [
            {"scenario": "S", "model_id": "a", "model_name": "A", "utility": 10, "cost": 5},
            {"scenario": "S", "model_id": "b", "model_name": "B", "utility": 12, "cost": 8},
        ]
    )
    result = compute_budget_frontier(df)
    first = result.iloc[0]
    assert first["budget_lower"] == 0
    assert first["budget_upper"] == 5
    assert first["optimal_model_id"] == "NO_FEASIBLE_MODEL"


def test_budget_exactly_at_model_cost_is_feasible():
    df = pd.DataFrame([{"scenario": "S", "model_id": "a", "model_name": "A", "utility": 10, "cost": 5}])
    result = compute_budget_frontier(df)
    row = result[result["budget_lower"] == 5].iloc[0]
    assert row["optimal_model_id"] == "a"


def test_two_feasible_models_choose_higher_utility_then_lower_cost():
    df = pd.DataFrame(
        [
            {"scenario": "S", "model_id": "a", "model_name": "A", "utility": 10, "cost": 5},
            {"scenario": "S", "model_id": "b", "model_name": "B", "utility": 12, "cost": 8},
        ]
    )
    result = compute_budget_frontier(df)
    row = result[result["budget_lower"] == 8].iloc[0]
    assert row["optimal_model_id"] == "b"
    assert math.isinf(row["budget_upper"])


def test_infinite_budget_keeps_best_model():
    df = pd.DataFrame(
        [
            {"scenario": "S", "model_id": "a", "model_name": "A", "utility": 10, "cost": 1},
            {"scenario": "S", "model_id": "b", "model_name": "B", "utility": 9, "cost": 100},
        ]
    )
    result = compute_budget_frontier(df)
    last = result.iloc[-1]
    assert math.isinf(last["budget_upper"])
    assert last["optimal_model_id"] == "a"

