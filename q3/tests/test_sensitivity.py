import pandas as pd

from sensitivity_analysis import input_scale_sensitivity, price_perturbation_sensitivity, ratio_sensitivity


def _fixtures():
    pricing = pd.DataFrame(
        [
            {"model_id": "a", "model_name": "A", "input_price": 1.0, "output_price": 2.0},
            {"model_id": "b", "model_name": "B", "input_price": 2.0, "output_price": 1.0},
        ]
    )
    workload = pd.DataFrame([{"scenario": "S", "workload_level": "baseline_template", "n_calls": 1, "input_tokens": 1000, "output_tokens": 1000}])
    utility = pd.DataFrame([{"model_id": "a", "scenario": "S", "utility": 10}, {"model_id": "b", "scenario": "S", "utility": 11}])
    return pricing, workload, utility


def test_input_scale_sensitivity_dimensions():
    pricing, workload, utility = _fixtures()
    result = input_scale_sensitivity(pricing, workload, utility, scales=(1.0, 2.0))
    assert set(result["parameter"].dropna()) >= {1.0, 2.0}
    assert {"analysis", "scenario", "model_id", "cost", "utility"}.issubset(result.columns)


def test_ratio_sensitivity_changes_cost_order_when_prices_cross():
    pricing, workload, utility = _fixtures()
    result = ratio_sensitivity(pricing, workload, utility, ratios=(0.1, 10.0))
    low = result[(result.analysis == "input_output_ratio") & (result.parameter == 0.1)].sort_values("cost")["model_id"].tolist()[0]
    high = result[(result.analysis == "input_output_ratio") & (result.parameter == 10.0)].sort_values("cost")["model_id"].tolist()[0]
    assert low != high


def test_price_perturbation_preserves_rows():
    pricing, workload, utility = _fixtures()
    result = price_perturbation_sensitivity(pricing, workload, utility, deltas=(-0.1, 0.0, 0.1))
    assert set(result["parameter"].dropna()) >= {-0.1, 0.0, 0.1}
    assert len(result) > 0

