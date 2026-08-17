# Q3 Freeze v1.0

Freeze version: Q3 v1.0
Freeze date: 2026-08-17
Git branch: q3-cost-pareto
Git commit: recorded by the final freeze commit in repository history
Q2 source commit: bff0e185510f79bd78dd190ccedc47c81b12f137
Q2 nominal SHA256: 82bc63f0d1983775bf9a512ad8e50d011c0d556cbdd56329ed8f74267de84ca1
Q2 bootstrap SHA256: 1eea0558c3df5e46c9b3135a7810f4ef6dbb2258f96e4bef4ae4e84e8c64b323
Pricing verification status: 8 FULL rows VERIFIED_FULL_PRICE; Fable REVIEWED_PARTIAL_COST; GLM REVIEWED_MISSING_PUBLIC_PRICE
Main analysis cohort size: 8
FULL models: Claude Opus 4.8; DeepSeek-V4-Flash; DeepSeek-V4-Pro; Gemini-3.1-Pro; GPT-5.5; GPT-5.6 Sol; Kimi K3; Qwen3.8-Max
PARTIAL models: Claude Fable 5
MISSING models: GLM-5.2
Workload version: q3/data/workload_config.csv, baseline_template rows
Tests: 20 passed, 1 existing SciPy OptimizeWarning
Reproducibility audit: PASS
Paper-result consistency audit: PASS
Freeze manifest audit: PASS
Final gate: Q3_READY_TO_FREEZE=TRUE; Q3_FROZEN=TRUE
Known limitations: standardized workloads; time-varying API prices; Fable fallback target/token billing not fully traceable; GLM public standard API price unavailable; cross-sectional fits are not causal.
