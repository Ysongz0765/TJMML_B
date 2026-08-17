# Q3 Reproducibility Audit

The frozen input files under `q3/frozen/v1.0/` were copied to an isolated
temporary root and executed through the Q3 runner and final-output
formatter. No current working-tree input was used by the isolated run.

`Q3_REPRODUCIBILITY_AUDIT = PASS`

| Final table | Rows | Row count | Columns | Keys | Max abs diff | Max rel diff |
|---|---:|---|---|---|---:|---:|
| `scenario_costs_final.csv` | 30 | True | True | True | 0 | 0 |
| `pareto_results_final.csv` | 24 | True | True | True | 0 | 0 |
| `budget_switch_points_final.csv` | 12 | True | True | True | 0 | 0 |
| `icer_results_final.csv` | 9 | True | True | True | 0 | 0 |
| `cost_performance_fit_final.csv` | 16 | True | True | True | 0 | 0 |
| `sensitivity_summary_final.csv` | 9 | True | True | True | 0 | 0 |
| `pareto_probability_final.csv` | 24 | True | True | True | 0 | 0 |
