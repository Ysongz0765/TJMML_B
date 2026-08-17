# Q3 Paper Fact Check

This table is generated from `q3/frozen/v1.0/`; it is the numerical source of truth for the standalone manuscript.

## Cohort

- FULL models: Claude Opus 4.8, DeepSeek-V4-Flash Max, DeepSeek-V4-Pro Max, Gemini-3.1-Pro (High), GPT-5.5, GPT-5.6 Sol, Kimi K3, Qwen3.8-Max
- PARTIAL models: Claude Fable 5
- MISSING models: GLM-5.2
- Main cohort size: 8

## Baseline Workloads

| Scenario | N | Input tokens | Billable output tokens | Output/input ratio |
|---|---:|---:|---:|---:|
| Research | 1 | 16000 | 4000 | 0.25 |
| General | 1 | 2000 | 1000 | 0.5 |
| Coding | 1 | 6000 | 6000 | 1 |

## Pareto Results

### Research
- Pareto models: DeepSeek-V4-Flash Max, DeepSeek-V4-Pro Max, Kimi K3
- Dominated models: Qwen3.8-Max, Gemini-3.1-Pro (High), Claude Opus 4.8, GPT-5.5, GPT-5.6 Sol
| Model | Utility | Cost (USD) | Pareto |
|---|---:|---:|---|
| DeepSeek-V4-Flash Max | 0.827289 | 0.012320 | Yes |
| DeepSeek-V4-Pro Max | 0.877794 | 0.036960 | Yes |
| Qwen3.8-Max | 0.839749 | 0.049854 | No |
| Gemini-3.1-Pro (High) | 0.828120 | 0.080000 | No |
| Kimi K3 | 0.901293 | 0.106830 | Yes |
| Claude Opus 4.8 | 0.879414 | 0.180000 | No |
| GPT-5.5 | 0.886162 | 0.200000 | No |
| GPT-5.6 Sol | 0.899241 | 0.200000 | No |

### General
- Pareto models: DeepSeek-V4-Flash Max, DeepSeek-V4-Pro Max, Qwen3.8-Max, Gemini-3.1-Pro (High), Kimi K3, GPT-5.6 Sol
- Dominated models: Claude Opus 4.8, GPT-5.5
| Model | Utility | Cost (USD) | Pareto |
|---|---:|---:|---|
| DeepSeek-V4-Flash Max | 0.646876 | 0.002200 | Yes |
| DeepSeek-V4-Pro Max | 0.654286 | 0.006600 | Yes |
| Qwen3.8-Max | 0.838380 | 0.008903 | Yes |
| Gemini-3.1-Pro (High) | 0.866159 | 0.016000 | Yes |
| Kimi K3 | 0.868707 | 0.020773 | Yes |
| Claude Opus 4.8 | 0.838339 | 0.035000 | No |
| GPT-5.5 | 0.837175 | 0.040000 | No |
| GPT-5.6 Sol | 0.932145 | 0.040000 | Yes |

### Coding
- Pareto models: DeepSeek-V4-Flash Max, DeepSeek-V4-Pro Max, Kimi K3
- Dominated models: Qwen3.8-Max, Gemini-3.1-Pro (High), Claude Opus 4.8, GPT-5.5, GPT-5.6 Sol
| Model | Utility | Cost (USD) | Pareto |
|---|---:|---:|---|
| DeepSeek-V4-Flash Max | 0.815577 | 0.010560 | Yes |
| DeepSeek-V4-Pro Max | 0.961063 | 0.031680 | Yes |
| Qwen3.8-Max | 0.925700 | 0.042732 | No |
| Gemini-3.1-Pro (High) | 0.925981 | 0.084000 | No |
| Kimi K3 | 0.981302 | 0.106830 | Yes |
| Claude Opus 4.8 | 0.916391 | 0.180000 | No |
| GPT-5.5 | 0.902514 | 0.210000 | No |
| GPT-5.6 Sol | 0.951273 | 0.210000 | No |

## Budget Switching

- Research: thresholds = 0.012320 → 0.036960 → 0.106830; model sequence = DeepSeek-V4-Flash Max → DeepSeek-V4-Pro Max → Kimi K3
- General: thresholds = 0.002200 → 0.006600 → 0.008903 → 0.016000 → 0.020773 → 0.040000; model sequence = DeepSeek-V4-Flash Max → DeepSeek-V4-Pro Max → Qwen3.8-Max → Gemini-3.1-Pro (High) → Kimi K3 → GPT-5.6 Sol
- Coding: thresholds = 0.010560 → 0.031680 → 0.106830; model sequence = DeepSeek-V4-Flash Max → DeepSeek-V4-Pro Max → Kimi K3

## ICER

| Scenario | From | To | Delta cost | Delta utility | ICER |
|---|---|---|---:|---:|---:|
| Coding | DeepSeek-V4-Flash Max | DeepSeek-V4-Pro Max | 0.021120 | 0.145485 | 0.145169 |
| Coding | DeepSeek-V4-Pro Max | Kimi K3 | 0.075150 | 0.020239 | 3.713059 |
| General | DeepSeek-V4-Flash Max | DeepSeek-V4-Pro Max | 0.004400 | 0.007410 | 0.593761 |
| General | DeepSeek-V4-Pro Max | Qwen3.8-Max | 0.002303 | 0.184094 | 0.012507 |
| General | Qwen3.8-Max | Gemini-3.1-Pro (High) | 0.007098 | 0.027779 | 0.255499 |
| General | Gemini-3.1-Pro (High) | Kimi K3 | 0.004772 | 0.002548 | 1.872844 |
| General | Kimi K3 | GPT-5.6 Sol | 0.019228 | 0.063438 | 0.303089 |
| Research | DeepSeek-V4-Flash Max | DeepSeek-V4-Pro Max | 0.024640 | 0.050504 | 0.487879 |
| Research | DeepSeek-V4-Pro Max | Kimi K3 | 0.069870 | 0.023499 | 2.973325 |

## Cost--Performance Fits

| Scenario | Subset | Model | R2 | AIC | AICc | BIC | LOOCV error | Warning |
|---|---|---|---:|---:|---:|---:|---:|---|
| Coding | all_models | linear | 0.070341 | -45.508753 | -43.108753 | -45.349870 | 0.004055 | None |
| Coding | all_models | log | 0.077727 | -45.572561 | -43.172561 | -45.413677 | 0.004089 | None |
| Coding | all_models | saturation | 0.070329 | -43.508649 | -37.508649 | -43.270324 | 0.003159 | None |
| General | all_models | linear | 0.506858 | -39.042970 | -36.642970 | -38.884087 | 0.008176 | None |
| General | all_models | log | 0.509852 | -39.091699 | -36.691699 | -38.932816 | 0.008130 | None |
| General | all_models | saturation | 0.755203 | -42.645925 | -36.645925 | -42.407600 | 9.802600 | None |
| Research | all_models | linear | 0.470986 | -57.794596 | -55.394596 | -57.635713 | 0.000682 | None |
| Research | all_models | log | 0.473763 | -57.836691 | -55.436691 | -57.677808 | 0.000678 | None |
| Research | all_models | saturation | 0.481753 | -55.959100 | -49.959100 | -55.720775 | 0.000870 | None |
| Coding | pareto_frontier | linear | 0.560468 | -14.103151 | NA | -15.905926 | NA | INSUFFICIENT_FRONTIER_SAMPLE |
| Coding | pareto_frontier | log | 0.568701 | -14.159878 | NA | -15.962653 | NA | INSUFFICIENT_FRONTIER_SAMPLE |
| General | pareto_frontier | linear | 0.667923 | -29.092921 | -25.092921 | -29.509402 | 0.014826 | None |
| General | pareto_frontier | log | 0.671657 | -29.160759 | -25.160759 | -29.577240 | 0.014420 | None |
| General | pareto_frontier | saturation | 0.845494 | -31.683723 | -19.683723 | -32.308445 | 2.608766 | None |
| Research | pareto_frontier | linear | 0.789025 | -21.534906 | NA | -23.337681 | NA | INSUFFICIENT_FRONTIER_SAMPLE |
| Research | pareto_frontier | log | 0.796630 | -21.645037 | NA | -23.447812 | NA | INSUFFICIENT_FRONTIER_SAMPLE |

## Sensitivity

- Coding/input_scale: STABLE_ON_TESTED_GRID; nominal-member retention = 1.0000; all-members retained = 1.0000; tested points = 3.
- Coding/input_output_ratio: STABLE_ON_TESTED_GRID; nominal-member retention = 1.0000; all-members retained = 1.0000; tested points = 5.
- Coding/price_perturbation: STABLE_ON_TESTED_GRID; nominal-member retention = 1.0000; all-members retained = 1.0000; tested points = 5.
- General/input_scale: STABLE_ON_TESTED_GRID; nominal-member retention = 1.0000; all-members retained = 1.0000; tested points = 3.
- General/input_output_ratio: STABLE_ON_TESTED_GRID; nominal-member retention = 1.0000; all-members retained = 1.0000; tested points = 5.
- General/price_perturbation: STABLE_ON_TESTED_GRID; nominal-member retention = 1.0000; all-members retained = 1.0000; tested points = 5.
- Research/input_scale: STABLE_ON_TESTED_GRID; nominal-member retention = 1.0000; all-members retained = 1.0000; tested points = 3.
- Research/input_output_ratio: STABLE_ON_TESTED_GRID; nominal-member retention = 1.0000; all-members retained = 1.0000; tested points = 5.
- Research/price_perturbation: STABLE_ON_TESTED_GRID; nominal-member retention = 1.0000; all-members retained = 1.0000; tested points = 5.

## Bootstrap Pareto Probability

| Model | Research | General | Coding |
|---|---:|---:|---:|
| Claude Opus 4.8 | 0.0565 | 0.0400 | 0.0015 |
| DeepSeek-V4-Flash Max | 1.0000 | 1.0000 | 1.0000 |
| DeepSeek-V4-Pro Max | 0.8890 | 0.6745 | 0.9465 |
| Gemini-3.1-Pro (High) | 0.1100 | 0.9050 | 0.1620 |
| GPT-5.5 | 0.0335 | 0.0000 | 0.0000 |
| GPT-5.6 Sol | 0.3405 | 0.9765 | 0.0600 |
| Kimi K3 | 0.7355 | 0.5225 | 0.6150 |
| Qwen3.8-Max | 0.1045 | 1.0000 | 0.2840 |
