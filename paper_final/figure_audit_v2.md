# Figure Audit v2

## Referenced figures in the final PDF

| figure | source | script |
| --- | --- | --- |
| `fig_framework` | `paper_final/figures/fig_framework.*` | `scripts/plotting/framework_figure.py` |
| `fig_q1_coverage` | `frozen/v1.0/final_modeling_matrix_v1.0.csv` | `scripts/plotting/q1_figures.py` |
| `fig_q1_spearman` | `outputs/stage3_llm_benchmark/spearman_missing_aware.xlsx` | `scripts/plotting/q1_figures.py` |
| `fig_q1_radar_ranking` | `q2/data/q1_capability_scores.csv`, `outputs/q1_v1.2/tables/paper_table_q1_v12_bootstrap.xlsx` | `scripts/plotting/q1_figures.py` |
| `fig_q1_rank_stability` | `outputs/q1_v1.2/bootstrap/bootstrap_ranking_A_v1.2.csv` | `scripts/plotting/q1_figures.py` |
| `fig_q1_robustness` | `outputs/q1_v1.2/sensitivity/lofo_summary_v1.2.csv` | `scripts/plotting/q1_figures.py` |
| `fig_q2_weight_matrix` | `q3/data/q2_to_q3_interface.md` | `scripts/plotting/q2_figures.py` |
| `fig_q2_utility_panels` | `q3/frozen/v1.0/scenario_utility.csv` | `scripts/plotting/q2_figures.py` |
| `fig_q2_rank_migration` | `outputs/q1_v1.2/tables/paper_table_q1_v12_bootstrap.xlsx`, `q3/frozen/v1.0/scenario_utility.csv` | `scripts/plotting/q2_figures.py` |
| `fig_q2_rho_sensitivity` | `q2/data/q1_bt_latent_scores.csv`, `q3/data/scenario_utility.csv`, `q3/data/q2_to_q3_interface.md` | `scripts/plotting/q2_figures.py` |
| `fig_q3_cost_components` | `q3/frozen/v1.0/scenario_costs_final.csv` | `scripts/plotting/q3_figures.py` |
| `fig_q3_pareto` | `q3/frozen/v1.0/pareto_results_final.csv`, `q3/frozen/v1.0/pareto_probability_final.csv` | `scripts/plotting/q3_figures.py` |
| `fig_q3_budget_steps` | `q3/frozen/v1.0/budget_switch_points_final.csv` | `scripts/plotting/q3_figures.py` |

## Replaced or archival figures

- `fig_q2_demand_utility` and `fig_q3_workload` remain in `paper_final/figures/` as archival outputs, but they are no longer referenced by `main.tex`.
- `fig_q1_radar_ranking` was refreshed on 2026-08-18 with a tighter crop of the user-provided source image, keeping the plot body, legend, and x-axis label while removing the original embedded caption/note block.

## Color and style compliance

- All manuscript figures use the unified low-saturation palette from `scripts/plotting/style.py`.
- No manuscript figure relies on default tab10, rainbow, jet, or saturated red/orange/green palettes.

## QA

- PNG previews checked for Q1, Q2, and Q3 figures.
- Page 1, 6, 10, 14, and 15 of the final PDF were visually inspected after compilation.
