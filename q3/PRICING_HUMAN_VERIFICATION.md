# Q3 Pricing Human Verification Cards

Audit date: 2026-08-17

Human verified: FALSE for every model. Codex prepared evidence and recommendations only.

## Summary

Use `q3/data/pricing_human_check.csv` for the one-page manual check table and `q3/data/pricing_audit.csv` for full evidence fields.

## kimi_k3_max

- Benchmark model: Kimi K3 (max reasoning)
- Benchmark config: max reasoning
- Official API SKU: `kimi-k3`
- SKU mapping status: EXACT
- Official config: `reasoning_effort=max`
- Config mapping status: SUPPORTED_CONFIG
- Input price: 2.9675
- Output price: 14.8375
- Price unit: USD / 1M billable tokens
- Context pricing rule: 1M context; CNY source price converted with USD/CNY 6.73967410
- Official source 1: https://platform.kimi.com/docs/pricing/chat-k3.md
- Official source 2: https://platform.kimi.com/docs/guide/use-thinking-models.md
- Codex recommendation: Use baseline price after human verification
- Confidence: high
- Special issue: reasoning_content tokens are billable
- Human verified: FALSE

## gpt_5_6_sol_max

- Benchmark model: GPT-5.6 Sol (max)
- Benchmark config: max
- Official API SKU: `gpt-5.6-sol`
- SKU mapping status: EXACT
- Official config: `reasoning.effort=max`
- Config mapping status: SUPPORTED_CONFIG
- Input price: 5.0000
- Output price: 30.0000
- Price unit: USD / 1M billable tokens
- Context pricing rule: prompts with >272K input tokens use 2x input and 1.5x output; Q3 baselines are below this threshold
- Official source 1: https://developers.openai.com/api/docs/models/gpt-5.6-sol
- Official source 2: https://developers.openai.com/api/docs/guides/reasoning
- Codex recommendation: Use short-context standard price after human verification
- Confidence: high
- Special issue: reasoning tokens are billable model tokens
- Human verified: FALSE

## gpt_5_5_xhigh

- Benchmark model: GPT-5.5 (xhigh)
- Benchmark config: xhigh
- Official API SKU: `gpt-5.5`
- SKU mapping status: EXACT
- Official config: `reasoning.effort=xhigh`
- Config mapping status: SUPPORTED_CONFIG
- Input price: 5.0000
- Output price: 30.0000
- Price unit: USD / 1M billable tokens
- Context pricing rule: prompts with >272K input tokens use 2x input and 1.5x output; Q3 baselines are below this threshold
- Official source 1: https://developers.openai.com/api/docs/models/gpt-5.5
- Official source 2: https://developers.openai.com/api/docs/guides/reasoning
- Codex recommendation: Use short-context standard price after human verification
- Confidence: high
- Special issue: xhigh is a reasoning configuration and not a separate pricing SKU
- Human verified: FALSE

## claude_fable_5_max

- Benchmark model: Claude Fable 5 (max, with fallback)
- Benchmark config: max with fallback
- Official API SKU: `claude-fable-5`
- SKU mapping status: EXACT
- Official config: adaptive thinking / benchmark max effort with fallback
- Config mapping status: FALLBACK_DEPENDENT
- Input price: 10.0000
- Output price: 50.0000
- Price unit: USD / 1M billable tokens
- Context pricing rule: 1M context; prompt cache hit price is 1.0000 USD / MTok
- Official source 1: https://docs.anthropic.com/en/docs/about-claude/models/overview
- Official source 2: https://docs.anthropic.com/en/docs/about-claude/pricing
- Codex recommendation: Do not treat base Fable price as full benchmark configuration cost until fallback target and billing are resolved
- Confidence: medium
- Special issue: fallback cost unresolved
- Human verified: FALSE

### Claude Fable fallback

- Actual fallback triggered: TRUE in aggregate benchmark notes
- fallback_count: 13 for Kimi Code Bench 2.0; unknown count for SWE-Marathon and Agents Last Exam
- total_eligible_calls: 80 for Kimi Code Bench 2.0; unknown for SWE-Marathon and Agents Last Exam
- fallback_rate: 0.1625 for Kimi Code Bench 2.0; 0.35 for SWE-Marathon aggregate; 0.40 downgraded annotation for Agents Last Exam
- fallback_target: UNKNOWN
- Cost correction needed: TRUE
- Cost correction resolved: FALSE
- Evidence file: `q3/data/fable_fallback_audit.csv`

## claude_opus_4_8_max

- Benchmark model: Claude Opus 4.8 (max)
- Benchmark config: max
- Official API SKU: `claude-opus-4-8`
- SKU mapping status: EXACT
- Official config: explicit effort requested by benchmark; official docs note Opus 4.8 defaults to high
- Config mapping status: SUPPORTED_CONFIG
- Input price: 5.0000
- Output price: 25.0000
- Price unit: USD / 1M billable tokens
- Context pricing rule: 1M context; prompt cache hit price is 0.5000 USD / MTok
- Official source 1: https://docs.anthropic.com/en/docs/about-claude/models/overview
- Official source 2: https://docs.anthropic.com/en/docs/about-claude/pricing
- Codex recommendation: Use base model price after human verification; no separate max price SKU found
- Confidence: medium
- Special issue: confirm exact effort parameter level during manual review
- Human verified: FALSE

## gemini_3_1_pro_high

- Benchmark model: Gemini-3.1-Pro (High)
- Benchmark config: High
- Official API SKU: `gemini-3.1-pro-preview`
- SKU mapping status: EXACT
- Official config: `thinking_level=high`
- Config mapping status: SUPPORTED_CONFIG
- Input price: 2.0000
- Output price: 12.0000
- Price unit: USD / 1M billable tokens
- Context pricing rule: <=200K input tier used for Q3 baseline; >200K tier is input 4.0000 and output 18.0000
- Official source 1: https://ai.google.dev/gemini-api/docs/models/gemini-3.1-pro-preview
- Official source 2: https://ai.google.dev/gemini-api/docs/pricing
- Codex recommendation: Use <=200K tier for current Q3 baselines after human verification
- Confidence: high
- Special issue: output price includes thinking tokens
- Human verified: FALSE

## deepseek_v4_pro_max

- Benchmark model: DeepSeek-V4-Pro Max
- Benchmark config: Max
- Official API SKU: `deepseek-v4-pro`
- SKU mapping status: EXACT
- Official config: thinking mode default or enabled
- Config mapping status: SUPPORTED_CONFIG
- Input price: 1.3200
- Output price: 3.9600
- Price unit: USD / 1M billable tokens
- Context pricing rule: peak price used for baseline; off-peak is half of peak
- Official source 1: https://api-docs.deepseek.com/quick_start/pricing
- Official source 2: NA
- Codex recommendation: Use peak realtime API price after human verification
- Confidence: high
- Special issue: time-of-day pricing tier
- Human verified: FALSE

## deepseek_v4_flash_max

- Benchmark model: DeepSeek-V4-Flash Max
- Benchmark config: Max
- Official API SKU: `deepseek-v4-flash`
- SKU mapping status: EXACT
- Official config: thinking mode default or enabled
- Config mapping status: SUPPORTED_CONFIG
- Input price: 0.4400
- Output price: 1.3200
- Price unit: USD / 1M billable tokens
- Context pricing rule: peak price used for baseline; off-peak is half of peak
- Official source 1: https://api-docs.deepseek.com/quick_start/pricing
- Official source 2: NA
- Codex recommendation: Use peak realtime API price after human verification
- Confidence: high
- Special issue: time-of-day pricing tier
- Human verified: FALSE

## qwen3_8_max

- Benchmark model: Qwen3.8-Max
- Benchmark config: source-specific default/max
- Official API SKU: `qwen3.8-max`
- SKU mapping status: EXACT
- Official config: thinking and non-thinking modes under same official pricing row
- Config mapping status: SUPPORTED_CONFIG
- Input price: 1.7805
- Output price: 5.3415
- Price unit: USD / 1M billable tokens
- Context pricing rule: first 1M-token input range; CNY source price converted with USD/CNY 6.73967410
- Official source 1: https://help.aliyun.com/zh/model-studio/model-pricing
- Official source 2: NA
- Codex recommendation: Use first-range standard API price after human verification
- Confidence: high
- Special issue: cache and batch discounts excluded from baseline
- Human verified: FALSE

## glm_5_2_max

- Benchmark model: GLM-5.2 (max)
- Benchmark config: max
- Official API SKU: `glm-5.2`
- SKU mapping status: EXACT
- Official config: `reasoning_effort=max`
- Config mapping status: SUPPORTED_CONFIG
- Input price: NA
- Output price: NA
- Price unit: USD / 1M billable tokens
- Context pricing rule: 1M context and 128K max output confirmed; standard API price not publicly observable in checked official sources
- Official source 1: https://docs.bigmodel.cn/cn/guide/models/text/glm-5.2.md
- Official source 2: https://open.bigmodel.cn/pricing
- Codex recommendation: Keep price as PRICE_NOT_PUBLICLY_OBSERVABLE until official input/output price is confirmed
- Confidence: medium
- Special issue: price unresolved but SKU/config are resolved
- Human verified: FALSE
