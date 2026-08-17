# Q3 Final Input Audit

Audit date: 2026-08-17  
Pre-run Git commit: `441f935e8bd65b1a51866a315c1af822297df4cd`

## Gate Result

`Q3_MAIN_ANALYSIS_COHORT_READY = TRUE`

The completed human review has been written back to all three formal pricing
files. The eight dynamically identified FULL rows have
`human_verified=TRUE` and `full_price_human_verified=TRUE` in each file.
Fable and GLM remain explicitly reviewed but are not full-price verified:

- `q3/data/model_pricing.csv`
- `q3/data/pricing_audit.csv`
- `q3/data/pricing_human_check.csv`

No price number, SKU, or configuration value was changed in the write-back.

## Q2 Interface

- Source branch: `origin/q2-final-paper`
- Source commit: `bff0e185510f79bd78dd190ccedc47c81b12f137`
- Freeze version: `Q2_SCENARIO_UTILITY_v1.0`
- Nominal input: 30 rows, 10 models, 3 scenarios
- Nominal duplicate keys: 0
- Nominal missing utilities: 0
- Nominal unknown model IDs: 0
- Nominal scenarios: Research, General, Coding
- Bootstrap input: 60,000 rows, 2,000 draws
- Bootstrap duplicate keys: 0
- Bootstrap missing utilities: 0

The five synchronized Q2 interface hashes are recorded in
`q3/data/q2_interface_provenance.json` and match their target files.

## Pricing

- Pricing rows: 10
- Human-verified FULL rows in all three price files: 8/8
- Complete base-price rows: 9
- `FULL` cost-observability rows: 8
- FULL models: Claude Opus 4.8, DeepSeek-V4-Flash, DeepSeek-V4-Pro,
  Gemini-3.1-Pro, GPT-5.5, GPT-5.6 Sol, Kimi K3, Qwen3.8-Max
- FULL human-verified models: same 8 models
- `PARTIAL` rows: Claude Fable 5
- `MISSING` rows: GLM-5.2
- Main analysis cohort size: 8
- Price date: 2026-08-17
- Distinct non-empty price source URLs: 8
- SKU mapping: all 10 `EXACT`
- Configuration mapping: 9 `SUPPORTED_CONFIG`, 1 `FALLBACK_DEPENDENT`

Claude Fable 5 remains `PARTIAL` because fallback target and token billing are
not traceable. GLM-5.2 remains `MISSING` because an official standard
input/output API price is not observable in the checked records. No imputation
or neighboring-SKU substitution is allowed.

The exclusion of Fable and GLM is due to incomplete cost observability, not
poor performance. Fable's base price is reviewed, but its fallback target,
token, and billing trace are incomplete. GLM's SKU and configuration are
reviewed, but its public standard input/output price remains unavailable.

## Workload

The current baseline rows were read without modification:

| Scenario | N calls | Input tokens | Billable output tokens | Output/input ratio |
|---|---:|---:|---:|---:|
| Research | 1 | 16,000 | 4,000 | 0.25 |
| General | 1 | 2,000 | 1,000 | 0.50 |
| Coding | 1 | 6,000 | 6,000 | 1.00 |

`output_tokens` means billable output tokens, including reasoning/thinking
tokens when provider billing rules include them, rather than only visible
answer text.

## Final Input Decision

The final input gate is passed for the strict 8-model main cohort. The
remaining `Q3_ALL_MODELS_FULL_COST_READY=FALSE` state is expected because Fable
and GLM do not have complete observable costs. Final freeze still additionally
requires the result, reproducibility, paper-consistency, and manifest audits.
