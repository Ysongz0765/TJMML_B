# Q2 standardized input datasets

This directory is a Q2 data interface prepared from Q1 frozen data and Q1 v1.2 official outputs.

## Data source

All files here are derived from:

- `frozen/v1.0/`
- `outputs/q1_v1.2/`

No benchmark was re-fetched, no Q1 ranking was changed, and no missing benchmark or latent score was imputed.

## Primary Q1 capability inputs

Q2 should primarily read the model capability profile:

- `data/q1_capability_scores.csv`
- `data/q1_bt_latent_scores.csv`
- `data/q1_model_applicability.csv`
- `data/q2_model_master_table.xlsx`

`C5_BT_score` is the estimated BT multimodal score and remains missing for structural capability absence. `C5_effective_score` is the Q1 Ranking A capability-availability value `C5*`; it is 0 for DeepSeek-V4-Pro Max, DeepSeek-V4-Flash Max, and GLM-5.2 (max).

## Reference only

The following are Q1 reference outputs, not Q2 scenario weights or utilities:

- `data/q1_model_rankings.csv`
- `data/q1_dimension_weights_reference.csv`

Q1 weights are for Q1 comprehensive performance evaluation under the frozen benchmark universe. They are not Q2 scenario weights for scientific long-text analysis, daily chat, or code development.

## What Q2 must not do directly

- Do not use Q1 Ranking A overall score as the final utility value for the three Q2 application scenarios.
- Do not reuse Q1 objective weights as Q2 scenario weights.
- Do not confuse C5 structural capability absence with benchmark zero.
- Do not fill missing latent scores with 0.
- Do not treat Ranking C as applicable to non-estimable C5 models.

## File groups

- `data/`: machine-readable Q1-to-Q2 data tables.
- `metadata/`: field definitions, provenance, and candidate Q1-to-Q2 capability mapping.
- `scripts/`: generation and validation scripts for this interface.
