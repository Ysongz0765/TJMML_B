import pandas as pd

from cost_model import compute_all_costs, compute_scenario_cost


def test_compute_scenario_cost_hand_calculation():
    result = compute_scenario_cost(
        {"input_price": 2.0, "output_price": 10.0},
        {"n_calls": 100, "input_tokens": 1000, "output_tokens": 200},
    )
    assert result["input_cost"] == 0.2
    assert result["output_cost"] == 0.2
    assert result["cost"] == 0.4


def test_compute_all_costs_preserves_missing_prices():
    pricing = pd.DataFrame([{"model_id": "m1", "model_name": "M1", "input_price": "NA", "output_price": 2.0}])
    workload = pd.DataFrame([{"scenario": "Research", "workload_level": "baseline_template", "n_calls": 1, "input_tokens": 1000, "output_tokens": 1000}])
    result = compute_all_costs(pricing, workload)
    assert pd.isna(result.loc[0, "cost"])

