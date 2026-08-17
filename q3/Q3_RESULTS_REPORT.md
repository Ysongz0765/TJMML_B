# Q3 Results Report

Audit date: 2026-08-17  
Status: **Provisional; human verification remains incomplete.**

## Final Gate

The formal final rerun is currently blocked. The repository state at commit
`441f935e8bd65b1a51866a315c1af822297df4cd` has `human_verified=FALSE` for all
10 rows in `model_pricing.csv`, `pricing_audit.csv`, and
`pricing_human_check.csv`. The prior results in this report are retained as
historical provisional outputs only. See `FINAL_INPUT_AUDIT.md` and
`Q3_FINAL_AUDIT.md`.

## 1. Data Closure

The formal Q2-to-Q3 interface was synchronized from
`origin/q2-final-paper` at commit `bff0e185510f79bd78dd190ccedc47c81b12f137`.
The nominal utility file contains 30 rows covering 10 models and the Research,
General, and Coding scenarios. The bootstrap utility file contains 60,000 rows
from 2,000 draws. The frozen interface validation reports 18/18 checks passed,
and the Q3 runner independently validated model coverage, scenario coverage,
duplicate keys, missing utilities, and utility ordering.

Q3 uses a transparent cost-observability cohort:

| Cohort | Models | Main analysis |
|---|---:|---|
| `FULL` | 8 | Included |
| `PARTIAL` | Claude Fable 5 | Excluded from main Pareto |
| `MISSING` | GLM-5.2 | Excluded from main Pareto |

Claude Fable 5 has an official base price, but the benchmark fallback
configuration lacks a traceable fallback target and token record. GLM-5.2 has
an identified SKU/configuration but no publicly observable official standard
input/output price in the checked sources. Neither case is imputed,
substituted, or marked `human_verified=TRUE`. Both remain visible in the cohort
and all-model cost tables with exclusion reasons.

## 2. Standardized Workloads

All costs use one standardized task per scenario and uncached input pricing.
`output_tokens` means billable output tokens, including reasoning/thinking tokens
when provider billing rules include them.

| Scenario | Calls | Input tokens | Billable output tokens | Input/output ratio |
|---|---:|---:|---:|---:|
| Research | 1 | 16,000 | 4,000 | 0.25 |
| General | 1 | 2,000 | 1,000 | 0.50 |
| Coding | 1 | 6,000 | 6,000 | 1.00 |

These are standardized comparison workloads, not empirical industry averages.

## 3. Scenario Cost and Utility

The following table reports the 8-model `FULL` cohort. Costs are USD per
standardized task; utility is the Q2 scenario utility.

| Model | Research cost | Research utility | General cost | General utility | Coding cost | Coding utility |
|---|---:|---:|---:|---:|---:|---:|
| DeepSeek-V4-Flash Max | 0.012320 | 0.827289 | 0.002200 | 0.646876 | 0.010560 | 0.815577 |
| DeepSeek-V4-Pro Max | 0.036960 | 0.877794 | 0.006600 | 0.654286 | 0.031680 | 0.961063 |
| Qwen3.8-Max | 0.049854 | 0.839749 | 0.008903 | 0.838380 | 0.042732 | 0.925700 |
| Gemini-3.1-Pro (High) | 0.080000 | 0.828120 | 0.016000 | 0.866159 | 0.084000 | 0.925981 |
| Claude Opus 4.8 (max) | 0.180000 | 0.879414 | 0.035000 | 0.838339 | 0.180000 | 0.916391 |
| Kimi K3 (max reasoning) | 0.106830 | 0.901293 | 0.020772 | 0.868707 | 0.106830 | 0.981302 |
| GPT-5.5 (xhigh) | 0.200000 | 0.886162 | 0.040000 | 0.837175 | 0.210000 | 0.902514 |
| GPT-5.6 Sol (max) | 0.200000 | 0.899241 | 0.040000 | 0.932145 | 0.210000 | 0.951273 |

The three scenarios yield different trade-offs; no global best model is
reported. DeepSeek-V4-Flash is the lowest-cost model in every baseline, while
the highest-utility point differs by scenario.

## 4. Pareto Frontiers

The main Pareto analysis is cost minimization plus utility maximization within
each scenario.

| Scenario | Pareto members | Dominated FULL models |
|---|---|---|
| Coding | DeepSeek-V4-Flash Max; DeepSeek-V4-Pro Max; Kimi K3 | GPT-5.6 Sol; GPT-5.5; Claude Opus 4.8; Gemini-3.1-Pro; Qwen3.8-Max |
| General | DeepSeek-V4-Flash Max; DeepSeek-V4-Pro Max; Qwen3.8-Max; Gemini-3.1-Pro; Kimi K3; GPT-5.6 Sol | GPT-5.5; Claude Opus 4.8 |
| Research | DeepSeek-V4-Flash Max; DeepSeek-V4-Pro Max; Kimi K3 | GPT-5.6 Sol; GPT-5.5; Claude Opus 4.8; Gemini-3.1-Pro; Qwen3.8-Max |

This is a scenario-specific frontier, not a universal ranking.

## 5. Budget Switch Points

For budgets below the cheapest FULL model, the result is `NO_FEASIBLE_MODEL`.
The non-empty budget intervals below report the selected model; upper bounds
are open at the next distinct model cost and the final interval is unbounded.

| Scenario | Budget interval (USD) | Selected model |
|---|---:|---|
| Coding | [0.010560, 0.031680) | DeepSeek-V4-Flash Max |
| Coding | [0.031680, 0.106830) | DeepSeek-V4-Pro Max |
| Coding | [0.106830, infinity) | Kimi K3 |
| General | [0.002200, 0.006600) | DeepSeek-V4-Flash Max |
| General | [0.006600, 0.008903) | DeepSeek-V4-Pro Max |
| General | [0.008903, 0.016000) | Qwen3.8-Max |
| General | [0.016000, 0.020772) | Gemini-3.1-Pro |
| General | [0.020772, 0.040000) | Kimi K3 |
| General | [0.040000, infinity) | GPT-5.6 Sol |
| Research | [0.012320, 0.036960) | DeepSeek-V4-Flash Max |
| Research | [0.036960, 0.106830) | DeepSeek-V4-Pro Max |
| Research | [0.106830, infinity) | Kimi K3 |

The intervals describe the utility-maximizing feasible choice at the observed
baseline costs, not a claim about production spending limits.

## 6. ICER

ICER is reported as additional USD per additional unit of utility along the
cost-ordered Pareto frontier.

| Scenario | Transition | Delta cost | Delta utility | ICER |
|---|---|---:|---:|---:|
| Coding | Flash -> Pro | 0.021120 | 0.145485 | 0.145169 |
| Coding | Pro -> Kimi | 0.075150 | 0.020239 | 3.713059 |
| General | Flash -> Pro | 0.004400 | 0.007410 | 0.593761 |
| General | Pro -> Qwen | 0.002302 | 0.184094 | 0.012507 |
| General | Qwen -> Gemini | 0.007097 | 0.027779 | 0.255499 |
| General | Gemini -> Kimi | 0.004772 | 0.002548 | 1.872844 |
| General | Kimi -> GPT-5.6 Sol | 0.019228 | 0.063438 | 0.303089 |
| Research | Flash -> Pro | 0.024640 | 0.050504 | 0.487879 |
| Research | Pro -> Kimi | 0.069870 | 0.023499 | 2.973325 |

The large final ICERs in Coding and Research indicate that the move from
DeepSeek-V4-Pro to Kimi buys a relatively small utility increment at a much
larger standardized-task cost.

## 7. Cost--Performance Fit

Fits use the 8-model FULL cohort. The all-model diagnostics are:

| Scenario | Best AICc among linear/log/saturation | R2 | LOOCV error | n |
|---|---|---:|---:|---:|
| Coding | Log | 0.077727 | 0.004089 | 8 |
| General | Saturation | 0.755203 | 9.802600 | 8 |
| Research | Log | 0.473763 | 0.000678 | 8 |

The fit results are descriptive cross-sectional associations only. Coding has
an extremely small R2, and the General saturation fit has a very large LOOCV
error relative to the linear and log fits. Pareto-frontier fits use only 3
points in Coding and Research, so their model-selection diagnostics are
unstable and should not be used as standalone evidence.

## 8. Sensitivity and Bootstrap Robustness

The sensitivity run contains 504 rows covering input-scale multipliers
0.5/1.0/2.0, input/output ratios 0.1/0.3/0.5/1.0/2.0, and simultaneous price
perturbations -10%/-5%/0/+5%/+10%, with Pareto and budget outputs.

Across the exported baseline sensitivity grid, the main frontier membership
pattern is stable for Coding and Research: DeepSeek-V4-Flash, DeepSeek-V4-Pro,
and Kimi remain the frontier members. General retains the broader frontier
pattern involving Flash, Pro, Qwen, Gemini, Kimi, and GPT-5.6 Sol. These
statements concern the tested grid only.

Bootstrap Pareto probabilities from 2,000 Q2 utility draws are:

| Scenario | Highest probabilities |
|---|---|
| Coding | Flash 1.0000; Pro 0.9465; Kimi 0.6150 |
| General | Flash 1.0000; Qwen 1.0000; GPT-5.6 Sol 0.9765; Gemini 0.9050 |
| Research | Flash 1.0000; Pro 0.8890; Kimi 0.7355 |

The probabilities quantify frontier membership under the supplied Q2 utility
bootstrap and fixed FULL-cohort costs; they do not quantify price uncertainty,
provider outages, latency, or deployment constraints.

## 9. Limitations and Release Gate

1. Fable 5 fallback cost is unresolved, so its base-price cost rows are
   descriptive only and are excluded from the main comparison.
2. GLM-5.2 has no observable official standard input/output price in the checked
   sources, so no imputed cost is reported.
3. Workloads are standardized scenarios rather than measured production
   distributions.
4. Cost--utility fits are cross-sectional and do not establish causality.
5. Prices are time-sensitive and all pricing rows still have
   `human_verified=FALSE`.

The generated outputs are therefore **provisional results ready for human
review**, not a final human-verified recommendation. Source tables and figures
are in `q3/outputs/`, with machine status in
`q3/outputs/diagnostics/q3_run_status.json`.
