# Q3 Repository Audit

## 1. Current repository structure

- Q1 frozen data and final modeling artifacts exist under `frozen/v1.0/`, `data/final/`, `data/processed/`, `outputs/q1*`, `reports/`, and `submission_support/`.
- Q2 interface data live under `q2/data/` with supporting metadata in `q2/metadata/` and generation scripts in `q2/scripts/`.
- Q3 is newly isolated under `q3/`.

## 2. Q1 frozen outputs already available

- Frozen benchmark manifest, raw benchmark data, final modeling matrix, model pool, readiness gate, source registry, and freeze manifest are present in `frozen/v1.0/`.
- Q1 final outputs include bootstrap summaries, ranking tables, dimension weights, LOFO/LOSO robustness, and figure sets in `outputs/q1/`, `outputs/q1_v1.1/`, and `outputs/q1_v1.2/`.

## 3. Q2 files already present

- `q2/data/q1_capability_scores.csv`
- `q2/data/q1_bt_latent_scores.csv`
- `q2/data/q1_model_applicability.csv`
- `q2/data/q1_model_rankings.csv`
- `q2/data/q1_uncertainty.csv`
- `q2/data/q1_dimension_weights_reference.csv`
- `q2/data/q1_evidence_strength.csv`
- `q2/data/benchmark_family_mapping.csv`
- `q2/data/source_registry_summary.csv`
- `q2/data/q2_model_master_table.csv`
- `q2/README_Q2_DATA.md`
- `q2/metadata/q1_to_q2_mapping.md`
- `q2/metadata/q2_data_dictionary.md`
- `q2/metadata/q2_data_provenance.md`

## 4. Formal Q2 scenario utility data

- No formal `scenario_utility.csv` or equivalent scenario utility output exists in the repository.
- Only a template has been created in `q3/data/scenario_utility_template.csv`.

## 5. Unified model_id and model name set

The 10 core Q2/Q3-compatible models are:

- `kimi_k3_max` - Kimi K3 (max reasoning)
- `gpt_5_6_sol_max` - GPT-5.6 Sol (max)
- `gpt_5_5_xhigh` - GPT-5.5 (xhigh)
- `claude_fable_5_max` - Claude Fable 5 (max, with fallback)
- `claude_opus_4_8_max` - Claude Opus 4.8 (max)
- `gemini_3_1_pro_high` - Gemini-3.1-Pro (High)
- `deepseek_v4_pro_max` - DeepSeek-V4-Pro Max
- `deepseek_v4_flash_max` - DeepSeek-V4-Flash Max
- `qwen3_8_max` - Qwen3.8-Max
- `glm_5_2_max` - GLM-5.2 (max)

## 6. Fields directly usable by Q3

- `model_id`, `model`, Q1 capability scores, latent theta values, applicability flags, ranking outputs, uncertainty summaries, evidence counts, and the one-row-per-model master table from Q2.
- These are suitable for joins, validation, and scenario utility ingestion.

## 7. Missing Q3 inputs

- Formal Q2 scenario utility values for Research / General / Coding.
- Human-verified exact pricing for each model/version.
- Final workload assumptions with provenance.

## 8. Naming consistency issues

- The core 10 `model_id` values are consistent across Q2 files.
- Human-readable names are mostly stable, but some exact-version labels are future-specific and must be matched carefully in the pricing table.

## 9. Duplicate / version / case issues

- No duplicate `model_id` values were observed in the core Q2 interface tables.
- Version naming is strict and should not be collapsed into a generic family label.
- Case differences are minor but should be normalized by `model_id`, not by display name.

## 10. Frozen vs intermediate files

- Formal frozen data: `frozen/v1.0/*`.
- Formal Q1 outputs: `outputs/q1*` and `reports/*`.
- Q2 interface data: `q2/data/*` and `q2/metadata/*`.
- Q3 templates and framework: `q3/*`.
- Intermediate or reproducible derivation material: `data/processed/*`, `submission_support/*`, and some workbook previews and payloads under `outputs/*`.

