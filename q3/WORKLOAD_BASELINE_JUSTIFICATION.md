# Q3 Workload Baseline Justification

Audit date: 2026-08-17

## 1. Why Q3 Does Not Use One Performance/Price Ratio

Q3 evaluates each model by scenario utility and workload cost as two separate objectives. A single `Performance / Price` ratio is not sufficient because API costs depend on both input and output tokens, and the input/output mix changes by scenario. A model can be cheap for input-heavy tasks but expensive for output-heavy tasks, so Q3 uses scenario-specific cost and Pareto analysis.

## 2. Input and Billable Output Tokens Are Priced Separately

The pricing table records `input_price`, `output_price`, and, where official docs provide it, `cached_input_price`. In the workload table, `output_tokens` means billable output tokens, not only user-visible answer tokens. For reasoning or thinking models, billable output can include hidden or summarized reasoning/thinking tokens when provider documentation says those tokens are billed. Baseline cost uses uncached input and billable output prices because cache-hit ratios are workload-specific and were not observed in Q2. Cached input prices remain available for sensitivity or secondary analysis.

## 3. Baseline Scenarios

| scenario | n_calls | input_tokens | billable output_tokens | output/input ratio | rationale |
|---|---:|---:|---:|---:|---|
| Research | 1 | 16000 | 4000 | 0.25 | Long-context scientific paper, report, or evidence synthesis task aligned with the Q2 research-oriented model comparison setting. |
| General | 1 | 2000 | 1000 | 0.50 | Mixed everyday assistant workload such as question answering, summarization, and short planning. |
| Coding | 1 | 6000 | 6000 | 1.00 | Code development or review workload where substantial generated code, explanation, or patch text is expected. |

## 4. Standardized Workloads, Not Industry Means

These baselines are standardized comparison scenarios. They are not claimed to be empirical industry averages, survey estimates, or measured production workloads. Their role is to make cost comparisons reproducible while Q2 provides scenario utility.

## 5. Rationale Sources

The workload design uses three evidence anchors:

- The Q2 scenario mapping, which separates research, general, and coding utility.
- Provider API billing documentation, which prices input and output tokens separately and sometimes provides cache or time-tier discounts.
- Benchmark comparability requirements, which require the same workload within a scenario for every model.

## 6. Sensitivity Design

The config includes explicit sensitivity rows for input-token scale and output/input ratio:

- Input scale: 0.5, 1.0, and 1.5 times the baseline input length while holding output length fixed.
- Output/input ratio: scenario-specific low, baseline, and high output lengths while holding input length fixed.

These rows allow cost ranking, Pareto membership, budget switch points, and selected optimal models to be checked against workload assumptions.

## 7. Parameters That Can Affect Pareto Ranking

Pareto results can change when:

- Output tokens are high and a model has expensive output pricing.
- Input tokens dominate and a model has high uncached input pricing.
- Cache-hit assumptions are introduced.
- DeepSeek peak/off-peak tier choice changes.
- CNY/USD conversion is refreshed.
- Previously unresolved prices become available.

## 8. Linear Scaling by Number of Calls

The baseline sets `n_calls=1` for every scenario to compare a single standardized task. Increasing `N_s` scales all model costs linearly within the same scenario and does not change within-scenario cost ordering when token lengths and prices are unchanged. Larger `N_s` values can be used later for budget magnitude interpretation.
