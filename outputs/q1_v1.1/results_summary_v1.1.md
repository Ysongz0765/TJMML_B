# Q1 v1.1 results summary

## C5 audit
- Type A capability absence: DeepSeek-V4-Pro Max; DeepSeek-V4-Flash Max.
- Type C observed: Kimi K3, GPT-5.6 Sol, GPT-5.5, Claude Fable 5, Claude Opus 4.8, Gemini-3.1-Pro, Qwen3.8-Max.
- REQUIRES_MANUAL_CONFIRMATION: GLM-5.2. Its frozen evidence does not distinguish capability absence from benchmark missing.

## Stability
- v1.0 C2/C3/C5 each had one unique bootstrap score vector because every family in those dimensions had one Exact Setting.
- v1.1 uses latent BT-theta ranking stability from a 2,000-replicate parametric BT bootstrap.

## Ranking-A weights
- C1: 0.125734
- C2: 0.210410
- C3: 0.138221
- C4: 0.108204
- C5: 0.417432

## Ranking A (nine resolved models; GLM conditional)
1. GPT-5.6 Sol (max): 79.839
2. Claude Fable 5 (max, with fallback): 70.591
3. Kimi K3 (max reasoning): 53.570
4. Gemini-3.1-Pro (High): 51.244
5. Qwen3.8-Max: 46.043
6. GPT-5.5 (xhigh): 33.926
7. Claude Opus 4.8 (max): 32.685
8. DeepSeek-V4-Pro Max: 28.601
9. DeepSeek-V4-Flash Max: 10.355

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

## Ranking C (seven complete multimodal models)
1. GPT-5.6 Sol (max): 77.430
2. Claude Fable 5 (max, with fallback): 67.172
3. Kimi K3 (max reasoning): 50.155
4. Qwen3.8-Max: 44.504
5. Gemini-3.1-Pro (High): 39.699
6. GPT-5.5 (xhigh): 30.893
7. Claude Opus 4.8 (max): 25.237

## Kimi K3
- Ranks A/B/C: 3/2/3.
- Ranking-A score: 53.570; bootstrap Top-3 frequency: 0.417.
- Strongest gap: C4 +31.707; weakest gap: C5 -20.513.
- C4 is strong direct evidence; C3 is model-inferred moderate evidence because only AA-LCR is directly observed for Kimi.

## Freeze gate
- Frozen SHA-256 unchanged; BT convergence, weight sums, coverage consistency, and figure non-emptiness passed.
- P0 remains: GLM-5.2 C5 applicability requires manual confirmation.
- Q1_V1.1_READY_TO_FREEZE = FALSE
