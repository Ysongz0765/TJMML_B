# Paper Audit

## Key findings

1. Q1 coverage is 164/210 = 78.10% from `frozen/v1.0/final_modeling_matrix_v1.0.csv`.
2. Q1 Ranking A top three are GPT-5.6 Sol (80.498), Claude Fable 5 (70.822), and Kimi K3 (53.720) from `outputs/q1_v1.2/tables/paper_table_q1_v12_bootstrap.xlsx`.
3. Q2 nominal scene utilities come from frozen interface data in `q3/data/scenario_utility.csv`, synced byte-for-byte from `origin/q2-final-paper`.
4. Q3 strict main Pareto uses the FULL cohort from `q3/frozen/v1.0/scenario_costs_final.csv` and `q3/frozen/v1.0/pareto_results_final.csv`.
5. The final decision logic is ordered as capability, scene utility, then cost-constrained Pareto choice.
6. Bootstrap provenance and alignment checks are recorded in `paper_final/bootstrap_provenance_audit.md`.

## Figure audit

| figure | data source | script |
| --- | --- | --- |
| `fig_q1_coverage` | `frozen/v1.0/final_modeling_matrix_v1.0.csv` | `scripts/plotting/q1_figures.py` |
| `fig_q1_spearman` | `outputs/stage3_llm_benchmark/spearman_missing_aware.xlsx` | `scripts/plotting/q1_figures.py` |
| `fig_q1_radar_ranking` | `q2/data/q1_capability_scores.csv`, `outputs/q1_v1.2/tables/paper_table_q1_v12_bootstrap.xlsx` | `scripts/plotting/q1_figures.py` |
| `fig_q1_rank_stability` | `outputs/q1_v1.2/bootstrap/bootstrap_ranking_A_v1.2.csv` | `scripts/plotting/q1_figures.py` |
| `fig_q1_robustness` | `outputs/q1_v1.2/sensitivity/lofo_summary_v1.2.csv` | `scripts/plotting/q1_figures.py` |
| `fig_q2_demand_utility` | `q3/data/q2_to_q3_interface.md`, `q3/frozen/v1.0/scenario_utility.csv` | `scripts/plotting/q2_figures.py` |
| `fig_q2_rank_migration` | `outputs/q1_v1.2/tables/paper_table_q1_v12_bootstrap.xlsx`, `q3/frozen/v1.0/scenario_utility.csv` | `scripts/plotting/q2_figures.py` |
| `fig_q2_rho_sensitivity` | `q2/data/q1_bt_latent_scores.csv`, `q3/data/scenario_utility.csv`, `q3/data/q2_to_q3_interface.md` | `scripts/plotting/q2_figures.py` |
| `fig_q3_cost_components` | `q3/frozen/v1.0/scenario_costs_final.csv` | `scripts/plotting/q3_figures.py` |
| `fig_q3_pareto` | `q3/frozen/v1.0/pareto_results_final.csv`, `q3/frozen/v1.0/pareto_probability_final.csv` | `scripts/plotting/q3_figures.py` |
| `fig_q3_workload` | `q3/frozen/v1.0/workload_config.csv`, `q3/frozen/v1.0/model_pricing.csv` | `scripts/plotting/q3_figures.py` |

## Frozen-data usage

- Q1 frozen outputs were used as read-only inputs.
- Q2 nominal utilities were read from the frozen Q2-to-Q3 interface; the rho-sensitivity plot now recomputes on the frozen latent scale and is anchored to the same nominal utility values.
- Q3 cost and Pareto tables were read from `q3/frozen/v1.0/` only.

## Q1 -> Q2 interface

- Capability scores: `q2/data/q1_capability_scores.csv`
- Latent theta: `q2/data/q1_bt_latent_scores.csv`
- Uncertainty: `q2/data/q1_uncertainty.csv`
- Scene mapping: `q2/metadata/q1_to_q2_mapping.md`

## Q2 -> Q3 interface

- Nominal utility: `q3/data/scenario_utility.csv`
- Bootstrap utility: `q3/data/scenario_utility_bootstrap.csv`
- Contract: `q3/data/q2_to_q3_interface.md`
- Scene weights are frozen constants in the interface contract; `scripts/plotting/q2_figures.py` parses the same contract read-only and `q3/src/run_q3.py` only validates the resulting utility table.

## Unresolved issues

- No blocking unresolved issue remains for paper compilation.
- Known non-blocking limitation: Claude Fable fallback and GLM-5.2 pricing remain partial or missing in the Q3 cost audit, so they are excluded from the strict main cost Pareto by design.

## Build status

- `mcm-paper-visualization` skill validated successfully.
- `main.tex` compiled successfully with XeLaTeX twice after the Q2 rho-sensitivity fix.
- `scripts/plotting/validate.py paper_final/figures` passed on 11 figure sets.
- Final PDF rendered to 12 pages.
- Final PDF artifact: `paper_final/final_paper.pdf`
