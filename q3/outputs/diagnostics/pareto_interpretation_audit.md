# Final Pareto Interpretation Audit

Audit date: 2026-08-17  
Input: `q3/outputs/tables/pareto_results_final.csv`

The strict Pareto analysis contains only the eight FULL, human-verified models.
Fable 5 and GLM-5.2 are not treated as dominated models: they are excluded
before the strict comparison because their complete benchmark costs are not
observable.

## Research

- Frontier size: 3
- Pareto models: DeepSeek-V4-Flash Max, DeepSeek-V4-Pro Max, Kimi K3
- Dominated models: Qwen3.8-Max, Gemini-3.1-Pro (High), Claude Opus 4.8,
  GPT-5.5, GPT-5.6 Sol
- Dominance audit:
  - Qwen3.8-Max is dominated by DeepSeek-V4-Pro Max.
  - Gemini-3.1-Pro is dominated by DeepSeek-V4-Pro Max and Qwen3.8-Max.
  - Claude Opus 4.8 is dominated by Kimi K3.
  - GPT-5.5 is dominated by Kimi K3 and GPT-5.6 Sol.
  - GPT-5.6 Sol is dominated by Kimi K3.
- High-cost/no-advantage cases: Claude Opus 4.8, GPT-5.5, and GPT-5.6 Sol
  have higher cost than at least one model with greater or equal utility.
- Frontier size is small; no high-parameter frontier fit should be interpreted.

## General

- Frontier size: 6
- Pareto models: DeepSeek-V4-Flash Max, DeepSeek-V4-Pro Max, Qwen3.8-Max,
  Gemini-3.1-Pro (High), Kimi K3, GPT-5.6 Sol
- Dominated models: Claude Opus 4.8, GPT-5.5
- Dominance audit:
  - Claude Opus 4.8 is dominated by Kimi K3, Gemini-3.1-Pro, and Qwen3.8-Max.
  - GPT-5.5 is dominated by Kimi K3, GPT-5.6 Sol, Claude Opus 4.8,
    Gemini-3.1-Pro, and Qwen3.8-Max.
- High-cost/no-advantage case: GPT-5.5 is dominated at the same cost as
  GPT-5.6 Sol.
- The six-point frontier supports descriptive comparison, but not a universal
  causal cost-performance law.

## Coding

- Frontier size: 3
- Pareto models: DeepSeek-V4-Flash Max, DeepSeek-V4-Pro Max, Kimi K3
- Dominated models: Qwen3.8-Max, Gemini-3.1-Pro (High), Claude Opus 4.8,
  GPT-5.5, GPT-5.6 Sol
- Dominance audit:
  - Qwen3.8-Max and Gemini-3.1-Pro are dominated by DeepSeek-V4-Pro Max.
  - Claude Opus 4.8 is dominated by Kimi K3, Gemini-3.1-Pro, DeepSeek-V4-Pro,
    and Qwen3.8-Max.
  - GPT-5.5 is dominated by Kimi K3, GPT-5.6 Sol, Claude Opus 4.8,
    Gemini-3.1-Pro, DeepSeek-V4-Pro, and Qwen3.8-Max.
  - GPT-5.6 Sol is dominated by Kimi K3 and DeepSeek-V4-Pro Max.
- High-cost/no-advantage cases: GPT-5.5 and GPT-5.6 Sol are more expensive
  than stronger frontier choices under the Coding baseline.
- Frontier size is small; frontier regression is marked
  `INSUFFICIENT_FRONTIER_SAMPLE`.
