# Q2 data provenance

| Q1 source file | Q2 output file | transformation | numerical values changed |
| --- | --- | --- | --- |
| `outputs/q1_v1.2/results_summary_v1.2.json` and frozen BT inputs | `data/q1_capability_scores.csv` | direct export of Q1 v1.2 scores plus C5* applicability separation | no, except explicit C5* availability field copied from Q1 Ranking A rule |
| frozen BT inputs and Q1 v1.2 BT code path | `data/q1_bt_latent_scores.csv` | read-only reconstruction of main regularized BT theta | no new scaling or imputation |
| `outputs/q1_v1.2/results_summary_v1.2.json` C5 audit and frozen selected benchmark rows | `data/q1_model_applicability.csv` | status normalization and direct observation counts | no benchmark scores changed |
| `outputs/q1_v1.2/results_summary_v1.2.json` rankings | `data/q1_model_rankings.csv` | direct export | no |
| `outputs/q1_v1.2/bootstrap/*.csv` | `data/q1_uncertainty.csv` | grouped bootstrap summary statistics and percentile intervals | summary statistics only |
| `outputs/q1_v1.2/results_summary_v1.2.json` weights | `data/q1_dimension_weights_reference.csv` | direct export of Ranking A reference weights and components | no |
| `frozen/v1.0/final_modeling_benchmark_manifest_v1.0.csv` | `data/benchmark_family_mapping.csv` | selected fields copied and joined to source type/title | no |
| `frozen/v1.0/source_registry_v1.0.csv` | `data/source_registry_summary.csv` | selected fields copied and renamed | no |
| frozen selected benchmark rows | `data/q1_evidence_strength.csv` | direct counts by model and dimension plus rule-based category | no benchmark scores changed |
| Q2 CSV files | `data/q2_model_master_table.xlsx` | one-row-per-model merge for Q2 interface convenience | no |
