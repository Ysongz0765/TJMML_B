# Q1 v1.2 results summary

## C5 audit
- Type A capability absence: DeepSeek-V4-Pro Max; DeepSeek-V4-Flash Max; GLM-5.2 (max).
- Type C observed: Kimi K3, GPT-5.6 Sol, GPT-5.5, Claude Fable 5, Claude Opus 4.8, Gemini-3.1-Pro, Qwen3.8-Max.
- GLM-5.2 Type A was confirmed by the manual capability verification record; its raw MMMU-Pro/MathVision cells remain NA.

## Stability
- v1.0 C2/C3/C5 each had one unique bootstrap score vector because every family in those dimensions had one Exact Setting.
- v1.2 uses latent BT-theta ranking stability from a 2,000-replicate parametric BT bootstrap.

## Ranking-A weights
- C1: 0.128212
- C2: 0.203358
- C3: 0.123432
- C4: 0.118157
- C5: 0.426840

## Ranking A (all ten models; C5* unified capability availability)
1. GPT-5.6 Sol (max): 80.498
2. Claude Fable 5 (max, with fallback): 70.822
3. Kimi K3 (max reasoning): 53.720
4. Gemini-3.1-Pro (High): 52.276
5. Qwen3.8-Max: 46.595
6. GPT-5.5 (xhigh): 33.485
7. Claude Opus 4.8 (max): 32.456
8. DeepSeek-V4-Pro Max: 28.142
9. GLM-5.2 (max): 14.906
10. DeepSeek-V4-Flash Max: 9.504

## Ranking B (all ten models, C1-C4)
1. Claude Fable 5 (max, with fallback): 79.577
2. Kimi K3 (max reasoning): 67.475
3. GPT-5.6 Sol (max): 65.990
4. Claude Opus 4.8 (max): 56.172
5. GPT-5.5 (xhigh): 52.172
6. Gemini-3.1-Pro (High): 47.412
7. DeepSeek-V4-Pro Max: 46.922
8. Qwen3.8-Max: 39.299
9. GLM-5.2 (max): 24.891
10. DeepSeek-V4-Flash Max: 15.823

## Ranking C (seven-model subset with estimable C5 capability)
1. GPT-5.6 Sol (max): 77.430
2. Claude Fable 5 (max, with fallback): 67.172
3. Kimi K3 (max reasoning): 50.155
4. Qwen3.8-Max: 44.504
5. Gemini-3.1-Pro (High): 39.699
6. GPT-5.5 (xhigh): 30.893
7. Claude Opus 4.8 (max): 25.237

## Kimi K3
- Ranks A/B/C: 3/2/3.
- Ranking-A score: 53.720; bootstrap Top-3 frequency: 0.422.
- Strongest gap: C4 +36.415; weakest gap: C5 -20.513.
- C4 is strong direct evidence; C3 is model-inferred moderate evidence because only AA-LCR is directly observed for Kimi.

## Freeze gate
- Frozen SHA-256 unchanged; BT convergence, weight sums, coverage consistency, and figure non-emptiness passed.
- No P0 issues remain; all capability applicability checks are complete.
- Q1_V1.2_READY_TO_FREEZE = TRUE
