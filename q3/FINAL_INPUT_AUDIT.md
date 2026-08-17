# Q3 Final Input Audit

Audit date: 2026-08-17  
Pre-run Git commit: `441f935e8bd65b1a51866a315c1af822297df4cd`

## Gate Result

`Q3_READY_TO_FREEZE = FALSE`

The repository does not contain the claimed human price verification. All
10 rows in each of the following files still have `human_verified=FALSE`:

- `q3/data/model_pricing.csv`
- `q3/data/pricing_audit.csv`
- `q3/data/pricing_human_check.csv`

No price number, SKU, or configuration value was changed in this audit.

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
- Human-verified rows in all three price files: 0/10
- Complete base-price rows: 9
- `FULL` cost-observability rows: 8
- `PARTIAL` rows: Claude Fable 5
- `MISSING` rows: GLM-5.2
- Price date: 2026-08-17
- Distinct non-empty price source URLs: 8
- SKU mapping: all 10 `EXACT`
- Configuration mapping: 9 `SUPPORTED_CONFIG`, 1 `FALLBACK_DEPENDENT`

Claude Fable 5 remains `PARTIAL` because fallback target and token billing are
not traceable. GLM-5.2 remains `MISSING` because an official standard
input/output API price is not observable in the checked records. No imputation
or neighboring-SKU substitution is allowed.

Because human verification is absent, the strict formal main cohort is
currently empty even though eight rows have complete observable base costs.

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

## Blocking Action

The owner must write the actual manual review outcome and verification date
into all three pricing verification files. After that change is present on
`q3-cost-pareto`, rerun the final runner and repeat every audit. Until then,
the existing tables remain provisional historical outputs and no Q3 freeze is
created.
