# Q3 Pricing Human Verification Checklist

Audit date: 2026-08-17

Human verification status: FALSE for all rows. This file records machine-collected official-source evidence and the remaining checks required before final Q3 reporting.

## A. Direct Official SKU Evidence

No row is marked human-verified. The audit did not assign any `human_verified=TRUE` value.

## B. Official SKU or Configuration Matches

| model_id | benchmark model | benchmark setting | candidate API SKU | price used | confidence | human_verified | verification note |
|---|---|---:|---|---:|---|---|---|
| `kimi_k3_max` | Kimi K3 | max reasoning | `kimi-k3` | input 2.9675; output 14.8375; cached input 0.2968 USD / 1M tokens | high | FALSE | Official Kimi K3 pricing is in CNY and was converted using USD/CNY 6.73967410 on 2026-08-17. The official docs also state max reasoning support and billable reasoning tokens. |
| `deepseek_v4_pro_max` | DeepSeek-V4-Pro Max | Max | `deepseek-v4-pro`; `DeepSeek-V4-Pro-0813` | input 1.3200; output 3.9600; cached input 0.0440 USD / 1M tokens | high | FALSE | Official DeepSeek pricing gives peak and off-peak tiers. The baseline records peak cache-miss input and peak output prices for a conservative standardized API workload. |
| `deepseek_v4_flash_max` | DeepSeek-V4-Flash Max | Max | `deepseek-v4-flash`; `DeepSeek-V4-Flash-0731` | input 0.4400; output 1.3200; cached input 0.0140 USD / 1M tokens | high | FALSE | Official DeepSeek pricing gives peak and off-peak tiers. The baseline records peak cache-miss input and peak output prices for a conservative standardized API workload. |
| `qwen3_8_max` | Qwen3.8-Max | source-specific default/max | `qwen3.8-max` | input 1.7805; output 5.3415 USD / 1M tokens | high | FALSE | Official Alibaba Model Studio pricing is in CNY and was converted using USD/CNY 6.73967410 on 2026-08-17. Context-cache and batch discounts are excluded from the baseline. |

## C. Unresolved Pricing Rows

| model_id | benchmark model | provider | status | required human action |
|---|---|---|---|---|
| `gpt_5_6_sol_max` | GPT-5.6 Sol (max) | OpenAI | UNRESOLVED | Confirm whether this exact benchmark model maps to an official OpenAI API SKU and record the official input/output prices. |
| `gpt_5_5_xhigh` | GPT-5.5 (xhigh) | OpenAI | UNRESOLVED | Confirm whether this exact benchmark model maps to an official OpenAI API SKU and whether `xhigh` changes billing. |
| `claude_fable_5_max` | Claude Fable 5 (max, with fallback) | Anthropic | UNRESOLVED | Confirm the primary SKU and fallback routing rule. Price fallback calls explicitly instead of using a single guessed price. |
| `claude_opus_4_8_max` | Claude Opus 4.8 (max) | Anthropic | UNRESOLVED | Confirm exact official API SKU and input/output prices. |
| `gemini_3_1_pro_high` | Gemini-3.1-Pro (High) | Google DeepMind | UNRESOLVED | Confirm exact Gemini API SKU and whether High reasoning changes the price. |
| `glm_5_2_max` | GLM-5.2 (max) | Zhipu AI / Z.ai | UNRESOLVED | Confirm exact official API SKU and prices. Do not infer from nearby GLM model names. |

## Source Notes

- Kimi official source: `https://platform.kimi.com/docs/pricing/chat-k3.md`
- DeepSeek official source: `https://api-docs.deepseek.com/quick_start/pricing`
- Qwen official source: `https://help.aliyun.com/zh/model-studio/model-pricing`
- Attempted unresolved sources are recorded in `q3/data/pricing_audit.csv`.
- CNY prices were converted to USD with USD/CNY 6.73967410 on 2026-08-17. This conversion is an audit convention and should be refreshed before final submission if the final run date differs.
