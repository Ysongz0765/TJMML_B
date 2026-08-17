import pandas as pd

from pareto_analysis import compute_pareto_frontier


def test_obvious_dominance():
    df = pd.DataFrame(
        [
            {"scenario": "S", "model_id": "a", "utility": 10, "cost": 5},
            {"scenario": "S", "model_id": "b", "utility": 9, "cost": 6},
        ]
    )
    result = compute_pareto_frontier(df)
    assert result[result.model_id == "a"].iloc[0]["pareto"] == True
    assert result[result.model_id == "b"].iloc[0]["pareto"] == False


def test_identical_points_are_both_pareto():
    df = pd.DataFrame(
        [
            {"scenario": "S", "model_id": "a", "utility": 10, "cost": 5},
            {"scenario": "S", "model_id": "b", "utility": 10, "cost": 5},
        ]
    )
    result = compute_pareto_frontier(df)
    assert result["pareto"].tolist() == [True, True]


def test_all_pareto_tradeoff():
    df = pd.DataFrame(
        [
            {"scenario": "S", "model_id": "a", "utility": 8, "cost": 1},
            {"scenario": "S", "model_id": "b", "utility": 10, "cost": 2},
        ]
    )
    result = compute_pareto_frontier(df)
    assert result["pareto"].tolist() == [True, True]


def test_single_model_is_pareto():
    df = pd.DataFrame([{"scenario": "S", "model_id": "a", "utility": 8, "cost": 1}])
    result = compute_pareto_frontier(df)
    assert result.loc[0, "pareto"] == True


def test_missing_values_are_not_zero():
    df = pd.DataFrame(
        [
            {"scenario": "S", "model_id": "a", "utility": 8, "cost": 1},
            {"scenario": "S", "model_id": "b", "utility": None, "cost": 0},
        ]
    )
    result = compute_pareto_frontier(df)
    assert result[result.model_id == "b"].iloc[0]["pareto"] == False
    assert result[result.model_id == "b"].iloc[0]["pareto_status_note"] == "missing utility or cost"
