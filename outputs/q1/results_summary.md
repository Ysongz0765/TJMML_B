# Q1 results summary

- Data: 10 models, 14 Benchmark Families, 21 Exact Settings, 164 non-missing records, coverage 0.7810.
- Frozen SHA-256 validation: passed.

## Dimension weights
- C1 Complex reasoning: 0.0134
- C2 Knowledge and factual reliability: 0.3399
- C3 Long context: 0.1997
- C4 Code and software engineering: 0.0600
- C5 Multimodal: 0.3870

## Overall ranking
1. GPT-5.6 Sol (max): 75.183, coverage=1.000
2. Claude Fable 5 (max, with fallback): 74.599, coverage=1.000
3. Kimi K3 (max reasoning): 49.056, coverage=1.000
4. DeepSeek-V4-Pro Max: 42.509, coverage=0.613
5. Gemini-3.1-Pro (High): 41.433, coverage=1.000
6. Qwen3.8-Max: 38.610, coverage=1.000
7. GPT-5.5 (xhigh): 30.129, coverage=1.000
8. Claude Opus 4.8 (max): 27.698, coverage=1.000
9. DeepSeek-V4-Flash Max: 25.374, coverage=0.613
10. GLM-5.2 (max): 25.071, coverage=0.613

## Kimi K3
- Main rank: 3; score: 49.056; top-3 probability: 1.000.
- Strongest dimension vs median: C4 Code and software engineering (36.415).
- Weakest dimension vs median: C5 Multimodal (-20.513).

## Most unstable sensitivity checks
- remove AA-LCR: Spearman=0.842, Kendall=0.689, Kimi rank change=1
- margin=none: Spearman=0.879, Kendall=0.733, Kimi rank change=1
- exclude C5: Spearman=0.794, Kendall=0.644, Kimi rank change=0

## Special network checks
- C3 leave-AA-LCR-out and C4 leave-LiveBench-out diagnostics are recorded in diagnostics/model_diagnostics.json.
- C5 missing scores remain NA and are not converted to zero.
