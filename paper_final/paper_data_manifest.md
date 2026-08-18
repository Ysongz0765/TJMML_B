# Paper Data Manifest

## Q1

| conclusion / figure | data source | notes |
| --- | --- | --- |
| 164/210 coverage | `frozen/v1.0/final_modeling_matrix_v1.0.csv` | 10 models x 21 settings, 164 valid cells |
| Missing-aware Spearman heatmap | `outputs/stage3_llm_benchmark/spearman_missing_aware.xlsx` | sheet `Rho` |
| Five-dimensional radar | `q2/data/q1_capability_scores.csv` | C1--C5 scores |
| Ranking A CI panel | `outputs/q1_v1.2/tables/paper_table_q1_v12_bootstrap.xlsx` | sheet `Ranking_A` |
| Rank stability heatmap | `outputs/q1_v1.2/bootstrap/bootstrap_ranking_A_v1.2.csv` | 2,000 bootstrap draws |
| LOFO robustness | `outputs/q1_v1.2/sensitivity/lofo_summary_v1.2.csv` | Spearman and overlap diagnostics |
| Ranking A weights | `q2/data/q1_dimension_weights_reference.csv` | objective weights reference only |

## Q2

| conclusion / figure | data source | notes |
| --- | --- | --- |
| Scenario demand weights | `q3/data/q2_to_q3_interface.md` | frozen KL-projected scene weights parsed verbatim |
| Scenario weight matrix | `q3/data/q2_to_q3_interface.md` | `fig_q2_weight_matrix`, same interface contract |
| Scenario utility panels | `q3/data/scenario_utility.csv` | nominal utility values; byte-for-byte synced from the frozen Q2 handoff |
| Ranking migration | `q3/data/scenario_utility.csv`, `outputs/q1_v1.2/tables/paper_table_q1_v12_bootstrap.xlsx` | Q1 rank + Q2 scene rank |
| CES sensitivity | `q2/data/q1_bt_latent_scores.csv`, `q3/data/scenario_utility.csv`, `q3/data/q2_to_q3_interface.md` | nominal Q2 utility is preserved; rho sweep is recomputed on the frozen latent scale |

## Q3

| conclusion / figure | data source | notes |
| --- | --- | --- |
| Cost decomposition | `q3/frozen/v1.0/scenario_costs_final.csv` | strict FULL cohort, Code scene shown |
| Pareto frontiers | `q3/frozen/v1.0/pareto_results_final.csv` | scene-wise frozen frontier |
| Pareto probabilities | `q3/frozen/v1.0/pareto_probability_final.csv` | bootstrap frontier probability |
| Budget switch points | `q3/frozen/v1.0/budget_switch_points_final.csv` | `fig_q3_budget_steps`; thresholds read directly from frozen results |
| Sensitivity summary | `q3/frozen/v1.0/sensitivity_summary_final.csv` | retained membership stability |

## Interface chain

- Q1 output to Q2 input: `q2/data/q1_capability_scores.csv`, `q2/data/q1_bt_latent_scores.csv`, `q2/data/q1_uncertainty.csv`.
- Q2 output to Q3 input: `q3/data/scenario_utility.csv`, `q3/data/scenario_utility_bootstrap.csv`, `q3/data/q2_to_q3_interface.md`.
- Q3 cost inputs: `q3/frozen/v1.0/model_pricing.csv`, `q3/frozen/v1.0/workload_config.csv`.
