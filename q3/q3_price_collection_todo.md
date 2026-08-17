# Q3 Price Collection TODO

Audit date: 2026-08-17

The current pricing audit separates SKU mapping, configuration mapping, and pricing readiness.

## Resolved Mapping

All 10 benchmark models have non-UNRESOLVED SKU and configuration mapping statuses in `q3/data/pricing_audit.csv`.

## Remaining Price Blockers

- `claude_fable_5_max`: base `claude-fable-5` price is available, but the benchmark configuration includes fallback. Local frozen evidence gives only aggregate fallback or downgraded rates, not fallback target models or token traces.
- `glm_5_2_max`: official docs confirm `glm-5.2` and `reasoning_effort=max`, but a public official standard input/output API price was not observable from checked official sources.

## Rules

- Use standard realtime API price as the primary input/output price unless a row is explicitly a special case.
- Price unit is `USD / 1M billable tokens`.
- Preserve original currency, original prices, FX rate, FX date, and FX source when converting non-USD prices.
- Treat `output_tokens` as billable output tokens, including reasoning/thinking tokens when provider billing rules include them.
- Leave unknown values as `NA`; never infer prices from nearby model names or third-party aggregators.
- Do not set `human_verified=TRUE`; final verification must be written back by a human.
