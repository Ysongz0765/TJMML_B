# Q3 Data Dictionary

## model_pricing.csv

| field | meaning |
| --- | --- |
| model_id | Stable model identifier reused from Q1/Q2. |
| model_name | Human-readable model name reused from Q2. |
| exact_version | Exact model/configuration to be priced. |
| provider | API or model provider. |
| price_date | Date on which pricing was verified. Required for final run. |
| input_price | Standard realtime API input token price in USD / 1M billable tokens. |
| output_price | Standard realtime API output token price in USD / 1M billable tokens. |
| cached_input_price | Cached input price when officially available; missing is allowed but must stay missing. |
| price_unit | Must be `USD / 1M billable tokens`. |
| deployment | Pricing deployment mode, normally standard realtime API. |
| source_type | Official source type or trusted fallback note. |
| source_url | Pricing source URL. |
| human_verified | Whether the exact version and price were manually verified. |
| notes | Version, currency, region, cache, batch, or missing-value notes. |

## workload_config.csv

| field | meaning |
| --- | --- |
| scenario | Scenario key: Research, General, or Coding. |
| scenario_name | Human-readable scenario name. |
| n_calls | Number of calls in the standard workload. |
| input_tokens | Average input tokens per call. |
| output_tokens | Average billable output tokens per call, including reasoning/thinking tokens when provider billing rules include them. |
| input_output_ratio | `output_tokens / input_tokens`. |
| workload_level | Baseline or sensitivity template label. |
| source_or_rationale | Evidence source or rationale for the parameterization. |
| notes | Missing-value and interpretation notes. |

## scenario_utility.csv

Formal Q2 output expected by Q3:

| field | meaning |
| --- | --- |
| model_id | Stable model identifier reused from Q1/Q2. |
| model_name | Human-readable model name. |
| scenario | Scenario key. |
| utility | Q2 scenario utility, expected in [0, 100]. |

## scenario_utility_bootstrap.csv

Optional Q2 bootstrap utility output:

| field | meaning |
| --- | --- |
| model_id | Stable model identifier reused from Q1/Q2. |
| model_name | Human-readable model name. |
| scenario | Scenario key. |
| bootstrap_id | Bootstrap replicate id. |
| utility | Bootstrap scenario utility. |
