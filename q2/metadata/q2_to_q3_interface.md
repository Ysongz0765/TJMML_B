# Q2 to Q3 scenario utility interface

`Q2_SCENARIO_UTILITY_FREEZE_VERSION = Q2_SCENARIO_UTILITY_v1.0`

This interface exports the exact nominal scene utilities used by the formal Q2 paper. It does not introduce price, Pareto, budget, ICER, or any alternative performance score.

## 1. Interface files

- `q2/outputs/scenario_utility.csv`: 30 frozen nominal utilities.
- `q2/outputs/scenario_utility_summary.csv`: the same utilities sorted by scene rank.
- `q2/outputs/scenario_utility_bootstrap.csv`: 60000 rows from 2000 aligned Q1-uncertainty propagation draws.
- `q2/outputs/q2_to_q3_validation.csv`: machine-readable interface quality checks.
- `q2/metadata/q2_to_q3_interface.md`: this contract.

## 2. Model identity

`model_id` is inherited unchanged from the standardized Q1/Q2 interface at Q1 data commit `754bc1b541b5b0d27e8b74b75b979849edf72cda`. No Q2- or Q3-specific model IDs are created. `model_name` retains the exact Q1 display name; `model_base_name` and `model_setting` expose the base family and the exact evaluation setting for pricing-SKU mapping.

## 3. Scenario definition

- `Research`: 科研长文本分析; CES core C1 complex reasoning, C2 factual reliability, C3 long context.
- `General`: 大众日常通用对话; CES core C1, C2, C3 and C5 multimodal availability.
- `Coding`: 计算机代码开发; CES core C1 complex reasoning and C4 code/software engineering.

Q3 must read `scenario_code` or the equivalent `scenario` column. Each model has exactly one nominal record in each scenario.

## 4. Utility definition

The formal Q2 input is the positive Bradley-Terry latent strength

```text
z_ij = exp(theta_ij - max_i(theta_ij)).
```

The nominal scenario utility is

```text
U_i^(s) = [sum_{j in J_s} w_j^(s) (z_ij + epsilon)^rho_s]^(1/rho_s),
```

with the continuous weighted geometric-mean limit when `rho_s = 0`. The numerical shift is `epsilon = 1e-06`. Structural C5 absence uses the frozen availability anchor 0.35 and is never interpreted as an observed benchmark zero or a zero-filled latent score.

## 5. Parameter source

- `Research` (科研长文本分析): C1=0.3439, C2=0.3250, C3=0.3311; alpha=0.675; rho=-0.50.
- `General` (大众日常通用对话): C1=0.2417, C2=0.3833, C3=0.1000, C5=0.2750; alpha=0.625; rho=0.00.
- `Coding` (计算机代码开发): C1=0.3500, C4=0.6500; alpha=0.650; rho=-0.40.

The weights are the KL minimum-information projection from the Q1 objective-weight prior under frozen scene constraints. The formal model specification SHA-256 is `5eb483577f32621802c3249d6a39fbdf81e8170fa6e1f7af2cf381fd3135482d`.

## 6. Scale and normalization

- Utility is not a rank score, price-adjusted score, Q1 overall score, or benchmark score.
- Dimension inputs are normalized across models within each ability dimension before CES aggregation.
- Utilities are positive and, under the implemented scale, lie in `(0, 1 + 1e-06]`; larger is better.
- No post-hoc min-max normalization is applied to the nominal scene utility.
- Because Research, General and Coding use different ability sets, KL weights and rho values, absolute utility levels are intended for comparison within a scenario only.
- Q3 must run Pareto analysis separately by scenario. It must not infer that Research utility 0.8 is economically or scientifically equivalent to Coding utility 0.8.

## 7. Uncertainty

`Q2_BOOTSTRAP_SCENARIO_UTILITY_AVAILABLE = TRUE`

The bootstrap interface contains 2000 aligned draws. The standardized Q1 interface supplies point theta and dimension-level bootstrap SD, not the original joint replicate table. Q2 therefore samples `theta_draw = point_theta + Normal(0, theta_bootstrap_sd)` with seed 20260817, independently across model-dimension cells because covariance is unavailable. The same bootstrap_id identifies one joint Q2 draw across all models and all three scenarios. Structural C5 anchors remain fixed. These rows propagate Q1 ability-estimation uncertainty only; alpha/rho parameter uncertainty is stored separately in the Q2 robustness outputs and is not mixed into this Q3 Pareto-bootstrap interface.

## 8. Q3 usage rule

Q3 must use `utility` directly as its performance variable `U_i^(s)`. It must not reweight abilities, rebuild a performance score, substitute Q1 overall score, convert rank to a score, or divide utility by price before the Q3 cost model. Cost, Pareto frontiers, budgets, ICER and cost-performance fitting belong exclusively to Q3.

Recommended nominal load:

```python
utility = pandas.read_csv('q2/outputs/scenario_utility.csv')
for scenario_code, group in utility.groupby('scenario_code'):
    # join group to Q3 pricing by model_id/model_setting, then run Q3 per scenario
    ...
```

## 9. Validation and paper synchronization

All 18 interface checks pass. The nominal interface, `outputs/q2/final/q2_scene_scores.csv`, and the generated LaTeX paper values are written from the same frozen in-memory reference result. Consequently the Q2 paper ranking and the Q3 performance interface cannot select different nominal result versions within a formal run.
